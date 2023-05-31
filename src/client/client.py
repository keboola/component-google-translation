import json
import logging
from json import JSONDecodeError
from typing import Dict

import requests
from keboola.http_client import HttpClient
from requests.exceptions import HTTPError

BASE_URL = 'https://translation.googleapis.com/language/translate/v2'

ENDPOINT_LANGUAGES = "languages"


class GoogleTranslateClientException(Exception):
    pass


class GoogleTranslateClient(HttpClient):

    def __init__(self, token: str, target_language: str):
        parameters = {'key': token, 'target': target_language, 'format': 'text'}
        self.token = token
        self.target_language = target_language

        super().__init__(base_url=BASE_URL,
                         default_params=parameters,
                         status_forcelist=(403, 500, 502),
                         max_retries=10,
                         backoff_factor=0.3)

        self._test_connection()
        self._init_supported_languages()

    def _test_connection(self) -> None:
        try:
            self.get(endpoint_path=ENDPOINT_LANGUAGES, params={'key': self.token})
        except HTTPError as http_error:
            raise GoogleTranslateClientException("API token verification failed. "
                                                 "Make sure your API token is valid.") from http_error
        logging.info("API token verified. Login successful.")

    def _init_supported_languages(self) -> None:
        try:
            _rsp = self.get(endpoint_path=ENDPOINT_LANGUAGES, params={'key': self.token})
        except HTTPError as http_error:
            raise GoogleTranslateClientException(http_error) from http_error

        self.supported_languages = [x['language'].lower() for x in _rsp['data']['languages']]

        logging.debug("Supported languages are:")
        logging.debug(self.supported_languages)

    def translate_text(self, text: str, source_language: str = '') -> Dict:

        if source_language != '' and source_language not in self.supported_languages:
            source_language = ''
        elif source_language == self.target_language:
            source_language = ''

        params = {'q': text, 'source': source_language}

        logging.debug("Request parameters:")
        logging.debug(params)

        raw_result = self._translate_text(params)
        translation_data = self.process_result(raw_result)
        return translation_data

    def _translate_text(self, params: Dict) -> requests.Response:
        try:
            return self.post_raw(data=params)
        except requests.exceptions.RetryError as e:
            raise GoogleTranslateClientException(
                f"There were some issues with translating the text. Retry 10x failed. Reason: {e}. "
                f"Possible issue might be related to daily limits reached. "
                f"Try raising daily limit value in Google Cloud Console settings.") from e

    def process_result(self, raw_result: requests.Response) -> Dict:
        if raw_result.ok is True:
            return raw_result.json()['data']['translations'][0]
        else:
            error_message = self.process_error_message(raw_result.text)
            raise GoogleTranslateClientException(f"Failed to translate text : {error_message}")

    @staticmethod
    def process_error_message(error: str) -> str:
        try:
            error_data = json.loads(error)
            return error_data.get("error").get("message")
        except (JSONDecodeError, KeyError):
            return error
