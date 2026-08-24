# Findings — appointment_jitsi (migrasi 17.0 → 18.0)

**Modul:** appointment_jitsi
**Migrasi:** 17.0 → 18.0
**Terakhir update:** 2026-08-24

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | Override mail template tidak pernah aktif (dari `F-13` backfill) | 1 | `[DIWARISI-SOURCE]` | **TERTINGGI** | ✅ Keputusan diambil — dipertahankan apa adanya di 18.0 |
| MF-02 | 12 bug/quirk lain dari backfill (`F-01`..`F-12`, kecuali `F-13`) | 1 | `[DIWARISI-SOURCE]` | Bervariasi (lihat `doc-dev/backfill/FINDINGS.md`) | ✅ Keputusan diambil — semua dipertahankan apa adanya di 18.0 |
| MF-03 | Dependency `appointment` Enterprise dikonfirmasi ganda (17.0 & 18.0) | 1 | `[GAP-MIGRASI]` (informasional, bukan blocking) | Sedang | Dikonfirmasi — perlu `enterprise18` untuk dev testing Step 9 |

---

## Detail

### MF-01 — Override mail template tidak pernah aktif (dari `F-13` backfill)
**Ditemukan di:** Step 1 (2026-08-24), diwarisi dari `doc-dev/backfill/FINDINGS.md` F-13 (2026-08-07)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `F-13` (`doc-dev/backfill/FINDINGS.md`), `BSL-015` (`01b_BASELINE_SPEC.md`), `BR-09`/`AC-09-01` (`doc-dev/backfill/spec/`)
**Lokasi:** `__manifest__.py:27-29` (key `"data"`) — `data/mail_template_data.xml` tidak terdaftar.
**Deskripsi:** Fitur inti modul yang diklaim di manifest/README ("email confirmation menampilkan link Jitsi") TIDAK PERNAH aktif di kode 17.0 yang berjalan — dikonfirmasi via test eksekusi nyata saat backfill.
**Dampak di 18.0:** Kalau di-port apa adanya (manifest 18.0 juga tidak mendaftarkan file itu), behavior 18.0 akan identik dengan 17.0 — fitur email tetap tidak aktif. Ini SESUAI prinsip bug-for-bug migration, bukan gap baru akibat migrasi.
**Rekomendasi:** Tidak ada tindakan di scope migrasi ini.
**Keputusan pemilik modul:** ✅ **Dipertahankan apa adanya di 18.0** — dikonfirmasi eksplisit 2026-08-24 (lihat `01a_MIGRATION_INTAKE.md` §Ringkasan poin 3). Perbaikan (kalau diinginkan) adalah scope terpisah di luar migrasi ini.

---

### MF-02 — 12 bug/quirk lain dari backfill (`F-01`..`F-12`, kecuali `F-13`)
**Ditemukan di:** Step 1 (2026-08-24), diwarisi dari `doc-dev/backfill/FINDINGS.md` (2026-08-07)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `F-01` s/d `F-12` (`doc-dev/backfill/FINDINGS.md`), `BSL-005`-`BSL-014`, `BSL-016`-`BSL-021` (`01b_BASELINE_SPEC.md`)
**Deskripsi:** 12 temuan lain dari backfill 17.0 — antara lain F-02 (toggle `is_jitsi` via `write()` tidak memicu recompute), F-03 (`create()` tidak batch-safe), F-04 (`videocall_location` bergantung urutan akses field), F-05 (`company_param` global, bukan per-company), F-06 (controller dead code), F-07 (URL tidak di-slug), F-08 (method manual tidak terhubung UI), F-09 (file HTML nyasar di root modul), F-10 (label field bentrok), F-11 (field `is_jitsi` per-event tidak dipakai di compute), F-12 (dependency Enterprise, lihat juga MF-03 di bawah untuk sisi migrasi-nya). Detail lengkap tiap item ada di `doc-dev/backfill/FINDINGS.md` dan `01b_BASELINE_SPEC.md` §8.
**Dampak di 18.0:** Kalau di-port apa adanya, semua quirk ini tetap ada di 18.0 — konsisten dengan prinsip bug-for-bug migration.
**Rekomendasi:** Tidak ada tindakan di scope migrasi ini untuk semuanya.
**Keputusan pemilik modul:** ✅ **Semua dipertahankan apa adanya di 18.0** — dikonfirmasi eksplisit 2026-08-24 (lihat `01a_MIGRATION_INTAKE.md` §Ringkasan poin 4). Tidak ada fix "sekalian" untuk item manapun di daftar ini selama migrasi berjalan.

---

### MF-03 — Dependency `appointment` Enterprise dikonfirmasi ganda (17.0 & 18.0)
**Ditemukan di:** Step 1 (2026-08-24)
**Tag:** `[GAP-MIGRASI]` (informasional — bukan isu blocking, murni kebutuhan infrastruktur)
**Ref:** `F-12` (`doc-dev/backfill/FINDINGS.md`), `BSL-021` (`01b_BASELINE_SPEC.md`)
**Deskripsi:** Dependency `appointment` dicek langsung isinya di `enterprise17/appointment` dan `enterprise18/appointment` (ADA di keduanya) vs `odoo17/addons` dan `odoo18/addons` (TIDAK ADA di keduanya) — dikonfirmasi Enterprise di KEDUA versi, bukan cuma diasumsikan dari manifest.
**Dampak:** Step 2 (diff analysis) dan Step 9 (dev testing) WAJIB pakai `native-*-enterprise`, bukan Community saja — sudah diantisipasi dan dicatat di `CLAUDE.md` §Folder dan `01a_MIGRATION_INTAKE.md` §2 sejak awal (menghindari lesson `purchase_product_optional` yang telat sadar soal ini).
**Rekomendasi:** Tidak perlu tindakan tambahan — sudah tercatat, tinggal dipakai konsisten di step-step berikutnya.
**Keputusan pemilik modul:** ✅ CONFIRMED, informasional — tidak butuh keputusan lebih lanjut.

---

## Catatan (di luar scope migrasi, tapi dicatat supaya tidak hilang)

Ditemukan saat investigasi Step 1: beberapa repo referensi lokal (`appointment-jitsi-17`, `enterprise18`, dan clone project migrasi lain di `D:\Kuncoro\doodex\repo\`) punya GitHub Personal Access Token tertanam plaintext di `git remote -v`. Bukan finding migrasi `appointment_jitsi`, tidak mempengaruhi kode/behavior modul — dicatat di `CLAUDE.md` §Catatan keamanan supaya dev bisa tindak lanjuti terpisah (rotate token, pindah ke credential helper).
