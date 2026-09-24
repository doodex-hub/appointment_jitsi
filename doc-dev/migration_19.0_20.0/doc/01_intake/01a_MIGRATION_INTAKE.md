# Migration Intake — appointment_jitsi

**Step:** 1 — Intake & Scope
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-24
**Status:** ✔️ Lulus gate — dikonfirmasi dev (Kuncoro) via `AskUserQuestion` 2026-09-24

---

## 0. Folder Referensi — Dikonfirmasi

- [x] `native-source` (Community 19.0) — `D:\Kuncoro\doodex\repo\odoo19` (`.git/HEAD` = `refs/heads/19.0`, dibaca via `cat`, bukan command git)
- [x] `native-source-enterprise` (Enterprise 19.0) — `D:\Kuncoro\doodex\repo\enterprise19` (addons-only, `refs/heads/19.0`)
- [x] `native-target` (Community 20.0) — `D:\Kuncoro\doodex\repo\odoo20` (`refs/heads/20.0`) — path diberikan dev di instruksi sesi ini
- [x] `native-target-enterprise` (Enterprise 20.0) — `D:\Kuncoro\doodex\repo\enterprise20` (addons-only, `refs/heads/20.0`) — path diberikan dev di instruksi sesi ini. **WAJIB** karena `appointment` = Enterprise.
- [x] `third-party-*` — tidak ada dependency OCA/vendor (manifest `depends` cuma `base`, `appointment`, `calendar`; carry-over konfirmasi dev project 17→18 dan 18→19, tidak ada perubahan `depends` di `migration/19.0`).

**Verifikasi langsung dependency Enterprise di 20.0:**
- `enterprise20/appointment/__manifest__.py` → `'license': 'OEEL-1'`, `'version': '1.3'` — tetap Enterprise.
- `odoo20/addons/calendar` ada (Community, LGPL-3). `appointment` TIDAK ada di `odoo20/addons` — konsisten Enterprise-only.

### 0a. Konfirmasi Branch/Versi

- [x] **Source** = branch `migration/19.0` di repo ini (HEAD `7bfabb3`, hasil migrasi 18→19 yang UAT sign-off 2026-08-26). Tidak ada folder `source-codebase` terpisah — dibaca via `git show migration/19.0:<path>` (lihat CLAUDE.md §Folder).
- [x] **Target** = branch `migration/20.0` (dibuat saat conditioning dari `migration/19.0`). `git diff migration/19.0 migration/20.0 -- appointment_jitsi` = kosong saat Step 1 dimulai (kode identik, belum ada perubahan migrasi).
- [x] Versi Odoo semantik 19.0 → 20.0 — dari instruksi dev ("Lakukan migrasi 19→20").
- [x] Nama branch lama di dokumen 18→19 (`migration/19.0_target`) ≠ nama aktual (`migration/19.0`) — sudah dikoreksi di CLAUDE.md, dicatat di sini sebagai referensi.

### 0b. Gate: Path Absolut di `.claude/settings.json`

- [x] Deny-list `Edit` untuk `odoo19`, `enterprise19`, `odoo20`, `enterprise20`, `migration-tool/knowledge/**`, `migration-tool/templates/**` sudah terisi path nyata (diperbarui saat conditioning). Tidak ada placeholder `{{ABS_PATH_...}}` tersisa.
- [x] `migration-tool/migration-records/**` di-allow untuk ditulis (tempat `SUMMARY.md` project ini).

---

## Ringkasan untuk Review — Dikonfirmasi Dev 2026-09-24

1. **Sifat migrasi:** port kode saja — Step 7 N/A. ✔️ (jawaban dev)
2. **Source dibekukan** (`migration/19.0` tidak aktif dikembangkan) — `SYNC_POLICY.md` tidak dipakai. ✔️ (jawaban dev)
3. **Aset App Store dari branch rilis `19.0`/`staging/19.0` TIDAK di-port** (banner.gif 57 MB, icon.png, folder `assets`, `index.html` baru, key `images` manifest; juga penghapusan `tests/`/`LICENSE`/`LISEZMOI.md` di branch rilis). Di luar scope port kode; `tests/` tetap dipertahankan untuk Step 9. ✔️ (jawaban dev)
4. **G1 & Step 9 dijalankan AI sendiri (Mode C)** via Docker — compose project terpisah (`appointment_jitsi_migration_20`), port host 8096, image Odoo 20 dibangun dari source `odoo20` + `enterprise20` (belum ada image resmi `odoo:20.0`). ✔️ (jawaban dev)
5. **Bug-for-bug:** semua quirk 19.0 dipertahankan (F-01..F-13 dari 17→18, termasuk F-13/`BSL-015` email Jitsi tidak pernah aktif; MF-01 & MF-02 dari 18→19 diterima sebagai baseline 19.0) — kecuali perubahan wajib murni kompatibilitas 20.0.
6. **Peringatan dini (dari riset Step 1, detail di Step 2):** Odoo 20.0 menghapus `ir.config_parameter.get_param()`/`set_param()` (diganti `get_bool/get_int/get_float/get_str` + `set_*`). Modul memanggil `get_param` di `_compute_jitsi_link` → **wajib diubah** (kalau tidak, compute crash `AttributeError` saat create event). Juga: `calendar.event.access_token` di 20.0 punya `default=str(uuid4())`, `readonly=True`, constraint `unique(access_token)`; XML-ID `appointment.appointment_booked_mail_template` di-rename jadi `appointment.appointment_booking_mail_template`.
7. **Dokumen pelengkap:** tidak ada di luar `doc-dev/` (backfill 17.0, migrasi 17→18, migrasi 18→19) — carry-over, tidak ada dokumen baru sejak 2026-08-26 (asumsi; tidak ditanyakan terpisah di sesi ini). Test lama: `appointment_jitsi/tests/test_appointment_jitsi.py` (13 test, lahir dari backfill 17.0, PASS 13/13 di 19.0).
8. **Constraint:** tidak ada deadline khusus; owner Kuncoro. **Instruksi dev sesi ini:** jalan terus sampai Step 9 lulus gate, **STOP WAJIB sebelum Step 10** (slot browser/Docker dibatasi — MF-46), laporkan "siap Step 10, menunggu slot".

---

## 1. Modul & Scope

- Modul: `appointment_jitsi` (single module).
- Deskripsi: integrasi Jitsi Meet ke `calendar.event` — link Jitsi per event (berbasis `access_token`) di field `jitsi_link` + menimpa `videocall_location`; setting global di Settings → Calendar.

## 2. Dependency Map (auto-scan `git show migration/19.0:appointment_jitsi/__manifest__.py`)

| Dependency | Tipe | Ada di 20.0? | Catatan |
|---|---|---|---|
| `base` | Native Community | Ya | **BREAKING kandidat:** `ir.config_parameter` API baru (lihat poin 6 di atas). `ir.model.access.csv` → `ir.access.csv` (knowledge 19-to-20) — modul punya file `security/ir.model.access.csv` header-only yang TIDAK terdaftar di manifest `data` → kemungkinan N/A, cek Step 2. |
| `calendar` | Native Community | Ya | `access_token` berubah definisi (default/readonly/unique), `_set_discuss_videocall_location()` sekarang lewat `_calendar_event_ensure_token()`. View `calendar.res_config_settings_view_form` + `setting#sync_google_calendar_setting` masih ada. |
| `appointment` | **Native Enterprise (OEEL-1)** | Ya (`enterprise20/appointment`) | Template `appointment_booked_mail_template` → `appointment_booking_mail_template` (rename XML-ID). Hanya dirujuk oleh `data/mail_template_data.xml` (TIDAK di-load, `BSL-015`) dan test `test_qa_s01`. |

## 2b. Struktur & Fitur Modul

| Fitur | Ada? | Lokasi/bukti | Fase Step 6 |
|---|---|---|---|
| Controllers aktif | Tidak | `controllers/appointment.py` 100% comment (`BSL-016`) | D1 N/A |
| Assets/JS/Owl/SCSS | Tidak | Tidak ada `static/src/`, tidak ada key `assets` | D2/E/F N/A |
| Model baru | Tidak | Hanya `_inherit` `calendar.event` + `res.config.settings` | B2 N/A |
| View | 1 inherit | `views/calendar_views.xml` (settings form + 1 act_window orphan `BSL-022`) | C1/C2 |
| Data | 0 terdaftar | `data/mail_template_data.xml` tidak di manifest (`BSL-015`) | — |
| Tests | 13 `TransactionCase` | `tests/test_appointment_jitsi.py` | G1/G2 |

## 3. Sifat Migrasi

- [x] Port kode saja — **dikonfirmasi dev 2026-09-24**
- [ ] Upgrade instance

## 4. Baseline Spec / Characterization Test (gate)

- [x] Spec lama: `doc-dev/migration_18.0_19.0/doc/01_intake/01b_BASELINE_SPEC.md` (BSL-001..022), diverifikasi lewat Step 9 (13/13 PASS) + Step 10 (QA 5/5) migrasi 18→19 terhadap kode 19.0 yang SAMA byte-for-byte dengan `migration/19.0` sekarang.
- [x] Test lama: `appointment_jitsi/tests/test_appointment_jitsi.py` (13 test, di repo ini; 2 assertion diupdate di 18→19 per MF-01).
- [x] `01b_BASELINE_SPEC.md` diisi — lihat file terpisah.

### 4a. Dokumen Pelengkap Lain

- [x] Tidak ada dokumen di luar `doc-dev/` (carry-over konfirmasi dev project sebelumnya; tidak ditanyakan terpisah di sesi ini — koreksi kalau ada).

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak — dibekukan (**dikonfirmasi dev 2026-09-24**).

## 5. Scope Boundary

- Tetap identik: seluruh behavior `01b_BASELINE_SPEC.md` (BSL-001..023), bug-for-bug.
- Sengaja diubah: **hanya** perubahan wajib kompatibilitas 20.0 (dicatat di `03_MIGRATION_SPEC.md` + `FINDINGS.md`).
- Di luar scope (keputusan dev): aset App Store branch rilis 19.0.

## 6. Constraint

- Deadline: tidak ada. Owner: Kuncoro.
- STOP wajib sebelum Step 10 (instruksi dev sesi ini).
