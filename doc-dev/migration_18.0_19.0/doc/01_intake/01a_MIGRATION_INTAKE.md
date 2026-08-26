# Migration Intake — appointment_jitsi

**Step:** 1 — Intake & Scope
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Status:** ✔️ Lulus gate — dikonfirmasi dev 2026-08-26

---

## 0. Folder Referensi — Dikonfirmasi Dev (2026-08-26)

- [x] `native-source` (Community 18.0) — `D:\Kuncoro\doodex\repo\odoo18` (clone `odoo/odoo`, branch `18.0`, sudah ada di disk, reuse dari project 17.0→18.0)
- [x] `native-source-enterprise` (Enterprise 18.0) — `D:\Kuncoro\doodex\repo\enterprise18` (reuse dari project sebelumnya)
- [x] `native-target` (Community 19.0) + `native-target-enterprise` (Enterprise 19.0) — **SATU folder gabungan**, dikonfirmasi via `ls` langsung: `D:\Kuncoro\doodex\repo\enterprise19.0` BUKAN addons-only, melainkan repo Odoo penuh (`odoo/`, `setup.py`, `MANIFEST.in`) dengan modul Community (`calendar`, dst) DAN Enterprise (`appointment`, dst) tergabung di `odoo/addons/` yang sama. **BUKAN git repo** (hasil extract/distribusi, bukan clone) — tidak ada `.git/` di dalamnya. `.claude/settings.json` mengisi `ABS_PATH_NATIVE_TARGET` DAN `ABS_PATH_NATIVE_TARGET_ENTERPRISE` dengan path yang sama, sesuai rekomendasi curation `advanced_sales_analysis`.
- [x] `third-party-source`/`third-party-target` — dev dikonfirmasi eksplisit (2026-08-26): **tidak ada** dependency OCA/vendor untuk pasangan versi ini juga, konsisten dengan project 17.0→18.0. Tidak perlu connect folder ini.

**Verifikasi langsung dependency Enterprise di 19.0 (bukan diasumsikan dari 18.0):**
- `appointment/__manifest__.py` di `enterprise19.0/odoo/addons/appointment` → `'license': 'OEEL-1'` (Enterprise) — dikonfirmasi masih Enterprise-licensed di 19.0, tidak berubah dari 17.0/18.0.
- `calendar/__manifest__.py` di `enterprise19.0/odoo/addons/calendar` → `'license': 'LGPL-3'` (Community) — tidak berubah.
- Modul `appointment` TIDAK ada di `odoo18/addons` (Community 18.0) — konsisten pola Enterprise-only yang sudah dikonfirmasi project sebelumnya.

### 0a. Konfirmasi Branch/Versi `source-codebase` & `target-codebase`

- [x] Folder `source-codebase` — `D:\Kuncoro\doodex\repo\appointment-jitsi-migration-19-source`, branch **`migration/18.0`** (clone baru 2026-08-26 dari remote `doodex-hub/appointment_jitsi`, commit `3a563b2` — hasil akhir migrasi 17.0→18.0 yang sudah UAT sign-off, identik dengan `migration/18.0_target`).
- [x] Folder `target-codebase` — `D:\Kuncoro\doodex\repo\appointment-jitsi-migration-19` (repo ini), branch **`migration/19.0_target`** (dibuat 2026-08-26 dari `origin/migration/18.0`, commit awal sama `3a563b2` — kode migrasi 19.0 akan ditulis di atas branch ini). Nama branch dikonfirmasi verbatim oleh dev di sesi ini sebelum dieksekusi.
- [x] Dikonfirmasi dua clone fisik terpisah (bukan symlink/alias) — `git clone` lokal dijalankan dari `target-codebase` ke folder sibling baru, persistensi diverifikasi di panggilan terpisah (`ls` + `git branch --show-current` dari dalam folder baru).
- [x] **Versi Odoo semantik, dikonfirmasi eksplisit dev:** 18.0 → 19.0 (dari instruksi awal dev: "migrasi 18 ke 19").
- [x] **Config yang diwarisi branch basis dicek SEBELUM checkout** (lesson `advanced_sales_analysis`): `.claude/settings.json`/`.gitignore` yang untracked di `target-codebase` sebelum checkout SUDAH versi `migration-tool` yang benar (bukan config tool lama `doc-dev-backfill`) — cuma placeholder `{{ABS_PATH_...}}` belum terisi dan path-nya masih untuk project 17.0→18.0 di branch basis. Untracked files di-backup lalu dihapus dulu supaya `checkout -b` tidak konflik, kemudian file tracked hasil checkout di-edit ulang dengan path project 19.0 ini.

### 0b. Gate: Path Absolut di `.claude/settings.json`

- [x] `ABS_PATH_SOURCE_CODEBASE` = `D:/Kuncoro/doodex/repo/appointment-jitsi-migration-19-source`
- [x] `ABS_PATH_MIGRATION_TOOL` = `D:/Kuncoro/doodex/repo/migration-tool-project/migration-tool`
- [x] `ABS_PATH_NATIVE_SOURCE` = `D:/Kuncoro/doodex/repo/odoo18`
- [x] `ABS_PATH_NATIVE_SOURCE_ENTERPRISE` = `D:/Kuncoro/doodex/repo/enterprise18`
- [x] `ABS_PATH_NATIVE_TARGET` = `D:/Kuncoro/doodex/repo/enterprise19.0` (folder gabungan, lihat §0)
- [x] `ABS_PATH_NATIVE_TARGET_ENTERPRISE` = `D:/Kuncoro/doodex/repo/enterprise19.0` (path SAMA dengan di atas — folder gabungan, sengaja diisi dobel sesuai rekomendasi curation, bukan dibiarkan kosong)
- [x] `ABS_PATH_THIRD_PARTY_SOURCE`/`ABS_PATH_THIRD_PARTY_TARGET` — dihapus seluruhnya dari `deny` list (dikonfirmasi tidak dipakai)

Gate ini **selesai** — tidak ada `{{ABS_PATH_...}}` literal tersisa di `.claude/settings.json`.

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Versi & branch:** migrasi 18.0 → 19.0 dikonfirmasi. `target-codebase` = repo ini (branch `migration/19.0_target`, dibuat dari `origin/migration/18.0`), `source-codebase` = clone baru `appointment-jitsi-migration-19-source` (branch `migration/18.0`).
2. **Sifat migrasi:** port kode saja — **dikonfirmasi dev 2026-08-26**. Step 7 (Data Migration) di-skip/N/A.
3. **Source dibekukan selama migrasi** — **dikonfirmasi dev 2026-08-26**. `SYNC_POLICY.md` tidak dipakai.
4. **Tidak ada dependency OCA/third-party** — **dikonfirmasi dev 2026-08-26**, konsisten project sebelumnya.
5. **Semua bug/quirk 18.0 dipertahankan bug-for-bug di 19.0** (13 `BSL-NNN` klaim quirk dari baseline 17.0→18.0, termasuk `BSL-015`/F-13 — email Jitsi tetap tidak pernah aktif) — **kecuali** wajib berubah untuk kompatibilitas 19.0 murni teknis (mis. field rename core kalau ada, dicek Step 2).
6. **Dependency Enterprise `appointment` dikonfirmasi tetap Enterprise-only di 19.0** (`license: OEEL-1`, dicek langsung ke `enterprise19.0/odoo/addons/appointment/__manifest__.py`) — sama seperti 17.0/18.0.
7. **`native-target`/`native-target-enterprise` 19.0 adalah SATU folder gabungan** (`enterprise19.0`, bukan git repo, hasil extract Community+Enterprise jadi satu tree) — beda struktur dari 18.0 (`odoo18`+`enterprise18` dua clone terpisah). Sudah ditangani di `.claude/settings.json` §0b.
8. **Dokumen pelengkap:** belum ditanyakan ulang eksplisit ke dev di sesi ini di luar 3 pertanyaan §3/§4b/OCA di atas — asumsi tidak ada dokumen baru selain `doc-dev/migration_17.0_18.0/` yang sudah ada (dasar baseline spec di bawah). Kalau ada dokumen lain yang dev tahu, sebutkan sebelum Step 2 mulai.
9. **Constraint:** belum ditanyakan ulang eksplisit — diasumsikan sama seperti project sebelumnya (tidak ada deadline khusus, owner Kuncoro single-owner). Koreksi kalau berbeda.

---

## 1. Modul & Scope

- Modul yang dimigrasi: `appointment_jitsi` (single module, tidak ada modul lain yang saling depend)
- Deskripsi singkat: menambahkan integrasi Jitsi Meet ke `calendar.event` — generate link Jitsi unik per event, simpan di field `jitsi_link`, secara teori disisipkan ke email konfirmasi appointment (lihat `BSL-015` — fitur ini tidak pernah aktif, bug-for-bug dipertahankan sejak 17.0).
- Apakah modul-modul ini saling depend satu sama lain: N/A, single module.

## 2. Dependency Map (auto-scan dari `source-codebase/appointment_jitsi/__manifest__.py`, branch `migration/18.0`)

| Dependency | Tipe | Versi tersedia di target (19.0)? | Catatan |
|---|---|---|---|
| `base` | Native Community | Ya (19.0 bawaan) | Belum ada indikasi breaking spesifik ke modul ini — cek detail Step 2 vs `knowledge/version-diffs/18-to-19.md` §1 (mis. `self._cr`/`self._uid`/`self._context` — modul ini TIDAK memakai pola ini setelah dicek kode 18.0, kemungkinan besar N/A) |
| `calendar` | Native Community | Ya (19.0 bawaan, `license: LGPL-3` dikonfirmasi) | Modul `_inherit` ke `calendar.event`, memakai field core `access_token`, `videocall_location` langsung (imperatif, lihat `BSL-010`). **WAJIB diff Step 2**: apakah `access_token`/`videocall_location`/`_compute_videocall_location`/`_set_discuss_videocall_location` masih ada dengan signature sama di 19.0. |
| `appointment` | **Native Enterprise** | Ya, ada di `enterprise19.0/odoo/addons/appointment` (`license: OEEL-1`, dikonfirmasi langsung — lihat §0) | **WAJIB cross-check via `native-target-enterprise` (= `enterprise19.0`), bukan Community.** `appointment.appointment_booked_mail_template` di-override modul ini — perlu dipastikan XML-ID/struktur template masih sama di 19.0. |

Dependency opsional yang dicek runtime (mis. `'hr.employee' in self.env`) — tidak ditemukan pola seperti ini di kode modul ini (konsisten temuan project 17.0→18.0, kode tidak berubah).

**Catatan dari `knowledge/version-diffs/18-to-19.md` §1a (temuan nyata project `advanced_sales_analysis`):** rename `sale.order.line.tax_id`→`tax_ids` — modul ini TIDAK menyentuh `sale.order.line` sama sekali, kemungkinan besar tidak relevan. Dikonfirmasi ulang di Step 2, bukan diasumsikan final di sini.

## 2b. Struktur & Fitur Modul (auto-scan — tidak berubah dari project 17.0→18.0, kode source identik)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 relevan |
|---|---|---|---|
| Controllers (route custom) | Tidak (secara fungsional) | `controllers/appointment.py` — seluruh isi di-comment-out (`BSL-016`), `controllers/__init__.py` tetap import (no-op) | D1 → **N/A** |
| Assets/CSS/JS custom | Tidak | Tidak ada folder `static/src/`, tidak ada key `assets` di manifest | D2, E, F → **N/A** |
| Komponen Owl/JavaScript custom | Tidak | Tidak ada file `.js` di modul | E, F → **N/A** |
| Field JSON, relasi berantai (>2 level), dynamic model creation | Tidak | Field modul ini: `jitsi_link` (Text, compute), `is_jitsi` (Boolean), `company_param` (Many2one `res.company`) — semua sederhana | B2 → **N/A** |
| View pakai `attrs=`/`states=`/`domain=`/`context=` dinamis | Sebagian | `views/calendar_views.xml` pakai `invisible="not is_jitsi"` (sudah syntax modern non-`attrs=` sejak 17.0) dan `context="{'module' : 'appointment_jitsi'}"` (statis) | C2 → **Kemungkinan N/A**, cek ulang Step 2 apakah ada perubahan syntax view lain di 19.0 (mis. `<tree>`→`<list>` — modul ini tidak punya `<tree>` sama sekali, hanya form settings, jadi kemungkinan besar tidak relevan) |

Modul ini KECIL dan SEDERHANA (2 model inherit, 1 view inherit, 1 data file — tidak terdaftar di manifest per `BSL-015`, 0 model baru, 0 JS/Owl, 0 controller aktif), kode identik dengan project 17.0→18.0 (tidak ada perubahan source antara UAT sign-off 18.0 dan mulai project ini). Applicability Check Step 6 kemungkinan besar akan menyatakan D1/D2/E/F/B2 sebagai N/A, fokus migrasi ada di kompatibilitas API `calendar.event`/`appointment`/`res.config.settings` (fase A/C) dan perubahan framework generik dari `knowledge/version-diffs/18-to-19.md` §1 (`osv.expression`→`Domain`, `_sql_constraints`→`Constraint`/`Index`, dll — modul ini TIDAK memakai pola-pola itu setelah dicek kode, kemungkinan besar semua N/A juga, dikonfirmasi ulang Step 2).

## 3. Sifat Migrasi

- [x] Port kode saja (belum ada data produksi — instalasi baru di versi target) — **dikonfirmasi dev 2026-08-26**
- [ ] Upgrade instance (ada data produksi — step 7 wajib jalan)

## 4. Baseline Spec / Characterization Test (gate)

- [x] Modul punya `FUNCTIONAL_SPEC.md` lama? **Ya, dua lapis:** (1) `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` + `01B_ACCEPTANCE_CRITERIA.md` + `FINDINGS.md` (verifikasi test asli 17.0), dan (2) `doc-dev/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md` (21 klaim `BSL-001`..`BSL-021`, semua `[MATCH]`) yang SUDAH diverifikasi ulang lewat dev testing (Step 9, 13/13 test PASS) DAN QA testing (Step 10, 5/5 skenario Pass, termasuk reproduksi live quirk `BSL-010`) langsung di kode 18.0 — bukan cuma cross-check statis.
  - Proses pengisian `01b_BASELINE_SPEC.md` (versi 18.0→19.0 ini): baca `doc-dev/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md` sebagai dasar → cross-check tiap klaim ke kode aktual `source-codebase/appointment_jitsi/` (branch `migration/18.0`) → kode source **identik byte-for-byte** dengan yang sudah diverifikasi test nyata di 18.0 (tidak ada perubahan source sejak UAT sign-off 2026-08-24) → seluruh 21 klaim disalin dengan tag `[MATCH]`, `(ref: BSL-NNN dari 01b_BASELINE_SPEC.md migrasi 17.0→18.0)`.
  - Lokasi tests existing: `appointment_jitsi/tests/test_appointment_jitsi.py` (13 test `TransactionCase`, sudah PASS terhadap kode 18.0 di dev testing Step 9 migrasi sebelumnya).
- [x] `01b_BASELINE_SPEC.md` sudah diisi — lihat file terpisah di folder yang sama.

### 4a. Dokumen Pelengkap Lain

- [ ] **Belum ditanyakan ulang eksplisit ke dev di sesi ini** — di project 17.0→18.0 dikonfirmasi tidak ada dokumen pelengkap lain di luar kode + `doc-dev/backfill/`. Untuk project ini diasumsikan sama (tidak ada dokumen baru sejak 2026-08-24), TAPI ini asumsi carry-over, bukan konfirmasi baru — tanyakan ke dev kalau ada dokumen lain (PRD, spec Excel/Notion/Confluence, dokumentasi vendor) sebelum Step 2 dianggap final.

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak — source module dibekukan selama migrasi berjalan (**dikonfirmasi dev 2026-08-26**).

## 5. Scope Boundary

- Yang harus tetap identik pasca migrasi: seluruh business logic di `01b_BASELINE_SPEC.md` — termasuk 21 klaim `BSL-NNN` (mewarisi 13 bug/quirk asal `FINDINGS.md` backfill F-01..F-13 yang sudah dipertahankan sejak 17.0→18.0).
- Yang sengaja diubah/di-drop selama migrasi: **tidak ada** — bug-for-bug migration, konsisten kebijakan project sebelumnya, kecuali perubahan yang **wajib** murni untuk kompatibilitas teknis 19.0 (akan dicatat eksplisit di `03_MIGRATION_SPEC.md` kalau ditemukan Step 2).

## 6. Constraint

- Deadline: tidak ada deadline khusus (asumsi carry-over dari project sebelumnya — belum ditanyakan ulang eksplisit).
- Owner tiap step: Kuncoro (asumsi carry-over — single owner, semua step).
