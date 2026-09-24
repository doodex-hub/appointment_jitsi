# Business Flow — Migrasi appointment_jitsi

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `09_devtest/09_DEV_TESTING.md`, `../CROSS_VERSION_COMPARE.md`
**Tanggal:** 2026-09-24
**Status:** ✔️ Lulus gate
**Slot:** dimulai atas izin eksplisit dev ("Lanjut step 10", chat 2026-09-24); instance QA dimatikan (`down -v`) segera setelah skenario live selesai.

> Install bersih (port kode saja, Step 7 N/A). Fase E (Owl/JS) N/A — tidak ada tour Step 9 yang bisa dirujuk; seluruh verifikasi UI dilakukan di sini.
>
> **Environment:** `docker-env/docker-compose.cvc.yml` — dua instance hidup berdampingan, DB kosong `--without-demo=all`, `--http-interface=0.0.0.0`:
> - **Target 20.0** `http://localhost:8097` (DB `qa20`, kode `migration/20.0` @ `75f98f0`, `odoo20` + `enterprise20`)
> - **Source 19.0** `http://127.0.0.1:8098` (DB `qa19`, snapshot `git archive migration/19.0`, `odoo19` + `enterprise19`) — untuk Cross-Version Compare
>
> **Mode:** AI-interaktif, **Playwright MCP** (default CLI). Login admin TANPA mengetik password: session dibuat di sisi server lewat `odoo shell` di container QA (`finalize()` session store native), cookie `session_id` dipasang ke konteks Playwright. Host berbeda (`localhost` vs `127.0.0.1`) supaya cookie kedua instance tidak saling timpa (cookie tidak membedakan port).
>
> **Retry yang terjadi (STOP-rule, semua ≤1 retry dengan pendekatan berbeda):** (1) navigasi pertama timeout 60 dtk — diverifikasi dari luar tool (`curl` 200 dalam 0,04 dtk; log server "Generating a new asset bundle") = generate bundle aset pertama kali, retry setelah selesai → OK; (2) `waitForLoadState('networkidle')` tidak pernah tercapai (long-polling bus Odoo) → ganti menunggu selector → OK; (3) klik ikon pertama di field Video Link ternyata tombol clipboard → ganti ke `button[name=action_join_video_call]` → OK; (4) URL popup Join tidak terbaca karena request eksternal di-abort → catat event `request` → OK. Request ke `meet.jit.si` sengaja diblok (tidak membuka situs eksternal).

---

## Skenario

- [x] Skenario dari AC risiko tinggi — S-01..S-05.
- [x] **Cross-Version Compare** — WAJIB (dependency Enterprise `appointment`). Dijalankan penuh, prosedur & hasil: `../CROSS_VERSION_COMPARE.md`. 3 temuan, semua `NATIVE-DIFF`, 0 `REGRESI` (RMV-01..03 di `FINDINGS.md`).
- [x] Spot-check integritas data — N/A (Step 7 N/A, port kode saja).
- [x] Multi-dialog/wizard dari satu aksi — **N/A, dikonfirmasi tidak ada kasus multi-dialog** (modul tidak punya wizard/dialog; satu-satunya popup adalah tab baru Join).

### S-01: Install + aktifkan Jitsi di Settings
**Level:** Smoke
**Precondition:** DB baru tanpa demo, modul ter-install (`-i appointment_jitsi` saat start container), login admin.
**Mode eksekusi:** AI-interaktif (Playwright MCP), di 20.0 dan 19.0
**Steps:** 1) Settings → Calendar. 2) Cek blok "Jitsi Configuration" berada setelah Google Calendar, field Company tersembunyi. 3) Centang "Jitsi Configuration". 4) Save.
**Expected:** (AC-14-01, AC-15-01, AC-01) install tanpa error; blok ada setelah Google Calendar; Company muncul saat dicentang, default company aktif; setelah Save tetap tercentang, parameter tersimpan.
**Actual:** 20.0: install tanpa ERROR (log `Modules loaded`); urutan `outlook → google → jitsi`; Company tersembunyi → muncul "My Company"; setelah Save tercentang, `is_jitsi_param="True"`, `company_param="1"`. **19.0 identik** (nilai sama persis). Toggle Company tersembunyi/muncul/tersembunyi lagi terverifikasi di kedua versi. Screenshot: `screenshots/{target-20.0,source-19.0}/s01_*`, `visual_settings_*`.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

### S-02: Buat event → Video Link Jitsi & tombol Join
**Level:** Main Flow
**Precondition:** S-01 (Jitsi aktif).
**Mode eksekusi:** AI-interaktif
**Steps:** 1) Calendar → Meetings (list) → New. 2) Isi Meeting Subject, Save. 3) Baca field Video Link. 4) Klik ikon Join (`action_join_video_call`).
**Expected:** (AC-01-01, AC-04-01, AC-13-01) Video Link = `https://meet.jit.si/{company}/{company}-{token}` walau `is_jitsi` event = False; Join membuka tab baru ke URL itu.
**Actual:** 20.0: langsung setelah Save Video Link = `https://meet.jit.si/My Company/My Company-7d264e93-…`; Join membuka tab baru ke URL yang sama (`match=true`); DB `jitsi_link == videocall_location`, `source=custom`, tanpa channel. 19.0: **tepat setelah Save Video Link kosong & tombol Join belum tampil**; setelah reload form tampil URL Jitsi + Join membuka URL yang sama; nilai DB identik 20.0. Selisih hanya pada tampilan tepat-setelah-save (19.0 menampilkan nilai sebelum compute Jitsi di-flush; 20.0 flush di `create()` native, DIFF-04) → **RMV-01 `NATIVE-DIFF`**, bukan regresi.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

### S-03: Uncheck setting → event baru kembali ke Discuss
**Level:** Main Flow
**Precondition:** S-02.
**Mode eksekusi:** AI-interaktif
**Steps:** 1) Settings → uncheck "Jitsi Configuration" → Save. 2) Buat event baru, Save, reload. 3) Baca Video Link.
**Expected:** (AC-10-01, AC-01-02) event baru memakai link Discuss, `jitsi_link` kosong.
**Actual:** 20.0: `is_jitsi_param="False"` (row tetap ada); Video Link `http://localhost:8069/calendar/join_videocall/<token>`, `jitsi_link=False`, `source=discuss`, **channel Discuss dibuat otomatis**. 19.0: row `is_jitsi_param` DIHAPUS; link Discuss sama, `jitsi_link=False`, **tanpa channel**. Outcome modul identik; mekanisme penyimpanan berbeda sesuai MF-01 (disetujui dev); pembuatan channel = fitur native baru → **RMV-02 `NATIVE-DIFF`**.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

### S-04: Email "booked" appointment TIDAK memuat link Jitsi 🔴
**Level:** Negative
**Precondition:** Jitsi aktif lagi (Settings), event baru dengan attendee Administrator (Jitsi link terisi di DB).
**Mode eksekusi:** AI-interaktif (Technical → template → Preview)
**Steps:** 1) Buka template 20.0 "Appointment: Appointment Booking" / 19.0 "Appointment: Appointment Booked". 2) Klik Preview, record = event QA S-04. 3) Periksa semua link di body.
**Expected:** (AC-11-01, `BSL-015`) body tidak memuat `jitsi_link`/`meet.jit.si`; hanya link core (`/calendar/meeting/join?token=`…).
**Actual:** 20.0 (body di iframe): `…/calendar/meeting/join?token=7ebf39d4…`, `…/odoo/calendar.event/3`, `…/calendar/videocall/7ebf39d4…`, + wrapper `redirect-url.email` & footer Odoo (layout native 20.0). 19.0: tiga link core yang sama (token berbeda). **Tidak ada `meet.jit.si` di kedua versi** walau `jitsi_link` event terisi. Bug-for-bug F-13 terjaga. Perbedaan layout email = `NATIVE-DIFF` (RMV-03).
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

### S-05: Route controller custom tidak aktif
**Level:** Negative
**Precondition:** instance hidup.
**Mode eksekusi:** AI-interaktif (HTTP request langsung, `curl`)
**Steps:** GET `/calendar/join_jitsi/abc`.
**Expected:** (AC-12-01, `BSL-016`) 404 di kedua versi.
**Actual:** 20.0 → 404, 19.0 → 404.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [DIKONFIRMASI]

### S-06: Quirk yang dipertahankan (urutan akses, toggle write, company global, nama berspasi, batch create)
**Level:** Detail
**Precondition:** —
**Mode eksekusi:** — (dicover automated test Step 9)
**Steps/Expected:** AC-03-01, AC-06-01, AC-07-01, AC-08-01, AC-09-01.
**Actual:** Step 9 `run-test-20260924-141941.log`: seluruh nilai observasional identik log 19.0 (`bug_confirmed` Skenario B `True`, toggle `before=False after=False`, batch `False`, company global, nama berspasi 2×). Tidak punya dampak UI tambahan di luar S-02.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [HASIL-BACA — ref: Step 9, AC-03/06/07/08/09]

### S-07: Deviasi disengaja — nilai manual non-boolean `is_jitsi_param`
**Level:** Detail
**Precondition:** —
**Mode eksekusi:** — (dicover Step 9 + keputusan dev)
**Expected/Actual:** AC-10-02: `"False"` manual → nonaktif di 20.0 (19.0: aktif). Terverifikasi tidak langsung di Step 9 (helper `_disable_jitsi` + `test_mig20_ac_10_01`); **disetujui dev 2026-09-24 (MF-01)**.
**Status:** [x] Pass / [ ] Fail
**Provenance:** [HASIL-BACA — ref: Step 9, AC-10-02 / MF-01]

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | S-01 | 1 |
| Main Flow | S-02, S-03 | 2 |
| Detail | S-06, S-07 | 2 |
| Negative | S-04, S-05 | 2 |

## Rekap Provenance

| Provenance | Jumlah | Skenario |
|---|---|---|
| `[DIKONFIRMASI]` | 5 | S-01, S-02, S-03, S-04, S-05 |
| `[HASIL-BACA]` | 2 | S-06, S-07 (merujuk bukti eksekusi Step 9) |
| `[HASIL-BACA-MURNI]` | 0 | — |
| `[PERLU-KEPUTUSAN]` | 0 | — |

Semua skenario Smoke/Negative `[DIKONFIRMASI]` live.

## Human QA Checklists

Digenerate di `human_qa/` (`00_README.md`, `01_SMOKE.md`, `02_MAIN_FLOW.md`, `03_DETAIL.md`, `04_NEGATIVE.md`).

## Loop-back

Tidak ada skenario Fail → tidak ada loop-back ke Step 9.

## Verdict

- [x] ✅ Lulus — semua skenario `[DIKONFIRMASI]`/`[HASIL-BACA]` (0 `[HASIL-BACA-MURNI]`), Cross-Version Compare 0 `REGRESI` — lanjut ke step 11
- [ ] ⚠️ Lulus Bersyarat
- [ ] ❌ Ada kegagalan
