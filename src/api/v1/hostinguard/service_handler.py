import importlib
import logging
import os
import re
import time
from typing import Optional

import requests
from django.utils.timezone import now
from elasticsearch import Elasticsearch
from rest_framework import status

from api.v1.hostinguard import constants
from services.cpanelapi import client as cpanel_client
from services.googleapi import client as google_client

settings = importlib.import_module(os.environ['DJANGO_SETTINGS_MODULE'])
logger = logging.getLogger(settings.LOGGER)


class GoogleHandler(object):

    def __init__(self, api_name, api_version, scopes, key_file_location):
        self.api_name = api_name
        self.api_version = api_version
        self.scopes = scopes
        self.key_file_location = key_file_location

    def get_google_data(self) -> dict:
        client = google_client.Client()
        service = client.get_service(
            api_name=self.api_name,
            api_version=self.api_version,
            scopes=self.scopes,
            key_file_location=self.key_file_location
        )
        profile = client.get_first_profile_id(service)

        result = service.data().realtime().get(
            ids='ga:' + profile,
            metrics=constants.REAL_TIME_USERS
        ).execute()
        active_users = int(result['totalsForAllResults'][constants.REAL_TIME_USERS])
        result = service.data().ga().get(
            ids='ga:' + profile,
            start_date='today',
            end_date='today',
            metrics='ga:sessions,ga:users,ga:newUsers').execute()
        users_cnt = int(result['totalsForAllResults'][constants.SESSIONS])
        unique_users_cnt = int(result['totalsForAllResults'][constants.UNIQUE_USERS])
        new_users_cnt = int(result['totalsForAllResults'][constants.NEW_USERS])

        google_data = {
            'active_users': active_users,
            'users_cnt': users_cnt,
            'unique_users_cnt': unique_users_cnt,
            'new_users_cnt': new_users_cnt
        }
        return google_data


class CPanelHandler(object):

    def __init__(self, host, username, password, use_ssl):
        self.host = host
        self.username = username
        self.password = password
        self.use_ssl = use_ssl

    def get_cpanel_data(self) -> dict:
        cpanel_data = {}
        whm = cpanel_client.Client(
            username=self.username,
            host=self.host,
            password=self.password,
            ssl=self.use_ssl
        )
        loadavg = whm.call('loadavg')
        cpanel_data['cpu_1'] = float(loadavg['one'])
        cpanel_data['cpu_5'] = float(loadavg['five'])
        cpanel_data['cpu_15'] = float(loadavg['fifteen'])
        return cpanel_data


class StaticResourceHandler(object):
    """
    Fetches and returns measurements not retrievable through APIs
    """
    MAX_RETRIES = 5
    MUL_FACTOR = 2
    TIMEOUT = 5

    def __init__(self, free_ep, logs_ep):
        self.free_ep = free_ep
        self.logs_ep = logs_ep

    # to be probably moved in a helper/utility class
    def get_data_with_retry(self, url: str) -> Optional['Response']:
        sleep_offset = 1
        for i in range(0, self.MAX_RETRIES):
            response = requests.get(url, timeout=self.TIMEOUT)
            logger.debug('get_data_with_retry(), status code: ' + str(response.status_code))
            logger.debug('text: ' + response.text)
            if response.status_code == status.HTTP_200_OK and response.text:
                return response
            time.sleep(sleep_offset)
            sleep_offset *= self.MUL_FACTOR

    def get_memory_data(self) -> dict:
        """
        Process the output of the "free -m" command, refreshed every 1m
        (nice to read: https://www.linuxatemyram.com)
        -------------------------------------------------------------------------------
                      total        used        free      shared  buff/cache   available
        Mem:          31753        2772       14548          74       14432       28411
        Swap:         20475           0       20475
        """
        data = {}
        # getting RAM usage
        free = self.get_data_with_retry(self.free_ep)
        mem = free.text.split('\n')[1]
        mem_values = re.split(r'\s+', mem)

        data['total_mem'] = int(mem_values[1])
        data['used_mem'] = int(mem_values[2])
        data['free_mem'] = int(mem_values[3])
        data['shared'] = int(mem_values[4])
        data['buffers_cache'] = int(mem_values[5])
        data['available'] = int(mem_values[6])

        # getting SWAP usage
        swap = free.text.split('\n')[2]
        swap_values = re.split(r'\s+', swap)
        data['total_swap'] = int(swap_values[1])
        data['used_swap'] = int(swap_values[2])
        data['free_swap'] = int(swap_values[3])

        return data

    def get_logs_data(self) -> dict:
        """
        Process the output of the following command:
        --------------------------------------------
        cat apache_access_log.log | grep "$(date +"%d/%b")" | cut -d ' ' -f 9 | sort | uniq -c | sort -nr
        ----------
        541432 200
        9736 304
        6217 301
        2218 499
        777 302
        683 404
        657 206
         27 444
          9 408
          2 405
          2 400
          1 416

        Refreshed every 1m
        """
        # retrieving logs using retry strategy because data
        # might not always be ready at server side
        logs = self.get_data_with_retry(self.logs_ep)
        if logs:
            requests_codes = logs.text.split('\n')
            data = {
                int(requests_code.strip().split()[1]): int(requests_code.strip().split()[0])
                for requests_code in requests_codes
                if requests_code != ''
            }
        else:
            # custom error code notified by backend.
            data = {999: 1}
        return data


class ElasticSearchHandler(object):

    def __init__(self, es_service, index, doc_type):
        self.es_service = es_service
        self.index = index
        self.doc_type = doc_type

    def write_result(self, data: dict) -> dict:
        es = Elasticsearch([self.es_service, ])
        data['timestamp'] = now()
        result = es.index(
            index=self.index,
            doc_type=self.doc_type,
            body=data
        )
        return result
