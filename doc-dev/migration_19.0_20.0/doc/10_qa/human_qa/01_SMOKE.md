# Smoke Test — appointment_jitsi

**Level:** Smoke — flow paling kritis. Kalau salah satu langkah di sini gagal: STOP, jangan lanjut deploy/testing lain, balik ke step 9 atau eskalasi ke tim dev.
**Estimasi waktu:** ~3 menit.
**Sumber:** skenario ber-`Level: Smoke` di `../10_BUSINESS_FLOW_MIGRATION.md` (S-01).

```
1. Login sebagai admin di Odoo 20.0 (Enterprise). Buka Apps, pastikan "Appointment Jitsi" berstatus Installed.
2. Buka Settings -> Calendar. Di bawah "Outlook Calendar" / "Google Calendar" harus ada blok "Jitsi Configuration".
3. Selama belum dicentang, field "Company" di blok itu TIDAK tampil.
4. Centang "Jitsi Configuration" -> field "Company" muncul, terisi company Anda.
5. Klik Save. Halaman reload: "Jitsi Configuration" tetap tercentang dan Company tetap terisi.
6. Buka Calendar -> Meetings -> New, isi judul, Save. Field "Video Link" (boleh perlu reload halaman) berisi
   https://meet.jit.si/<Nama Company>/<Nama Company>-<kode>.
```
Gagal kalau: modul error saat install, blok Jitsi tidak ada, Save error, atau Video Link bukan link meet.jit.si.

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker QA 20.0 (port 8097), DB kosong tanpa demo | AI (Playwright MCP) | Pass | Video Link langsung tampil tanpa reload di 20.0 (RMV-01) |
