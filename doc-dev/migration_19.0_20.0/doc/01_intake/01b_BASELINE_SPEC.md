# Baseline Spec — appointment_jitsi

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di **19.0** — bukan bagaimana diimplementasikan.
**Tanggal:** 2026-09-24
**Status:** ✔️ Lulus gate (bersama `01a`, dikonfirmasi dev 2026-09-24)
**Sumber:** `doc-dev/migration_18.0_19.0/doc/01_intake/01b_BASELINE_SPEC.md` (BSL-001..022) + `doc-dev/migration_18.0_19.0/doc/FINDINGS.md` (MF-01, MF-02) + cross-check langsung ke kode `migration/19.0` (`git show migration/19.0:appointment_jitsi/...`) dan native 19.0 (`odoo19`, `enterprise19`). Kode `migration/19.0` identik dengan yang lulus Step 9 (13/13) & Step 10 (5/5) migrasi 18→19.

> Ini **sumber kebenaran** untuk `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` dan testing Step 9/10/11 — BUKAN `03_MIGRATION_SPEC.md`.

---

## Provenance Tag

`[MATCH]` = klaim spec 18→19 dicek ulang ke kode 19.0 aktual dan cocok (plus sudah terbukti lewat test nyata di 19.0). `[NO-SPEC]` = klaim baru dari baca kode, belum ada di spec sebelumnya. Format: `[BSL-NNN] [TAG] (ref: BSL-NNN 18.0→19.0)`. Penomoran ID sengaja SAMA dengan dokumen 18→19 supaya traceable; ID baru mulai `BSL-023`.

---

## Ringkasan untuk Review

Tally: 23 klaim — 22 `[MATCH]`, 1 `[NO-SPEC]` (`BSL-023`), 0 `[GAP]`.

Poin paling kritis untuk migrasi 20.0:
1. **`[BSL-015]`** — `data/mail_template_data.xml` TIDAK terdaftar di manifest → email Jitsi tidak pernah aktif. **Tetap tidak didaftarkan di 20.0.**
2. **`[BSL-006]`/`[BSL-014]`/`[BSL-023]`** — logic aktif/tidak Jitsi sepenuhnya dari `ir.config_parameter` global dibaca via `get_param()` (truthy string). API ini **dihapus di 20.0** — perlu padanan yang mempertahankan observable behavior (lihat Step 2/3).
3. **`[BSL-005]`/`[BSL-009]`** — baseline 19.0 = behavior SETELAH MF-01: cabang `'is_jitsi' in values` di `create()` tidak pernah terpicu (values selalu list). `access_token` terisi dari mekanisme core, nilai `access_token` kiriman caller lolos apa adanya.
4. **`[BSL-010]`** — urutan akses `jitsi_link` vs `videocall_location` menentukan hasil. Port apa adanya.
5. **`[BSL-020]`** — field per-event `is_jitsi` tidak dipakai di compute link.

---

## 1. Tujuan Modul

Menambahkan integrasi Jitsi Meet ke `calendar.event`: link Jitsi unik per event (berbasis `access_token`), disimpan di `jitsi_link` dan ditulis juga ke `videocall_location`, supaya tombol "Join" standar mengarah ke Jitsi, bukan Odoo Discuss. (Penyisipan link ke email — lihat `[BSL-015]` — tidak pernah aktif.)

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `calendar.event` (`_inherit`) | Field `jitsi_link`/`is_jitsi`, compute link, `action_join_video_call()`, `generate_jitsi_link()`/`clear_jitsi_link()`, override `create()` |
| `res.config.settings` (`_inherit`) | Toggle global `is_jitsi` (`is_jitsi_param`) + `company_param` (Many2one `res.company`) |

Tidak ada model baru; `security/ir.model.access.csv` header-only dan TIDAK terdaftar di manifest.

## 3. Field dengan Makna Bisnis

### calendar.event
- `jitsi_link` (Text, compute `_compute_jitsi_link`, `store=True`, `copy=True`)
- `is_jitsi` (Boolean, default False) — lihat `[BSL-020]`

### res.config.settings
- `is_jitsi` (Boolean, `config_parameter='is_jitsi_param'`)
- `company_param` (Many2one `res.company`, `config_parameter='company_param'`, default `self.env.company`)

## 4. Business Workflow

- `[BSL-001]` `[MATCH]` (ref: BSL-001) Admin: Settings → Calendar → blok "Jitsi Configuration" (setelah "Google Calendar"), centang "Enable Jitsi Integration", pilih "Company" (field muncul hanya saat dicentang, `required`).
- `[BSL-002]` `[MATCH]` (ref: BSL-002) Kalau `is_jitsi_param` truthy: event yang di-compute mendapat `jitsi_link` = `videocall_location` = `https://meet.jit.si/{company}/{company}-{access_token}`. Kalau tidak: `_set_discuss_videocall_location()` core (link Discuss `.../calendar/join_videocall/{token}`).
- `[BSL-003]` `[MATCH]` (ref: BSL-003) User membuat/mengedit event, "Join" lewat `action_join_video_call`.
- `[BSL-004]` `[MATCH]` (ref: BSL-004) Peserta appointment berharap email berisi link Jitsi — tidak terwujud (`[BSL-015]`).

## 5. Server-Side Logic dengan Side Effect

- `[BSL-005]` `[MATCH]` (ref: BSL-005 + MF-01 18→19) **create:** override `@api.model def create(self, values)` — di 19.0 di-route ke `model_create_multi`, `values` SELALU list → `'is_jitsi' in values` selalu False → cabang set/reset `access_token` TIDAK PERNAH jalan (single maupun batch). Observable 19.0: `access_token` event baru terisi non-empty (dari mekanisme core/compute), nilai `access_token` yang dikirim caller lolos apa adanya (tidak direset False walau `is_jitsi=False`). Diverifikasi test `test_ac_02_01`/`test_ac_02_02` (PASS di 19.0).
- `[BSL-006]` `[MATCH]` (ref: BSL-006) **`_compute_jitsi_link`** (`@api.depends('access_token')`): baca `get_param('is_jitsi_param')` (truthy-string check) + `get_param('company_param')` (string id) → `res.company.search([('id','=',…)], limit=1)`; nama company atau literal `'Record not found'`. Aktif: per record, kalau `access_token` kosong → set `uuid4().hex`; tulis `jitsi_link` & `videocall_location`. Tidak aktif: `rec._set_discuss_videocall_location()` per record (jitsi_link tidak disentuh → tetap False/nilai lama).
- `[BSL-007]` `[MATCH]` (ref: BSL-007) **`action_join_video_call()`**: `act_url` ke `jitsi_link` kalau `self.is_jitsi` else `videocall_location`, `target: 'new'` (menimpa versi core yang selalu `videocall_location`).
- `[BSL-008]` `[MATCH]` (ref: BSL-008) `generate_jitsi_link()` (panggil compute) / `clear_jitsi_link()` (set False) — publik, tidak dirujuk UI.

## 6. Client-Side Behavior

- Backend: hanya inherit `calendar.res_config_settings_view_form` (xpath `//setting[@id='sync_google_calendar_setting']` after), `invisible="not is_jitsi"`. `jitsi_link` tidak tampil di view manapun.
- Tidak ada JS/Owl/asset. Tidak ada frontend/controller aktif.

## 7. Dependency Eksternal

- Eksplisit: `base`, `appointment`, `calendar`.
- `[BSL-021]` `[MATCH]` (ref: BSL-021) `appointment` = Enterprise OEEL-1 (dicek ulang tetap OEEL-1 di `enterprise20`). Test butuh source Enterprise.
- Menulis field core `calendar.event.videocall_location` dan `access_token` (`[BSL-010]`).
- `data/mail_template_data.xml` (tidak di-load) merujuk `calendar.calendar_template_meeting_update` dan `appointment.appointment_booked_mail_template`.

## 8. Quirk / Behavior Non-Obvious

- `[BSL-009]` `[MATCH]` (ref: BSL-009 + MF-01) `create()` batch: `'is_jitsi' in values` (list) → False; tidak ada token dari override. Observable: sama dengan single-create (`[BSL-005]`). (Ada/tidaknya warning log saat install bukan behavior bisnis — tidak diklaim di sini, dicatat apa adanya di log G1.)
- `[BSL-010]` `[MATCH]` (ref: BSL-010) `videocall_location` core (compute resmi `_compute_videocall_location`, depends `videocall_source`,`access_token`) ditulis imperatif dari `_compute_jitsi_link`. Akses `jitsi_link` dulu → Jitsi; akses `videocall_location` dulu → compute core (Discuss). Test `test_ac_03_01` (observasional).
- `[BSL-011]` `[MATCH]` (ref: BSL-011) Toggle `is_jitsi` via `write()` tidak memicu recompute.
- `[BSL-012]` `[MATCH]` (ref: BSL-012) `company_param` satu nilai global lintas company.
- `[BSL-013]` `[MATCH]` (ref: BSL-013) Nama company disisipkan dua kali, tidak di-slug/escape (spasi masuk mentah).
- `[BSL-014]` `[MATCH]` (ref: BSL-014) Uncheck setting → 19.0 core `set_param(key, False)` MENGHAPUS row `ir.config_parameter` → `get_param` = False → fallback Discuss (F-01 ternyata bukan bug di 19.0 lewat jalur UI).
- `[BSL-015]` `[MATCH]` (ref: BSL-015) **PALING KRITIS.** Manifest `data` = `["views/calendar_views.xml"]` saja. Template email TIDAK pernah dioverride; body `appointment_booked_mail_template` hanya memuat link core `/calendar/meeting/join?token=` (test `test_qa_s01`).
- `[BSL-016]` `[MATCH]` (ref: BSL-016) Controller 100% comment-out; tidak ada route.
- `[BSL-017]` `[MATCH]` (ref: BSL-017) = `[BSL-008]`, tidak terhubung UI.
- `[BSL-018]` `[MATCH]` (ref: BSL-018) File `googleaeed8a7b9ec156e7.html` di root modul (tidak berhubungan dengan logic).
- `[BSL-019]` `[MATCH]` (ref: BSL-019) Label "Company" `company_param` bentrok dengan `company_id` — warning saat install, kosmetik.
- `[BSL-020]` `[MATCH]` (ref: BSL-020) `is_jitsi` per-event tidak dicek di compute; hanya dipakai di `create()` (tidak efektif, `[BSL-005]`) dan `action_join_video_call()`.
- `[BSL-021]` — lihat §7.
- `[BSL-022]` `[MATCH]` (ref: BSL-022 + MF-02) `ir.actions.act_window` `res_config_settings_action` orphan (tidak dirujuk apapun), `target=current` (fix MF-02 di 19.0).
- `[BSL-023]` `[NO-SPEC]` (ref: —) **Baru dicatat 2026-09-24 dari baca kode.** Karena `get_param` mengembalikan string mentah dan dicek truthy, NILAI STRING APAPUN yang tersimpan di `is_jitsi_param` (termasuk `"False"`/`"0"` yang di-set manual via System Parameters atau `set_param('is_jitsi_param', 'False')`) MENGAKTIFKAN Jitsi di 19.0. Hanya "row tidak ada" yang menonaktifkan. Jalur UI Settings (uncheck) tidak memicu quirk ini karena menghapus row (`[BSL-014]`). Test helper `_disable_jitsi()` (`set_param(..., 'False')`) di 19.0 sebenarnya TIDAK menonaktifkan Jitsi — test yang memakainya (`test_ac_02_03`, `test_ac_04_01`) hanya observasional (tanpa assertion), jadi tetap PASS.

---

## Cara Pakai

ID `BSL-NNN` dirujuk `03_MIGRATION_SPEC.md` dan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`. Jangan dipakai ulang untuk klaim lain.
