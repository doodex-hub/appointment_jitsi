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

| ID | Judul | Tag | Prioritas |
|---|---|---|---|
| F-01 | `is_jitsi_param` dibaca sebagai string truthy, bukan boolean | `[PERLU-KEPUTUSAN]` | Tinggi |
| F-02 | `is_jitsi` toggle via `write()` tidak memicu recompute link | `[PERLU-KEPUTUSAN]` | Tinggi |
| F-03 | `create()` tidak batch-safe (`@api.model` bukan `@api.model_create_multi`) | `[PERLU-KEPUTUSAN]` | Tinggi |
| F-04 | `videocall_location` ditulis dari compute lain, bukan compute resminya | `[PERLU-KEPUTUSAN]` | Tinggi |
| F-05 | `company_param` global, tidak per-company (multi-company) | `[PERLU-KEPUTUSAN]` | Sedang |
| F-06 | `controllers/appointment.py` 100% dead code (di-comment-out) | `[HASIL-BACA]` | Rendah |
| F-07 | URL Jitsi memakai nama company mentah + duplikasi segmen path | `[PERLU-KEPUTUSAN]` | Sedang |
| F-08 | `generate_jitsi_link()`/`clear_jitsi_link()` tidak terhubung ke UI manapun | `[PERLU-KEPUTUSAN]` | Rendah |
| F-09 | File `googleaeed8a7b9ec156e7.html` (Google Search Console verification) ikut ter-commit di root modul | `[PERLU-KEPUTUSAN]` | Rendah |

---

## Detail

### F-01 — `is_jitsi_param` dibaca sebagai string truthy, bukan boolean
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/calendar_event.py:42-48`
**Ref:** BR-08, AC-01-03
**Deskripsi:** `get_param('is_jitsi_param')` dipakai langsung di `if is_jitsi_enabled:` tanpa
dikonversi eksplisit ke bool. `ir.config_parameter` menyimpan `fields.Boolean(config_parameter=...)`
sebagai string setelah pernah di-set. Python menganggap string `"False"` sebagai truthy (non-empty
string). Kalau Odoo core menyimpan literal string `"False"` saat admin uncheck setting (bukan
menghapus key), integrasi Jitsi TETAP dianggap aktif meski sudah dimatikan.
**Dampak:** Kalau benar terjadi, admin tidak bisa benar-benar mematikan integrasi Jitsi setelah
pernah mengaktifkannya sekali — semua event baru tetap dapat link Jitsi bukan link Discuss.
**Rekomendasi:** Cast eksplisit, mis. `is_jitsi_enabled = get_param('is_jitsi_param') in ('True', True, '1')`
atau pola standar Odoo `bool(get_param(...))` setelah cek behavior asli (lihat verifikasi Step 04
di bawah).
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-02 — `is_jitsi` toggle via `write()` tidak memicu recompute link
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/calendar_event.py:20-23, 37`
**Ref:** BR-05, AC-04-01
**Deskripsi:** `_compute_jitsi_link` hanya `@api.depends('access_token')`, tidak menyertakan
`is_jitsi`. Toggle `is_jitsi` True/False pada event yang sudah ada (lewat form/`write()`, tidak
di-override modul ini) tidak mengubah `access_token`, sehingga tidak memicu recompute sama sekali.
**Dampak:** Event yang diubah dari `is_jitsi=False` ke `True` (atau sebaliknya) lewat edit form
BISA menampilkan link yang tidak konsisten dengan status `is_jitsi` terbaru sampai ada trigger
lain (mis. field lain yang kebetulan memicu `access_token` berubah).
**Rekomendasi:** Tambahkan `is_jitsi` ke `@api.depends`, atau override `write()` untuk memanggil
ulang compute saat `is_jitsi` berubah.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-03 — `create()` tidak batch-safe (`@api.model` bukan `@api.model_create_multi`)
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/calendar_event.py:71-78`
**Ref:** BR-03, AC-02-03
**Deskripsi:** Override `create(self, values)` pakai `@api.model` (single-record semantics) sesuai
konvensi Odoo < 13, padahal Odoo 17 memanggil `create()` dengan LIST of dict untuk skenario batch
(termasuk event berulang lewat `calendar.recurrence`). `'is_jitsi' in values` pada input list
mengecek keanggotaan string di list, bukan di tiap dict — hampir selalu `False`.
**Dampak:** `access_token` tidak ikut di-generate lewat jalur `create()` untuk create batch;
kalau `is_jitsi_param` global TIDAK aktif, event batch itu tidak pernah dapat Jitsi link lewat
jalur manapun (fallback ke Discuss, sesuai BR-01) — tapi kalau `is_jitsi_param` global aktif,
compute `_compute_jitsi_link` tetap bisa menghasilkan link Jitsi terlepas dari override `create()`
ini (karena logic global tidak bergantung pada `is_jitsi` per-event, lihat BR-01) — TAPI
`access_token` yang dipakai jadi hasil generate compute, bukan hasil override `create()` — efek
akhirnya BISA sama, perlu dikonfirmasi test nyata apakah ada skenario yang benar-benar berbeda
hasilnya.
**Rekomendasi:** Ganti ke `@api.model_create_multi def create(self, vals_list)`, loop tiap dict.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-04 — `videocall_location` ditulis dari compute lain, bukan compute resminya
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `models/calendar_event.py:56, 59`
**Ref:** BR-04, AC-03-01
**Deskripsi:** `videocall_location` adalah field `calendar.event` core Odoo dengan compute
resminya sendiri. Modul ini menulis field itu secara imperatif dari `_compute_jitsi_link` (method
BEDA, depends BEDA) tanpa mendeklarasikan ulang `compute=` field tersebut. Ini kelas bug SEJENIS
dengan lesson "tabrakan nama method Odoo core" di `PLAYBOOK.md`, tapi levelnya field-compute:
kalau compute RESMI `videocall_location` ter-trigger ulang oleh dependency-nya sendiri
(kemungkinan `videocall_source` atau field lain, BUKAN `access_token`), nilai Jitsi yang sudah
ditulis modul ini berisiko tertimpa balik tanpa error yang terlihat.
**Dampak:** Kalau terkonfirmasi, link Jitsi bisa "hilang"/kembali ke link Discuss secara silent
tiap kali ada operasi yang memicu compute resmi `videocall_location` (mis. update field terkait
video call lewat jalur lain, sync, dst).
**Rekomendasi:** Verifikasi lewat `__mro__`/depends check (Step 04, pola sama dengan lesson
`purchase_product_optional`) apakah race ini benar-benar terjadi di runtime. Kalau ya,
pertimbangkan set `videocall_location` HANYA lewat compute resminya (override compute resmi, atau
tambahkan `access_token`/kondisi Jitsi ke dependency compute resmi) alih-alih menulis dari method
lain.
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

## Limitasi Tool (kalau ada)

- F-01, F-04, F-05 butuh konfirmasi RUNTIME (bukan cuma baca kode) — dijadwalkan diverifikasi di
  Step 04 (`TransactionCase` + `_logger.info` pola sama seperti lesson `purchase_product_optional`
  soal `ir.config_parameter`/`__mro__` compute).
- Modul tidak punya `tests/` sama sekali sebelum backfill — semua test di Step 04 adalah test BARU
  yang ditulis BACKFILL, bukan test yang sudah ada sebelumnya.
