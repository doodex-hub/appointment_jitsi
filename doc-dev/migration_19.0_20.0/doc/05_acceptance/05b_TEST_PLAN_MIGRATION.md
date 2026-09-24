# Test Plan (Migrasi) — appointment_jitsi

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-09-24
**Status:** ✅ Selesai

---

## Step 9 — Dev Testing

> Eksekusi Mode C (AI): image dibangun dari `python:3.12-slim-bookworm` + `odoo20/requirements.txt` (belum ada image resmi `odoo:20.0`), `odoo20` di-mount `/opt/odoo:ro`, `enterprise20` di-mount `/mnt/enterprise:ro`, modul di `/mnt/extra-addons`. Wrapper `docker-env/run-test.sh` (dari `templates/run-test.sh.template`) — selalu `down -v` + `MSYS_NO_PATHCONV=1` + sanity check jumlah test "Starting". `--without-demo=all`. Tidak ada Owl/JS → Tour N/A.
>
> Audit kesiapan test: 13 test existing bukan stub (terverifikasi sejak backfill, PASS di 18.0 & 19.0). 2 test baru ditambahkan di Step 6.

| AC | Deskripsi | Integration (`TransactionCase`) | Tour |
|---|---|---|---|
| AC-01-01, AC-13-01 | Jitsi aktif → link Jitsi | `test_ac_01_01_jitsi_link_format_when_enabled` (assert) | N/A |
| AC-01-02 | Fallback Discuss | `test_ac_01_02_fallback_discuss_when_disabled` (assert) | N/A |
| AC-02-01/02 | create single-dict | `test_ac_02_01_…`, `test_ac_02_02_…` (assert) | N/A |
| AC-03-01 | Urutan akses (quirk) | `test_ac_03_01_…` (assert compute name + log) | N/A |
| AC-04-01 | `action_join_video_call` | **BARU** `test_mig20_ac_04_01_action_join_video_call` (assert) | N/A |
| AC-05-01 | generate/clear | `test_ac_08_01_…` (assert) | N/A |
| AC-06-01 | batch create | `test_ac_02_03_…` (log) | N/A |
| AC-07-01 | write toggle | `test_ac_04_01_write_toggle_no_recompute` (log) | N/A |
| AC-08-01 | company global | `test_ac_05_01_…` (assert) | N/A |
| AC-09-01 | nama mentah | `test_ac_06_01_…` (assert) | N/A |
| AC-10-01 | uncheck → Discuss | **BARU** `test_mig20_ac_10_01_uncheck_setting_falls_back_to_discuss` (assert) + `test_ac_01_03_…` (log) | N/A |
| AC-10-02 | deviasi BSL-023 | tidak langsung (helper `_disable_jitsi`) | N/A |
| AC-11-01 🔴 | email tanpa Jitsi | `test_qa_s01_…` (assert, retarget MF-02) | N/A |
| AC-12-01 | controller mati | `test_ac_07_01_…` (assert) | N/A |
| AC-14-01 | install 20.0+EE | log G1 (0 ERROR, cek WARNING) | N/A |
| AC-15-01 | settings view | log G1 (view valid) — visual di Step 10 | N/A |

Target: **15/15 test PASS**, 0 ERROR di log install, sanity count "Starting" = 15.

## Step 10 — QA Testing (menunggu slot dari dev — STOP wajib)

> Mode: AI-interaktif (Playwright MCP, default CLI) terhadap instance QA 20.0 (`--http-interface=0.0.0.0`, port 8097), atau Manual kalau dev memilih.

| AC | Skenario | Manual | AI-interaktif |
|---|---|---|---|
| AC-15-01, AC-01-01 | Smoke: Settings → Calendar → centang Jitsi + pilih Company → Save; buat event → tombol Join/URL Jitsi | opsional | ✅ |
| AC-10-01 | Uncheck setting → event baru pakai Discuss | opsional | ✅ |
| AC-11-01 🔴 | Booking appointment / preview email → tidak ada link Jitsi | opsional | ✅ |
| AC-14-01 | Install via Apps di DB bersih | opsional | ✅ |
| MF-03 | Event Jitsi: cek apakah channel Discuss ikut dibuat (native 20.0) — observasi | — | ✅ |

## Step 11 — UAT

| Kelompok | AC | UAT |
|---|---|---|
| Aktivasi & pemakaian Jitsi | AC-01, 04, 10, 13, 15 | Owner konfirmasi toggle + link identik 19.0; review deviasi AC-10-02 (MF-01) |
| Quirk dipertahankan | AC-02, 03, 06, 07, 08, 09, 11 | Owner sign-off quirk sengaja dipertahankan |
| Instalasi | AC-12, 14 | Install bersih 20.0 Enterprise |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer (AI Mode C) | Integration | Otomatis, 15 test | 16 |
| 10 | QA | AI-interaktif/Manual | Menunggu slot | 5 skenario |
| 11 | Owner (Kuncoro) | UAT | Manual | 3 kelompok |
