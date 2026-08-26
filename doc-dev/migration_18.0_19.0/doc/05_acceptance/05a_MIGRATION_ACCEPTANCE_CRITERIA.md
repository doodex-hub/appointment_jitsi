# Migration Acceptance Criteria — appointment_jitsi

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/01b_BASELINE_SPEC.md` dan kode 18.0 yang berjalan — bukan `03_MIGRATION_SPEC.md`
**Tanggal:** 2026-08-26

> Tiap AC di bawah HARUS lulus dengan hasil **identik** dengan 18.0 (bug-for-bug) — "lulus" berarti behavior 19.0 SAMA PERSIS dengan `01b_BASELINE_SPEC.md`, termasuk bug/quirk-nya. **Kecuali AC-02/AC-06** (lihat catatan `⚠️ MF-01` di masing-masing) — untuk keduanya, "identik" berarti *observable outcome* (`jitsi_link` akhirnya terisi benar atau tidak), BUKAN wajib mekanisme internal yang sama persis, karena `02_DIFF_ANALYSIS.md` DIFF-01 mengonfirmasi mekanisme `@api.model create` di ORM core BERUBAH 18.0→19.0.

---

## AC-01 — Aktivasi Jitsi via config global

**AC-01-01** (verifies `BSL-001`, `BSL-002`)
Given `ir.config_parameter('is_jitsi_param')` truthy dan `company_param` menunjuk company valid
When `calendar.event` dibuat/di-recompute (`access_token` berubah)
Then `jitsi_link`/`videocall_location` terisi format `https://meet.jit.si/{company}/{company}-{access_token}` — identik dengan 18.0

**AC-01-02** (verifies `BSL-002`)
Given `is_jitsi_param` tidak aktif
When `_compute_jitsi_link` jalan
Then event jatuh ke `_set_discuss_videocall_location()` (fallback Discuss) — identik dengan 18.0

## AC-02 — `create()` single-dict behavior ⚠️ MF-01 — RESOLVED, deviation diterima dev 2026-08-26

**AC-02-01** (verifies `BSL-005`)
Given payload `create()` satu dict dengan `is_jitsi=True`
When `calendar.event.create(values)` dipanggil
Then `access_token` tetap terisi non-empty (via mekanisme default core, BUKAN lagi cabang eksplisit `create()` yang tidak terpicu lagi di 19.0 — `DIFF-01`/`MF-01`). **Deviation diterima:** format token berubah dari 32-char `uuid4().hex` (18.0) jadi 36-char UUID berdash (19.0) — kosmetik, bukan regresi fungsional. Dikonfirmasi empiris G1.

**AC-02-02** (verifies `BSL-005`) — **deviation diterima, BUKAN lagi "identik 18.0"**
Given payload `create()` satu dict dengan `is_jitsi=False` DAN `access_token` eksplisit dikirim caller
When `calendar.event.create(values)` dipanggil
Then **(19.0, BERBEDA dari 18.0)** nilai `access_token` yang dikirim caller LOLOS APA ADANYA, TIDAK direset `False` lagi — cabang eksplisit reset di `create()` tidak terpicu untuk single-create (`MF-01`). Dev eksplisit menerima deviation ini (2026-08-26) demi mempertahankan `[BSL-009]` (quirk batch-create) tetap utuh — dua-duanya tidak bisa dipertahankan bersamaan di 19.0 (lihat `FINDINGS.md` MF-01 untuk analisis lengkap).

## AC-03 — Urutan akses field menentukan hasil compute (quirk, WAJIB tetap ada)

**AC-03-01** (verifies `BSL-006`, `BSL-010`)
Given setup identik, `is_jitsi_param` aktif
When `jitsi_link` diakses DULU vs `videocall_location` diakses DULU (tanpa pernah baca `jitsi_link`)
Then hasil BERBEDA (skenario A: keduanya berisi URL Jitsi; skenario B: `videocall_location` = compute resmi core, `jitsi_link` tidak pernah ter-compute) — **PASS berarti quirk ini TETAP terjadi**, bukan diperbaiki. Tidak terdampak `DIFF-01` (compute, bukan create).

## AC-04 — `action_join_video_call()`

**AC-04-01** (verifies `BSL-007`)
Given event dengan `is_jitsi` true/false
When `action_join_video_call()` dipanggil
Then return `ir.actions.act_url` ke `jitsi_link` (true) atau `videocall_location` (false), `target: 'new'`

## AC-05 — Method manual tidak terhubung UI

**AC-05-01** (verifies `BSL-008`, `BSL-017`)
Given `generate_jitsi_link()`/`clear_jitsi_link()` didefinisikan di model
When cek `views/calendar_views.xml`
Then TIDAK ada button/server action yang memanggilnya — sama seperti 18.0

## AC-06 — `create()` tidak batch-safe (quirk, WAJIB tetap ada) ⚠️ MF-01

**AC-06-01** (verifies `BSL-009`)
Given `create()` dipanggil dengan LIST berisi >1 dict (mis. recurring event)
When override `create()` modul ini menjalankan `'is_jitsi' in values`
Then **observable outcome yang WAJIB identik:** `access_token` tetap terisi lewat default core/compute untuk tiap event batch, efek reset eksplisit `is_jitsi=False` per-item TIDAK terjadi untuk batch — **behavior ini kemungkinan besar TETAP SAMA di 19.0** (karena `values` SUDAH list juga di 18.0 untuk kasus batch — `DIFF-01` cuma mengubah kasus SINGLE-create, bukan batch). **WAJIB dijalankan ulang untuk konfirmasi**, jangan diasumsikan dari analisis ini saja.

## AC-07 — Toggle `is_jitsi` via `write()` tidak memicu recompute (quirk, WAJIB tetap ada)

**AC-07-01** (verifies `BSL-011`)
Given event existing `is_jitsi=False` (link Discuss aktif)
When `write({'is_jitsi': True})` dipanggil (setting Jitsi aktif, TANPA mengubah field lain)
Then `jitsi_link`/`videocall_location` TIDAK ter-recompute — **PASS berarti bug ini tetap terjadi**

## AC-08 — `company_param` global (quirk, WAJIB tetap ada)

**AC-08-01** (verifies `BSL-012`)
Given 2 event milik 2 company berbeda (multi-company aktif)
When `_compute_jitsi_link` jalan untuk keduanya
Then KEDUA event pakai `company_name` yang SAMA dari `company_param` global — **PASS berarti tidak per-company**, sama seperti 18.0

## AC-09 — Format URL tidak di-slug (quirk, WAJIB tetap ada)

**AC-09-01** (verifies `BSL-013`)
Given `company_param` menunjuk company bernama mengandung spasi
When `jitsi_link` dibentuk
Then string company disisipkan APA ADANYA (tidak di-slug/encode), segmen path terduplikasi — sama seperti 18.0

## AC-10 — `is_jitsi_param` bukan truthy-string bug (konfirmasi non-bug tetap berlaku)

**AC-10-01** (verifies `BSL-014`)
Given admin PERNAH centang lalu uncheck "Enable Jitsi Integration"
When `_compute_jitsi_link` jalan sesudahnya
Then `get_param('is_jitsi_param')` balik bool `False` asli (row `ir.config_parameter` dihapus Odoo core) — **cek ulang di 19.0**, mekanisme Odoo core bisa saja beda per versi (tidak ditemukan indikasi perubahan di `02_DIFF_ANALYSIS.md`, tapi belum diverifikasi eksekusi nyata)

## AC-11 — Override mail template TIDAK PERNAH AKTIF (bug paling kritis, WAJIB tetap ada) 🔴

**AC-11-01** (verifies `BSL-004`, `BSL-015`)
Given `is_jitsi_param` aktif, `jitsi_link` event terisi penuh, event punya minimal satu attendee
When `appointment.appointment_booked_mail_template` di-render
Then body HTML hasil render TIDAK mengandung `jitsi_link` sama sekali — identik dengan template ASLI Odoo core, `data/mail_template_data.xml` TETAP tidak terdaftar di `__manifest__.py` 19.0. **PASS = bug tetap tereproduksi.** Test paling penting di seluruh migrasi ini — kalau AC ini malah menunjukkan `jitsi_link` MUNCUL di email, itu regresi tidak disengaja yang WAJIB di-escalate.

## AC-12 — Controller dead code

**AC-12-01** (verifies `BSL-016`)
Given `controllers/appointment.py` seluruh isi di-comment-out
When modul di-install/upgrade di 19.0
Then TIDAK ADA route HTTP tambahan terdaftar dari modul ini — sama seperti 18.0

## AC-13 — Field per-event `is_jitsi` tidak dipakai di compute (quirk, WAJIB tetap ada)

**AC-13-01** (verifies `BSL-020`)
Given event dibuat TANPA `is_jitsi=True` sama sekali (default `False`)
When `is_jitsi_param` global aktif
Then event TETAP mendapat `jitsi_link` penuh — **PASS berarti field per-event tetap diabaikan di compute**, sama seperti 18.0

## AC-14 — Dependency Enterprise (infrastruktur, bukan behavior modul)

**AC-14-01** (verifies `BSL-021`)
Given modul depend ke `appointment` (Enterprise, `OEEL-1`, dikonfirmasi ulang tetap Enterprise di 19.0)
When modul di-install di lingkungan test 19.0
Then instalasi WAJIB pakai `enterprise19.0` (folder gabungan Community+Enterprise, bukan git repo) sebagai extra addons path — cek infrastruktur, bukan AC fungsional modul
