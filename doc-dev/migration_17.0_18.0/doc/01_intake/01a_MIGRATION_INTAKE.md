# Migration Intake — appointment_jitsi

**Step:** 1 — Intake & Scope
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Status:** 🔄 Draft — menunggu review user untuk menutup gate

---

## 0. Folder Referensi — Dikonfirmasi Dev (2026-08-24)

- [x] `native-target` (Community 18.0) — `D:\Kuncoro\doodex\repo\odoo18` (clone `odoo/odoo`, branch `18.0`, sudah ada di disk)
- [x] `native-source` (Community 17.0) — `D:\Kuncoro\doodex\repo\odoo17` (clone `odoo/odoo`, branch `17.0`, sudah ada di disk)
- [x] `native-target-enterprise` — **dikonfirmasi WAJIB.** Auto-scan manifest menemukan dependency `appointment`; dicek langsung isi folder: `appointment` ADA di `D:\Kuncoro\doodex\repo\enterprise18\appointment`, TIDAK ADA di `D:\Kuncoro\doodex\repo\odoo18\addons` → Enterprise, bukan Community. Path: `D:\Kuncoro\doodex\repo\enterprise18` (branch `18.0`).
- [x] `native-source-enterprise` — sama, dikonfirmasi ada di `D:\Kuncoro\doodex\repo\enterprise17\appointment` (branch `17.0`).
- [x] `third-party-source`/`third-party-target` — dev dikonfirmasi eksplisit: **tidak ada** dependency OCA/vendor. Manifest cuma depend ke `base`/`appointment`/`calendar` (semua Odoo native). Tidak perlu connect folder ini.

### 0a. Konfirmasi Branch/Versi `source-codebase` & `target-codebase`

- [x] Folder `source-codebase` — `D:\Kuncoro\doodex\repo\appointment-jitsi-migration-18-source`, branch **`migration/17.0_source`** (baru dibuat 2026-08-24 dari `backfill/17.0`, commit `6f840bd`). Dev eksplisit memilih membuat branch+clone baru (bukan reuse folder `appointment-jitsi-17` yang sudah ada) untuk menjaga source-codebase project ini terisolasi/bersih dari folder kerja lain.
- [x] Folder `target-codebase` — `D:\Kuncoro\doodex\repo\appointment-jitsi-migration-18` (repo ini), branch **`migration/18.0_target`** (baru dibuat 2026-08-24 dari `backfill/17.0`, commit `6f840bd` — titik awal sama dengan source-codebase, kode migrasi 18.0 akan ditulis di atas branch ini).
- [x] Dikonfirmasi dua clone fisik terpisah (bukan symlink/alias) — `git clone` lokal dijalankan dari `target-codebase` ke folder baru, origin di-set ulang ke `https://kuncoroddx@github.com/doodex-hub/appointment_jitsi.git` (URL bersih, tanpa token).
- [x] **Versi Odoo semantik, dikonfirmasi eksplisit dev:** 17.0 → 18.0.

### 0b. Gate: Path Absolut di `.claude/settings.json`

- [x] `ABS_PATH_SOURCE_CODEBASE` = `D:/Kuncoro/doodex/repo/appointment-jitsi-migration-18-source`
- [x] `ABS_PATH_MIGRATION_TOOL` = `D:/Kuncoro/doodex/repo/migration-tool-project/migration-tool`
- [x] `ABS_PATH_NATIVE_TARGET` = `D:/Kuncoro/doodex/repo/odoo18`
- [x] `ABS_PATH_NATIVE_SOURCE` = `D:/Kuncoro/doodex/repo/odoo17`
- [x] `ABS_PATH_NATIVE_TARGET_ENTERPRISE` = `D:/Kuncoro/doodex/repo/enterprise18` (dipakai — dependency `appointment` Enterprise)
- [x] `ABS_PATH_NATIVE_SOURCE_ENTERPRISE` = `D:/Kuncoro/doodex/repo/enterprise17` (dipakai — sama alasan)
- [x] `ABS_PATH_THIRD_PARTY_SOURCE`/`ABS_PATH_THIRD_PARTY_TARGET` — dihapus seluruhnya dari `deny` list (dikonfirmasi tidak dipakai)

Gate ini **selesai** — tidak ada `{{ABS_PATH_...}}` literal tersisa di `.claude/settings.json`.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Versi & branch:** migrasi 17.0 → 18.0 dikonfirmasi. `target-codebase` = repo ini (branch `migration/18.0_target`), `source-codebase` = clone baru `appointment-jitsi-migration-18-source` (branch `migration/17.0_source`, dari `backfill/17.0`).
2. **Sifat migrasi:** port kode saja, dikonfirmasi. Step 7 (Data Migration) di-skip/N/A.
3. **F-13 (paling kritis, dari `FINDINGS.md` backfill)** — `data/mail_template_data.xml` tidak terdaftar di manifest 17.0, fitur "link Jitsi di email konfirmasi" TIDAK PERNAH aktif. **Dev memutuskan: dipertahankan apa adanya di 18.0** (bug-for-bug), bukan diperbaiki sekalian saat migrasi. Dicatat eksplisit di `CLAUDE.md` §Source of Truth supaya tidak "keceplosan" diperbaiki di Step 6.
4. **F-01 s/d F-12 (12 temuan lain)** — dev memutuskan **semua dipertahankan apa adanya**, tidak ada perbaikan "sekalian" selama migrasi ini.
5. **Dependency Enterprise dikonfirmasi ganda:** `appointment` adalah modul Enterprise di KEDUA versi (17.0 dan 18.0) — dicek langsung isi folder `enterprise17`/`enterprise18`, bukan diasumsikan dari manifest saja. `native-*-enterprise` wajib dipakai di Step 2.
6. **Dokumen pelengkap:** dikonfirmasi tidak ada dokumen lain di luar kode + `doc-dev/backfill/` (functional spec, acceptance criteria, findings) yang sudah ada.
7. **Constraint:** tidak ada deadline khusus. Owner: Kuncoro (single owner, semua step).
8. **Temuan keamanan di luar scope** (dicatat, bukan bagian migrasi): beberapa repo referensi lokal (`appointment-jitsi-17`, `enterprise18`, dll) punya GitHub token tertanam plaintext di remote URL — lihat `CLAUDE.md` §Catatan keamanan. Direkomendasikan dev rotate token tsb terpisah dari migrasi ini.

---

## 1. Modul & Scope

- Modul yang dimigrasi: `appointment_jitsi` (single module, tidak ada modul lain yang saling depend)
- Deskripsi singkat: menambahkan integrasi Jitsi Meet ke `calendar.event` — generate link Jitsi unik per event, simpan di field `jitsi_link`, disisipkan ke email konfirmasi appointment/meeting (secara teori — lihat F-13, fitur ini nyatanya tidak pernah aktif).
- Apakah modul-modul ini saling depend satu sama lain: N/A, single module.

## 2. Dependency Map (auto-scan dari `source-codebase/appointment_jitsi/__manifest__.py`)

| Dependency | Tipe | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `base` | Native Community | Ya (18.0 bawaan) | Tidak ada perubahan API yang relevan diketahui saat ini — dicek detail di Step 2 |
| `calendar` | Native Community | Ya (18.0 bawaan) | Modul ini `_inherit` ke `calendar.event` — field core `access_token`, `videocall_location` dipakai langsung (lihat BSL di `01b_BASELINE_SPEC.md` §8). Perlu diff API Step 2. |
| `appointment` | **Native Enterprise** | Ya, ada di `enterprise18/appointment` (dikonfirmasi) | **WAJIB cross-check via `native-target-enterprise`, bukan Community.** `appointment.appointment_booked_mail_template` di-override modul ini — perlu dipastikan XML-ID/struktur template masih sama di 18.0. |

Dependency opsional yang dicek runtime (mis. `'hr.employee' in self.env`) — tidak ditemukan pola seperti ini di kode modul ini setelah dibaca `models/calendar_event.py` dan `controllers/appointment.py` (controller 100% dead code, lihat §2b).

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 relevan |
|---|---|---|---|
| Controllers (route custom) | Tidak (secara fungsional) | `controllers/appointment.py` — seluruh isi di-comment-out (F-06), `controllers/__init__.py` tetap import (no-op) | D1 → **N/A**, tidak ada route aktif untuk dimigrasikan; cukup pastikan file yang di-comment tetap valid Python di 18.0 |
| Assets/CSS/JS custom | Tidak | Tidak ada folder `static/src/`, tidak ada key `assets` di manifest | D2, E, F → **N/A** |
| Komponen Owl/JavaScript custom | Tidak | Tidak ada file `.js` di modul | E, F → **N/A** |
| Field JSON, relasi berantai (>2 level), dynamic model creation | Tidak | Field modul ini: `jitsi_link` (Text, compute), `is_jitsi` (Boolean), `company_param` (Many2one `res.company`) — semua sederhana | B2 → **N/A** |
| View pakai `attrs=`/`states=`/`domain=`/`context=` dinamis | Sebagian | `views/calendar_views.xml` pakai `invisible="not is_jitsi"` (syntax Odoo 17 modern, bukan `attrs=` lama) dan `context="{'module' : 'appointment_jitsi'}"` (statis, bukan dinamis) | C2 → **Kemungkinan N/A**, tapi WAJIB dicek Step 2 apakah syntax `invisible="..."` non-attrs berubah di 18.0 |

Semua kolom "Ada di modul?" mayoritas "Tidak" — modul ini KECIL dan SEDERHANA (2 model inherit, 1 view inherit, 1 data file, 0 model baru, 0 JS/Owl, 0 controller aktif). Applicability Check Step 6 kemungkinan besar akan menyatakan D1/D2/E/F/B2 sebagai N/A, dan fokus migrasi ada di kompatibilitas API `calendar.event`/`appointment`/`res.config.settings` (fase A/C) — dikonfirmasi ulang di Step 2/6, bukan diasumsikan final di sini.

## 3. Sifat Migrasi

- [x] Port kode saja (belum ada data produksi — instalasi baru di versi target)
- [ ] Upgrade instance (ada data produksi — step 7 wajib jalan)

## 4. Baseline Spec / Characterization Test (gate)

- [x] Modul punya `FUNCTIONAL_SPEC.md` lama? **Ya** — hasil kerja backfill sebelumnya: `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` + `01B_ACCEPTANCE_CRITERIA.md`, keduanya **sudah diverifikasi via eksekusi test nyata** (Odoo 17 Enterprise + Postgres 15, Docker) — bukan cuma baca-kode statis. `FINDINGS.md` (13 temuan, semua dikonfirmasi via test) melengkapinya.
  - Proses pengisian `01b_BASELINE_SPEC.md`: baca `01A_FUNCTIONAL_SPEC.md`/`01B_ACCEPTANCE_CRITERIA.md` sebagai draft awal → cross-check tiap klaim ke kode aktual di `source-codebase/appointment_jitsi/` → SEMUA klaim cocok dengan kode (backfill sendiri sudah melalui proses verifikasi test nyata sebelumnya, tidak ditemukan penyimpangan baru saat cross-check ulang untuk migrasi ini) → disalin/dirangkum dengan tag `[MATCH]` + `(ref: BR-NN/AC-NN-NN)`.
  - Lokasi tests existing yang dipakai untuk verifikasi: `appointment_jitsi/tests/test_appointment_jitsi.py` (13 test `TransactionCase`, ditulis saat backfill, semua PASS terhadap kode 17.0).
- [x] `01b_BASELINE_SPEC.md` sudah diisi — lihat file terpisah di folder yang sama.

### 4a. Dokumen Pelengkap Lain

- [x] Ditanyakan eksplisit ke dev: **dikonfirmasi tidak ada** dokumen pelengkap lain (PRD, spec Excel/Notion/Confluence, dokumentasi vendor) di luar kode `source-codebase` dan `doc-dev/backfill/` yang sudah ada — dikonfirmasi 2026-08-24.

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak — source module dibekukan selama migrasi berjalan (dikonfirmasi dev 2026-08-24).

## 5. Scope Boundary

- Yang harus tetap identik pasca migrasi: seluruh business logic di `01b_BASELINE_SPEC.md` — termasuk 13 bug/quirk `FINDINGS.md` backfill (F-01 s/d F-13, lihat keputusan dev di §Ringkasan poin 3-4 dan `CLAUDE.md` §Source of Truth).
- Yang sengaja diubah/di-drop selama migrasi: **tidak ada** — dev eksplisit memilih bug-for-bug migration, tanpa fix apapun "sekalian" (termasuk F-13 yang paling kritis).

## 6. Constraint

- Deadline: tidak ada deadline khusus (dikonfirmasi dev 2026-08-24) — dikerjakan sesuai kecepatan proses normal.
- Owner tiap step: Kuncoro (single owner — dev, review, QA, sign-off semua dipegang sendiri).
