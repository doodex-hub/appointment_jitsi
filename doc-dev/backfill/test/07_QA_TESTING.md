# QA Testing — appointment_jitsi

**Step:** 07 — QA Testing (backfill, TANPA UAT — BACKFILL berhenti di sini)
**Ref:** `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`, `doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md`, `03B_TEST_PLAN.md`
**Tanggal:** 2026-08-07

---

## 1. Area / AC yang Harus Dicakup

- [x] Alur end-to-end "email konfirmasi appointment menampilkan link Jitsi" — AC-09-01
- [x] Alur "aktivasi Jitsi via Settings → event baru dapat link" — AC-01-01/AC-01-02/AC-01-03
- [x] Alur "toggle is_jitsi pada event existing" — AC-04-01
- [x] Alur "multi-company" — AC-05-01
- [x] Skenario "hanya satu dialog/wizard disentuh": **N/A** — modul ini tidak punya wizard/dialog
  custom sama sekali (tidak ada `wizard/` di modul), dan tidak menambah dialog apapun ke form
  `calendar.event`. Satu-satunya UI baru adalah dua field di Settings (checkbox + Many2one), tidak
  ada skenario "dialog kedua terabaikan" yang relevan.

---

## 2. Format Skenario

```
### S-{{NN}}: {{Nama Skenario}}
**Precondition:** {{kondisi awal}}
**Mode eksekusi:** Mode C (docker, real) / Desk-review
**Steps:** ...
**Expected:** ...
**Actual:** ...
**Status:** ☐ Pass / ☐ Fail
**Provenance:** [HASIL-BACA] / [DIKONFIRMASI] / [PERLU-KEPUTUSAN]
```

---

## 3. Skenario

### S-01: Email konfirmasi appointment TIDAK menampilkan link Jitsi (F-13, PALING KRITIS)
**Precondition:** Integrasi Jitsi aktif (`is_jitsi_param=True`, `company_param` valid), event
`calendar.event` dibuat dengan minimal satu attendee, `jitsi_link` event terisi penuh dan benar.
**Mode eksekusi:** Mode C (docker, real — Odoo 17 Enterprise + Postgres 15, test
`test_qa_s01_mail_template_does_not_render_jitsi_link`)
**Steps:**
1. Aktifkan Jitsi via `res.config.settings` (setara admin mencentang "Enable Jitsi Integration" +
   memilih Company di Settings → Calendar).
2. Buat `calendar.event` dengan satu partner sebagai attendee.
3. Render `appointment.appointment_booked_mail_template` (`body_html`) untuk event itu — setara
   email yang BENAR-BENAR dikirim saat appointment di-booking lewat alur normal Odoo.
4. Cek isi body HTML hasil render.
**Expected (sesuai intent modul — README/manifest):** Body email memuat blok "How to Join" dengan
link `jitsi_link` (`https://meet.jit.si/...`).
**Actual (kode SEKARANG):** Body email TIDAK mengandung `jitsi_link` sama sekali — identik byte-per-byte
dengan template ASLI `appointment` core (dibandingkan langsung ke
`enterprise17/appointment/data/mail_template_data.xml`). Hanya berisi link "Join" standar
(`/calendar/meeting/join?token={access_token}`). Root cause: `data/mail_template_data.xml` (satu-satunya
file yang berisi override Jitsi untuk template ini) TIDAK terdaftar di `__manifest__.py` `data` —
Odoo tidak pernah memuatnya, dikonfirmasi juga tidak ada baris "loading
appointment_jitsi/data/mail_template_data.xml" di log instalasi manapun sepanjang seluruh sesi
Step 04/07.
**Status:** ✅ Pass (test memvalidasi behavior SEKARANG, yang merupakan BUG — lihat kolom Expected
vs Actual untuk gap-nya)
**Provenance:** `[PERLU-KEPUTUSAN]` — lihat `FINDINGS.md` F-13, prioritas TERTINGGI

---

### S-02: Aktivasi Jitsi global → event baru dapat link Jitsi format benar
**Precondition:** Tidak ada.
**Mode eksekusi:** Mode C (docker, real — test `test_ac_01_01_jitsi_link_format_when_enabled`, Step 04)
**Steps:**
1. Set `is_jitsi_param=True`, `company_param` = company aktif.
2. Buat `calendar.event` baru (tanpa menyertakan `is_jitsi` di payload create).
**Expected:** `jitsi_link` terisi format `https://meet.jit.si/{company}/{company}-{access_token}`.
**Actual:** Sesuai expected — PASS. **Catatan penting (lihat F-11):** event ini dibuat TANPA
`is_jitsi=True` sama sekali, tapi TETAP dapat `jitsi_link` — membuktikan field per-event `is_jitsi`
tidak berpengaruh ke compute ini, cuma setting GLOBAL yang menentukan.
**Status:** ✅ Pass
**Provenance:** `[DIKONFIRMASI]`

---

### S-03: Uncheck setting Jitsi setelah pernah aktif — apakah benar-benar mati?
**Precondition:** Jitsi pernah diaktifkan sekali.
**Mode eksekusi:** Mode C (docker, real — test `test_ac_01_03_uncheck_setting_still_truthy`, Step 04)
**Steps:**
1. Aktifkan Jitsi via `res.config.settings.execute()`.
2. Uncheck via `res.config.settings` lagi (`is_jitsi=False`), `.execute()`.
3. Buat event baru, cek `videocall_location`.
**Expected (hipotesis awal Step 01):** Berisiko tetap dapat link Jitsi kalau `ir.config_parameter`
menyimpan string `"False"` truthy.
**Actual:** Odoo MENGHAPUS row `ir.config_parameter` sepenuhnya saat uncheck — `get_param` balik
`False` (bool asli). Event baru jatuh ke fallback (bukan Jitsi). **F-01 TERBANTAHKAN, bukan bug.**
**Status:** ✅ Pass
**Provenance:** `[DIKONFIRMASI]`

---

### S-04: Toggle `is_jitsi` pada event existing tidak mengubah link
**Precondition:** Event sudah ada dengan `is_jitsi=False`.
**Mode eksekusi:** Mode C (docker, real — test `test_ac_04_01_write_toggle_no_recompute`, Step 04)
**Steps:**
1. Buat event `is_jitsi=False`. Catat `videocall_location`.
2. Aktifkan setting Jitsi global.
3. `event.write({'is_jitsi': True})`.
4. Cek `videocall_location` lagi.
**Expected (kalau field is_jitsi dianggap berarti "opt-in per event"):** Link berubah jadi Jitsi
setelah `is_jitsi=True`.
**Actual:** `videocall_location` TIDAK BERUBAH SAMA SEKALI (`before == after`). Sejalan dengan
F-11: `is_jitsi` per-event tidak dipakai compute; ditambah F-02: recompute cuma depends
`access_token`, yang tidak berubah oleh `write({'is_jitsi': True})`.
**Status:** ✅ Pass (memvalidasi bug F-02 secara eksplisit)
**Provenance:** `[DIKONFIRMASI]`

---

### S-05: Multi-company — nama company di URL Jitsi tidak mengikuti company event
**Precondition:** Dua company ada di database, Jitsi aktif dengan `company_param` = company A.
**Mode eksekusi:** Mode C (docker, real — test `test_ac_05_01_company_param_global_multi_company`, Step 04)
**Steps:**
1. Buat event di context company A.
2. Buat event di context company B.
3. Bandingkan `jitsi_link` keduanya.
**Expected (kalau per-company):** Event company B memakai nama company B di link.
**Actual:** KEDUA event memakai nama company A (dari `company_param` global) — company B TIDAK
pernah muncul di link manapun.
**Status:** ✅ Pass (memvalidasi F-05)
**Provenance:** `[DIKONFIRMASI]`

---

## 4. Status Sub-file & Rekap Eksekusi

| File | Isi | Status | Dieksekusi? | Mode |
|---|---|---|---|---|
| §3 di file ini | 5 skenario end-to-end/business-flow | ✅ Selesai | Ya | Mode C (docker, real — Odoo 17 Enterprise + Postgres 15) |
| `07B_QA_AI_BROWSER.md` | N/A — tidak dibuat | N/A | Tidak | Lihat rasional di `03B_TEST_PLAN.md` §Step 07 (modul tidak punya JS/OWL kustom atau dialog ganda yang butuh Tour/browser) |

**Keterbatasan eksekusi:** Tidak ada desk-review murni — SEMUA skenario di §3 dieksekusi nyata
lewat `TransactionCase` di Odoo 17 Enterprise + Postgres 15 (Docker, Mode C). Satu-satunya
prasyarat infrastruktur yang tidak bisa dihindari: modul butuh mount source Odoo Enterprise lokal
(lihat F-12) — kalau environment lain tidak punya akses ini, Step 04/07 modul ini harus jatuh ke
desk-review.

---

## 5. Rekap Findings

| Tag | Jumlah |
|---|---|
| `[PERLU-KEPUTUSAN]` | 6 (F-08, F-09 di FINDINGS, F-11, F-13, plus F-02/F-03/F-04 yang sudah `[DIKONFIRMASI]` — lihat catatan) |
| `[DIKONFIRMASI]` | 7 (F-02, F-03, F-04, F-05, F-06, F-07, F-13 hasil eksekusi; F-01 dikonfirmasi BUKAN bug) |
| `[HASIL-BACA]` (tanpa masalah) | 2 (F-10, F-12 — informasional) |

**Verdict:** Backfill dokumentasi selesai sampai Step 07 (QA Testing). **Tidak ada sign-off** — ini
bukan release gate. 13/13 test `TransactionCase` PASS, semua mendemonstrasikan behavior SEKARANG
(termasuk bug-bug yang terkonfirmasi) secara eksplisit lewat assertion, bukan cuma "hijau tanpa
makna". Keputusan atas seluruh item `[PERLU-KEPUTUSAN]` di `FINDINGS.md` — terutama **F-13**
(fitur email inti tidak pernah aktif) — ada di tangan pemilik modul.

---

## 6. Bug / Perlu Perbaikan (Konsolidasi)

| Ditemukan di | Scenario | Ringkasan masalah | Status perbaikan |
|---|---|---|---|
| §3 | S-01 | **F-13 (TERTINGGI):** `data/mail_template_data.xml` tidak terdaftar di manifest — fitur email Jitsi tidak pernah aktif | ☐ Belum |
| §3 | S-04 | F-02: toggle `is_jitsi` via `write()` tidak memicu recompute link | ☐ Belum |
| Step 04 (AC-03-01) | — | F-04: hasil `jitsi_link`/`videocall_location` bergantung urutan field dibaca | ☐ Belum |
| Step 04 (AC-02-03) | — | F-03: `create()` tidak batch-safe (WARNING resmi Odoo) | ☐ Belum |
| §3 | S-05 | F-05: `company_param` global, tidak per-company | ☐ Belum |
| Step 01/04 | — | F-11: field per-event `is_jitsi` tidak dipakai compute | ☐ Belum |
| Step 01 | — | F-06: controller dead code | ☐ Belum (dampak rendah) |
| Step 01 | — | F-07: format URL Jitsi (duplikasi + tanpa slug) | ☐ Belum |
| Step 01/instalasi | — | F-10: label field "Company" bentrok | ☐ Belum (kosmetik) |
| Step 01 | — | F-08: method manual generate/clear tidak terhubung UI | ☐ Belum (butuh klarifikasi intent) |
| Step 01 | — | F-09: file Google verification nyasar di repo modul | ☐ Belum (kosmetik) |

---

## 7. Slot Metode Masa Depan (belum dibuat)

Tidak ada kandidat saat ini — modul cukup kecil, `07B_QA_AI_BROWSER.md`/Playwright tidak relevan
(lihat rasional di `03B_TEST_PLAN.md`).
