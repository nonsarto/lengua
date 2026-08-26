"use client";

/**
 * Transkript mit Inline-Markierungen aus drei Quellen (Offsets gegen das
 * ORIGINAL-Transkript, nie die korrigierte Fassung):
 *   - error:   error_log char_start/char_end        → rot
 *   - de:      deutsche Wörter (client-seitig via trigger_de gematcht) → amber
 *   - lowconf: low_conf_spans der Transkription     → gepunktete Unterstreichung
 * Zwei verschiedene Dinge, zwei Farben (Fehler ≠ fehlende Vokabel).
 *
 * segmentSpans() schneidet den Text an allen Span-Grenzen in atomare Segmente —
 * verkraftet damit beliebige Überlappungen ohne verschachtelte Elemente.
 */

export type Span = { start: number; end: number; kind: "error" | "de" | "lowconf" };

export function segmentSpans(text: string, spans: Span[]) {
  const valid = spans.filter(
    (s) => s.start != null && s.end != null && s.start >= 0 && s.end <= text.length && s.start < s.end
  );
  const bounds = new Set<number>([0, text.length]);
  for (const s of valid) {
    bounds.add(s.start);
    bounds.add(s.end);
  }
  const sorted = [...bounds].sort((a, b) => a - b);
  const segments: { text: string; kinds: Set<Span["kind"]> }[] = [];
  for (let i = 0; i < sorted.length - 1; i++) {
    const [a, b] = [sorted[i], sorted[i + 1]];
    const kinds = new Set<Span["kind"]>();
    for (const s of valid) if (s.start <= a && b <= s.end) kinds.add(s.kind);
    segments.push({ text: text.slice(a, b), kinds });
  }
  return segments;
}

const norm = (s: string) =>
  s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

const DE_ARTICLES = new Set(["der", "die", "das", "den", "dem", "des", "ein", "eine", "einen"]);

/** Deutsche Wörter im Transkript finden: trigger_de-Tokens (ohne Artikel),
 *  akzent-/case-insensitiv. Chunks tragen keine Offsets — daher Matching hier. */
export function germanSpans(text: string, triggers: (string | null)[]): Span[] {
  const spans: Span[] = [];
  const normText = norm(text);
  for (const trigger of triggers) {
    if (!trigger) continue;
    for (const token of trigger.split(/\s+/)) {
      const t = norm(token);
      if (t.length < 3 || DE_ARTICLES.has(t)) continue;
      let from = 0;
      while (true) {
        const idx = normText.indexOf(t, from);
        if (idx === -1) break;
        spans.push({ start: idx, end: idx + t.length, kind: "de" });
        from = idx + t.length;
      }
    }
  }
  return spans;
}

const SEGMENT_STYLE: Record<string, string> = {
  error: "bg-red-50 underline decoration-red-400 decoration-2 underline-offset-2",
  de: "bg-amber-100 rounded-sm",
  lowconf: "underline decoration-dotted decoration-stone-400 underline-offset-4",
};

export default function TranscriptHighlights({ text, spans }: { text: string; spans: Span[] }) {
  const segments = segmentSpans(text, spans);
  return (
    <p className="whitespace-pre-wrap leading-relaxed">
      {segments.map((seg, i) =>
        seg.kinds.size === 0 ? (
          <span key={i}>{seg.text}</span>
        ) : (
          <span key={i} className={[...seg.kinds].map((k) => SEGMENT_STYLE[k]).join(" ")}>
            {seg.text}
          </span>
        )
      )}
    </p>
  );
}
