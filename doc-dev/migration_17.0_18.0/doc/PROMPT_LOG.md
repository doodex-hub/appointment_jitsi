# Prompt Log — appointment_jitsi

**Tujuan:** data empiris untuk `migration-tool/ai-doc/ROADMAP.md` Fase 5 (Otomasi Bertahap).

---

## Klasifikasi

- **Normal** — prompt yang menjalankan/melanjutkan salah satu dari 11 step, atau review/verifikasi konten migrasi modul ini.
- **Tool-fix** — prompt yang hasilnya perubahan ke `migration-tool/templates/`, `migration-tool/ai-doc/`, atau proses SOP itu sendiri.
- **Tidak dihitung** — orientasi murni, basa-basi non-actionable.

## Log per Step

| Step | # Prompt Normal | # Prompt Tool-fix | Catatan |
|---|---|---|---|
| 0 — Bootstrap (sebelum step 1 resmi) | 1 | 0 | "Lakukan migrasi" — kickoff project, bootstrap sudah dijalankan dev sebelumnya (`.claude/settings.json`/`.gitignore`) |
| 1 — Intake & Baseline Spec | 3 | 0 | Investigasi folder referensi (source-codebase, native-*, enterprise), konfirmasi versi/branch/sifat migrasi via AskUserQuestion (3 putaran), keputusan bug-for-bug (F-13 + F-01..F-12), setup branch `migration/17.0_source`/`migration/18.0_target`, tulis `CLAUDE.md`/`01a`/`01b`/`FINDINGS.md`/`PROMPT_LOG.md` |
| 2 — Diff & Compatibility Analysis | | | |
| 3 — Migration Spec | | | |
| 4 — Spec Completeness Review | | | |
| 5 — Acceptance Criteria & Test Plan | | | |
| 6 — Code Migration (semua fase A-G2) | | | |
| 7 — Data Migration Scripts | | | N/A — port kode saja |
| 8 — Code Review | | | |
| 9 — Dev Testing | | | |
| 10 — QA Testing | | | |
| 11 — UAT Sign-off | | | |
| **Total** | 4 | 0 | |

## Catatan Definisi

*(belum ada revisi kriteria)*

## Ringkasan Akhir Project

*(diisi setelah step 11 selesai)*
