-- Capturar versteht einzelne Wörter (es ODER de) als Nachschlage-Intention:
-- neuer Modus "word" → Übersetzung als Microdose, Lemma wandert ins Vokabular
-- (Dedup über get_or_create_vocab_item). Auf BEIDEN Instanzen ausführen.
alter type capture_kind add value if not exists 'word';
