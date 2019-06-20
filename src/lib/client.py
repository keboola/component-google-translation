import logging
import requests
import sys
from kbc.client_base import HttpClientBase

BASE_URL = 'https://translation.googleapis.com/language/translate/v2'


class googleTranslateClient(HttpClientBase):

    def __init__(self, token, target_language):

        _def_params = {'key': token,
                       'target': target_language,
                       'format': 'text'}

        self.token = token
        self.target_language = target_language

        HttpClientBase.__init__(self, base_url=BASE_URL, default_params=_def_params,
                                status_forcelist=(403, 500, 502), max_retries=10, backoff_factor=0.3)

        self._check_api_token()

        # self.post_raw = requests.post

    def _check_api_token(self):

        _url = 'https://translation.googleapis.com/language/translate/v2/languages'
        _req_params = {'key': self.token}
        _rsp = requests.get(_url, params=_req_params)

        if _rsp.status_code == 200:

            logging.info("API token verified. Login successful.")

            self.supported_languages = [x['language'] for x in _rsp.json()['data']['languages']]

            logging.debug("Supported languages are:")
            logging.debug(self.supported_languages)

        else:

            _msg = _rsp.json().get('error').get('message')
            logging.error("API token verification failed. Request returned status code %s: %s" % (
                _rsp.status_code, _msg))
            sys.exit(1)

    def translate_text(self, text, source_language=''):

        if source_language != '' and source_language not in self.supported_languages:

            source_language = ''

        elif source_language == self.target_language:

            source_language = ''

        logging.debug("Source language set to %s." % source_language)

        _req_params = {'q': text, 'source': source_language}

        # _req_params = {**self._default_params, **_req_params}

        logging.debug("Request parameters:")
        logging.debug(_req_params)

        try:
            _rsp = self.post_raw(url=self.base_url, params=_req_params)

            return _rsp

        except requests.exceptions.RetryError as e:

            logging.error(
                "There were some issues with translating the text. Retry 10x failed. Reason:")
            logging.error(e)
            logging.error("Possible issue might be related to daily limits reached. Try raising daily limit value in" +
                          " Google Cloud Console settings.")
            sys.exit(2)
