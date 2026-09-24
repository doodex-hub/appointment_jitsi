# Main Flow — appointment_jitsi

**Level:** Main Flow — flow bisnis inti sehari-hari.
**Estimasi waktu:** ~5 menit.
**Sumber:** skenario ber-`Level: Main Flow` di `../10_BUSINESS_FLOW_MIGRATION.md` (S-02, S-03). Prasyarat: Smoke sudah Pass (Jitsi aktif).

### A. Join meeting lewat Jitsi (S-02)
```
1. Calendar -> Meetings -> New. Isi judul saja (jangan ubah field lain), Save.
2. Lihat field "Video Link": harus link https://meet.jit.si/<Company>/<Company>-<kode>.
   (Catatan: di 19.0 link baru muncul setelah halaman di-reload; di 20.0 langsung muncul — itu normal.)
3. Klik ikon "Join" (panah masuk kotak) di sebelah Video Link.
4. Tab baru terbuka ke alamat yang SAMA PERSIS dengan Video Link.
```

### B. Matikan Jitsi -> kembali ke Odoo Discuss (S-03)
```
1. Settings -> Calendar -> hilangkan centang "Jitsi Configuration" -> field Company hilang -> Save.
2. Setelah reload, "Jitsi Configuration" tetap TIDAK tercentang.
3. Calendar -> Meetings -> New, isi judul, Save.
4. "Video Link" sekarang link Odoo Discuss (.../calendar/join_videocall/<kode>), BUKAN meet.jit.si.
5. Event lama (dibuat saat Jitsi aktif) diharapkan tetap memakai link Jitsi-nya (link hanya dihitung ulang
   kalau token event berubah). Catatan: langkah ini belum diuji live pada run 2026-09-24 — centang hasilnya di sini.
6. (Info 20.0) Event Discuss otomatis mendapat channel di aplikasi Discuss — fitur bawaan Odoo 20, bukan modul ini.
7. Nyalakan lagi "Jitsi Configuration" + Save supaya kembali ke kondisi awal.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker QA 20.0 (8097) + 19.0 (8098) berdampingan | AI (Playwright MCP) | Pass | Identik 19.0 kecuali RMV-01/RMV-02 (native) |
