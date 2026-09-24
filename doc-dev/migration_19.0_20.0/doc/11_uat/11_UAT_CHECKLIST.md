# UAT Checklist — Migrasi appointment_jitsi (19.0 → 20.0)

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`, `FINDINGS.md`
**Tanggal draft:** 2026-09-24
**Status:** ✔️ Sign-off (waiver) — owner Kuncoro menutup UAT berdasarkan hasil AI-test yang sudah ada (chat 2026-09-24); lihat catatan waiver di bagian Sign-off

> Kriteria sukses: pemakai TIDAK merasakan bedanya dibanding 19.0, **kecuali** item yang sudah disetujui berubah (lihat "Review Item Out-of-Scope").
>
> Dokumen ini adalah **skrip test untuk dijalankan sendiri** oleh owner/business user. Kolom **Actual** dan **Status** semestinya diisi orang yang menjalankan; pada siklus ini diisi AI dengan rujukan bukti Step 9/10 atas permintaan eksplisit owner (waiver, lihat Sign-off). Hasil test AI (Step 9/10) ada di dokumen masing-masing dan bukan pengganti UAT ini.

---

## Persiapan Sebelum UAT

- [ ] Odoo **20.0 Enterprise** (staging/salinan, bukan produksi) dengan modul **Appointment Jitsi** versi `20.0.1.0.0` ter-install dari branch `migration/20.0`.
- [ ] Login sebagai **Administrator** untuk langkah Settings (T-01, T-03), dan — kalau tersedia — sebagai **user internal biasa** (grup Calendar/Appointment standar, bukan admin) untuk T-02, supaya hak akses standar ikut teruji.
- [ ] Minimal satu company aktif. Untuk T-04 butuh company kedua bernama **"PT Doodex Indonesia"** (dengan spasi).
- [ ] Untuk T-05: satu **Appointment Type** yang bisa dibooking dari portal (mis. "Demo Jitsi", durasi 30 menit), dan email tujuan yang bisa Anda buka (atau server email test seperti Mailpit).

## Skenario Test

### T-01: Mengaktifkan integrasi Jitsi

**Data dummy:** Company = company utama Anda (mis. "My Company").

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka **Settings → Calendar** | Di bawah "Outlook Calendar" / "Google Calendar" ada blok **"Jitsi Configuration"**; field **Company** belum terlihat | [AI S-01, 20.0 dan 19.0] Blok ada setelah Google Calendar; Company tersembunyi | [x] Pass [ ] Fail |
| 2 | Centang **Jitsi Configuration** | Field **Company** muncul, terisi company aktif | [AI S-01] Company muncul, default "My Company" | [x] Pass [ ] Fail |
| 3 | Klik **Save** | Tersimpan tanpa error; setelah halaman reload tetap tercentang & Company tetap terisi | [AI S-01] Tersimpan (`is_jitsi_param=True`, `company_param=1`), tetap tercentang | [x] Pass [ ] Fail |

### T-02: Membuat meeting dan join lewat Jitsi

**Data dummy:** Meeting Subject = "UAT Jitsi 01".

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | **Calendar → Meetings → New**, isi Meeting Subject, jangan ubah field lain, **Save** | Tersimpan tanpa error | [AI S-02] Tersimpan tanpa error — sebagai **admin**; user non-admin tidak dites | [x] Pass [ ] Fail |
| 2 | Lihat field **Video Link** | Berisi `https://meet.jit.si/<Nama Company>/<Nama Company>-<kode>` (di 20.0 langsung tampil; di 19.0 dulu perlu reload — RMV-01) | [AI S-02] `https://meet.jit.si/My Company/My Company-7d264e93-…`, langsung tampil | [x] Pass [ ] Fail |
| 3 | Klik ikon **Join** (panah masuk kotak) di samping Video Link | Tab baru terbuka ke alamat yang **sama persis** dengan Video Link dan ruang Jitsi terbuka | [AI S-02] Tab baru ke URL sama persis (request ke meet.jit.si diblok AI — ruang Jitsi tidak benar-benar dibuka) | [x] Pass [ ] Fail |
| 4 | Buat meeting kedua "UAT Jitsi 02" | Video Link-nya beda kode dari meeting pertama (unik per meeting) | [AI S-02/S-04] Tiap meeting beda token (`7d264e93…` vs `7ebf39d4…`) | [x] Pass [ ] Fail |

### T-03: Mematikan Jitsi → kembali ke Odoo Discuss

**Data dummy:** Meeting Subject = "UAT Discuss 01".

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | **Settings → Calendar** → hilangkan centang **Jitsi Configuration** → **Save** | Field Company hilang; setelah reload tetap tidak tercentang | [AI S-03] Company hilang, tetap tidak tercentang setelah reload | [x] Pass [ ] Fail |
| 2 | Buat meeting baru "UAT Discuss 01", **Save** | **Video Link** berisi link Odoo (`…/calendar/join_videocall/<kode>`), bukan meet.jit.si | [AI S-03] `…/calendar/join_videocall/4e6854fd…`, `jitsi_link` kosong | [x] Pass [ ] Fail |
| 3 | Buka lagi meeting "UAT Jitsi 01" dari T-02 | Video Link-nya **tetap** link Jitsi lama (tidak berubah otomatis — perilaku 19.0 dipertahankan) | Tidak dites live oleh AI (hanya dari desain kode: link dihitung ulang hanya bila token berubah) | [ ] Pass [ ] Fail — **tidak dites** (waiver) |
| 4 | (Info, bukan syarat) Buka aplikasi **Discuss** | Di 20.0 meeting "UAT Discuss 01" punya channel sendiri — fitur baru bawaan Odoo 20, bukan dari modul ini (RMV-02) | [AI S-03] Channel Discuss dibuat (fitur native 20.0) | [x] Pass [ ] Fail |
| 5 | Nyalakan kembali Jitsi (**centang + Save**) untuk T-04/T-05 | Tersimpan | [AI S-04 setup] Tersimpan | [x] Pass [ ] Fail |

### T-04: Perilaku lama yang sengaja dipertahankan

**Data dummy:** company kedua "PT Doodex Indonesia".

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | **Settings → Calendar → Jitsi → Company** = "PT Doodex Indonesia" → Save; buat meeting "UAT Spasi" | Link: `https://meet.jit.si/PT Doodex Indonesia/PT Doodex Indonesia-<kode>` — nama masuk apa adanya (dengan spasi) dan muncul 2× | [AI Step 9 `test_ac_06_01`, automated — bukan lewat UI] spasi mentah, nama 2× | [x] Pass [ ] Fail |
| 2 | Pindah ke company lain (switcher company kanan atas), buat meeting "UAT Company Lain" | Link tetap memakai nama company yang dipilih di Settings, bukan company aktif | [AI Step 9 `test_ac_05_01`, automated `with_company` — bukan switcher UI] tetap nama company Settings | [x] Pass [ ] Fail |
| 3 | Kembalikan Company Jitsi ke company utama → Save | Tersimpan | N/A (langkah reset) | — |

### T-05: Email booking appointment TIDAK berisi link Jitsi (perilaku lama, sengaja dipertahankan) 🔴

**Data dummy:** booking atas nama "UAT Customer", email yang bisa Anda buka.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Dari halaman portal/website appointment, booking Appointment Type "Demo Jitsi" | Booking berhasil, meeting terbentuk di Calendar dengan Video Link Jitsi | Tidak dites — AI tidak melakukan booking portal nyata | [ ] Pass [ ] Fail — **tidak dites** (waiver) |
| 2 | Buka email konfirmasi booking yang diterima | Email berisi tombol **Join/View** dan link "Video meeting" ke alamat **Odoo** — **TIDAK** ada tulisan/link `meet.jit.si` | [AI S-04, via **Preview template** di 20.0 dan 19.0, bukan email nyata] link hanya ke Odoo, tidak ada meet.jit.si | [x] Pass (terbatas: Preview) [ ] Fail |

> Kalau link `meet.jit.si` MUNCUL di email: itu perubahan perilaku tidak disengaja → tandai Fail dan laporkan. (Catatan: link "Video meeting" Odoo sendiri bisa meneruskan ke ruang Jitsi saat diklik — itu perilaku bawaan Odoo, sama seperti 19.0.)

### T-06: Item yang TIDAK bisa dites lewat tampilan biasa (informasi, bukan kegagalan)

- **Isi manual System Parameter `is_jitsi_param`** (Developer Mode → Technical → System Parameters) dengan `False`/`0`: di 20.0 dibaca **nonaktif**, di 19.0 dibaca aktif. Perubahan disengaja, **sudah disetujui** (MF-01, `BSL-023`). Jalur normal lewat Settings tidak terpengaruh.
- **Checkbox "Enable Jitsi Integration" per event** (`is_jitsi`) tidak tampil di form dan tidak menentukan link — hanya setting global (`BSL-020`).
- **Tombol "generate/clear Jitsi link"** tidak ada di UI (`BSL-008`); halaman `/calendar/join_jitsi/...` tidak ada / 404 (`BSL-016`).
- **Perilaku `create()` lewat kode/API** (format token 36 karakter, `access_token` kiriman caller tidak direset) — sama dengan 19.0 (MF-01 migrasi 18→19).

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario | Status | Catatan |
|---|---|---|---|---|
| 1 | Aktivasi & pemakaian Jitsi | T-01, T-02, T-03 | [x] Pass [ ] Fail | Waiver: bukti AI Step 9/10. Tidak dites: T-02 user non-admin, T-03 #3 |
| 2 | Perilaku lama yang dipertahankan | T-04, T-05, T-06 | [x] Pass [ ] Fail | Waiver: bukti AI Step 9/10. T-04 via automated test (bukan UI); T-05 hanya Preview template — booking portal dan email nyata tidak dites |
| 3 | Instalasi di 20.0 Enterprise | Persiapan | [x] Pass [ ] Fail | G1/Step 9/Step 10: install 20.0 + enterprise20 tanpa ERROR |

## Review Item Out-of-Scope / Perubahan yang Disepakati

Owner mengonfirmasi sadar & menerima:

- [x] **MF-01** — padanan `get_param` di 20.0: nilai manual non-boolean `is_jitsi_param` kini dibaca nonaktif (disetujui via chat 2026-09-24).
- [x] **RMV-01/02/03** (perubahan bawaan Odoo 20): Video Link langsung tampil setelah Save; meeting Discuss otomatis punya channel; gaya tampilan & layout email baru. — diterima implisit lewat penutupan UAT via chat 2026-09-24.
- [x] **Aset App Store** branch rilis 19.0 (banner.gif, icon, index.html, key `images`) **tidak di-port** ke `migration/20.0` (keputusan intake, dijawab dev 2026-09-24) — perlu ditangani saat merge ke branch rilis 20.0.
- [x] Rujukan XML-ID lama di `data/mail_template_data.xml` (file tidak di-load, F-13) dibiarkan apa adanya. — diterima implisit lewat penutupan UAT via chat 2026-09-24.

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal di staging dengan modul `appointment` Enterprise versi final 20.0 (Step 7 N/A karena port kode saja — kalau ternyata ada DB produksi 19.0 yang di-upgrade, perlu Step 7 terpisah).
- [ ] Backup database sebelum instalasi/upgrade.
- [ ] Push branch `migration/20.0` (12+ commit lokal, belum di-push) — manual oleh dev.
- [ ] README/LISEZMOI modul sudah menyebut 20.0 (sudah diperbarui A6); klaim README soal "link di email konfirmasi" tidak akurat (F-13) — sengaja tidak diubah, pertimbangkan koreksi di scope terpisah.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| Owner modul / PM | Kuncoro | 2026-09-24 | Via chat: "UAT diselsaiakn bersarkan AI-test yang sudah ada" — **waiver UAT manual**, sign-off berdasarkan bukti AI Step 9/10 |
| FA | — | — | Tidak ada (single owner) |
| User | — | — | Tidak ada (single owner) |

> **Catatan waiver (transparansi):** sign-off ini TIDAK didasarkan pada eksekusi manual T-01..T-05 oleh owner, melainkan pada bukti otomatis/AI (Step 9: 15/15 test; Step 10: 5 skenario live Playwright + Cross-Version Compare). Kolom Actual diisi AI dengan rujukan bukti tersebut atas permintaan eksplisit owner. **Belum pernah dites siapapun:** T-02 sebagai user non-admin, T-03 #3 (meeting lama tetap link Jitsi), T-05 booking portal + email nyata. Direkomendasikan dicek di staging sebelum go-live (`10_qa/human_qa/01_SMOKE.md`, `04_NEGATIVE.md`).

## Penutupan Migrasi (setelah Sign-off terisi)

- [x] `doc/MIGRATION_CLOSED.md` ditulis: SHA `b460a32`, branch `migration/20.0`, 2026-09-24.
