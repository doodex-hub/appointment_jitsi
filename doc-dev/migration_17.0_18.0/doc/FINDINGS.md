# Findings — appointment_jitsi (migrasi 17.0 → 18.0)

**Modul:** appointment_jitsi
**Migrasi:** 17.0 → 18.0
**Terakhir update:** 2026-10-02

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | Override mail template tidak pernah aktif (dari `F-13` backfill) | 1 | `[DIWARISI-SOURCE]` | **TERTINGGI** | ✅ Keputusan diambil — dipertahankan apa adanya di 18.0 |
| MF-02 | 12 bug/quirk lain dari backfill (`F-01`..`F-12`, kecuali `F-13`) | 1 | `[DIWARISI-SOURCE]` | Bervariasi (lihat `doc-dev/backfill/FINDINGS.md`) | ✅ Keputusan diambil — semua dipertahankan apa adanya di 18.0 |
| MF-03 | Dependency `appointment` Enterprise dikonfirmasi ganda (17.0 & 18.0) | 1 | `[GAP-MIGRASI]` (informasional, bukan blocking) | Sedang | Dikonfirmasi — perlu `enterprise18` untuk dev testing Step 9 |
| MF-04 | `action_join_video_call()` bertabrakan nama dengan method core `calendar.event`, tidak tercatat di backfill | 8 | `[DIWARISI-SOURCE]` | Rendah | ✅ Diverifikasi benign, pre-existing sejak 17.0 |
| MF-05 | `static/description/assets/icons/bullet-diamond.png` tidak pernah ter-commit di branch rilis 18.0 — 28 ikon bullet di halaman Store rusak | pasca-rilis | `[DIWARISI-SOURCE]` | Rendah | ✅ RESOLVED 2026-10-02 — aset ditambahkan, rilis 18.0.1.0.1 |
| MF-06 | Temuan review pasca-rilis (kosmetik/kode mati): `ir.model.access.csv` kosong & tak terdaftar, README merujuk `LICENSE` yang dibuang di staging, `description` manifest menyesatkan | pasca-rilis | `[DIWARISI-SOURCE]` | Rendah | Dicatat, TIDAK diperbaiki (di luar lingkup rilis) |
| MF-07 | Ringkasan hotfix rilis 18.0.1.0.1 (2026-10-02) | pasca-rilis | — | — | ✅ Terkirim: staging/18.0 c54931a→40b4456 · 18.0 50b7324→a859b8a |

---

## Detail

### MF-01 — Override mail template tidak pernah aktif (dari `F-13` backfill)
> **Update 2026-10-02:** diverifikasi di kode rilis `origin/18.0` — manifest `data` masih hanya `views/calendar_views.xml`; `mail_template_data.xml` tetap tidak terdaftar. Status tidak berubah (dipertahankan).

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

### MF-04 — `action_join_video_call()` bertabrakan nama dengan method core `calendar.event`
**Ditemukan di:** Step 8 (2026-08-24) — cek kolisi method wajib (`08_CODE_REVIEW.md` §D Arah 1)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `08_review/08_CODE_REVIEW.md` §D
**Lokasi:** `models/calendar_event.py:61-69` (modul) vs `odoo18/addons/calendar/models/calendar_event.py:1035` (core, juga ada identik di `odoo17` baris 985)
**Deskripsi:** Modul mendefinisikan `action_join_video_call()` pada `calendar.event` — nama PERSIS SAMA dengan method core yang sudah ada di `calendar.event` SEJAK 17.0 (bukan baru muncul di 18.0). Modul TIDAK memanggil `super()`, jadi override-nya total lewat MRO. Tidak pernah tercatat sebagai finding terpisah di backfill (`doc-dev/backfill/FINDINGS.md` F-01..F-13).
**Dampak:** Diverifikasi via baca isi core (byte-identical 17.0/18.0): core hanya `return {'type': 'ir.actions.act_url', 'url': self.videocall_location, 'target': 'new'}` — tidak ada side-effect lain yang hilang akibat override total ini. **Tidak ada dampak fungsional**, dan karena core identik di kedua versi, tidak ada risiko baru dari migrasi.
**Rekomendasi:** Tidak ada tindakan — dicatat murni untuk melengkapi audit trail collision-check yang terlewat di backfill.
**Keputusan pemilik modul:** ✅ CONFIRMED benign, informasional — tidak butuh keputusan lebih lanjut.

---

### MF-05 — Aset `bullet-diamond.png` hilang di rilis 18.0
**Ditemukan di:** review pasca-rilis (2026-10-02) · **Tag:** `[DIWARISI-SOURCE]`
**Lokasi:** `appointment_jitsi/static/description/index.html` — 28 rujukan `./assets/icons/bullet-diamond.png`
**Deskripsi:** File tidak ada di `origin/18.0` (maupun `origin/staging/18.0`), sehingga halaman deskripsi Odoo Store menampilkan ikon rusak. Rilis 20.0 sudah memiliki file ini; `index.html` di 18.0 merujuknya sejak commit "update index.html".
**Resolusi:** PNG yang sama (blob `df95bbc`, 1012 byte) diambil dari `origin/20.0` dan ditambahkan; semua rujukan lokal `index.html` diverifikasi ada. Tanpa perubahan kode. Versi modul di-bump patch ke `18.0.1.0.1`. Kode Python/XML tidak berubah.
**Keputusan pemilik modul:** ✅ Disetujui (lingkup A, chat 2026-10-02).

---

### MF-06 — Temuan review pasca-rilis, tidak diperbaiki
**Ditemukan di:** review pasca-rilis (2026-10-02) · **Tag:** `[DIWARISI-SOURCE]`
1. `security/ir.model.access.csv` hanya berisi header dan tidak terdaftar di manifest `data`. Modul tidak punya model baru, jadi tidak ada celah akses.
2. `appointment_jitsi/README.md` menulis "licensed under LGPLv3 (./LICENSE)", padahal `LICENSE` sengaja dibuang di branch staging/rilis — tautan rusak di rilis.
3. `description` manifest menyebut "Jitsi API" dan "Customizes the appointment confirmation email", padahal tidak ada pemanggilan API dan email tidak pernah aktif (F-13: `data/mail_template_data.xml` tidak terdaftar di manifest — diverifikasi MASIH begitu di rilis 18.0).
**Rekomendasi:** perbaiki bersama keputusan produk F-13 (daftarkan atau hapus template email); sisanya kosmetik.
**Keputusan pemilik modul:** *(kosong — belum diputuskan; lingkup rilis dibatasi aset saja)*

---

### MF-07 — Ringkasan hotfix rilis 18.0.1.0.1
**Tanggal:** 2026-10-02 · **Alur:** hotfix dari `origin/staging/18.0` → `staging/18.0` → `18.0` (ff-only, tanpa force)
**Perubahan:** tambah `bullet-diamond.png` + bump versi `18.0.1.0.1` (2 commit, 2 file).
**Bukti:** semua gambar lokal yang dirujuk `index.html` ada di commit hotfix; `git diff origin/staging/18.0 origin/18.0` kosong; file terlarang 0; `banner.png` 0; manifest `images` = banner.gif + icon.png.
**Hash:** staging/18.0 c54931a→40b4456 · 18.0 50b7324→a859b8a
**Belum teruji:** tampilan di apps.odoo.com (menunggu Store memuat ulang; belum diketahui apakah bump patch diperlukan). Tidak ada uji Docker karena tidak ada perubahan kode.
**Catatan audit:** 20.0 tidak diubah; dokumen ini tidak di-push dari branch rilis.

---

## Catatan (di luar scope migrasi, tapi dicatat supaya tidak hilang)

Ditemukan saat investigasi Step 1: beberapa repo referensi lokal (`appointment-jitsi-17`, `enterprise18`, dan clone project migrasi lain di `D:\Kuncoro\doodex\repo\`) punya GitHub Personal Access Token tertanam plaintext di `git remote -v`. Bukan finding migrasi `appointment_jitsi`, tidak mempengaruhi kode/behavior modul — dicatat di `CLAUDE.md` §Catatan keamanan supaya dev bisa tindak lanjuti terpisah (rotate token, pindah ke credential helper).
