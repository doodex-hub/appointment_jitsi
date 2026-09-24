# Negative — appointment_jitsi

**Level:** Negative — hal yang HARUS TIDAK terjadi. Jalankan minimal sekali sebelum rilis besar.
**Estimasi waktu:** ~5 menit.
**Sumber:** skenario ber-`Level: Negative` di `../10_BUSINESS_FLOW_MIGRATION.md` (S-04, S-05).

### A. Email booking TIDAK berisi link Jitsi (S-04) — perilaku lama yang sengaja dipertahankan
```
1. Pastikan Jitsi aktif dan ada event dengan Video Link meet.jit.si.
2. Aktifkan Developer Mode. Settings -> Technical -> Email Templates -> "Appointment: Appointment Booking".
3. Klik "Preview", pilih event tadi sebagai record.
4. Periksa isi email: tombol Join/View dan link "Video meeting" mengarah ke alamat Odoo
   (/calendar/meeting/join?token=..., /calendar/videocall/...). TIDAK boleh ada tulisan/link meet.jit.si.
5. (Lebih baik lagi) Lakukan booking appointment sungguhan dari portal, cek email yang diterima: sama, tanpa meet.jit.si.
```
Kalau link meet.jit.si MUNCUL di email: itu perubahan perilaku yang tidak disengaja -> laporkan ke tim dev.

### B. Tidak ada halaman custom /calendar/join_jitsi (S-05)
```
1. Buka http://<server>/calendar/join_jitsi/abc di browser.
2. Harus tampil halaman 404 (tidak ditemukan).
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker QA 20.0 + 19.0 | AI (Playwright MCP + curl) | Pass | A lewat Preview template (belum booking portal nyata) |
