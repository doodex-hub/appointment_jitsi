# Migration Acceptance Criteria — appointment_jitsi

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/01b_BASELINE_SPEC.md` + kode 19.0 (`migration/19.0`) — bukan `03_MIGRATION_SPEC.md`
**Tanggal:** 2026-09-24
**Status:** ✅ Selesai

> "Lulus" = behavior 20.0 identik dengan 19.0 (bug-for-bug), termasuk quirk. Pengecualian eksplisit hanya **AC-10-02** (deviasi `BSL-023`, MF-01). Penomoran AC mengikuti dokumen 18→19 supaya traceable; AC baru: AC-10-02, AC-15-01.

---

## AC-01 — Aktivasi Jitsi via config global

**AC-01-01** (verifies `BSL-001`, `BSL-002`, `BSL-006`) 🔶 risiko DIFF-01 + MF-03
Given setting Jitsi aktif (`is_jitsi_param` = True) dan `company_param` = company valid
When `calendar.event` dibuat (single create)
Then `access_token` terisi; `jitsi_link` diawali `https://meet.jit.si/{company}/{company}-`; `videocall_location == jitsi_link` — identik 19.0. Tidak ada exception (DIFF-01).

**AC-01-02** (verifies `BSL-002`)
Given row `is_jitsi_param` tidak ada
When event dibuat
Then `videocall_location` bukan link Jitsi (fallback Discuss) — identik 19.0.

## AC-02 — `create()` single-dict (baseline pasca MF-01 18→19)

**AC-02-01** (verifies `BSL-005`)
Given `create({... 'is_jitsi': True})`
Then `access_token` terisi non-empty (dari default core).

**AC-02-02** (verifies `BSL-005`)
Given `create({... 'is_jitsi': False, 'access_token': '<literal>'})`
Then `access_token == '<literal>'` (lolos apa adanya, tidak direset) — identik 19.0. Tidak melanggar `unique(access_token)` baru (DIFF-02).

## AC-03 — Urutan akses field menentukan hasil (quirk)

**AC-03-01** (verifies `BSL-010`) 🔶 MF-03
Given Jitsi aktif
When skenario A (baca `jitsi_link` dulu) vs B (baca `videocall_location` dulu)
Then `videocall_location` field compute resmi BUKAN `_compute_jitsi_link` (assert); nilai A vs B dicatat (observasional seperti 19.0). **Perubahan hasil observasi vs 19.0 dicatat di Step 9 sebagai dampak DIFF-04 native, bukan kode modul.**

## AC-04 — `action_join_video_call()`

**AC-04-01** (verifies `BSL-007`)
Given event `is_jitsi=True` dan event `is_jitsi=False`
When `action_join_video_call()`
Then `{'type': 'ir.actions.act_url', 'url': jitsi_link | videocall_location, 'target': 'new'}` sesuai flag — identik 19.0. (Test BARU — di 19.0 belum ada test eksplisit.)

## AC-05 — Method manual

**AC-05-01** (verifies `BSL-008`, `BSL-017`)
Given event dengan link Jitsi
When `clear_jitsi_link()` lalu `generate_jitsi_link()`
Then link kosong lalu terisi ulang; tidak ada button di view.

## AC-06 — `create()` batch (quirk)

**AC-06-01** (verifies `BSL-009`)
Given `create([dict, dict])` dengan `is_jitsi=True`
Then override tidak memengaruhi token (observasional); tidak ada exception.

## AC-07 — Toggle `is_jitsi` via `write()` tidak recompute (quirk)

**AC-07-01** (verifies `BSL-011`)
Given event existing, lalu `write({'is_jitsi': True})`
Then `videocall_location` tidak berubah karena write itu (observasional).

## AC-08 — `company_param` global (quirk)

**AC-08-01** (verifies `BSL-012`)
Given event di company A dan company B, `company_param` = A
Then kedua `jitsi_link` memuat nama A.

## AC-09 — Nama company mentah, dua kali (quirk)

**AC-09-01** (verifies `BSL-013`)
Given company "PT Doodex Indonesia"
Then `jitsi_link` mengandung spasi dan nama muncul 2×.

## AC-10 — Semantik setting global

**AC-10-01** (verifies `BSL-014`) 🔶 DIFF-01
Given admin mencentang lalu uncheck "Enable Jitsi Integration" lewat `res.config.settings.execute()`
When event baru dibuat
Then event TIDAK mendapat link Jitsi (fallback Discuss) — identik 19.0 (walau mekanisme penyimpanan native berubah: 20.0 menyimpan `"False"`, 19.0 menghapus row). (Test BARU dengan assertion; test lama `test_ac_01_03` tetap observasional.)

**AC-10-02** (verifies `BSL-023`) ⚠️ **DEVIASI DISENGAJA — MF-01**
Given `is_jitsi_param` di-set manual ke string non-boolean-true (mis. `"False"`)
Then **20.0: Jitsi NONAKTIF** (19.0: aktif). Diterima sebagai konsekuensi wajib API `get_bool` 20.0 demi AC-10-01. Diverifikasi tidak langsung lewat helper `_disable_jitsi()` (`set_bool(False)`).

## AC-11 — Override mail template tidak pernah aktif 🔴

**AC-11-01** (verifies `BSL-004`, `BSL-015`)
Given Jitsi aktif, event dengan attendee
When template "booked" appointment (20.0: `appointment.appointment_booking_mail_template`, MF-02) di-render
Then body TIDAK memuat `jitsi_link`, memuat `/calendar/meeting/join?token=`; `data/mail_template_data.xml` tetap tidak di manifest.

## AC-12 — Controller dead code

**AC-12-01** (verifies `BSL-016`)
Then `controllers/appointment.py` tanpa baris aktif; tidak ada route baru.

## AC-13 — `is_jitsi` per-event diabaikan compute

**AC-13-01** (verifies `BSL-020`)
Given event tanpa `is_jitsi` (default False), Jitsi global aktif
Then event tetap mendapat `jitsi_link` (dicakup `test_ac_01_01`).

## AC-14 — Instalasi 20.0 + Enterprise

**AC-14-01** (verifies `BSL-021`, `BSL-019`, `BSL-022`)
When `-i appointment_jitsi` di Odoo 20.0 + `enterprise20`
Then install tanpa ERROR; settings view ter-render (xpath valid); act_window orphan ter-load.

## AC-15 — Settings view

**AC-15-01** (verifies `BSL-001`)
Given form Settings (`res.config.settings`)
Then blok "Jitsi Configuration" muncul setelah "Google Calendar", field Company muncul hanya saat dicentang (dicek via arch hasil `get_views` di Step 9 dan visual di Step 10).
