import importlib
import logging
import os
from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

settings = importlib.import_module(os.environ['DJANGO_SETTINGS_MODULE'])
logger = logging.getLogger(settings.LOGGER)


class HealthView(APIView):

    def get(self, request):
        response = {'date': datetime.now()}
        logger.info('health response: ' + str(response['date']))
        return Response(
            status=status.HTTP_200_OK,
            data=response
        )
