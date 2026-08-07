# Dev Testing — appointment_jitsi

**Step:** 04 — Developer Testing (backfill)
**Module:** `appointment_jitsi`
**Spec ref:** `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-08-07

> Semua test di dokumen ini BENAR-BENAR DIJALANKAN (Mode C — AI jalankan langsung dari Claude Code
> CLI), bukan desk-review. Lihat §0 untuk detail environment + kendala nyata yang ditemukan dan
> diselesaikan.

---

## 0. Environment & Kendala Nyata

**Setup:** `docker-env/docker-compose.yml` (Odoo 17 + Postgres 15, instantiate dari
`doc-dev-backfill/templates/docker-compose.yml.template`).

**Percobaan #1 — GAGAL total:** image resmi `odoo:17.0` (Community, Docker Hub) →
`"module appointment_jitsi: Unmet dependencies: appointment"`. Root cause: `appointment` (dan
dependency-nya, `web_gantt`) berlisensi `OEEL-1` (Odoo Enterprise) — tidak dibundel di image
Community publik. Dikonfirmasi modul `appointment` bahkan tidak pernah ter-load sama sekali di
log (bukan error saat load, tapi memang tidak ada di addons-path).

**Percobaan #2 — SUKSES:** menambahkan volume mount read-only ke checkout Odoo 17 Enterprise
lokal (`D:\Kuncoro\doodex\repo\enterprise17`, lisensi Doodex sebagai Odoo partner) sebagai extra
addons-path di `docker-compose.yml`. Modul `appointment_jitsi` (42/42 modul) berhasil ter-install
penuh. Dicatat sebagai limitasi/prasyarat environment permanen — lihat `FINDINGS.md` F-12.

**Hasil final (percobaan #3, setelah 2 perbaikan test — bukan perbaikan kode modul):**
```
0 failed, 0 error(s) of 12 tests when loading database 'appointment_jitsi_test'
```
12 test class `TestAppointmentJitsi` (`appointment_jitsi/tests/test_appointment_jitsi.py`), semua
`TransactionCase`, `@tagged('post_install', '-at_install')`. Dua test SEMPAT error di percobaan
#2 karena bug di ASSERTION test itu sendiri (mengasumsikan `videocall_location` selalu string,
padahal bisa `False`) — diperbaiki (bukan mengubah kode bisnis), dijalankan ulang, PASS.

**Warning resmi Odoo yang tercatat saat instalasi (bukan dari test, dari proses `-i` itu sendiri):**
1. `odoo.api.create`: *"The model odoo.addons.appointment_jitsi.models.calendar_event is not
   overriding the create method in batch"* → lihat F-03.
2. `odoo.addons.base.models.ir_model`: *"Two fields (company_param, company_id) of
   res.config.settings() have the same label: Company. [Modules: appointment_jitsi and
   base_setup]"* → lihat F-10 (temuan baru, tidak ketahuan dari baca kode Step 01).

---

## 1. Smoke Test (happy path)

| # | Area/fitur | Happy path / edge case | Cara | Status |
|---|---|---|---|---|
| 1 | Aktivasi Jitsi + create event | Setting aktif, company valid → event baru dapat `jitsi_link` format benar | Mode C (docker, real) | ✅ Pass |
| 2 | Setting tidak pernah diaktifkan | Event baru fallback ke Discuss (`videocall_location` tidak berisi URL Jitsi) | Mode C (docker, real) | ✅ Pass |

---

## 2. Unit & Integration Test Specification

### 2a. Model Fields — `calendar.event`

**File:** `models/calendar_event.py`

#### TC-F-01 — `jitsi_link` (computed, stored)

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Integration | `is_jitsi_param`=True, `company_param` valid, event dibuat | `jitsi_link` = `https://meet.jit.si/{company}/{company}-{access_token}` — **TERBUKTI di test, PASS** | `[DIKONFIRMASI]` |
| 02 | Integration | `is_jitsi_param` tidak pernah di-set | `videocall_location` bukan link Jitsi (fallback Discuss, hasil aktual `False` di test-env tanpa attendee — lihat F-04) — **PASS** | `[DIKONFIRMASI]` |
| 03 | Integration | Uncheck setting setelah pernah aktif (via `res.config.settings.execute()`) | `ir.config_parameter` row DIHAPUS, `get_param` balik `False` (bool asli) — **F-01 TERBANTAHKAN, bukan bug** | `[DIKONFIRMASI]` |

#### TC-F-02 — `access_token` / `create()` override

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Integration | `create()` single dict, `is_jitsi=True` | `access_token` = uuid4 hex baru (32 char) — **PASS** | `[DIKONFIRMASI]` |
| 02 | Integration | `create()` single dict, `is_jitsi=False` + `access_token` lain disertakan | `access_token` direset `False`, menimpa nilai yang disertakan — **PASS** | `[DIKONFIRMASI]` |
| 03 | Integration | `create()` LIST of dict (batch), `is_jitsi=True` di tiap dict | Odoo cetak WARNING resmi "not overriding create in batch"; `access_token` TETAP terisi (dari default core, bukan dari override modul) — **dikonfirmasi, dampak lebih ringan dari perkiraan** | `[DIKONFIRMASI]` |

### 2b. Race Condition `videocall_location` vs `jitsi_link` (F-04)

#### TC-RACE-01 — Urutan akses field menentukan hasil compute

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Integration | Setup config Jitsi IDENTIK, `event_a.jitsi_link` dibaca DULU | `jitsi_link` DAN `videocall_location` KEDUANYA berisi URL Jitsi — **PASS** | `[DIKONFIRMASI]` |
| 02 | Integration | Setup config Jitsi IDENTIK, `event_b.videocall_location` dibaca DULU (jitsi_link tidak pernah disentuh) | Compute RESMI core (`_compute_videocall_location`) yang jalan, hasil `False` — `jitsi_link` tidak pernah ter-compute — **PASS, membuktikan F-04** | `[DIKONFIRMASI]` |

### 2c. Multi-Company & Format URL

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Integration | Dua event beda company (`with_company`), `company_param` disetel ke company A | Kedua event menghasilkan `jitsi_link` dengan nama company A yang SAMA (bukan company masing-masing event) — **PASS, F-05 dikonfirmasi** | `[DIKONFIRMASI]` |
| 02 | Integration | Nama company berspasi ("PT Doodex Indonesia") | Spasi masuk mentah ke URL, nama company muncul 2x di path — **PASS, F-07 dikonfirmasi** | `[DIKONFIRMASI]` |

### 2d. Toggle & Dead Code

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Integration | Event `is_jitsi=False` → `write({'is_jitsi': True})` (tanpa ubah field lain) | `videocall_location` TIDAK berubah (tidak ter-recompute) — **PASS, F-02 dikonfirmasi** | `[DIKONFIRMASI]` |
| 02 | Unit | Baca source `controllers/appointment.py` | Nol baris aktif (semua di-comment-out) — **PASS, F-06 dikonfirmasi** | `[DIKONFIRMASI]` |
| 03 | Unit | Panggil `generate_jitsi_link()`/`clear_jitsi_link()` langsung | Kedua method berfungsi normal (clear → kosong, generate → terisi lagi) — **PASS** | `[HASIL-BACA]` |

### 2e. Test Matrix Summary

| Area | Unit | Integration | Provenance |
|---|---|---|---|
| `jitsi_link`/`videocall_location` compute | | ✓ | `[DIKONFIRMASI]` |
| `create()` override | | ✓ | `[DIKONFIRMASI]` |
| Race condition urutan field | | ✓ | `[DIKONFIRMASI]` |
| Multi-company & format URL | | ✓ | `[DIKONFIRMASI]` |
| Toggle via `write()` | | ✓ | `[DIKONFIRMASI]` |
| Controller dead code | ✓ | | `[DIKONFIRMASI]` |
| Method manual generate/clear | ✓ | | `[HASIL-BACA]` |

### 2f. Ringkasan

- Unit: 2 TC (controller dead code, generate/clear method)
- Integration: 10 TC
- Total: 12 test method, semua PASS (`0 failed, 0 error(s) of 12 tests`)
- Jalankan ulang: `cd docker-env && docker compose up` (lihat §0), lalu `docker compose down`
  setelah selesai (AI sudah menjalankan & membersihkan sendiri di sesi ini).

### 2g. Override/Collision Check terhadap Odoo Core

| # | Method | Model | Kelas yang mendefinisikan (`__mro__` / `field.compute`) | Override total Odoo core? | Provenance |
|---|---|---|---|---|---|
| 01 | `create` | `calendar.event` | Memanggil `super().create(values)` — EXTEND, bukan override total. TAPI dikonfirmasi Odoo sendiri: tidak batch-safe (lihat F-03) | ☐ Ya / ☑ Tidak (extend, tapi ada gap batch) | `[DIKONFIRMASI]` |
| 02 | `_compute_jitsi_link` | `calendar.event` | Nama method BARU, tidak bentrok nama. TAPI menulis field `videocall_location` yang compute RESMI-nya `_compute_videocall_location` (CORE, dikonfirmasi via `field.compute` introspection) — kelas bug SEJENIS di level field, bukan nama method (lihat F-04) | ☐ Ya (nama method) / ☑ **Ya, di level field-compute** | `[DIKONFIRMASI]` |
| 03 | `generate_jitsi_link`, `clear_jitsi_link`, `action_join_video_call` | `calendar.event` | Nama BARU, tidak bentrok | ☐ Tidak relevan (tidak bentrok) | `[HASIL-BACA]` |

### 2h. Incoming Email

**N/A** — modul tidak override `message_process()`/`message_route()`, tidak punya `mail.alias`
custom, tidak depend `fetchmail.server`. Modul hanya memodifikasi ISI (bukan header/routing) dua
mail template BAWAAN yang dikirim lewat jalur outgoing existing `calendar`/`appointment`.
