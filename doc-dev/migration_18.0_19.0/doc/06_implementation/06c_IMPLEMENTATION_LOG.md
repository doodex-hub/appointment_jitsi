# Implementation Log — appointment_jitsi

**Step:** 6 — Code Migration
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `migration-tool/templates/06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-08-26

---

## Catatan Khusus — Starting Point Bukan Checkout Kosong

`target-codebase` (repo ini, branch `migration/19.0_target`) dibuat dari `origin/migration/18.0` (commit `3a563b2`) — kode `appointment_jitsi/` SUDAH berisi modul 18.0 penuh sejak awal Step 6 dimulai, bukan folder kosong. Konsisten kesimpulan `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md` (port 1:1 tanpa rewrite logic), sebagian besar fase A-G di bawah adalah **konfirmasi tidak ada perubahan yang dibutuhkan**. Perubahan aktual: 3 baris teks housekeeping (manifest version, README compatibility ×2 — dalam folder modul dan root repo).

---

## Applicability Check

| Fase | Relevan untuk modul ini? (dari `01a` §2b) | Keterangan |
|---|---|---|
| C1 — View Sederhana | **Ya** | Modul punya `views/calendar_views.xml`, terdaftar di manifest `data` |
| B2 — Model Kompleks | Tidak | Tidak ada field JSON/relasi berantai/dynamic model creation |
| C2 — Semantik XML & UX | Tidak | View sudah pakai syntax modern, dikonfirmasi tidak berubah (`DIFF-03`) |
| D1 — Controllers | Tidak | `controllers/appointment.py` 100% dead code |
| D2 — Assets & CSS | Tidak | Tidak ada asset/CSS custom |
| E — JavaScript (Owl) | Tidak | Tidak ada file `.js` |
| F — Upgrade Template | Tidak (otomatis, karena E N/A) | — |

---

## Fase A — Fondasi

### A1 — Manifest Bootstrap
- **Aksi:** `__manifest__.py` — `"version": "18.0.1.0.0"` → `"19.0.1.0.0"`. `depends`/`data` TIDAK berubah — `data/mail_template_data.xml` SENGAJA TIDAK ditambahkan (`[BSL-015]`/`FINDINGS.md`).
- **Status:** ✅ Selesai

### A2 — XML Tree → List
- **Status:** ✅ N/A — tidak ada tag `<tree>` di modul ini (`DIFF-08`).

### A3 — Security Hardening
- **Status:** ✅ N/A — `security/ir.model.access.csv` hanya header.

### A4 — Skeleton & Folder Integrity
- **Status:** ✅ Selesai — struktur folder konsisten (diwarisi dari commit yang sama), tidak ada yang hilang.

### A5 — Python API Compatibility (Models Only)
- **Aksi:** `models/calendar_event.py` — `create(self, values)` dengan `@api.model` **SENGAJA TIDAK diubah** ke `@api.model_create_multi`, meski `DIFF-01`/`MF-01` mengonfirmasi mekanisme routing berubah di ORM core 19.0. Keputusan (per `03_MIGRATION_SPEC.md` §1): port 1:1 dulu, verifikasi observable behavior via 13 test existing di checkpoint G1/Step 9 — BUKAN mengubah kode secara proaktif berdasarkan analisis statis semata.
- **Status:** ✅ Selesai (tidak ada perubahan kode, keputusan disengaja)

### C1 — View Sederhana (revisi — 1 perubahan wajib ditemukan G1)
- **Aksi tambahan (di luar rencana awal `03_MIGRATION_SPEC.md`):** `views/calendar_views.xml` — `<field name="target">inline</field>` → `<field name="target">current</field>` pada record `res_config_settings_action`. **WAJIB** — `inline` dihapus total dari selection `ir.actions.act_window.target` di 19.0 core (`MF-02`), install gagal keras tanpa fix ini. Record ini dead code/orphaned (`[BSL-022]`, ditemukan baru saat G1 — gap baseline sebelumnya), jadi perubahan value ini nol dampak observable.
- **Status:** ✅ Selesai

### Checkpoint G1 — Install Test
- **Status:** ✅ **LULUS (2026-08-26, Mode C — AI jalankan langsung, dikonfirmasi dev).** Perlu 4 percobaan (2 infra fix + 1 ESCALATION dev + retest) — jauh lebih banyak dari project 17.0→18.0 (sukses percobaan pertama), konsisten kesimpulan risiko naik jadi RENDAH-SEDANG di `02_DIFF_ANALYSIS.md`. Hasil akhir: `Module appointment_jitsi loaded` bersih, `13/13 test PASS (0 failed, 0 error(s))`, `Registry loaded in ~60s`. Log lengkap: `docker-env/logs/odoo_19.log`.
- **Percobaan 1 (postgres:15 polos):** ❌ GAGAL, exit 255 — `CREATE EXTENSION IF NOT EXISTS vector` error. Odoo 19.0 core menjalankan ini saat init DB dasar (general infra finding, TIDAK spesifik modul ini — lihat `migration-records/appointment_jitsi_18.0_19.0/SUMMARY.md` CAND-02). Fix: ganti image `db` ke `pgvector/pgvector:pg15`.
- **Percobaan 2 (pgvector, sebelum fix `target=inline`):** ❌ GAGAL, exit 255 — `ValueError: Wrong value for ir.actions.act_window.target: 'inline'` saat parsing `views/calendar_views.xml:4-11` (record `res_config_settings_action`, dead code/orphaned — `[BSL-022]`, baru ditemukan di sini, gap baseline sebelumnya). `inline` DIHAPUS TOTAL dari selection `ir.actions.act_window.target` di 19.0 core (`MF-02`, general finding — lihat `SUMMARY.md` CAND-03). Fix: ganti `target` ke `current` (nol dampak observable, action tidak pernah dipanggil).
- **Percobaan 3 (kedua fix infra diterapkan):** ⚠️ Install SUKSES (modul loaded bersih), TAPI `2 failed, 0 error(s)` dari 13 test — **persis sesuai prediksi `MF-01`** (Step 2): `test_ac_02_01`/`test_ac_02_02` gagal karena mekanisme `create()` `@api.model` berubah di ORM 19.0 (`model_create_multi`, `values` selalu list). **ESCALATION dijawab dev** (lihat `FINDINGS.md` MF-01) — pilih terima observable-outcome baru, `create()` TIDAK diubah, update 2 assertion test untuk mencerminkan baseline 19.0 yang baru (format token 36-char vs 32-char, dan hilangnya reset-to-`False` untuk single-create — demi mempertahankan `[BSL-009]` utuh).
- **Percobaan 4 (assertion test diupdate sesuai keputusan dev):** ✅ **SUKSES PENUH** — `13/13 test PASS (0 failed, 0 error(s))`. Semua quirk tereproduksi PERSIS sesuai `01b_BASELINE_SPEC.md`: F-01 non-bug (`bug_confirmed=False`), F-02/`[BSL-011]` (`bug_confirmed=True`), F-03/`[BSL-009]` (`bug_confirmed=False`, batch tetap utuh), F-04/`[BSL-010]` (`bug_confirmed=True`, race condition urutan akses field), F-13/`[BSL-015]` (`muncul_di_body=False`, email tetap tidak aktif). Warning MUNCUL PERSIS seperti diprediksi: `Two fields (company_param, company_id) ... have the same label: Company` (`[BSL-019]`).

---

## Fase B — Python Models (Semantik)

### B1 — Model Risiko Rendah
- **Aksi:** `models/calendar_event.py` (`CalendarEvent`, `ResConfigSettings`) — dibaca ulang penuh, dikonfirmasi TIDAK ADA perubahan yang dibutuhkan di luar catatan `DIFF-01` (A5 di atas).
- **Status:** ✅ Selesai (copy apa adanya)

### B2 — Model Kompleks
- **Status:** ✅ N/A

---

## Fase C — XML Views

### C1 — View Sederhana
- **Aksi:** `views/calendar_views.xml` — dikonfirmasi xpath anchor `sync_google_calendar_setting` + syntax `invisible=` valid di 19.0 (`DIFF-03`). Tidak ada perubahan.
- **Status:** ✅ Selesai (copy apa adanya)

### C2 — Semantik XML & UX
- **Status:** ✅ N/A

---

## Fase D — Controllers & Assets

### D1 — Controllers
- **Aksi:** `controllers/appointment.py`, `controllers/__init__.py` — dikonfirmasi tetap dead code, import no-op dipertahankan.
- **Status:** ✅ Selesai (copy apa adanya)

### D2 — Assets & CSS
- **Status:** ✅ N/A

---

## Fase E — JavaScript (Owl)
**Status:** ✅ N/A

## Fase F — Upgrade Template
**Status:** ✅ N/A (otomatis, karena E N/A)

---

## Fase G2 — Validasi Akhir (Runtime)

- **Status:** ✅ **Selesai (via `--test-enable` di run G1 yang sama, percobaan 4, 2026-08-26).** `DIFF-01`/`MF-01` (create single-dict, dampak dikonfirmasi + deviation diterima dev), `MF-02` (target=inline, fixed), `DIFF-02`/`DIFF-03` (field/view core tidak error) semua terkonfirmasi valid di server hidup. Tidak perlu run G2 terpisah.

---

## File Lain (Copy Apa Adanya, Tidak Ada Perubahan Kode)

Dikonfirmasi copy 1:1 tanpa modifikasi: `data/mail_template_data.xml`, `security/ir.model.access.csv`, `tests/__init__.py`, `tests/test_appointment_jitsi.py`, `LICENSE`, `LISEZMOI.md`, `googleaeed8a7b9ec156e7.html`, seluruh `static/description/**`.

**Perubahan housekeeping (bukan business logic):**
- `appointment_jitsi/README.md` — "Compatibility: Odoo version: 18.0 Enterprise Edition" → "19.0 Enterprise Edition".
- `README.md` (root repo) — baris Compatibility yang sama, diupdate untuk konsistensi.
- `docker-env/docker-compose.19.0.yml` (baru) — adaptasi dari `docker-compose.18.0.yml`: image `odoo:19.0`, mount `enterprise19.0/odoo/addons` (bukan `enterprise18` langsung — struktur folder gabungan 19.0 beda dari 18.0).

---

## Riwayat Percobaan G1

| # | Mode (A/B/C) | Hasil | Catatan |
|---|---|---|---|
| 1 | C — AI jalankan langsung | ❌ Gagal, exit 255 | `postgres:15` polos — Odoo 19.0 butuh pgvector saat init DB dasar |
| 2 | C — AI jalankan langsung | ❌ Gagal, exit 255 | `pgvector/pgvector:pg15` — install gagal karena `target=inline` dihapus di 19.0 (`MF-02`) |
| 3 | C — AI jalankan langsung | ⚠️ Install sukses, 2/13 test gagal | Kedua infra fix diterapkan — `MF-01` terkonfirmasi berdampak, ESCALATION ke dev |
| 4 | C — AI jalankan langsung | ✅ **Sukses penuh, 13/13 test PASS** | Assertion 2 test diupdate sesuai keputusan dev (MF-01 diterima sebagai deviation) |

## Ringkasan Step 6

**Selesai penuh (2026-08-26).** Kode migrasi: 3 perubahan teks housekeeping (manifest version, README ×2) + 1 perubahan kode wajib (`views/calendar_views.xml` `target=inline`→`current`, `MF-02`, install-blocking, nol dampak observable karena dead code). `create()` (`MF-01`) sengaja TIDAK diubah — dev eksplisit menerima deviation observable-outcome demi mempertahankan `[BSL-009]` utuh, 2 test assertion diupdate untuk mencerminkan baseline 19.0 yang baru. Checkpoint G1+Fase G2 LULUS di percobaan ke-4 (2 infra fix + 1 keputusan dev diperlukan) — jauh lebih banyak percobaan dari migrasi 17.0→18.0 (sukses langsung), konsisten kesimpulan risiko naik ke RENDAH-SEDANG. Dua finding general baru (`MF-02`, plus pgvector) dicatat ke `migration-records/appointment_jitsi_18.0_19.0/SUMMARY.md` untuk kandidat curation `knowledge/version-diffs/18-to-19.md`.
