# UAT Checklist — Migrasi appointment_jitsi (19.0 → 20.0)

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`, `FINDINGS.md`
**Tanggal draft:** 2026-09-24
**Status:** ✅ Draft siap dijalankan — ⏳ menunggu eksekusi & sign-off dev/owner (Kuncoro)

> Kriteria sukses: pemakai TIDAK merasakan bedanya dibanding 19.0, **kecuali** item yang sudah disetujui berubah (lihat "Review Item Out-of-Scope").
>
> Dokumen ini adalah **skrip test untuk dijalankan sendiri** oleh owner/business user. Kolom **Actual** dan **Status** sengaja kosong — diisi oleh orang yang menjalankan, bukan oleh AI. Hasil test AI (Step 9/10) ada di dokumen masing-masing dan bukan pengganti UAT ini.

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
| 1 | Buka **Settings → Calendar** | Di bawah "Outlook Calendar" / "Google Calendar" ada blok **"Jitsi Configuration"**; field **Company** belum terlihat | | [ ] Pass [ ] Fail |
| 2 | Centang **Jitsi Configuration** | Field **Company** muncul, terisi company aktif | | [ ] Pass [ ] Fail |
| 3 | Klik **Save** | Tersimpan tanpa error; setelah halaman reload tetap tercentang & Company tetap terisi | | [ ] Pass [ ] Fail |

### T-02: Membuat meeting dan join lewat Jitsi

**Data dummy:** Meeting Subject = "UAT Jitsi 01".

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | **Calendar → Meetings → New**, isi Meeting Subject, jangan ubah field lain, **Save** | Tersimpan tanpa error | | [ ] Pass [ ] Fail |
| 2 | Lihat field **Video Link** | Berisi `https://meet.jit.si/<Nama Company>/<Nama Company>-<kode>` (di 20.0 langsung tampil; di 19.0 dulu perlu reload — RMV-01) | | [ ] Pass [ ] Fail |
| 3 | Klik ikon **Join** (panah masuk kotak) di samping Video Link | Tab baru terbuka ke alamat yang **sama persis** dengan Video Link dan ruang Jitsi terbuka | | [ ] Pass [ ] Fail |
| 4 | Buat meeting kedua "UAT Jitsi 02" | Video Link-nya beda kode dari meeting pertama (unik per meeting) | | [ ] Pass [ ] Fail |

### T-03: Mematikan Jitsi → kembali ke Odoo Discuss

**Data dummy:** Meeting Subject = "UAT Discuss 01".

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | **Settings → Calendar** → hilangkan centang **Jitsi Configuration** → **Save** | Field Company hilang; setelah reload tetap tidak tercentang | | [ ] Pass [ ] Fail |
| 2 | Buat meeting baru "UAT Discuss 01", **Save** | **Video Link** berisi link Odoo (`…/calendar/join_videocall/<kode>`), bukan meet.jit.si | | [ ] Pass [ ] Fail |
| 3 | Buka lagi meeting "UAT Jitsi 01" dari T-02 | Video Link-nya **tetap** link Jitsi lama (tidak berubah otomatis — perilaku 19.0 dipertahankan) | | [ ] Pass [ ] Fail |
| 4 | (Info, bukan syarat) Buka aplikasi **Discuss** | Di 20.0 meeting "UAT Discuss 01" punya channel sendiri — fitur baru bawaan Odoo 20, bukan dari modul ini (RMV-02) | | [ ] Pass [ ] Fail |
| 5 | Nyalakan kembali Jitsi (**centang + Save**) untuk T-04/T-05 | Tersimpan | | [ ] Pass [ ] Fail |

### T-04: Perilaku lama yang sengaja dipertahankan

**Data dummy:** company kedua "PT Doodex Indonesia".

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | **Settings → Calendar → Jitsi → Company** = "PT Doodex Indonesia" → Save; buat meeting "UAT Spasi" | Link: `https://meet.jit.si/PT Doodex Indonesia/PT Doodex Indonesia-<kode>` — nama masuk apa adanya (dengan spasi) dan muncul 2× | | [ ] Pass [ ] Fail |
| 2 | Pindah ke company lain (switcher company kanan atas), buat meeting "UAT Company Lain" | Link tetap memakai nama company yang dipilih di Settings, bukan company aktif | | [ ] Pass [ ] Fail |
| 3 | Kembalikan Company Jitsi ke company utama → Save | Tersimpan | | [ ] Pass [ ] Fail |

### T-05: Email booking appointment TIDAK berisi link Jitsi (perilaku lama, sengaja dipertahankan) 🔴

**Data dummy:** booking atas nama "UAT Customer", email yang bisa Anda buka.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Dari halaman portal/website appointment, booking Appointment Type "Demo Jitsi" | Booking berhasil, meeting terbentuk di Calendar dengan Video Link Jitsi | | [ ] Pass [ ] Fail |
| 2 | Buka email konfirmasi booking yang diterima | Email berisi tombol **Join/View** dan link "Video meeting" ke alamat **Odoo** — **TIDAK** ada tulisan/link `meet.jit.si` | | [ ] Pass [ ] Fail |

> Kalau link `meet.jit.si` MUNCUL di email: itu perubahan perilaku tidak disengaja → tandai Fail dan laporkan. (Catatan: link "Video meeting" Odoo sendiri bisa meneruskan ke ruang Jitsi saat diklik — itu perilaku bawaan Odoo, sama seperti 19.0.)

### T-06: Item yang TIDAK bisa dites lewat tampilan biasa (informasi, bukan kegagalan)

- **Isi manual System Parameter `is_jitsi_param`** (Developer Mode → Technical → System Parameters) dengan `False`/`0`: di 20.0 dibaca **nonaktif**, di 19.0 dibaca aktif. Perubahan disengaja, **sudah disetujui** (MF-01, `BSL-023`). Jalur normal lewat Settings tidak terpengaruh.
- **Checkbox "Enable Jitsi Integration" per event** (`is_jitsi`) tidak tampil di form dan tidak menentukan link — hanya setting global (`BSL-020`).
- **Tombol "generate/clear Jitsi link"** tidak ada di UI (`BSL-008`); halaman `/calendar/join_jitsi/...` tidak ada / 404 (`BSL-016`).
- **Perilaku `create()` lewat kode/API** (format token 36 karakter, `access_token` kiriman caller tidak direset) — sama dengan 19.0 (MF-01 migrasi 18→19).

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario | Status | Catatan |
|---|---|---|---|---|
| 1 | Aktivasi & pemakaian Jitsi | T-01, T-02, T-03 | [ ] Pass [ ] Fail | |
| 2 | Perilaku lama yang dipertahankan | T-04, T-05, T-06 | [ ] Pass [ ] Fail | |
| 3 | Instalasi di 20.0 Enterprise | Persiapan | [ ] Pass [ ] Fail | |

## Review Item Out-of-Scope / Perubahan yang Disepakati

Owner mengonfirmasi sadar & menerima:

- [ ] **MF-01** — padanan `get_param` di 20.0: nilai manual non-boolean `is_jitsi_param` kini dibaca nonaktif (disetujui via chat 2026-09-24).
- [ ] **RMV-01/02/03** (perubahan bawaan Odoo 20): Video Link langsung tampil setelah Save; meeting Discuss otomatis punya channel; gaya tampilan & layout email baru.
- [ ] **Aset App Store** branch rilis 19.0 (banner.gif, icon, index.html, key `images`) **tidak di-port** ke `migration/20.0` (keputusan intake) — perlu ditangani saat merge ke branch rilis 20.0.
- [ ] Rujukan XML-ID lama di `data/mail_template_data.xml` (file tidak di-load, F-13) dibiarkan apa adanya.

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal di staging dengan modul `appointment` Enterprise versi final 20.0 (Step 7 N/A karena port kode saja — kalau ternyata ada DB produksi 19.0 yang di-upgrade, perlu Step 7 terpisah).
- [ ] Backup database sebelum instalasi/upgrade.
- [ ] Push branch `migration/20.0` (9+ commit lokal, belum di-push) — manual oleh dev.
- [ ] README/LISEZMOI modul sudah menyebut 20.0 (sudah diperbarui A6); klaim README soal "link di email konfirmasi" tidak akurat (F-13) — sengaja tidak diubah, pertimbangkan koreksi di scope terpisah.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| Owner modul / PM | | | |
| FA | | | |
| User | | | |

> Kosongkan sampai skenario T-01..T-05 benar-benar dijalankan sendiri.

## Penutupan Migrasi (setelah Sign-off terisi)

- [ ] `doc/MIGRATION_CLOSED.md` ditulis dengan SHA HEAD `migration/20.0` + tanggal (AI bisa menuliskannya setelah Anda konfirmasi sign-off).
