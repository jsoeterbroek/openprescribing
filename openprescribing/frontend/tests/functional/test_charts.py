# -*- coding: utf-8 -*-
from .selenium_base import SeleniumTestCase


class MapTest(SeleniumTestCase):
    # These tests run against a MockAPIServer started by the
    # custom_runner
    def test_map_slider(self):
        response = self.browser.get("https://www.google.com")
        print("Google response:")
        print(response)
        if not "Google" in self.browser.title:
            raise Exception("Unable to load google page!")
        elem = self.browser.find_element_by_name("q")
        elem.send_keys("BrowserStack")
        elem.submit()
        print(self.browser.title)
        self.browser.quit()

class SmallListTest(SeleniumTestCase):
    # These tests run against a MockAPIServer started by the
    # custom_runner
    def test_nothing_hidden_by_default(self):
        self.browser.get(
            self.live_server_url
            + (
                "/analyse/#org=practice&orgIds=X&numIds=0212000AA"
                "&denom=total_list_size&selectedTab=summary"
            )
        )
        warning = self.find_by_xpath("//div[contains(@class, 'toggle')]/a")
        self.assertIn("Remove", warning.text)
        xlabels = self.find_by_xpath("//*[contains(@class, 'highcharts-xaxis-labels')]")
        self.assertIn("GREEN", xlabels.text)
        warning.click()
        warning = self.find_by_xpath("//div[contains(@class, 'toggle')]/a")
        self.assertIn("Show", warning.text)
        xlabels = self.find_by_xpath("//*[contains(@class, 'highcharts-xaxis-labels')]")
        self.assertNotIn("GREEN", xlabels.text)


class AnalyseSummaryTotalsTest(SeleniumTestCase):
    def test_summary_totals_on_analyse_page(self):
        self.browser.get(self.live_server_url + "/analyse/#org=CCG&numIds=0212000AA")
        expected = {
            "panel-heading": (
                "Total prescribing for Rosuvastatin Calcium across all "
                "CCGs in NHS England"
            ),
            "js-selected-month": "Sep '16",
            "js-financial-year-range": "Apr—Sep '16",
            "js-year-range": "Oct '15—Sep '16",
            "js-cost-month-total": "29,720",
            "js-cost-financial-year-total": "178,726",
            "js-cost-year-total": "379,182",
            "js-items-month-total": "1,669",
            "js-items-financial-year-total": "9,836",
            "js-items-year-total": "20,622",
        }
        for classname, value in expected.items():
            selector = (
                '//*[@id="{id}"]'
                '//*[contains(concat(" ", @class, " "), " {classname} ")]'.format(
                    id="js-summary-totals", classname=classname
                )
            )
            element = self.find_by_xpath(selector)
            self.assertTrue(
                element.is_displayed(), ".{} is not visible".format(classname)
            )
            self.assertEqual(element.text.strip(), value)
