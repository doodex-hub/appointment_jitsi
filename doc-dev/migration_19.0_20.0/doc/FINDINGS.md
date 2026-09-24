# Findings — appointment_jitsi (migrasi 19.0 → 20.0)

> Dokumen konsolidasi TUNGGAL untuk semua gap/bug/ambiguitas yang butuh keputusan manusia selama migrasi 19→20 (template: `migration-tool/templates/FINDINGS.md`). Prefix `MF-NNN` direset dari 01 untuk pasangan versi ini; `MF-01`/`MF-02` milik 18→19 dirujuk sebagai "MF-01 (18→19)".

**Modul:** appointment_jitsi
**Migrasi:** 19.0 → 20.0
**Terakhir update:** 2026-09-24

---

## Ringkasan

| ID | Judul | Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | `ir.config_parameter.get_param()`/`set_param()` dihapus di 20.0 — `_compute_jitsi_link` crash; padanan typed mengubah semantik string truthy (`BSL-023`) | 2 | `[GAP-MIGRASI]` | **Tinggi** | ✅ RESOLVED — opsi 1 (`get_bool`) DISETUJUI dev (Kuncoro, chat 2026-09-24) |
| MF-02 | XML-ID `appointment.appointment_booked_mail_template` di-rename `appointment_booking_mail_template` — test `test_qa_s01` wajib retarget | 2 | `[GAP-MIGRASI]` | Rendah | ✅ RESOLVED Step 6 — test diretarget, PASS di Step 9 |
| MF-03 | `calendar.event.create()` 20.0 memanggil `_ensure_videocall_channels()` (flush `videocall_location`) — bisa menggeser urutan compute `BSL-010` saat create | 2 | `[GAP-MIGRASI]` | Sedang | ✅ RESOLVED (G1 #2 + observasi Step 9) — nilai identik 19.0; event Jitsi tidak dibuatkan channel Discuss |
| MF-04 | Pelanggaran proses: AI menjalankan satu `git log` read-only di repo `enterprise20` (dilarang CLAUDE.md) | 1 | `[PROSES]` | Rendah | ✅ Dicatat & dilaporkan ke dev; tidak diulang |
| RMV-01 | Video Link event baru: 19.0 kosong sampai reload, 20.0 langsung tampil (nilai DB identik) | 10 (CVC) | `NATIVE-DIFF` | Rendah | ✅ Dicatat, tidak difix — info UAT |
| RMV-02 | Event Discuss di 20.0 otomatis mendapat `discuss.channel` (19.0 tidak); event Jitsi tidak | 10 (CVC) | `NATIVE-DIFF` | Rendah | ✅ Dicatat, tidak difix — info UAT |
| RMV-03 | Gaya widget Settings/form & layout email native berbeda | 10 (CVC) | `NATIVE-DIFF` | Info | ✅ Dicatat |
| MF-05 | UAT ditutup dengan waiver — sign-off berdasarkan bukti AI Step 9/10, bukan eksekusi manual owner | 11 | `[PROSES]` | Sedang | ✅ Diterima owner (chat 2026-09-24); 3 langkah belum pernah dites, direkomendasikan cek staging |

**Diwarisi (bukan finding baru):** F-01..F-13 (17→18) dan MF-01/MF-02 (18→19) dipertahankan sebagai baseline 19.0 (`01b_BASELINE_SPEC.md`).

---

## Detail

### MF-01 — `get_param()`/`set_param()` dihapus di 20.0
**Ditemukan di:** Step 2 (2026-09-24) — sinyal awal di Step 1.
**Tag:** `[GAP-MIGRASI]` · **Ref:** DIFF-01, DIFF-11, `[BSL-006]`, `[BSL-014]`, `[BSL-023]`
**Lokasi:** `appointment_jitsi/models/calendar_event.py` `_compute_jitsi_link` (baris 42-44); `tests/test_appointment_jitsi.py` (helper `_enable_jitsi`/`_disable_jitsi`, log `get_param` di `test_ac_01_02`/`test_ac_01_03`).
**Deskripsi:** `odoo20/odoo/addons/base/models/ir_config_parameter.py` hanya menyediakan getter/setter bertipe (`get_bool/get_int/get_float/get_str`, `set_*`). `get_param`/`set_param` tidak ada lagi (tanpa alias). Selain itu `res.config.settings.set_values()` 20.0 menyimpan boolean via `set_bool()` → row berisi `"False"` saat di-uncheck (19.0: row DIHAPUS).
**Dampak kalau di-port apa adanya:** `AttributeError` di `_compute_jitsi_link` → setiap `calendar.event.create()` gagal (compute stored dijalankan saat create) → modul memblokir Calendar/Appointment total.
**Opsi:**
1. `get_bool('is_jitsi_param')` + `get_int('company_param')` — **Risiko rendah.** Jalur UI (centang/uncheck Settings) identik dengan 19.0 (`[BSL-002]`, `[BSL-014]`). Deviasi hanya untuk nilai yang di-set MANUAL di System Parameters: `"False"`/`"0"`/`"no"`/`"off"` → nonaktif (19.0: aktif), string lain non-boolean (mis. `"abc"`) → nilai invalid → default `False` + warning log (19.0: aktif). `company_param` tidak valid/kosong → `0` → company tidak ditemukan → `'Record not found'` (sama seperti 19.0).
2. `get_str('is_jitsi_param')` dicek truthy — mempertahankan `[BSL-023]` persis, TAPI uncheck di UI menyimpan `"False"` (truthy) → Jitsi TIDAK BISA dimatikan dari Settings → bug F-01 muncul kembali di jalur utama. **Risiko tinggi.**
**Keputusan:** Opsi 1 (diterapkan AI sesuai prinsip "Eksekusi Berkelanjutan" — ada satu opsi jelas lebih aman; alasannya: workflow utama `[BSL-014]` > quirk input manual `[BSL-023]`). Test helper ikut diport: `_enable_jitsi` → `set_bool(True)` + `set_int(company.id)`, `_disable_jitsi` → `set_bool(False)` (catatan: di 19.0 helper ini sebenarnya tidak menonaktifkan Jitsi, `[BSL-023]`; dua test pemakainya hanya observasional). **Dev dapat mengoreksi keputusan ini kapan saja** — mengganti ke opsi 2 cukup satu baris.
**Keputusan pemilik modul:** ✅ **Disetujui (Kuncoro via chat, 2026-09-24)** — deviasi `BSL-023`/AC-10-02 diterima sebagai baseline 20.0.

---

### MF-02 — Rename XML-ID template "booked"
**Ditemukan di:** Step 2 (2026-09-24) · **Tag:** `[GAP-MIGRASI]` · **Ref:** DIFF-08, `[BSL-015]`
**Lokasi:** `tests/test_appointment_jitsi.py` `test_qa_s01_mail_template_does_not_render_jitsi_link`; `data/mail_template_data.xml` (tidak di-load).
**Deskripsi:** `enterprise20` tidak punya `appointment_booked_mail_template`; padanannya `appointment_booking_mail_template` (model `calendar.event`, isi setara, link join `/calendar/meeting/join?token=`). `_default_booked_mail_template_id()` di 20.0 tetap menunjuk `attendee_invitation_mail_template` (sama dengan 19.0).
**Rekomendasi/Resolusi:** retarget `env.ref` di test ke XML-ID baru (assertion sama). `data/mail_template_data.xml` TIDAK diubah — file tidak terdaftar di manifest (`[BSL-015]`), rujukan basinya tidak berefek; memperbaikinya = mengubah dead code yang dipertahankan bug-for-bug. Dicatat: kalau suatu hari file itu didaftarkan, XML-ID wajib disesuaikan.
**Keputusan pemilik modul:** perubahan wajib test-only, tidak mengubah behavior modul.

---

### MF-03 — `_ensure_videocall_channels()` di `create()` 20.0
**Ditemukan di:** Step 2 (2026-09-24) · **Tag:** `[GAP-MIGRASI]` · **Ref:** DIFF-04, `[BSL-002]`, `[BSL-010]`
**Deskripsi:** Native 20.0 menambah `events._ensure_videocall_channels()` di akhir `calendar.event.create()` yang `flush_recordset(['videocall_location'])` lalu membuat `discuss.channel` untuk event ber-`videocall_source='discuss'`. Ini bisa memaksa compute core `videocall_location` jalan sebelum `jitsi_link`.
**Rekomendasi:** port kode tanpa perubahan (bug-for-bug). Verifikasi nilai akhir di G1/Step 9: `test_ac_01_01` (assert `videocall_location == jitsi_link` saat Jitsi aktif) + log observasional `test_ac_03_01`. Kalau berubah → eskalasi.
**Status:** ✅ RESOLVED (G1 #2, 2026-09-24) — `test_ac_01_01` PASS (`videocall_location == jitsi_link`), `test_ac_03_01` Skenario A Jitsi penuh / Skenario B `videocall_location=False` / `bug_confirmed=True` = identik log 19.0. Tidak ada perubahan kode. Observasi Step 9 (`odoo shell`): event Jitsi → `videocall_source=custom`, TIDAK ada `discuss.channel`; event fallback Discuss → channel dibuat (fitur native baru 20.0, bukan behavior modul — dicatat untuk UAT). Lanjutan: RMV-01 (efek tampilan Video Link setelah Save) dan RMV-02 (channel Discuss) dari Cross-Version Compare Step 10.

---

### MF-04 — `git log` di repo `enterprise20`
**Ditemukan di:** Step 1 (2026-09-24) · **Tag:** `[PROSES]`
**Deskripsi:** Saat riset rename template, AI menjalankan `git log --oneline -3 -- appointment/data/mail_template_data.xml` di dalam `enterprise20`. Read-only (tidak mengubah apapun), tapi melanggar "Larangan mutlak: JANGAN jalankan command git apapun di repo lain" di CLAUDE.md. Sisa riset memakai `cat .git/HEAD`/`grep`/`sed` saja.
**Tindakan:** dicatat & dilaporkan di ringkasan sesi; tidak diulang.

---

### RMV-01 — Waktu tampil Video Link setelah Save (Cross-Version Compare)
**Ditemukan di:** Step 10, Cross-Version Compare (2026-09-24) · **Klasifikasi:** `NATIVE-DIFF` · **Ref:** MF-03, DIFF-04, `BSL-010`, S-02
**Deskripsi:** Jitsi aktif → Calendar → New → Save. **19.0:** form langsung setelah Save menampilkan Video Link KOSONG dan tombol Join belum ada; setelah reload tampil URL Jitsi + Join. **20.0:** URL Jitsi + Join langsung tampil. Nilai DB kedua versi identik (`jitsi_link == videocall_location`, `source=custom`). Akar: 19.0 membaca `videocall_location` untuk response form sebelum stored compute `_compute_jitsi_link` di-flush (`BSL-010`); 20.0 `create()` native memanggil `_ensure_videocall_channels()` yang flush lebih awal.
**Tindakan:** tidak difix (bukan kode modul; perilaku 20.0 tidak lebih buruk). Informasikan di UAT: user 20.0 tidak lagi perlu reload untuk melihat link.

### RMV-02 — Channel Discuss otomatis (fitur native 20.0)
**Ditemukan di:** Step 10 (2026-09-24) · **Klasifikasi:** `NATIVE-DIFF` · **Ref:** MF-03, DIFF-04, S-03
**Deskripsi:** Saat Jitsi nonaktif (fallback Discuss), event baru di 20.0 langsung mendapat `discuss.channel`; 19.0 tidak. Event Jitsi (`videocall_source=custom`) tidak mendapat channel di kedua versi (juga dikonfirmasi Step 9 `odoo shell`).
**Tindakan:** tidak difix. Info UAT.

### RMV-03 — Perbedaan tampilan native
**Ditemukan di:** Step 10 visual pass (2026-09-24) · **Klasifikasi:** `NATIVE-DIFF` · **Ref:** S-01, S-04
**Deskripsi:** checkbox/ikon bantuan Settings, widget Video Link, layout form event, email (wrapper `redirect-url.email`, footer, preview di iframe) berbeda gaya. Struktur & teks custom modul identik.

**Cross-link:** MF-03 → lihat juga RMV-01/RMV-02 (efek UI dari DIFF-04 yang ditemukan lewat Cross-Version Compare).

---

### MF-05 — UAT waiver
**Ditemukan di:** Step 11 (2026-09-24) · **Tag:** `[PROSES]`
**Deskripsi:** Owner (Kuncoro) menyatakan via chat "UAT diselsaiakn bersarkan AI-test yang sudah ada". Kolom Actual `11_UAT_CHECKLIST.md` diisi AI dengan rujukan bukti Step 9/10; tidak ada eksekusi manual oleh business user. Langkah yang TIDAK tercakup bukti apapun: T-02 sebagai user non-admin, T-03 #3 (meeting lama tetap link Jitsi setelah setting dimatikan), T-05 booking portal + email nyata (hanya Preview template).
**Rekomendasi:** jalankan `10_qa/human_qa/01_SMOKE.md` + `04_NEGATIVE.md` di staging 20.0 sebelum go-live produksi.

---

## Cara Pakai

1. Update setiap kali step manapun menemukan gap/bug/ambiguitas yang butuh keputusan manusia.
2. ID `MF-NNN` sequential, tidak dipakai ulang.
3. Step 4 dan Step 8 WAJIB baca file ini sebagai bagian gate.
