# Findings — appointment_jitsi

> Satu file konsolidasi — pemilik modul cukup baca file ini untuk tahu semua hal yang butuh
> keputusan manusia, tanpa perlu baca ulang seluruh `doc-dev/backfill/`. Diisi terus sepanjang
> proses, bukan bagian dari template SOP normal — ini spesifik BACKFILL.
>
> **Prinsip:** begitu ditemukan spot ambigu/bug, catat di sini dan LANJUT — jangan berhenti
> menunggu resolusi satu per satu.
>
> **Dokumen hidup, bukan laporan sekali-jadi:** pemilik modul boleh memperbaiki kode bisnis
> SENDIRI (di luar BACKFILL) kapan saja berdasarkan finding di sini. Update entry terkait jadi
> `✅ RESOLVED`/`✅ CONFIRMED` + tanggal + bukti test (bukan dihapus).

---

## Ringkasan

> **Semua item di bawah sudah diverifikasi via eksekusi nyata di Step 04** (Odoo 17 Enterprise +
> Postgres 15 via Docker, `docker-env/`, 12 test `TransactionCase` — lihat
> `test/04A_DEV_TESTING.md`) — bukan lagi dugaan baca-kode semata. Beberapa hipotesis awal Step 01
> TERBANTAHKAN oleh eksekusi nyata (F-01), dan satu hipotesis TERBUKTI lebih serius dari perkiraan
> awal dengan mekanisme yang jauh lebih presisi (F-04).

| ID | Judul | Tag | Prioritas | Status |
|---|---|---|---|---|
| F-01 | ~~`is_jitsi_param` dibaca sebagai string truthy~~ — TERBANTAHKAN, `get_param` balik bool `False` asli | `[DIKONFIRMASI]` | — | ✅ RESOLVED (bukan bug) |
| F-02 | `is_jitsi` toggle via `write()` tidak memicu recompute link | `[DIKONFIRMASI]` | Tinggi | ✅ CONFIRMED via test |
| F-03 | `create()` tidak batch-safe (`@api.model` bukan `@api.model_create_multi`) | `[DIKONFIRMASI]` | Sedang | ✅ CONFIRMED, dampak direvisi (lebih ringan dari perkiraan awal) |
| F-04 | `videocall_location`/`jitsi_link` hasilnya BERGANTUNG urutan field mana yang dibaca lebih dulu | `[DIKONFIRMASI]` | **Tinggi** | ✅ CONFIRMED via test A/B, mekanisme presisi ditemukan |
| F-05 | `company_param` global, tidak per-company (multi-company) | `[DIKONFIRMASI]` | Sedang | ✅ CONFIRMED via test |
| F-06 | `controllers/appointment.py` 100% dead code (di-comment-out) | `[HASIL-BACA]` | Rendah | ✅ CONFIRMED via test |
| F-07 | URL Jitsi memakai nama company mentah + duplikasi segmen path | `[DIKONFIRMASI]` | Sedang | ✅ CONFIRMED via test |
| F-08 | `generate_jitsi_link()`/`clear_jitsi_link()` tidak terhubung ke UI manapun | `[PERLU-KEPUTUSAN]` | Rendah | Method tetap berfungsi normal saat dipanggil langsung (test pass) |
| F-09 | File `googleaeed8a7b9ec156e7.html` ikut ter-commit di root modul | `[PERLU-KEPUTUSAN]` | Rendah | — |
| F-10 | **Baru** — Label field "Company" bentrok antara `company_param` (modul ini) dan `company_id` (`base_setup`) di `res.config.settings` | `[HASIL-BACA]` | Rendah | Ditemukan dari WARNING Odoo sendiri saat instalasi |
| F-11 | **Baru** — Field per-event `is_jitsi` TIDAK dipakai sama sekali di `_compute_jitsi_link` — hanya `is_jitsi_param` GLOBAL yang menentukan Jitsi/Discuss untuk SEMUA event | `[PERLU-KEPUTUSAN]` | **Tinggi** | Ditemukan saat AC-01-01 (event dibuat TANPA `is_jitsi=True` tetap dapat link Jitsi) |
| F-12 | Modul butuh addon Enterprise (`appointment` + `web_gantt`, `license: OEEL-1`) — tidak bisa di-test dengan image `odoo:17.0` Community publik | `[HASIL-BACA]` | — | Limitasi environment, lihat "Limitasi Tool" |
| F-13 | **PALING KRITIS** — `data/mail_template_data.xml` TIDAK terdaftar di `__manifest__.py` `data` — fitur UTAMA modul ("email confirmation menampilkan link Jitsi") TIDAK PERNAH AKTIF SAMA SEKALI | `[PERLU-KEPUTUSAN]` | **TERTINGGI** | ✅ CONFIRMED via test nyata (Step 07) |

---

## Detail

### F-01 — ~~`is_jitsi_param` dibaca sebagai string truthy~~ — TERBANTAHKAN oleh eksekusi nyata
**Tag:** `[DIKONFIRMASI]`
**Lokasi:** `models/calendar_event.py:42-48`
**Ref:** BR-08, AC-01-03
**Deskripsi (hipotesis awal Step 01):** `get_param('is_jitsi_param')` dipakai langsung di
`if is_jitsi_enabled:` tanpa dikonversi eksplisit ke bool — dikhawatirkan `ir.config_parameter`
menyimpan literal string `"False"` (truthy di Python) setelah admin uncheck setting.
**Hasil verifikasi nyata (Step 04, test `test_ac_01_03_uncheck_setting_still_truthy`):**
mengaktifkan lewat `res.config.settings` lalu uncheck via `.execute()` menghasilkan Odoo BENAR-BENAR
MENGHAPUS row `ir.config_parameter` terkait (log: `"User #1 deleted ir.config_parameter records
with IDs: [16]"`), sehingga `get_param('is_jitsi_param')` sesudahnya mengembalikan `False` (Python
bool asli, dikonfirmasi `type(raw_value).__name__ == 'bool'`), BUKAN string `"False"`. Event yang
dibuat sesudahnya jatuh ke fallback Discuss (`videocall_location=False` di test-environment ini,
lihat F-04 untuk alasan `False` bukan link Discuss). **F-01 BUKAN bug** — cara Odoo core
menangani `fields.Boolean(config_parameter=...)` saat uncheck (hapus row, bukan simpan
string "False") membuat kekhawatiran awal tidak relevan.
**Dampak:** Tidak ada.
**Rekomendasi:** Tidak perlu perubahan kode. Tetap boleh ditambahkan cast eksplisit
(`bool(get_param(...))`) sebagai defensive coding kalau pemilik modul mau, tapi bukan urgent fix.
**Keputusan pemilik modul:** ✅ RESOLVED (bukan bug) — 2026-08-07, berdasar eksekusi test nyata di
Step 04, tidak perlu keputusan lebih lanjut.

---

### F-02 — `is_jitsi` toggle via `write()` tidak memicu recompute link
**Tag:** `[DIKONFIRMASI]`
**Lokasi:** `models/calendar_event.py:20-23, 37`
**Ref:** BR-05, AC-04-01
**Deskripsi:** `_compute_jitsi_link` hanya `@api.depends('access_token')`, tidak menyertakan
`is_jitsi`. Toggle `is_jitsi` True/False pada event yang sudah ada (lewat form/`write()`, tidak
di-override modul ini) tidak mengubah `access_token`, sehingga tidak memicu recompute sama sekali.
**Hasil verifikasi nyata (Step 04, test `test_ac_04_01_write_toggle_no_recompute`):** event dibuat
`is_jitsi=False` (`videocall_location` awal = `False`), lalu setting Jitsi diaktifkan DAN
`event.write({'is_jitsi': True})` dipanggil — `videocall_location` SETELAH write TETAP `False`
(tidak berubah sama sekali). **Bug dikonfirmasi 100% nyata** (`bug_confirmed=True` di log).
**Catatan penting (lihat F-11):** dampak sebenarnya BUKAN soal `is_jitsi` per-event (field itu
TIDAK dipakai `_compute_jitsi_link` sama sekali, lihat F-11) — dampak nyatanya adalah:
apapun pemicu recompute `jitsi_link` (hanya `access_token`), event yang sudah pernah computed
TIDAK PERNAH otomatis ter-refresh kalau setting GLOBAL `is_jitsi_param` diaktifkan/dimatikan
BELAKANGAN — event lama tetap membawa link versi lama sampai `access_token`-nya berubah lagi
(mis. lewat `generate_jitsi_link()` manual, lihat F-08).
**Dampak:** Event lama tidak otomatis "ikut" perubahan setting global Jitsi — perlu trigger
manual (`generate_jitsi_link()`) supaya link ter-refresh sesuai status setting saat ini.
**Rekomendasi:** Kalau perilaku "auto-refresh saat setting diubah" diinginkan, perlu compute ulang
massal (`_compute_jitsi_link()` dipanggil untuk semua event) tiap kali `is_jitsi_param`/`company_param`
berubah (mis. lewat override `set_values()` di `res.config.settings`).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-03 — `create()` tidak batch-safe (`@api.model` bukan `@api.model_create_multi`)
**Tag:** `[DIKONFIRMASI]`
**Lokasi:** `models/calendar_event.py:71-78`
**Ref:** BR-03, AC-02-03
**Deskripsi:** Override `create(self, values)` pakai `@api.model` (single-record semantics) sesuai
konvensi Odoo < 13, padahal Odoo 17 memanggil `create()` dengan LIST of dict untuk skenario batch
(termasuk event berulang lewat `calendar.recurrence`). `'is_jitsi' in values` pada input list
mengecek keanggotaan string di list, bukan di tiap dict — hampir selalu `False`.
**Hasil verifikasi nyata (Step 04):** dikonfirmasi LANGSUNG oleh Odoo sendiri saat modul di-install
— WARNING resmi ORM: `"The model odoo.addons.appointment_jitsi.models.calendar_event is not
overriding the create method in batch"`. Test `test_ac_02_03_create_batch_list_is_jitsi_check_fails`
memanggil `create([{...is_jitsi:True}, {...is_jitsi:True}])` — `access_token` KEDUA event TETAP
terisi (`bug_confirmed=False` untuk skenario ini), karena `access_token` adalah field CORE
`calendar.event` yang sudah punya default value generator sendiri (independen dari override
modul ini) — override `create()` modul ini hanya PUNYA EFEK EKSTRA untuk single-record create:
(a) memastikan `access_token` FRESH (uuid baru, bukan default core) saat `is_jitsi=True`, dan
(b) me-RESET `access_token` jadi `False` secara eksplisit saat `is_jitsi=False`. Untuk create
batch, KEDUA efek ekstra itu (terutama efek (b), reset ke `False`) TIDAK PERNAH terjadi — event
batch dengan `is_jitsi=False` eksplisit akan TETAP membawa `access_token` default dari core
(bukan `False`), berbeda dari perilaku single-create.
**Dampak:** Direvisi jadi **Sedang** (bukan Tinggi seperti perkiraan awal) — karena `access_token`
tetap terisi lewat default core, modul tidak benar-benar "gagal total" untuk skenario batch (mis.
recurring events). Sisa dampak: efek RESET `access_token` ke `False` saat `is_jitsi=False` eksplisit
tidak konsisten antara single-create vs batch-create — perilaku niche, kemungkinan jarang terpicu
di penggunaan normal (recurring event biasanya tidak mengirim `is_jitsi=False` eksplisit per-item).
**Rekomendasi:** Ganti ke `@api.model_create_multi def create(self, vals_list)`, loop tiap dict —
akan menghilangkan WARNING resmi Odoo dan menyamakan perilaku single vs batch.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-04 — `jitsi_link`/`videocall_location` hasilnya bergantung urutan field mana yang dibaca lebih dulu
**Tag:** `[DIKONFIRMASI]`
**Lokasi:** `models/calendar_event.py:37-59`
**Ref:** BR-04, AC-03-01
**Deskripsi (hipotesis awal Step 01):** `videocall_location` adalah field `calendar.event` core
Odoo dengan compute resminya sendiri (`_compute_videocall_location`, dikonfirmasi via introspeksi
`field.compute` di Step 04). Modul ini menulis field itu secara imperatif dari `_compute_jitsi_link`
(method BEDA, depends BEDA — cuma `access_token`) tanpa mendeklarasikan ulang `compute=` field
tersebut.
**Hasil verifikasi nyata (Step 04, test `test_ac_03_01_videocall_location_race_with_core_compute`,
skenario A/B dengan setup config IDENTIK):**
- **Skenario A** — baca `event.jitsi_link` DULU (memicu `_compute_jitsi_link`, yang MENULIS
  `videocall_location` sebagai side-effect di dalam method itu) → `jitsi_link` DAN
  `videocall_location` KEDUANYA berisi URL Jitsi yang benar.
- **Skenario B** — baca `event.videocall_location` DULU, TANPA PERNAH menyentuh `jitsi_link` sama
  sekali → yang jalan adalah compute RESMI core (`_compute_videocall_location`), BUKAN
  `_compute_jitsi_link` — `videocall_location` = `False` (compute resmi core butuh kondisi lain,
  kemungkinan jumlah attendee, yang tidak terpenuhi di test ini), dan `jitsi_link` TIDAK PERNAH
  ter-compute sama sekali karena tidak pernah diakses.
- **Verdict test:** `bug_confirmed=True` — dua event dengan setup IDENTIK menghasilkan
  `videocall_location` yang BERBEDA TOTAL (`https://meet.jit.si/...` vs `False`) murni karena
  urutan akses field.
**Mekanisme presisi (lebih spesifik dari hipotesis awal):** karena `videocall_location` TIDAK
terdaftar sebagai output resmi `_compute_jitsi_link` (hanya `jitsi_link` yang terdaftar), Odoo
HANYA memicu `_compute_jitsi_link` kalau `jitsi_link` itu sendiri yang diakses/dibutuhkan. Kalau
KODE LAIN (view, method lain, automation) membaca `videocall_location` TANPA pernah membaca
`jitsi_link` duluan, override Jitsi TIDAK PERNAH JALAN SAMA SEKALI untuk record itu — bukan soal
"tertimpa balik" seperti hipotesis awal, tapi soal "tidak pernah tertulis dari awal".
**Dampak (Tinggi, dikonfirmasi):** Satu-satunya jalur yang memastikan `jitsi_link` ter-compute
duluan adalah lewat mail template (`t-if="object.jitsi_link"` membaca `jitsi_link` duluan — AMAN)
dan `action_join_video_call()` saat `is_jitsi=True` (membaca `self.jitsi_link` duluan lewat
short-circuit ternary — AMAN). TAPI kode Odoo CORE manapun (calendar view "Join" button, list
view, kanban, API/RPC eksternal) yang membaca `videocall_location` LEBIH DULU — sebelum
`jitsi_link` pernah diakses sama sekali untuk record itu — akan mendapat hasil compute RESMI core,
BUKAN link Jitsi, walau setting Jitsi aktif. Karena `jitsi_link` sendiri TIDAK ditampilkan di
view manapun (tidak ada di `calendar_views.xml`), risiko "videocall_location dibaca duluan" oleh
komponen UI Odoo standar (yang lebih sering baca `videocall_location`, field core yang memang
ditampilkan) CUKUP TINGGI di penggunaan nyata.
**Rekomendasi:** Jangan menulis `videocall_location` dari method lain — deklarasikan ulang field
itu di modul ini dengan `compute='_compute_jitsi_link'` (atau tambahkan logic Jitsi ke DALAM
compute resmi core lewat extend, bukan side-write dari compute field lain).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-05 — `company_param` global, tidak per-company (multi-company)
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/calendar_event.py:44-45`, `models/calendar_event.py:90-95`
**Ref:** BR-06, AC-05-01
**Deskripsi:** Nilai "Company" yang dipakai membentuk URL Jitsi disimpan sebagai SATU
`ir.config_parameter` global (`company_param`), bukan per-company atau diturunkan dari
`event.company_id`/`event.partner_id`. Di setup multi-company, semua room Jitsi lintas company
memakai nama company yang sama (hasil config global), terlepas company asli event.
**Dampak:** Berpotensi membingungkan/tidak sesuai ekspektasi di deployment multi-company — room
Jitsi tidak mencerminkan company event yang sebenarnya.
**Rekomendasi:** Klarifikasi ke pemilik modul apakah target deployment memang single-company
(Doodex sendiri) sehingga ini non-issue, atau perlu diturunkan dari `event.company_id` untuk
kasus general.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-06 — `controllers/appointment.py` 100% dead code (di-comment-out)
**Tag:** `[HASIL-BACA]`
**Lokasi:** `controllers/appointment.py:1-51`
**Ref:** AC-07-01
**Deskripsi:** Seluruh isi file (route `/calendar/join_jitsi/<access_token>` yang me-render
halaman embed Jitsi custom lewat `external_api.js`) di-comment-out. `controllers/__init__.py`
tetap meng-`import` file ini (no-op karena isinya cuma komentar) — tidak menyebabkan error, tapi
tidak ada route HTTP tambahan yang benar-benar terdaftar dari modul ini.
**Dampak:** Tidak ada dampak fungsional saat ini (murni dead code), tapi berpotensi
membingungkan developer berikutnya yang mengira fitur ini aktif dari nama file/struktur folder.
**Rekomendasi:** Klarifikasi apakah fitur ini sengaja dinonaktifkan (mis. digantikan pendekatan
link langsung `meet.jit.si` yang lebih sederhana) atau sisa development yang belum dibersihkan.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-07 — URL Jitsi memakai nama company mentah + duplikasi segmen path
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/calendar_event.py:49-56`
**Ref:** BR-07, AC-06-01
**Deskripsi:** `f"{jitsi_base_url}/{company_name}/{company_name}-{access_token}"` — nama company
disisipkan dua kali (sekali sebagai "folder", sekali sebagai prefix room), dan tidak di-slug atau
di-escape URL. Nama company berspasi/karakter khusus (mis. "PT. Doodex Indonesia") akan masuk
mentah ke URL.
**Dampak:** Berisiko menghasilkan URL yang tidak valid/tidak konsisten di sebagian client, atau
room Jitsi yang berbeda dari yang diharapkan (Jitsi treat setiap path unik sebagai room berbeda —
karakter yang di-encode berbeda oleh client berbeda bisa menghasilkan room yang tidak match).
**Rekomendasi:** Slug-kan `company_name` (mis. `slugify`) dan pertimbangkan hilangkan duplikasi
segmen path kalau memang tidak disengaja.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-08 — `generate_jitsi_link()`/`clear_jitsi_link()` tidak terhubung ke UI manapun
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/calendar_event.py:25-35`
**Ref:** AC-08-01
**Deskripsi:** Kedua method didefinisikan di model tapi tidak direferensikan di
`views/calendar_views.xml` (satu-satunya file view modul ini) sebagai button/`server_action`, dan
tidak ada file view lain di modul ini yang meng-override form `calendar.event`.
**Dampak:** Tidak ada dampak error, tapi method ini kemungkinan dead code dari sudut pandang
modul ini sendiri (mungkin dipanggil dari luar modul — server action ad-hoc di database produksi
yang bukan bagian dari kode module — atau memang sisa pengembangan).
**Rekomendasi:** Klarifikasi ke pemilik modul; kalau memang dipanggil dari luar modul, catat di
mana supaya dokumentasi Step 01 lengkap.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-09 — File `googleaeed8a7b9ec156e7.html` ikut ter-commit di root modul
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `appointment_jitsi/googleaeed8a7b9ec156e7.html`
**Deskripsi:** File verifikasi Google Search Console (biasanya ditaruh di web root situs, bukan
di dalam source modul Odoo) ikut ter-commit ke repo module ini — tidak berhubungan dengan logic
Odoo apapun.
**Dampak:** Tidak ada dampak fungsional ke modul (Odoo tidak memuat file ini sebagai apapun), tapi
kemungkinan salah taruh saat development/deploy web terpisah.
**Rekomendasi:** Klarifikasi ke pemilik modul apakah file ini sengaja disertakan (mis. untuk
tujuan hosting statis lain) atau bisa dihapus dari repo modul. **BACKFILL tidak menghapus file
ini** (di luar scope — bukan kode bisnis, tapi tetap bukan wewenang BACKFILL mengubah/menghapus).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-10 — Label field "Company" bentrok antara `company_param` (modul ini) dan `company_id` (`base_setup`)
**Tag:** `[HASIL-BACA]`
**Lokasi:** `models/calendar_event.py:90-95` (field `company_param` di `res.config.settings`)
**Deskripsi:** Odoo sendiri mencetak WARNING saat instalasi: `"Two fields (company_param,
company_id) of res.config.settings() have the same label: Company. [Modules: appointment_jitsi
and base_setup]"`. Dua field berbeda di form Settings yang sama-sama berlabel "Company" bisa
membingungkan user (field `company_id` bawaan `base_setup` biasanya berarti company AKTIF user,
sedangkan `company_param` modul ini berarti "nama company yang dipakai di URL Jitsi" — dua makna
yang berbeda tapi label sama).
**Dampak:** Kosmetik/UX, tidak ada dampak fungsional.
**Rekomendasi:** Ganti label `company_param` jadi lebih spesifik, mis. "Jitsi Room Company Name".
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-11 — Field per-event `is_jitsi` TIDAK dipakai di `_compute_jitsi_link`
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/calendar_event.py:37-59`
**Deskripsi:** `_compute_jitsi_link` HANYA membaca `ir.config_parameter('is_jitsi_param')` GLOBAL
untuk menentukan apakah event dapat link Jitsi — TIDAK PERNAH mengecek `rec.is_jitsi` (field
per-event) sama sekali di dalam method itu. Dikonfirmasi nyata: test `test_ac_01_01_...` membuat
event TANPA menyertakan `is_jitsi=True` sama sekali (default `False`), dan event itu TETAP
mendapat `jitsi_link` penuh (karena setting global aktif). Field `is_jitsi` per-event HANYA dipakai
di dua tempat lain: (1) `create()` — untuk memutuskan generate/reset `access_token`, dan (2)
`action_join_video_call()` — untuk memilih `jitsi_link` vs `videocall_location` sebagai URL
return.
**Dampak:** Kalau intent modul ini adalah "Jitsi opt-in PER EVENT" (yang tersirat dari adanya
field `is_jitsi` di level `calendar.event`, bukan cuma di Settings), maka fitur itu TIDAK BERFUNGSI
— begitu setting global aktif, SEMUA event (terlepas `is_jitsi` true/false) dapat `jitsi_link`
terisi lewat compute. Field `is_jitsi` per-event efeknya jadi sangat terbatas/membingungkan
(cuma soal `access_token`/pilihan URL di `action_join_video_call`, bukan soal "aktif/tidak aktif").
**Rekomendasi:** Klarifikasi ke pemilik modul: apakah `is_jitsi` per-event memang dimaksudkan
sebagai kontrol tambahan (dan `_compute_jitsi_link` perlu ditambah kondisi `rec.is_jitsi`), atau
field ini sengaja general-only dan namanya/dokumentasinya yang perlu diperjelas.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-12 — Modul butuh addon Enterprise (`appointment` + `web_gantt`), tidak tersedia di image publik `odoo:17.0`
**Tag:** `[HASIL-BACA]`
**Lokasi:** `__manifest__.py` (`depends: appointment`), `README.md` ("Odoo version: 17.0 Enterprise Edition")
**Deskripsi:** Percobaan pertama Step 04 (Mode C, image resmi `odoo:17.0` dari Docker Hub) GAGAL
total dengan `"module appointment_jitsi: Unmet dependencies: appointment"` — modul `appointment`
(dan dependency-nya sendiri, `web_gantt`) berlisensi `OEEL-1` (Odoo Enterprise), tidak dibundel di
image Community publik. Diselesaikan dengan me-mount checkout Enterprise 17 yang sudah ada secara
lokal di mesin dev (`D:\Kuncoro\doodex\repo\enterprise17`, di luar Doodex, berlisensi Doodex
sebagai Odoo partner) sebagai extra addons path di `docker-env/docker-compose.yml`.
**Dampak:** Bukan bug modul — murni kebutuhan infrastruktur testing. **Developer/CI lain yang mau
menjalankan test modul ini WAJIB punya akses ke source Odoo 17 Enterprise** (lisensi Doodex atau
mount serupa), TIDAK BISA hanya pakai image `odoo:17.0` Community publik.
**Rekomendasi:** Dokumentasikan kebutuhan Enterprise ini secara eksplisit di README modul (README
sudah menyebutnya, tapi `__manifest__.py` tidak ada catatan apapun soal ini) — pertimbangkan
tambahkan catatan di `docker-env/README` (kalau ada) soal mount Enterprise addons untuk dev lain.
**Keputusan pemilik modul:** *(kosong — diisi manusia, sifatnya informasional)*

---

### F-13 — `data/mail_template_data.xml` tidak terdaftar di `__manifest__.py` — override email TIDAK PERNAH AKTIF
**Tag:** `[PERLU-KEPUTUSAN]`
**Prioritas:** **TERTINGGI** — ini membatalkan fitur utama modul yang diklaim di manifest/README.
**Lokasi:** `__manifest__.py:27-29` (key `"data"`)
**Ref:** US-03, Scope §"Yang Termasuk" (Email Notification)
**Deskripsi:** `__manifest__.py` hanya mendaftarkan:
```python
"data": [
    "views/calendar_views.xml",
],
```
File `data/mail_template_data.xml` — yang berisi SATU-SATUNYA logic modul ini untuk menyisipkan
`jitsi_link` ke email konfirmasi appointment/undangan meeting (override
`calendar.calendar_template_meeting_update` dan `appointment.appointment_booked_mail_template`) —
TIDAK ADA di daftar itu sama sekali. Odoo hanya me-load file yang eksplisit terdaftar di
`data`/`demo`/`assets` manifest; file yang ada di folder tapi tidak terdaftar TIDAK PERNAH dibaca,
TANPA warning atau error apapun (silent).
**Hasil verifikasi nyata (Step 07, test `test_qa_s01_mail_template_does_not_render_jitsi_link`):**
me-render `appointment.appointment_booked_mail_template` untuk event dengan `jitsi_link` terisi
penuh — body HTML hasil render SAMA PERSIS dengan template ASLI `appointment` core (dikonfirmasi
baris demi baris terhadap `enterprise17/appointment/data/mail_template_data.xml`), TIDAK
mengandung `jitsi_link` sama sekali, hanya link "Join" standar Odoo (`/calendar/meeting/join?token=`,
pakai `access_token`, BUKAN Jitsi). Dikonfirmasi juga di log instalasi: baris
`"loading appointment_jitsi/data/mail_template_data.xml"` **TIDAK PERNAH MUNCUL** di log Odoo
manapun sepanjang seluruh sesi Step 04/07 (dibandingkan modul lain yang datanya termuat, semua
mencetak baris "loading {module}/data/...").
**Dampak:** **Fitur inti modul yang diklaim di manifest summary/description DAN README** ("Email
Notification: Customizes the appointment confirmation email template to include the Jitsi meeting
link") **TIDAK PERNAH BEKERJA** di deployment manapun yang memakai kode SEKARANG — peserta
appointment/meeting TIDAK PERNAH menerima link Jitsi lewat email, walau integrasi Jitsi aktif dan
`jitsi_link` event terisi benar di database. Users harus membuka record `calendar.event` secara
manual di backend untuk mendapat link Jitsi (via `action_join_video_call()`), fitur "otomatis
lewat email" sepenuhnya tidak berfungsi.
**Rekomendasi:** Tambahkan `"data/mail_template_data.xml"` ke list `"data"` di `__manifest__.py`,
lalu `-u appointment_jitsi` (upgrade modul) di semua deployment yang sudah terinstall — TAPI
perlu diperhatikan: karena pola override memakai `noupdate` flip (lihat file XML), upgrade modul
yang SUDAH TERLANJUR terinstall tanpa file ini mungkin perlu langkah tambahan (drop record
`ir.model.data` lama / uninstall-reinstall) supaya override benar-benar ter-apply — perlu
pengujian tambahan terpisah dari BACKFILL (di luar scope: BACKFILL tidak mengubah kode bisnis).
**Keputusan pemilik modul:** *(kosong — diisi manusia — ini WAJIB diputuskan mengingat dampaknya
ke fitur inti modul)*

---

## Limitasi Tool (kalau ada)

- Modul tidak punya `tests/` sama sekali sebelum backfill — semua 12 test di `tests/test_appointment_jitsi.py`
  adalah test BARU yang ditulis BACKFILL, bukan test yang sudah ada sebelumnya.
- F-08 (`generate_jitsi_link()`/`clear_jitsi_link()` tidak terhubung UI) tidak bisa dipastikan
  100% "dead code" murni dari kode repo ini — mungkin dipanggil dari server action/automation
  ad-hoc di database produksi yang bukan bagian dari kode modul, tidak terlihat dari BACKFILL.
- Step 04 SEMPAT gagal total di percobaan pertama (F-12) — diselesaikan dengan SATU workaround
  infrastruktur (mount Enterprise addons lokal), bukan workaround kode. Kalau workaround itu
  tidak tersedia di environment lain (mis. CI tanpa akses Enterprise), Step 04 modul ini TIDAK
  BISA dijalankan sampai infrastruktur serupa disediakan.
