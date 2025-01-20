import csv
import logging
from typing import Dict

from keboola.component.base import ComponentBase
from keboola.component.dao import TableDefinition
from keboola.component.exceptions import UserException

from client import GoogleTranslateClient, GoogleTranslateClientException

API_KEY = '#API_key'
TARGET_LANGUAGE_KEY = 'target_language'

MANDATORY_PARS = [API_KEY, TARGET_LANGUAGE_KEY]
OUTPUT_FIELDS = ['id', 'translatedText', 'detectedSourceLanguage']
DEFAULT_OUTPUT_PK = ['id', 'translatedText', 'detectedSourceLanguage']
DEFAULT_OUTPUT_TABLE_NAME = "translated-text.csv"

FAILED_OUTPUT_FIELDS = ['id', 'failed_text', "reason"]
FAILED_OUTPUT_PK = ['id']


class Component(ComponentBase):

    def __init__(self):
        super().__init__()
        self.client = None

    def run(self):
        self.validate_configuration_parameters(MANDATORY_PARS)
        self.validate_input_table()
        self._init_client()

        input_table = self.get_input_table()
        self._create_result_table()

        logging.info("Starting translation...")

        self.translate_file(input_table)

        logging.info("Translation finished")

        self.close_result()

    def _init_client(self) -> None:
        params = self.configuration.parameters
        try:
            self.client = GoogleTranslateClient(params.get(API_KEY), params.get(TARGET_LANGUAGE_KEY))
        except GoogleTranslateClientException as google_exc:
            raise UserException(google_exc) from google_exc

    def translate_file(self, input_table: TableDefinition) -> None:
        _requestCounter = 0
        with open(input_table.full_path) as _input:
            reader = csv.DictReader(_input)
            for row in reader:
                _requestCounter += 1
                if _requestCounter % 500 == 0:
                    logging.info(f"Made {_requestCounter} requests to Google Translate API.")
                self.translate_row(row)

    def translate_row(self, row: Dict) -> None:
        row_id = row['id']
        to_translate = row['text']
        source_language = row.get('source')
        if source_language is not None:
            source_language = source_language.lower()
        try:
            _rsp_js = self.client.translate_text(text=to_translate, source_language=source_language)
            parsed_response = self.parse_translate_response(_rsp_js, source_language, row_id)
            self.writer.writerow(parsed_response)
        except GoogleTranslateClientException as google_exc:
            logging.warning(f"Could not translate text for id {row_id}. \n{google_exc}")
            self.fail_writer.writerow({'id': row_id, 'failed_text': to_translate, "reason": google_exc})

    @staticmethod
    def parse_translate_response(_rsp_js: Dict, source_language: str, row_id: str) -> Dict:
        _translatedText = _rsp_js['translatedText']
        _detectedSourceLanguage = _rsp_js.get('detectedSourceLanguage')
        if _detectedSourceLanguage is None:
            _detectedSourceLanguage = source_language
        return {'id': row_id, 'translatedText': _translatedText, 'detectedSourceLanguage': _detectedSourceLanguage}

    def _create_result_table(self) -> None:
        params = self.configuration.parameters
        if 'destination' in params:
            destination = params['destination']
            incremental = (True if destination.get('load_type') == 'incremental_load' else False)
            self.table_definition = self.create_out_table_definition(destination.get('output_table_name'),
                                                                     incremental=incremental,
                                                                     columns=OUTPUT_FIELDS,
                                                                     primary_key=destination.get('output_table_name'))
        else:
            # backward compatibility for older configurations
            self.table_definition = self.create_out_table_definition(DEFAULT_OUTPUT_TABLE_NAME,
                                                                     columns=OUTPUT_FIELDS,
                                                                     primary_key=DEFAULT_OUTPUT_PK)

        self.out_file = open(self.table_definition.full_path, 'w')
        self.writer = csv.DictWriter(self.out_file, fieldnames=OUTPUT_FIELDS,
                                     restval='', extrasaction='ignore',
                                     quotechar='"', quoting=csv.QUOTE_ALL)

        self.failed_table_definition = self.create_out_table_definition("failed_translations.csv",
                                                                        columns=FAILED_OUTPUT_FIELDS,
                                                                        primary_key=FAILED_OUTPUT_PK)

        self.failed_out_file = open(self.failed_table_definition.full_path, 'w')
        self.fail_writer = csv.DictWriter(self.failed_out_file, fieldnames=FAILED_OUTPUT_FIELDS,
                                          restval='', extrasaction='ignore',
                                          quotechar='"', quoting=csv.QUOTE_ALL)

    def close_result(self) -> None:
        self.out_file.close()
        self.write_manifest(self.table_definition)

        self.failed_out_file.close()
        self.write_manifest(self.failed_table_definition)

    def validate_input_table(self) -> None:
        input_tables = self.get_input_tables_definitions()

        if len(input_tables) == 0:
            raise UserException(
                "No input table was provided. Please provide an input table, with mandatory columns \"id\"," +
                " \"text\" and optional column \"source\". See documentation for more information.")

        input_table = input_tables[0]

        if 'id' not in input_table.columns or 'text' not in input_table.columns:
            raise UserException(
                f"Missing required column \"id\" or \"text\" in table {input_table.name}. "
                f"Please, make sure all of the required columns are inputted.")

    def get_input_table(self) -> TableDefinition:
        return self.get_input_tables_definitions()[0]


if __name__ == "__main__":
    try:
        comp = Component()
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
