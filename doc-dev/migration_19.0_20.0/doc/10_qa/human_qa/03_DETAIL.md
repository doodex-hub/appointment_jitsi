# Detail — appointment_jitsi

**Level:** Detail — varian/perilaku khusus yang SENGAJA dipertahankan dari 19.0 (bukan bug baru).
**Estimasi waktu:** ~10 menit.
**Sumber:** skenario ber-`Level: Detail` di `../10_BUSINESS_FLOW_MIGRATION.md` (S-06, S-07). Sebagian besar sudah diuji otomatis (Step 9); langkah di bawah untuk re-cek manual.

```
1. (Nama company masuk mentah) Settings -> Calendar -> Jitsi -> pilih company yang namanya berspasi, Save.
   Buat event baru: link Jitsi berisi nama company apa adanya (dengan spasi), muncul 2 kali di URL.
2. (Satu company untuk semua) Di database multi-company, buat event dari company lain:
   link Jitsi-nya tetap memakai nama company yang dipilih di Settings, bukan company event.
3. (Centang "Enable Jitsi" per event tidak berpengaruh ke link) Link ditentukan setting global saja.
4. (Mengubah event lama tidak membuat link baru) Edit event yang sudah ada / ubah setting:
   Video Link event lama TIDAK berubah otomatis.
5. (Perubahan disengaja 20.0, MF-01) Kalau parameter sistem "is_jitsi_param" diisi manual "False"/"0"
   lewat Settings -> Technical -> System Parameters, di 20.0 Jitsi dianggap NONAKTIF (di 19.0 dianggap aktif).
   Jalur normal lewat Settings tidak terpengaruh.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Automated test Step 9 (Odoo 20.0) | AI | Pass | Nilai identik 19.0; poin 5 disetujui dev |
