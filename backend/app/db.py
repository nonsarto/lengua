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
