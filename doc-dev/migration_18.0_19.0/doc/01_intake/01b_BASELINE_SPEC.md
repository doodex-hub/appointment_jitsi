# Baseline Spec — appointment_jitsi

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 18.0 — bukan bagaimana diimplementasikan.
**Tanggal:** 2026-08-26
**Sumber:** Direkonsiliasi dari `doc-dev/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md` (21 klaim `BSL-001`..`BSL-021`, sudah diverifikasi via dev testing Step 9 — 13/13 test PASS terhadap kode 18.0 — DAN QA testing Step 10 — 5/5 skenario Pass, termasuk reproduksi live quirk `BSL-010` — pada project migrasi 17.0→18.0) + cross-check langsung ke kode `source-codebase/appointment_jitsi/` (branch `migration/18.0`, commit `3a563b2`). Kode source **identik** dengan yang sudah diverifikasi test nyata di 18.0 — tidak ada perubahan sejak UAT sign-off 2026-08-24. Tidak ditemukan penyimpangan baru.

> Ini **sumber kebenaran** untuk `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` dan semua testing (step 9, 10, 11) — BUKAN `03_MIGRATION_SPEC.md`.

---

## Provenance Tag

Semua klaim di bawah bertag `[MATCH]` — sudah diverifikasi dua kali lipat dari project sebelumnya: (1) cross-check ke `FUNCTIONAL_SPEC.md`/`ACCEPTANCE_CRITERIA.md`/`FINDINGS.md` backfill 17.0, DAN (2) dev testing + QA testing nyata langsung di kode 18.0 (bukan cuma baca statis). Confidence tertinggi yang mungkin dicapai baseline spec tool ini. Format: `[BSL-NNN] [MATCH] (ref: BSL-NNN 17.0→18.0)`.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

Tally: 21 klaim, semua `[MATCH]` (0 `[GAP]`, 0 `[NO-SPEC]`) — baseline ini sudah lolos DUA siklus verifikasi nyata (backfill 17.0 + migrasi 17.0→18.0 lengkap dengan dev/QA testing), jauh lebih solid dari titik awal migrasi manapun.

Poin paling kritis untuk migrasi 19.0 (bug yang WAJIB dipertahankan, bukan diperbaiki):

1. **`[BSL-015]` PALING KRITIS** — override mail template (`data/mail_template_data.xml`) tidak terdaftar di manifest, fitur "link Jitsi di email" TIDAK PERNAH aktif sejak 17.0, dikonfirmasi tetap begitu di 18.0. **WAJIB tetap tidak terdaftar di manifest 19.0.**
2. **`[BSL-020]`** — field per-event `is_jitsi` tidak dipakai sama sekali di logic compute link — hanya setting global yang menentukan. Migrasi 19.0 harus mempertahankan pemisahan ini persis.
3. **`[BSL-010]`** — `jitsi_link`/`videocall_location` hasilnya bergantung urutan field mana yang diakses lebih dulu (side-effect compute yang menulis field lain tanpa redeclare). Quirk paling halus, sudah dikonfirmasi live via QA testing 18.0 — **WAJIB port apa adanya**, jangan "dibersihkan" saat Step 6.
4. **`[BSL-021]`** — dependency `appointment` berlisensi Enterprise (OEEL-1) — **dikonfirmasi ulang tetap Enterprise di 19.0** (lihat `01a_MIGRATION_INTAKE.md` §0, dicek langsung `enterprise19.0/odoo/addons/appointment/__manifest__.py`). Dev testing Step 9 nanti butuh akses `enterprise19.0` (folder gabungan Community+Enterprise, bukan git repo).
5. Sisa 17 klaim (`[BSL-001]`-`[BSL-009]`, `[BSL-011]`-`[BSL-014]`, `[BSL-016]`-`[BSL-019]`) — behavior lebih straightforward, detail di §4/5/8 di bawah, tidak berubah dari dokumentasi 17.0→18.0.

**Perhatian khusus Step 2 (belum bisa dijawab di sini, baru bisa dijawab setelah diff analysis):** apakah field core `calendar.event.access_token`/`videocall_location`, method `_compute_videocall_location()`/`_set_discuss_videocall_location()`, dan XML-ID `calendar.res_config_settings_view_form`/`appointment.appointment_booked_mail_template`/`calendar.calendar_template_meeting_update` yang jadi tumpuan `BSL-006`/`BSL-007`/`BSL-021` masih ada dengan signature/nama yang sama di Odoo 19.0 — belum diverifikasi di dokumen ini, itu tugas `02_DIFF_ANALYSIS.md`.

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
- `[BSL-001]` `[MATCH]` (ref: BSL-001 17.0→18.0) Admin membuka **Settings → Calendar → Jitsi Configuration**, mencentang "Enable Jitsi Integration", memilih "Company" yang namanya dipakai di URL room Jitsi.
- `[BSL-002]` `[MATCH]` (ref: BSL-002 17.0→18.0) Kalau `ir.config_parameter('is_jitsi_param')` truthy DAN `company_param` menunjuk company valid: setiap event yang di-compute (`access_token` berubah/baru) mendapat `jitsi_link`/`videocall_location` format `https://meet.jit.si/{company}/{company}-{access_token}`. Kalau tidak aktif, event jatuh ke `_set_discuss_videocall_location()` bawaan Odoo (link Discuss standar).
- `[BSL-003]` `[MATCH]` (ref: BSL-003 17.0→18.0) User membuat/mengedit `calendar.event` dengan `is_jitsi=True`, mengharapkan link otomatis terisi dan bisa "Join" dari tombol standar (`action_join_video_call`) atau link di email.
- `[BSL-004]` `[MATCH]` (ref: BSL-004 17.0→18.0) Peserta appointment yang membuat janji lewat Appointment MENGHARAPKAN menerima email (`appointment_booked_mail_template`) dengan link Jitsi — **tapi lihat `[BSL-015]`: ekspektasi ini tidak pernah terwujud, dikonfirmasi tetap begitu di 18.0.**

## 5. Server-Side Logic dengan Side Effect

### calendar.event
- `[BSL-005]` `[MATCH]` (ref: BSL-005 17.0→18.0) **create (single dict):** kalau key `is_jitsi` ada di `values` dan truthy → `access_token` di-set UUID baru sebelum `super().create()`. Kalau ada dan falsy → `access_token` di-set eksplisit `False`, menimpa `access_token` apapun yang sudah dikirim caller di dict yang sama.
- `[BSL-006]` `[MATCH]` (ref: BSL-006 17.0→18.0) **`_compute_jitsi_link` (`@api.depends('access_token')`):** baca `is_jitsi_param` + `company_param` global via `ir.config_parameter`. Kalau aktif: loop tiap record, generate `access_token` UUID kalau belum ada, tulis `jitsi_link` DAN `videocall_location` dengan format yang sama. Kalau tidak aktif: panggil `_set_discuss_videocall_location()` (core). `is_jitsi_param` yang di-uncheck admin membuat Odoo core MENGHAPUS row `ir.config_parameter` (bukan simpan string `"False"`) — dikonfirmasi via test nyata di 17.0 dan 18.0.
- `[BSL-007]` `[MATCH]` (ref: BSL-007 17.0→18.0) **`action_join_video_call()`:** return `ir.actions.act_url` ke `self.jitsi_link` kalau `self.is_jitsi` true, else ke `self.videocall_location`. `target: 'new'`.
- `[BSL-008]` `[MATCH]` (ref: BSL-008 17.0→18.0) **`generate_jitsi_link()`/`clear_jitsi_link()`:** method publik tersedia di model, TAPI tidak direferensikan di `views/calendar_views.xml` manapun sebagai button/server action.

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
- `[BSL-021]` `[MATCH]` (ref: BSL-021 17.0→18.0) `appointment` (dan dependency-nya, `web_gantt`) berlisensi Enterprise (`OEEL-1`) — TIDAK tersedia di image Community publik. **Dikonfirmasi ulang tetap Enterprise di 19.0** (lihat `01a_MIGRATION_INTAKE.md` §0). Dev testing (Step 9) modul ini WAJIB akses source Odoo Enterprise (lokal: `enterprise19.0`, folder gabungan).
- Modul menulis langsung ke field core `calendar.event.videocall_location` dan `calendar.event.access_token` (bukan field modul sendiri) — lihat `[BSL-010]`.
- Modul override 2 mail template BAWAAN (bukan mail template baru): `calendar.calendar_template_meeting_update` dan `appointment.appointment_booked_mail_template`, via `data/mail_template_data.xml` yang memakai pola `noupdate` flip (unlock → write → lock kembali).

## 8. Quirk / Behavior Non-Obvious

- `[BSL-009]` `[MATCH]` (ref: BSL-009 17.0→18.0) `create()` di-override dengan `@api.model` (single-record signature), bukan `@api.model_create_multi`. Odoo memanggil `create()` dengan LIST of dict untuk skenario batch (termasuk recurring event via `calendar.recurrence`) — `'is_jitsi' in values` pada input list mengecek keanggotaan string di LIST (bukan di tiap dict), hampir selalu `False`. Odoo mencetak WARNING resmi saat install modul ini soal ini (dikonfirmasi tetap muncul di 18.0).
- `[BSL-010]` `[MATCH]` (ref: BSL-010 17.0→18.0) `videocall_location` adalah field CORE `calendar.event` dengan compute resminya sendiri (`_compute_videocall_location`, dependency berbeda). Modul ini menulis field itu secara IMPERATIF dari `_compute_jitsi_link` (compute BEDA, depends BEDA — cuma `access_token`) tanpa redeclare field. Kalau `jitsi_link` DIAKSES DULU → override Jitsi berlaku. Kalau `videocall_location` DIAKSES DULU tanpa pernah menyentuh `jitsi_link` → compute resmi core yang jalan, override Jitsi TIDAK PERNAH terjadi. **Dikonfirmasi live via QA testing 18.0** (bukan cuma dev testing) — quirk paling halus di modul ini.
- `[BSL-011]` `[MATCH]` (ref: BSL-011 17.0→18.0) `@api.depends('access_token')` tidak menyertakan `is_jitsi` — toggle `is_jitsi` True/False pada event EXISTING lewat `write()` tidak memicu recompute `jitsi_link`/`videocall_location` sama sekali.
- `[BSL-012]` `[MATCH]` (ref: BSL-012 17.0→18.0) `company_param` adalah SATU `ir.config_parameter` GLOBAL, bukan per-company/per-event. Di setup multi-company, SEMUA room Jitsi lintas company memakai nama company yang sama.
- `[BSL-013]` `[MATCH]` (ref: BSL-013 17.0→18.0) Format URL: `f"{jitsi_base_url}/{company_name}/{company_name}-{access_token}"` — nama company disisipkan DUA KALI (folder + prefix room), tidak di-slug/escape.
- `[BSL-014]` `[MATCH]` (ref: BSL-014 17.0→18.0) `is_jitsi_param` disimpan/dihapus sebagai row `ir.config_parameter` (bukan string `"False"` truthy) — bukan bug, dikonfirmasi via eksekusi nyata di 17.0 dan 18.0. **Perlu diverifikasi ulang mekanisme core ini saat dev testing 19.0** (Step 2/9) — bisa saja berbeda di versi baru walau kemungkinan kecil.
- `[BSL-015]` `[MATCH]` (ref: BSL-015 17.0→18.0) **PALING KRITIS.** `__manifest__.py` `data` HANYA berisi `["views/calendar_views.xml"]` — `data/mail_template_data.xml` tidak terdaftar. Override `appointment_booked_mail_template` TIDAK PERNAH berlaku pada instalasi manapun yang memakai kode ini. **Dikonfirmasi tetap begitu di 18.0** (dev testing Step 9 project sebelumnya, `muncul_di_body=False`). Keputusan dev: dipertahankan apa adanya di 19.0 juga — manifest TIDAK mendaftarkan file ini.
- `[BSL-016]` `[MATCH]` (ref: BSL-016 17.0→18.0) `controllers/appointment.py` seluruh isinya di-comment-out (route custom `/calendar/join_jitsi/<token>`). `controllers/__init__.py` tetap `from . import appointment` (no-op, tidak error). Tidak ada route HTTP tambahan yang benar-benar terdaftar dari modul ini.
- `[BSL-017]` `[MATCH]` (ref: BSL-017 17.0→18.0) `generate_jitsi_link()`/`clear_jitsi_link()` — lihat `[BSL-008]` — tidak terhubung UI manapun.
- `[BSL-018]` `[MATCH]` (ref: BSL-018 17.0→18.0) File `googleaeed8a7b9ec156e7.html` (verifikasi Google Search Console) ikut ter-commit di root folder modul — tidak berhubungan dengan logic Odoo apapun.
- `[BSL-019]` `[MATCH]` (ref: BSL-019 17.0→18.0) Label field "Company" pada `company_param` (modul ini) bentrok dengan `company_id` (`base_setup`) di form `res.config.settings` yang sama — Odoo mencetak WARNING resmi saat instalasi. Kosmetik, tidak ada dampak fungsional.
- `[BSL-020]` `[MATCH]` (ref: BSL-020 17.0→18.0) Field per-event `is_jitsi` TIDAK PERNAH dicek di dalam `_compute_jitsi_link` — HANYA `ir.config_parameter('is_jitsi_param')` GLOBAL yang menentukan Jitsi/Discuss untuk SEMUA event. Field `is_jitsi` per-event efeknya terbatas ke 2 tempat lain saja: `create()` (`[BSL-005]`) dan `action_join_video_call()` (`[BSL-007]`).

- `[BSL-022]` `[NO-SPEC]` (ref: —) **BARU ditemukan Step 6/G1 2026-08-26 — GAP di baseline 17.0->18.0 sebelumnya, TIDAK pernah terdokumentasikan/tereksekusi test manapun.** `views/calendar_views.xml` baris 4-11 mendefinisikan `<record id="res_config_settings_action" model="ir.actions.act_window">` (action "Configuration" ke `res.config.settings` form) — XML-ID ini TIDAK PERNAH direferensikan menu/button/kode Python manapun di modul ini (dikonfirmasi grep menyeluruh) — dead code orphaned, pola yang sama seperti `controllers/appointment.py` (`[BSL-016]`) dan `generate_jitsi_link()`/`clear_jitsi_link()` (`[BSL-008]`/`[BSL-017]`). Karena tidak pernah dipanggil UI manapun dan 13 test existing juga tidak pernah mengeksekusinya, klaim ini baru ketahuan lewat instalasi nyata di 19.0 (lihat `MF-02`), bukan dari baca statis biasa.

---

## Cara Pakai

ID `BSL-NNN` di dokumen ini dirujuk langsung oleh `03_MIGRATION_SPEC.md` (strategi teknis Step 3) dan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` (Step 5, tiap AC wajib sebut `BSL-NNN` yang diverifikasi). Jangan mengubah/memakai ulang ID yang sudah ada untuk klaim lain. Penomoran ID ini **direset ulang dari 001** untuk dokumen 18.0→19.0 ini (bukan lanjut dari 022) — tapi tiap klaim membawa referensi eksplisit `(ref: BSL-NNN 17.0→18.0)` ke ID asalnya supaya traceable lintas project migrasi.
