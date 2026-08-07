# Acceptance Criteria — appointment_jitsi

**Module:** `appointment_jitsi`
**Ref:** `01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-08-07
**Status:** Backfill retroaktif

> Format: Given/When/Then, diturunkan dari Business Rules (BR-*) di `01A_FUNCTIONAL_SPEC.md`.

---

## AC-01 — Aktivasi Jitsi via config global (BR-01, BR-08)

**AC-01-01** — ref `BR-01` `[HASIL-BACA]`
Given `ir.config_parameter('is_jitsi_param')` sudah pernah di-set truthy ("True") dan
`company_param` menunjuk company valid
When sebuah `calendar.event` dibuat/direcompute (`access_token` berubah)
Then `jitsi_link` dan `videocall_location` terisi format
`https://meet.jit.si/{company_name}/{company_name}-{access_token}`

**AC-01-02** — ref `BR-01` `[HASIL-BACA]`
Given `is_jitsi_param` belum pernah di-set sama sekali (`get_param` default `False`)
When `_compute_jitsi_link` jalan
Then event jatuh ke `_set_discuss_videocall_location()` bawaan Odoo (link Discuss standar, bukan Jitsi)

**AC-01-03** — ref `BR-08` `[PERLU-KEPUTUSAN]`
Given admin PERNAH mencentang "Enable Jitsi Integration" lalu meng-UNCHECK-nya kembali
When `_compute_jitsi_link` jalan sesudahnya
Then **perlu dikonfirmasi via Step 04**: apakah `get_param('is_jitsi_param')` mengembalikan string
`"False"` (truthy di Python → integrasi Jitsi TETAP dianggap aktif, BUG) atau Odoo menghapus key
config_parameter-nya sepenuhnya saat unchecked (`get_param` balik ke default `False` bool →
perilaku benar). Lihat `FINDINGS.md` F-01.

---

## AC-02 — Generate `access_token`/link saat create event (BR-02, BR-03)

**AC-02-01** — ref `BR-02` `[HASIL-BACA]`
Given payload `create()` berupa SATU dict dengan `is_jitsi=True`
When `calendar.event.create(values)` dipanggil
Then `access_token` di-set UUID baru sebelum `super().create()`, lalu `_compute_jitsi_link`
(depends `access_token`) menghasilkan `jitsi_link` sesuai BR-01

**AC-02-02** — ref `BR-02` `[HASIL-BACA]`
Given payload `create()` berupa satu dict dengan `is_jitsi=False` (key ada, nilai falsy)
When `create()` dipanggil
Then `access_token` di-set eksplisit `False` sebelum `super().create()` — menimpa `access_token`
apapun yang sudah ada di `values` yang sama

**AC-02-03** — ref `BR-03` `[PERLU-KEPUTUSAN]`
Given `calendar.event.create()` dipanggil dengan LIST berisi >1 dict (mis. lewat pembuatan event
berulang/`calendar.recurrence`, atau caller lain yang create batch)
When override `create()` modul ini menjalankan `'is_jitsi' in values`
Then pengecekan itu mengecek keanggotaan string `'is_jitsi'` pada LIST of dict (bukan pada tiap
dict), hasilnya hampir selalu `False` — logic BR-02 tidak jalan untuk skenario batch ini, perlu
dikonfirmasi lewat test nyata di Step 04 (buat event recurring dengan `is_jitsi=True` dan cek
apakah `access_token`/`jitsi_link` tetap terisi lewat jalur lain atau kosong). Lihat `FINDINGS.md` F-03.

---

## AC-03 — Interaksi `videocall_location` dengan compute core (BR-04)

**AC-03-01** — ref `BR-04` `[PERLU-KEPUTUSAN]`
Given event dengan `is_jitsi_param` aktif, `videocall_location` sudah ditulis oleh
`_compute_jitsi_link` ke URL Jitsi
When sesuatu di core `calendar` memicu ulang compute RESMI `videocall_location` (mis. dependency
compute core itu berubah, seperti `videocall_source`)
Then **perlu dikonfirmasi via Step 04** apakah nilai Jitsi tertimpa balik oleh compute core, atau
Odoo ORM memang menghormati nilai terakhir yang di-assign dan tidak memaksa recompute ulang tanpa
dependency compute-nya sendiri berubah. Lihat `FINDINGS.md` F-04.

---

## AC-04 — Recompute saat toggle `is_jitsi` pada event existing (BR-05)

**AC-04-01** — ref `BR-05` `[PERLU-KEPUTUSAN]`
Given event `calendar.event` sudah ada dengan `is_jitsi=False` (link Discuss aktif di
`videocall_location`)
When user meng-update `is_jitsi=True` lewat `write()` (bukan `create()`) TANPA mengubah field lain
Then `jitsi_link`/`videocall_location` TIDAK ikut ter-recompute (dependency compute cuma
`access_token`) — `action_join_video_call()` akan mengembalikan `self.jitsi_link` (kemungkinan
kosong/link Discuss lama) padahal `is_jitsi` sudah `True`. Perlu dikonfirmasi lewat test nyata.

---

## AC-05 — Nilai Company URL bersifat global (BR-06)

**AC-05-01** — ref `BR-06` `[PERLU-KEPUTUSAN]`
Given dua `calendar.event` milik dua company berbeda (multi-company aktif), `is_jitsi_param`
aktif, `company_param` disetel ke salah satu company
When `_compute_jitsi_link` jalan untuk KEDUA event
Then KEDUA event menghasilkan `jitsi_link` dengan segmen `company_name` yang SAMA (dari
`company_param` global), bukan mengikuti company masing-masing event — perlu dikonfirmasi apakah
ini disengaja (single-tenant Jitsi room per Doodex) atau gap multi-company. Lihat `FINDINGS.md` F-05.

---

## AC-06 — Format URL Jitsi (BR-07)

**AC-06-01** — ref `BR-07` `[HASIL-BACA]`
Given `company_param` menunjuk company bernama mengandung spasi (mis. "PT. Doodex Indonesia")
When `jitsi_link` dibentuk
Then string company disisipkan APA ADANYA (tidak di-slug/encode) ke dua segmen path
(`/{company}/{company}-{token}`) — berpotensi menghasilkan URL dengan spasi mentah yang tidak
valid di sebagian client/browser. Lihat `FINDINGS.md` F-07.

---

## AC-07 — Controller Jitsi custom tidak aktif (Yang Tidak Termasuk)

**AC-07-01** — ref (Scope §"Yang Tidak Termasuk") `[HASIL-BACA]`
Given `controllers/appointment.py` seluruh isinya di-comment-out, `controllers/__init__.py` tetap
`from . import appointment`
When modul di-install/upgrade
Then TIDAK ADA route HTTP tambahan yang terdaftar dari modul ini — link "Join" yang dipakai di
email (`/calendar/meeting/join?token=...`) adalah route BAWAAN `appointment`/`calendar`, bukan
dari controller modul ini. Lihat `FINDINGS.md` F-06.

---

## AC-09 — Override mail template tidak pernah aktif (BR-09, F-13, PALING KRITIS)

**AC-09-01** — ref `BR-09` `[DIKONFIRMASI]`
Given `is_jitsi_param` aktif, `jitsi_link` event terisi penuh, event punya minimal satu attendee
When `appointment.appointment_booked_mail_template` di-render (`_render_field('body_html', ...)`) untuk event itu
Then body HTML hasil render TIDAK mengandung `jitsi_link` sama sekali — identik dengan template
ASLI Odoo core (`appointment/data/mail_template_data.xml`), hanya berisi link "Join" standar
(`/calendar/meeting/join?token={access_token}`). **DIKONFIRMASI via test nyata** —
`data/mail_template_data.xml` tidak pernah ter-load karena tidak terdaftar di `__manifest__.py`.
Lihat `FINDINGS.md` F-13 (prioritas TERTINGGI di seluruh backfill ini).

---

## AC-08 — Tombol manual generate/clear link tidak terhubung ke UI

**AC-08-01** — ref (Scope §"Yang Termasuk", `generate_jitsi_link`/`clear_jitsi_link`) `[PERLU-KEPUTUSAN]`
Given method `generate_jitsi_link()` dan `clear_jitsi_link()` didefinisikan di model
When mencari referensi keduanya di `views/calendar_views.xml` (satu-satunya file view di modul ini)
Then TIDAK ditemukan button/menu/server action yang memanggil kedua method ini — perlu konfirmasi
pemilik modul apakah ini dipanggil dari luar modul (mis. automation/server action di database
produksi yang tidak ikut ter-backfill) atau memang dead code. Lihat `FINDINGS.md` F-08.
