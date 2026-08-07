# Functional Spec — appointment_jitsi

**Module:** `appointment_jitsi`
**Odoo Version:** 17.0
**Depends:** `base`, `appointment`, `calendar`
**Last Updated:** 2026-08-07
**Status:** Backfill retroaktif — dibaca dari kode existing, bukan requirement baru
**Provenance:** lihat `doc-dev-backfill/templates/CLAUDE_TEMPLATE.md` §Provenance Tag untuk arti `[HASIL-BACA]`/`[DIKONFIRMASI]`/`[PERLU-KEPUTUSAN]`

---

## Ringkasan untuk Review — Perlu Konfirmasi User

> Maks. 5-8 poin — cuma yang genuinely ambigu/berisiko/butuh keputusan pemilik modul. Semua poin
> ini juga ada di `FINDINGS.md`.

1. **`is_jitsi_param` dibaca sebagai string mentah dari `ir.config_parameter`, bukan di-cast ke bool** — `if is_jitsi_enabled:` di `_compute_jitsi_link` bisa TRUE bahkan saat setting eksplisit di-uncheck (string `"False"` non-kosong tetap truthy di Python). Lihat F-01.
2. **Toggle `is_jitsi` pada event existing via `write()` TIDAK memicu recompute `jitsi_link`/`videocall_location`** — `@api.depends('access_token')` tidak menyertakan `is_jitsi`, dan `write()` tidak di-override. Lihat F-02.
3. **`create()` di-override dengan signature single-record (`@api.model`, bukan `@api.model_create_multi`)** — pada create batch (mis. recurring event), `values` adalah list, sehingga `'is_jitsi' in values` hampir selalu `False` dan `access_token` tidak ikut di-generate untuk skenario batch. Lihat F-03.
4. **`videocall_location` ditulis langsung dari `_compute_jitsi_link`, padahal field itu punya compute method sendiri di `calendar` core (`_compute_videocall_location`)** — berpotensi tertimpa balik kalau compute core itu ter-trigger ulang oleh field dependency-nya sendiri. Lihat F-04.
5. **`company_param` (Company dipakai di URL Jitsi) adalah SATU nilai global (`ir.config_parameter`), bukan per-company** — di setup multi-company, semua event dari company manapun memakai nama company yang sama di link Jitsi. Lihat F-05.
6. **`controllers/appointment.py` seluruhnya di-comment-out** — tidak ada route HTTP aktif dari modul ini; fitur "buka halaman Jitsi custom" yang tersirat dari nama file tidak pernah berjalan. Lihat F-06.
7. **URL Jitsi dibentuk dari `company_name` mentah (tanpa slug/escape) dan menduplikasi nama company di path** (`{base}/{company}/{company}-{token}`) — berisiko rusak untuk nama company berspasi/karakter khusus. Lihat F-07.

---

## Latar Belakang & Tujuan

Modul menambahkan integrasi Jitsi Meet ke `calendar.event` (dipakai juga oleh alur Appointment
Odoo): setiap event bisa mendapat link Jitsi unik (berbasis `access_token` UUID), disimpan di
field baru `jitsi_link`, dan link itu disisipkan ke template email konfirmasi
appointment/undangan meeting supaya peserta bisa langsung join lewat Jitsi alih-alih Odoo Discuss
bawaan. `[HASIL-BACA]`

---

## Scope

### Yang Termasuk (disimpulkan dari kode)

- Field baru `calendar.event.jitsi_link` (computed, stored) dan `calendar.event.is_jitsi`
  (boolean, default `False`). `[HASIL-BACA]`
- Setting global "Enable Jitsi Integration" (`is_jitsi`, config_parameter `is_jitsi_param`) +
  "Company" (`company_param`, config_parameter `company_param`) di **Settings → Calendar**
  (`res.config.settings`, ditambahkan lewat inherit view `calendar.res_config_settings_view_form`). `[HASIL-BACA]`
- Generate ulang `access_token` UUID setiap kali event dibuat dengan `is_jitsi=True` (via override
  `create()`), atau setiap kali `generate_jitsi_link()`/`_compute_jitsi_link()` dipanggil ulang. `[HASIL-BACA]`
- Override konten dua mail template BAWAAN Odoo (bukan template baru):
  `calendar.calendar_template_meeting_update` dan `appointment.appointment_booked_mail_template`
  — menambah blok "How to Join" yang menampilkan `jitsi_link` (fallback ke `videocall_location`
  standar Odoo kalau `jitsi_link` kosong). `[HASIL-BACA]`
- Method `action_join_video_call()` mengembalikan action `ir.actions.act_url` ke
  `jitsi_link`/`videocall_location` tergantung `is_jitsi`. `[HASIL-BACA]`
- Method `generate_jitsi_link()` dan `clear_jitsi_link()` tersedia di model, TAPI tidak dipanggil
  dari view/button manapun yang ditemukan di `views/calendar_views.xml` — kemungkinan dipanggil
  lewat server action/automation eksternal yang tidak termasuk dalam modul ini, atau sisa kode
  yang belum/sudah tidak dihubungkan ke UI. `[PERLU-KEPUTUSAN]` (lihat F-08)

### Yang Tidak Termasuk

- `controllers/appointment.py` (route custom `/calendar/join_jitsi/<token>` yang me-render halaman
  Jitsi embed sendiri via `external_api.js`) — kode ADA di file tapi 100% di-comment-out, jadi
  SECARA FUNGSIONAL tidak termasuk scope yang berjalan saat ini, walau jejak kodenya masih ada di
  repo. `[HASIL-BACA]` (lihat F-06)
- Tidak ada model baru — modul murni `_inherit` ke `calendar.event`/`res.config.settings`, karena
  itu `security/ir.model.access.csv` cuma berisi header tanpa baris akses (tidak butuh access
  rule baru). `[HASIL-BACA]`
- Tidak ada dukungan eksplisit multi-company untuk nilai "Company" yang dipakai di URL Jitsi —
  hanya satu nilai global. `[PERLU-KEPUTUSAN]` (lihat F-05)

---

## User Stories (rekonstruksi)

> Ditulis dari sudut pandang kode, bukan wawancara user asli.

### US-01 — Admin mengaktifkan integrasi Jitsi
Sebagai admin, saya membuka **Settings → Calendar → Jitsi Configuration**, mencentang "Enable
Jitsi Integration", memilih "Company" yang namanya dipakai di URL room Jitsi, supaya event baru
otomatis dapat link Jitsi. `[HASIL-BACA]`

### US-02 — User membuat/mengedit calendar event dengan Jitsi aktif
Sebagai user yang membuat `calendar.event` dengan `is_jitsi=True`, saya mengharapkan
`jitsi_link`/`videocall_location` otomatis terisi begitu event dibuat, dan bisa langsung "Join"
dari tombol standar Odoo (`action_join_video_call`) atau dari link di email konfirmasi. `[HASIL-BACA]`

### US-03 — Peserta appointment menerima email konfirmasi
Sebagai peserta yang membuat janji lewat Appointment, saya menerima email
(`appointment_booked_mail_template`) yang menampilkan link Jitsi (bukan link Discuss default)
kalau `jitsi_link` terisi. `[HASIL-BACA]`

---

## Business Rules

> **Cek wajib tiap BR yang berasal dari method pada model `_inherit`:** apakah nama method ini
> bentrok dengan method Odoo core yang sudah ada di model yang sama? Hasil cek untuk modul ini:
> `create()` pada `calendar.event` DIPANGGIL via `super().create(values)` (bukan reimplementasi
> total) — jadi bukan kelas bug "method tertimpa total" seperti lesson `onchange_partner_id`.
> `_compute_jitsi_link`, `generate_jitsi_link`, `clear_jitsi_link`, `action_join_video_call` adalah
> nama BARU, tidak bentrok nama dengan Odoo core. TAPI ditemukan kelas bug SEJENIS pada level
> **field compute** (bukan nama method) — lihat BR-04/F-04: `videocall_location` punya compute
> resmi sendiri di core `calendar`, dan modul ini menulis field itu dari compute LAIN
> (`_compute_jitsi_link`) tanpa mendeklarasikan ulang field-nya.

### BR-01 — Link Jitsi hanya dibentuk kalau integrasi diaktifkan secara global
Kalau `ir.config_parameter('is_jitsi_param')` "truthy" (lihat F-01 soal string vs bool), setiap
event di-loop untuk diberi `access_token` (kalau belum ada) lalu `jitsi_link` dan
`videocall_location` diisi format `https://meet.jit.si/{company}/{company}-{access_token}`. Kalau
tidak, event jatuh ke `_set_discuss_videocall_location()` bawaan Odoo (link Discuss standar). `[HASIL-BACA]`
**Lokasi kode:** `models/calendar_event.py:37-59`

### BR-02 — `access_token` di-generate ulang saat create kalau `is_jitsi` diberikan
Saat `calendar.event.create(values)` dipanggil dan key `is_jitsi` ada di `values`: kalau nilainya
truthy, `access_token` di-set UUID baru; kalau nilainya falsy, `access_token` di-set `False`
(override eksplisit, bahkan kalau caller lain sudah menyertakan `access_token` di `values` yang
sama — `values['access_token']` ditimpa). `[HASIL-BACA]`
**Lokasi kode:** `models/calendar_event.py:71-78`

### BR-03 — `create()` tidak batch-safe untuk pola pengecekan `is_jitsi`
Signature `@api.model create(self, values)` (bukan `@api.model_create_multi`) mengasumsikan
`values` selalu satu dict. Kalau Odoo memanggil `create()` dengan LIST of dict (batch — terjadi
pada event berulang/`calendar.recurrence`, atau caller lain yang sengaja create banyak sekaligus),
`'is_jitsi' in values` mengecek keanggotaan STRING di dalam LIST (bukan di dalam dict), yang
hampir selalu `False` — jadi logic BR-02 SENYAP tidak berjalan untuk create batch, `access_token`
tidak di-generate lewat jalur ini (baru muncul belakangan lewat compute `_compute_jitsi_link` kalau
`is_jitsi_param` global aktif, TAPI compute itu sendiri baru jalan kalau `access_token` sudah
punya nilai — lihat BR-01 dependency `access_token`). `[PERLU-KEPUTUSAN]`
**Lokasi kode:** `models/calendar_event.py:71-78`

### BR-04 — `videocall_location` ditulis dari compute lain, bukan compute resminya sendiri
`_compute_jitsi_link` (`@api.depends('access_token')`) menulis LANGSUNG ke
`rec.videocall_location` (baik jalur Jitsi aktif maupun fallback `_set_discuss_videocall_location()`),
padahal `videocall_location` di `calendar.event` core Odoo punya field compute RESMI sendiri
(biasanya `_compute_videocall_location`, dependency berbeda — mis. `videocall_source`). Field
tidak di-redeclare (tidak ada `videocall_location = fields.Char(compute=...)` baru di modul ini),
jadi assignment ini murni Python-level side-write di luar compute resminya. Risiko: kalau
dependency compute RESMI core berubah nilainya belakangan (event di-update lewat jalur lain yang
memicu compute asli), nilai Jitsi yang sudah ditulis modul ini bisa TERTIMPA BALIK tanpa error
yang terlihat — sama kelasnya dengan lesson "method collision" di `PLAYBOOK.md`, hanya levelnya
field-compute, bukan nama method. `[PERLU-KEPUTUSAN]`
**Lokasi kode:** `models/calendar_event.py:37-59`

### BR-05 — Recompute `jitsi_link` tidak ter-trigger oleh perubahan `is_jitsi`
`@api.depends('access_token')` TIDAK menyertakan `is_jitsi` sebagai dependency. Toggle `is_jitsi`
pada event yang SUDAH ADA (lewat `write()`, tidak di-override modul ini) tidak memicu recompute
`_compute_jitsi_link` sama sekali (`access_token` tidak berubah). Efek: event yang awalnya dibuat
`is_jitsi=False` (link Discuss), lalu diubah jadi `is_jitsi=True` lewat form, `jitsi_link`/
`videocall_location` TETAP berisi link Discuss lama sampai ada trigger lain yang mengubah
`access_token` (mis. `generate_jitsi_link()` dipanggil manual — tapi lihat F-08, tidak ada
tombol UI untuk itu). `[PERLU-KEPUTUSAN]`
**Lokasi kode:** `models/calendar_event.py:20-23, 37-59`

### BR-06 — Nilai "Company" untuk URL Jitsi bersifat global, bukan per-event/per-company
`company_param` disimpan sebagai SATU `ir.config_parameter` (bukan field per-company atau
per-event) — `_compute_jitsi_link` selalu memakai nilai config global ini untuk SEMUA event,
terlepas `event.partner_id`/company milik event yang sebenarnya. Di setup multi-company, seluruh
room Jitsi lintas company memakai nama company yang sama. `[PERLU-KEPUTUSAN]`
**Lokasi kode:** `models/calendar_event.py:44-45`, `models/calendar_event.py:90-95`

### BR-07 — Format URL Jitsi menduplikasi nama company di path
`f"{jitsi_base_url}/{company_name}/{company_name}-{rec.access_token}"` menghasilkan URL seperti
`https://meet.jit.si/Doodex/Doodex-abc123...` — segmen path pertama (`/{company_name}/`) tampak
tidak perlu (room Jitsi hanya ditentukan oleh path setelah domain; Jitsi tidak punya konsep
sub-folder), dan `company_name` tidak di-escape/slug — spasi/karakter khusus pada nama company
akan masuk mentah ke URL. `[PERLU-KEPUTUSAN]`
**Lokasi kode:** `models/calendar_event.py:49-56`

### BR-08 — `is_jitsi_param` dibaca sebagai truthy string, bukan boolean
`get_param('is_jitsi_param')` mengembalikan `False` (Python bool) HANYA kalau key benar-benar
tidak ada; begitu pernah di-set, Odoo menyimpan nilai `fields.Boolean(config_parameter=...)`
sebagai STRING (`"True"`/`"False"`) di `ir.config_parameter`. `if is_jitsi_enabled:` mengevaluasi
string non-kosong APAPUN (termasuk `"False"`) sebagai truthy — berpotensi integrasi Jitsi TETAP
aktif meski admin sudah uncheck settingnya (butuh konfirmasi Step 04 untuk pastikan bagaimana
persisnya Odoo core menyimpan boolean config_parameter yang di-uncheck — dihapus dari
`ir.config_parameter` sepenuhnya vs disimpan sebagai string `"False"`). `[PERLU-KEPUTUSAN]`
**Lokasi kode:** `models/calendar_event.py:42-43, 48`
