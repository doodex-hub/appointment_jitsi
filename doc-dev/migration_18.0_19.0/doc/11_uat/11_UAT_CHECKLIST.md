# UAT Checklist — Migrasi appointment_jitsi

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-26

> Kriteria sukses: user (Kuncoro) TIDAK merasakan bedanya dibanding 18.0, **kecuali** dua deviation yang sudah disetujui eksplisit selama migrasi ini (lihat "Review Item Out-of-Scope" di bawah).
>
> **Status:** ✅ Ditutup 2026-08-26 — Kuncoro (owner modul, single owner project ini) mengonfirmasi eksplisit ("Ya, UAT selesai — disetujui") bahwa UAT dianggap selesai, memahami & menerima kedua deviation (`MF-01`, `MF-02`) yang tercatat di dokumen ini. Migrasi `appointment_jitsi` 18.0→19.0 dinyatakan **SELESAI PENUH**.

---

## Persiapan Sebelum UAT

- [x] Modul `appointment_jitsi` versi 19.0 sudah terinstall dan teruji (Step 6 G1 + Step 10, environment `docker-env/docker-compose.19.0.yml`/`.qa.yml`, keduanya sudah di-teardown pasca testing).
- [x] Login sebagai Administrator sudah diverifikasi (tidak ada model/access right baru).
- [x] Data pendukung: minimal 1 company aktif (default "My Company") — sudah dipakai di Step 10.

## Skenario Test (Test Script) — hasil dari Step 10, direkap ulang untuk sign-off

### T-01: Mengaktifkan integrasi Jitsi

| # | Langkah | Expected | Actual (Step 10) | Status |
|---|---|---|---|---|
| 1 | Buka **Settings → Calendar** | Muncul section "Jitsi Configuration" | ✅ Muncul (S-01) | [x] Pass [ ] Fail |
| 2 | Centang checkbox tersebut | Muncul field "Company" tambahan | ✅ Muncul, default "My Company" (S-02) | [x] Pass [ ] Fail |
| 3 | Klik **Save** | Setting tersimpan tanpa error | ✅ Tersimpan (S-02) | [x] Pass [ ] Fail |

### T-02: Membuat meeting dan mendapat link Jitsi

| # | Langkah | Expected | Actual (Step 10) | Status |
|---|---|---|---|---|
| 1 | Buat calendar event baru | Event tersimpan | ✅ (S-03) | [x] Pass [ ] Fail |
| 2 | Baca `jitsi_link`/`videocall_location` | Terisi format `https://meet.jit.si/{company}/{company}-{token}` | ✅ Persis (S-03) | [x] Pass [ ] Fail |

**⚠️ Perhatian khusus T-02 (deviation `MF-01`, WAJIB dikonfirmasi paham & diterima):** token di URL sekarang berformat 36-karakter dengan dash (mis. `ab1ea424-27d5-491c-bc74-ca0e944b235f`), BUKAN lagi 32-karakter tanpa dash seperti di 18.0. Link tetap unik dan tetap berfungsi — ini murni perubahan format kosmetik akibat mekanisme ORM `create()` yang berubah di Odoo 19.0 (lihat `FINDINGS.md` MF-01), BUKAN bug. Efek lain dari deviation ini: kalau seseorang membuat event dengan `is_jitsi=False` DAN menyertakan nilai `access_token` sendiri secara eksplisit lewat kode/API (bukan lewat UI biasa — UI tidak punya field ini), nilai itu SEKARANG tidak lagi otomatis direset ke kosong seperti di 18.0.

### T-03: Email konfirmasi TIDAK menampilkan link Jitsi (perilaku lama, sengaja dipertahankan)

| # | Langkah | Expected | Actual (Step 9) | Status |
|---|---|---|---|---|
| 1 | Appointment di-booking sampai email konfirmasi terkirim | Email terkirim | ✅ Dikonfirmasi via test otomatis | [x] Pass [ ] Fail |
| 2 | Buka isi email konfirmasi | TIDAK ADA link `meet.jit.si` di email | ✅ `muncul_di_body=False` | [x] Pass [ ] Fail |

> **Catatan T-03:** sama seperti di 18.0 — ini SESUAI HARAPAN (bug-for-bug), bukan kegagalan.

## Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Method `generate_jitsi_link()`/`clear_jitsi_link()`** — tidak ada tombol UI, sama seperti 18.0 (`BSL-008`/`BSL-017`).
- **Toggle per-meeting "aktif/tidak aktif Jitsi"** — tidak ada di layar, hanya setting global (`BSL-020`).

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Aktivasi integrasi Jitsi | T-01 | [x] Pass [ ] Fail | |
| 2 | Pembuatan meeting & link Jitsi | T-02 | [x] Pass [ ] Fail | Termasuk deviation `MF-01` — lihat catatan T-02 |
| 3 | Email konfirmasi (perilaku lama dipertahankan) | T-03 | [x] Pass [ ] Fail | |

## Review Item Out-of-Scope

Stakeholder (Kuncoro) perlu mengonfirmasi sadar & menerima item berikut:

- **Diwarisi dari 18.0 (sudah disetujui migrasi sebelumnya):** Email konfirmasi tidak pernah menampilkan link Jitsi (F-13/`[BSL-015]`) — fitur inti yang diklaim modul TIDAK BEKERJA sejak 17.0, tetap tidak bekerja di 19.0. 12 quirk/bug lain (F-01..F-12/`BSL-NNN` terkait) — lihat `01b_BASELINE_SPEC.md`.
- **BARU di migrasi 18.0→19.0 ini (`MF-01`, sudah disetujui dev di Step 6 via ESCALATION real-time):** format `access_token` berubah (32-char hex → 36-char dash) untuk single-record create, dan reset `access_token=False` saat `is_jitsi=False` tidak lagi terjadi untuk single-create. Keputusan: diterima demi mempertahankan `[BSL-009]` (quirk batch-create) tetap utuh — dua-duanya tidak bisa dipertahankan bersamaan di Odoo 19.0 (root cause: perubahan mekanisme `@api.model create` di ORM core, lihat `FINDINGS.md` MF-01 untuk analisis lengkap).
- **BARU di migrasi ini (`MF-02`, fix wajib, sudah diterapkan):** satu record `ir.actions.act_window` dead code/orphaned (`[BSL-022]`) diubah `target="inline"`→`target="current"` karena `inline` dihapus total dari Odoo 19.0 — nol dampak observable (record tidak pernah dipanggil UI manapun).
- [x] Dikonfirmasi diterima — Kuncoro, 2026-08-26 (chat, bersamaan dengan konfirmasi UAT selesai)

## Prasyarat Sebelum Go-Live Produksi

- [x] Rehearsal upgrade sungguhan — **N/A**, sifatnya "port kode saja" (dikonfirmasi `01a_MIGRATION_INTAKE.md` §3).
- [ ] Backup database produksi sebelum instalasi — tetap direkomendasikan sebagai praktik umum.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| Owner modul | Kuncoro | 2026-08-26 | Dikonfirmasi via chat ("Ya, UAT selesai — disetujui") |

> Diisi berdasarkan konfirmasi eksplisit Kuncoro di chat 2026-08-26, bukan diasumsikan sepihak oleh AI.
