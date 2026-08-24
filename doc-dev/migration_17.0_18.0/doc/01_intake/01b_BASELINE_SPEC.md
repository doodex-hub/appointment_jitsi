# Baseline Spec — appointment_jitsi

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 17.0 — bukan bagaimana diimplementasikan.
**Tanggal:** 2026-08-24
**Sumber:** Direkonsiliasi dari `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` + `01B_ACCEPTANCE_CRITERIA.md` (keduanya sudah diverifikasi via eksekusi test nyata, Odoo 17 Enterprise + Postgres 15 Docker, `appointment_jitsi/tests/test_appointment_jitsi.py`) + cross-check langsung ke kode `source-codebase/appointment_jitsi/`. Semua klaim di bawah cocok dengan kode aktual — tidak ditemukan penyimpangan baru.

> Ini **sumber kebenaran** untuk `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` dan semua testing (step 9, 10, 11) — BUKAN `03_MIGRATION_SPEC.md`.

---

## Provenance Tag

Semua klaim di bawah bertag `[MATCH]` — sudah dibahas di `01A_FUNCTIONAL_SPEC.md`/`01B_ACCEPTANCE_CRITERIA.md`/`FINDINGS.md` dan dikonfirmasi cocok dengan kode aktual (bahkan sudah diverifikasi via eksekusi test nyata saat backfill, confidence tinggi). Format: `[BSL-NNN] [MATCH] (ref: ...)`.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

Tally: 21 klaim, semua `[MATCH]` (0 `[GAP]`, 0 `[NO-SPEC]`) — modul ini sudah melalui backfill lengkap dengan test eksekusi nyata sebelum migrasi ini dimulai, jadi baseline-nya jauh lebih solid dari kasus migrasi tanpa spec lama.

Poin paling kritis untuk migrasi (bug yang WAJIB dipertahankan, bukan diperbaiki — sudah disetujui dev di `01a_MIGRATION_INTAKE.md`):

1. **`[BSL-015]` PALING KRITIS** — override mail template (`data/mail_template_data.xml`) tidak terdaftar di manifest, fitur "link Jitsi di email" TIDAK PERNAH aktif di 17.0. **WAJIB tetap tidak terdaftar di manifest 18.0** — jangan tambahkan baris ini ke `data` manifest saat Step 6, walau kelihatan seperti "bug jelas yang gampang diperbaiki".
2. **`[BSL-020]`** — field per-event `is_jitsi` tidak dipakai sama sekali di logic compute link — hanya setting global yang menentukan. Field ini secara efektif jadi "dekorasi" (cuma dipakai di 2 tempat lain: `create()` dan `action_join_video_call()`). Migrasi 18.0 harus mempertahankan pemisahan ini persis.
3. **`[BSL-010]`** — `jitsi_link`/`videocall_location` hasilnya bergantung urutan field mana yang diakses lebih dulu (side-effect dari compute yang menulis field lain tanpa redeclare). Ini quirk paling halus — kalau Step 6 "membersihkan" cara `_compute_jitsi_link` menulis `videocall_location`, behavior observable BISA berubah walau niatnya cuma refactor teknis. WAJIB port apa adanya.
4. **`[BSL-021]`** — dependency `appointment` berlisensi Enterprise (OEEL-1) di 17.0 DAN 18.0 (dikonfirmasi). Dev testing Step 9 nanti butuh akses `enterprise18` lokal, sama seperti backfill butuh `enterprise17`.
5. Sisa 17 klaim (`[BSL-001]`-`[BSL-009]`, `[BSL-011]`-`[BSL-014]`, `[BSL-016]`-`[BSL-019]`) — behavior lebih straightforward, detail di §4/5/8 di bawah.

---

## 1. Tujuan Modul

Modul menambahkan integrasi Jitsi Meet ke `calendar.event` (dipakai juga oleh alur Appointment Odoo): setiap event bisa mendapat link Jitsi unik (berbasis `access_token` UUID), disimpan di field baru `jitsi_link`, dan (secara teori — lihat `[BSL-015]`) link itu disisipkan ke template email konfirmasi appointment/undangan meeting supaya peserta bisa langsung join lewat Jitsi alih-alih Odoo Discuss bawaan.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `calendar.event` (`_inherit`) | Menyimpan `jitsi_link`/`is_jitsi`, generate/compute link, expose `action_join_video_call()` |
| `res.config.settings` (`_inherit`, TransientModel) | Toggle global "Enable Jitsi Integration" + pilih "Company" untuk URL room |

Tidak ada model baru — modul murni `_inherit`, karena itu `security/ir.model.access.csv` cuma berisi header tanpa baris akses.

## 3. Field dengan Makna Bisnis

### calendar.event
- `jitsi_link` (Text, compute `_compute_jitsi_link`, `store=True`, `copy=True`) — URL room Jitsi lengkap.
- `is_jitsi` (Boolean, default `False`) — flag per-event, TAPI lihat `[BSL-020]`: tidak dipakai di compute link.

### res.config.settings
- `is_jitsi` (Boolean, `config_parameter='is_jitsi_param'`) — toggle global aktif/tidaknya integrasi Jitsi untuk SEMUA event.
- `company_param` (Many2one `res.company`, `config_parameter='company_param'`, default `self.env.company`) — nama company dipakai di URL Jitsi, GLOBAL (lihat `[BSL-012]`).

## 4. Business Workflow / State Transition

### Aktivasi & penggunaan Jitsi
- `[BSL-001]` `[MATCH]` (ref: US-01) Admin membuka **Settings → Calendar → Jitsi Configuration**, mencentang "Enable Jitsi Integration", memilih "Company" yang namanya dipakai di URL room Jitsi.
- `[BSL-002]` `[MATCH]` (ref: BR-01, AC-01-01, AC-01-02) Kalau `ir.config_parameter('is_jitsi_param')` truthy DAN `company_param` menunjuk company valid: setiap event yang di-compute (`access_token` berubah/baru) mendapat `jitsi_link`/`videocall_location` format `https://meet.jit.si/{company}/{company}-{access_token}`. Kalau tidak aktif, event jatuh ke `_set_discuss_videocall_location()` bawaan Odoo (link Discuss standar).
- `[BSL-003]` `[MATCH]` (ref: US-02) User membuat/mengedit `calendar.event` dengan `is_jitsi=True`, mengharapkan link otomatis terisi dan bisa "Join" dari tombol standar (`action_join_video_call`) atau link di email.
- `[BSL-004]` `[MATCH]` (ref: US-03) Peserta appointment yang membuat janji lewat Appointment MENGHARAPKAN menerima email (`appointment_booked_mail_template`) dengan link Jitsi — **tapi lihat `[BSL-015]`: ekspektasi ini tidak pernah terwujud di kode 17.0 yang berjalan.**

## 5. Server-Side Logic dengan Side Effect

### calendar.event
- `[BSL-005]` `[MATCH]` (ref: BR-02, AC-02-01, AC-02-02) **create (single dict):** kalau key `is_jitsi` ada di `values` dan truthy → `access_token` di-set UUID baru sebelum `super().create()`. Kalau ada dan falsy → `access_token` di-set eksplisit `False`, menimpa `access_token` apapun yang sudah dikirim caller di dict yang sama.
- `[BSL-006]` `[MATCH]` (ref: BR-01, F-01) **`_compute_jitsi_link` (`@api.depends('access_token')`):** baca `is_jitsi_param` + `company_param` global via `ir.config_parameter`. Kalau aktif: loop tiap record, generate `access_token` UUID kalau belum ada, tulis `jitsi_link` DAN `videocall_location` dengan format yang sama. Kalau tidak aktif: panggil `_set_discuss_videocall_location()` (core). Catatan `is_jitsi_param`: dikonfirmasi via test nyata bahwa Odoo MENGHAPUS row `ir.config_parameter` saat admin uncheck setting (bukan menyimpan string `"False"`) — jadi `get_param()` balik Python bool `False` asli, BUKAN string truthy. Ini BUKAN bug (hipotesis awal backfill soal "truthy string" terbantahkan oleh eksekusi nyata).
- `[BSL-007]` `[MATCH]` (ref: `action_join_video_call`) **`action_join_video_call()`:** return `ir.actions.act_url` ke `self.jitsi_link` kalau `self.is_jitsi` true, else ke `self.videocall_location`. `target: 'new'`.
- `[BSL-008]` `[MATCH]` (ref: AC-08-01, F-08) **`generate_jitsi_link()`/`clear_jitsi_link()`:** method publik tersedia di model (`generate_jitsi_link` memanggil ulang `_compute_jitsi_link`; `clear_jitsi_link` set `jitsi_link = False`), TAPI tidak direferensikan di `views/calendar_views.xml` manapun (satu-satunya file view modul ini) sebagai button/server action.

## 6. Client-Side Behavior (Views)

### Backend
- `views/calendar_views.xml` — HANYA extend `res.config.settings` form (inherit `calendar.res_config_settings_view_form`), menambah setting block "Jitsi Configuration" dengan field `is_jitsi` + `company_param` (visible kalau `is_jitsi` true, pakai syntax modern `invisible="not is_jitsi"`, bukan `attrs=` lama).
- **Tidak ada** perubahan ke form/list/kanban `calendar.event` itu sendiri — field `jitsi_link` TIDAK ditampilkan di view manapun (hanya dipakai internal oleh compute + mail template + `action_join_video_call`).
- **Tidak ada** komponen Owl/JS custom, tidak ada asset/CSS custom.

### Public/Frontend
- Tidak ada widget publik/controller aktif — lihat `[BSL-016]`.

## 7. Dependency Eksternal

### Eksplisit (manifest)
- `depends: ["base", "appointment", "calendar"]`

### Implisit/Inferred
- `[BSL-021]` `[MATCH]` (ref: F-12) `appointment` (dan dependency-nya, `web_gantt`) berlisensi Enterprise (`OEEL-1`) — TIDAK tersedia di image Community publik `odoo:17.0`/`odoo:18.0`. Dev testing (Step 9) modul ini WAJIB akses source Odoo Enterprise (lokal: `enterprise17`/`enterprise18`).
- Modul menulis langsung ke field core `calendar.event.videocall_location` dan `calendar.event.access_token` (bukan field modul sendiri) — lihat `[BSL-010]`.
- Modul override 2 mail template BAWAAN (bukan mail template baru): `calendar.calendar_template_meeting_update` dan `appointment.appointment_booked_mail_template`, via `data/mail_template_data.xml` yang memakai pola `noupdate` flip (unlock → write → lock kembali).

## 8. Quirk / Behavior Non-Obvious

- `[BSL-009]` `[MATCH]` (ref: BR-03, AC-02-03, F-03) `create()` di-override dengan `@api.model` (single-record signature), bukan `@api.model_create_multi`. Odoo 17/18 memanggil `create()` dengan LIST of dict untuk skenario batch (termasuk recurring event via `calendar.recurrence`) — `'is_jitsi' in values` pada input list mengecek keanggotaan string di LIST (bukan di tiap dict), hampir selalu `False`. Dampak nyata (dikonfirmasi test): lebih ringan dari dugaan awal — `access_token` tetap terisi lewat default core untuk batch create, TAPI efek eksplisit reset `access_token=False` saat `is_jitsi=False` TIDAK terjadi untuk batch (beda dari single-create). Odoo sendiri mencetak WARNING resmi saat install modul ini soal ini.
- `[BSL-010]` `[MATCH]` (ref: BR-04, AC-03-01, F-04) `videocall_location` adalah field CORE `calendar.event` dengan compute resminya sendiri (`_compute_videocall_location`, dependency berbeda). Modul ini menulis field itu secara IMPERATIF dari `_compute_jitsi_link` (compute BEDA, depends BEDA — cuma `access_token`) tanpa redeclare field. Efek dikonfirmasi via test A/B (setup identik): kalau `jitsi_link` DIAKSES DULU → `_compute_jitsi_link` jalan, `videocall_location` ikut Jitsi. Kalau `videocall_location` DIAKSES DULU tanpa pernah menyentuh `jitsi_link` → compute RESMI core yang jalan, hasilnya `False` (bukan Jitsi) — override Jitsi TIDAK PERNAH terjadi untuk record itu. Karena `jitsi_link` tidak ditampilkan di view manapun, risiko "`videocall_location` diakses duluan oleh komponen UI core" cukup tinggi di penggunaan nyata.
- `[BSL-011]` `[MATCH]` (ref: BR-05, AC-04-01, F-02) `@api.depends('access_token')` tidak menyertakan `is_jitsi` — toggle `is_jitsi` True/False pada event EXISTING lewat `write()` tidak memicu recompute `jitsi_link`/`videocall_location` sama sekali (dikonfirmasi `bug_confirmed=True` via test nyata). Event lama tidak otomatis "ikut" perubahan setting global Jitsi sampai `access_token` berubah lewat jalur lain.
- `[BSL-012]` `[MATCH]` (ref: BR-06, AC-05-01, F-05) `company_param` adalah SATU `ir.config_parameter` GLOBAL, bukan per-company/per-event. Di setup multi-company, SEMUA room Jitsi lintas company memakai nama company yang sama (dikonfirmasi via test multi-company nyata).
- `[BSL-013]` `[MATCH]` (ref: BR-07, AC-06-01, F-07) Format URL: `f"{jitsi_base_url}/{company_name}/{company_name}-{access_token}"` — nama company disisipkan DUA KALI (folder + prefix room), tidak di-slug/escape. Nama company berspasi/karakter khusus masuk mentah ke URL.
- `[BSL-014]` `[MATCH]` (ref: BR-08, F-01) Hipotesis awal ("`is_jitsi_param` disimpan sebagai string `"False"` truthy setelah uncheck") **TERBANTAHKAN** oleh eksekusi nyata — Odoo core MENGHAPUS row `ir.config_parameter` saat `fields.Boolean(config_parameter=...)` di-uncheck, `get_param()` balik bool `False` asli. Bukan bug, tidak perlu perubahan apapun di 18.0, tapi wajib diverifikasi ulang saat dev testing 18.0 (mekanisme Odoo core ini bisa saja berbeda di versi baru — cross-check Step 2/9).
- `[BSL-015]` `[MATCH]` (ref: BR-09, AC-09-01, F-13) **PALING KRITIS.** `__manifest__.py` `data` HANYA berisi `["views/calendar_views.xml"]` — `data/mail_template_data.xml` tidak terdaftar. Odoo hanya memuat file yang eksplisit terdaftar; file yang ada di folder tapi tidak terdaftar TIDAK PERNAH dibaca, TANPA warning/error. Dikonfirmasi via test nyata: render `appointment_booked_mail_template` untuk event dengan `jitsi_link` penuh menghasilkan body HTML IDENTIK dengan template asli `appointment` core — override modul ini TIDAK PERNAH berlaku pada instalasi manapun yang memakai kode ini. **Keputusan dev untuk migrasi 18.0: dipertahankan apa adanya (lihat `01a_MIGRATION_INTAKE.md` §Ringkasan poin 3) — manifest 18.0 TIDAK mendaftarkan file ini.**
- `[BSL-016]` `[MATCH]` (ref: AC-07-01, F-06) `controllers/appointment.py` seluruh isinya di-comment-out (route custom `/calendar/join_jitsi/<token>` yang me-render halaman Jitsi embed sendiri via `external_api.js`). `controllers/__init__.py` tetap `from . import appointment` (no-op, tidak error). Tidak ada route HTTP tambahan yang benar-benar terdaftar dari modul ini — link "Join" di email pakai route bawaan `appointment`/`calendar`.
- `[BSL-017]` `[MATCH]` (ref: AC-08-01, F-08) `generate_jitsi_link()`/`clear_jitsi_link()` — lihat `[BSL-008]` — tidak terhubung UI manapun, kemungkinan dipanggil dari server action/automation eksternal di luar kode modul, atau sisa development.
- `[BSL-018]` `[MATCH]` (ref: F-09) File `googleaeed8a7b9ec156e7.html` (verifikasi Google Search Console) ikut ter-commit di root folder modul (`appointment_jitsi/googleaeed8a7b9ec156e7.html`) — tidak berhubungan dengan logic Odoo apapun, tidak dimuat Odoo sebagai apapun.
- `[BSL-019]` `[MATCH]` (ref: F-10) Label field "Company" pada `company_param` (modul ini) bentrok dengan `company_id` (`base_setup`) di form `res.config.settings` yang sama — Odoo mencetak WARNING resmi saat instalasi. Kosmetik, tidak ada dampak fungsional.
- `[BSL-020]` `[MATCH]` (ref: F-11) Field per-event `is_jitsi` TIDAK PERNAH dicek di dalam `_compute_jitsi_link` — HANYA `ir.config_parameter('is_jitsi_param')` GLOBAL yang menentukan Jitsi/Discuss untuk SEMUA event, terlepas nilai `is_jitsi` event itu sendiri. Dikonfirmasi test nyata: event dibuat TANPA `is_jitsi=True` tetap dapat `jitsi_link` penuh saat setting global aktif. Field `is_jitsi` per-event efeknya terbatas ke 2 tempat lain saja: `create()` (`[BSL-005]`) dan `action_join_video_call()` (`[BSL-007]`).

---

## Cara Pakai

ID `BSL-NNN` di dokumen ini dirujuk langsung oleh `03_MIGRATION_SPEC.md` (strategi teknis Step 3) dan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` (Step 5, tiap AC wajib sebut `BSL-NNN` yang diverifikasi). Jangan mengubah/memakai ulang ID yang sudah ada untuk klaim lain.
