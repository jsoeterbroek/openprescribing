import datetime
import json

from django.test import TestCase
from mock import patch

from frontend.models import PCT


class TestAPIMeasureViews(TestCase):
    fixtures = ['one_month_of_measures', '']
    api_prefix = '/api/1.0'

    def test_api_measure_global(self):
        url = '/api/1.0/measure/?measure=cerazette&format=json'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['measures'][0]['name'],
                         'Cerazette vs. Desogestrel')
        self.assertEqual(data['measures'][0]['description'][:10], 'Total quan')
        self.assertEqual(data['measures'][0][
                         'why_it_matters'][:10], 'This is th')
        self.assertEqual(data['measures'][0]['is_cost_based'], True)
        self.assertEqual(data['measures'][0]['is_percentage'], True)
        self.assertEqual(data['measures'][0]['low_is_good'], True)
        self.assertEqual(len(data['measures'][0]['data']), 1)
        d = data['measures'][0]['data'][0]
        self.assertEqual(d['numerator'], 85500)
        self.assertEqual(d['denominator'], 181500)
        self.assertEqual("%.4f" % d['calc_value'], '0.4711')
        self.assertEqual("%.4f" % d['percentiles']['practice']['10'], '0.0419')
        self.assertEqual("%.4f" % d['percentiles']['practice']['50'], '0.1176')
        self.assertEqual("%.4f" % d['percentiles']['practice']['90'], '0.8200')
        self.assertEqual("%.4f" % d['percentiles']['ccg']['10'], '0.0793')
        self.assertEqual("%.4f" % d['percentiles']['ccg']['50'], '0.1176')
        self.assertEqual("%.4f" % d['percentiles']['ccg']['90'], '0.4823')
        self.assertEqual("%.2f" % d['cost_savings'][
                         'practice']['10'], '70149.77')
        self.assertEqual("%.2f" % d['cost_savings'][
                         'practice']['50'], '59029.41')
        self.assertEqual("%.2f" % d['cost_savings'][
                         'practice']['90'], '162.00')
        self.assertEqual("%.2f" % d['cost_savings']['ccg']['10'], '64174.56')
        self.assertEqual("%.2f" % d['cost_savings']['ccg']['50'], '58658.82')
        self.assertEqual("%.2f" % d['cost_savings']['ccg']['90'], '11731.76')

    def test_api_all_measures_global(self):
        url = '/api/1.0/measure/?format=json'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['measures'][0]['data']), 1)
        self.assertEqual(data['measures'][0]['low_is_good'], True)
        d = data['measures'][0]['data'][0]
        self.assertEqual(d['numerator'], 85500)
        self.assertEqual(d['denominator'], 181500)
        self.assertEqual("%.4f" % d['calc_value'], '0.4711')

    def test_api_all_measures_global_with_tags(self):
        url = '/api/1.0/measure/?format=json&tags=XXX'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['measures']), 0)

        url = '/api/1.0/measure/?format=json&tags=core'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['measures']), 1)

    def test_api_measure_by_all_ccgs(self):
        url = '/api/1.0/measure/?format=json'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['measures'][0]['data']), 1)
        self.assertEqual(data['measures'][0]['low_is_good'], True)
        d = data['measures'][0]['data'][0]
        self.assertEqual(d['numerator'], 85500)
        self.assertEqual(d['denominator'], 181500)
        self.assertEqual("%.4f" % d['calc_value'], '0.4711')

    def test_api_measure_numerators_by_ccg(self):
        testmeasure = {
            "is_cost_based": True,
            "numerator_columns": ["SUM(quantity) AS numerator, "],
            "numerator_from": "",
            "numerator_where": ["(bnf_code LIKE '0205%')"],
            "denominator_columns": ["SUM(quantity) AS denominator"],
            "denominator_from":"",
            "denominator_where": ["(bnf_code LIKE '02%')"]
        }

        with patch('api.views_measures._getMeasureData', return_value=testmeasure):
            url = '/api/1.0/measure_numerators_by_ccg/'
            url += '?measure=cerazette&org=02Q&format=json'
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertEqual(data, [
                {'total_items': 1,
                 'bnf_code': '0205010F0AAAAAA',
                 'presentation_name': None,
                 'numerator': 100.0,
                 'cost': 1.0,
                 'ccg': '02Q',
                 'quantity': 100.0}])


    def test_api_measure_by_ccg(self):
        url = '/api/1.0/measure_by_ccg/'
        url += '?org=02Q&measure=cerazette&format=json'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['measures'][0]['data']), 1)
        self.assertEqual(data['measures'][0]['low_is_good'], True)
        d = data['measures'][0]['data'][0]
        self.assertEqual(d['numerator'], 82000)
        self.assertEqual(d['denominator'], 143000)
        self.assertEqual(d['percentile'], 100)
        self.assertEqual("%.4f" % d['calc_value'], '0.5734')
        self.assertEqual("%.2f" % d['cost_savings']['10'], '63588.51')
        self.assertEqual("%.2f" % d['cost_savings']['50'], '58658.82')
        self.assertEqual("%.2f" % d['cost_savings']['90'], '11731.76')

    def test_api_measure_by_ccg_excludes_closed(self):
        url = '/api/1.0/measure_by_ccg/'
        url += '?org=02Q&measure=cerazette&format=json'
        pct = PCT.objects.get(pk='02Q')
        pct.close_date = datetime.date(2001, 1, 1)
        pct.save()
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['measures'])

    def test_api_all_measures_by_ccg(self):
        url = '/api/1.0/measure_by_ccg/'
        url += '?org=02Q&format=json'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['measures'][0]['data']), 1)
        self.assertEqual(data['measures'][0]['low_is_good'], True)
        d = data['measures'][0]['data'][0]
        self.assertEqual(d['numerator'], 82000)
        self.assertEqual(d['denominator'], 143000)
        self.assertEqual(d['percentile'], 100)
        self.assertEqual("%.4f" % d['calc_value'], '0.5734')

    def test_api_measure_by_practice(self):
        url = '/api/1.0/measure_by_practice/'
        url += '?org=C84001&measure=cerazette&format=json'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['measures'][0]['data']), 1)
        self.assertEqual(data['measures'][0]['low_is_good'], True)
        d = data['measures'][0]['data'][0]
        self.assertEqual(d['numerator'], 1000)
        self.assertEqual(d['denominator'], 11000)
        self.assertEqual("%.2f" % d['percentile'], '33.33')
        self.assertEqual("%.4f" % d['calc_value'], '0.0909')
        self.assertEqual("%.2f" % d['cost_savings']['10'], '485.58')
        self.assertEqual("%.2f" % d['cost_savings']['50'], '-264.71')
        self.assertEqual("%.2f" % d['cost_savings']['90'], '-7218.00')

        # Practice with only Cerazette prescribing.
        url = '/api/1.0/measure_by_practice/'
        url += '?org=A85017&measure=cerazette&format=json'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        d = data['measures'][0]['data'][0]
        self.assertEqual(d['numerator'], 1000)
        self.assertEqual(d['denominator'], 1000)
        self.assertEqual(d['percentile'], 100)
        self.assertEqual(d['calc_value'], 1)
        self.assertEqual("%.2f" % d['cost_savings']['10'], '862.33')

        # Practice with only Deso prescribing.
        url = '/api/1.0/measure_by_practice/'
        url += '?org=A86030&measure=cerazette&format=json'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['measures'][0]['data']), 1)
        d = data['measures'][0]['data'][0]
        self.assertEqual(d['numerator'], 0)
        self.assertEqual(d['denominator'], 1000)
        self.assertEqual(d['percentile'], 0)
        self.assertEqual(d['calc_value'], 0)
        self.assertEqual("%.2f" % d['cost_savings']['10'], '-37.67')

        # Practice with no prescribing of either.
        url = '/api/1.0/measure_by_practice/'
        url += '?org=B82010&measure=cerazette&format=json'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['measures'][0]['data']), 1)
        d = data['measures'][0]['data'][0]
        self.assertEqual(d['numerator'], 0)
        self.assertEqual(d['denominator'], 0)
        self.assertEqual(d['percentile'], None)
        self.assertEqual(d['calc_value'], None)
        self.assertEqual(d['cost_savings']['10'], 0.0)

    def test_api_all_measures_by_practice(self):
        url = '/api/1.0/measure_by_practice/'
        url += '?org=C84001&format=json'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['measures'][0]['data']), 1)
        self.assertEqual(data['measures'][0]['low_is_good'], True)
        d = data['measures'][0]['data'][0]
        self.assertEqual(d['numerator'], 1000)
        self.assertEqual(d['denominator'], 11000)
        self.assertEqual("%.2f" % d['percentile'], '33.33')
        self.assertEqual("%.4f" % d['calc_value'], '0.0909')

    def test_api_no_practice(self):
        url = '/api/1.0/measure_by_practice/'
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 400)
