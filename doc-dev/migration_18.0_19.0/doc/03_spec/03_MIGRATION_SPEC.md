# Migration Spec (Teknis) — appointment_jitsi

**Step:** 3 — Migration Spec
**Versi:** 18.0 → 19.0
**Ref:** `02_diff/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-26

> Dokumen ini memandu IMPLEMENTASI (step 6). Ini **bukan** dasar testing/acceptance criteria — itu datang dari `01b_BASELINE_SPEC.md`. Lihat step 5.

---

## 1. Ringkasan Strategi

**Port langsung (copy 1:1), nyaris tanpa perubahan kode.** `02_DIFF_ANALYSIS.md` mengonfirmasi hampir semua simbol native yang dipakai modul byte-identical 18.0→19.0, dependency Enterprise `appointment` tetap ada. Perubahan wajib: housekeeping manifest (bump versi). **Tidak ada rewrite disengaja, tidak ada perbaikan bug** — seluruh 21 klaim `BSL-NNN` di `01b_BASELINE_SPEC.md` di-port apa adanya, sesuai kebijakan bug-for-bug dev.

**Pengecualian yang perlu perhatian (bukan perubahan kode, tapi perubahan PROSES verifikasi):** `MF-01`/`DIFF-01` — mekanisme `@api.model create` berubah di ORM core 19.0 (`model_create_multi` menggantikan `model_create_single`). Keputusan: **`create()` TETAP di-port 1:1** (tidak diubah ke `@api.model_create_multi` atau logic lain) di Step 6 ini, TAPI Step 9 WAJIB menjalankan ulang 13 test existing dan membandingkan hasil per-assertion untuk `[BSL-005]`/`[BSL-009]` — bukan diasumsikan otomatis identik seperti migrasi 17.0→18.0. Kalau test menunjukkan observable behavior berubah, itu dicatat sebagai "perubahan wajib demi kompatibilitas 19.0" (diperbolehkan `CLAUDE.md` §Source of Truth) — BUKAN eskalasi blocking, karena satu-satunya cara mempertahankan behavior 100% identik adalah rewrite total `create()` yang justru lebih berisiko (rewrite demi rewrite, dilarang `CLAUDE.md`).

## 2. Strategi per File/Simbol

| File/simbol | Ref `DIFF-NNN` | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `__manifest__.py` | DIFF-06 | Copy apa adanya, HANYA ubah `"version": "18.0.1.0.0"` → `"19.0.1.0.0"`. **JANGAN** tambahkan `"data/mail_template_data.xml"` ke list `"data"` (lihat `[BSL-015]`). | Rendah | `BSL-015` |
| `models/calendar_event.py` (`CalendarEvent`) | **DIFF-01** (⚠️), DIFF-02 | Copy apa adanya — `create()` override TETAP `@api.model` (single-record signature, TIDAK diubah). `_compute_jitsi_link`/`generate_jitsi_link`/`clear_jitsi_link`/`action_join_video_call` tetap identik. **WAJIB verifikasi empiris Step 9** untuk `create()` — lihat §1 di atas dan `FINDINGS.md` MF-01. | **Sedang** (naik dari Rendah di 17.0→18.0) — mekanisme decorator berubah, dampak observable belum pasti sampai Step 9 | `BSL-005`-`BSL-011`, `BSL-020` |
| `models/calendar_event.py` (`ResConfigSettings`) | — | Copy apa adanya — field `is_jitsi`/`company_param` dengan `config_parameter=` tetap sama. | Rendah | `BSL-012` |
| `views/calendar_views.xml` | DIFF-03 | Copy apa adanya — xpath anchor `sync_google_calendar_setting` dan syntax `invisible="not is_jitsi"` sudah kompatibel 19.0, tidak perlu diubah. | Rendah | `BSL-001` |
| `data/mail_template_data.xml` | DIFF-04, DIFF-05 | Copy apa adanya (file tetap ADA di folder, TETAP TIDAK didaftarkan di manifest). XML-ID target dikonfirmasi masih ada di 19.0. | Rendah (risiko proses: "jangan sampai keceplosan didaftarkan") | `BSL-015` |
| `controllers/appointment.py`, `controllers/__init__.py` | — | Copy apa adanya — seluruh isi tetap di-comment-out, import no-op tetap dipertahankan. | Rendah | `BSL-016` |
| `security/ir.model.access.csv` | — | Copy apa adanya (cuma header). | Rendah | — |
| `README.md` | — | Update baris "Compatibility: Odoo version: 18.0 Enterprise Edition" → "19.0 Enterprise Edition" (housekeeping teks). | Rendah | — |
| `googleaeed8a7b9ec156e7.html` | — | Copy apa adanya (di luar scope perubahan). | Rendah | `BSL-018` |
| `__init__.py` (root), `models/__init__.py`, `controllers/__init__.py` | — | Copy apa adanya. | Rendah | — |
| `tests/__init__.py`, `tests/test_appointment_jitsi.py` | — | Copy apa adanya (13 test `TransactionCase`), dijalankan ulang terhadap 19.0 di Step 9 — **prioritas tinggi karena MF-01**, bandingkan per-assertion, bukan cuma count PASS. | **Sedang** (lihat MF-01) | Semua `BSL-NNN` |
| `static/description/*`, `LICENSE`, `LISEZMOI.md` | — | Copy apa adanya, tidak ada perubahan. | Rendah | — |

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers
*(Mencegah instalasi atau operasi inti di 19.0)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version harus `19.0.x.x.x` | `__manifest__.py` | Housekeeping standar |

**Priority:** HIGH secara prosedural, risiko teknis RENDAH — tidak ada blocker install lain (`02_DIFF_ANALYSIS.md` §4, DIFF-08/09 N/A).

### OWL Widget yang Butuh Rewrite/Review

**N/A** — modul tidak punya komponen Owl/JS.

### Controller & Route

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `controllers/appointment.py` seluruhnya dead code — tetap dipertahankan apa adanya | `controllers/appointment.py` | Rendah |

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Dependency `appointment` (Enterprise) tetap ada tidak berubah di 19.0 | `__manifest__.py` | Rendah — dikonfirmasi DIFF-06 |
| 2 | Dev testing (Step 9) butuh mount `enterprise19.0` (folder gabungan Community+Enterprise, BUKAN git repo) sebagai extra addons path — beda struktur dari 18.0 (`odoo18`+`enterprise18` dua clone) | `docker-env/docker-compose.yml` (kalau di-reuse dari project sebelumnya) | Sedang — infrastruktur |

### Kompatibilitas Data Model

**Tidak ada** — modul tidak menambah model baru, field yang ditambahkan (`jitsi_link`, `is_jitsi`, `company_param`) tidak berubah tipe/struktur di 19.0 (murni field modul sendiri).

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Override 2 mail template BAWAAN tidak pernah aktif (by design, `[BSL-015]`) — pastikan Step 6 TIDAK "memperbaiki" ini secara tidak sengaja | `__manifest__.py`, `data/mail_template_data.xml` | **Tinggi** (risiko proses) |
| 2 | **`MF-01`** — mekanisme `@api.model create` berubah di ORM core 19.0, dampak observable ke `[BSL-005]`/`[BSL-009]` belum diverifikasi empiris | `models/calendar_event.py` | **Tinggi** — WAJIB jadi prioritas #1 di Step 9, lihat urutan testing di bawah |

### Urutan Prioritas Testing (Step 9, mengikuti `01b_BASELINE_SPEC.md`)

1. Install & startup — manifest ter-bump, modul ter-install bersih di atas Odoo 19 Enterprise + `enterprise19.0` mounted
2. **`[BSL-005]`/`[BSL-009]` create() — PRIORITAS TERTINGGI (MF-01):** jalankan test create single-dict DAN batch, bandingkan `access_token`/`jitsi_link` hasil vs baseline 18.0 satu per satu assertion
3. `[BSL-002]` core flow — toggle setting global, buat event, cek `jitsi_link`/`videocall_location` terisi format yang benar
4. `[BSL-015]` — verifikasi ulang tetap direproduksi (email TETAP tidak menampilkan link Jitsi) — test POSITIF (konfirmasi bug-for-bug berhasil)
5. Sisa `BSL-010`-`BSL-014`, `BSL-016`-`BSL-021` — quirk lain, re-run 13 test existing sebagai regression check

### View List (dulu Tree) Checklist

**N/A** — tidak ada `<tree>`/list view di modul ini.

### Estimasi Effort

| Area | Effort | Catatan |
|---|---|---|
| Code migration (Step 6) | **Sangat kecil** (< 1 jam) | Copy folder + bump versi manifest + update README |
| Dev testing (Step 9) | **Sedang-Tinggi** (naik dari Sedang di 17.0→18.0) | Environment (mount `enterprise19.0`) + verifikasi detail MF-01 per-assertion, bukan cuma count PASS |
| Sisa step (4,5,8,10,11) | **Kecil-sedang** | Mengikuti pola `01b_BASELINE_SPEC.md` yang sudah solid |

## 3. Data Migration

N/A — sifat migrasi "port kode saja" (dikonfirmasi `01a_MIGRATION_INTAKE.md` §3). Step 7 di-skip.

## 4. Scope

### Termasuk
- Port seluruh file modul apa adanya ke struktur 19.0.
- Bump versi manifest `18.0.1.0.0` → `19.0.1.0.0`.
- Update baris "Compatibility" di `README.md` (18.0 → 19.0 Enterprise Edition).
- Port 13 test `TransactionCase` yang sudah ada, dijalankan ulang terhadap 19.0 di Step 9 dengan perhatian khusus MF-01.

### Di Luar Scope (sengaja, disetujui di intake)
- Memperbaiki `[BSL-015]`/F-13 (mendaftarkan `data/mail_template_data.xml` di manifest).
- Memperbaiki bug/quirk lain (`BSL-009`-`BSL-014`, `BSL-016`-`BSL-020`).
- Rewrite `create()` ke `@api.model_create_multi` secara proaktif — TIDAK dilakukan di Step 6 ini; keputusan ditunda sampai hasil Step 9 empiris menunjukkan apakah perubahan observable benar-benar terjadi dan apakah itu perlu ditangani.
- Menghapus `controllers/appointment.py` dead code atau file `googleaeed8a7b9ec156e7.html` yang nyasar.
