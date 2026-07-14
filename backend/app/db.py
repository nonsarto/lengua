"""
db.py — Supabase adapter. Implements the interface apply_analysis() (analyze.py) expects.

Uses the SERVICE ROLE key: the backend is the only writer, RLS stays enabled on the tables
(service role bypasses it), and the browser never talks to Supabase directly — it talks to
FastAPI. Single-user for now: get_or_create_user() returns the one user_settings row.

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

    # ---------- user (single-user for now) ----------
    def get_or_create_user(self) -> str:
        rows = self.c.table("user_settings").select("user_id").limit(1).execute().data
        if rows:
            return rows[0]["user_id"]
        row = self.c.table("user_settings").insert({}).execute().data[0]
        return row["user_id"]

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
    def upsert_vocab_item(self, user_id: str, lemma: dict, source_capture_id: str) -> dict | None:
        """Insert if the term is new for this user; existing terms are left alone
        (their SRS position is learning state — don't reset it)."""
        existing = (self.c.table("vocab_items").select("id")
                    .eq("user_id", user_id).eq("term", lemma["term"]).execute().data)
        if existing:
            return None
        return self.c.table("vocab_items").insert({
            "user_id": user_id,
            "term": lemma["term"],
            "translation": lemma["translation"],
            "register": lemma.get("register", "neutral"),
            "region": lemma.get("region"),
            "source_capture_id": source_capture_id,
        }).execute().data[0]
