# Code Review — appointment_jitsi

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/06c_IMPLEMENTATION_LOG.md`, `01_intake/01b_BASELINE_SPEC.md`, `FINDINGS.md`
**Odoo Version:** 20.0
**Revisi di-review:** `migration/20.0` @ `3c2bd89` vs base `migration/19.0` @ `7bfabb3` (`git diff migration/19.0 3c2bd89 -- appointment_jitsi`)
**Files reviewed:** `__manifest__.py`, `models/calendar_event.py`, `tests/test_appointment_jitsi.py`, `README.md`, `LISEZMOI.md` (+ file tak berubah dibaca untuk konteks: `views/calendar_views.xml`, `data/mail_template_data.xml`, `controllers/appointment.py`)
**Tanggal:** 2026-09-24
**Status:** ✔️ Lulus gate

---

## A. Issues

**Status skill `odoo-review`:**
- [x] Terinstall (`.claude/skills/odoo-review` + `odoo-guidelines` + `odoo-security` + `odoo-web-guidelines` di `target-codebase`, untracked) & dijalankan — proses: scope (diff pinned di atas) → map → read → rules pass → merits pass. Catatan: instruksi dev menyebut skill di `migration-tool\.claude\skills`; folder itu tidak ada — yang dipakai salinan di `target-codebase/.claude/skills/`.
- [ ] BELUM terinstall

**Map file → section:** `__manifest__.py` → Manifest; `models/calendar_event.py` → Imports, Naming and model layout, Computes/onchange/constraints, Fields, odoo-security "Don't over-sudo"; `tests/…` → Tests, Imports, Naming; `README`/`LISEZMOI` → (dokumentasi, tidak ada section). Target branch = versi rilis (20.0) → Changes in a stable version dipakai sebagai lensa "minimal diff".

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| R-01 | 🔵 Info | Konvensi (pre-existing) | `models/calendar_event.py` | 71-78 | `create` pakai `@api.model` + `values` dianggap dict (guideline: wajib `@api.model_create_multi`). | **Tidak diubah** — quirk dipertahankan (`BSL-005`/`BSL-009`, MF-01 18→19 disetujui dev). |
| R-02 | 🔵 Info | Konvensi (pre-existing) | `models/calendar_event.py` | 37-59 | Stored compute `_compute_jitsi_link` punya side effect (menulis `access_token` & `videocall_location`) dan `@api.depends` tidak lengkap (membaca `ir.config_parameter`). | **Tidak diubah** — quirk `BSL-010`/`BSL-011`. |
| R-03 | 🔵 Info | Security (dinilai, OK) | `models/calendar_event.py` | 42 | `self.env['ir.config_parameter'].sudo()` — dicek sesuai "Don't over-sudo": dibutuhkan karena `get_bool/get_int` 20.0 melakukan `check_access('read')` dan user Calendar biasa tidak punya akses baca `ir.config_parameter`; hanya membaca dua key tetap milik modul, tidak menerima input user, tidak mengembalikan data sensitif. Identik 19.0. | Tidak perlu tindakan. |
| R-04 | 🔵 Info | Manifest (pre-existing) | `__manifest__.py` | 23 | `base` terdaftar di `depends` (guideline: jangan). | Tidak diubah (minimal diff; tanpa efek fungsional). |
| R-05 | 🔵 Info | Imports (pre-existing) | `models/calendar_event.py` | 3 | `_` di-import tapi tidak dipakai. | Tidak diubah (minimal diff). |
| R-06 | 🔵 Info | Business logic (merits) | `models/calendar_event.py` | 43 | `get_bool` untuk nilai non-boolean manual → `False` + WARNING log sekali per cache (`ir_config_parameter._get`), sementara 19.0 menganggap aktif. | Sudah terdokumentasi sebagai deviasi disengaja AC-10-02 / MF-01 (menunggu review dev). |

**Merits pass (hunk yang berubah):**
- `get_int('company_param')`: row hilang / `None` → `0` → `search([('id','=',0)])` kosong → `'Record not found'` — sama dengan 19.0 (`get_param` False → search kosong). Nilai lama dari DB 19.0 (`"5"`) terbaca `5`. ✅
- `get_bool('is_jitsi_param')`: `"True"` (disimpan 19.0 saat dicentang) → True; `"False"` (disimpan 20.0 saat uncheck) → False. ✅ jalur UI identik.
- Multi-record compute: getter dipanggil sekali di luar loop, seperti sebelumnya (ormcache per key/tipe). Tidak ada regresi performa. ✅
- Test baru gagal tanpa perubahan? `test_mig20_ac_10_01` gagal di kode 19.0-as-is (AttributeError) dan akan gagal juga kalau dipakai `get_str` truthy (opsi 2 MF-01): `event_off.jitsi_link` akan terisi. ✅ benar-benar menguji keputusan MF-01.
- `test_mig20_ac_04_01`: `write({'videocall_location': ...})` ke URL https → `videocall_source='custom'`, tidak memicu recompute `jitsi_link` (depends hanya `access_token`) → cabang `is_jitsi` benar-benar dibedakan. ✅

**Guidelines read:** Manifest; Imports; Naming and model layout; Translate only static literals; Computes, onchange and constraints; Tests; Changes in a stable version; odoo-security "Don't over-sudo" (SKILL.md).

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item | Implementasi | Status | Catatan |
|---|---|---|---|
| DIFF-12 manifest | `20.0.1.0.0`, key lain utuh | ✅ Match | |
| DIFF-01 compute | `get_bool`/`get_int`, sisa body identik | ✅ Match | diff produksi = 3 baris |
| DIFF-01 test helper | `set_bool`/`set_int`, log `get_str` | ✅ Match | |
| DIFF-08 test retarget | `appointment.appointment_booking_mail_template` | ✅ Match | data file tak disentuh |
| 2 test baru | `test_mig20_ac_04_01`, `test_mig20_ac_10_01` | ✅ Match | |
| DIFF-02/03/05/06/07/09/10/11 "tidak diubah" | tidak diubah (`git diff` hanya 5 file di atas) | ✅ Match | |
| A6 README/LISEZMOI | versi → 20.0 | ✅ Match | housekeeping |

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC | Behavior | Status | Jejak Nalar (Desk Review) | Catatan |
|---|---|---|---|---|
| AC-01-01 | Jitsi aktif → link Jitsi | ✅ | Admin centang → `set_values` → `set_bool('is_jitsi_param', True)` → user buat event → `create()` super → default `access_token` → stored compute `_compute_jitsi_link` → `get_bool` True → URL `meet.jit.si/{company}/{company}-{token}` ditulis ke `jitsi_link` & `videocall_location` → user lihat link Jitsi. | G1 #2 PASS |
| AC-01-02 | Fallback Discuss | ✅ | Row tidak ada → `get_bool` default False → `_set_discuss_videocall_location()` saat `jitsi_link` dihitung. | |
| AC-02-01/02 | create single | ✅ | `create` tidak diubah; routing identik 19↔20 (DIFF-03). | |
| AC-03-01 | urutan akses | ✅ | Tidak ada perubahan kode; log G1 identik 19.0 (MF-03). | |
| AC-04-01 | join action | ✅ | Klik Join → `action_join_video_call` modul (MRO menimpa core, sama 19.0) → `jitsi_link` kalau `is_jitsi`, else `videocall_location`. | test baru |
| AC-05..09, 11..13 | quirk dipertahankan | ✅ | Kode terkait tidak berubah; hanya sumber flag global yang diganti API. | |
| AC-10-01 | uncheck → Discuss | ✅ | Uncheck → `set_bool(False)` → row `"False"` → `get_bool` False → Discuss. | test baru |
| AC-10-02 | deviasi `BSL-023` | ⚠️ Deviasi disengaja | Nilai manual `"False"` → `get_bool` False (19.0: truthy). | MF-01, menunggu review dev |
| AC-14/15 | install + settings view | ✅ | G1 #2 install tanpa ERROR; xpath valid. Visual → Step 10. | |

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — satu-satunya deviasi (`BSL-023`/AC-10-02) tercatat di `03_MIGRATION_SPEC.md` §2 + `FINDINGS.md` MF-01.

**Empat arah tabrakan:**
1. Arah 1 — method modul dengan nama sama core: hanya `action_join_video_call` (menimpa core tanpa `super()`, pre-existing sejak 17.0, `BSL-007`) dan `create` (memanggil `super()`). Tidak ada yang baru.
2. Arah 2 — definisi BARU di native TARGET dengan nama sama: ripgrep `jitsi_link|is_jitsi|company_param|generate_jitsi_link|clear_jitsi_link` di `odoo20` & `enterprise20` (`*.py`, `*.xml`) = 0 file. `def action_join_video_call` hanya di `odoo20/addons/calendar/models/calendar_event.py:1532` (sama 19.0).
3. Arah 3 — registry UI replace-total: N/A (tanpa JS).
4. Arah 4 — kapabilitas baru native yang tumpang-tindih: **ada satu yang diamati, bukan bug** — native 20.0 membuat `discuss.channel` otomatis untuk event video-call Discuss (`_ensure_videocall_channels`, DIFF-04). Modul tidak menambah action/registry; untuk event Jitsi `videocall_source` = `custom` sehingga channel seharusnya tidak dibuat — dikonfirmasi visual di Step 10 (MF-03 sisa observasi).

- [x] Sudah dicek (keempat arah) — tidak ada tabrakan/penyimpangan; satu observasi native (Arah 4) dijadwalkan Step 10.

## E. Perubahan Tak Tertelusuri

- [x] Tidak ada — `git diff migration/19.0 3c2bd89 -- appointment_jitsi` = 5 file, semuanya tertelusuri ke §B.

## F. Kontribusi ke Knowledge Base

- [x] Tidak ada temuan baru di step ini selain CAND-01..04 yang sudah dicatat di Step 2 (`migration-records/appointment_jitsi_19.0_20.0/SUMMARY.md`); CAND-03 diupdate dengan hasil G1 (lihat Step 9).

## G. Verdict

- Ringkasan: 0 🔴 · 0 🟡 · 6 🔵 (semua pre-existing/terdokumentasi)
- [x] ✅ Lulus — tidak ada 🔴, lanjut ke step 9
- [ ] ❌ Ditolak
