# Dev Testing — appointment_jitsi

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-08-24

---

**Eksekusi aktual (2026-08-24, Mode C — AI jalankan langsung):**
```
MSYS_NO_PATHCONV=1 docker compose -f docker-env/docker-compose.18.0.yml up --abort-on-container-exit
```
(`command:` di dalam compose: `odoo -d appointment_jitsi_test_18 -i appointment_jitsi --addons-path=...,/mnt/enterprise-addons,/mnt/extra-addons --test-enable --test-tags=/appointment_jitsi --stop-after-init`)

**Verifikasi anti-false-pass (wajib per `USAGE_GUIDE.md` — lesson `crm_probability_from_stage`):** `grep -c "^    def test_"` pada `tests/test_appointment_jitsi.py` = **13**. Log menunjukkan 13 baris `Starting TestAppointmentJitsi.test_...` dengan NAMA method asli (bukan `0 tests` akibat tag ter-mangle MSYS) — angka cocok persis. `MSYS_NO_PATHCONV=1` sudah dipakai di command, tag filter terbukti bekerja benar.

## 9a. Audit Kesiapan Test

13 method di `tests/test_appointment_jitsi.py` sudah diaudit isinya SEBELUM migrasi ini (saat backfill 2026-08-07, lihat `doc-dev/backfill/test/04A_DEV_TESTING.md`) — semua mengandung assertion nyata (bukan stub), dikonfirmasi lulus eksekusi terhadap 17.0. Audit ulang isi method TIDAK diperlukan untuk migrasi ini karena file test di-port apa adanya (tidak ada modifikasi), dan hasil run terhadap 18.0 di bawah membuktikan langsung tiap method benar-benar menjalankan assertion (log per-test menunjukkan output `BACKFILL AC-XX-XX/F-XX: ...` yang HANYA bisa muncul kalau kode di dalam method benar-benar dieksekusi, bukan sekadar lolos karena kosong).

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01, AC-01-02, AC-01-03 | Aktivasi Jitsi global | `test_appointment_jitsi.py` | ✅ Lengkap | Assertion + log nilai aktual |
| AC-02-01, AC-02-02, AC-02-03 | `create()` single/batch | `test_appointment_jitsi.py` | ✅ Lengkap | — |
| AC-03-01 | Urutan akses field | `test_appointment_jitsi.py` | ✅ Lengkap | Skenario A/B eksplisit |
| AC-04-01 (write toggle, `BSL-011`) | Toggle `write()` tidak recompute | `test_appointment_jitsi.py` (`test_ac_04_01_write_toggle_no_recompute`) | ✅ Lengkap | — |
| AC-04-01 (05a — `action_join_video_call`, `BSL-007`) | Return action URL | — | ❌ **Tidak ada test** | Gap test coverage — risiko rendah (logic trivial ternary), TIDAK memblokir gate (lihat `08_CODE_REVIEW.md` §C) |
| AC-05-01..AC-13-01 | Sisa quirk (F-05, F-06, F-07, F-08) | `test_appointment_jitsi.py` | ✅ Lengkap | — |
| **AC-11-01** 🔴 | Mail template tidak aktif | `test_appointment_jitsi.py` (`test_qa_s01_mail_template_does_not_render_jitsi_link`) | ✅ Lengkap | Test paling kritis — hasil di bawah |
| AC-14-01 | Dependency Enterprise | — (cek instalasi, bukan test method) | ✅ Terverifikasi via install log | — |

**Verdict audit:** Semua AC prioritas tinggi (terutama AC-11-01) berstatus Lengkap — lanjut eksekusi. Satu gap non-blocking (AC-04-01/`action_join_video_call`) dicatat, tidak eskalasi karena risiko rendah dan bukan area yang disentuh migrasi.

## Baseline

- Characterization test asli: 13 method `TransactionCase` (`appointment_jitsi/tests/test_appointment_jitsi.py`), ditulis saat backfill, hasil run terhadap `source-codebase` (17.0, dari backfill 2026-08-07): **13/13 PASS** (lihat `doc-dev/backfill/test/04A_DEV_TESTING.md`).
- Applicability Check Fase E (Owl/JS): **Tidak, N/A** — tidak ada tour test yang perlu ditambahkan.

## Hasil Unit, Integration & Tour Test (target-codebase, Odoo 18.0)

| AC | Integration | Tour | Pass/Fail | Catatan |
|---|---|---|---|---|
| AC-01-01 | `test_ac_01_01_jitsi_link_format_when_enabled` | N/A | ✅ Pass | `jitsi_link=https://meet.jit.si/YourCompany/YourCompany-<uuid>` — format identik 17.0 |
| AC-01-02 | `test_ac_01_02_fallback_discuss_when_disabled` | N/A | ✅ Pass | `get_param=False`, fallback Discuss |
| AC-01-03 | `test_ac_01_03_uncheck_setting_still_truthy` | N/A | ✅ Pass | `get_param setelah uncheck = False (type=bool)` — F-01 tetap non-bug di 18.0 |
| AC-02-01 | `test_ac_02_01_create_single_dict_enables_token` | N/A | ✅ Pass | — |
| AC-02-02 | `test_ac_02_02_create_single_dict_disable_resets_token` | N/A | ✅ Pass | — |
| AC-02-03 | `test_ac_02_03_create_batch_list_is_jitsi_check_fails` | N/A | ✅ Pass | `bug_confirmed=False` untuk skenario spesifik ini (access_token tetap terisi via default core) — identik nuansa 17.0 (`[BSL-009]`) |
| AC-03-01 | `test_ac_03_01_videocall_location_race_with_core_compute` | N/A | ✅ Pass (bug tereproduksi) | Skenario A: Jitsi penuh. Skenario B: `videocall_location=False`. `bug_confirmed=True` — identik `[BSL-010]` |
| AC-07-01 (write toggle) | `test_ac_04_01_write_toggle_no_recompute` | N/A | ✅ Pass (bug tereproduksi) | `before=False after=False`, `bug_confirmed=True` — identik `[BSL-011]` |
| AC-08-01 | `test_ac_05_01_company_param_global_multi_company` | N/A | ✅ Pass | Dua event, `company_name` (`YourCompany`) sama — identik `[BSL-012]` |
| AC-09-01 | `test_ac_06_01_company_name_with_space_not_escaped` | N/A | ✅ Pass | `.../PT Doodex Indonesia/PT Doodex Indonesia-<uuid>` — spasi mentah, identik `[BSL-013]` |
| AC-12-01 | `test_ac_07_01_controller_is_dead_code` | N/A | ✅ Pass | 0 baris aktif |
| AC-05-01 (generate/clear) | `test_ac_08_01_generate_and_clear_jitsi_link_still_work` | N/A | ✅ Pass | — |
| **AC-11-01** 🔴 | `test_qa_s01_mail_template_does_not_render_jitsi_link` | N/A | ✅ **Pass — bug tereproduksi persis** | `jitsi_link` terisi penuh, `muncul_di_body=False` — email TETAP tidak menampilkan link Jitsi di 18.0, identik `[BSL-015]`/F-13 |
| AC-04-01 (`action_join_video_call`) | — (tidak ada test) | N/A | ⚠️ Tidak dieksekusi | Gap test coverage, risiko rendah — lihat `08_CODE_REVIEW.md` |
| AC-14-01 | Install log (`enterprise18` mounted, `appointment` ter-load) | N/A | ✅ Pass | `Module appointment_jitsi loaded in 0.23s, 118 queries` |

**Ringkasan mentah dari log Odoo:** `odoo.tests.result: 0 failed, 0 error(s) of 13 tests when loading database 'appointment_jitsi_test_18'`. Dua warning non-fatal muncul persis sesuai prediksi `02_DIFF_ANALYSIS.md`: `DeprecationWarning` (create signature, `DIFF-01`) dan label clash "Company" (F-10). Log lengkap: `docker-env/logs/odoo_18.log`.

## Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru yang perlu dicatat ke `migration-records/` dari step ini — semua hasil sesuai prediksi Step 2/3, tidak ada perilaku Odoo 18 yang mengejutkan dibanding dugaan. (Temuan `action_join_video_call` collision sudah dicatat di Step 8/`FINDINGS.md` MF-04, sifatnya spesifik modul bukan version-diff general.)

## Verdict

- [x] ✅ **Semua AC prioritas Unit/Integration pass** (13/13 test PASS, 0 gagal) — lanjut ke Step 10 (QA Testing). Satu gap non-blocking (AC-04-01/`action_join_video_call`, tidak ada test eksplisit) dicatat untuk kelengkapan, tidak menghalangi gate karena risiko rendah dan behavior-nya trivial (ternary sederhana, tidak disentuh migrasi).
