# Prompt Log — appointment_jitsi (19.0 → 20.0)

**Tujuan:** data empiris untuk `ai-doc/ROADMAP.md` Fase 5 — prompt **Normal** vs **Tool-fix** per step. Definisi klasifikasi: `migration-tool/templates/PROMPT_LOG.md`.

---

## Log per Step

| Step | # Prompt Normal | # Prompt Tool-fix | Catatan |
|---|---|---|---|
| 0 — Bootstrap/Conditioning | — | — | Sesi conditioning terpisah (2026-09-24), tidak dihitung di sesi ini |
| 1 — Intake & Baseline Spec | 1 | 0 | Prompt kickoff tunggal ("migrasi 19→20, jalan terus sampai Step 9, STOP sebelum Step 10") + 1 batch `AskUserQuestion` (4 pertanyaan intake, semua dijawab opsi rekomendasi) |
| 2 — Diff & Compatibility Analysis | 0 | 0 | Jalan terus dari prompt kickoff |
| 3 — Migration Spec | 0 | 0 | |
| 4 — Spec Completeness Review | 0 | 0 | |
| 5 — Acceptance Criteria & Test Plan | 0 | 0 | |
| 6 — Code Migration (A-G2) | 0 | 0 | |
| 7 — Data Migration Scripts | — | — | N/A (port kode saja) |
| 8 — Code Review | 0 | 0 | |
| 9 — Dev Testing | 0 | 0 | |
| 10 — QA Testing | 2 | 0 | "pertanyaan kurang tegas? status" (AI merumuskan ulang 2 keputusan jadi pertanyaan ya/tidak) + "1,2 YA, lanjut step 10" (MF-01 disetujui + izin slot Step 10) |
| 11 — UAT Sign-off | 2 | 0 | "apa pertanyaan?" (klarifikasi) + "YA" (izin draft Step 11) |
| **Total** | 5 | 0 | |

## Catatan Definisi

*(belum ada revisi kriteria)*

## Ringkasan Akhir Project (isi setelah step 11 selesai)

- ...
