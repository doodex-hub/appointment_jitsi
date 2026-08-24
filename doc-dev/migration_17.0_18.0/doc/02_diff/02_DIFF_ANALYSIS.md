# Diff & Compatibility Analysis — appointment_jitsi

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Ref:** `01_intake/01a_MIGRATION_INTAKE.md`, `migration-tool/knowledge/`

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/17-to-18.md` | Ya | `migration-tool/knowledge/version-diffs/17-to-18.md` — dipakai sebagai referensi umum di bawah |
| `dependency-compat/<nama>/...` | Tidak ada entry untuk `calendar`/`appointment`/`base` spesifik | `migration-tool/knowledge/dependency-compat/` (ada `account_payment`, `auth_totp`, `auth_totp_mail_enforce`, `purchase_product_matrix`, `sale_report` — tidak relevan ke modul ini) |

## 0b. Gate Community vs Enterprise

- [x] `01a_MIGRATION_INTAKE.md` §2 mencantumkan SATU baris "Native Enterprise" (`appointment`).
- [x] `native-target-enterprise` (`enterprise18`) dan `native-source-enterprise` (`enterprise17`) sudah di-connect (lihat `01a_MIGRATION_INTAKE.md` §0) — dipakai langsung untuk cek `appointment.appointment_booked_mail_template` di bawah (`DIFF-05`), bukan diasumsikan dari Community.
- Setiap baris `DIFF-NNN` di §1 di bawah menyebut eksplisit sumber cek: `native-source`/`native-target` (Community, `odoo17`/`odoo18`) untuk simbol `calendar`, `native-source-enterprise`/`native-target-enterprise` (`enterprise17`/`enterprise18`) untuk simbol `appointment`.

## 0c. Gate Transitive Dependency

Tidak ada `depends` yang dihapus dari manifest modul ini pada migrasi ini (`base`, `appointment`, `calendar` semua tetap ada di 18.0, dikonfirmasi §1 di bawah) — gate ini **N/A**, tidak ada dependency yang perlu dievaluasi transitifnya.

---

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `models/calendar_event.py:71-78` — override `create(self, values)` dengan `@api.model` (single-record) | `odoo/api.py` — wrapper `_model_create_single` untuk `@api.model` yang dipakai di `create()` | **Tidak berubah** — dikonfirmasi baca langsung `native-source/odoo/api.py` DAN `native-target/odoo/api.py`: pesan `DeprecationWarning` "The model {module} is not overriding the create method in batch" dan mekanisme wrapper `_model_create_single` byte-identical di 17.0 dan 18.0. Base `models.py` `create()` sendiri sudah `@api.model_create_multi` di KEDUA versi (bukan perubahan baru di 18.0). | **Koreksi ke `knowledge/version-diffs/17-to-18.md` §1b** (entri "Python `create()` — wajib" berlaku UMUM tapi TIDAK berarti install-blocking untuk kasus spesifik modul ini): signature lama TETAP jalan di 18.0 lewat wrapper deprecated yang sama, BUKAN hard requirement kompatibilitas. Karena dev memutuskan bug-for-bug (F-03 dipertahankan, lihat `FINDINGS.md` MF-02), TIDAK ADA alasan teknis wajib mengubah signature ini saat migrasi — boleh di-port 1:1 apa adanya. | `native-source`=`odoo17/odoo/api.py`, `native-target`=`odoo18/odoo/api.py` (line ~484-488, identik) |
| DIFF-02 | `models/calendar_event.py:37-59` — baca/tulis field core `access_token`, `videocall_location`; panggil `_set_discuss_videocall_location()` | `calendar.event`: field `access_token`, `videocall_location` (compute `_compute_videocall_location`, `@api.depends('videocall_source', 'access_token')`), `videocall_source` (compute `_compute_videocall_source`), method `_set_discuss_videocall_location()` | **Tidak berubah** — byte-identical (hanya offset baris file bergeser +7 baris, isi logic sama persis) antara `odoo17/addons/calendar/models/calendar_event.py` dan `odoo18/addons/calendar/models/calendar_event.py`. | `[BSL-006]`/`[BSL-010]` (quirk "urutan akses field menentukan hasil compute") akan berperilaku IDENTIK di 18.0 — tidak perlu penyesuaian, dan tidak ada risiko baru dari native. | `native-source`=`odoo17/addons/calendar/models/calendar_event.py:128-533`, `native-target`=`odoo18/addons/calendar/models/calendar_event.py:129-534` |
| DIFF-03 | `views/calendar_views.xml` — `<xpath expr="//setting[@id='sync_google_calendar_setting']" position="after">`, `inherit_id="calendar.res_config_settings_view_form"` | View `calendar.res_config_settings_view_form`, anchor `id="sync_google_calendar_setting"` | **Tidak berubah** — anchor `sync_google_calendar_setting` ada di baris yang sama persis (`res_config_settings_views.xml:17`) di kedua versi. Syntax `invisible="not is_jitsi"` modul ini SUDAH memakai bentuk modern (bukan `attrs=`), jadi tidak kena breaking change `<tree>`→`<list>` (view ini bukan tree/list, murni settings form) atau perubahan chatter/kanban di `knowledge/version-diffs/17-to-18.md` §1. | View inherit ini bisa di-port 1:1, xpath tidak perlu diubah. | `native-source`=`odoo17/addons/calendar/views/res_config_settings_views.xml`, `native-target`=`odoo18/addons/calendar/views/res_config_settings_views.xml` |
| DIFF-04 | `data/mail_template_data.xml` — override `<record id="calendar.calendar_template_meeting_update" model="mail.template">` | XML-ID `calendar.calendar_template_meeting_update` di `calendar/data/mail_template_data.xml` | **Ada, tidak dihapus** di 18.0 — XML-ID dikonfirmasi masih ada di `odoo18/addons/calendar/data/mail_template_data.xml`. Isi body template kemungkinan berbeda kosmetik (belum di-diff detail — **tidak prioritas** karena override ini tidak pernah ter-load sama sekali, lihat `[BSL-015]`/F-13, dan dev memutuskan dipertahankan tidak aktif). | Tidak ada dampak fungsional untuk migrasi ini (file tetap tidak terdaftar di manifest 18.0, sama seperti 17.0). Dicatat untuk referensi kalau F-13 suatu saat diperbaiki di luar scope migrasi ini — body template perlu di-diff ulang saat itu. | `native-target`=`odoo18/addons/calendar/data/mail_template_data.xml` |
| DIFF-05 | `data/mail_template_data.xml` — override `<record id="appointment.appointment_booked_mail_template" model="mail.template">` | XML-ID `appointment.appointment_booked_mail_template` di `enterprise18/appointment/data/mail_template_data.xml` | **Ada, tidak dihapus** di 18.0 Enterprise — dikonfirmasi langsung di `native-target-enterprise` (`enterprise18/appointment/data/mail_template_data.xml`), juga direferensikan di `enterprise18/appointment/models/calendar_event.py`. Sama seperti DIFF-04, isi body belum di-diff detail (tidak prioritas, override tidak pernah aktif). | Sama seperti DIFF-04 — tidak ada dampak fungsional untuk migrasi bug-for-bug ini. | `native-target-enterprise`=`enterprise18/appointment/data/mail_template_data.xml` |
| DIFF-06 | `__manifest__.py` `depends: ["base", "appointment", "calendar"]` | Modul `appointment` (Enterprise) | **Tidak dihapus** — dikonfirmasi ada di `enterprise18/appointment` (juga di `enterprise17/appointment`), TIDAK ada di `odoo18/addons` maupun `odoo17/addons` Community di KEDUA versi. Bukan kasus seperti `sale_product_configurator` (lesson `purchase_product_optional`) yang hilang total di 18.0 — modul `appointment` tetap ada dan tetap Enterprise di kedua versi. | Tidak perlu perubahan `depends`. Dev testing (Step 9) tetap wajib mount `enterprise18` (bukan lagi `enterprise17`) sebagai extra addons path, sama pola seperti backfill mount `enterprise17` (lihat `doc-dev/backfill/FINDINGS.md` F-12). | `native-source-enterprise`=`enterprise17`, `native-target-enterprise`=`enterprise18` |
| DIFF-07 | `views/calendar_views.xml` — cek breaking change `<tree>`→`<list>` (knowledge §1) | N/A | **N/A** — modul ini tidak punya `<tree>`/`<list>` view sama sekali (satu-satunya view adalah settings form inherit). | Tidak ada risiko install-blocking dari breaking change ini. | Baca langsung `views/calendar_views.xml` (`source-codebase`) — tidak ada tag `<tree>` |
| DIFF-08 | Cek breaking change chatter `<div class="oe_chatter">` (knowledge §1) | N/A | **N/A** — modul ini tidak menyentuh form `calendar.event` sama sekali (tidak ada chatter custom di view manapun). | Tidak ada risiko. | Baca langsung `views/calendar_views.xml` |
| DIFF-09 | Cek breaking change kanban arch (knowledge §1) | N/A | **N/A** — tidak ada kanban view di modul ini. | Tidak ada risiko. | Baca langsung struktur folder `views/` |
| DIFF-10 | Cek Owl/JS breaking changes (knowledge §1b) | N/A | **N/A** — dikonfirmasi di `01a_MIGRATION_INTAKE.md` §2b: tidak ada file `.js`, tidak ada folder `static/src/`, tidak ada key `assets` di manifest. | Tidak ada risiko — Fase E/F Step 6 langsung N/A. | Struktur folder `source-codebase/appointment_jitsi/` |

## 2. Kompatibilitas Dependency (OCA/Third-Party)

N/A — dikonfirmasi dev di `01a_MIGRATION_INTAKE.md` §0 tidak ada dependency OCA/vendor pihak ketiga.

## 3. Temuan Baru — Ditulis ke Migration Records

- [x] `DIFF-01` (koreksi ke knowledge base umum soal `create()`/`@api.model_create_multi`) — ditulis sebagai kandidat kategori `version-diff` di `migration-tool/migration-records/appointment_jitsi_17.0_18.0/SUMMARY.md`. **Belum** dipromosikan ke `knowledge/version-diffs/17-to-18.md` — itu HANYA lewat sesi curation eksplisit.

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| Dependency `appointment` Enterprise hilang/berubah struktur di 18.0 | **Rendah** (sudah dikonfirmasi tidak hilang, lihat DIFF-06) | Tetap wajib mount `enterprise18` di dev testing (Step 9) |
| Field/method core `calendar.event` yang dipakai modul berubah di 18.0 | **Rendah** — byte-identical (DIFF-02, DIFF-03) | Tidak perlu penyesuaian kode |
| `create()` signature lama (`@api.model`) gagal/di-block di 18.0 | **Rendah** — dikonfirmasi masih didukung via deprecated wrapper yang sama (DIFF-01) | Boleh port 1:1, konsisten dengan keputusan bug-for-bug F-03 |
| Breaking change umum 17→18 (`<tree>`, chatter, kanban, Owl/JS) | **Tidak relevan (N/A)** | Modul terlalu kecil/sederhana untuk terkena — dikonfirmasi eksplisit per item (DIFF-07..10), bukan diasumsikan |
| Override mail template (F-13) — apakah manifest 18.0 "keceplosan" mendaftarkan file ini | **Perlu kewaspadaan proses, bukan risiko teknis** | Step 6 WAJIB TIDAK menambahkan `data/mail_template_data.xml` ke `data` manifest 18.0 — sudah ditegaskan di `CLAUDE.md`/`FINDINGS.md` MF-01 |
| Perubahan versi manifest `17.0.1.0.0` → `18.0.1.0.0` | **Rendah** | Housekeeping standar, dikerjakan di Step 6 |

**Kesimpulan Step 2:** modul ini SANGAT KECIL dan SEDERHANA — 2 model inherit, 1 view inherit, 1 data file (tidak aktif), tanpa JS/Owl/controller aktif. Tidak ditemukan satu pun breaking change 17→18 yang benar-benar berdampak ke modul ini setelah dicek satu-satu terhadap `native-source`/`native-target` dan `native-source-enterprise`/`native-target-enterprise`. Risiko migrasi keseluruhan: **RENDAH** — Step 3 (Migration Spec) kemungkinan besar akan berupa port langsung + bump versi manifest, tanpa perubahan logic.
