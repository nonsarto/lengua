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

# Start-Ease importierter Vokabeln: unter dem 2.5-Default eigener Captures. Ein Wort aus einem
# Check hast du aktiv produziert; ein importiertes ist fremdes, unbewiesenes Material.
IMPORT_COLD_EASE = 2.3


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

    def create_pairing_code(self, user_id: str) -> str:
        """Einmal-Code für den Telegram-Speaking-Bot (bot_pairing_codes, Migration 013).
        Der Bot löst ihn per /start <code> ein; 24 h gültig, einmal verwendbar.
        Zeichenvorrat von token_urlsafe (A-Za-z0-9_-) = exakt der erlaubte
        Telegram-start-Payload."""
        import secrets
        code = secrets.token_urlsafe(8)
        self.c.table("bot_pairing_codes").insert(
            {"code": code, "user_id": user_id}).execute()
        return code

    def delete_user_full(self, user_id: str) -> None:
        """Nutzer + ALLE seine Daten löschen (Admin). FK-sichere Reihenfolge:
        Join-Tabellen über die Situations-IDs, vocab vor captures (source_capture_id),
        captures vor documents; Bot-Verknüpfungen zuletzt vor dem Nutzer selbst.
        Geteilte Inhalte (concepts, exercises, seed) bleiben unberührt."""
        sit_ids = [r["id"] for r in (self.c.table("situations").select("id")
                                     .eq("user_id", user_id).execute().data)]
        if sit_ids:
            self.c.table("situation_vocab").delete().in_("situation_id", sit_ids).execute()
            self.c.table("situation_concepts").delete().in_("situation_id", sit_ids).execute()
        for table in ("corrections", "concept_evidence", "exercise_attempts",
                      "listening_items", "daily_sessions", "error_log",
                      "speaking_chunks", "speaking_sessions", "vocab_items",
                      "captures", "documents", "situations", "concept_state",
                      "bot_pairing_codes", "bot_links"):
            try:
                self.c.table(table).delete().eq("user_id", user_id).execute()
            except Exception:
                pass  # Tabelle existiert auf dieser Instanz evtl. nicht (ca ohne Bot)
        self.c.table("user_settings").delete().eq("user_id", user_id).execute()

    def claim_onboarding(self, user_id: str) -> bool:
        """Atomarer Doppel-Submit-Schutz: setzt onboarded_at NUR wenn noch null. Gibt True
        zurück, wenn DIESER Aufruf den Slot geholt hat — nur dann darf gesät werden. Schließt
        die TOCTOU-Lücke zwischen 'schon onboarded?'-Prüfung und dem Schreiben."""
        res = (self.c.table("user_settings").update({"onboarded_at": "now()"})
               .eq("user_id", user_id).is_("onboarded_at", "null").execute())
        return bool(res.data)

    def list_users(self) -> list[dict]:
        return (self.c.table("user_settings")
                .select("user_id, username, display_name, is_admin, level_estimate,"
                        " onboarded_at, created_at")
                .order("created_at").execute().data)

    # ---------- llm usage / admin stats ----------
    def insert_llm_usage(self, row: dict) -> None:
        self.c.table("llm_usage").insert(row).execute()

    def admin_stats(self) -> list[dict]:
        """Pro Nutzer: letzte Aktivität + Aktivitäts- und Verbrauchszähler (7/30 Tage).
        Familien-Skala: 30-Tage-Rohzeilen holen und in Python aggregieren ist billiger
        und klarer als ein RPC. llm_usage darf fehlen (Migration 016 noch nicht gelaufen,
        ca-Instanz) — dann bleiben die Token-Felder einfach 0."""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        cutoff30 = (now - timedelta(days=30)).isoformat()
        cutoff7 = now - timedelta(days=7)

        def _ts(value: str) -> datetime:
            return datetime.fromisoformat(value)

        # (interner Key, Tabelle, Zeitspalte, Extra-Spalten)
        sources = [
            ("sessions", "daily_sessions", "created_at", ""),
            ("exercises", "exercise_attempts", "answered_at", ""),
            ("captures", "captures", "created_at", ""),
            ("voices", "speaking_sessions", "created_at", ", duration_sec"),
        ]
        rows30: dict[str, list[dict]] = {}
        for key, table, ts_col, extra in sources:
            rows30[key] = (self.c.table(table).select(f"user_id, {ts_col}{extra}")
                           .gte(ts_col, cutoff30).limit(10000).execute().data)

        try:
            usage_rows = (self.c.table("llm_usage")
                          .select("user_id, model, input_tokens, output_tokens,"
                                  " cache_read_tokens, cache_write_tokens, audio_seconds")
                          .gte("created_at", cutoff30).limit(10000).execute().data)
        except Exception:
            usage_rows = []

        stats = []
        for u in self.list_users():
            if (u.get("username") or "").startswith("__"):
                continue  # Testnutzer
            uid = u["user_id"]
            s = {**u, "last_active": None, "voice_min_30d": 0,
                 "tokens_in_30d": 0, "tokens_out_30d": 0, "tokens_cache_30d": 0,
                 "audio_sec_30d": 0, "models_30d": {}}
            for key, table, ts_col, _ in sources:
                mine = [r for r in rows30[key] if r["user_id"] == uid]
                s[f"{key}_30d"] = len(mine)
                s[f"{key}_7d"] = sum(1 for r in mine if _ts(r[ts_col]) >= cutoff7)
                if mine:
                    latest = max(r[ts_col] for r in mine)
                    if s["last_active"] is None or latest > s["last_active"]:
                        s["last_active"] = latest
                if key == "voices":
                    s["voice_min_30d"] = sum(r.get("duration_sec") or 0 for r in mine) // 60
            # Nichts in 30 Tagen: letzte Aktivität überhaupt nachschlagen
            if s["last_active"] is None:
                for _, table, ts_col, _extra in sources:
                    r = (self.c.table(table).select(ts_col).eq("user_id", uid)
                         .order(ts_col, desc=True).limit(1).execute().data)
                    if r and (s["last_active"] is None or r[0][ts_col] > s["last_active"]):
                        s["last_active"] = r[0][ts_col]
            for r in usage_rows:
                if r["user_id"] != uid:
                    continue
                s["tokens_in_30d"] += r["input_tokens"]
                s["tokens_out_30d"] += r["output_tokens"]
                s["tokens_cache_30d"] += r["cache_read_tokens"] + r["cache_write_tokens"]
                s["audio_sec_30d"] += r["audio_seconds"]
                m = s["models_30d"].setdefault(
                    r["model"], {"in": 0, "out": 0, "cache_read": 0, "cache_write": 0})
                m["in"] += r["input_tokens"]
                m["out"] += r["output_tokens"]
                m["cache_read"] += r["cache_read_tokens"]
                m["cache_write"] += r["cache_write_tokens"]
            stats.append(s)
        return stats

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
    def create_capture(self, user_id: str, raw_text: str, kind: str, source: str = "web",
                       capture_id: str | None = None, analysis: dict | None = None) -> str:
        """capture_id darf vorab (uuid4) vergeben werden — so kann die Antwort die ID
        schon tragen, während die Persistenz im Hintergrund nachläuft.
        analysis = die volle analyze()-Ausgabe; aufgehoben für die Detailansicht der Historie."""
        payload = {"user_id": user_id, "raw_text": raw_text, "kind": kind, "source": source}
        if capture_id:
            payload["id"] = capture_id
        if analysis is not None:
            payload["analysis"] = analysis
        row = self.c.table("captures").insert(payload).execute().data[0]
        return row["id"]

    def update_capture_analysis(self, user_id: str, capture_id: str, kind: str,
                                analysis: dict) -> None:
        """Die Capture-Zeile besteht schon (synchron angelegt) — hier wird sie nach der
        vollen Hintergrund-Analyse angereichert (kind ggf. korrigiert, analysis überschrieben)."""
        (self.c.table("captures").update({"kind": kind, "analysis": analysis})
         .eq("user_id", user_id).eq("id", capture_id).execute())

    def list_captures(self, user_id: str, limit: int = 20) -> list[dict]:
        """Recent captures, newest first, with their correction (if any) nested in.
        Die Onboarding-Capture (source='onboarding') trägt Evidence, ist aber keine
        Nutzer-Handlung — sie gehört nicht in die sichtbare Historie."""
        return (self.c.table("captures")
                .select("id, raw_text, kind, created_at, corrections(wrong, correct)")
                .eq("user_id", user_id)
                .neq("source", "onboarding")
                .order("created_at", desc=True)
                .limit(limit)
                .execute().data)

    def get_capture_detail(self, user_id: str, capture_id: str) -> dict | None:
        """Die volle Analyse EINES Captures für die Detailansicht. Neu-Einträge tragen die
        analyze()-Ausgabe als `analysis`-Blob; für Alt-Einträge (analysis=null) wird
        rekonstruiert, was in den verknüpften Tabellen liegt — mehr gibt es dort nicht."""
        rows = (self.c.table("captures")
                .select("id, raw_text, kind, created_at, analysis")
                .eq("user_id", user_id).eq("id", capture_id).limit(1)
                .execute().data)
        if not rows:
            return None
        cap = rows[0]
        base = {"id": cap["id"], "raw_text": cap["raw_text"], "kind": cap["kind"],
                "created_at": cap["created_at"]}

        analysis = cap.get("analysis")
        if analysis:
            corr = analysis.get("correction")
            return {**base, "persisted": True,
                    "gist": analysis.get("gist"),
                    "notes": analysis.get("notes") or "",
                    "correction": ({"wrong": corr["wrong"], "correct": corr["correct"],
                                    "why": corr.get("why")} if corr else None),
                    "concepts": [{"slug": c["slug"], "label": c.get("label", c["slug"]),
                                  "evidence": c.get("evidence")}
                                 for c in analysis.get("concepts", [])],
                    "lemmas": [{"term": l["term"], "translation": l["translation"],
                                "register": l.get("register"), "region": l.get("region")}
                               for l in analysis.get("lemmas", [])],
                    "word": analysis.get("word"),
                    "brief": analysis.get("brief")}

        # Alt-Eintrag: aus den Fakten zusammensetzen, die persistiert wurden.
        corr_rows = (self.c.table("corrections")
                     .select("wrong, correct, concepts(slug, label)")
                     .eq("user_id", user_id).eq("capture_id", capture_id).limit(1)
                     .execute().data)
        concept_rows = (self.c.table("concept_evidence")
                        .select("kind, concepts(slug, label)")
                        .eq("user_id", user_id).eq("capture_id", capture_id)
                        .execute().data)
        vocab_rows = (self.c.table("vocab_items")
                      .select("term, translation, register, region")
                      .eq("user_id", user_id).eq("source_capture_id", capture_id)
                      .execute().data)
        corr = corr_rows[0] if corr_rows else None
        return {**base, "persisted": False,
                "gist": None, "notes": "",
                "correction": ({"wrong": corr["wrong"], "correct": corr["correct"], "why": None}
                               if corr else None),
                "concepts": [{"slug": r["concepts"]["slug"],
                              "label": r["concepts"].get("label") or r["concepts"]["slug"],
                              "evidence": r.get("kind")}
                             for r in concept_rows if r.get("concepts")],
                "lemmas": [{"term": v["term"], "translation": v["translation"],
                            "register": v.get("register"), "region": v.get("region")}
                           for v in vocab_rows],
                "word": None,
                "brief": None}

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
                                 tags: list[str] | None = None,
                                 source: str = "capture") -> tuple[str, bool]:
        """Returns (item_id, created). Existing terms are left alone — their SRS position
        is learning state, don't reset it. `source` marks the origin (capture|seed|import)
        so the session generator can weight self-captured vocab ahead of imported."""
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
            "source": source,
        }).execute().data[0]
        return row["id"], True

    def get_vocab_item(self, user_id: str, item_id: str) -> dict | None:
        rows = (self.c.table("vocab_items").select("*")
                .eq("user_id", user_id).eq("id", item_id).execute().data)
        return rows[0] if rows else None

    def update_vocab_srs(self, item_id: str, patch: dict) -> None:
        self.c.table("vocab_items").update(patch).eq("id", item_id).execute()

    def bulk_import_vocab(self, user_id: str, items: list[dict],
                          situation_id: str | None = None, source: str = "import",
                          source_document_id: str | None = None) -> tuple[int, int]:
        """Massenimport aus Datei ODER Dokument. Dedupe gegen bestehende Terme (case-insensitiv),
        die neuen KALT ins SRS: sofort fällig (Spalten-Default now()), interval/reps 0, und
        eine niedrigere Start-Ease als eine eigene Capture — die Herkunft seedet die
        Startposition (importiert = fremdes Material, kein aktiv produziertes Wort).
        source_document_id hält die Herkunft fest, wenn die Vokabeln aus einem Dokument stammen.
        Gibt (imported, skipped) zurück."""
        existing = {t.lower() for t in self._user_terms(user_id)}
        rows = []
        for it in items:
            key = it["term"].lower()
            if not it["term"].strip() or not it["translation"].strip() or key in existing:
                continue
            existing.add(key)
            rows.append({
                "user_id": user_id,
                "term": it["term"],
                "translation": it["translation"],
                "register": it.get("register", "neutral"),
                "region": it.get("region"),
                "situation_id": situation_id,
                "tags": it.get("tags", []),
                "source": source,
                "source_document_id": source_document_id,
                "srs_ease": IMPORT_COLD_EASE,   # kälter als der 2.5-Default eigener Captures
            })
        if not rows:
            return 0, len(items)
        inserted = self.c.table("vocab_items").insert(rows).execute().data
        if situation_id:
            for r in inserted:
                self.add_vocab_to_situation(situation_id, r["id"])
        return len(inserted), len(items) - len(inserted)

    # ---------- documents (hochgeladenes Lernmaterial — Herkunft eines Boosts/Imports) ----------
    def create_document(self, user_id: str, filename: str | None, kind: str,
                        mode: str) -> dict:
        return self.c.table("documents").insert({
            "user_id": user_id, "filename": filename, "kind": kind, "mode": mode,
        }).execute().data[0]

    def update_document(self, document_id: str, fields: dict) -> None:
        self.c.table("documents").update(fields).eq("id", document_id).execute()

    def list_documents(self, user_id: str, limit: int = 20) -> list[dict]:
        return (self.c.table("documents").select("*")
                .eq("user_id", user_id).order("created_at", desc=True)
                .limit(limit).execute().data)

    # ---------- situations (shelves) ----------
    def get_or_create_situation(self, user_id: str, name: str, is_seed: bool = False) -> dict:
        # Erster Buchstabe groß — beide Anlege-Wege (Input + brief) liefern sonst
        # gemischte Schreibweisen im Regal ("transporte" neben "En la farmacia").
        name = (name[:1].upper() + name[1:]) if name else name
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

    @staticmethod
    def _seed_tags(w: dict) -> list[str]:
        """Tags fürs persönliche SRS: Herkunft + Thema, Phrasen zusätzlich als "frase" —
        darauf zieht der Practicar-Modus "frases"."""
        tags = ["seed", w["topic"]]
        if w.get("is_phrase"):
            tags.append("frase")
        return tags

    def seed_words_for_topic(self, user_id: str, topic: str) -> list[dict]:
        # select("*"): tolerant gegenüber Instanzen, auf denen Migration 004
        # (is_phrase/note) noch nicht gelaufen ist.
        words = (self.c.table("seed_vocab").select("*")
                 .eq("topic", topic).order("freq_rank").execute().data)
        mine = self._user_terms(user_id)
        return [{"id": w["id"], "term": w["term"], "translation": w["translation"],
                 "register": w["register"], "freq_rank": w["freq_rank"], "cefr": w["cefr"],
                 "is_phrase": bool(w.get("is_phrase")), "note": w.get("note"),
                 "added": w["term"] in mine} for w in words]

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
            source_capture_id=None, tags=self._seed_tags(w), source="seed",
        )
        return created

    def promote_daily_seed(self, user_id: str, quota: int = 10) -> int:
        """Bis zu N neue Grundwortschatz-Wörter pro Tag rücken automatisch ins SRS nach
        (nach Frequenz-Rang). Deterministisch; no-op wenn seed_vocab leer ist (lengua/es).
        Startet erst, wenn der Nutzer selbst angefangen hat (mindestens eine eigene
        Capture) — sonst ist der allererste Drill eine Seed-Kulisse statt seiner Wörter."""
        from datetime import datetime, timezone
        own = (self.c.table("captures").select("id", count="exact")
               .eq("user_id", user_id).neq("source", "onboarding")
               .limit(1).execute()).count or 0
        if own == 0:
            return 0
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
                    source_capture_id=None, tags=self._seed_tags(w), source="seed",
                )
                mine.add(w["term"])
                added += 1
            offset += 200
        return added

    # ---------- practicar (drill selection — pulls exactly where scoring wobbles) ----------
    @staticmethod
    def _source_weighted(base, limit: int) -> list[dict]:
        """Quellengewichtung (Punkt 4): selbst eingefangene Vokabeln (source != 'import')
        haben Vorrang vor importierten — ein Massenimport von hunderten Karten flutet die
        Auswahl nicht und verwässert den persönlichen Vorsprung nicht. Explizit über ZWEI
        Queries statt Zufall: erst die eigenen bis zum Limit, importierte füllen nur den Rest,
        jeweils in der von base() vorgegebenen SRS-Reihenfolge. base() liefert je Aufruf einen
        FRISCHEN Builder (ohne source-Filter) — supabase-py-Builder mutieren beim Filtern."""
        own = base().neq("source", "import").limit(limit).execute().data
        if len(own) >= limit:
            return own
        imported = base().eq("source", "import").limit(limit - len(own)).execute().data
        return own + imported

    def due_vocab_items(self, user_id: str, limit: int = 8,
                        phrases: bool | None = None) -> list[dict]:
        """SRS-due items. phrases=True → only intent-phrases, False → only words, None → both.
        Eigene vor importierten (Quellengewichtung)."""
        def base():
            q = (self.c.table("vocab_items").select("*")
                 .eq("user_id", user_id).lte("srs_due", "now()"))
            if phrases is True:
                q = q.contains("tags", ["frase"])
            elif phrases is False:
                q = q.not_.contains("tags", ["frase"])
            return q.order("srs_due")
        return self._source_weighted(base, limit)

    def warmup_vocab(self, user_id: str, limit: int = 15) -> list[dict]:
        """Fällige Vokabeln, die FAST sitzen — für den leichten Einstieg. Meiste Wiederholungen
        (höchste Vertrautheit) zuerst; das sind die sicheren, motivierenden Treffer. Eigene vor
        importierten — importierte starten kalt (reps 0) und würden den Einstieg sonst fluten."""
        def base():
            return (self.c.table("vocab_items").select("*")
                    .eq("user_id", user_id).lte("srs_due", "now()")
                    .order("srs_reps", desc=True).order("srs_due"))
        return self._source_weighted(base, limit)

    def situation_vocab(self, user_id: str, limit: int = 15) -> list[dict]:
        """Situationsvokabular (Regale) — für den Ausklang. Fällige zuerst (eigene vor
        importierten); wenn nichts fällig ist, trotzdem welche zeigen (der Ausklang soll nie
        leer sein). Jede Query frisch bauen — die supabase-py-Builder mutieren."""
        def due_base():
            return (self.c.table("vocab_items").select("*")
                    .eq("user_id", user_id).not_.is_("situation_id", "null")
                    .lte("srs_due", "now()").order("srs_due"))
        due = self._source_weighted(due_base, limit)
        if len(due) >= limit:
            return due
        rest = (self.c.table("vocab_items").select("*")
                .eq("user_id", user_id).not_.is_("situation_id", "null")
                .order("srs_due").limit(limit).execute().data)
        seen = {r["id"] for r in due}
        return due + [r for r in rest if r["id"] not in seen][: limit - len(due)]

    # ---------- daily_sessions (der eingefrorene 15-Minuten-Bogen) ----------
    def get_current_session(self, user_id: str, today: str) -> dict | None:
        """Die anzuzeigende Session: eine offene (auch von gestern — Fortsetzen, Mitternacht
        ersetzt nichts), sonst die heute abgeschlossene ('heute erledigt'), sonst None (→ neu)."""
        active = (self.c.table("daily_sessions").select("*")
                  .eq("user_id", user_id).eq("status", "active")
                  .order("session_date", desc=True).limit(1).execute().data)
        if active:
            return active[0]
        done = (self.c.table("daily_sessions").select("*")
                .eq("user_id", user_id).eq("session_date", today)
                .eq("status", "completed").limit(1).execute().data)
        return done[0] if done else None

    def create_daily_session(self, user_id: str, today: str, plan: list[dict],
                             headline: str, budget_seconds: int) -> dict:
        return (self.c.table("daily_sessions").insert({
            "user_id": user_id, "session_date": today, "plan": plan,
            "headline": headline, "budget_seconds": budget_seconds,
        }).execute().data[0])

    def get_session(self, user_id: str, session_id: str) -> dict | None:
        rows = (self.c.table("daily_sessions").select("*")
                .eq("user_id", user_id).eq("id", session_id).limit(1).execute().data)
        return rows[0] if rows else None

    def last_session_core_slug(self, user_id: str) -> str | None:
        """Kern-Konzept der zuletzt erzeugten Session (aus dem Plan) — damit ein Reroll nicht
        direkt dasselbe Konzept nochmal zieht."""
        rows = (self.c.table("daily_sessions").select("plan")
                .eq("user_id", user_id).order("created_at", desc=True).limit(1).execute().data)
        if not rows:
            return None
        for item in rows[0].get("plan") or []:
            if item.get("kind") in ("explain", "exercise"):
                return item.get("concept_slug")
        return None

    def save_session_progress(self, session_id: str, cursor: int, progress: list[dict]) -> None:
        (self.c.table("daily_sessions")
         .update({"cursor": cursor, "progress": progress}).eq("id", session_id).execute())

    def save_session_plan(self, session_id: str, plan: list[dict]) -> None:
        """Plan im Nachhinein erweitern/ersetzen (mehr Übungen anfragen / 'otra')."""
        self.c.table("daily_sessions").update({"plan": plan}).eq("id", session_id).execute()

    def complete_session(self, session_id: str) -> None:
        (self.c.table("daily_sessions")
         .update({"status": "completed", "completed_at": "now()"})
         .eq("id", session_id).execute())

    def clear_current_session(self, user_id: str, today: str) -> None:
        """'Session ändern' / reroll: die aktuelle Session wegräumen, damit neu gewürfelt wird.
        Trifft jede offene Session (auch ältere) und die heutige Zeile."""
        self.c.table("daily_sessions").delete().eq("user_id", user_id).eq("status", "active").execute()
        self.c.table("daily_sessions").delete().eq("user_id", user_id).eq("session_date", today).execute()

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

    # ---------- concept exercises (interaktive Übungen — Generierung LLM, Rest Code) ----------
    def insert_exercises(self, concept_id: str, items: list[dict], cefr: str | None) -> int:
        """Batch rein; grobe Dedup gegen bestehende Prompts desselben Kapitels."""
        existing = {e["prompt"] for e in self.exercises_for_concept(concept_id)}
        rows = [{"concept_id": concept_id, "etype": ex["etype"], "prompt": ex["prompt"],
                 "options": ex["options"], "answers": ex["answers"],
                 "explanation": ex["explanation"], "cefr": cefr}
                for ex in items if ex["prompt"] not in existing]
        if rows:
            self.c.table("concept_exercises").insert(rows).execute()
        return len(rows)

    def exercises_for_concept(self, concept_id: str) -> list[dict]:
        return (self.c.table("concept_exercises").select("*")
                .eq("concept_id", concept_id).order("created_at").execute().data)

    def get_exercise(self, exercise_id: str) -> dict | None:
        rows = (self.c.table("concept_exercises").select("*, concepts(id, slug)")
                .eq("id", exercise_id).execute().data)
        return rows[0] if rows else None

    def exercise_attempts(self, user_id: str, exercise_ids: list[str]) -> dict[str, dict]:
        """Pro Übung: Zahl der Versuche + ob der LETZTE korrekt war (für die Auswahl)."""
        if not exercise_ids:
            return {}
        rows = (self.c.table("exercise_attempts")
                .select("exercise_id, correct, answered_at")
                .eq("user_id", user_id).in_("exercise_id", exercise_ids)
                .order("answered_at").execute().data)
        out: dict[str, dict] = {}
        for r in rows:
            s = out.setdefault(r["exercise_id"], {"count": 0, "last_correct": None})
            s["count"] += 1
            s["last_correct"] = r["correct"]
        return out

    def log_exercise_attempt(self, user_id: str, exercise_id: str, correct: bool) -> None:
        self.c.table("exercise_attempts").insert({
            "user_id": user_id, "exercise_id": exercise_id, "correct": correct,
        }).execute()

    # ---------- temario (Grammatik-Katalog A1-B2 — geteilte Lektionen, Migration 017) ----------
    # Status kommt aus dem Connect Layer (concept_state über concept_slug), nie von hier.
    # Join in Python statt SQL-View — dasselbe Muster wie list_concepts_with_state.

    def _states_for_concept_slugs(self, user_id: str, slugs: list[str]) -> dict[str, dict]:
        """concept_slug → concept_state-Zeile dieses Nutzers (nur vorhandene)."""
        if not slugs:
            return {}
        concepts = (self.c.table("concepts").select("id, slug")
                    .in_("slug", slugs).execute().data)
        if not concepts:
            return {}
        by_id = {c["id"]: c["slug"] for c in concepts}
        states = (self.c.table("concept_state")
                  .select("concept_id, state, need_count, last_seen")
                  .eq("user_id", user_id).in_("concept_id", list(by_id)).execute().data)
        return {by_id[s["concept_id"]]: s for s in states}

    def list_grammar_topics_with_state(self, user_id: str) -> list[dict]:
        """Alle Topics (Niveau-Reihenfolge = Enum-Reihenfolge A1→B2) + Nutzer-Status +
        ob eine freigegebene Lektion existiert. Themen ohne Konzept bleiben 'sin_ver'."""
        topics = (self.c.table("grammar_topics")
                  .select("slug, level, title_es, subtitle_de, order_index, concept_slug")
                  .order("level").order("order_index").execute().data)
        reviewed = (self.c.table("grammar_lessons").select("topic_id, grammar_topics(slug)")
                    .eq("reviewed", True).execute().data)
        has_lesson = {r["grammar_topics"]["slug"] for r in reviewed if r.get("grammar_topics")}
        states = self._states_for_concept_slugs(
            user_id, [t["concept_slug"] for t in topics if t["concept_slug"]])
        out = []
        for t in topics:
            s = states.get(t["concept_slug"], {}) if t["concept_slug"] else {}
            out.append({**t,
                        "state": s.get("state", "sin_ver"),
                        "need_count": s.get("need_count", 0),
                        "has_lesson": t["slug"] in has_lesson})
        return out

    def get_grammar_topic_detail(self, user_id: str, slug: str) -> dict | None:
        """Ein Thema + seine jüngste FREIGEGEBENE Lektion (Review-Gate liegt hier in der
        Query — unreviewte Lektionen sind für die App unsichtbar) + Status + Konzept-Link."""
        rows = self.c.table("grammar_topics").select("*").eq("slug", slug).execute().data
        if not rows:
            return None
        topic = rows[0]
        lessons = (self.c.table("grammar_lessons").select("blocks, version, generated_at")
                   .eq("topic_id", topic["id"]).eq("reviewed", True)
                   .order("version", desc=True).limit(1).execute().data)
        concept = None
        if topic["concept_slug"]:
            c = (self.c.table("concepts").select("slug, label")
                 .eq("slug", topic["concept_slug"]).execute().data)
            concept = c[0] if c else None
        states = self._states_for_concept_slugs(user_id, [topic["concept_slug"]]) \
            if topic["concept_slug"] else {}
        s = states.get(topic["concept_slug"], {})
        return {"slug": topic["slug"], "level": topic["level"],
                "title_es": topic["title_es"], "subtitle_de": topic["subtitle_de"],
                "lesson": lessons[0] if lessons else None,
                "concept": concept,
                "state": s.get("state", "sin_ver"),
                "need_count": s.get("need_count", 0)}

    # ---------- escucha (Hörverstehen — Text aus eigenen Vokabeln, MC-Fragen) ----------
    def listening_target_terms(self, user_id: str, n: int = 6) -> list[str]:
        """Zielwörter für einen Hörtext: erst fällige SRS-Wörter, dann restliches eigenes
        Vokabular, zur Not Grundwortschatz — damit auch früh genug Material da ist."""
        terms: list[str] = []
        for r in self.due_vocab_items(user_id, limit=n, phrases=False):
            if r["term"] not in terms:
                terms.append(r["term"])
        if len(terms) < 3:
            rows = (self.c.table("vocab_items").select("term")
                    .eq("user_id", user_id).not_.contains("tags", ["frase"])
                    .order("created_at", desc=True).limit(n).execute().data)
            for r in rows:
                if r["term"] not in terms:
                    terms.append(r["term"])
        if len(terms) < 3:
            rows = (self.c.table("seed_vocab").select("term")
                    .eq("is_phrase", False).order("freq_rank").limit(n).execute().data)
            for r in rows:
                if r["term"] not in terms:
                    terms.append(r["term"])
        return terms[:n]

    def create_listening_item(self, user_id: str, passage: str, gist: str,
                              questions: list, audio_b64: str | None = None,
                              audio_media_type: str | None = None) -> str:
        """Audio wird mit abgelegt (Migration 015), damit ein unbeantworteter Hörtext beim
        nächsten Aufruf wiederverwendet wird statt neu zu generieren (Text- + TTS-Call).
        Fallback ohne Audio-Spalten, solange die Migration noch nicht gelaufen ist."""
        base = {"user_id": user_id, "passage": passage, "gist": gist, "questions": questions}
        if audio_b64:
            try:
                row = self.c.table("listening_items").insert(
                    {**base, "audio_b64": audio_b64,
                     "audio_media_type": audio_media_type or "audio/mpeg"}).execute().data[0]
                return row["id"]
            except Exception:
                pass  # Spalten fehlen noch → altes Verhalten
        row = self.c.table("listening_items").insert(base).execute().data[0]
        return row["id"]

    def get_listening_item(self, item_id: str, user_id: str) -> dict | None:
        rows = (self.c.table("listening_items").select("*")
                .eq("id", item_id).eq("user_id", user_id).execute().data)
        return rows[0] if rows else None

    def get_reusable_listening_item(self, user_id: str) -> dict | None:
        """Jüngster unbeantworteter Hörtext MIT gespeichertem Audio — wird erneut serviert,
        statt pro Seitenbesuch Text + TTS neu zu generieren. None, solange die
        Audio-Spalten (Migration 015) fehlen oder nichts Wiederverwendbares da ist."""
        try:
            rows = (self.c.table("listening_items").select("*")
                    .eq("user_id", user_id).is_("answered_at", "null")
                    .not_.is_("audio_b64", "null")
                    .order("created_at", desc=True).limit(1).execute().data)
        except Exception:
            return None
        return rows[0] if rows else None

    def mark_listening_answered(self, item_id: str) -> None:
        try:
            self.c.table("listening_items").update(
                {"answered_at": "now()"}).eq("id", item_id).execute()
        except Exception:
            pass  # Spalte fehlt noch (vor Migration 015) — dann eben kein Reuse-Tracking

    # ---------- hablar (Speaking Bot; Tabellen aus Migration 012) ----------
    # Der Bot (lengua-bot, Railway) schreibt diese Tabellen per Service-Key;
    # hier wird nur gelesen. Audio liegt als bucket-relativer Pfad im privaten
    # Bucket speaking-audio — Auslieferung über signierte URLs.

    def list_speaking_sessions(self, user_id: str, limit: int = 50) -> list[dict]:
        return (self.c.table("speaking_sessions")
                .select("id, created_at, duration_sec, transcript")
                .eq("user_id", user_id)
                .order("created_at", desc=True).limit(limit).execute().data)

    def get_speaking_session(self, user_id: str, session_id: str) -> dict | None:
        rows = (self.c.table("speaking_sessions").select("*")
                .eq("id", session_id).eq("user_id", user_id).execute().data)
        return rows[0] if rows else None

    def list_speaking_errors(self, user_id: str, session_ids: list[str]) -> list[dict]:
        if not session_ids:
            return []
        return (self.c.table("error_log")
                .select("session_id, error_type, original, corrected, explanation,"
                        " char_start, char_end")
                .eq("user_id", user_id).in_("session_id", session_ids)
                .execute().data)

    def list_speaking_chunks(self, user_id: str, session_id: str | None = None) -> list[dict]:
        q = (self.c.table("speaking_chunks")
             .select("id, session_id, chunk_es, example_es, trigger_de, status, activated_at")
             .eq("user_id", user_id))
        if session_id is not None:
            q = q.eq("session_id", session_id)
        return q.execute().data

    def speaking_error_counts(self, user_id: str, days: int = 14) -> dict[str, int]:
        from datetime import datetime, timedelta, timezone
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        rows = (self.c.table("error_log").select("error_type")
                .eq("user_id", user_id).gte("created_at", cutoff).execute().data)
        counts: dict[str, int] = {}
        for r in rows:
            counts[r["error_type"]] = counts.get(r["error_type"], 0) + 1
        return counts

    def count_open_speaking_chunks(self, user_id: str) -> int:
        res = (self.c.table("speaking_chunks").select("id", count="exact")
               .eq("user_id", user_id).eq("status", "open").execute())
        return res.count or 0

    def speaking_audio_url(self, path: str, expires_sec: int = 3600) -> str | None:
        try:
            res = self.c.storage.from_("speaking-audio").create_signed_url(path, expires_sec)
            return res.get("signedURL") or res.get("signedUrl")
        except Exception:
            return None
