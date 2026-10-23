"""Browser regression checks for the merged static prototype.

Run: python3 -m unittest discover -s tests -v
Requires Playwright, Chromium, and access to the application's public CDNs.
"""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
from threading import Thread
import unittest

from playwright.sync_api import expect, sync_playwright


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class PrototypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.server = ThreadingHTTPServer(
            ('127.0.0.1', 0), partial(QuietHandler, directory=str(root))
        )
        cls.server_thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}/'
        cls.playwright = sync_playwright().start()
        chromium = shutil.which('chromium') or shutil.which('chromium-browser')
        cls.browser = cls.playwright.chromium.launch(
            headless=True, **({'executable_path': chromium} if chromium else {})
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()

    def setUp(self):
        self.page = self.browser.new_page(viewport={'width': 1440, 'height': 1000})
        self.errors = []
        self.failed_requests = []
        self.dialog_messages = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.on('requestfailed', lambda request: self.failed_requests.append(request.url))
        self.page.on('dialog', self.accept_dialog)
        self.page.goto(self.url, wait_until='networkidle')
        self.page.wait_for_function('typeof stackedChartInstance !== "undefined" && stackedChartInstance !== null')

    def tearDown(self):
        self.page.close()
        self.assertEqual(self.errors, [], 'Browser JavaScript errors')
        self.assertEqual(self.failed_requests, [], 'External resources failed to load')

    def toggle_premium(self):
        self.page.locator('label:has(#premiumToggle)').click()

    def accept_dialog(self, dialog):
        self.dialog_messages.append(dialog.message)
        dialog.accept()

    def select_role(self, key):
        self.page.locator('#goalJobSelect').select_option(key)

    def test_entry_charts_and_related_skill_tags(self):
        self.assertTrue(self.page.url.endswith('/linkedin_skillsbridge_prototype_skill_tags.html'))
        self.assertEqual(self.page.locator('#recommendationsGrid > div').count(), 15)
        self.assertEqual(self.page.locator('#skillPillsContainer button').count(), 6)
        self.assertEqual(self.page.evaluate('stackedChartInstance.options.scales.x.max'), 7)
        # Preserve the deployed competency values, including competency above the requirement.
        self.assertEqual(self.page.evaluate('stackedChartInstance.data.datasets[0].data'), [6, 3, 6, 2, 5])
        self.assertEqual(self.page.evaluate('stackedChartInstance.data.datasets[1].data'), [1, 0, 0, 4, 0])
        mlops = self.page.locator('#skillPillsContainer button').filter(has_text='MLOps Ops & Governance')
        self.assertIn('4/7', mlops.inner_text())
        self.assertIn('role requirement: 3/7', mlops.get_attribute('title'))
        card = self.page.locator('#recommendationsGrid > div').filter(has_text='Pro-Bono Non-Profit AI Roadmap Lead')
        self.assertEqual([text.strip() for text in card.locator('span:has(i.fa-tag)').all_text_contents()], [
            'Product Strategy & Roadmap', 'Stakeholder Management'
        ])
        self.assertTrue(self.page.locator('img').evaluate_all('(items) => items.every(i => i.complete && i.naturalWidth > 0)'))

    def test_skill_and_category_filters_survive_membership_changes(self):
        self.page.locator('#skillPillsContainer button').filter(has_text='Stakeholder Management').click()
        self.assertEqual(self.page.locator('#recommendationsGrid > div').count(), 3)
        for category in ['LEARN', 'PRACTICE', 'CONNECT']:
            self.page.locator(f'#tab-rec-{category}').click()
            self.assertEqual(self.page.locator('#recommendationsGrid > div').count(), 1)
            self.assertIn('Stakeholder Management', self.page.locator('#selectedSkillBadge').inner_text())
            self.toggle_premium()
            self.assertEqual(self.page.locator('#recommendationsGrid > div').count(), 1)
            self.assertIn('Stakeholder Management', self.page.locator('#recommendationsGrid span:has(i.fa-tag)').inner_text())
        self.select_role('solutions_arch')
        self.assertEqual(self.page.locator('#selectedSkillBadge').inner_text(), 'Showing: All Role Gaps')

    def test_all_four_roles_keep_charts_tags_and_both_cta_destinations(self):
        roles = [('principal_pm', 74), ('solutions_arch', 81), ('vp_growth', 62), ('lead_data_sci', 76)]
        for role, score in roles:
            with self.subTest(role=role):
                self.select_role(role)
                title = self.page.locator('#goalJobSelect option:checked').inner_text()
                self.assertEqual(self.page.locator('#overallPercentage').inner_text(), f'{score}%')
                self.assertEqual(self.page.locator('#skillPillsContainer button').count(), 6)
                self.assertNotIn('undefined', self.page.locator('#skillPillsContainer').inner_text())
                self.assertTrue(self.page.evaluate('stackedChartInstance.data.datasets.every(d => d.data.every(Number.isFinite))'))
                self.assertGreater(self.page.locator('#recommendationsGrid span:has(i.fa-tag)').count(), 0)
                self.assertEqual(self.page.locator('#jobsCtaLabel').inner_text(), 'Apply For Jobs Now')
                self.page.locator('#jobsCta').click()
                self.assertTrue(self.page.locator('#view-jobs').is_visible())
                self.assertFalse(self.page.locator('#jobModal').is_visible())
                self.assertEqual(self.page.locator('#jobsSearchInput').input_value(), title)
                self.assertEqual(self.page.locator('#jobsList button').count(), 4)
                self.assertTrue(all(title in text for text in self.page.locator('#jobsList h2').all_text_contents()))
                self.page.get_by_role('button', name='← Back to SkillsBridge').click()
                self.toggle_premium()
                self.assertEqual(self.page.locator('#jobsCtaLabel').inner_text(), 'AUTO-MATCH')
                self.assertIn('AUTO-MATCH READY', self.page.locator('#jobsCtaStatus').inner_text())
                self.page.locator('#jobsCta').click()
                self.assertTrue(self.page.locator('#jobModal').is_visible())
                self.assertFalse(self.page.locator('#view-jobs').is_visible())
                self.assertEqual(self.page.locator('#modalJobTitleTag').inner_text(), title)
                self.assertEqual(self.page.locator('#modalScoreBadge').inner_text(), f'{score}% Score')
                self.page.get_by_role('button', name='Close Window').click()
                self.toggle_premium()
                self.assertEqual(self.page.locator('#jobsCtaLabel').inner_text(), 'Apply For Jobs Now')

    def test_regular_jobs_search_selection_save_and_application_preview(self):
        self.page.locator('#jobsCta').click()
        listings = self.page.locator('#jobsList button')
        listings.nth(1).click()
        self.assertIn('CedarArc Digital', self.page.locator('#jobsDetail').inner_text())
        self.page.locator('#mockSaveButton').click()
        self.assertEqual(self.page.locator('#mockSaveButton').inner_text(), 'Saved')
        listings.nth(0).click()
        listings.nth(1).click()
        self.assertEqual(self.page.locator('#mockSaveButton').get_attribute('aria-pressed'), 'true')
        self.page.locator('#mockSaveButton').click()
        self.assertEqual(self.page.locator('#mockSaveButton').inner_text(), 'Save')
        self.page.get_by_role('button', name='Easy Apply', exact=True).click()
        self.assertIn('no application has been submitted', self.page.locator('#mockJobFeedback').inner_text())
        for query, count in [('Architect', 4), ('', 16), ('no such job', 0), ('<img src=x onerror=alert(1)>', 0)]:
            with self.subTest(query=query):
                self.page.locator('#jobsSearchInput').fill(query)
                self.page.get_by_role('button', name='Search', exact=True).click()
                self.assertEqual(self.page.locator('#jobsList button').count(), count)
                self.assertEqual(self.page.locator('#jobsResultsTitle').inner_text(), query or 'All jobs')
        self.assertEqual(self.page.locator('#jobsResultsTitle img').count(), 0)
        self.assertIn('No matching jobs', self.page.locator('#jobsDetail').inner_text())
        self.page.locator('#nav-recruiter').click()
        self.assertFalse(self.page.locator('#view-jobs').is_visible())
        self.assertTrue(self.page.locator('#view-recruiter').is_visible())
        self.page.locator('#nav-dashboard').click()
        self.assertTrue(self.page.locator('#view-dashboard').is_visible())

    def test_chart_click_filter_uses_current_role_after_switching(self):
        self.select_role('solutions_arch')
        self.page.evaluate("stackedChartInstance.stop(); stackedChartInstance.update('none')")
        self.page.locator('#skillsStackedChart').scroll_into_view_if_needed()
        # Click a real chart bar after changing role, rather than invoking its callback.
        point = self.page.evaluate('''() => {
            const chart = stackedChartInstance;
            const bar = chart.getDatasetMeta(0).data[0];
            const bounds = chart.canvas.getBoundingClientRect();
            return {x: bounds.left + (bar.x + bar.base) / 2, y: bounds.top + bar.y};
        }''')
        self.page.mouse.click(point['x'], point['y'])
        expect(self.page.locator('#selectedSkillBadge')).to_have_text('Filtered: Cloud System Infrastructure')
        self.assertNotIn('Product Strategy', self.page.locator('#selectedSkillBadge').inner_text())

    def test_preserved_views_and_demo_alerts(self):
        self.page.locator('#nav-recruiter').click()
        self.assertTrue(self.page.locator('#view-recruiter').is_visible())
        self.page.locator('#view-recruiter button[onclick^="alert("]').first.click()
        self.assertIn('Frictionless Outreach', self.dialog_messages[-1])
        self.page.evaluate("switchView('matcher')")
        self.page.locator('button[onclick="setGoalAndSwitch(\'solutions_arch\')"]').click()
        self.assertTrue(self.page.locator('#view-dashboard').is_visible())
        self.assertEqual(self.page.locator('#goalJobSelect').input_value(), 'solutions_arch')
        self.page.evaluate("switchView('dimensional')")
        self.assertTrue(self.page.locator('#view-dimensional').is_visible())
        self.page.locator('#nav-dashboard').click()
        self.page.locator('#recommendationsGrid button').first.click()
        self.assertIn('Navigating to featured development partner', self.dialog_messages[-1])

    def test_regular_jobs_on_mobile(self):
        self.page.set_viewport_size({'width': 390, 'height': 844})
        self.page.locator('#jobsCta').click()
        self.assertTrue(self.page.locator('#view-jobs').is_visible())
        self.page.locator('#jobsList button').nth(2).click()
        self.page.get_by_role('button', name='Easy Apply', exact=True).click()
        self.assertIn('no application has been submitted', self.page.locator('#mockJobFeedback').inner_text())
        self.page.get_by_role('button', name='← Back to SkillsBridge').click()
        self.assertTrue(self.page.locator('#view-dashboard').is_visible())


if __name__ == '__main__':
    unittest.main()
