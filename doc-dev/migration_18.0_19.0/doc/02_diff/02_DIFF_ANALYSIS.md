# Diff & Compatibility Analysis — appointment_jitsi

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Ref:** `01_intake/01a_MIGRATION_INTAKE.md`, `migration-tool/knowledge/`

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/18-to-19.md` | Ya | §1 (OCA wiki, generik) + §1a (1 temuan nyata dari `advanced_sales_analysis`: `sale.order.line.tax_id`→`tax_ids`) |
| `dependency-compat/<nama>/...` | Tidak ada entry untuk `calendar`/`appointment` spesifik | Ada `sale_report` (dari `advanced_sales_analysis`) — tidak relevan ke modul ini |

## 0b. Gate Community vs Enterprise

- [x] `01a_MIGRATION_INTAKE.md` §2 mencantumkan SATU baris "Native Enterprise" (`appointment`).
- [x] `native-target`+`native-target-enterprise` (SATU folder gabungan `enterprise19.0`) dan `native-source`/`native-source-enterprise` (`odoo18`/`enterprise18`) sudah di-connect — dipakai langsung untuk cek `appointment.appointment_booked_mail_template` di bawah (`DIFF-05`).

## 0c. Gate Transitive Dependency

Tidak ada `depends` yang dihapus dari manifest modul ini (`base`, `appointment`, `calendar` semua tetap ada di 19.0, dikonfirmasi §1 di bawah) — gate ini **N/A**.

---

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| **DIFF-01** | `models/calendar_event.py` — override `create(self, values)` dengan `@api.model` (single-record signature) | `odoo/orm/decorators.py` `model()` — routing `@api.model create` | **⚠️ BERUBAH — temuan paling penting Step 2 ini.** Di 18.0 (`odoo/api.py:421-433`), `@api.model` pada `create` di-route ke `model_create_single()` → wrapper `_model_create_single` yang, kalau argumen berupa LIST, **meng-iterasi dan memanggil override per-dict** (`self.browse().concat(*(create(self, vals) for vals in arg))`) — method asli tetap menerima `values` sebagai SATU dict per panggilan. Di 19.0 (`odoo/orm/decorators.py:309-321`), `@api.model` pada `create` di-route ke `model_create_multi()` (`odoo/orm/decorators.py:353-368`) — wrapper ini **TIDAK PERNAH memecah list**: dict tunggal dibungkus jadi `[vals]`, list tetap dikirim utuh sebagai list. Method asli (`values` parameter di kode modul) SEKARANG SELALU menerima LIST, tidak pernah dict mentah, apapun cara caller memanggil. | **Dampak ke `[BSL-005]`:** kode `if 'is_jitsi' in values:` (mengecek keanggotaan key di dict) akan SELALU jadi pengecekan keanggotaan STRING DI LIST di 19.0 (list tidak pernah berisi string `'is_jitsi'` sebagai elemen) — cabang UUID-generation eksplisit di `create()` **tidak akan pernah terpicu lagi, termasuk untuk single-create** (beda dari 18.0 di mana single-create memicu cabang ini dengan benar). **Mitigasi parsial:** `[BSL-006]` (`_compute_jitsi_link`) punya logic UUID-generation REDUNDAN sendiri ("generate `access_token` UUID kalau belum ada") — jitsi_link kemungkinan besar TETAP terisi lewat compute, hanya lewat jalur berbeda dari 18.0. **Yang kemungkinan benar-benar hilang:** efek eksplisit "reset `access_token=False` saat `is_jitsi=False` dikirim bareng `access_token` di dict yang sama" (paruh kedua `[BSL-005]`) — edge case jarang terjadi di penggunaan nyata. **WAJIB diverifikasi empiris via 13 test existing di Step 9** (khususnya test yang menutupi `[BSL-005]`/`[BSL-009]`) — jangan disimpulkan aman/rusak hanya dari baca statis ini, persis seperti `[BSL-009]` sendiri baru concludable setelah eksekusi test nyata di project 17.0→18.0. | `native-source`=`odoo18/odoo/api.py:421-491`, `native-target`=`enterprise19.0/odoo/orm/decorators.py:309-368` |
| DIFF-02 | `models/calendar_event.py` — baca/tulis field core `access_token`, `videocall_location`; panggil `_set_discuss_videocall_location()` | `calendar.event`: field `access_token`, `videocall_location` (compute `_compute_videocall_location`), method `_set_discuss_videocall_location()` | **Tidak berubah** — byte-identical (offset baris bergeser +12, isi logic sama persis, dikonfirmasi baca langsung kedua file). | `[BSL-006]`/`[BSL-010]` (quirk "urutan akses field menentukan hasil compute") akan berperilaku IDENTIK di 19.0. | `native-source`=`odoo18/addons/calendar/models/calendar_event.py:129-534`, `native-target`=`enterprise19.0/odoo/addons/calendar/models/calendar_event.py:141-577` |
| DIFF-03 | `views/calendar_views.xml` — `<xpath expr="//setting[@id='sync_google_calendar_setting']" position="after">`, `inherit_id="calendar.res_config_settings_view_form"` | View `calendar.res_config_settings_view_form`, anchor `id="sync_google_calendar_setting"` | **Tidak berubah** — anchor ada di baris yang SAMA PERSIS (`res_config_settings_views.xml:17`) di kedua versi. Syntax `invisible="not is_jitsi"` sudah modern, tidak kena breaking change apapun (view ini bukan search view, jadi tidak kena breaking `<group string=/expand=>` di `knowledge/version-diffs/18-to-19.md` §1). | View inherit bisa di-port 1:1, xpath tidak perlu diubah. | `native-source`=`odoo18/addons/calendar/views/res_config_settings_views.xml`, `native-target`=`enterprise19.0/odoo/addons/calendar/views/res_config_settings_views.xml` |
| DIFF-04 | `data/mail_template_data.xml` — override `<record id="calendar_template_meeting_update" model="mail.template">` | XML-ID `calendar.calendar_template_meeting_update` | **Ada, tidak dihapus** di 19.0 (`enterprise19.0/odoo/addons/calendar/data/mail_template_data.xml:348`). Tidak relevan fungsional — override ini tidak pernah ter-load (`[BSL-015]`). | Tidak ada dampak fungsional (file tetap tidak terdaftar di manifest 19.0). | `native-target`=`enterprise19.0/odoo/addons/calendar/data/mail_template_data.xml` |
| DIFF-05 | `data/mail_template_data.xml` — override `<record id="appointment_booked_mail_template" model="mail.template">` | XML-ID `appointment.appointment_booked_mail_template` | **Ada, tidak dihapus** di 19.0 Enterprise (`enterprise19.0/odoo/addons/appointment/data/mail_template_data.xml:5`). | Sama seperti DIFF-04 — tidak ada dampak fungsional. | `native-target-enterprise`=`enterprise19.0/odoo/addons/appointment/data/mail_template_data.xml` |
| DIFF-06 | `__manifest__.py` `depends: ["base", "appointment", "calendar"]` | Modul `appointment` (Enterprise) | **Tidak dihapus, tetap Enterprise.** Dikonfirmasi `enterprise19.0/odoo/addons/appointment/__manifest__.py` → `'license': 'OEEL-1'` (sama seperti 17.0/18.0), sekaligus dikonfirmasi TIDAK ADA `appointment` di `odoo18/addons` Community. `calendar` tetap `LGPL-3`. | Tidak perlu perubahan `depends`. Dev testing (Step 9) WAJIB mount `enterprise19.0` (folder gabungan Community+Enterprise 19.0, BUKAN git repo) sebagai addons path. | `native-source-enterprise`=`enterprise18`, `native-target`/`native-target-enterprise`=`enterprise19.0` |
| DIFF-07 | Cek pola generik `knowledge/version-diffs/18-to-19.md` §1 (`self._cr`/`_uid`/`_context`, `osv.expression`, `_sql_constraints`, `auto_join`, `type="json"`, `toggle_active`, `SUPERUSER_ID` import, `ormcache_context`, `urljoin`, `name_search(args=)`, `api.returns`, `read_group()`, `category_id`/`groups_id` `res.groups`) | N/A | **N/A — dikonfirmasi via grep menyeluruh** ke seluruh `.py`/`.xml` modul (`source-codebase/appointment_jitsi/`): nol match untuk semua pola di atas. Modul tidak memakai satupun pattern yang di-deprecate/dihapus di 19.0. | Tidak ada risiko dari breaking change framework generik. | `source-codebase/appointment_jitsi/**/*.py`, `**/*.xml` |
| DIFF-08 | Cek breaking `<tree>`→`<list>`, chatter, kanban, `<group string=/expand=>` search view | N/A | **N/A** — modul tidak punya `<tree>`/`<list>`/kanban/chatter/search view sama sekali (satu-satunya view adalah settings form). | Tidak ada risiko. | `views/calendar_views.xml` |
| DIFF-09 | Cek breaking Owl/JS (`t-raw`→`t-out`, dst) | N/A | **N/A** — tidak ada file `.js`/Owl di modul (dikonfirmasi `01a_MIGRATION_INTAKE.md` §2b). | Tidak ada risiko. | Struktur folder `source-codebase/appointment_jitsi/` |
| DIFF-10 | `knowledge/version-diffs/18-to-19.md` §1a — rename `sale.order.line.tax_id`→`tax_ids` (temuan `advanced_sales_analysis`) | `sale.order.line` | **Tidak relevan** — modul ini tidak menyentuh `sale.order.line`/`sale.report`/perhitungan pajak SO line sama sekali. | Tidak ada dampak. | Baca kode modul — tidak ada referensi `sale.order` |

## 2. Kompatibilitas Dependency (OCA/Third-Party)

N/A — dikonfirmasi dev di `01a_MIGRATION_INTAKE.md` §0 tidak ada dependency OCA/vendor pihak ketiga.

## 3. Temuan Baru — Ditulis ke Migration Records

- [x] `DIFF-01` (perubahan mekanisme `@api.model create` → `model_create_multi` di 19.0, ORM core dipindah ke `odoo/orm/decorators.py`) — **kandidat kuat untuk `knowledge/version-diffs/18-to-19.md`** (belum tercantum di §1/§1a manapun, dan berpotensi berdampak ke MODUL LAIN manapun yang meng-override `create()` dengan gaya `@api.model` single-dict, pola yang cukup umum di modul custom lama). Ditulis sebagai kandidat kategori `version-diff` + `dependency-compat/calendar` di `migration-tool/migration-records/appointment_jitsi_18.0_19.0/SUMMARY.md`. **Belum** dipromosikan ke `knowledge/` — hanya lewat sesi curation eksplisit.

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| **Mekanisme `@api.model create` berubah (DIFF-01)** | **SEDANG-TINGGI** — perlu verifikasi empiris Step 9, bukan cuma port 1:1 tanpa dicek | Kemungkinan besar observable behavior TETAP setara (fallback UUID di `_compute_jitsi_link`), tapi edge case `[BSL-005]` paruh kedua (reset `access_token=False`) kemungkinan berubah. Kode BOLEH tetap di-port 1:1 (bug-for-bug), TAPI hasil test 13/13 WAJIB dicek ulang satu-satu di Step 9, jangan diasumsikan pasti PASS seperti migrasi 17.0→18.0 sebelumnya. |
| Dependency `appointment` Enterprise hilang/berubah struktur di 19.0 | **Rendah** (dikonfirmasi tidak hilang, DIFF-06) | Tetap wajib mount `enterprise19.0` (folder gabungan) di dev testing |
| Field/method core `calendar.event` yang dipakai modul berubah di 19.0 | **Rendah** — byte-identical (DIFF-02, DIFF-03) | Tidak perlu penyesuaian kode |
| Breaking change umum 18→19 (ORM Domain, `_sql_constraints`, dll — `knowledge/version-diffs/18-to-19.md` §1) | **Tidak relevan (N/A)** | Modul tidak memakai pattern manapun yang terdampak (DIFF-07) |
| Override mail template (F-13/`[BSL-015]`) — manifest 19.0 "keceplosan" mendaftarkan file ini | **Perlu kewaspadaan proses, bukan risiko teknis** | Step 6 WAJIB TIDAK menambahkan `data/mail_template_data.xml` ke `data` manifest 19.0 |
| Perubahan versi manifest `18.0.1.0.0` → `19.0.1.0.0` | **Rendah** | Housekeeping standar, Step 6 |

**Kesimpulan Step 2:** modul ini tetap KECIL dan SEDERHANA secara struktural, dan hampir semua permukaan API yang dipakai (field core `calendar.event`, XML-ID view/template, lisensi `appointment`) **byte-identical/tidak berubah** antara 18.0 dan 19.0. **TAPI** ditemukan SATU perubahan mekanisme ORM core yang genuinely relevan (`DIFF-01` — `@api.model create` routing) yang TIDAK tercantum di riset OCA wiki manapun (`knowledge/version-diffs/18-to-19.md` §1/§1a) — modul ini jadi data point PERTAMA untuk temuan ini. Risiko migrasi keseluruhan: **RENDAH-SEDANG** (naik dari "RENDAH" murni di migrasi 17.0→18.0) — Step 3 tetap berupa port langsung + bump versi manifest tanpa perubahan logic yang disengaja, TAPI Step 9 dev testing WAJIB dijalankan lengkap dan hasilnya dibandingkan detail per test (bukan cuma "13/13 PASS" sebagai angka, tapi per-assertion) untuk memastikan `[BSL-005]`/`[BSL-009]` masih berperilaku setara secara observable.
