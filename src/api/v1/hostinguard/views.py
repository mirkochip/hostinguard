import importlib
import logging
import os

from rest_framework.views import APIView

settings = importlib.import_module(os.environ['DJANGO_SETTINGS_MODULE'])
logger = logging.getLogger(settings.LOGGER)


class HostinGuardView(APIView):

    def post(self, request):
        """
        Fetches last server measurements and update ElasticSearch accordingly.
        This EP should be triggered automatically through a scheduled job.
        """
        pass
