import logging

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)


class Client(object):

    def get_service(self, api_name, api_version, scopes, key_file_location):
        """
        Get a service that communicates to a Google API.

        Args:
            api_name: The name of the api to connect to.
            api_version: The api version to connect to.
            scopes: A list auth scopes to authorize for the application.
            key_file_location: The path to a valid service account JSON key file.

        Returns:
            A service that is connected to the specified API.
        """

        credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_location, scopes=scopes)

        # Build the service object.
        service = build(api_name, api_version, credentials=credentials)

        logger.info('service for Google API created.')
        return service

    @staticmethod
    def get_first_profile_id(service):
        """
        Use the Analytics service object to get the first profile id.
        """

        # Get a list of all Google Analytics accounts for this user
        accounts = service.management().accounts().list().execute()

        if accounts.get('items'):
            # Get the first Google Analytics account.
            account = accounts.get('items')[0].get('id')

            # Get a list of all the properties for the first account.
            properties = service.management().webproperties().list(
                accountId=account).execute()

            if properties.get('items'):
                # Get the first property id.
                property = properties.get('items')[0].get('id')

                # Get a list of all views (profiles) for the first property.
                profiles = service.management().profiles().list(
                    accountId=account,
                    webPropertyId=property).execute()

                if profiles.get('items'):
                    # return the first view (profile) id.
                    return profiles.get('items')[0].get('id')
