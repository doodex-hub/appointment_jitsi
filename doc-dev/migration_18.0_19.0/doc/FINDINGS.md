# Findings — appointment_jitsi (migrasi 18.0 → 19.0)

> **Cross-cutting, direkomendasikan (tidak kondisional)** — dokumen konsolidasi TUNGGAL untuk semua
> gap/bug/ambiguitas yang butuh keputusan manusia selama migrasi, supaya user tidak perlu buka
> `01b_BASELINE_SPEC.md`/`03_MIGRATION_SPEC.md`/`04_SPEC_COMPLETENESS_REVIEW.md`/`08_CODE_REVIEW.md`
> satu per satu untuk tahu apa yang masih terbuka. Hidup di root `doc/` (sejajar `PROMPT_LOG.md`).

**Modul:** appointment_jitsi
**Migrasi:** 18.0 → 19.0
**Terakhir update:** 2026-08-26

---

## Beda Peran dari Mekanisme Lain (jangan bingung/duplikat)

| Mekanisme | Kapan dipakai | Sifat |
|---|---|---|
| Format `ESCALATION` (`CLAUDE.md`) | Isu **blocking** — butuh keputusan user SEBELUM lanjut ke step/fase berikutnya | Sinkron, muncul di respons AI saat itu juga |
| Tag `[GAP]` di `01b_BASELINE_SPEC.md` | Penyimpangan spec lama vs kode aktual, per-klaim `BSL-NNN` | Inline, granular per klaim |
| Section Gap di `04_SPEC_COMPLETENESS_REVIEW.md` / `08_CODE_REVIEW.md` | Gap spesifik di titik gate itu | Inline, per dokumen |
| **`FINDINGS.md` (file ini)** | **Semua finding lintas step (1-11) yang butuh keputusan manusia** | Living document, append-only |

**Catatan prefix `MF-`:** modul ini juga pernah lewat migrasi 17.0→18.0 (`doc-dev/migration_17.0_18.0/doc/`, tidak ada `FINDINGS.md` cross-cutting terpisah di project itu — findings-nya tercatat di `CLAUDE.md` §Ringkasan) dan `doc-dev/backfill/FINDINGS.md` (skema `F-NNN`, 13 temuan F-01..F-13). File ini pakai skema `MF-NNN` sendiri untuk pasangan versi 18.0→19.0, tidak menimpa/menomori ulang `F-NNN` backfill.

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| — | Belum ada finding baru khusus 18.0→19.0 per akhir Step 1 | — | — | — | — |

**Finding yang DIWARISI dari project sebelumnya (bukan finding baru, dicatat sebagai referensi — detail lengkap di `01b_BASELINE_SPEC.md`):** 13 bug/quirk asal backfill (`F-01`..`F-13`, terutama `F-13`/`BSL-015` — email Jitsi tidak pernah aktif) semuanya WAJIB dipertahankan bug-for-bug di 19.0, sudah dikonfirmasi dev di `01a_MIGRATION_INTAKE.md` §Ringkasan poin 5. Tidak dicatat ulang sebagai `MF-NNN` di sini kecuali muncul keputusan BARU yang berbeda dari keputusan 17.0→18.0.

---

## Detail

*(belum ada entry `MF-NNN` — akan diisi begitu step manapun menemukan gap/bug/ambiguitas yang butuh keputusan manusia)*

---

## Cara Pakai

1. Update SETIAP KALI step manapun (1-11) menemukan gap/bug/ambiguitas yang butuh keputusan manusia — jangan tunggu sampai akhir project.
2. ID `MF-NNN` sequential, tidak pernah dipakai ulang.
3. Finding yang diwarisi dari bug/quirk source ditag `[DIWARISI-SOURCE]`. Finding yang genuinely muncul KARENA migrasi (breaking change 19.0) ditag `[GAP-MIGRASI]`, referensi `DIFF-NNN` dari `02_DIFF_ANALYSIS.md`.
4. Step 4 dan Step 8 WAJIB baca file ini sebagai bagian gate.
