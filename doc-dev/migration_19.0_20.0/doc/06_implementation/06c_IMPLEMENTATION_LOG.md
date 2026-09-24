# Implementation Log — appointment_jitsi

**Step:** 6 — Code Migration
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `migration-tool/templates/06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-09-24
**Status:** ✅ Selesai (G1 #2 PASS 17/17, 0 ERROR)

---

## Aturan

Append only · satu bagian per fase · faktual · tertelusuri · pengecualian eksplisit.

---

## Applicability Check

| Fase | Relevan? | Bukti/alasan (`01a` §2b) |
|---|---|---|
| B2 | ☐ Ya / ☑ Tidak | Tidak ada model baru/field kompleks |
| C2 | ☐ Ya / ☑ Tidak | Satu view inherit settings; xpath valid di 20.0 (DIFF-07), tidak ada perubahan semantik XML |
| D1 | ☐ Ya / ☑ Tidak | Controller 100% comment (`BSL-016`) |
| D2 | ☐ Ya / ☑ Tidak | Tidak ada key `assets`/`static/src` |
| E | ☐ Ya / ☑ Tidak | Tidak ada JS/Owl |
| F | ☐ Ya / ☑ Tidak | Tidak ada template Owl |

---

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 | ✅ manifest `20.0.1.0.0` | 2026-09-24 |
| A2 | ✅ N/A — tidak ada `<tree>`/`view_mode tree` (grep 0) | 2026-09-24 |
| G1 #1 (setelah A1/A2) | ✅ install Pass / test 10 error (DIFF-01 terbukti) | 2026-09-24 |
| A3 | ✅ N/A — tidak ada ACL/rule yang di-load (`security/ir.model.access.csv` di luar manifest, DIFF-10) | 2026-09-24 |
| A4 | ✅ struktur folder utuh (20 file sama dengan `migration/19.0`) | 2026-09-24 |
| A5 | ✅ `get_param` → `get_bool`/`get_int` + adaptasi test | 2026-09-24 |
| A6 | ✅ README/LISEZMOI versi basi diperbarui | 2026-09-24 |
| G1 #2 (setelah A3–A6) | ✅ Pass 17/17 | 2026-09-24 |
| B1 | ✅ tidak ada perubahan tambahan (sudah di A5) | 2026-09-24 |
| B2, C2, D1, D2, E, F | N/A — dikonfirmasi Applicability Check | — |
| C1 | ✅ tidak ada perubahan (DIFF-07/09) | 2026-09-24 |
| G2 (runtime) | ✅ Ter-cover G1 #2 (`--test-enable`, TransactionCase) — verifikasi UI live di Step 10 (menunggu slot) | 2026-09-24 |

## Riwayat Percobaan G1

| # | Setelah fase | Mode | Hasil | Error | Tanggal |
|---|---|---|---|---|---|
| 1 | A1/A2 (hanya bump manifest) | C | ☑ Install Pass / ☑ Test Fail | `0 failed, 10 error(s) of 15 tests` — semua `AttributeError: 'ir.config_parameter' object has no attribute 'set_param'` / `'get_param'` (helper test + `_compute_jitsi_link`). Log: `docker-env/logs/run-test-20260924-135718.log` (lokal, di-gitignore) | 2026-09-24 |
| 2 | A5/A6 | C | ☑ Pass | `0 failed, 0 error(s) of 17 tests`; 19 baris "Starting" (15 test modul + 2 `WebSuite`/`MobileWebSuite` bawaan); 0 baris ERROR/CRITICAL; satu-satunya WARNING modul = label "Company" duplikat (`BSL-019`, identik 17/18/19). Log: `run-test-20260924-140505.log` | 2026-09-24 |

**Environment G1 (Mode C, dipilih dev di intake):** image `appointment_jitsi_migration_20-odoo` (build `docker-env/Dockerfile`, `python:3.12-slim-bookworm` + `odoo20/requirements.txt` + Google Chrome), `postgres:16`, `odoo20` → `/opt/odoo:ro`, `enterprise20` → `/mnt/enterprise:ro`, `--without-demo=all`. Wrapper `docker-env/run-test.sh` (`down -v` + `MSYS_NO_PATHCONV=1` + sanity count). Compose file `docker-env/docker-compose.20.0.yml`, project `appointment_jitsi_migration_20`, port 8096.

---

## [Fase A1] Manifest Bootstrap
- **Scope:** `appointment_jitsi/__manifest__.py`
- **Aksi:** `version` `19.0.1.0.0` → `20.0.1.0.0` (DIFF-12).
- **Sengaja TIDAK diubah:** `data` (tetap hanya `views/calendar_views.xml` — `BSL-015`), `images` (`banner.png` — aset store rilis 19.0 di luar scope, keputusan intake), `depends`, `license`, deskripsi.
- **Status:** ✅

## [Fase A2] XML Tree → List
- **Aksi:** grep `<tree` / `view_mode ... tree` = 0 → N/A.

## [Fase A3] Security Hardening
- **Aksi:** tidak ada. `security/ir.model.access.csv` (header-only) tidak terdaftar di manifest → tidak terdampak `ir.access` 20.0 (DIFF-10). File dibiarkan apa adanya.

## [Fase A4] Skeleton & Folder Integrity
- **Aksi:** verifikasi 20 file identik daftar `git ls-tree migration/19.0 -- appointment_jitsi`; tidak ada file ditambah/dihapus.

## [Fase A5] Python API Compatibility
- **Scope:** `models/calendar_event.py`, `tests/test_appointment_jitsi.py`
- **Aksi (produksi, DIFF-01/MF-01):** `_compute_jitsi_link` — `get_param = ICP.get_param` → `ICP = self.env['ir.config_parameter'].sudo()`; `is_jitsi_enabled = ICP.get_bool('is_jitsi_param')`; `company_param_id = ICP.get_int('company_param')`. Tiga baris saja.
- **Aksi (test):** helper `_enable_jitsi` → `set_bool(True)` + `set_int(company.id)`; `_disable_jitsi` → `set_bool(False)`; log observasi `get_param(...)` → `get_str(..., None)` (2 tempat); `test_qa_s01` `env.ref` → `appointment.appointment_booking_mail_template` (DIFF-08/MF-02) + catatan docstring. Test BARU: `test_mig20_ac_04_01_action_join_video_call` (AC-04-01, `BSL-007`), `test_mig20_ac_10_01_uncheck_setting_falls_back_to_discuss` (AC-10-01, `BSL-014`). Prefix `mig20_` supaya tidak bentrok dengan penomoran backfill (`test_ac_04_01_write_toggle…` adalah AC-07 di dokumen migrasi).
- **Sengaja TIDAK diubah:** sisa body `_compute_jitsi_link` (search company, `'Record not found'`, cabang `uuid4().hex`, format URL, fallback Discuss), `create()` (`BSL-005/009`), `action_join_video_call()`, field, `ResConfigSettings`, assertion 13 test lama (selain retarget `env.ref`).
- **Status:** ✅

## [Fase A6] Housekeeping README/Metadata
- **Aksi:** `README.md` "Odoo version: 19.0 Enterprise Edition" → 20.0; `LISEZMOI.md` "Version d'Odoo : 17.0" (sudah basi sejak 18.0) → 20.0. Isi lain (termasuk klaim "include them in appointment confirmation emails" yang faktanya tidak aktif, `BSL-015`) tidak diubah — perbaikan klaim fitur di luar scope bug-for-bug.

## [Fase B1/C1] — tidak ada perubahan tambahan di luar A5.

## [Fase G2] Validasi Akhir
- Runtime tervalidasi lewat G1 #2 (`--test-enable`, 15 test modul PASS). Verifikasi nilai (bukan sekadar "tidak error"), sesuai `02_DIFF_ANALYSIS.md` §0e:
  - DIFF-01: `test_ac_01_01` link Jitsi terbentuk; `test_mig20_ac_10_01` uncheck → `get_str` = `'False'` (bukan row dihapus seperti 19.0) → `get_bool` False → Discuss.
  - **MF-03 / DIFF-04:** `test_ac_01_01` `videocall_location == jitsi_link` tetap PASS; `test_ac_03_01` Skenario A = Jitsi penuh, Skenario B `videocall_location=False`, `bug_confirmed=True` — **identik log 19.0** (`doc-dev/migration_18.0_19.0/doc/09_devtest/09_DEV_TESTING.md`). Flush baru di `create()` tidak menggeser hasil observable.
  - DIFF-02: token format `str(uuid4())` 36-char (sama dengan 19.0 pasca MF-01), tidak ada `IntegrityError` dari `unique(access_token)`.
- Verifikasi UI (Settings form, tombol Join, email) → Step 10 (menunggu slot dari dev).
