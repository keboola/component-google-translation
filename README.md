# Google Translate Extractor

## Overview

The extractor for Google Translate allows to translate text into a desired language using Google Translate API. The Cloud Translation is a paid service serviced by Google and is subject to [Google Cloud's Terms & Condition](https://cloud.google.com/terms/). For pricing information, please visit the [support pages](https://cloud.google.com/translate/pricing).

## Requirements

The component requires valid Google Cloud API token with translation allowed. The API token is subject to [limits](https://cloud.google.com/translate/quotas) thus you will need to set up the translation limits according to your needs. The component uses exponential backoff to overcome Google's 100 second limit in case it is reached.

## Input

The component takes as an input one or more tables and 2 user specified parameters. A sample configuration can be found in [component's repository](https://bitbucket.org/kds_consulting_team/kds-team.ex-google-translation/src/master/component_config/sample-config/).

### Input table(s)

Each of the table must contain 2 required columns and may contain 1 optional column to make the translation more precise. The list of columns is:

- `id` - (required) the column is used as primary key in the output,
- `text` - (required) text to be translated
- `source` - (optional) an [ISO-639-1 language identifier](https://cloud.google.com/translate/docs/languages) of the source language of the text. If the column is left out or left blank, the Translate API will automatically detect the source language.

### API Token

The API token can be obtained in the credentials section of the [Google Cloud Console](https://console.cloud.google.com/apis/credentials). The API token must have translation allowed, otherwise the component will fail.

### Target language

An [ISO-639-1 language identifier](https://cloud.google.com/translate/docs/languages) of the language to which all text will be translated.

## Output

The output of the extractor is a table with translated columns. The table is loaded incrementally with column `id` used as a primary key and with following column specification:

- `id` - identificator of text. Relates to original request.
- `translatedText` - a translation of the text in the target language
- `detectedSourceLanguage` - if `source` is not specified, the column contains information on detected language in the text. Otherwise is equal to `source`.

## Development

For development purposes, the container needs to be built and image ran. Use following commands:

```
docker-compose build dev
docker-compose run --rm dev
```