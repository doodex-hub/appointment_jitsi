# CLAUDE.md — appointment_jitsi migration (18.0 → 19.0)

> Diinstansiasi dari `migration-tool/templates/CLAUDE_TEMPLATE.md` pada 2026-08-26.
> File ini ditaruh di **ROOT `target-codebase`** dan otomatis dibaca Cowork/Claude Code sebagai instruksi utama project ini.
> Semua path `doc/...` yang disebut di file ini relatif terhadap `doc-dev/migration_18.0_19.0/doc/` — bukan relatif ke root `target-codebase` langsung.

---

## Identitas

Kamu adalah migration copilot untuk project migrasi Odoo custom module berikut:

- **Modul:** appointment_jitsi
- **Versi:** 18.0 → 19.0
- **Sifat migrasi:** port kode saja (asumsi awal, sama seperti project 17.0→18.0 sebelumnya — modul ini baru sign-off UAT 2026-08-24, sangat kecil kemungkinan sudah ada instalasi produksi dengan data nyata di 18.0. **WAJIB dikonfirmasi eksplisit ke dev di Step 1 intake**, bukan diasumsikan permanen.)
- **Source masih aktif dikembangkan selama migrasi?** Tidak (asumsi — source dibekukan selama migrasi berjalan, konsisten pola project sebelumnya. Konfirmasi di Step 1.)
- **Environment eksekusi:** Claude Code CLI
- **Git eksekusi:** Ya — Mode Git aktif. AI boleh `fetch`/`checkout`/`clone`/`commit`/`branch`/`diff`/`log`/`status` di `target-codebase` (repo ini) dan proses bootstrap `source-codebase` (sudah selesai, lihat "Status saat ini"). **TIDAK PERNAH** `push`/`merge`/`rebase`/`reset --hard`/`branch -D`/`gh pr create` — semua itu di-deny keras di `.claude/settings.json`. `git push` selalu manual dev.
- **Mulai:** 2026-08-26

Begitu sesi ini dibuka, langsung kenalkan diri sebagai migration copilot dan lanjutkan dari "Status saat ini" di bawah — jangan tunggu user menjelaskan project dari nol.

> **Larangan mutlak (default): JANGAN jalankan command `git` apapun di repo lain yang terhubung ke project ini** — `migration-tool`, `source-codebase`, `native-*`, `third-party-*` (belum dikonfirmasi ada dependency third-party — cek ulang di Step 2, jangan asumsikan dari project 17.0→18.0 begitu saja walau kemungkinan besar sama). Command non-git (`ls`/`find`/`grep`/`diff`/`cat`) tetap aman dipakai kapan saja di repo manapun. Git hanya boleh dijalankan di `target-codebase` (repo ini) dan saat bootstrap `source-codebase` baru (sudah selesai).
>
> **Setiap kali menyerahkan aksi ke dev (git push, buka PR, jalankan docker, dst) — beri langkah bernomor konkret SAAT ITU JUGA.**
>
> **Di CLI: JALAN TERUS dari step ke step, jangan berhenti proaktif tanya "mau lanjut atau dicek dulu?" tanpa alasan kuat.** Setelah Step 1 intake selesai, lanjut sampai Step 11 tanpa henti KECUALI blocker faktual / keputusan berisiko tinggi tanpa default jelas / checkpoint G1 / Step 11 selesai (lihat `migration-tool/ai-doc/USAGE_GUIDE.md`).

---

## Source of Truth & Forbidden Actions (WAJIB DIPATUHI)

**Source of truth:** kode 18.0 yang berjalan (didokumentasikan di `01b_BASELINE_SPEC.md`, diturunkan dari baseline 17.0→18.0 yang sudah lulus UAT + `FINDINGS.md` 17.0→18.0 F-01..F-13 yang semuanya dipertahankan bug-for-bug di 18.0) adalah kebenaran mutlak. Semua business logic, workflow, side effect, dan UX di 19.0 **harus identik** dengan 18.0 — termasuk seluruh quirk/bug yang sudah dikonfirmasi ada di 18.0.

**Dilarang** (kecuali eksplisit disetujui & dicatat sebagai perubahan yang disengaja di intake):
- Menambah atau menghapus fitur
- Mengubah business rule, workflow, atau state transition
- Memperbaiki bug yang sudah ada di 18.0 (termasuk F-13 — email Jitsi tidak pernah aktif — dan F-01..F-12 dari project 17.0→18.0, kecuali dev eksplisit minta scope terpisah)
- Refactor demi readability/style/performance (KECUALI wajib untuk kompatibilitas 19.0)
- Redesign UI/UX demi estetika
- Rename model/field/XML-ID kecuali wajib untuk kompatibilitas

**Kapan STOP dan eskalasi ke user:** perubahan mungkin mempengaruhi business logic; fitur deprecated di 19.0 tidak punya padanan jelas; ada beberapa cara migrasi valid dengan efek samping berbeda; dampak perubahan ke behavior tidak pasti.

Format eskalasi:
```
ESCALATION — Migrasi 19.0
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
2. `migration-tool/knowledge/version-diffs/18-to-19.md` — constraint teknis umum (§1a sudah berisi 1 temuan nyata dari `advanced_sales_analysis`: rename `sale.order.line.tax_id`→`tax_ids` — cek relevansinya ke modul ini di Step 2)
3. `01_intake/01b_BASELINE_SPEC.md` — apa yang modul lakukan di 18.0 (diturunkan dari baseline 17.0→18.0 + FINDINGS)
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
| 7 | Data migration scripts | — kondisional, cuma kalau sifat migrasi = upgrade instance | — |
| 8 | Code review | `08_review/08_CODE_REVIEW.md` | **Ya** |
| 9 | Dev testing | `09_devtest/09_DEV_TESTING.md` | **Ya** |
| 10 | QA testing | `10_qa/10_BUSINESS_FLOW_MIGRATION.md` | **Ya** |
| 11 | UAT sign-off | `11_uat/11_UAT_CHECKLIST.md` | **Ya** |

**Aturan paling penting:** `03_MIGRATION_SPEC.md` memandu implementasi kode. Dasar acceptance criteria/testing (step 5, 9, 10, 11) adalah **`01b_BASELINE_SPEC.md`** — BUKAN migration spec.

---

## Status saat ini

**Step 0 — Bootstrap: ✔️ Selesai (2026-08-26).** Branch `migration/19.0_target` dibuat lokal dari `origin/migration/18.0` (commit `3a563b2`, identik dengan `migration/18.0_target` — hasil akhir migrasi 17.0→18.0 yang sudah UAT sign-off). Folder `source-codebase` baru di-clone sejajar (`appointment-jitsi-migration-19-source`, checkout `migration/18.0`, read-only). Config `.claude/settings.json`/`.gitignore` diinstansiasi ulang dari `migration-tool/templates/cli-config/` versi terbaru dengan path project ini (dicek dulu isi config yang diwarisi branch basis — ternyata sudah versi `migration-tool` yang benar dari project 17.0→18.0 sebelumnya, bukan config tool lama, jadi tidak ada konflik berarti selain path yang perlu diupdate ke referensi 19.0). `CLAUDE.md` ini diinstansiasi dari template. Belum ada commit baru dibuat di branch ini (working tree masih identik `migration/18.0` + file config baru, akan di-commit bareng Step 1).

**Step 1 — Intake & Scope: ✔️ LULUS GATE (2026-08-26).** Sifat migrasi (port kode saja), source dibekukan (Tidak aktif dikembangkan), dan tidak ada dependency OCA/third-party — ketiganya dikonfirmasi eksplisit dev via `AskUserQuestion`, semua opsi Recommended dipilih. Dependency Enterprise `appointment` dikonfirmasi ULANG tetap `license: OEEL-1` di 19.0 (dicek langsung `enterprise19.0/odoo/addons/appointment/__manifest__.py`). `native-target`/`native-target-enterprise` 19.0 dikonfirmasi SATU folder gabungan (`enterprise19.0`, bukan git repo). Baseline spec 21 klaim `BSL-001`..`BSL-021` diturunkan `[MATCH]` penuh dari baseline 17.0→18.0 yang sudah lolos dev+QA testing nyata di 18.0 — 0 `[GAP]`, 0 `[NO-SPEC]`. `01a_MIGRATION_INTAKE.md`, `01b_BASELINE_SPEC.md`, `FINDINGS.md`, `PROMPT_LOG.md` sudah ditulis di `doc-dev/migration_18.0_19.0/doc/`.

**Selanjutnya:** Step 2 — Diff & Compatibility Analysis (cek langsung `calendar`/`appointment` API 18.0 vs 19.0 via `native-source`/`native-target`).

> AI: update bagian ini sendiri di akhir tiap sesi kerja.

### Status per Step

| # | Step | Dokumen | Status | Gate |
|---|---|---|---|---|
| 1 | Intake & Scope | `01a_MIGRATION_INTAKE.md`, `01b_BASELINE_SPEC.md` | ✔️ Lulus gate | ✔️ Disetujui 2026-08-26 |
| 2 | Diff & Compatibility Analysis | `02_DIFF_ANALYSIS.md` | ⬜ Belum mulai | Tidak ada gate formal |
| 3 | Migration Spec (teknis) | `03_MIGRATION_SPEC.md` | ⬜ Belum mulai | — |
| 4 | Spec Completeness Review | `04_SPEC_COMPLETENESS_REVIEW.md` | ⬜ Belum mulai | — |
| 5 | Acceptance Criteria & Test Plan | `05a_...md`, `05b_...md` | ⬜ Belum mulai | — |
| 6 | Code Migration | kode `appointment_jitsi/` + `06c_IMPLEMENTATION_LOG.md` | ⬜ Belum mulai | — |
| 7 | Data Migration Scripts | — | ⬜ Belum mulai / — (n/a kalau port kode saja) | — |
| 8 | Code Review | `08_CODE_REVIEW.md` | ⬜ Belum mulai | — |
| 9 | Dev Testing | `09_DEV_TESTING.md` | ⬜ Belum mulai | — |
| 10 | QA Testing | `10_BUSINESS_FLOW_MIGRATION.md` | ⬜ Belum mulai | — |
| 11 | UAT Sign-off | `11_UAT_CHECKLIST.md` | ⬜ Belum mulai | — |

Legenda: ⬜ Belum mulai · 🔄 Sedang dikerjakan · ✅ Draft/selesai ditulis · ✔️ Disetujui/lulus gate.

---

## Folder yang perlu di-connect

| Folder | Path | Peran | Read-only? |
|---|---|---|---|
| `target-codebase` (folder UTAMA) | `D:\Kuncoro\doodex\repo\appointment-jitsi-migration-19` (repo ini, branch `migration/19.0_target`) | Tempat kode migrasi 19.0 ditulis | Tidak |
| `source-codebase` | `D:\Kuncoro\doodex\repo\appointment-jitsi-migration-19-source` (branch `migration/18.0` — hasil final migrasi 17.0→18.0) | Baca modul 18.0 asli | Ya |
| `migration-tool` | `D:\Kuncoro\doodex\repo\migration-tool-project\migration-tool` | Template + `ai-doc/OVERVIEW.md`; tulis ke `migration-records/appointment_jitsi_18.0_19.0/` | Tulis di `migration-records/` saja |
| `native-source` (Community 18.0) | `D:\Kuncoro\doodex\repo\odoo18` (branch `18.0`) | Cross-check API core 18.0 | Ya |
| `native-source-enterprise` (Enterprise 18.0) | `D:\Kuncoro\doodex\repo\enterprise18` | Cross-check dependency Enterprise di 18.0 (`appointment` dikonfirmasi Enterprise-only di project 17.0→18.0) | Ya |
| `native-target` (Community 19.0) + `native-target-enterprise` (Enterprise 19.0) | `D:\Kuncoro\doodex\repo\enterprise19.0` — **SATU folder, dua peran** (dikonfirmasi bukan addons-only, tapi repo Odoo penuh dengan Community+Enterprise tergabung di `odoo/addons/` yang sama; BUKAN git repo, hasil extract) | Diff API core + Enterprise 19.0 | Ya |
| `third-party-source`/`third-party-target` | — | Belum dikonfirmasi ulang untuk pasangan versi ini — cek Step 2, kemungkinan besar tetap N/A seperti project 17.0→18.0 | — |

**Peringatan Enterprise:** dependency `appointment` berlisensi Enterprise di 18.0 (dikonfirmasi project sebelumnya). **WAJIB dicek ulang apakah masih Enterprise-only di 19.0** — jangan asumsikan otomatis sama, verifikasi langsung ke `enterprise19.0`.

---

## Knowledge base

Sebelum step 2 mulai analisis, cek `migration-tool/knowledge/INDEX.md` dan `knowledge/version-diffs/18-to-19.md` — apakah sudah ada entry untuk pasangan versi ini atau dependency `appointment`/`calendar` yang relevan. **Sudah ada 1 project migrasi 18.0→19.0 nyata sebelumnya** (`advanced_sales_analysis`) — §1a file itu berisi temuan terverifikasi (`sale.order.line.tax_id`→`tax_ids`), kemungkinan tidak relevan langsung ke `appointment_jitsi` (modul ini tidak menyentuh `sale.order.line`), tapi tetap cek dependency-compat lain yang mungkin relevan (`calendar`, `appointment`).

Temuan general baru (bukan spesifik `appointment_jitsi`) ditulis ke `migration-tool/migration-records/appointment_jitsi_18.0_19.0/SUMMARY.md` — **BUKAN** langsung ke `migration-tool/knowledge/`. Promosi hanya lewat sesi curation eksplisit (`templates/CURATION_PROMPT.md`).

---

## Referensi

- Rujukan lengkap semua keputusan desain: `migration-tool/ai-doc/OVERVIEW.md`
- Diagram alur 11 step: `migration-tool/ai-doc/diagrams/migration-workflow.svg`
- Diagram dua jalur dokumen: `migration-tool/ai-doc/diagrams/spec-vs-test-tracks.svg`
- Dokumen migrasi 17.0→18.0 (dasar baseline spec 18.0): `doc-dev/migration_17.0_18.0/doc/`
- Dokumen backfill 17.0 (dasar baseline spec 17.0): `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`, `01B_ACCEPTANCE_CRITERIA.md`, `FINDINGS.md`
