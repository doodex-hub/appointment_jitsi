# Diff & Compatibility Analysis — appointment_jitsi

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-24
**Status:** ✅ Selesai
**Ref:** `01_intake/01a_MIGRATION_INTAKE.md`, `01_intake/01b_BASELINE_SPEC.md`, `migration-tool/knowledge/`

---

## 0. Knowledge Base Check

| Sumber | Ada entry? | Lokasi / relevansi |
|---|---|---|
| `version-diffs/19-to-20.md` | Ya | 6 baris: `/web/session/logout` GET 405, `logOutItem` tidak di-export, `ir.model.access.csv`→`ir.access.csv`, `res.partner` self-write, `computeOptionalActiveFields`, fitur pin `mail.message`. **Semua N/A** untuk modul ini — grep `session/logout`, `log_out`, `user_menu_items`, `computeOptionalActiveFields`, `pinned_at` = 0 match (modul tanpa JS). `ir.model.access.csv` modul header-only & tidak di manifest → N/A (DIFF-10). |
| `migration-records/pos-margin-sale_19.0_20.0` (kandidat, belum dikurasi) | Ya | `_to_store()` dihapus, `product_variant_easy_edit_view` dihapus — grep 0 match, N/A. |
| `dependency-compat/appointment/` | Hanya `18-to-19.md` | Tidak ada data point 19→20 → analisis baru (DIFF-02, DIFF-08). |
| `dependency-compat/calendar/` | Tidak ada | Analisis baru. |
| `dependency-compat/base` (`ir.config_parameter`) | Tidak ada | **Analisis baru — temuan terbesar project ini (DIFF-01).** |

## 0b. Gate Community vs Enterprise

- [x] §2 intake punya dependency Enterprise (`appointment`).
- [x] `enterprise20/appointment` dicek langsung: masih ada, `license: OEEL-1`, tidak pindah ke Community (`odoo20/addons/appointment` tidak ada).
- [x] Kolom "Sumber" di §1 menyebut clone mana yang dicek.

## 0c. Gate Transitive Dependency

- [x] Tidak ada `depends` yang dihapus → N/A.

## 0d. Gate Grep Menyeluruh

- [x] Grep seluruh `appointment_jitsi/` (termasuk `tests/`, `data/`, di luar `static/`) untuk simbol dari knowledge base DAN simbol breaking yang ditemukan di §1: `get_param`/`set_param` (1 file produksi, 1 file test — 7 kemunculan), `appointment_booked_mail_template` (data tidak di-load + 1 test), `access_token` (compute + create + test). Tiap kemunculan dipetakan ke DIFF di §1.

## 0e. Gate Silent-Regression per Tipe Override

| Override | Kategori | Hasil cek |
|---|---|---|
| `calendar.event._compute_jitsi_link` (method baru, `@api.depends('access_token')`, bukan override) | (a) entry point compute | Dipicu dari `access_token` — di 20.0 `access_token` punya `default` di `calendar` (dulu di `appointment`), jadi compute tetap terpicu saat create. Isi body memanggil `get_param` → **crash** (DIFF-01), bukan silent. |
| `calendar.event.create` (`@api.model`) | (a) | Routing `api.model`→`model_create_multi` identik 19↔20 (`odoo/orm/decorators.py` `model()`), return type sama. Behavior MF-01 18→19 tetap. |
| `calendar.event.action_join_video_call` (override tanpa `super()`) | (a) | Core 20.0 tetap return `act_url` ke `videocall_location` `target=new`; override menimpa sama seperti 19.0. Entry point: tombol "Join" native — masih memanggil method publik yang sama (`action_join_video_call` di view calendar). Tidak berubah. |
| `calendar.event._set_discuss_videocall_location` (dipanggil, bukan override) | (a) | Masih ada, sekarang lewat `_calendar_event_ensure_token()` (`sudo().write`) — behavior observable sama (link Discuss + token). |
| Tulis imperatif `videocall_location` dari compute lain (`BSL-010`) | (a) | **Jalur pemanggilan berubah:** `calendar.event.create()` 20.0 BARU memanggil `_ensure_videocall_channels()` yang `flush_recordset(['videocall_location'])` di akhir create (DIFF-04) — urutan compute `videocall_location` vs `jitsi_link` saat create bisa bergeser. Wajib diverifikasi NILAI di G1/Step 9, bukan sekadar "tidak error". |
| `res.config.settings` field `config_parameter` | (a) | `set_values()` 20.0 dirombak: boolean → `set_bool` (simpan string `"True"`/`"False"`, TIDAK lagi hapus row), many2one → `set_int`. Lihat DIFF-01/DIFF-11. |
| View inherit `calendar.res_config_settings_view_form` | (b) | xpath `//setting[@id='sync_google_calendar_setting']` masih ada di `odoo20/addons/calendar/views/res_config_settings_views.xml:17`. |
| (c) Owl patch / (d) registry | — | N/A — modul tanpa JS. |

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `models/calendar_event.py` `_compute_jitsi_link`: `self.env['ir.config_parameter'].sudo().get_param` (×2); `tests/`: `set_param`×3, `get_param`×2 | `ir.config_parameter.get_param()`/`set_param()` | **Dihapus.** `odoo20/odoo/addons/base/models/ir_config_parameter.py` (173 baris) hanya punya `get_bool/get_int/get_float/get_str` + `set_bool/set_int/set_float/set_str` (typed). Tidak ada alias/shim (grep `def get_param` di `odoo20/odoo` + `odoo20/addons` = 0; 12 pemanggil native sisa di addon lain = sisa belum dimigrasi native, bukan bukti API masih ada). | **Kritis (crash).** `_compute_jitsi_link` dijalankan saat create event apapun → `AttributeError` → SEMUA pembuatan `calendar.event` gagal setelah modul terpasang. Semantik juga berubah: 19.0 uncheck setting = row dihapus; 20.0 = row berisi `"False"`. Kalau modul membaca sebagai string truthy (`get_str`), uncheck di UI TIDAK mematikan Jitsi (F-01 muncul lagi). → pakai `get_bool('is_jitsi_param')` + `get_int('company_param')`. Deviasi tersisa: `[BSL-023]` (string non-kosong apapun = aktif) tidak bisa dipertahankan bersamaan dengan `[BSL-014]` → **MF-01**. | analisis baru, `odoo20` + `odoo19` (`ir_config_parameter.py`, `res_config.py`) |
| DIFF-02 | `_compute_jitsi_link` cabang `if not rec.access_token: rec.access_token = uuid4().hex`; test `test_ac_02_02` kirim `access_token` literal | `calendar.event.access_token` | **Definisi berubah.** 19.0: `calendar` = `Char(store, copy=False, index)`, default `str(uuid4())` + `readonly` datang dari `appointment` (`enterprise19/appointment/models/calendar_event.py:76-80`). 20.0: default `str(uuid4())` + `readonly=True` pindah ke `calendar` (`odoo20/.../calendar_event.py:189`), plus **constraint baru `unique(access_token)`** (`:327`) dan helper `_calendar_event_ensure_token()`. | Rendah. Default & readonly efektif sama (event dengan `appointment` terpasang sudah begitu di 19.0). Modul tidak pernah meng-assign token duplikat (hanya `uuid4().hex` / `False`). Test `test_ac_02_02` pakai literal unik per transaksi → aman. Tidak perlu ubah kode. | analisis baru, `odoo20`, `enterprise19`, `enterprise20` |
| DIFF-03 | `create()` `@api.model` | `odoo/orm/decorators.py` `model()`/`model_create_multi()` | Tidak berubah (19↔20 sama, cuma syntax generic `[C: Callable]`). | Tidak ada — `[BSL-005]`/`[BSL-009]` (baseline pasca MF-01 18→19) tetap. | analisis baru, `odoo19`/`odoo20` |
| DIFF-04 | Tulis imperatif `videocall_location` di `_compute_jitsi_link` (`[BSL-010]`) | `calendar.event.create()` → `_ensure_videocall_channels()` (BARU di 20.0; 0 kemunculan di `odoo19`) | **Behavior berubah.** Akhir `create()` sekarang `flush_recordset(['videocall_location'])` lalu membuat `discuss.channel` untuk event yang `videocall_source == 'discuss'` & belum lewat. | Sedang — belum bisa dipastikan statis: (1) urutan compute saat create bisa bergeser (core `_compute_videocall_location` dipaksa jalan lebih dulu), (2) event Jitsi mungkin tetap mendapat channel Discuss kalau saat flush `videocall_location` masih Discuss. Observable yang dijaga: setelah create dengan Jitsi aktif, `jitsi_link` & `videocall_location` = URL Jitsi (`test_ac_01_01`). Verifikasi empiris G1 → **MF-03**. Pembuatan channel Discuss sendiri = fitur native baru, bukan behavior modul. | analisis baru, `odoo20` |
| DIFF-05 | override `action_join_video_call()` | `calendar.event.action_join_video_call()` | Tidak berubah (`act_url`, `videocall_location`, `target=new`). | Tidak ada. | `odoo19`/`odoo20` |
| DIFF-06 | pemanggilan `_set_discuss_videocall_location()` | idem | Signature sama; implementasi pakai `_calendar_event_ensure_token()` (sudo write token kalau kosong). | Tidak ada perubahan observable (link Discuss format sama `…/calendar/join_videocall/{token}`). | `odoo20` |
| DIFF-07 | `views/calendar_views.xml` inherit `calendar.res_config_settings_view_form`, xpath `setting#sync_google_calendar_setting` | view native | Tidak berubah (XML-ID & `setting id` sama; atribut `documentation`/`help` masih dipakai native). | Tidak ada. | `odoo20` |
| DIFF-08 | `tests/test_qa_s01` `env.ref('appointment.appointment_booked_mail_template')`; `data/mail_template_data.xml` (tidak di-load) | `appointment` mail template | **Rename XML-ID** → `appointment.appointment_booking_mail_template` (`enterprise20/appointment/data/mail_template_data.xml:5`). Grep `appointment_booked_mail_template` di `odoo20`+`enterprise20` = 0 (tidak ada alias). Isi masih memuat `/calendar/meeting/join?token={{ object.sudo().access_token }}`. | Test `test_qa_s01` → `ValueError` di 20.0; wajib retarget ke XML-ID baru (intent test sama: body template "booked" tidak memuat `jitsi_link`). Data file tetap tidak di-load (`[BSL-015]`) → rujukan basinya dibiarkan apa adanya (bug-for-bug, tidak ada efek install). → **MF-02**. | analisis baru, `enterprise19`/`enterprise20` |
| DIFF-09 | `res_config_settings_action` `target=current` | `ir.actions.act_window.target` | Tidak berubah (`current` masih valid). | Tidak ada. | `odoo20` |
| DIFF-10 | `security/ir.model.access.csv` (header-only, TIDAK di manifest) | `ir.model.access` → `ir.access` | Berubah struktural (knowledge 19-to-20). | N/A — file tidak pernah di-load; dibiarkan apa adanya (port as-is, tidak menambah/menghapus file). | knowledge base |
| DIFF-11 | `res.config.settings.is_jitsi`/`company_param` (`config_parameter=`) | `res.config.settings.set_values()`/`get_values()` | Dirombak ke `match field.type` + typed setter/getter. Boolean & many2one tetap didukung. | Tidak ada perubahan deklarasi field. Efek ke penyimpanan → DIFF-01. | `odoo19`/`odoo20` `res_config.py` |
| DIFF-12 | `__manifest__.py` `version: 19.0.1.0.0` | — | Wajib prefix seri 20.0. | Bump ke `20.0.1.0.0`. | konvensi |

## 2. Kompatibilitas Dependency (OCA/Third-Party)

Tidak ada dependency OCA/third-party.

## 3. Temuan Baru — Migration Records

- [x] DIFF-01 (`get_param`/`set_param` dihapus + semantik boolean config param berubah) → kandidat `version-diff` di `migration-tool/migration-records/appointment_jitsi_19.0_20.0/SUMMARY.md`.
- [x] DIFF-02 (`calendar.event.access_token` default/readonly pindah ke `calendar` + unique) dan DIFF-04 (`_ensure_videocall_channels` di create) → kandidat `dependency-compat/calendar`.
- [x] DIFF-08 (rename `appointment_booked_mail_template`) → kandidat `dependency-compat/appointment` 19-to-20.

## 4. Ringkasan Risiko

| Item | Level | Catatan |
|---|---|---|
| DIFF-01 `get_param` dihapus | **Tinggi** (crash semua create event) | Fix wajib, murah. Deviasi kecil `[BSL-023]` (MF-01). |
| DIFF-04 flush `videocall_location` di create | Sedang | Tidak bisa dipastikan statis → G1/Step 9 (MF-03). |
| DIFF-08 rename template | Rendah (test-only) | MF-02. |
| DIFF-02 `access_token` unique/default | Rendah | Tidak perlu ubah kode; dipantau di G1. |
| Lainnya | Tidak ada | |
