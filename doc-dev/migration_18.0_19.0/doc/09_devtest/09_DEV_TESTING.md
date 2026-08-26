# Dev Testing — appointment_jitsi

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-08-26

---

**Eksekusi aktual (2026-08-26, Mode C — AI jalankan langsung, dikonfirmasi dev):**
```
MSYS_NO_PATHCONV=1 docker compose -f docker-env/docker-compose.19.0.yml up --abort-on-container-exit
```
(`command:` di dalam compose: `odoo -d appointment_jitsi_test_19 -i appointment_jitsi --addons-path=...,/mnt/enterprise-addons,/mnt/extra-addons --test-enable --test-tags=/appointment_jitsi --stop-after-init`)

**Butuh 4 percobaan** (lihat `06_implementation/06c_IMPLEMENTATION_LOG.md` untuk kronologi lengkap) — hasil final di bawah dari **percobaan ke-4**, setelah 2 infra fix (pgvector, `target=inline`) dan 1 keputusan dev (`MF-01`, terima observable-outcome baru + update 2 assertion).

**Verifikasi anti-false-pass:** `grep -c "^    def test_"` pada `tests/test_appointment_jitsi.py` = **13**. Log menunjukkan 13 baris `Starting TestAppointmentJitsi.test_...` dengan nama method asli — angka cocok persis, tag filter bekerja benar (`MSYS_NO_PATHCONV=1` dipakai).

## 9a. Audit Kesiapan Test

13 method sudah diaudit isinya di project 17.0→18.0 sebelumnya (semua mengandung assertion nyata, bukan stub). Untuk migrasi ini, 2 method (`test_ac_02_01`, `test_ac_02_02`) di-EDIT SENGAJA (Step 6, disetujui dev) untuk mencerminkan baseline 19.0 yang baru terkait `MF-01` — bukan dilonggarkan sembarangan, tiap perubahan assertion disertai docstring yang menjelaskan alasan lengkap. 11 method lain tidak disentuh sama sekali.

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01, AC-01-02, AC-01-03 | Aktivasi Jitsi global | `test_appointment_jitsi.py` | ✅ Lengkap | Tidak diubah |
| **AC-02-01, AC-02-02** ⚠️ | `create()` single-dict | `test_appointment_jitsi.py` | ✅ Lengkap, assertion diupdate | Lihat docstring test — deviation `MF-01` disetujui dev |
| AC-02-03 | `create()` batch | `test_appointment_jitsi.py` | ✅ Lengkap | Tidak diubah |
| AC-03-01 | Urutan akses field | `test_appointment_jitsi.py` | ✅ Lengkap | Tidak diubah |
| AC-04-01 (write toggle, `BSL-011`) | Toggle `write()` tidak recompute | `test_appointment_jitsi.py` | ✅ Lengkap | Tidak diubah |
| AC-04-01 (05a — `action_join_video_call`, `BSL-007`) | Return action URL | — | ❌ Tidak ada test | Gap lama diwarisi 17.0→18.0, tidak diperluas scope-nya di migrasi ini |
| AC-05-01..AC-13-01 | Sisa quirk | `test_appointment_jitsi.py` | ✅ Lengkap | Tidak diubah |
| **AC-11-01** 🔴 | Mail template tidak aktif | `test_appointment_jitsi.py` | ✅ Lengkap | Test paling kritis — hasil di bawah |
| AC-14-01 | Dependency Enterprise | — (cek instalasi) | ✅ Terverifikasi via install log | — |

**Verdict audit:** Semua AC prioritas tinggi (terutama AC-11-01) Lengkap. Gap non-blocking (AC-04-01/`action_join_video_call`) diwarisi apa adanya, tidak diperluas di migrasi ini.

## Baseline

- Characterization test asli: 13 method, hasil run terhadap 18.0 (project 17.0→18.0): **13/13 PASS**.
- Applicability Check Fase E (Owl/JS): **Tidak, N/A**.

## Hasil Unit, Integration & Tour Test (target-codebase, Odoo 19.0, percobaan ke-4)

| AC | Integration | Tour | Pass/Fail | Catatan |
|---|---|---|---|---|
| AC-01-01 | `test_ac_01_01_jitsi_link_format_when_enabled` | N/A | ✅ Pass | `jitsi_link=https://meet.jit.si/My Company/My Company-<uuid>` — format identik 18.0 |
| AC-01-02 | `test_ac_01_02_fallback_discuss_when_disabled` | N/A | ✅ Pass | `get_param=False`, fallback Discuss |
| AC-01-03 | `test_ac_01_03_uncheck_setting_still_truthy` | N/A | ✅ Pass | `get_param setelah uncheck = False (type=bool)` — F-01 tetap non-bug di 19.0 |
| **AC-02-01** ⚠️ | `test_ac_02_01_create_single_dict_enables_token` | N/A | ✅ Pass (assertion diupdate) | `access_token` terisi non-empty (format 36-char, bukan lagi 32-char `.hex` — `MF-01`, deviation disetujui) |
| **AC-02-02** ⚠️ | `test_ac_02_02_create_single_dict_disable_resets_token` | N/A | ✅ Pass (assertion diupdate) | `access_token` = `'should-be-overwritten'` (nilai caller lolos apa adanya, TIDAK direset — `MF-01`, deviation disetujui) |
| AC-02-03 | `test_ac_02_03_create_batch_list_is_jitsi_check_fails` | N/A | ✅ Pass | `bug_confirmed=False` — identik 18.0, `[BSL-009]` TERJAGA UTUH (poin krusial keputusan dev di `MF-01`) |
| AC-03-01 | `test_ac_03_01_videocall_location_race_with_core_compute` | N/A | ✅ Pass (bug tereproduksi) | Skenario A: Jitsi penuh. Skenario B: `videocall_location=False`. `bug_confirmed=True` — identik `[BSL-010]` |
| AC-07-01 (write toggle) | `test_ac_04_01_write_toggle_no_recompute` | N/A | ✅ Pass (bug tereproduksi) | `before=False after=False`, `bug_confirmed=True` — identik `[BSL-011]` |
| AC-08-01 | `test_ac_05_01_company_param_global_multi_company` | N/A | ✅ Pass | Dua event, `company_name` sama — identik `[BSL-012]` |
| AC-09-01 | `test_ac_06_01_company_name_with_space_not_escaped` | N/A | ✅ Pass | `.../PT Doodex Indonesia/PT Doodex Indonesia-<uuid>` — spasi mentah, identik `[BSL-013]` |
| AC-12-01 | `test_ac_07_01_controller_is_dead_code` | N/A | ✅ Pass | 0 baris aktif |
| AC-05-01 (generate/clear) | `test_ac_08_01_generate_and_clear_jitsi_link_still_work` | N/A | ✅ Pass | — |
| **AC-11-01** 🔴 | `test_qa_s01_mail_template_does_not_render_jitsi_link` | N/A | ✅ **Pass — bug tereproduksi persis** | `jitsi_link` terisi penuh, `muncul_di_body=False` — email TETAP tidak menampilkan link Jitsi di 19.0, identik `[BSL-015]`/F-13 |
| AC-04-01 (`action_join_video_call`) | — (tidak ada test) | N/A | ⚠️ Tidak dieksekusi | Gap test coverage lama, risiko rendah |
| AC-14-01 | Install log (`enterprise19.0` mounted, `appointment` ter-load) | N/A | ✅ Pass | `Module appointment_jitsi loaded` bersih, `Registry loaded in ~60.8s` |

**Ringkasan mentah dari log Odoo (percobaan ke-4):** `odoo.tests.result: 0 failed, 0 error(s) of 13 tests when loading database 'appointment_jitsi_test_19'`. Warning non-fatal yang muncul: `Two fields (company_param, company_id) ... have the same label: Company` (`[BSL-019]`, identik prediksi). Log lengkap: `docker-env/logs/odoo_19.log`.

**Percobaan ke-3 (SEBELUM keputusan dev, untuk audit trail):** `2 failed, 0 error(s)` — `test_ac_02_01` (`AssertionError: 36 != 32`), `test_ac_02_02` (`AssertionError: 'should-be-overwritten' is not false`). Keduanya konsisten prediksi `MF-01`, bukan bug baru yang mengejutkan.

## Kontribusi ke Knowledge Base

- [x] Ada — 3 temuan general dicatat ke `migration-records/appointment_jitsi_18.0_19.0/SUMMARY.md`: `@api.model create` routing (Step 2), pgvector requirement (Step 6), `target=inline` dihapus (Step 6). Ketiganya kandidat kuat untuk `knowledge/version-diffs/18-to-19.md` — jauh lebih banyak temuan general baru dibanding migrasi 17.0→18.0 (0 temuan baru selain kolisi method spesifik-modul), konsisten kesimpulan ini adalah project migrasi 18.0→19.0 KEDUA lewat `migration-tool` dan pasangan versi ini masih relatif "segar" (belum banyak dieksplorasi).

## Verdict

- [x] ✅ **Semua AC prioritas Unit/Integration pass** (13/13 test PASS, 0 gagal, di percobaan final) — lanjut ke Step 10 (QA Testing). Dua deviation observable (`MF-01`, AC-02-01/02) sudah disetujui dev eksplisit, bukan gap tersembunyi. Satu gap non-blocking (AC-04-01) diwarisi apa adanya dari project sebelumnya.
