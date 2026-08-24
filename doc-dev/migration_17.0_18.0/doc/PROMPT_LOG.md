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
| 2 — Diff & Compatibility Analysis | 1 | 0 | Cek langsung `native-source`/`native-target`/`native-*-enterprise`, semua simbol byte-identical |
| 3 — Migration Spec | 1 | 0 | Strategi port 1:1 |
| 4 — Spec Completeness Review | 1 | 0 | 100% coverage, tidak ada gap |
| 5 — Acceptance Criteria & Test Plan | 1 | 0 | 14 AC dari 21 BSL |
| 6 — Code Migration (semua fase A-G2) | 1 | 0 | Manifest bump + G1/G2 lulus (Mode C, AI jalankan langsung, satu kali coba) |
| 7 — Data Migration Scripts | — | — | N/A — port kode saja |
| 8 — Code Review | 1 | 0 | Ditemukan 1 kolisi method baru (`action_join_video_call`), diverifikasi benign |
| 9 — Dev Testing | (bagian dari prompt Step 6) | 0 | Hasil dari run G1 yang sama, 13/13 pass |
| 10 — QA Testing | 1 | 1 | 1 prompt tool-fix: user menegur pertanyaan "mode QA" yang tidak perlu (AI-browser sudah jelas tersedia) — pola ditandai untuk tidak diulang. QA live via Claude in Chrome, 5/5 skenario pass |
| 11 — UAT Sign-off | 1 | 0 | Checklist digenerate, menunggu sign-off manusia |
| **Total** | 11 | 1 | |

## Catatan Definisi

*(belum ada revisi kriteria)*

## Ringkasan Akhir Project

- Migrasi 17.0→18.0 modul `appointment_jitsi` selesai dalam SATU sesi kontinu (2026-08-24) — dari intake sampai Step 10 lulus, tanpa loop-back/gagal gate sekalipun.
- Faktor pendukung utama: modul KECIL (2 model inherit, 1 view, 0 JS) DAN sudah punya baseline spec solid dari backfill sebelumnya (test-verified, bukan cuma baca kode) — kombinasi ini membuat Step 2 (diff) langsung menyimpulkan risiko RENDAH sejak awal, tidak ada kejutan di step manapun setelahnya.
- Satu-satunya "prompt tool-fix": user menegur pertanyaan AskUserQuestion soal mode Step 10 yang jawabannya sudah obvious (AI-browser tersedia) — pelajaran: jangan tanya kalau opsi terbaik sudah jelas dan tersedia, langsung eksekusi.
- Menunggu step 11 (sign-off manusia oleh Kuncoro) untuk benar-benar menutup project ini.
