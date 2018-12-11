import os
import requests
import json
import pandas as pd


DEFAULT_TABLE_SOURCE = "data/in/tables/"
DEFAULT_TABLE_DESTINATION = "data/out/tables/"

base_url = "https://translation.googleapis.com/language/translate/v2"


def output(filename, data):

    dest = filename + ".csv"

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
    print(json_obj)
    json_obj = json_obj.get('data').get('translations')[0]
    translated_text = json_obj.get('translatedText')
    detected_source_language = json_obj.get('detectedSourceLanguage')

    return {
        "original_id": original_id,
        "translated_text": translated_text,
        "detected_source_language": detected_source_language
    }


def main(input_table_name, target_language, api_key):

    df = pd.read_csv(input_table_name)
    df = df[['id', 'text']]

    result_records = []

    for _, row in df.iterrows():
        original_id = row.get('id')
        text = row.get('text')

        result_record = translate(original_id, text, api_key=api_key, target_language=target_language)
        result_records.append(result_record)

    df_result = pd.DataFrame.from_records(result_records)
    output(input_table_name.replace('.csv', '') + '_translated', df_result)
