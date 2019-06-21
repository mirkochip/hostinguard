from datetime import datetime

from django.urls import reverse
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase


class TestHealthView(APITestCase):

    def test_post_success(self):
        url = reverse('health')
        params = {}
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue(isinstance(response.data['date'], datetime))
