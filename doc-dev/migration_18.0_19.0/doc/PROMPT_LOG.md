# Prompt Log — appointment_jitsi

**Tujuan:** data empiris untuk `ai-doc/ROADMAP.md` Fase 5 (Otomasi Bertahap) — mengukur seberapa sering user harus prompt untuk **flow normal** migrasi vs prompt **tool-fix**, per step.

**Cross-cutting** — hidup di root `doc/`.

---

## Klasifikasi

- **Normal** — prompt yang menjalankan/melanjutkan salah satu dari 11 step, atau review/verifikasi konten migrasi modul ini.
- **Tool-fix** — prompt yang hasilnya perubahan ke `migration-tool/templates/`, `migration-tool/ai-doc/`, atau proses SOP itu sendiri.
- **Tidak dihitung** — orientasi murni.
- Satu prompt user = satu unit hitung.

## Log per Step

| Step | # Prompt Normal | # Prompt Tool-fix | Catatan |
|---|---|---|---|
| 0 — Bootstrap (sebelum step 1 resmi) | 1 | 0 | Prompt awal dev ("migrasi 18 ke 19, branch target migration/19.0_target, source copy dari migration/18.0") memicu seluruh bootstrap: pre-flight Mode Git (tanya GUI client — dijawab sudah tertutup), fetch, checkout -b, clone source-codebase sibling + verifikasi persistensi, instantiasi `CLAUDE.md`/`.claude/settings.json`/`.gitignore`. |
| 1 — Intake & Baseline Spec | 1 | 0 | Satu putaran `AskUserQuestion` (3 pertanyaan: sifat migrasi, source aktif dikembangkan, dependency OCA) dijawab semua dengan opsi Recommended — dihitung sebagai 1 prompt normal (gate konfirmasi awal, bukan tool-fix). |
| 2 — Diff & Compatibility Analysis | | | |
| 3 — Migration Spec | | | |
| 4 — Spec Completeness Review | | | |
| 5 — Acceptance Criteria & Test Plan | | | |
| 6 — Code Migration (semua fase A-G2) | | | |
| 7 — Data Migration Scripts | | | — (n/a, port kode saja) |
| 8 — Code Review | | | |
| 9 — Dev Testing | | | |
| 10 — QA Testing | | | |
| 11 — UAT Sign-off | | | |
| **Total** | 2 | 0 | |

## Catatan Definisi

*(belum ada revisi kriteria di project ini)*

## Ringkasan Akhir Project (isi setelah step 11 selesai)

- Step dengan rasio Tool-fix tertinggi: ...
- Step yang paling "bersih": ...
- Lihat `ai-doc/ROADMAP.md` §5 di `migration-tool`.
