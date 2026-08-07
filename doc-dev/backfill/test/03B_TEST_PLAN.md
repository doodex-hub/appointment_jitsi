# Test Plan — appointment_jitsi

**Module:** `appointment_jitsi`
**Ref:** `doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md`
**Taxonomy:** vocab test bawaan Odoo (`TransactionCase`/`HttpCase`/`Tour`) — `cicd/test_design/odoo-testing-taxonomy.md`
tidak diakses sesi ini (opsional, lihat `PLAYBOOK.md` §0), istilah belum disamakan ke taxonomy resmi Doodex.
**Dibuat oleh:** BACKFILL (Step 03B, backfill)
**Last Updated:** 2026-08-07

---

## Step 04 — Developer Testing (backfill)

**Output:** `04A_DEV_TESTING.md`. Tidak ada `04B_API_TEST.md` — modul tidak expose endpoint API
eksternal (controller satu-satunya, `controllers/appointment.py`, 100% dead code / di-comment-out,
lihat F-06).

| AC | Deskripsi singkat | Unit | Integration | API |
|---|---|---|---|---|
| AC-01-01 | Jitsi aktif + company valid → `jitsi_link` format benar | | ✓ | |
| AC-01-02 | Jitsi tidak aktif → fallback Discuss | | ✓ | |
| AC-01-03 | `is_jitsi_param` uncheck → tetap truthy? (F-01) | | ✓ | |
| AC-02-01 | `create()` single dict `is_jitsi=True` → `access_token` baru | | ✓ | |
| AC-02-02 | `create()` single dict `is_jitsi=False` → `access_token` direset `False` | | ✓ | |
| AC-02-03 | `create()` batch list → cek `'is_jitsi' in values` gagal terdeteksi (F-03) | | ✓ | |
| AC-03-01 | `videocall_location` ditulis compute lain — race dengan compute resmi (F-04) | | ✓ | |
| AC-04-01 | Toggle `is_jitsi` via `write()` tidak memicu recompute (F-02) | | ✓ | |
| AC-05-01 | `company_param` global lintas multi-company (F-05) | | ✓ | |
| AC-06-01 | Nama company berspasi masuk mentah ke URL (F-07) | ✓ | | |
| AC-07-01 | Controller dead code — tidak ada route terdaftar | ✓ | | |
| AC-08-01 | `generate_jitsi_link()`/`clear_jitsi_link()` tetap berfungsi walau tidak dipanggil UI | ✓ | | |

**Ringkasan:** 3 AC → Unit, 9 AC → Integration, API = N/A (tidak ada endpoint eksternal modul
ini — route satu-satunya sudah dead code, dikonfirmasi statis di Step 01/AC-07-01).

**Email (kondisional):** Outgoing — modul memodifikasi ISI (bukan header) dua mail template
BAWAAN Odoo (`calendar.calendar_template_meeting_update`, `appointment.appointment_booked_mail_template`)
yang dipakai jalur pengiriman email EXISTING milik `calendar`/`appointment` core (bukan jalur
pengiriman baru buatan modul ini). Modul TIDAK menginjeksi/memodifikasi header (To/Cc/Bcc/dst) —
cukup diverifikasi lewat assert isi `body_html` hasil `_render_field`/`generate_email` (Integration
`TransactionCase`, tidak butuh Mailpit/GreenMail). Mailpit OPSIONAL untuk verifikasi visual Step 07
kalau `docker-env/` kebetulan sudah disiapkan untuk keperluan lain — tidak wajib untuk modul ini,
tidak ditambahkan ke `docker-env/` secara default (lihat `CLAUDE.md` §"Cek wajib Step 01 — modul
menyentuh email").

---

## Step 07 — QA Testing (level AI-interaktif + Smoke human-confirmed, TANPA UAT)

**Output:** `07_QA_TESTING.md`. Tidak ada `07B_QA_AI_BROWSER.md` terpisah — modul tidak punya
dialog/wizard custom, tidak ada JS/OWL kustom yang perlu dibuktikan lewat Tour/browser di luar apa
yang sudah tercakup Integration test Step 04 (satu-satunya UI baru adalah dua field standar
`invisible`-toggle di form Settings, pola bawaan Odoo, risiko rendah). Skenario visual dicatat
sebagai desk-review eksplisit di `07_QA_TESTING.md` §3, bukan Tour headless — dijelaskan alasannya
di sana (bukan dilewatkan diam-diam).

| AC | Deskripsi singkat | AI-interaktif (07 §3) | AI-Browser (07B) |
|---|---|---|---|
| AC-01-01 | Jitsi aktif → link benar (ulang, level skenario end-to-end) | ✓ | |
| AC-01-02 | Jitsi nonaktif → fallback Discuss (skenario end-to-end) | ✓ | |
| AC-01-03 | Uncheck setting → cek link generation berikutnya (F-01) | ✓ | |
| AC-04-01 | Toggle `is_jitsi` di form existing event → cek tampilan link (F-02) | ✓ | |
| AC-05-01 | Multi-company: dua event beda company → bandingkan `jitsi_link` (F-05) | ✓ | |
| AC-07-01 | Konfirmasi tidak ada route `/calendar/join_jitsi/...` aktif | ✓ | |
| — | Skenario "satu dialog/wizard disentuh" | N/A — modul tidak punya >1 dialog/wizard yang terpicu dari satu aksi (tidak ada wizard sama sekali di modul ini) | |

**Ringkasan:** BACKFILL pakai AI-interaktif (`07_QA_TESTING.md` §3) sebagai default. AI-Browser/Tour
TIDAK dipakai untuk modul ini (rasional di atas) — kalau asumsi ini ternyata salah setelah Step 04
selesai (mis. ditemukan behavior UI yang genuinely butuh JS/OWL nyata untuk dibuktikan), akan
direvisi dan ditambahkan `07B_QA_AI_BROWSER.md`/Tour sebelum Step 07 ditutup.

---

## Ringkasan Keseluruhan

| Step | Tipe | Jumlah AC |
|---|---|---|
| 04 | Unit | 3 |
| 04 | Integration | 9 |
| 04 | Smoke | 1 happy path (Jitsi aktif end-to-end: settings → create event → join) |
| 04 | API (kondisional) | N/A |
| 07 | AI-interaktif (`07` §3) | 6 (subset paling berisiko/butuh konfirmasi visual) |
| 07 | AI-Browser (`07B`) | 0 — tidak dipakai, lihat rasional di atas |
