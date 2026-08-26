# Test Plan (Migrasi) — appointment_jitsi

**Step:** 5 — Acceptance Criteria & Test Plan (satu paket dengan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-26

---

## Step 9 — Dev Testing

> Eksekusi: **otomatis/background** — `odoo-bin -i appointment_jitsi --test-enable --test-tags /appointment_jitsi --stop-after-init`, dengan `enterprise19.0` (folder gabungan Community+Enterprise, BUKAN git repo) di-mount sebagai extra addons path (lihat AC-14-01). Tidak ada Owl/JS/Tour. Semua 13 test method di `tests/test_appointment_jitsi.py` di-port apa adanya dari 18.0, dijalankan ulang terhadap 19.0 sebagai regression check — **dengan perhatian khusus per-assertion untuk AC-02-01/AC-06-01 (MF-01), bukan cuma count PASS/FAIL agregat.**

| AC | Deskripsi | Unit | Integration | Tour |
|---|---|---|---|---|
| AC-01-01, AC-01-02 | Aktivasi Jitsi via config global | — | Existing (`test_ac_01_01_...`, `test_ac_01_02_...`) | N/A |
| **AC-02-01** ⚠️ MF-01 | `create()` single-dict | — | Existing (`test_ac_02_01_...`, `test_ac_02_02_...`) — **WAJIB baca assertion detail, bukan cuma status PASS**: kalau assertion mengecek `access_token` di-set EKSPLISIT oleh cabang `create()` (bukan cuma "ada nilai"), assertion itu bisa PASS-dengan-alasan-berbeda (lewat fallback compute, bukan cabang create) — catat di `06c_IMPLEMENTATION_LOG.md` mana yang terjadi | N/A |
| AC-03-01 | Urutan akses field (quirk) | — | Existing (`test_ac_03_01_videocall_location_race_with_core_compute`) | N/A |
| AC-04-01 | `action_join_video_call()` | — | Cek apakah sudah ter-cover implisit test existing (lihat catatan project 17.0→18.0: "belum ada test eksplisit, gap non-blocking") — kalau masih belum, tetap non-blocking untuk migrasi ini | N/A |
| AC-05-01 | Method manual tidak di UI | — | Existing (`test_ac_08_...`) — cek struktural, bukan eksekusi | N/A |
| **AC-06-01** ⚠️ MF-01 | `create()` batch (quirk) | — | Existing (`test_ac_02_03_create_batch_list_is_jitsi_check_fails`) — **bandingkan hasil vs baseline 18.0**, dugaan: TETAP SAMA (batch sudah menerima list di kedua versi) tapi WAJIB dikonfirmasi eksekusi, bukan diasumsikan | N/A |
| AC-07-01 | Toggle `write()` tidak recompute (quirk) | — | Existing (`test_ac_04_01_write_toggle_no_recompute`) | N/A |
| AC-08-01 | `company_param` global (quirk) | — | Existing (`test_ac_05_...` multi-company) | N/A |
| AC-09-01 | Format URL tidak di-slug (quirk) | — | Existing (`test_ac_06_01_...`) | N/A |
| AC-10-01 | `is_jitsi_param` non-bug | — | Existing (`test_ac_01_03_uncheck_setting_still_truthy`) | N/A |
| **AC-11-01** 🔴 | Mail template tidak aktif (paling kritis) | — | Existing (`test_qa_s01_mail_template_does_not_render_jitsi_link`) — **WAJIB dijalankan ulang eksplisit, hasil harus PASS (bug tetap ada)** | N/A |
| AC-12-01 | Controller dead code | — | Existing (`test_ac_07_01_...`) | N/A |
| AC-13-01 | `is_jitsi` per-event diabaikan (quirk) | — | Existing (`test_ac_01_01_...` sudah mencakup ini secara implisit) | N/A |
| AC-14-01 | Dependency Enterprise | — | Cek instalasi — install log harus bersih dengan `enterprise19.0` mounted | N/A |

**Audit kesiapan test:** 13 method di `tests/test_appointment_jitsi.py` sudah diverifikasi BUKAN stub sejak backfill DAN sudah PASS terhadap 18.0 (`doc-dev/migration_17.0_18.0/doc/09_devtest/09_DEV_TESTING.md`). Tidak perlu audit ulang dari nol — cukup re-run terhadap 19.0 dengan perhatian ekstra ke assertion AC-02-01/AC-06-01.

## Step 10 — QA Testing

> Mode: **Manual** (dev/QA sendiri, single owner) — modul kecil, tidak ada UI kompleks yang butuh AI-interaktif/tool eksternal.

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-01-01 | Smoke: aktifkan setting, buat event, cek link Jitsi terbentuk | ✅ | — | — |
| **AC-02-01/AC-06-01** ⚠️ | Smoke: buat event tunggal DAN recurring event (batch), cek `jitsi_link` terbentuk di kedua kasus — reproduksi live temuan MF-01 | ✅ | — | — |
| **AC-11-01** 🔴 | Smoke: kirim/preview email konfirmasi appointment, pastikan TIDAK ada link Jitsi | ✅ | — | — |
| AC-14-01 | Smoke: instalasi modul bersih di Odoo 19 Enterprise (Apps → Install) | ✅ | — | — |

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Aktivasi & penggunaan Jitsi | AC-01, AC-02, AC-04, AC-13 | Owner modul konfirmasi behavior toggle + generate link identik (observable) dengan 18.0, termasuk klarifikasi MF-01 kalau mekanisme internal `create()` berubah |
| Bug/quirk yang dipertahankan | AC-03, AC-06, AC-07, AC-08, AC-09, AC-11 | Owner modul sign-off eksplisit bahwa SEMUA quirk ini memang sengaja dipertahankan |
| Instalasi & infrastruktur | AC-14 | Konfirmasi modul terinstall bersih di lingkungan 19.0 Enterprise final |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer (Kuncoro) | Integration (TransactionCase) | Otomatis/background, re-run 13 test existing, perhatian ekstra AC-02-01/AC-06-01 (MF-01) | 14 |
| 10 | QA (Kuncoro) | Manual | 4 smoke check, prioritas AC-11 + AC-02/AC-06 | 4 |
| 11 | Owner modul (Kuncoro) | UAT | Manual, sign-off per kelompok fitur | 3 kelompok |
