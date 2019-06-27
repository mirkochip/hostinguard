import importlib
import logging
import os

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.hostinguard import service_handler
from api.v1.hostinguard.constants import APP1

settings = importlib.import_module(os.environ['DJANGO_SETTINGS_MODULE'])
logger = logging.getLogger(settings.LOGGER)


class HostinGuardView(APIView):

    def post(self, request):
        """
        Fetches last server measurements and update ElasticSearch accordingly.
        This EP should be triggered automatically through a scheduled job.
        """
        google_handler = service_handler.GoogleHandler(
            api_name=settings.GOOGLE_API[APP1]['API_NAME'],
            api_version=settings.GOOGLE_API[APP1]['API_VERSION'],
            scopes=settings.GOOGLE_API[APP1]['SCOPES'],
            key_file_location=settings.GOOGLE_API[APP1]['KEY_FILE_LOCATION']
        )
        google_data = google_handler.get_google_data()
        logger.debug('google_data: ' + str(google_data))

        cpanel_handler = service_handler.CPanelHandler(
            host=settings.CPANEL[APP1]['HOST'],
            username=settings.CPANEL[APP1]['USERNAME'],
            password=settings.CPANEL[APP1]['PASSWORD'],
            use_ssl=settings.CPANEL[APP1]['USE_SSL']
        )
        cpanel_data = cpanel_handler.get_cpanel_data()
        logger.debug('cpanel_data: ' + str(cpanel_data))

        static_resource_handler = service_handler.StaticResourceHandler(
            free_ep=settings.STATIC_RESOURCE[APP1]['FREE_EP'],
            logs_ep=settings.STATIC_RESOURCE[APP1]['LOGS_EP']
        )
        memory_data = static_resource_handler.get_memory_data()
        logger.debug('memory_data: ' + str(memory_data))
        logs_data = {'logs_data': static_resource_handler.get_logs_data()}
        logger.debug('logs_data: ' + str(logs_data))

        data = {
            **google_data,
            **cpanel_data,
            **memory_data,
            **logs_data
        }
        elastic_search_handler = service_handler.ElasticSearchHandler(
            es_service=settings.ES_SERVICE,
            index=settings.ES[APP1]['INDEX'],
            doc_type=settings.ES[APP1]['DOC_TYPE']
        )
        response = elastic_search_handler.write_result(data)
        logger.debug('es persistence: ' + response['result'])

        if response['result'] == 'created':
            return Response(status=status.HTTP_201_CREATED, data={'status': 'SUCCESS'})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'status': 'FAILURE'})
