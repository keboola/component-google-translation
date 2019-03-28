import json
import requests

base_url = "https://translation.googleapis.com/language/translate/v2"

def translate(original_id, text, api_key, target_language='en'):
    params = {
        'target': target_language,
        'q': text,
        'key': api_key
    }

    r = requests.post(base_url, params=params)
    # print(json.loads(r.content))
    # print(json.loads(r))
    if json.loads(r.content).get("error"):
        raise ValueError(json.loads(r.content).get("error").get("message"))

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


translate("1", "hello", "1234")
# translate("1", "hello", "AIzaSyAkzMRVbmggvF1_l5_Z1fn2CVFivT8KwUI")

# {'data': {'translations': [{'translatedText': 'hello', 'detectedSourceLanguage': 'en'}]}}