import time
from unittest import TestCase

import requests
from elasticsearch import Elasticsearch
from flexmock import flexmock

from api.v1.hostinguard import service_handler
from services.cpanelapi.client import Client as CPanelClient
from services.googleapi.client import Client as GoogleClient


class TestGoogleHandler(TestCase):

    def test_get_google_data(self):
        mock_google_response_1 = {
            'totalsForAllResults': {
                'rt:activeUsers': '1',
            }
        }
        mock_google_response_2 = {
            'totalsForAllResults': {
                'ga:sessions': '2',
                'ga:users': '3',
                'ga:newUsers': '4'
            }
        }
        stubbed_execute_1 = flexmock().should_receive('execute').and_return(mock_google_response_1).mock()
        stubbed_get_1 = flexmock().should_receive('get').and_return(stubbed_execute_1).once().mock()
        stubbed_realtime_1 = flexmock().should_receive('realtime').and_return(stubbed_get_1).once().mock()
        stubbed_execute_2 = flexmock().should_receive('execute').and_return(mock_google_response_2).mock()
        stubbed_get_2 = flexmock().should_receive('get').and_return(stubbed_execute_2).once().mock()
        stubbed_realtime_2 = flexmock().should_receive('ga').and_return(stubbed_get_2).once().mock()

        stubbed_google_service = flexmock().should_receive('data').and_return(
            stubbed_realtime_1).and_return(stubbed_realtime_2).twice().mock()
        stubbed_google_client = flexmock(GoogleClient)
        stubbed_google_client.should_receive('get_service').and_return(stubbed_google_service).once()
        stubbed_google_client.should_receive('get_first_profile_id').and_return('profile_id').once()

        google_handler = service_handler.GoogleHandler(
            api_name='fake_api_name',
            api_version='fake_api_version',
            scopes='fake_scopes',
            key_file_location='fake_key_file_location'
        )
        google_data = google_handler.get_google_data()

        self.assertEqual(google_data['active_users'], 1)
        self.assertEqual(google_data['users_cnt'], 2)
        self.assertEqual(google_data['unique_users_cnt'], 3)
        self.assertEqual(google_data['new_users_cnt'], 4)


class TestCPanelHandler(TestCase):

    def test_get_cpanel_data(self):
        stubbed_response = {
            'one': 0.1,
            'five': 0.5,
            'fifteen': 0.15
        }
        flexmock(CPanelClient).new_instances(flexmock().should_receive('call').and_return(stubbed_response).mock())
        cpanel_handler = service_handler.CPanelHandler(
            host='fake_host',
            username='fake_username',
            password='fake_password',
            use_ssl='fake_use_ssl'
        )
        cpanel_data = cpanel_handler.get_cpanel_data()

        self.assertEqual(cpanel_data['cpu_1'], 0.1)
        self.assertEqual(cpanel_data['cpu_5'], 0.5)
        self.assertEqual(cpanel_data['cpu_15'], 0.15)


class TestStaticResourceHandler(TestCase):

    def test_get_data_with_retry_ok(self):
        url = 'fake_url'
        flexmock(requests).should_receive('get').and_return(flexmock(text='this_is_fake_data', status_code=200))
        flexmock(time).should_receive('sleep')
        static_resource_handler = service_handler.StaticResourceHandler(
            free_ep='fake_free_ep',
            logs_ep='fake_logs_ep'
        )
        data = static_resource_handler.get_data_with_retry(url)
        self.assertEqual(data.text, 'this_is_fake_data')

    def test_get_data_with_retry_missing_data(self):
        url = 'fake_url'
        flexmock(requests).should_receive('get').and_return(flexmock(text='', status_code=200))
        flexmock(time).should_receive('sleep')
        static_resource_handler = service_handler.StaticResourceHandler(
            free_ep='fake_free_ep',
            logs_ep='fake_logs_ep'
        )
        data = static_resource_handler.get_data_with_retry(url)
        self.assertIsNone(data)

    def test_get_data_with_retry_bad_request(self):
        url = 'fake_url'
        flexmock(requests).should_receive('get').and_return(flexmock(text='this_is_fake_data', status_code=400))
        flexmock(time).should_receive('sleep')
        static_resource_handler = service_handler.StaticResourceHandler(
            free_ep='fake_free_ep',
            logs_ep='fake_logs_ep'
        )
        data = static_resource_handler.get_data_with_retry(url)
        self.assertIsNone(data)

    def test_get_memory_data(self):
        stubbed_free = '              total        used        free      shared  buff/cache   available\n' \
                       'Mem:          31753        2772       14548          74       14432       28411\n' \
                       'Swap:         20475           0       20475'

        flexmock(service_handler.StaticResourceHandler).should_receive(
            'get_data_with_retry').and_return(flexmock(text=stubbed_free))
        static_resource_handler = service_handler.StaticResourceHandler(
            free_ep='fake_free_ep',
            logs_ep='fake_logs_ep'
        )
        memory_data = static_resource_handler.get_memory_data()

        self.assertEqual(memory_data['total_mem'], 31753)
        self.assertEqual(memory_data['used_mem'], 2772)
        self.assertEqual(memory_data['free_mem'], 14548)
        self.assertEqual(memory_data['shared'], 74)
        self.assertEqual(memory_data['buffers_cache'], 14432)
        self.assertEqual(memory_data['available'], 28411)
        self.assertEqual(memory_data['total_swap'], 20475)
        self.assertEqual(memory_data['used_swap'], 0)
        self.assertEqual(memory_data['free_swap'], 20475)

    def test_get_logs_data_ok(self):
        stubbed_logs = ' 663620 200 \n' \
                       '  11882 304 \n' \
                       '   7138 301 \n' \
                       '   2906 499 \n' \
                       '    876 206 \n' \
                       '    795 404 \n' \
                       '    786 302 \n' \
                       '     27 444 \n' \
                       '     10 408 \n' \
                       '      2 405 \n' \
                       '      2 400 \n' \
                       '      1 416'
        flexmock(service_handler.StaticResourceHandler).should_receive(
            'get_data_with_retry').and_return(flexmock(text=stubbed_logs))
        static_resource_handler = service_handler.StaticResourceHandler(
            free_ep='fake_free_ep',
            logs_ep='fake_logs_ep'
        )
        logs_data = static_resource_handler.get_logs_data()

        self.assertEqual(logs_data[200], 663620)
        self.assertEqual(logs_data[404], 795)
        self.assertEqual(logs_data[400], 2)

    def test_get_logs_missing_data(self):
        stubbed_logs = None
        flexmock(service_handler.StaticResourceHandler).should_receive('get_data_with_retry').and_return(stubbed_logs)
        static_resource_handler = service_handler.StaticResourceHandler(
            free_ep='fake_free_ep',
            logs_ep='fake_logs_ep'
        )
        logs_data = static_resource_handler.get_logs_data()
        self.assertEqual(logs_data[999], 1)


class TestElasticSearchHandler(TestCase):

    def test_write_result(self):
        mock_data = {
            'fake_field_1': 1,
            'fake_field:2': 2,
            'fake_field_n': 100
        }
        flexmock(Elasticsearch).new_instances(flexmock().should_receive('index').and_return({'created': True}).mock())
        elastic_search_handler = service_handler.ElasticSearchHandler(
            es_service='fake_es_service',
            index='fake_index',
            doc_type='fake_doc_type'
        )
        result = elastic_search_handler.write_result(mock_data)
        self.assertTrue(result['created'])
