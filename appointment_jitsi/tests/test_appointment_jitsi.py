# -*- coding: utf-8 -*-
import logging

from odoo.tests.common import TransactionCase, tagged

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestAppointmentJitsi(TransactionCase):
    """BACKFILL tests — doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.CalendarEvent = cls.env['calendar.event']
        cls.ICP = cls.env['ir.config_parameter'].sudo()

    def _enable_jitsi(self, company):
        self.ICP.set_param('is_jitsi_param', 'True')
        self.ICP.set_param('company_param', str(company.id))

    def _disable_jitsi(self):
        self.ICP.set_param('is_jitsi_param', 'False')

    def test_ac_01_01_jitsi_link_format_when_enabled(self):
        """AC-01-01 (BR-01): Jitsi aktif + company valid -> jitsi_link format benar."""
        company = self.env.company
        self._enable_jitsi(company)
        event = self.CalendarEvent.create({
            'name': 'Test Jitsi Event',
            'start': '2026-08-10 10:00:00',
            'stop': '2026-08-10 11:00:00',
        })
        expected_prefix = "https://meet.jit.si/%s/%s-" % (company.name, company.name)
        _logger.info("BACKFILL AC-01-01: jitsi_link=%s videocall_location=%s",
                     event.jitsi_link, event.videocall_location)
        self.assertTrue(event.access_token, "access_token harus ter-generate saat compute jalan")
        self.assertTrue(event.jitsi_link.startswith(expected_prefix),
                         "jitsi_link tidak sesuai format BR-01: %s" % event.jitsi_link)
        self.assertEqual(event.videocall_location, event.jitsi_link,
                          "videocall_location harus disamakan dengan jitsi_link saat Jitsi aktif (BR-04)")

    def test_ac_01_02_fallback_discuss_when_disabled(self):
        """AC-01-02 (BR-01): Jitsi tidak pernah di-set -> fallback ke Discuss."""
        self.ICP.search([('key', '=', 'is_jitsi_param')]).unlink()
        event = self.CalendarEvent.create({
            'name': 'Test Discuss Fallback Event',
            'start': '2026-08-10 10:00:00',
            'stop': '2026-08-10 11:00:00',
        })
        _logger.info("BACKFILL AC-01-02: get_param(is_jitsi_param)=%r videocall_location=%r",
                     self.ICP.get_param('is_jitsi_param'), event.videocall_location)
        is_jitsi_link = bool(event.videocall_location) and \
            event.videocall_location.startswith('https://meet.jit.si')
        self.assertFalse(is_jitsi_link,
                          "Tanpa is_jitsi_param di-set, videocall_location seharusnya bukan link Jitsi")

    def test_ac_01_03_uncheck_setting_still_truthy(self):
        """AC-01-03 (BR-08 / F-01): setelah pernah aktif lalu di-uncheck, apakah tetap truthy?"""
        company = self.env.company
        self._enable_jitsi(company)
        # Konfirmasi sekali di-set, lalu "uncheck" lewat res.config.settings (jalur UI asli)
        settings = self.env['res.config.settings'].create({
            'is_jitsi': False,
            'company_param': company.id,
        })
        settings.execute()
        raw_value = self.ICP.get_param('is_jitsi_param')
        _logger.info("BACKFILL AC-01-03/F-01: get_param(is_jitsi_param) setelah uncheck = %r (type=%s)",
                     raw_value, type(raw_value).__name__)
        event = self.CalendarEvent.create({
            'name': 'Test Uncheck Event',
            'start': '2026-08-10 10:00:00',
            'stop': '2026-08-10 11:00:00',
        })
        _logger.info("BACKFILL AC-01-03/F-01: videocall_location setelah uncheck = %r",
                     event.videocall_location)
        is_still_jitsi = bool(event.videocall_location) and \
            event.videocall_location.startswith('https://meet.jit.si')
        _logger.info("BACKFILL AC-01-03/F-01 VERDICT: bug_confirmed=%s (True berarti F-01 NYATA terjadi)",
                     is_still_jitsi)
        # Dicatat sebagai temuan nyata di 04A_DEV_TESTING.md berdasar hasil log ini,
        # bukan digagalkan otomatis di sini (tujuannya observasi, lihat FINDINGS.md F-01).

    def test_ac_02_01_create_single_dict_enables_token(self):
        """AC-02-01 (BR-02): create() single dict is_jitsi=True -> access_token baru.

        Baseline 19.0 (MF-01, disetujui dev 2026-08-26): di 18.0, create()'s
        override `if 'is_jitsi' in values` melihat `values` sebagai dict mentah
        (32-char uuid4().hex dari cabang eksplisit ini). Di 19.0, @api.model
        create di-route ke model_create_multi() -- values SELALU list, cabang
        eksplisit itu tidak pernah terpicu lagi untuk single-create. access_token
        akhirnya terisi lewat mekanisme default core lain (36-char uuid berdash,
        bukan lagi uuid4().hex 32-char dari cabang eksplisit create()) -- observable
        outcome yang WAJIB tetap benar adalah access_token TERISI VALID (non-empty,
        unik), bukan format/panjang stringnya persis. Assertion panjang 32 char
        DIHAPUS (implementation detail yang sengaja berubah karena keterbatasan
        ORM 19.0, bukan regresi fungsional -- lihat FINDINGS.md MF-01)."""
        event = self.CalendarEvent.create({
            'name': 'Test Single Create Enable',
            'start': '2026-08-10 10:00:00',
            'stop': '2026-08-10 11:00:00',
            'is_jitsi': True,
        })
        self.assertTrue(event.access_token, "access_token harus tetap terisi non-empty")

    def test_ac_02_02_create_single_dict_disable_resets_token(self):
        """AC-02-02 (BR-02): create() single dict is_jitsi=False.

        Baseline 18.0: access_token direset False walau caller menyertakan nilai lain
        (cabang eksplisit create() menimpa apapun yang caller kirim). Baseline 19.0
        (MF-01, disetujui dev 2026-08-26): cabang itu tidak pernah terpicu lagi untuk
        single-create (values selalu list) -- nilai yang caller kirim di 'access_token'
        SEKARANG LOLOS APA ADANYA, tidak direset. Ini deviation yang DITERIMA SENGAJA
        (bukan diperbaiki lewat rewrite create(), supaya BSL-009/quirk batch-create
        tetap terjaga persis -- lihat FINDINGS.md MF-01 untuk alasan lengkap kenapa
        dua-duanya tidak bisa dipertahankan bersamaan di 19.0)."""
        event = self.CalendarEvent.create({
            'name': 'Test Single Create Disable',
            'start': '2026-08-10 10:00:00',
            'stop': '2026-08-10 11:00:00',
            'is_jitsi': False,
            'access_token': 'should-be-overwritten',
        })
        self.assertEqual(event.access_token, 'should-be-overwritten',
                          "MF-01 (disetujui): di 19.0 nilai caller lolos apa adanya, "
                          "TIDAK direset False lagi seperti 18.0 -- deviation disengaja")

    def test_ac_02_03_create_batch_list_is_jitsi_check_fails(self):
        """AC-02-03 (BR-03 / F-03): create() batch list -> 'is_jitsi' in values gagal terdeteksi."""
        self._disable_jitsi()
        vals_list = [
            {
                'name': 'Test Batch Event 1',
                'start': '2026-08-11 10:00:00',
                'stop': '2026-08-11 11:00:00',
                'is_jitsi': True,
            },
            {
                'name': 'Test Batch Event 2',
                'start': '2026-08-12 10:00:00',
                'stop': '2026-08-12 11:00:00',
                'is_jitsi': True,
            },
        ]
        events = self.CalendarEvent.create(vals_list)
        _logger.info("BACKFILL AC-02-03/F-03: access_token batch = %s",
                     events.mapped('access_token'))
        bug_confirmed = not any(events.mapped('access_token'))
        _logger.info("BACKFILL AC-02-03/F-03 VERDICT: bug_confirmed=%s "
                     "(True berarti override create() tidak generate access_token untuk batch)",
                     bug_confirmed)

    def test_ac_03_01_videocall_location_race_with_core_compute(self):
        """AC-03-01 (BR-04 / F-04): videocall_location ditulis dari compute lain -- HASIL
        bergantung pada urutan field mana (jitsi_link vs videocall_location) yang dibaca LEBIH
        DULU, karena videocall_location TIDAK terdaftar sebagai compute resmi _compute_jitsi_link."""
        company = self.env.company
        self._enable_jitsi(company)

        field = self.CalendarEvent._fields.get('videocall_location')
        compute_name = getattr(field, 'compute', None)
        _logger.info("BACKFILL AC-03-01/F-04: field.compute terdaftar untuk videocall_location = %r "
                     "(HARUS BUKAN '_compute_jitsi_link' -- kalau bukan, tulisan modul ini murni "
                     "side-write di luar compute resmi field itu)", compute_name)
        self.assertNotEqual(compute_name, '_compute_jitsi_link')

        # Skenario A: baca jitsi_link DULU -> _compute_jitsi_link jalan -> videocall_location
        # ikut ditulis sebagai side-effect di dalam method itu.
        event_a = self.CalendarEvent.create({
            'name': 'Test Race - read jitsi_link first',
            'start': '2026-08-10 10:00:00',
            'stop': '2026-08-10 11:00:00',
        })
        _ = event_a.jitsi_link  # trigger _compute_jitsi_link duluan
        _logger.info("BACKFILL AC-03-01/F-04 [Skenario A - jitsi_link dibaca dulu]: "
                     "jitsi_link=%r videocall_location=%r", event_a.jitsi_link, event_a.videocall_location)

        # Skenario B: baca videocall_location DULU -> compute RESMI (_compute_videocall_location,
        # core) yang jalan, BUKAN _compute_jitsi_link -- jitsi_link belum pernah disentuh sama sekali.
        event_b = self.CalendarEvent.create({
            'name': 'Test Race - read videocall_location first',
            'start': '2026-08-10 10:00:00',
            'stop': '2026-08-10 11:00:00',
        })
        videocall_first = event_b.videocall_location  # trigger compute RESMI duluan (bukan Jitsi)
        _logger.info("BACKFILL AC-03-01/F-04 [Skenario B - videocall_location dibaca dulu]: "
                     "videocall_location=%r (SEBELUM jitsi_link pernah dibaca sama sekali)",
                     videocall_first)

        bug_confirmed = (event_a.videocall_location != videocall_first)
        _logger.info("BACKFILL AC-03-01/F-04 VERDICT: bug_confirmed=%s (True berarti hasil akhir "
                     "videocall_location BERBEDA murni karena urutan field mana yang dibaca lebih "
                     "dulu, walau setup config IDENTIK di kedua skenario -- event_a=%r event_b=%r)",
                     bug_confirmed, event_a.videocall_location, videocall_first)

    def test_ac_04_01_write_toggle_no_recompute(self):
        """AC-04-01 (BR-05 / F-02): toggle is_jitsi via write() tidak memicu recompute."""
        company = self.env.company
        self._disable_jitsi()
        event = self.CalendarEvent.create({
            'name': 'Test Toggle Event',
            'start': '2026-08-10 10:00:00',
            'stop': '2026-08-10 11:00:00',
            'is_jitsi': False,
        })
        location_before = event.videocall_location
        self._enable_jitsi(company)
        event.write({'is_jitsi': True})
        location_after = event.videocall_location
        _logger.info("BACKFILL AC-04-01/F-02: before=%s after=%s", location_before, location_after)
        bug_confirmed = (location_before == location_after)
        _logger.info("BACKFILL AC-04-01/F-02 VERDICT: bug_confirmed=%s "
                     "(True berarti toggle is_jitsi TIDAK memicu recompute link)", bug_confirmed)

    def test_ac_05_01_company_param_global_multi_company(self):
        """AC-05-01 (BR-06 / F-05): company_param satu nilai global lintas company."""
        company_a = self.env.company
        company_b = self.env['res.company'].create({'name': 'Backfill Test Company B'})
        self._enable_jitsi(company_a)

        event_a = self.CalendarEvent.with_company(company_a).create({
            'name': 'Test Event Company A',
            'start': '2026-08-10 10:00:00',
            'stop': '2026-08-10 11:00:00',
        })
        event_b = self.CalendarEvent.with_company(company_b).create({
            'name': 'Test Event Company B',
            'start': '2026-08-10 12:00:00',
            'stop': '2026-08-10 13:00:00',
        })
        _logger.info("BACKFILL AC-05-01/F-05: event_a.jitsi_link=%s event_b.jitsi_link=%s",
                     event_a.jitsi_link, event_b.jitsi_link)
        self.assertIn(company_a.name, event_a.jitsi_link)
        self.assertIn(company_a.name, event_b.jitsi_link,
                       "F-05 terkonfirmasi: event company B tetap memakai nama company_param "
                       "global (company A), bukan company_id event itu sendiri")

    def test_ac_06_01_company_name_with_space_not_escaped(self):
        """AC-06-01 (BR-07 / F-07): nama company berspasi masuk mentah ke URL."""
        company = self.env['res.company'].create({'name': 'PT Doodex Indonesia'})
        self._enable_jitsi(company)
        event = self.CalendarEvent.create({
            'name': 'Test Spaced Company Name',
            'start': '2026-08-10 10:00:00',
            'stop': '2026-08-10 11:00:00',
        })
        _logger.info("BACKFILL AC-06-01/F-07: jitsi_link=%s", event.jitsi_link)
        self.assertIn(' ', event.jitsi_link,
                      "F-07 terkonfirmasi: spasi nama company masuk mentah tanpa slug/escape ke URL")
        self.assertEqual(event.jitsi_link.count(company.name), 2,
                          "F-07 terkonfirmasi: nama company muncul dua kali (duplikasi segmen path)")

    def test_ac_07_01_controller_is_dead_code(self):
        """AC-07-01: controllers/appointment.py 100% di-comment-out, tidak ada @http.route aktif."""
        import inspect
        from odoo.addons.appointment_jitsi.controllers import appointment as ctrl_module
        source = inspect.getsource(ctrl_module)
        active_lines = [
            line for line in source.splitlines()
            if line.strip() and not line.strip().startswith('#')
        ]
        _logger.info("BACKFILL AC-07-01: baris aktif (non-comment) di controllers/appointment.py = %s",
                     active_lines)
        self.assertEqual(active_lines, [],
                          "Kalau ada baris aktif, F-06 sudah tidak berlaku (controller sudah dihidupkan)")

    def test_ac_08_01_generate_and_clear_jitsi_link_still_work(self):
        """AC-08-01: generate_jitsi_link()/clear_jitsi_link() tetap berfungsi walau tidak dipanggil UI."""
        company = self.env.company
        self._enable_jitsi(company)
        event = self.CalendarEvent.create({
            'name': 'Test Manual Methods',
            'start': '2026-08-10 10:00:00',
            'stop': '2026-08-10 11:00:00',
        })
        self.assertTrue(event.jitsi_link)
        event.clear_jitsi_link()
        self.assertFalse(event.jitsi_link)
        event.generate_jitsi_link()
        self.assertTrue(event.jitsi_link, "generate_jitsi_link() harus mengisi ulang jitsi_link")

    def test_qa_s01_mail_template_does_not_render_jitsi_link(self):
        """S-01 (Step 07 / F-13): appointment_booked_mail_template TIDAK PERNAH menampilkan
        jitsi_link -- root cause: data/mail_template_data.xml TIDAK terdaftar di __manifest__.py
        'data', jadi override template ini TIDAK PERNAH di-load Odoo sama sekali. Assertion di
        bawah mendokumentasikan perilaku SEKARANG (bug) secara eksplisit -- kalau F-13 diperbaiki
        (file ditambahkan ke manifest), test ini WAJIB direvisi mengikuti behavior baru."""
        company = self.env.company
        self._enable_jitsi(company)
        partner = self.env['res.partner'].create({'name': 'Test QA Partner'})
        event = self.CalendarEvent.create({
            'name': 'Test QA Mail Render',
            'start': '2026-08-10 10:00:00',
            'stop': '2026-08-10 11:00:00',
            'partner_ids': [(4, partner.id)],
        })
        template = self.env.ref('appointment.appointment_booked_mail_template')
        rendered = template._render_field('body_html', event.ids)
        body = rendered[event.id]
        _logger.info("BACKFILL S-01/F-13: jitsi_link=%r muncul_di_body=%s",
                     event.jitsi_link, event.jitsi_link in body)
        self.assertNotIn(event.jitsi_link, body,
                          "F-13 TERKONFIRMASI RESOLVED?! data/mail_template_data.xml sudah "
                          "ter-load -- update FINDINGS.md F-13 jadi RESOLVED kalau ini terjadi")
        self.assertIn('/calendar/meeting/join?token=', body,
                      "Body seharusnya cuma memuat link 'Join' standar Odoo core (access_token), "
                      "bukan jitsi_link -- membuktikan template YANG DIPAKAI adalah versi core asli")
