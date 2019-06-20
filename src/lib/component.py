import csv
import json
import logging
import os
import sys
from lib.client import googleTranslateClient
from kbc.env_handler import KBCEnvHandler
from kbc.result import KBCResult, KBCTableDef


API_KEY = '#API_key'
TARGET_LANGUAGE_KEY = 'target_language'

MANDATORY_PARS = [API_KEY, TARGET_LANGUAGE_KEY]
OUTPUT_FIELDS = ['id', 'translatedText', 'detectedSourceLanguage']
OUTPUT_PK = ['id']


class Component(KBCEnvHandler):

    def __init__(self):

        KBCEnvHandler.__init__(self, MANDATORY_PARS)
        self.validate_config(MANDATORY_PARS)

        self.token = self.cfg_params[API_KEY]
        self.target_language = self.cfg_params[TARGET_LANGUAGE_KEY]

        self.client = googleTranslateClient(self.token, self.target_language)
        self._check_input_tables()
        self._create_result_table()

    def _create_result_table(self):

        _out_path = os.path.join(self.tables_out_path, 'translated-text.csv')
        self.writer = csv.DictWriter(open(_out_path, 'w'), fieldnames=OUTPUT_FIELDS,
                                     restval='', extrasaction='ignore',
                                     quotechar='"', quoting=csv.QUOTE_ALL)

        self.writer.writeheader()

        _tbl_def = KBCTableDef('translated-text', OUTPUT_FIELDS, OUTPUT_PK)
        _result_def = KBCResult(full_path=_out_path,
                                file_name='translated-text.csv',
                                table_def=_tbl_def)

        self.out_result_def = _result_def

        self.create_manifests(results=[_result_def])

    def _check_input_tables(self):

        _input_tables = self.configuration.get_input_tables()

        logging.debug("Input tables:")
        logging.debug(_input_tables)

        if len(_input_tables) == 0:

            logging.error("No input table was provided. Please provide an input table, with mandatory columns \"id\"," +
                          " \"text\" and optional column \"source\". See documentation for more information.")

            sys.exit(1)

        for _t in _input_tables:

            _path = _t['full_path']
            _mnfst_path = _path + '.manifest'
            with open(_mnfst_path) as _mnfst_file:

                _mnfst = json.load(_mnfst_file)

                _columns = _mnfst['columns']

                if 'id' in _columns and 'text' in _columns:

                    pass

                else:

                    logging.error("Missing required column \"id\" or \"text\" in table %s." % _t['destination'])
                    logging.error("Please, make sure all of the required columns are inputted.")

                    sys.exit(1)

        self.input_tables = _input_tables

    def run(self):

        logging.info("Starting translation...")
        _requestCounter = 0

        for _table in self.input_tables:

            _path = _table['full_path']
            with open(_path) as _input:
                _reader = csv.DictReader(_input)

                for row in _reader:

                    _requestCounter += 1

                    _id = row['id']
                    _toTranslate = row['text']
                    _sourceLanguage = row.get('source')

                    _rsp = self.client.translate_text(text=_toTranslate,
                                                      source_language=_sourceLanguage)

                    if _rsp.ok is True:

                        _rsp_js = _rsp.json()['data']['translations'][0]

                        _translatedText = _rsp_js['translatedText']
                        _detectedSourceLanguage = _rsp_js.get('detectedSourceLanguage')

                        if _detectedSourceLanguage is None:

                            _detectedSourceLanguage = _sourceLanguage

                        _toWrite = {'id': _id,
                                    'translatedText': _translatedText,
                                    'detectedSourceLanguage': _detectedSourceLanguage}

                        self.writer.writerow(_toWrite)

                    else:

                        logging.warn("Could not translate text for id %s." % _id)

                    if _requestCounter % 500 == 0:

                        logging.info("Made %s requests to Google Translate API." % _requestCounter)
