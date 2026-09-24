# Cross-Version Compare — appointment_jitsi (19.0 → 20.0)

**Titik panggil:** A (in-flow, dari `10_qa/10_BUSINESS_FLOW_MIGRATION.md`) — kriteria: ada dependency Enterprise (`appointment`, OEEL-1).
**Tanggal:** 2026-09-24
**Prosedur:** `migration-tool/templates/CROSS_VERSION_COMPARE.md` (tidak disalin ulang di sini).

---

## 1. Environment

| Instance | URL | Kode modul | Native | DB |
|---|---|---|---|---|
| Source 19.0 | `http://127.0.0.1:8098` | `git archive migration/19.0` (snapshot read-only di scratchpad, env `SRC19_ADDONS`) | `odoo19` + `enterprise19` | `qa19` |
| Target 20.0 | `http://localhost:8097` | `appointment_jitsi/` @ `migration/20.0` `75f98f0` | `odoo20` + `enterprise20` | `qa20` |

Compose: `docker-env/docker-compose.cvc.yml` (image 19.0 dibangun dari `docker-env/cvc-19.0/`). Satu Postgres, dua DB, `--without-demo=all`, data dibuat manual identik per skenario. Tidak ada versi antara. Instance dimatikan `down -v` setelah selesai.

Cara menyalakan ulang (kalau perlu), dari `docker-env/`:
```bash
git -C .. archive migration/19.0 appointment_jitsi | tar -x -C /path/src19
```
```bash
COMPOSE_FILE=docker-compose.cvc.yml SRC19_ADDONS=/path/src19 docker compose up -d
```

## 2. Scope

Satu addon. Flow custom: Settings Jitsi, pembuatan event + Video Link/Join, fallback Discuss, template email booked, route controller.

## 3. Static-diff (kandidat)

`git diff migration/19.0 migration/20.0 -- appointment_jitsi`: produksi hanya `_compute_jitsi_link` (3 baris, `get_bool`/`get_int`) + versi manifest. Kandidat dari diff native (Step 2): DIFF-01 (penyimpanan boolean setting), DIFF-04 (flush + channel Discuss di `create()`), DIFF-08 (rename template). → Live-test: S-01, S-02, S-03, S-04 (+ S-05 route).

## 4. Live-test & visual pass

Detail per skenario: `10_qa/10_BUSINESS_FLOW_MIGRATION.md`. Screenshot sejajar: `10_qa/screenshots/source-19.0/` vs `10_qa/screenshots/target-20.0/`.

Visual pass terpisah (blok Settings, form event, preview email): struktur & teks custom identik; perbedaan hanya gaya widget/ikon/layout email native.

## 5. Temuan

| ID | Klasifikasi | Ringkasan | Tindak lanjut |
|---|---|---|---|
| RMV-01 | `NATIVE-DIFF` | Setelah Save event baru (Jitsi aktif): 19.0 Video Link kosong & Join belum tampil sampai reload; 20.0 langsung tampil. Nilai DB identik. Akar: `create()` 20.0 flush `videocall_location` (DIFF-04). Terkait MF-03, `BSL-010`. | Tidak difix (perilaku 20.0 lebih baik, bukan kode modul). Dicatat untuk UAT. |
| RMV-02 | `NATIVE-DIFF` | Event dengan link Discuss (Jitsi nonaktif) di 20.0 otomatis mendapat `discuss.channel`; 19.0 tidak. Event Jitsi tidak mendapat channel di kedua versi. | Tidak difix. Dicatat untuk UAT. |
| RMV-03 | `NATIVE-DIFF` | Gaya widget Settings/form & layout email (wrapper `redirect-url.email`, body iframe di preview) berbeda. | Tidak difix. |

**Total:** 3 `NATIVE-DIFF`, 0 `REGRESI`, 0 `GAP-LAMA` baru, 0 `PERLU-DEV`.

## 6. Laporan penutup

Tidak ada regresi fungsional modul. Gap terbuka: tidak ada. Rekomendasi human QA sebelum go-live: jalankan `10_qa/human_qa/01_SMOKE.md` + `04_NEGATIVE.md` di instance 20.0 final (terutama S-04 dengan booking appointment nyata dari portal, bukan cuma Preview template).

## Kontribusi ke Knowledge Base

- [x] Ada — `migration-records/appointment_jitsi_19.0_20.0/SUMMARY.md` CAND-03 (update RMV-01/02) + CAND-05 (proses: login Playwright tanpa password, cookie port collision, `networkidle` Odoo).
