"""
db.py — Supabase adapter. Implements the interface apply_analysis() (analyze.py) expects.

Uses the SERVICE ROLE key: the backend is the only writer, RLS stays enabled on the tables
(service role bypasses it), and the browser never talks to Supabase directly — it talks to
FastAPI. Users live in user_settings (username/password_hash/is_admin) — the admin creates
accounts, every request runs as the authenticated user (see auth.py + main.current_user).

Slug reconciliation lives here (golden rule #3): analyze() proposes slugs, get_or_create_concept()
reuses existing ones and creates new ones with reviewed=false. Slugs are never renamed.
"""

import os
from supabase import create_client, Client

_client: Client | None = None


def get_db() -> "Database":
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
        _client = create_client(url, key)
    return Database(_client)


class Database:
    def __init__(self, client: Client):
        self.c = client

    # ---------- users ----------
    def get_user_by_id(self, user_id: str) -> dict | None:
        rows = (self.c.table("user_settings").select("*")
                .eq("user_id", user_id).execute().data)
        return rows[0] if rows else None

    def get_user_by_username(self, username: str) -> dict | None:
        rows = (self.c.table("user_settings").select("*")
                .eq("username", username).execute().data)
        return rows[0] if rows else None

    def create_user(self, username: str, password_hash: str, display_name: str,
                    is_admin: bool = False) -> dict:
        return self.c.table("user_settings").insert({
            "username": username, "password_hash": password_hash,
            "display_name": display_name, "is_admin": is_admin,
        }).execute().data[0]

    def update_user(self, user_id: str, fields: dict) -> None:
        self.c.table("user_settings").update(fields).eq("user_id", user_id).execute()

    def list_users(self) -> list[dict]:
        return (self.c.table("user_settings")
                .select("user_id, username, display_name, is_admin, level_estimate,"
                        " onboarded_at, created_at")
                .order("created_at").execute().data)

    def claim_legacy_user(self, username: str, password_hash: str,
                          display_name: str) -> dict | None:
        """Turn the pre-auth single-user row (with all its learning data) into the admin.
        Returns None if there is no unclaimed row."""
        rows = (self.c.table("user_settings").select("user_id")
                .is_("username", "null").limit(1).execute().data)
        if not rows:
            return None
        self.update_user(rows[0]["user_id"], {
            "username": username, "password_hash": password_hash,
            "display_name": display_name, "is_admin": True,
            "onboarded_at": "now()",  # der Admin hat schon echte Daten — kein Test nötig
        })
        return self.get_user_by_id(rows[0]["user_id"])

    # ---------- captures ----------
    def create_capture(self, user_id: str, raw_text: str, kind: str, source: str = "web") -> str:
        row = self.c.table("captures").insert({
            "user_id": user_id, "raw_text": raw_text, "kind": kind, "source": source,
        }).execute().data[0]
        return row["id"]

    def list_captures(self, user_id: str, limit: int = 20) -> list[dict]:
        """Recent captures, newest first, with their correction (if any) nested in."""
        return (self.c.table("captures")
                .select("id, raw_text, kind, created_at, corrections(wrong, correct)")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute().data)

    # ---------- concepts (slug reconciliation) ----------
    def get_or_create_concept(self, slug: str, label: str | None, cefr: str | None) -> dict:
        rows = self.c.table("concepts").select("*").eq("slug", slug).execute().data
        if rows:
            return rows[0]  # reuse — never regenerate or rename slugs
        return self.c.table("concepts").insert({
            "slug": slug,
            "label": label or slug,
            "cefr": cefr,
            "reviewed": False,  # new concepts wait for human review
        }).execute().data[0]

    # ---------- evidence ----------
    def add_evidence(self, user_id: str, concept_id: str, capture_id: str, kind: str) -> None:
        self.c.table("concept_evidence").insert({
            "user_id": user_id, "concept_id": concept_id,
            "capture_id": capture_id, "kind": kind,
        }).execute()

    # ---------- concept state ----------
    def get_or_create_state(self, user_id: str, concept_id: str) -> dict:
        rows = (self.c.table("concept_state").select("*")
                .eq("user_id", user_id).eq("concept_id", concept_id).execute().data)
        if rows:
            return rows[0]
        return self.c.table("concept_state").insert({
            "user_id": user_id, "concept_id": concept_id,
        }).execute().data[0]

    def save_state(self, state: dict) -> None:
        self.c.table("concept_state").update({
            "need_count": state["need_count"],
            "success_count": state["success_count"],
            "state": state["state"],
            "last_seen": "now()",
            "updated_at": "now()",
        }).eq("id", state["id"]).execute()

    # ---------- corrections ----------
    def add_correction(self, user_id: str, capture_id: str,
                       wrong: str, correct: str, concept_id: str | None) -> None:
        self.c.table("corrections").insert({
            "user_id": user_id, "capture_id": capture_id,
            "wrong": wrong, "correct": correct, "concept_id": concept_id,
        }).execute()

    # ---------- reading surfaces (Slice 5) ----------
    def list_concepts_with_state(self, user_id: str) -> list[dict]:
        """All concepts + this user's state merged in (zeros where never touched)."""
        concepts = (self.c.table("concepts")
                    .select("id, slug, label, ctype, cefr, reviewed").execute().data)
        states = (self.c.table("concept_state").select("*")
                  .eq("user_id", user_id).execute().data)
        by_cid = {s["concept_id"]: s for s in states}
        out = []
        for concept in concepts:
            s = by_cid.get(concept["id"], {})
            out.append({
                **concept,
                "state": s.get("state", "sin_ver"),
                "need_count": s.get("need_count", 0),
                "success_count": s.get("success_count", 0),
                "relevance_boost": s.get("relevance_boost", 0),
                "boost_expires_at": s.get("boost_expires_at"),
                "updated_at": s.get("updated_at"),
            })
        return out

    def update_concept_body(self, slug: str, fields: dict) -> None:
        self.c.table("concepts").update(fields).eq("slug", slug).execute()

    def list_concept_slugs(self) -> list[str]:
        return [r["slug"] for r in
                self.c.table("concepts").select("slug").order("slug").execute().data]

    def merge_concept(self, dup_slug: str, canonical_slug: str) -> dict:
        """Deterministic consolidation: repoint every trace of the duplicate (evidence,
        corrections, situation links) to the canonical concept, sum the learning state,
        then delete the duplicate. Slugs stay stable — duplicates die, canonicals never move."""
        from analyze import derive_state

        dup_rows = self.c.table("concepts").select("id, slug").eq("slug", dup_slug).execute().data
        canon_rows = self.c.table("concepts").select("id, slug").eq("slug", canonical_slug).execute().data
        if not dup_rows or not canon_rows:
            raise KeyError(f"merge: '{dup_slug}' oder '{canonical_slug}' existiert nicht")
        dup_id, canon_id = dup_rows[0]["id"], canon_rows[0]["id"]

        self.c.table("concept_evidence").update({"concept_id": canon_id}) \
            .eq("concept_id", dup_id).execute()
        self.c.table("corrections").update({"concept_id": canon_id}) \
            .eq("concept_id", dup_id).execute()

        links = (self.c.table("situation_concepts").select("*")
                 .eq("concept_id", dup_id).execute().data)
        for link in links:
            self.c.table("situation_concepts").upsert(
                {**link, "concept_id": canon_id},
                on_conflict="situation_id,concept_id", ignore_duplicates=True).execute()
        self.c.table("situation_concepts").delete().eq("concept_id", dup_id).execute()

        merged_states = 0
        for ds in self.c.table("concept_state").select("*").eq("concept_id", dup_id).execute().data:
            cs = self.get_or_create_state(ds["user_id"], canon_id)
            need = cs["need_count"] + ds["need_count"]
            success = cs["success_count"] + ds["success_count"]
            rank = ["sin_ver", "visto", "flojo", "aprendiendo", "dominado"]
            fallback = max(cs["state"], ds["state"], key=rank.index)
            self.c.table("concept_state").update({
                "need_count": need,
                "success_count": success,
                "state": derive_state(need, success, fallback),
                "relevance_boost": max(cs["relevance_boost"], ds["relevance_boost"]),
                "boost_expires_at": max(filter(None, [cs.get("boost_expires_at"),
                                                      ds.get("boost_expires_at")]), default=None),
                "updated_at": "now()",
            }).eq("id", cs["id"]).execute()
            self.c.table("concept_state").delete().eq("id", ds["id"]).execute()
            merged_states += 1

        self.c.table("concepts").delete().eq("id", dup_id).execute()
        return {"merged": dup_slug, "into": canonical_slug, "states_merged": merged_states}

    def delete_concept(self, slug: str) -> None:
        """Hard delete incl. all traces — for concepts that should never have existed
        (e.g. vocabulary-topic pseudo-concepts). Not for real duplicates: use merge_concept."""
        rows = self.c.table("concepts").select("id").eq("slug", slug).execute().data
        if not rows:
            return
        cid = rows[0]["id"]
        for table in ("concept_evidence", "concept_state", "situation_concepts"):
            self.c.table(table).delete().eq("concept_id", cid).execute()
        self.c.table("corrections").update({"concept_id": None}).eq("concept_id", cid).execute()
        self.c.table("concepts").delete().eq("id", cid).execute()

    def get_concept_detail(self, user_id: str, slug: str) -> dict | None:
        """One chapter: shared body + personal mantle (state, your actual error sentences)."""
        rows = self.c.table("concepts").select("*").eq("slug", slug).execute().data
        if not rows:
            return None
        concept = rows[0]
        states = (self.c.table("concept_state").select("*")
                  .eq("user_id", user_id).eq("concept_id", concept["id"]).execute().data)
        corrections = (self.c.table("corrections")
                       .select("wrong, correct, created_at")
                       .eq("user_id", user_id).eq("concept_id", concept["id"])
                       .order("created_at", desc=True).limit(10).execute().data)
        return {**concept, "user_state": states[0] if states else None, "corrections": corrections}

    def hot_concepts(self, user_id: str, limit: int = 5) -> list[dict]:
        """'En caliente': freshly promoted concepts, newest movement first."""
        states = (self.c.table("concept_state")
                  .select("need_count, success_count, state, updated_at, concepts(slug, label, cefr)")
                  .eq("user_id", user_id).eq("state", "aprendiendo")
                  .order("updated_at", desc=True).limit(limit).execute().data)
        return [{
            "slug": s["concepts"]["slug"], "label": s["concepts"]["label"],
            "cefr": s["concepts"]["cefr"], "need_count": s["need_count"],
            "success_count": s["success_count"],
        } for s in states]

    def due_vocab(self, user_id: str, limit: int = 5) -> tuple[int, list[str]]:
        """SRS-due vocab: count + a small preview. The drill itself is Slice 6."""
        res = (self.c.table("vocab_items").select("term", count="exact")
               .eq("user_id", user_id).lte("srs_due", "now()")
               .order("srs_due").limit(limit).execute())
        return res.count or 0, [r["term"] for r in res.data]

    # ---------- vocab ----------
    def get_or_create_vocab_item(self, user_id: str, lemma: dict, source_capture_id: str,
                                 situation_id: str | None = None,
                                 tags: list[str] | None = None) -> tuple[str, bool]:
        """Returns (item_id, created). Existing terms are left alone — their SRS position
        is learning state, don't reset it."""
        existing = (self.c.table("vocab_items").select("id")
                    .eq("user_id", user_id).eq("term", lemma["term"]).execute().data)
        if existing:
            return existing[0]["id"], False
        row = self.c.table("vocab_items").insert({
            "user_id": user_id,
            "term": lemma["term"],
            "translation": lemma["translation"],
            "register": lemma.get("register", "neutral"),
            "region": lemma.get("region"),
            "situation_id": situation_id,
            "tags": tags or [],
            "source_capture_id": source_capture_id,
        }).execute().data[0]
        return row["id"], True

    def get_vocab_item(self, user_id: str, item_id: str) -> dict | None:
        rows = (self.c.table("vocab_items").select("*")
                .eq("user_id", user_id).eq("id", item_id).execute().data)
        return rows[0] if rows else None

    def update_vocab_srs(self, item_id: str, patch: dict) -> None:
        self.c.table("vocab_items").update(patch).eq("id", item_id).execute()

    # ---------- situations (shelves) ----------
    def get_or_create_situation(self, user_id: str, name: str, is_seed: bool = False) -> dict:
        rows = (self.c.table("situations").select("*")
                .eq("user_id", user_id).eq("name", name).execute().data)
        if rows:
            return rows[0]
        return self.c.table("situations").insert({
            "user_id": user_id, "name": name, "is_seed": is_seed,
        }).execute().data[0]

    def add_vocab_to_situation(self, situation_id: str, vocab_item_id: str) -> None:
        self.c.table("situation_vocab").upsert(
            {"situation_id": situation_id, "vocab_item_id": vocab_item_id},
            on_conflict="situation_id,vocab_item_id", ignore_duplicates=True,
        ).execute()

    def link_situation_concept(self, situation_id: str, concept_id: str,
                               why: str | None = None) -> None:
        row = {"situation_id": situation_id, "concept_id": concept_id, "why": why}
        try:
            self.c.table("situation_concepts").upsert(
                row, on_conflict="situation_id,concept_id", ignore_duplicates=True).execute()
        except Exception:
            # 'why' column not migrated yet (db/migrations/001) — link without the sentence
            row.pop("why")
            self.c.table("situation_concepts").upsert(
                row, on_conflict="situation_id,concept_id", ignore_duplicates=True).execute()

    def boost_concept(self, user_id: str, concept_id: str, boost: int, days: int) -> None:
        from datetime import datetime, timedelta, timezone
        state = self.get_or_create_state(user_id, concept_id)
        self.c.table("concept_state").update({
            "relevance_boost": boost,
            "boost_expires_at": (datetime.now(timezone.utc) + timedelta(days=days)).isoformat(),
            "updated_at": "now()",
        }).eq("id", state["id"]).execute()

    def list_situations(self, user_id: str) -> list[dict]:
        sits = (self.c.table("situations").select("id, name, is_seed, created_at")
                .eq("user_id", user_id).order("created_at", desc=True).execute().data)
        counts: dict[str, int] = {}
        for j in self.c.table("situation_vocab").select("situation_id").execute().data:
            counts[j["situation_id"]] = counts.get(j["situation_id"], 0) + 1
        return [{**s, "item_count": counts.get(s["id"], 0)} for s in sits]

    def get_situation_detail(self, user_id: str, situation_id: str) -> dict | None:
        rows = (self.c.table("situations").select("*")
                .eq("user_id", user_id).eq("id", situation_id).execute().data)
        if not rows:
            return None
        sit = rows[0]
        joins = (self.c.table("situation_vocab").select("vocab_item_id")
                 .eq("situation_id", situation_id).execute().data)
        items = []
        if joins:
            items = (self.c.table("vocab_items")
                     .select("id, term, translation, register, region, tags")
                     .in_("id", [j["vocab_item_id"] for j in joins])
                     .order("created_at").execute().data)
        concepts = (self.c.table("situation_concepts")
                    .select("*, concepts(slug, label, cefr)")
                    .eq("situation_id", situation_id).execute().data)
        return {**sit, "items": items,
                "concepts": [{"slug": c["concepts"]["slug"], "label": c["concepts"]["label"],
                              "cefr": c["concepts"]["cefr"], "why": c.get("why")}
                             for c in concepts]}

    def loose_vocab(self, user_id: str, limit: int = 100) -> list[dict]:
        """Vocab that grew out of captures, not out of a shelf."""
        return (self.c.table("vocab_items")
                .select("id, term, translation, register, region")
                .eq("user_id", user_id).is_("situation_id", "null")
                .order("created_at", desc=True).limit(limit).execute().data)

    def recent_situations(self, user_id: str, days: int = 7) -> list[dict]:
        from datetime import datetime, timedelta, timezone
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        return (self.c.table("situations").select("id, name, created_at")
                .eq("user_id", user_id).eq("is_seed", False)
                .gte("created_at", cutoff)
                .order("created_at", desc=True).limit(5).execute().data)

    # ---------- seed vocab (Grundwortschatz — geteiltes Wörterbuch, kein Lernstand) ----------
    def _user_terms(self, user_id: str) -> set[str]:
        return {v["term"] for v in (self.c.table("vocab_items").select("term")
                                    .eq("user_id", user_id).execute().data)}

    def seed_topics(self, user_id: str) -> list[dict]:
        """Themen-Regale des Grundwortschatzes + wie viel davon schon im eigenen SRS ist."""
        words = self.c.table("seed_vocab").select("term, topic").execute().data
        if not words:
            return []
        mine = self._user_terms(user_id)
        topics: dict[str, dict] = {}
        for w in words:
            t = topics.setdefault(w["topic"], {"topic": w["topic"], "count": 0, "added": 0})
            t["count"] += 1
            if w["term"] in mine:
                t["added"] += 1
        return sorted(topics.values(), key=lambda t: t["topic"])

    def seed_words_for_topic(self, user_id: str, topic: str) -> list[dict]:
        words = (self.c.table("seed_vocab")
                 .select("id, term, translation, register, freq_rank, cefr")
                 .eq("topic", topic).order("freq_rank").execute().data)
        mine = self._user_terms(user_id)
        return [{**w, "added": w["term"] in mine} for w in words]

    def add_seed_word(self, user_id: str, seed_id: str) -> bool:
        """Ein Grundwortschatz-Wort manuell ins persönliche SRS holen."""
        rows = self.c.table("seed_vocab").select("*").eq("id", seed_id).execute().data
        if not rows:
            raise KeyError("seed word no existe")
        w = rows[0]
        _, created = self.get_or_create_vocab_item(
            user_id,
            {"term": w["term"], "translation": w["translation"],
             "register": w["register"], "region": None},
            source_capture_id=None, tags=["seed", w["topic"]],
        )
        return created

    def promote_daily_seed(self, user_id: str, quota: int = 10) -> int:
        """Bis zu N neue Grundwortschatz-Wörter pro Tag rücken automatisch ins SRS nach
        (nach Frequenz-Rang). Deterministisch; no-op wenn seed_vocab leer ist (lengua/es)."""
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).date().isoformat()
        promoted_today = (self.c.table("vocab_items").select("id", count="exact")
                          .eq("user_id", user_id).contains("tags", ["seed"])
                          .gte("created_at", today).execute()).count or 0
        slots = quota - promoted_today
        if slots <= 0:
            return 0
        mine = self._user_terms(user_id)
        added, offset = 0, 0
        while added < slots:
            page = (self.c.table("seed_vocab").select("*")
                    .order("freq_rank").range(offset, offset + 199).execute().data)
            if not page:
                break
            for w in page:
                if added >= slots:
                    break
                if w["term"] in mine:
                    continue
                self.get_or_create_vocab_item(
                    user_id,
                    {"term": w["term"], "translation": w["translation"],
                     "register": w["register"], "region": None},
                    source_capture_id=None, tags=["seed", w["topic"]],
                )
                mine.add(w["term"])
                added += 1
            offset += 200
        return added

    # ---------- practicar (drill selection — pulls exactly where scoring wobbles) ----------
    def due_vocab_items(self, user_id: str, limit: int = 8,
                        phrases: bool | None = None) -> list[dict]:
        """SRS-due items. phrases=True → only intent-phrases, False → only words, None → both."""
        q = (self.c.table("vocab_items").select("*")
             .eq("user_id", user_id).lte("srs_due", "now()"))
        if phrases is True:
            q = q.contains("tags", ["frase"])
        elif phrases is False:
            q = q.not_.contains("tags", ["frase"])
        return q.order("srs_due").limit(limit).execute().data

    def shaky_concepts(self, user_id: str) -> list[dict]:
        """Concepts whose state wobbles — the drill source."""
        states = (self.c.table("concept_state")
                  .select("concept_id, state, need_count, concepts(slug, label, ctype)")
                  .eq("user_id", user_id).in_("state", ["flojo", "aprendiendo"])
                  .order("need_count", desc=True).execute().data)
        return [{"concept_id": s["concept_id"], "slug": s["concepts"]["slug"],
                 "label": s["concepts"]["label"], "ctype": s["concepts"]["ctype"]}
                for s in states]

    def corrections_for_concepts(self, user_id: str, concept_ids: list[str],
                                 limit: int = 12) -> list[dict]:
        if not concept_ids:
            return []
        return (self.c.table("corrections")
                .select("wrong, correct, concept_id, concepts(slug, label)")
                .eq("user_id", user_id).in_("concept_id", concept_ids)
                .order("created_at", desc=True).limit(limit).execute().data)

    def verbs_for_patterns(self, slugs: list[str], limit: int = 12) -> list[dict]:
        if not slugs:
            return []
        return (self.c.table("verbs")
                .select("infinitive, translation, pattern_tags, conjugations")
                .overlaps("pattern_tags", slugs)
                .order("freq_rank").limit(limit).execute().data)

    def frequent_verbs(self, limit: int = 12) -> list[dict]:
        return (self.c.table("verbs")
                .select("infinitive, translation, pattern_tags, conjugations")
                .order("freq_rank").limit(limit).execute().data)
