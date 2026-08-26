# Findings — appointment_jitsi (migrasi 18.0 → 19.0)

> **Cross-cutting, direkomendasikan (tidak kondisional)** — dokumen konsolidasi TUNGGAL untuk semua
> gap/bug/ambiguitas yang butuh keputusan manusia selama migrasi, supaya user tidak perlu buka
> `01b_BASELINE_SPEC.md`/`03_MIGRATION_SPEC.md`/`04_SPEC_COMPLETENESS_REVIEW.md`/`08_CODE_REVIEW.md`
> satu per satu untuk tahu apa yang masih terbuka. Hidup di root `doc/` (sejajar `PROMPT_LOG.md`).

**Modul:** appointment_jitsi
**Migrasi:** 18.0 → 19.0
**Terakhir update:** 2026-08-26

---

## Beda Peran dari Mekanisme Lain (jangan bingung/duplikat)

| Mekanisme | Kapan dipakai | Sifat |
|---|---|---|
| Format `ESCALATION` (`CLAUDE.md`) | Isu **blocking** — butuh keputusan user SEBELUM lanjut ke step/fase berikutnya | Sinkron, muncul di respons AI saat itu juga |
| Tag `[GAP]` di `01b_BASELINE_SPEC.md` | Penyimpangan spec lama vs kode aktual, per-klaim `BSL-NNN` | Inline, granular per klaim |
| Section Gap di `04_SPEC_COMPLETENESS_REVIEW.md` / `08_CODE_REVIEW.md` | Gap spesifik di titik gate itu | Inline, per dokumen |
| **`FINDINGS.md` (file ini)** | **Semua finding lintas step (1-11) yang butuh keputusan manusia** | Living document, append-only |

**Catatan prefix `MF-`:** modul ini juga pernah lewat migrasi 17.0→18.0 (`doc-dev/migration_17.0_18.0/doc/`, tidak ada `FINDINGS.md` cross-cutting terpisah di project itu — findings-nya tercatat di `CLAUDE.md` §Ringkasan) dan `doc-dev/backfill/FINDINGS.md` (skema `F-NNN`, 13 temuan F-01..F-13). File ini pakai skema `MF-NNN` sendiri untuk pasangan versi 18.0→19.0, tidak menimpa/menomori ulang `F-NNN` backfill.

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | `@api.model create` di-route ke `model_create_multi` di 19.0 (bukan `model_create_single` seperti 18.0) — `values` di `create()` modul ini SELALU list, tidak pernah dict mentah | 2 | `[GAP-MIGRASI]` | Sedang-Tinggi | ✅ RESOLVED 2026-08-26 — dampak dikonfirmasi empiris di G1 (2/13 test gagal), dev pilih terima observable-outcome baru + update 2 assertion test, create() TIDAK diubah |
| MF-02 | `ir.actions.act_window.target` value `'inline'` DIHAPUS TOTAL di 19.0 — install GAGAL (`ValueError`) pada `res_config_settings_action` (dead code, tidak pernah dipakai) | 6 (G1) | `[GAP-MIGRASI]` | **Tinggi (install-blocking)** | ✅ RESOLVED 2026-08-26 — diubah ke `'current'`, zero observable impact (action tidak pernah dipanggil) |

**Finding yang DIWARISI dari project sebelumnya (bukan finding baru, dicatat sebagai referensi — detail lengkap di `01b_BASELINE_SPEC.md`):** 13 bug/quirk asal backfill (`F-01`..`F-13`, terutama `F-13`/`BSL-015` — email Jitsi tidak pernah aktif) semuanya WAJIB dipertahankan bug-for-bug di 19.0, sudah dikonfirmasi dev di `01a_MIGRATION_INTAKE.md` §Ringkasan poin 5. Tidak dicatat ulang sebagai `MF-NNN` di sini kecuali muncul keputusan BARU yang berbeda dari keputusan 17.0→18.0.

---

## Detail

### MF-01 — `@api.model create` di-route ke `model_create_multi` di 19.0 (bukan `model_create_single` seperti 18.0)
**Ditemukan di:** Step 2 (2026-08-26)
**Tag:** `[GAP-MIGRASI]` — genuinely muncul karena perubahan platform 19.0, perlu keputusan cara penanganan (bukan bug source yang diwarisi).
**Ref:** `DIFF-01` (`02_DIFF_ANALYSIS.md`), berdampak ke `[BSL-005]`/`[BSL-009]` (`01b_BASELINE_SPEC.md`)
**Lokasi:** `appointment_jitsi/models/calendar_event.py` — override `create(self, values)` dengan `@api.model`
**Deskripsi:** Di 18.0, `@api.model` pada method bernama `create` di-route ke `model_create_single()` (`odoo/api.py`) — wrapper-nya memecah input LIST menjadi panggilan per-dict, jadi `values` di dalam method SELALU dict tunggal per invocation (verified: `_model_create_single`, `odoo/api.py:467-474`). Di 19.0, `@api.model` pada `create` di-route ke `model_create_multi()` (`odoo/orm/decorators.py:309-368`) — wrapper ini TIDAK memecah list, dict tunggal cuma dibungkus `[vals]`. Akibatnya `values` di dalam method modul ini SEKARANG SELALU list, tidak pernah dict mentah.
**Dampak:** Cabang `if 'is_jitsi' in values:` di `create()` (`[BSL-005]`) mengecek keanggotaan STRING di LIST, bukan key di dict — tidak akan pernah `True` lagi, TERMASUK untuk single-create (beda dari 18.0 yang benar untuk single-create). Efek UUID-generation eksplisit dan reset `access_token=False` di `create()` kemungkinan besar tidak lagi terpicu. **Mitigasi kemungkinan:** `_compute_jitsi_link` (`[BSL-006]`) punya logic UUID-generation redundan sendiri, jadi `jitsi_link` observable KEMUNGKINAN tetap terisi lewat jalur compute — tapi paruh kedua `[BSL-005]` (reset eksplisit `access_token=False`) kemungkinan benar-benar hilang.
**Rekomendasi:** JANGAN asumsikan aman atau rusak dari analisis statis ini saja. Step 6: port kode `create()` 1:1 dulu (bug-for-bug default). Step 9: jalankan 13 test existing terhadap 19.0 dan bandingkan **per-assertion** (bukan cuma count PASS) terutama test yang menutupi `[BSL-005]`/`[BSL-009]` — kalau ada assertion yang berubah hasil, catat sebagai `[GAP-MIGRASI]` baru dan eskalasi ke dev (opsi: terima behavior baru sebagai "perubahan wajib demi kompatibilitas 19.0" vs adaptasi kode `create()` supaya observable behavior tetap identik).

**Hasil empiris G1 (2026-08-26):** dikonfirmasi dampak NYATA, persis sesuai prediksi — `2 failed, 0 error(s)` dari 13 test:
- `test_ac_02_01_create_single_dict_enables_token` — `access_token` tetap terisi (non-empty), TAPI format berubah dari 32-char `uuid4().hex` jadi 36-char UUID berdash (dari mekanisme default core lain, bukan cabang eksplisit `create()` yang sudah tidak terpicu). Observable outcome (link valid) tetap OK, cuma format token kosmetik berbeda.
- `test_ac_02_02_create_single_dict_disable_resets_token` — paruh reset `access_token=False` saat `is_jitsi=False` TIDAK terjadi lagi untuk single-create — nilai yang caller kirim lolos apa adanya.

**ESCALATION dijawab dev (2026-08-26):** ditawarkan 2 opsi — (1) terima observable-outcome baru, `create()` TIDAK diubah, update assertion 2 test; (2) rewrite `create()` iterasi per-item untuk restore behavior 18.0 persis, TAPI efek sampingnya `[BSL-009]`/quirk batch-create ikut "diperbaiki" tanpa sengaja (melanggar bug-for-bug eksplisit untuk `BSL-009`). **Dev memilih opsi (1)** — konsisten prioritas: `BSL-009` (bug yang eksplisit disetujui dipertahankan) > konsistensi mekanisme `create()` single-record (bukan bug yang perlu dipertahankan, cuma implementation detail).
**Keputusan pemilik modul:** ✅ **Diterima (2026-08-26)** — observable-outcome 19.0 yang baru (format token berbeda, reset-to-False untuk single-create hilang) DITERIMA sebagai baseline 19.0 yang sah. `models/calendar_event.py` `create()` TIDAK diubah. `tests/test_appointment_jitsi.py` — `test_ac_02_01`/`test_ac_02_02` assertion diupdate untuk mencerminkan behavior baru (lihat docstring test masing-masing untuk detail lengkap alasan).

---

### MF-02 — `ir.actions.act_window.target` value `'inline'` dihapus total di 19.0 — install GAGAL
**Ditemukan di:** Step 6, checkpoint G1 (2026-08-26)
**Tag:** `[GAP-MIGRASI]` — genuinely muncul karena perubahan platform 19.0 (field selection Odoo core, bukan bug source yang diwarisi).
**Ref:** `[BSL-022]` (`01b_BASELINE_SPEC.md`, baru ditambahkan — gap baseline sebelumnya)
**Lokasi:** `appointment_jitsi/views/calendar_views.xml:9` — `<record id="res_config_settings_action" model="ir.actions.act_window">`, `<field name="target">inline</field>`
**Deskripsi:** Odoo 18.0 `ir.actions.act_window.target` selection: `current`/`new`/`inline`/`fullscreen`/`main`. Odoo 19.0 (`enterprise19.0/odoo/addons/base/models/ir_actions.py:317`): opsi `inline` **DIHAPUS TOTAL** (bukan cuma dianggap deprecated) — tidak seperti pola deprecation Odoo yang biasanya menyisakan alias backward-compat (mis. `toggle_active` di `knowledge/version-diffs/18-to-19.md` §1). G1 install test pertama (docker, `odoo:19.0` + `enterprise19.0`) GAGAL total dengan traceback `ValueError: Wrong value for ir.actions.act_window.target: 'inline'` saat parsing `data/calendar_views.xml` — modul tidak bisa ter-install SAMA SEKALI di 19.0 tanpa fix ini.
**Dampak:** Install-blocking murni (bukan cuma runtime warning) — **tanpa fix ini modul TIDAK BISA dimigrasikan ke 19.0 sama sekali.** Record `res_config_settings_action` sendiri dikonfirmasi dead code/orphaned (`[BSL-022]`, tidak pernah direferensikan menu/button/kode manapun di modul ini) — jadi nilai `target` yang dipilih tidak pernah teramati user manapun.
**Rekomendasi/Resolusi:** Diubah `inline` → `current` (nilai default field ini di kedua versi) — pilihan paling netral untuk record yang tidak pernah benar-benar dibuka. **Tidak ada perubahan observable behavior** karena action ini tidak pernah dipanggil. Diterapkan langsung tanpa eskalasi (keputusan teknis dengan satu opsi jelas aman, konsisten prinsip "Eksekusi Berkelanjutan").
**Keputusan pemilik modul:** ✅ Diterima — perubahan wajib demi kompatibilitas 19.0, di luar kendali bug-for-bug (nilai lama tidak ada penggantinya, dihapus total dari Odoo core).

---

---

## Cara Pakai

1. Update SETIAP KALI step manapun (1-11) menemukan gap/bug/ambiguitas yang butuh keputusan manusia — jangan tunggu sampai akhir project.
2. ID `MF-NNN` sequential, tidak pernah dipakai ulang.
3. Finding yang diwarisi dari bug/quirk source ditag `[DIWARISI-SOURCE]`. Finding yang genuinely muncul KARENA migrasi (breaking change 19.0) ditag `[GAP-MIGRASI]`, referensi `DIFF-NNN` dari `02_DIFF_ANALYSIS.md`.
4. Step 4 dan Step 8 WAJIB baca file ini sebagai bagian gate.
