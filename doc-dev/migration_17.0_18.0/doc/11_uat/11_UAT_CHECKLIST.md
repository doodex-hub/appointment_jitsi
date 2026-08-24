# UAT Checklist — Migrasi appointment_jitsi

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-24

> Kriteria sukses: user (Kuncoro) TIDAK merasakan bedanya dibanding 17.0, kecuali tidak ada satupun yang memang disepakati berubah — migrasi ini murni port kode.
>
> **Kolom Actual/Status di bawah SENGAJA dikosongkan oleh AI** — ini draft test script, dijalankan sendiri dengan tangan oleh Kuncoro (single owner project ini), bukan laporan hasil dari AI/dev testing (yang sudah ada di `09_DEV_TESTING.md`/`10_BUSINESS_FLOW_MIGRATION.md`).

---

## Persiapan Sebelum UAT

- [ ] Modul `appointment_jitsi` versi 18.0 sudah terinstall di environment yang dipakai UAT (bisa pakai environment yang sama seperti Step 9/10 — `docker-env/docker-compose.18.0.yml`, atau environment staging Doodex sendiri kalau sudah tersedia).
- [ ] Login sebagai Administrator (modul ini cuma butuh akses Settings, tidak ada role khusus lain yang perlu diuji — tidak ada model/access right baru).
- [ ] Tidak butuh data pendukung khusus selain: minimal 1 company aktif (default "My Company" cukup).
- [ ] Rekomendasi: pakai database staging/dry-run, bukan database produksi asli.

## Skenario Test (Test Script)

### T-01: Mengaktifkan integrasi Jitsi

**Data dummy yang perlu dientri:** tidak ada data khusus — cukup pakai company default.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka **Settings → Calendar** | Muncul section "Jitsi Configuration" dengan checkbox "Integration video conference with Jitsi" | | [ ] Pass [ ] Fail |
| 2 | Centang checkbox tersebut | Muncul field "Company" tambahan di bawahnya | | [ ] Pass [ ] Fail |
| 3 | Klik **Save** | Setting tersimpan tanpa error/pesan merah | | [ ] Pass [ ] Fail |

### T-02: Membuat meeting dan mendapat link Jitsi

**Data dummy yang perlu dientri:** Subject meeting bebas, mis. "Demo Meeting Jitsi".

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka **Calendar**, klik **New**, isi Meeting Subject "Demo Meeting Jitsi", klik **Save** | Meeting tersimpan | | [ ] Pass [ ] Fail |
| 2 | Buka kembali meeting yang baru dibuat, lihat field "Videocall URL" | Field ini mungkin KOSONG saat pertama dibuka — ini **bukan bug**, memang perilaku dari versi lama (link baru muncul setelah "disentuh" sistem sekali, lihat catatan di bawah) | | [ ] Pass [ ] Fail |
| 3 | Refresh/buka ulang halaman meeting sekali lagi | Field "Videocall URL" sekarang terisi link berformat `https://meet.jit.si/...` | | [ ] Pass [ ] Fail |
| 4 | Klik "Join video call" | Membuka tab baru menuju link Jitsi tersebut | | [ ] Pass [ ] Fail |

### T-03: Email konfirmasi TIDAK menampilkan link Jitsi (perilaku lama, sengaja dipertahankan)

**Data dummy yang perlu dientri:** buat appointment lewat menu Appointments (kalau ada appointment type yang sudah dikonfigurasi), atau lewati skenario ini kalau belum ada appointment type siap pakai di environment UAT.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Booking satu appointment (lewat appointment type manapun yang tersedia) sampai email konfirmasi terkirim | Email konfirmasi terkirim ke peserta | | [ ] Pass [ ] Fail |
| 2 | Buka isi email konfirmasi tersebut | Email HANYA berisi link "Join" standar Odoo (`/calendar/meeting/join?token=...`) — **TIDAK ADA** link `meet.jit.si` di email, walau integrasi Jitsi aktif dan meeting punya link Jitsi valid | | [ ] Pass [ ] Fail |

> **Catatan penting untuk T-03:** hasil "TIDAK ADA link Jitsi di email" ini SESUAI HARAPAN, bukan kegagalan — modul ini punya keterbatasan yang sudah ada sejak versi lama (17.0) dan sengaja dipertahankan di migrasi ini (lihat `FINDINGS.md` MF-01). Kalau suatu saat ingin diperbaiki supaya email BENAR-BENAR menampilkan link Jitsi, itu perubahan terpisah di luar migrasi ini.

## Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Method `generate_jitsi_link()`/`clear_jitsi_link()`** — ada di dalam kode modul tapi tidak ada tombol di layar manapun untuk memicunya. Ini sudah begitu sejak versi lama (`BSL-008`/`BSL-017`), bukan sesuatu yang hilang saat migrasi.
- **Toggle per-meeting "aktif/tidak aktif Jitsi"** — tidak ada di layar; integrasi Jitsi HANYA dikontrol oleh setting global di Settings (T-01), berlaku untuk SEMUA meeting sekaligus. Field internal `is_jitsi` per-meeting ada di database tapi tidak menentukan apa-apa dari sisi tampilan (`BSL-020`).

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Aktivasi integrasi Jitsi | T-01 | [ ] Pass [ ] Fail | |
| 2 | Pembuatan meeting & link Jitsi | T-02 | [ ] Pass [ ] Fail | |
| 3 | Email konfirmasi (perilaku lama dipertahankan) | T-03 | [ ] Pass [ ] Fail | |

## Review Item Out-of-Scope

Stakeholder (Kuncoro) mengonfirmasi sadar & menerima bahwa item berikut SENGAJA tidak diperbaiki di migrasi ini (bug-for-bug, lihat `03_MIGRATION_SPEC.md` §4 dan `FINDINGS.md`):

- Email konfirmasi tidak pernah menampilkan link Jitsi (F-13/MF-01) — fitur inti yang diklaim modul TIDAK BEKERJA sejak 17.0, tetap tidak bekerja di 18.0.
- 12 quirk/bug lain (F-01..F-12) — lihat `doc-dev/backfill/FINDINGS.md` untuk detail lengkap tiap satu.
- [ ] Dikonfirmasi diterima — ...

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal upgrade sungguhan — **N/A untuk migrasi ini**, sifatnya "port kode saja" (instalasi baru di 18.0), bukan upgrade instance dengan data produksi (`01a_MIGRATION_INTAKE.md` §3).
- [ ] Backup database produksi sebelum instalasi — tetap direkomendasikan sebagai praktik umum sebelum instalasi modul apapun di lingkungan produksi.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| Owner modul | | | |

> Kosongkan sampai Kuncoro benar-benar menjalankan T-01/T-02/T-03 dengan tangan sendiri dan menyetujui.
