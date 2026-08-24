# Migration Acceptance Criteria — appointment_jitsi

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/01b_BASELINE_SPEC.md` dan kode 17.0 yang berjalan — bukan `03_MIGRATION_SPEC.md`
**Tanggal:** 2026-08-24

> Tiap AC di bawah HARUS lulus dengan hasil **identik** dengan 17.0 (bug-for-bug) — "lulus" untuk modul ini berarti behavior 18.0 SAMA PERSIS dengan `01b_BASELINE_SPEC.md`, termasuk bug/quirk-nya. AC yang memverifikasi bug yang harus dipertahankan (mis. AC-11) dianggap **PASS** kalau bug itu TETAP terjadi di 18.0 — bukan sebaliknya.

---

## AC-01 — Aktivasi Jitsi via config global

**AC-01-01** (verifies `BSL-001`, `BSL-002`)
Given `ir.config_parameter('is_jitsi_param')` truthy dan `company_param` menunjuk company valid
When `calendar.event` dibuat/di-recompute (`access_token` berubah)
Then `jitsi_link`/`videocall_location` terisi format `https://meet.jit.si/{company}/{company}-{access_token}` — identik dengan 17.0

**AC-01-02** (verifies `BSL-002`)
Given `is_jitsi_param` tidak aktif
When `_compute_jitsi_link` jalan
Then event jatuh ke `_set_discuss_videocall_location()` (fallback Discuss) — identik dengan 17.0

## AC-02 — `create()` single-dict behavior

**AC-02-01** (verifies `BSL-005`)
Given payload `create()` satu dict dengan `is_jitsi=True`/`False`
When `calendar.event.create(values)` dipanggil
Then `access_token` di-set UUID baru (True) atau `False` eksplisit (False) — identik dengan 17.0, TIDAK diubah ke `@api.model_create_multi`

## AC-03 — Urutan akses field menentukan hasil compute (quirk, WAJIB tetap ada)

**AC-03-01** (verifies `BSL-006`, `BSL-010`)
Given setup identik, `is_jitsi_param` aktif
When `jitsi_link` diakses DULU vs `videocall_location` diakses DULU (tanpa pernah baca `jitsi_link`)
Then hasil BERBEDA (skenario A: keduanya berisi URL Jitsi; skenario B: `videocall_location` = compute resmi core, `jitsi_link` tidak pernah ter-compute) — **PASS berarti quirk ini TETAP terjadi**, bukan diperbaiki

## AC-04 — `action_join_video_call()`

**AC-04-01** (verifies `BSL-007`)
Given event dengan `is_jitsi` true/false
When `action_join_video_call()` dipanggil
Then return `ir.actions.act_url` ke `jitsi_link` (true) atau `videocall_location` (false), `target: 'new'`

## AC-05 — Method manual tidak terhubung UI

**AC-05-01** (verifies `BSL-008`, `BSL-017`)
Given `generate_jitsi_link()`/`clear_jitsi_link()` didefinisikan di model
When cek `views/calendar_views.xml`
Then TIDAK ada button/server action yang memanggilnya — sama seperti 17.0 (method tetap berfungsi kalau dipanggil langsung via kode/shell)

## AC-06 — `create()` tidak batch-safe (quirk, WAJIB tetap ada)

**AC-06-01** (verifies `BSL-009`)
Given `create()` dipanggil dengan LIST berisi >1 dict (mis. recurring event)
When override `create()` modul ini menjalankan `'is_jitsi' in values`
Then pengecekan gagal jalan sesuai desain awal (cek keanggotaan string di list, bukan di tiap dict) — `access_token` tetap terisi lewat default core, TAPI efek reset eksplisit `is_jitsi=False` tidak terjadi untuk batch — **PASS berarti perilaku ini TETAP identik dengan 17.0**

## AC-07 — Toggle `is_jitsi` via `write()` tidak memicu recompute (quirk, WAJIB tetap ada)

**AC-07-01** (verifies `BSL-011`)
Given event existing `is_jitsi=False` (link Discuss aktif)
When `write({'is_jitsi': True})` dipanggil (setting Jitsi aktif, TANPA mengubah field lain)
Then `jitsi_link`/`videocall_location` TIDAK ter-recompute — **PASS berarti bug ini tetap terjadi**

## AC-08 — `company_param` global (quirk, WAJIB tetap ada)

**AC-08-01** (verifies `BSL-012`)
Given 2 event milik 2 company berbeda (multi-company aktif)
When `_compute_jitsi_link` jalan untuk keduanya
Then KEDUA event pakai `company_name` yang SAMA dari `company_param` global — **PASS berarti tidak per-company**, sama seperti 17.0

## AC-09 — Format URL tidak di-slug (quirk, WAJIB tetap ada)

**AC-09-01** (verifies `BSL-013`)
Given `company_param` menunjuk company bernama mengandung spasi
When `jitsi_link` dibentuk
Then string company disisipkan APA ADANYA (tidak di-slug/encode), segmen path terduplikasi — sama seperti 17.0

## AC-10 — `is_jitsi_param` bukan truthy-string bug (konfirmasi non-bug tetap berlaku)

**AC-10-01** (verifies `BSL-014`)
Given admin PERNAH centang lalu uncheck "Enable Jitsi Integration"
When `_compute_jitsi_link` jalan sesudahnya
Then `get_param('is_jitsi_param')` balik bool `False` asli (row `ir.config_parameter` dihapus Odoo core) — **cek ulang di 18.0**, karena ini bergantung mekanisme Odoo core yang bisa saja beda per versi (walau dari `02_DIFF_ANALYSIS.md` tidak ditemukan indikasi perubahan)

## AC-11 — Override mail template TIDAK PERNAH AKTIF (bug paling kritis, WAJIB tetap ada) 🔴

**AC-11-01** (verifies `BSL-004`, `BSL-015`)
Given `is_jitsi_param` aktif, `jitsi_link` event terisi penuh, event punya minimal satu attendee
When `appointment.appointment_booked_mail_template` di-render
Then body HTML hasil render TIDAK mengandung `jitsi_link` sama sekali — identik dengan template ASLI Odoo core, `data/mail_template_data.xml` TETAP tidak terdaftar di `__manifest__.py` 18.0. **PASS = bug tetap tereproduksi.** Ini adalah test paling penting di seluruh migrasi ini (lihat `FINDINGS.md` MF-01) — kalau AC ini malah menunjukkan `jitsi_link` MUNCUL di email, itu regresi tidak disengaja (`data/mail_template_data.xml` keceplosan terdaftar) yang WAJIB di-escalate, bukan dianggap "perbaikan bonus".

## AC-12 — Controller dead code

**AC-12-01** (verifies `BSL-016`)
Given `controllers/appointment.py` seluruh isi di-comment-out
When modul di-install/upgrade di 18.0
Then TIDAK ADA route HTTP tambahan terdaftar dari modul ini — sama seperti 17.0

## AC-13 — Field per-event `is_jitsi` tidak dipakai di compute (quirk, WAJIB tetap ada)

**AC-13-01** (verifies `BSL-020`)
Given event dibuat TANPA `is_jitsi=True` sama sekali (default `False`)
When `is_jitsi_param` global aktif
Then event TETAP mendapat `jitsi_link` penuh — **PASS berarti field per-event tetap diabaikan di compute**, sama seperti 17.0

## AC-14 — Dependency Enterprise (infrastruktur, bukan behavior modul)

**AC-14-01** (verifies `BSL-021`)
Given modul depend ke `appointment` (Enterprise, `OEEL-1`)
When modul di-install di lingkungan test 18.0
Then instalasi WAJIB pakai `enterprise18` sebagai extra addons path (bukan image Community publik `odoo:18.0` saja) — cek infrastruktur, bukan AC fungsional modul
