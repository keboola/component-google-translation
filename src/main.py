import os
import requests
import json
import pandas as pd
from googleapiclient.errors import HttpError


DEFAULT_TABLE_SOURCE = "/data/in/tables/"
DEFAULT_TABLE_DESTINATION = "/data/out/tables/"

base_url = "https://translation.googleapis.com/language/translate/v2"


def output(filename, data):

    dest = DEFAULT_TABLE_DESTINATION + filename + ".csv"

    if os.path.isfile(dest):
        with open(dest, 'a') as b:
            data.to_csv(b, index=False, header=False)
        b.close()
    else:
        with open(dest, 'w+') as b:
            data.to_csv(b, index=False, header=True)
        b.close()


def translate(original_id, text, api_key, target_language='en'):
    params = {
        'target': target_language,
        'q': text,
        'key': api_key
    }

    r = requests.post(base_url, params=params)

    json_obj = json.loads(r.text)
    json_obj = json_obj.get('data').get('translations')[0]
    translated_text = json_obj.get('translatedText')
    detected_source_language = json_obj.get('detectedSourceLanguage')

    return {
        "original_id": original_id,
        "original_text": text,
        "translated_text": translated_text,
        "detected_source_language": detected_source_language
    }


def main(input_table_path, target_language, api_key):

    df = pd.read_csv(input_table_path)

    cols = df.columns.values
    msg = """Please prepare all your input tables with the 2 columns below:
    - id: the original ID column in your raw table, this is only for you to have a reference key
    - text: the column of texts you want to analyze Other columns in the tables will be omitted."""
    if not ('id' in cols) or not ('text' in cols):
        raise ValueError(msg)

    df = df[['id', 'text']]

    result_records = []

    for _, row in df.iterrows():
        original_id = row.get('id')
        text = row.get('text')

        try:
            result_record = translate(original_id, text, api_key=api_key, target_language=target_language)
            result_records.append(result_record)
        except HttpError as e:
            if json.loads(e.content).get('error', '').get('reason', '').find('keyInvalid') > 0:
                raise ValueError("The API Key is invalid")

    df_result = pd.DataFrame.from_records(result_records)

    output_table_name = input_table_path.split('/')[-1]
    # strip the csv file extension
    output_table_name = output_table_name[:-4]
    output(output_table_name + '_translated', df_result)
