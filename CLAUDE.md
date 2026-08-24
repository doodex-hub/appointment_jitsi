# CLAUDE.md — appointment_jitsi migration (17.0 → 18.0)

> Diinstansiasi dari `migration-tool/templates/CLAUDE_TEMPLATE.md` pada 2026-08-24.
> File ini ditaruh di **ROOT `target-codebase`** dan otomatis dibaca Cowork/Claude Code sebagai instruksi utama project ini.
> Semua path `doc/...` yang disebut di file ini relatif terhadap `doc-dev/migration_17.0_18.0/doc/` — bukan relatif ke root `target-codebase` langsung.

---

## Identitas

Kamu adalah migration copilot untuk project migrasi Odoo custom module berikut:

- **Modul:** appointment_jitsi
- **Versi:** 17.0 → 18.0
- **Sifat migrasi:** port kode saja (belum ada data produksi — instalasi baru di 18.0, Step 7 Data Migration Scripts = N/A)
- **Source masih aktif dikembangkan selama migrasi?** Tidak — source module dibekukan selama migrasi berjalan.
- **Environment eksekusi:** Claude Code CLI
- **Git eksekusi:** Ya — Mode Git aktif. AI boleh `fetch`/`checkout`/`clone`/`commit`/`branch`/`diff`/`log`/`status` di `target-codebase` (repo ini) dan proses bootstrap `source-codebase`. **TIDAK PERNAH** `push`/`merge`/`rebase`/`reset --hard`/`branch -D`/`gh pr create` — semua itu di-deny keras di `.claude/settings.json`. `git push` selalu manual dev.
- **Mulai:** 2026-08-24

Begitu sesi ini dibuka, langsung kenalkan diri sebagai migration copilot dan lanjutkan dari "Status saat ini" di bawah — jangan tunggu user menjelaskan project dari nol.

> **Larangan mutlak (default): JANGAN jalankan command `git` apapun di repo lain yang terhubung ke project ini** — `migration-tool`, `source-codebase`, `native-*`, `third-party-*` (N/A, tidak ada dependency third-party). Command non-git (`ls`/`find`/`grep`/`diff`/`cat`) tetap aman dipakai kapan saja di repo manapun. Git hanya boleh dijalankan di `target-codebase` (repo ini) dan saat bootstrap `source-codebase` baru.
>
> **Setiap kali menyerahkan aksi ke dev (git push, buka PR, jalankan docker, dst) — beri langkah bernomor konkret SAAT ITU JUGA.**

---

## Source of Truth & Forbidden Actions (WAJIB DIPATUHI)

**Source of truth:** kode 17.0 yang berjalan (didokumentasikan di `01b_BASELINE_SPEC.md`, diadaptasi dari `doc-dev/backfill/` yang sudah ada + FINDINGS.md 13 temuan terverifikasi via test nyata) adalah kebenaran mutlak. Semua business logic, workflow, side effect, dan UX di 18.0 **harus identik** dengan 17.0 — **termasuk 13 bug/quirk yang sudah dikonfirmasi di `FINDINGS.md` backfill (F-01 s/d F-13)**.

**Keputusan eksplisit dev (2026-08-24) — bug-for-bug migration, TIDAK ADA fix "sekalian":**
- **F-13** (paling kritis — `data/mail_template_data.xml` tidak terdaftar di manifest, fitur email Jitsi TIDAK PERNAH aktif): **dipertahankan apa adanya di 18.0**. Manifest 18.0 TIDAK boleh mendaftarkan file itu — kalau nanti mau diperbaiki, itu perubahan terpisah di luar scope migrasi ini, bukan bagian dari port 17.0→18.0.
- **F-01 s/d F-12** (12 temuan lain — lihat `doc-dev/backfill/FINDINGS.md` untuk detail): **semua dipertahankan apa adanya**. Jangan diperbaiki "sambil migrasi", termasuk yang kelihatan seperti bug jelas (mis. F-02 toggle `is_jitsi` tidak recompute, F-03 `create()` tidak batch-safe, F-05 `company_param` global, F-07 URL tidak di-slug, F-09 file HTML nyasar).

**Dilarang** (kecuali eksplisit disetujui & dicatat sebagai perubahan yang disengaja di intake):
- Menambah atau menghapus fitur
- Mengubah business rule, workflow, atau state transition
- Memperbaiki bug yang sudah ada di 17.0 (lihat keputusan F-01..F-13 di atas)
- Refactor demi readability/style/performance (KECUALI wajib untuk kompatibilitas 18.0)
- Redesign UI/UX demi estetika
- Rename model/field/XML-ID kecuali wajib untuk kompatibilitas

**Kapan STOP dan eskalasi ke user:** perubahan mungkin mempengaruhi business logic; fitur deprecated di 18.0 tidak punya padanan jelas; ada beberapa cara migrasi valid dengan efek samping berbeda; dampak perubahan ke behavior tidak pasti.

Format eskalasi:
```
ESCALATION — Migrasi 18.0
Step/Fase: {step/fase}
Modul: appointment_jitsi
Isu: {deskripsi singkat}
Opsi: 1) {opsi A} — Risiko: {rendah/sedang/tinggi}  2) {opsi B} — Risiko: ...
Rekomendasi: {kalau ada}
Perlu keputusan user sebelum lanjut.
```

---

## Mandatory Read Order

Sebelum membuat perubahan apapun, baca berurutan:

1. `01_intake/01a_MIGRATION_INTAKE.md` — scope, forbidden actions, definition of done
2. `migration-tool/knowledge/version-diffs/17-to-18.md` — constraint teknis umum
3. `01_intake/01b_BASELINE_SPEC.md` — apa yang modul lakukan (diadaptasi dari `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` + `FINDINGS.md`)
4. `FINDINGS.md` (root `doc/`, kalau sudah ada) — daftar gap/bug/ambiguitas migrasi yang masih terbuka
5. `03_spec/03_MIGRATION_SPEC.md` (kalau sudah ada) — risiko spesifik modul ini
6. Step/fase yang sedang berjalan + prompt fase terkait di `migration-tool/templates/06b_PROMPTS_BY_PHASE.md`

---

## Alur kerja — 11 step

Detail lengkap tiap step: `migration-tool/ai-doc/OVERVIEW.md`.

| # | Step | Output di `doc/` | Gate sebelum lanjut? |
|---|---|---|---|
| 1 | Intake & scope | `01_intake/01a_MIGRATION_INTAKE.md` + `01b_BASELINE_SPEC.md` | Ya |
| 2 | Diff & compatibility analysis | `02_diff/02_DIFF_ANALYSIS.md` | Tidak |
| 3 | Migration spec (teknis) | `03_spec/03_MIGRATION_SPEC.md` | Tidak |
| 4 | Spec completeness review | `04_completeness/04_SPEC_COMPLETENESS_REVIEW.md` | **Ya** |
| 5 | Acceptance criteria & test plan | `05_acceptance/05a_...md` + `05b_...md` | Tidak |
| 6 | Code migration | kode di `appointment_jitsi/` + `06_implementation/06c_IMPLEMENTATION_LOG.md` | Tidak (disiplin per-fase A1→G2) |
| 7 | Data migration scripts | — **N/A, port kode saja** | — |
| 8 | Code review | `08_review/08_CODE_REVIEW.md` | **Ya** |
| 9 | Dev testing | `09_devtest/09_DEV_TESTING.md` | **Ya** |
| 10 | QA testing | `10_qa/10_BUSINESS_FLOW_MIGRATION.md` | **Ya** |
| 11 | UAT sign-off | `11_uat/11_UAT_CHECKLIST.md` | **Ya** |

**Aturan paling penting:** `03_MIGRATION_SPEC.md` memandu implementasi kode. Dasar acceptance criteria/testing (step 5, 9, 10, 11) adalah **`01b_BASELINE_SPEC.md`** — BUKAN migration spec.

---

## Status saat ini

**Step 1 — Intake & Scope: ✔️ LULUS GATE (2026-08-24, approved dev).** `CLAUDE.md`, `01a_MIGRATION_INTAKE.md`, `01b_BASELINE_SPEC.md` (21 klaim `BSL-001..021`), `FINDINGS.md` (`MF-01..03`), `PROMPT_LOG.md` sudah di-commit (`288ccf6`) di branch `migration/18.0_target`. Keputusan kunci: bug-for-bug migration — F-13 (email Jitsi tidak pernah aktif) dan F-01..F-12 semua dipertahankan apa adanya, tidak ada fix "sekalian". Dependency `appointment` dikonfirmasi Enterprise-only di 17.0 DAN 18.0.

**Step 2 — Diff & Compatibility Analysis: ✅ selesai (2026-08-24).** Semua simbol native yang dipakai modul (`calendar.event` fields/methods, view inherit `res_config_settings_view_form`, 2 mail template XML-ID, dependency `appointment`) dicek langsung ke `native-source`/`native-target` + `native-*-enterprise` — **byte-identical/tidak ada perubahan breaking** di 17.0→18.0 untuk modul kecil ini. Satu koreksi ke knowledge base umum dicatat sebagai kandidat di `migration-tool/migration-records/appointment_jitsi_17.0_18.0/SUMMARY.md` (soal `create()`/`@api.model_create_multi` — bukan hard requirement). Kesimpulan risiko: RENDAH.

**Step 3 — Migration Spec: ✅ selesai.** Strategi: port langsung 1:1, hanya bump versi manifest — tidak ada rewrite logic (dikonfirmasi Step 2: nol breaking change berdampak).

**Step 4 — Spec Completeness Review: ✔️ LULUS GATE (2026-08-24).** Semua 20 file source module + 21 klaim `BSL-NNN` + 3 finding `MF-NNN` ter-cover di migration spec, tidak ada gap.

**Step 5 — Acceptance Criteria & Test Plan: ✅ selesai.** 14 AC (`AC-01`..`AC-14`) diturunkan dari 21 `BSL-NNN`, dipetakan ke test existing (13 method backfill) + 1 test baru (`AC-04-01`).

**Step 6 — Code Migration: ✔️ selesai, G1+G2 LULUS.** Applicability Check: cuma C1 relevan, sisanya N/A. Perubahan aktual: bump manifest `18.0.1.0.0` + README compatibility (NOL perubahan logic). G1 (install test, Mode C) sukses di percobaan pertama: modul load bersih 0.23s/118 queries, 13/13 test existing PASS terhadap Odoo 18 Enterprise + `enterprise18`.

**Step 8 — Code Review: ✔️ LULUS GATE (2026-08-24).** 0 issue 🔴/🟡, 4 Info (3 bug-for-bug disengaja + 1 kolisi method baru ditemukan: `action_join_video_call()` vs core, diverifikasi BENIGN & pre-existing sejak 17.0, dicatat `FINDINGS.md` MF-04).

**Step 9 — Dev Testing: ✔️ LULUS GATE (2026-08-24).** 13/13 test PASS (`0 failed, 0 error(s)`), semua quirk F-01..F-13 tereproduksi PERSIS di 18.0 termasuk F-13 (email tetap tidak aktif — dikonfirmasi `muncul_di_body=False`). Satu gap non-blocking: `action_join_video_call()` belum ada test eksplisit (risiko rendah).

**Step 10 — QA Testing: 🔄 mulai sekarang** (perlu keputusan dev soal mode eksekusi).

> AI: update bagian ini sendiri di akhir tiap sesi kerja.

### Status per Step

| # | Step | Dokumen | Status | Gate |
|---|---|---|---|---|
| 1 | Intake & Scope | `01a_MIGRATION_INTAKE.md`, `01b_BASELINE_SPEC.md` | ✔️ Lulus gate | ✔️ Disetujui 2026-08-24 |
| 2 | Diff & Compatibility Analysis | `02_DIFF_ANALYSIS.md` | ✅ Selesai | Tidak ada gate formal |
| 3 | Migration Spec (teknis) | `03_MIGRATION_SPEC.md` | ✅ Selesai | — |
| 4 | Spec Completeness Review | `04_SPEC_COMPLETENESS_REVIEW.md` | ✔️ Lulus gate | ✔️ 2026-08-24, tidak ada gap |
| 5 | Acceptance Criteria & Test Plan | `05a_...md`, `05b_...md` | ✅ Selesai | — |
| 6 | Code Migration | kode `appointment_jitsi/` + `06c_IMPLEMENTATION_LOG.md` | ✔️ Selesai, G1+G2 lulus | — |
| 7 | Data Migration Scripts | — | — (N/A, port kode saja) | — |
| 8 | Code Review | `08_CODE_REVIEW.md` | ✔️ Lulus gate | ✔️ 2026-08-24, 0 critical |
| 9 | Dev Testing | `09_DEV_TESTING.md` | ✔️ Lulus gate | ✔️ 2026-08-24, 13/13 pass |
| 10 | QA Testing | `10_BUSINESS_FLOW_MIGRATION.md` | 🔄 Sedang dikerjakan | — |
| 11 | UAT Sign-off | `11_UAT_CHECKLIST.md` | ⬜ Belum mulai | — |

Legenda: ⬜ Belum mulai · 🔄 Sedang dikerjakan · ✅ Draft/selesai ditulis · ✔️ Disetujui/lulus gate.

---

## Folder yang perlu di-connect

| Folder | Path | Peran | Read-only? |
|---|---|---|---|
| `target-codebase` (folder UTAMA) | `D:\Kuncoro\doodex\repo\appointment-jitsi-migration-18` (repo ini, branch `migration/18.0_target`) | Tempat kode migrasi 18.0 ditulis | Tidak |
| `source-codebase` | `D:\Kuncoro\doodex\repo\appointment-jitsi-migration-18-source` (branch `migration/17.0_source`, dari `backfill/17.0` — sudah berisi functional spec + tests backfill) | Baca modul 17.0 asli | Ya |
| `migration-tool` | `D:\Kuncoro\doodex\repo\migration-tool-project\migration-tool` | Template + `ai-doc/OVERVIEW.md`; tulis ke `migration-records/appointment_jitsi_17.0_18.0/` | Tulis di `migration-records/` saja |
| `native-source` (Community 17.0) | `D:\Kuncoro\doodex\repo\odoo17` (branch `17.0`) | Cross-check API core 17.0 | Ya |
| `native-target` (Community 18.0) | `D:\Kuncoro\doodex\repo\odoo18` (branch `18.0`) | Diff API core 18.0 | Ya |
| `native-source-enterprise` (Enterprise 17.0) | `D:\Kuncoro\doodex\repo\enterprise17` (branch `17.0`) | **WAJIB** — `appointment` adalah modul Enterprise (dikonfirmasi: ada di `enterprise17/appointment`, tidak ada di `odoo17/addons`) | Ya |
| `native-target-enterprise` (Enterprise 18.0) | `D:\Kuncoro\doodex\repo\enterprise18` (branch `18.0`) | **WAJIB** — sama alasan di atas, dikonfirmasi ada di `enterprise18/appointment` | Ya |
| `third-party-source`/`third-party-target` | — | N/A — dikonfirmasi tidak ada dependency OCA/vendor | — |

**Peringatan Enterprise (dari lesson `purchase_product_optional`):** dependency `appointment` berlisensi Enterprise di KEDUA versi (17.0 dan 18.0) — sudah dikonfirmasi langsung dari isi folder `enterprise17`/`enterprise18`, bukan diasumsikan. Step 2 wajib cross-check diff API `appointment` lewat `native-*-enterprise`, bukan `native-*` Community saja.

---

## Knowledge base

Sebelum step 2 mulai analisis, cek `migration-tool/knowledge/INDEX.md` dan `knowledge/version-diffs/17-to-18.md` — apakah sudah ada entry untuk pasangan versi ini atau dependency `appointment`/`calendar` yang relevan.

Temuan general baru (bukan spesifik `appointment_jitsi`) ditulis ke `migration-tool/migration-records/appointment_jitsi_17.0_18.0/SUMMARY.md` — **BUKAN** langsung ke `migration-tool/knowledge/`. Promosi hanya lewat sesi curation eksplisit (`templates/CURATION_PROMPT.md`).

---

## Catatan keamanan (ditemukan 2026-08-24, di luar scope migrasi tapi perlu diketahui dev)

Beberapa repo referensi di `D:\Kuncoro\doodex\repo\` (`appointment-jitsi-17`, `enterprise18`, dan clone project migrasi lain) punya GitHub Personal Access Token tertanam plaintext di `git remote -v` (URL `https://<user>:<token>@github.com/...`). Bukan bagian dari kode `appointment_jitsi`, tapi risiko kebocoran nyata kalau folder-folder itu pernah di-share/backup. Rekomendasi: rotate token yang bersangkutan, pakai credential helper Git alih-alih menaruh token di URL remote. `target-codebase`/`source-codebase` project ini sendiri sudah pakai URL bersih (tanpa token).

---

## Referensi

- Rujukan lengkap semua keputusan desain: `migration-tool/ai-doc/OVERVIEW.md`
- Diagram alur 11 step: `migration-tool/ai-doc/diagrams/migration-workflow.svg`
- Diagram dua jalur dokumen: `migration-tool/ai-doc/diagrams/spec-vs-test-tracks.svg`
- Dokumen backfill 17.0 (dasar baseline spec): `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`, `01B_ACCEPTANCE_CRITERIA.md`, `FINDINGS.md`
