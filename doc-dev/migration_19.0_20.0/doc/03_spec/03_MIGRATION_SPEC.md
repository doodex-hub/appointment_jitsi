# Migration Spec (Teknis) — appointment_jitsi

**Step:** 3 — Migration Spec
**Versi:** 19.0 → 20.0
**Ref:** `02_diff/02_DIFF_ANALYSIS.md`, `FINDINGS.md`
**Tanggal:** 2026-09-24
**Status:** ✅ Selesai

> Memandu IMPLEMENTASI (Step 6). Dasar acceptance/testing tetap `01b_BASELINE_SPEC.md`.

---

## 1. Ringkasan Strategi

Port langsung hampir seluruh modul. **Satu perubahan kode produksi wajib** (DIFF-01: `get_param` → `get_bool`/`get_int` di `_compute_jitsi_link`) + bump versi manifest. Test suite: port helper config param ke API bertipe (DIFF-01), retarget satu `env.ref` (DIFF-08), dan tambah test assertion untuk dua perilaku yang di 19.0 hanya diamati lewat log/tanpa test (AC-04, AC-10) supaya perubahan DIFF-01 terverifikasi nilai akhirnya. Tidak ada JS/Owl/controller/data yang berubah. `create()`, `action_join_video_call()`, `data/mail_template_data.xml`, `controllers/`, `security/`, file Google verification — **tidak disentuh** (bug-for-bug).

## 2. Strategi per File/Simbol

| File/simbol | Ref DIFF | Strategi | Risiko | Ref BSL |
|---|---|---|---|---|
| `__manifest__.py` `version` | DIFF-12 | `19.0.1.0.0` → `20.0.1.0.0`. Key lain TIDAK diubah (termasuk `images: static/description/banner.png`, `data` tetap satu file). | Rendah | BSL-015 |
| `models/calendar_event.py` `_compute_jitsi_link` | DIFF-01 | Ganti `get_param = ICP.get_param` jadi `ICP = self.env['ir.config_parameter'].sudo()`; `is_jitsi_enabled = ICP.get_bool('is_jitsi_param')`; `company_param_id = ICP.get_int('company_param')`. Sisa body (search company, `'Record not found'`, cabang token `uuid4().hex`, format URL, fallback `_set_discuss_videocall_location()`) **identik**. | Sedang (MF-01 — deviasi `BSL-023` untuk nilai manual non-boolean) | BSL-002, 006, 012, 013, 014, 023 |
| `models/calendar_event.py` `create()` | DIFF-03 | Tidak diubah. | Rendah | BSL-005, 009 |
| `models/calendar_event.py` `action_join_video_call`, `generate_jitsi_link`, `clear_jitsi_link`, field defs | DIFF-05 | Tidak diubah. | Rendah | BSL-007, 008 |
| `models/calendar_event.py` `ResConfigSettings` | DIFF-11 | Tidak diubah (deklarasi `config_parameter=` tetap valid). | Rendah | BSL-001, 014 |
| `views/calendar_views.xml` | DIFF-07, DIFF-09 | Tidak diubah. | Rendah | BSL-001, 022 |
| `data/mail_template_data.xml` | DIFF-08 | Tidak diubah, tetap TIDAK di manifest. | Rendah | BSL-015 |
| `security/ir.model.access.csv` | DIFF-10 | Tidak diubah (tidak di-load). | Rendah | — |
| `controllers/*` | — | Tidak diubah. | Rendah | BSL-016 |
| `tests/test_appointment_jitsi.py` helper `_enable_jitsi`/`_disable_jitsi` + log `get_param` | DIFF-01 | `set_param('is_jitsi_param','True')` → `set_bool(..., True)`; `set_param('company_param', str(id))` → `set_int(..., id)`; `_disable_jitsi` → `set_bool(..., False)`; log `get_param(...)` → `get_str(...)` (nilai mentah untuk observasi). | Rendah | — |
| `tests/…` `test_qa_s01` | DIFF-08 | `env.ref('appointment.appointment_booked_mail_template')` → `appointment.appointment_booking_mail_template`; assertion & docstring disesuaikan (intent sama). | Rendah | BSL-015 |
| `tests/…` test BARU | DIFF-01, DIFF-05 | `test_ac_04_01_action_join_video_call` (assert URL per `is_jitsi`, `target=new`); `test_ac_10_01_uncheck_setting_falls_back_to_discuss` (centang → uncheck via `res.config.settings.execute()` → event baru BUKAN Jitsi — mengunci `BSL-014` di atas API baru). | Rendah | BSL-007, 014 |

## 2b. Risk Analysis

### Critical Migration Blockers

| # | Isu | Lokasi | Rujukan |
|---|---|---|---|
| 1 | Manifest version 20.0.x | `__manifest__.py` | konvensi |
| 2 | `get_param` tidak ada → `AttributeError` di compute saat create event | `models/calendar_event.py:42-44` | DIFF-01 (kandidat CAND-01 migration-records) |

### OWL Widget / Controller / Assets
N/A — tidak ada.

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref |
|---|---|---|---|---|
| 1 | `access_token` unique + default di core | `calendar.event` | Rendah — tanpa perubahan kode | DIFF-02 |
| 2 | Penyimpanan boolean setting `"False"` (bukan hapus row) | `ir.config_parameter` | Ditangani `get_bool` | DIFF-01, BSL-014 |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | `_ensure_videocall_channels()` + flush `videocall_location` di akhir `create()` → urutan compute/efek channel Discuss untuk event Jitsi | `calendar.event.create()` native | Sedang — verifikasi nilai di G1 (MF-03) |

### Urutan Prioritas Testing

1. Install bersih 20.0 (+ `enterprise20`) — G1.
2. Create event dengan Jitsi aktif → `jitsi_link`/`videocall_location` Jitsi (`test_ac_01_01`) — memverifikasi DIFF-01 + MF-03.
3. Fallback Discuss & uncheck setting (`test_ac_01_02`, `test_ac_10_01` baru).
4. Quirk yang dipertahankan (`test_ac_02_*`, `03_01`, `04_01`, `05_01`, `06_01`, `07_01`, `08_01`).
5. Template email tidak memuat Jitsi (`test_qa_s01`).

### View List Checklist
N/A — tidak ada list/tree view.

## 3. Data Migration

N/A — port kode saja. (Catatan kalau suatu hari upgrade instance: row `is_jitsi_param` lama bernilai `"True"` tetap terbaca `True` oleh `get_bool`; row non-boolean manual akan terbaca invalid → False.)

## 4. Scope

### Termasuk
- Perubahan kode wajib DIFF-01 + DIFF-12; adaptasi test DIFF-01/DIFF-08; 2 test assertion tambahan.

### Di Luar Scope (disetujui intake)
- Aset App Store branch rilis 19.0.
- Perbaikan bug/quirk apapun (F-01..F-13, BSL-009/010/011/012/013/015/020).
- Memperbarui rujukan XML-ID basi di `data/mail_template_data.xml` (file tidak di-load).
