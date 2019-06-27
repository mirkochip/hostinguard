from django.test import TestCase
from flexmock import flexmock
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from api.v1.hostinguard import service_handler


class HostinGuardView(TestCase):

    def test_post_success(self):
        flexmock(service_handler.GoogleHandler).should_receive('get_google_data').and_return({'a': 1}).once()
        flexmock(service_handler.CPanelHandler).should_receive('get_cpanel_data').and_return({'b': 2}).once()
        flexmock(service_handler.StaticResourceHandler).should_receive('get_memory_data').and_return({'c': 3}).once()
        flexmock(service_handler.StaticResourceHandler).should_receive('get_logs_data').and_return({'d': 4}).once()
        flexmock(service_handler.ElasticSearchHandler).should_receive(
            'write_result').and_return({'result': 'created'}).once()
        url = reverse('app1-hostinguard-update')
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'SUCCESS')

    def test_post_failure(self):
        flexmock(service_handler.GoogleHandler).should_receive('get_google_data').and_return({'a': 1}).once()
        flexmock(service_handler.CPanelHandler).should_receive('get_cpanel_data').and_return({'b': 2}).once()
        flexmock(service_handler.StaticResourceHandler).should_receive('get_memory_data').and_return({'c': 3}).once()
        flexmock(service_handler.StaticResourceHandler).should_receive('get_logs_data').and_return({'d': 4}).once()
        flexmock(service_handler.ElasticSearchHandler).should_receive(
            'write_result').and_return({'result': 'huston_we_have_a_problem'}).once()
        url = reverse('app1-hostinguard-update')
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'FAILURE')
