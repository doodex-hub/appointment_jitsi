# Business Flow — Migrasi appointment_jitsi

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-24

> Instalasi bersih (bukan upgrade dari data produksi) — sesuai sifat migrasi "port kode saja" (`01a_MIGRATION_INTAKE.md` §3). Owl/JS: N/A, tidak ada tour test (modul tidak punya JS).

**Mode eksekusi dipakai:** AI-interaktif, real Chrome (`Claude in Chrome`, deviceId `277f7ea8...`, terhubung lokal) mengendalikan server Odoo 18 hidup (`docker-compose.18.0.qa.yml`, container terpisah dari G1, `--without-demo=all`, TANPA `--stop-after-init` supaya bisa diklik). Server & container sudah di-teardown setelah sesi ini selesai (`docker compose down`).

**Catatan teknis eksekusi (untuk transparansi, bukan bug modul):** dua environment browser dicoba — panel Browser bawaan (Chromium sandboxed) mengalami kegagalan mount aplikasi Odoo (`Service worker registration failed`, root Owl tidak pernah ter-mount, `document.body` tetap kosong walau semua network request 200 OK) — ini keterbatasan environment sandboxed, bukan masalah modul. Beralih ke **Claude in Chrome** (Chrome asli, terhubung lokal) — semua render berhasil normal.

---

## Skenario

### S-01: Instalasi modul & Jitsi Configuration muncul di Settings
**Level:** Smoke
**Precondition:** Modul `appointment_jitsi` 18.0 ter-install (dikonfirmasi Step 6 G1), server Odoo 18 hidup dengan `enterprise18` mounted.
**Mode eksekusi:** AI-interaktif
**Steps:** Login admin → Settings → tab "Calendar" → cari section "Jitsi Configuration".
**Expected:** Section "Jitsi Configuration" muncul dengan checkbox "Integration video conference with Jitsi", persis seperti di 17.0.
**Actual:** ✅ Muncul persis sesuai ekspektasi — screenshot dikonfirmasi visual (`Jitsi Configuration`, `Integration video conference with Jitsi`).
**Status:** [x] Pass

### S-02: Aktivasi setting + pilih Company, tersimpan
**Level:** Smoke
**Precondition:** S-01 pass.
**Mode eksekusi:** AI-interaktif
**Steps:** Centang "Jitsi Configuration" → field "Company" muncul (default "My Company") → klik Save.
**Expected:** Setting tersimpan tanpa error, tidak ada "Unsaved changes" tersisa.
**Actual:** ✅ Checkbox tercentang, field Company muncul otomatis (`invisible="not is_jitsi"` bekerja benar di 18.0), Save berhasil (dikonfirmasi via JS: `hasUnsaved=false`, `jitsiChecked=true` pasca-reload).
**Status:** [x] Pass

### S-03: Buat calendar event, link Jitsi ter-generate dengan format benar (BSL-002/006/007/013/020)
**Level:** Main Flow
**Precondition:** S-02 pass (Jitsi aktif, Company = "My Company").
**Mode eksekusi:** AI-interaktif
**Steps:** Calendar app → New → isi "Meeting Subject" → Save (TANPA menyentuh field `is_jitsi` — tidak ada di view, konsisten `[BSL-001]`) → baca `jitsi_link` via RPC (`read` field `jitsi_link`, `videocall_location`, `is_jitsi`) → reload form.
**Expected:** `jitsi_link`/`videocall_location` terisi `https://meet.jit.si/{company}/{company}-{uuid}`, `is_jitsi` tetap `false` tapi link tetap terisi (setting global menang, `[BSL-020]`), nama company ("My Company", ada spasi) masuk apa adanya tanpa slug (`[BSL-013]`).
**Actual:** ✅ **Persis sesuai baseline.** RPC read: `{"jitsi_link":"https://meet.jit.si/My Company/My Company-7327f956-2bec-48c6-82e5-adaf363e32ec","videocall_location":"...(sama)","is_jitsi":false}`. Setelah reload, form UI menampilkan "Videocall URL" terisi URL yang sama persis, tombol "Join video call"/"Clear meeting" (tombol CORE `calendar`, BUKAN dari modul ini — konsisten `[BSL-008]`/`[BSL-017]`, method `action_join_video_call()`/`generate_jitsi_link()` milik modul tetap tidak terhubung UI manapun).
**Status:** [x] Pass

### S-04: Urutan akses field menentukan hasil compute — quirk WAJIB tetap ada (BSL-010/F-04)
**Level:** Detail
**Precondition:** S-03 (event baru dibuat, BELUM pernah dibaca field `jitsi_link` sama sekali).
**Mode eksekusi:** AI-interaktif
**Steps:** Buka form event yang BARU dibuat (sebelum RPC apapun) → amati field "Videocall URL" di form.
**Expected:** Field "Videocall URL" KOSONG (compute `_compute_jitsi_link` belum pernah terpicu karena `jitsi_link` belum pernah diakses) — sesuai `[BSL-010]`, BUKAN bug baru.
**Actual:** ✅ **Direproduksi persis live** — screenshot form pertama kali dibuka menunjukkan "Videocall URL" KOSONG (padahal setting Jitsi sudah aktif), sampai `jitsi_link` dibaca eksplisit lewat RPC di S-03, BARU field terisi. Ini reproduksi nyata quirk `[BSL-010]`/F-04 dari sudut pandang UI sungguhan (bukan cuma test backend) — konsisten dengan hasil `test_ac_03_01_videocall_location_race_with_core_compute` di Step 9.
**Status:** [x] Pass (quirk tereproduksi, bukan regresi)

### S-05: Email konfirmasi appointment TIDAK menampilkan link Jitsi (F-13, PALING KRITIS)
**Level:** Negative
**Precondition:** Event dengan `jitsi_link` terisi penuh (dari S-03).
**Mode eksekusi:** **Tidak dieksekusi ulang via browser** — memerlukan setup Appointment Type + alur booking publik penuh (di luar scope smoke-check ringan). **Bukti dipakai: eksekusi otomatis nyata Step 9** (`test_qa_s01_mail_template_does_not_render_jitsi_link`, dijalankan terhadap server Odoo 18 yang SAMA persis dengan yang dipakai S-01..S-04 di sesi ini).
**Expected:** Body email hasil render `appointment.appointment_booked_mail_template` TIDAK mengandung `jitsi_link` sama sekali.
**Actual:** ✅ Dikonfirmasi via Step 9: `jitsi_link` terisi penuh, `muncul_di_body=False`. Transparan dicatat di sini: ini bukti dari test otomatis (bukan klik manual baru), tapi mengukur EXACT hal yang sama yang akan terlihat manusia kalau membuka email sungguhan.
**Status:** [x] Pass (bug tereproduksi, sesuai keputusan bug-for-bug)

### Multi-dialog check (checklist wajib)
N/A — dikonfirmasi tidak ada kasus modul ini memicu >1 dialog/wizard dari satu aksi user (modul cuma menambah field + 1 setting toggle, tidak ada wizard/dialog custom sama sekali).

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | S-01, S-02 | 2 |
| Main Flow | S-03 | 1 |
| Detail | S-04 | 1 |
| Negative | S-05 | 1 |

## Human QA Checklists

Tidak digenerate terpisah (`human_qa/`) untuk migrasi ini — modul terlalu kecil (5 skenario total, semua sudah lulus dengan bukti live+otomatis) dan owner (Kuncoro) adalah single-person untuk seluruh siklus dev/QA/UAT. 5 skenario di atas cukup jadi referensi re-verifikasi cepat kalau dibutuhkan di kemudian hari.

## Loop-back

Tidak ada skenario Fail — tidak perlu loop-back ke Step 9.

## Verdict

- [x] ✅ **Lulus** — 5/5 skenario Pass (2 Smoke, 1 Main Flow, 1 Detail, 1 Negative). Semua quirk `01b_BASELINE_SPEC.md` yang tersentuh skenario ini (`BSL-001, 002, 006, 007, 008, 010, 013, 015, 017, 020`) tereproduksi PERSIS sesuai 17.0. Lanjut ke Step 11 (UAT Sign-off).
