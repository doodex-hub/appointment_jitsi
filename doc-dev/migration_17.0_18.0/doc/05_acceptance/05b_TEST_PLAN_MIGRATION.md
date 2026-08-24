# Test Plan (Migrasi) — appointment_jitsi

**Step:** 5 — Acceptance Criteria & Test Plan (satu paket dengan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-24

---

## Step 9 — Dev Testing

> Eksekusi: **otomatis/background** — `odoo-bin -i appointment_jitsi --test-enable --test-tags /appointment_jitsi --stop-after-init`, dengan `enterprise18` di-mount sebagai extra addons path (lihat AC-14-01). Tidak ada Owl/JS/Tour (modul tidak punya komponen frontend). Semua 13 test method di `tests/test_appointment_jitsi.py` sudah ADA dari backfill (bukan stub — sudah diverifikasi jalan nyata terhadap 17.0, lihat `doc-dev/backfill/test/04A_DEV_TESTING.md`) dan **di-port apa adanya**, dijalankan ulang terhadap 18.0 sebagai regression check.

| AC | Deskripsi | Unit | Integration | Tour |
|---|---|---|---|---|
| AC-01-01, AC-01-02 | Aktivasi Jitsi via config global | — | Existing (`test_ac_01_01_...`, `test_ac_01_02_...`) | N/A |
| AC-02-01 | `create()` single-dict | — | Existing (`test_ac_02_01_...`, `test_ac_02_02_...`) | N/A |
| AC-03-01 | Urutan akses field (quirk) | — | Existing (`test_ac_03_01_videocall_location_race_with_core_compute`) | N/A |
| AC-04-01 | `action_join_video_call()` | — | Baru — belum ada test eksplisit di backfill, tambahkan di Step 9 kalau belum ter-cover implisit | N/A |
| AC-05-01 | Method manual tidak di UI | — | Existing (`test_ac_08_...`) — cek struktural (grep view), bukan eksekusi | N/A |
| AC-06-01 | `create()` batch (quirk) | — | Existing (`test_ac_02_03_create_batch_list_is_jitsi_check_fails`) | N/A |
| AC-07-01 | Toggle `write()` tidak recompute (quirk) | — | Existing (`test_ac_04_01_write_toggle_no_recompute`) | N/A |
| AC-08-01 | `company_param` global (quirk) | — | Existing (`test_ac_05_...` multi-company) | N/A |
| AC-09-01 | Format URL tidak di-slug (quirk) | — | Existing (`test_ac_06_01_...`) | N/A |
| AC-10-01 | `is_jitsi_param` non-bug | — | Existing (`test_ac_01_03_uncheck_setting_still_truthy`) | N/A |
| **AC-11-01** 🔴 | Mail template tidak aktif (paling kritis) | — | Existing (`test_qa_s01_mail_template_does_not_render_jitsi_link`) — **WAJIB dijalankan ulang eksplisit, hasil harus PASS (bug tetap ada)** | N/A |
| AC-12-01 | Controller dead code | — | Existing (`test_ac_07_01_...`) | N/A |
| AC-13-01 | `is_jitsi` per-event diabaikan (quirk) | — | Existing (`test_ac_01_01_...` sudah mencakup ini secara implisit) | N/A |
| AC-14-01 | Dependency Enterprise | — | Cek instalasi (bukan test method) — install log harus bersih dengan `enterprise18` mounted | N/A |

**Audit kesiapan test (per peringatan template):** 13 method di `tests/test_appointment_jitsi.py` sudah diverifikasi BUKAN stub saat backfill (semua mengandung assertion nyata, dikonfirmasi hasil eksekusi PASS di `doc-dev/backfill/test/04A_DEV_TESTING.md`) — tidak perlu audit ulang dari nol, cukup re-run terhadap 18.0.

## Step 10 — QA Testing

> Mode: **Manual** (dev/QA sendiri, single owner) — modul kecil, tidak ada UI kompleks yang butuh AI-interaktif/tool eksternal.

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-01-01 | Smoke: aktifkan setting, buat event, cek link Jitsi terbentuk | ✅ | — | — |
| **AC-11-01** 🔴 | Smoke: kirim/preview email konfirmasi appointment, pastikan TIDAK ada link Jitsi (cuma link "Join" standar) — konfirmasi bug tetap ada, bukan regresi baru | ✅ | — | — |
| AC-14-01 | Smoke: instalasi modul bersih di Odoo 18 Enterprise (Apps → Install) | ✅ | — | — |

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Aktivasi & penggunaan Jitsi | AC-01, AC-02, AC-04, AC-13 | Owner modul konfirmasi behavior toggle + generate link identik dengan 17.0 |
| Bug/quirk yang dipertahankan (F-01..F-13) | AC-03, AC-06, AC-07, AC-08, AC-09, AC-11 | Owner modul sign-off eksplisit bahwa SEMUA quirk ini memang sengaja dipertahankan (bukan kelupaan) — rujuk `FINDINGS.md` MF-01/MF-02 |
| Instalasi & infrastruktur | AC-14 | Konfirmasi modul terinstall bersih di lingkungan 18.0 Enterprise final (bukan cuma docker dev) |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer (Kuncoro) | Integration (TransactionCase) | Otomatis/background, re-run 13 test existing + 1 test baru (AC-04-01) | 14 |
| 10 | QA (Kuncoro) | Manual | 3 smoke check, prioritas AC-11 | 3 |
| 11 | Owner modul (Kuncoro) | UAT | Manual, sign-off per kelompok fitur | 3 kelompok |
