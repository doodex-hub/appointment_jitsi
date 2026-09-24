# Dev Testing — appointment_jitsi

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-09-24
**Status:** ✔️ Lulus gate
**Revisi yang dites:** `migration/20.0` @ `f9d74b8` (kode = `3c2bd89`)

---

> Eksekusi Mode C lewat wrapper resmi dari `docker-env/`:
> ```bash
> ./run-test.sh odoo appointment_jitsi_test_20 appointment_jitsi
> ```
> Environment: image `appointment_jitsi_migration_20-odoo` (source `odoo20` branch `20.0` + `enterprise20` branch `20.0`, read-only mount), `postgres:16`, fresh DB tiap run (`down -v`), `--without-demo=all`, `MSYS_NO_PATHCONV=1`. Fase E (Owl/JS) N/A → tidak ada tour test (bukan celah: modul tanpa JS).

## 9a. Audit Kesiapan Test

1. **Registrasi:** `tests/__init__.py` meng-import satu-satunya file `test_appointment_jitsi.py` ✅.
2. **Isi method** (parse `ast` di dalam container — host tidak punya Python): 15 method, **0 stub**. 12 method punya `assert*` (1–5 assert), 3 method observasional tanpa assert **by design sejak backfill** (`test_ac_01_03`, `test_ac_02_03`, `test_ac_04_01_write_toggle…`) — verdict-nya dari nilai log dibandingkan baseline 19.0.

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01 🔶, AC-13-01 | Jitsi aktif → link Jitsi | `test_ac_01_01` | ✅ Lengkap (3 assert) | memverifikasi DIFF-01 + MF-03 |
| AC-01-02 | fallback Discuss | `test_ac_01_02` | ✅ Lengkap | |
| AC-02-01/02 | create single | `test_ac_02_01`, `test_ac_02_02` | ✅ Lengkap | |
| AC-03-01 🔶 | urutan akses | `test_ac_03_01` | ✅ Lengkap (assert compute) + log | |
| AC-04-01 | join action | `test_mig20_ac_04_01` | ✅ Lengkap (baru) | |
| AC-05-01 | generate/clear | `test_ac_08_01` | ✅ Lengkap | |
| AC-06-01 | batch create | `test_ac_02_03` | ✅ Observasional (log) | |
| AC-07-01 | write toggle | `test_ac_04_01_write_toggle…` | ✅ Observasional (log) | |
| AC-08-01 | company global | `test_ac_05_01` | ✅ Lengkap | |
| AC-09-01 | nama mentah | `test_ac_06_01` | ✅ Lengkap | |
| AC-10-01 🔶 | uncheck → Discuss | `test_mig20_ac_10_01` (+ `test_ac_01_03` log) | ✅ Lengkap (baru, 5 assert) | |
| AC-10-02 ⚠️ | deviasi BSL-023 | tidak langsung (helper `_disable_jitsi`) | ✅ Terdokumentasi | MF-01 |
| AC-11-01 🔴 | email tanpa Jitsi | `test_qa_s01` | ✅ Lengkap | retarget MF-02 |
| AC-12-01 | controller mati | `test_ac_07_01` | ✅ Lengkap | |
| AC-14-01 | install 20.0+EE | log install | ✅ | |
| AC-15-01 | settings view | observasi `odoo shell` (di bawah) | ✅ | visual → Step 10 |

**Verdict audit:** [x] semua AC prioritas (🔶/🔴) Lengkap — lanjut eksekusi.

## Baseline

- Test asli source (`migration/19.0`): 13 test yang sama (sebelum adaptasi) — **13/13 PASS terhadap 19.0** di Step 9 migrasi 18→19 (`doc-dev/migration_18.0_19.0/doc/09_devtest/09_DEV_TESTING.md`). Tidak ada test di lokasi lain (`01a` §4: test lahir dari backfill 17.0, sudah di repo ini).
- Kode 19.0 as-is di 20.0 (G1 #1, hanya bump manifest): install PASS, **10/13 ERROR** `AttributeError` `get_param`/`set_param` — bukti DIFF-01.
- Applicability Check Fase E: Tidak (N/A).

## Hasil Unit, Integration & Tour Test (target-codebase)

**Run resmi:** `docker-env/logs/run-test-20260924-141941.log` (lokal, gitignored) — `0 failed, 0 error(s) of 17 tests` (15 test modul + `WebSuite.test_unit_desktop` & `MobileWebSuite.test_unit_mobile` bawaan `web` yang ikut ter-collect oleh tag `post_install`), 19 baris "Starting" (15 modul + 2 web + 2 baris "Starting post tests"/container), **0 baris ERROR/CRITICAL**. Diulang identik dari G1 #2 (`run-test-20260924-140505.log`) → hasil stabil.

| AC | Integration | Pass/Fail | Nilai teramati 20.0 | Baseline 19.0 | Catatan |
|---|---|---|---|---|---|
| AC-01-01 | `test_ac_01_01` | ✅ Pass | `jitsi_link = videocall_location = https://meet.jit.si/My Company/My Company-<uuid36>` | sama | DIFF-01 fix bekerja; MF-03 tidak menggeser hasil |
| AC-01-02 | `test_ac_01_02` | ✅ Pass | `get_str=None`, `videocall_location=False` | `get_param=False`, bukan Jitsi | |
| AC-02-01 | `test_ac_02_01` | ✅ Pass | token terisi | sama | |
| AC-02-02 | `test_ac_02_02` | ✅ Pass | `access_token == 'should-be-overwritten'` | sama | tidak kena `unique` (DIFF-02) |
| AC-03-01 | `test_ac_03_01` | ✅ Pass | A: Jitsi penuh; B: `videocall_location=False`; `bug_confirmed=True` | identik | `BSL-010` terjaga |
| AC-04-01 | `test_mig20_ac_04_01` | ✅ Pass | URL sesuai `is_jitsi`, `target=new` | (belum pernah dites) | |
| AC-05-01 | `test_ac_08_01` | ✅ Pass | clear → False, generate → terisi | sama | |
| AC-06-01 | `test_ac_02_03` | ✅ Pass | token batch terisi, `bug_confirmed=False` | identik | `BSL-009` |
| AC-07-01 | `test_ac_04_01_write_toggle…` | ✅ Pass | `before=False after=False`, `bug_confirmed=True` | identik | `BSL-011` |
| AC-08-01 | `test_ac_05_01` | ✅ Pass | kedua event pakai "My Company" | sama | `BSL-012` |
| AC-09-01 | `test_ac_06_01` | ✅ Pass | `…/PT Doodex Indonesia/PT Doodex Indonesia-…` | sama | `BSL-013` |
| AC-10-01 | `test_mig20_ac_10_01` + `test_ac_01_03` | ✅ Pass | uncheck → row `'False'` → `get_bool` False → event baru tanpa Jitsi; `bug_confirmed=False` | 19.0: row dihapus → sama secara observable | mekanisme native berubah, outcome sama |
| AC-11-01 🔴 | `test_qa_s01` | ✅ Pass | `muncul_di_body=False`, body memuat `/calendar/meeting/join?token=` | sama | `BSL-015` terjaga |
| AC-12-01 | `test_ac_07_01` | ✅ Pass | 0 baris aktif | sama | |
| AC-14-01 | install log | ✅ Pass | 0 ERROR; WARNING modul hanya label "Company" duplikat | sama (`BSL-019`) | WARNING `markdown2` = native, bukan modul |

**Observasi tambahan (`odoo shell`, DB `obs20` sekali pakai, di-rollback, event tanggal 2030 supaya lolos filter "belum lewat" native):**

| Observasi | Hasil | Relevansi |
|---|---|---|
| Event baru, Jitsi aktif | `videocall_source='custom'`, `videocall_channel_id=[]` | **MF-03 tuntas:** fitur native baru `_ensure_videocall_channels` TIDAK membuat channel Discuss untuk event Jitsi |
| Event baru, Jitsi nonaktif | link Discuss, `videocall_source='discuss'`, channel dibuat (`[3]`) | Fitur native 20.0 (tidak ada di 19.0) — bukan behavior modul, dicatat untuk UAT |
| Arch form `res.config.settings` | blok `sync_jitsi_meet_setting` ada, posisinya setelah `sync_google_calendar_setting`, field `company_param` ada, `invisible="not is_jitsi"` ada | AC-15-01 (struktur); visual → Step 10 |

## Kontribusi ke Knowledge Base

- [x] Ada — `migration-records/appointment_jitsi_19.0_20.0/SUMMARY.md`: CAND-01 dikonfirmasi empiris (G1 #1: 10 `AttributeError`), CAND-03 diupdate (flush baru di `create()` tidak menggeser hasil untuk pola "tulis `videocall_location` dari compute lain"; channel Discuss hanya untuk `videocall_source='discuss'`).

## Verdict

- [x] ✅ Semua AC prioritas Unit/Integration pass — **siap Step 10** (menunggu slot dari dev, STOP wajib sesuai instruksi sesi)
- [ ] ❌ Ada yang gagal
