# Migration Spec (Teknis) — appointment_jitsi

**Step:** 3 — Migration Spec
**Versi:** 17.0 → 18.0
**Ref:** `02_diff/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-24

> Dokumen ini memandu IMPLEMENTASI (step 6). Ini **bukan** dasar testing/acceptance criteria — itu datang dari `01b_BASELINE_SPEC.md`. Lihat step 5.

---

## 1. Ringkasan Strategi

**Port langsung (copy 1:1), nyaris tanpa perubahan kode.** `02_DIFF_ANALYSIS.md` mengonfirmasi tidak ada satu pun breaking change 17→18 yang berdampak ke modul ini (semua simbol native yang dipakai byte-identical, dependency Enterprise `appointment` tetap ada di kedua versi). Satu-satunya perubahan wajib adalah housekeeping manifest (bump versi). **Tidak ada rewrite, tidak ada perbaikan bug** — seluruh 21 klaim `BSL-NNN` di `01b_BASELINE_SPEC.md` (termasuk 13 quirk/bug F-01..F-13) di-port apa adanya, sesuai keputusan bug-for-bug dev (`FINDINGS.md` MF-01/MF-02).

## 2. Strategi per File/Simbol

| File/simbol | Ref `DIFF-NNN` | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `__manifest__.py` | DIFF-06 | Copy apa adanya, HANYA ubah `"version": "17.0.1.0.0"` → `"18.0.1.0.0"`. **JANGAN** tambahkan `"data/mail_template_data.xml"` ke list `"data"` (lihat `[BSL-015]`/MF-01). | Rendah | `BSL-015` |
| `models/calendar_event.py` (`CalendarEvent`) | DIFF-01, DIFF-02 | Copy apa adanya — `create()` override tetap `@api.model` (single-record, TIDAK diubah ke `@api.model_create_multi`), `_compute_jitsi_link`/`generate_jitsi_link`/`clear_jitsi_link`/`action_join_video_call` tetap identik. | Rendah — dikonfirmasi wrapper deprecated `_model_create_single` masih didukung 18.0 (DIFF-01) | `BSL-005`-`BSL-011`, `BSL-020` |
| `models/calendar_event.py` (`ResConfigSettings`) | — | Copy apa adanya — field `is_jitsi`/`company_param` dengan `config_parameter=` tetap sama. | Rendah | `BSL-012` |
| `views/calendar_views.xml` | DIFF-03 | Copy apa adanya — xpath anchor `sync_google_calendar_setting` dan syntax `invisible="not is_jitsi"` sudah kompatibel 18.0, tidak perlu diubah. | Rendah | `BSL-001` |
| `data/mail_template_data.xml` | DIFF-04, DIFF-05 | Copy apa adanya (file tetap ADA di folder, TAPI tetap TIDAK didaftarkan di manifest — lihat baris `__manifest__.py` di atas). XML-ID target (`calendar.calendar_template_meeting_update`, `appointment.appointment_booked_mail_template`) dikonfirmasi masih ada di 18.0, jadi kalaupun didaftarkan file ini tidak akan gagal parse — tapi TETAP tidak didaftarkan sesuai keputusan dev. | Rendah (secara teknis file valid; risiko proses adalah "jangan sampai keceplosan didaftarkan") | `BSL-015` |
| `controllers/appointment.py`, `controllers/__init__.py` | — | Copy apa adanya — seluruh isi tetap di-comment-out, import no-op tetap dipertahankan. | Rendah | `BSL-016` |
| `security/ir.model.access.csv` | — | Copy apa adanya (cuma header, tidak ada baris akses — tidak ada model baru). | Rendah | — |
| `README.md` | — | Update "Compatibility: Odoo version: 17.0 Enterprise Edition" → "18.0 Enterprise Edition" (housekeeping, bukan business logic). | Rendah | — |
| `googleaeed8a7b9ec156e7.html` | — | Copy apa adanya (di luar scope perubahan — lihat `[BSL-018]`). | Rendah | `BSL-018` |
| `__init__.py` (root), `models/__init__.py`, `controllers/__init__.py` | — | Copy apa adanya — cuma `from . import ...`, tidak ada logic. | Rendah | — |
| `tests/__init__.py`, `tests/test_appointment_jitsi.py` | — | Copy apa adanya (13 test `TransactionCase` dari backfill), dijalankan ulang terhadap 18.0 di Step 9 sebagai regression check utama (lihat §Urutan Prioritas Testing poin 5). | Rendah | Semua `BSL-NNN` (test ini yang memverifikasi baseline) |
| `static/description/banner.png`, `icon.png`, `index.html`, `assets/appointment_jitsi.png`, `assets/doodex_odoo.png`, `LICENSE`, `LISEZMOI.md` | — | Copy apa adanya, tidak ada perubahan (asset statis, tidak ada logic Odoo). | Rendah | — |

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers
*(Mencegah instalasi atau operasi inti di 18.0)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version harus `18.0.x.x.x` | `__manifest__.py` | `knowledge/version-diffs/17-to-18.md` (housekeeping standar) |

**Priority:** HIGH secara prosedural (wajib dilakukan), tapi risiko teknis RENDAH — tidak ditemukan blocker install lain (lihat `02_DIFF_ANALYSIS.md` §4, DIFF-07/08/09/10 semua N/A untuk modul ini).

### OWL Widget yang Butuh Rewrite/Review

**N/A** — modul tidak punya komponen Owl/JS (dikonfirmasi `01a_MIGRATION_INTAKE.md` §2b, `02_DIFF_ANALYSIS.md` DIFF-10).

### Controller & Route

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `controllers/appointment.py` seluruhnya dead code (di-comment-out) — tetap dipertahankan apa adanya, BUKAN dihidupkan/dihapus | `controllers/appointment.py` | Rendah — tidak ada tindakan, murni port |

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Dependency `appointment` (Enterprise) tetap ada tidak berubah di 18.0 — tidak perlu penyesuaian `depends` | `__manifest__.py` | Rendah — dikonfirmasi DIFF-06 |
| 2 | Dev testing (Step 9) butuh mount `enterprise18` (bukan lagi `enterprise17`) sebagai extra addons path | `docker-env/docker-compose.yml` (kalau di-reuse dari backfill) | Sedang — infrastruktur, bukan kode modul |

### Kompatibilitas Data Model

**Tidak ada** — modul tidak menambah model baru, field baru yang ditambahkan (`jitsi_link`, `is_jitsi`, `company_param`) tidak berubah tipe/struktur di 18.0 (field-field ini murni milik modul ini sendiri, bukan field core yang bisa berubah oleh Odoo).

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Override 2 mail template BAWAAN tidak pernah aktif (by design, F-13) — pastikan Step 6 TIDAK "memperbaiki" ini secara tidak sengaja saat menyalin manifest | `__manifest__.py`, `data/mail_template_data.xml` | **Tinggi** (risiko proses, bukan risiko teknis) — lihat `FINDINGS.md` MF-01 |

### Urutan Prioritas Testing (Step 9, mengikuti `01b_BASELINE_SPEC.md`)

1. Install & startup — manifest ter-bump, modul ter-install bersih di atas Odoo 18 Enterprise + `enterprise18` mounted (setara F-12 lama)
2. `[BSL-002]` core flow — toggle setting global, buat event, cek `jitsi_link`/`videocall_location` terisi format yang benar
3. `[BSL-005]` create() single-dict — `access_token` di-set/di-reset sesuai `is_jitsi`
4. `[BSL-015]` — **verifikasi ulang F-13 tetap direproduksi** di 18.0 (email TETAP tidak menampilkan link Jitsi) — ini justru test POSITIF (mengonfirmasi bug-for-bug berhasil, bukan regresi baru)
5. Sisa `BSL-009`-`BSL-014`, `BSL-016`-`BSL-021` — quirk lain, re-run test yang sudah ada di `appointment_jitsi/tests/test_appointment_jitsi.py` (13 test dari backfill) terhadap kode 18.0 sebagai regression check utama

### View List (dulu Tree) Checklist

**N/A** — tidak ada `<tree>`/list view di modul ini (dikonfirmasi `02_DIFF_ANALYSIS.md` DIFF-07).

### Estimasi Effort

| Area | Effort | Catatan |
|---|---|---|
| Code migration (Step 6) | **Sangat kecil** (< 1 jam) | Copy folder + bump versi manifest + update README, tidak ada rewrite logic |
| Dev testing (Step 9) | **Sedang** | Bukan karena kode rumit, tapi karena environment (mount `enterprise18`, ulang 13 test existing) |
| Sisa step (2,4,5,8,10,11) | **Kecil-sedang** | Dokumentasi mengikuti pola yang sudah given `01b_BASELINE_SPEC.md` solid |

## 3. Data Migration

N/A — sifat migrasi "port kode saja" (dikonfirmasi `01a_MIGRATION_INTAKE.md` §3), tidak ada data produksi yang perlu ditransformasi. Step 7 di-skip.

## 4. Scope

### Termasuk
- Port seluruh file modul (`models/`, `views/`, `data/`, `controllers/`, `security/`, `static/`, root files) apa adanya ke struktur 18.0.
- Bump versi manifest `17.0.1.0.0` → `18.0.1.0.0`.
- Update baris "Compatibility" di `README.md` modul (17.0 → 18.0 Enterprise Edition) — housekeeping teks, bukan logic.
- Port 13 test `TransactionCase` yang sudah ada (`appointment_jitsi/tests/test_appointment_jitsi.py`) apa adanya, dijalankan ulang terhadap 18.0 sebagai regression check di Step 9.

### Di Luar Scope (sengaja, disetujui di intake)
- Memperbaiki F-13 (mendaftarkan `data/mail_template_data.xml` di manifest) — `01a_MIGRATION_INTAKE.md` §Ringkasan poin 3.
- Memperbaiki F-01..F-12 (12 bug/quirk lain) — `01a_MIGRATION_INTAKE.md` §Ringkasan poin 4.
- Mengubah `create()` ke `@api.model_create_multi` — walau best practice, bukan wajib teknis (DIFF-01) dan akan mengubah behavior F-03 yang harus dipertahankan.
- Menghapus `controllers/appointment.py` dead code atau file `googleaeed8a7b9ec156e7.html` yang nyasar — di luar scope, bukan bagian dari port fungsional.
