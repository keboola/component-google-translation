# Google Translate

## Overview

The application for Google Translate allows to translate text into a desired language using Google Translate API. The Cloud Translation is a paid service serviced by Google and is subject to [Google Cloud's Terms & Condition](https://cloud.google.com/terms/). For pricing information, please visit the [support pages](https://cloud.google.com/translate/pricing).

## Requirements

The component requires valid Google Cloud API token with translation allowed. The API token is subject to [limits](https://cloud.google.com/translate/quotas) thus you will need to set up the translation limits according to your needs. The component uses exponential backoff to overcome Google's 100 second limit in case it is reached. In case the daily limit is reached, the component will fail.

## Input & Output

A sample configuration can be found in [component's repository](https://bitbucket.org/kds_consulting_team/kds-team.ex-google-translation/src/master/component_config/sample-config/) including table inputs and outputs. Output table is loaded incrementally with `id` column used as a primary key.

### Input table

Each of the table must contain 2 required columns and may contain 1 optional column to make the translation more precise. The list of columns is:

- `id` - (required) the column is used as primary key in the output,
- `text` - (required) text to be translated,
- `source` - (optional) an [ISO-639-1 language identifier](https://cloud.google.com/translate/docs/languages) of the source language of the text. If the column is left out or left blank, the Translate API will automatically detect the source language.

Any additional columns will be ignored by the component. The input table therefore might take a form like the one below.

| id 	| text                                     	| source 	| randomColumn 	    |
|----	|------------------------------------------	|--------	|--------------	    |
| 1 	| Tôi lái xe máy của tôi khi tôi ngã xuống 	|        	| foo          	    |
| 2  	| Je n'ai pas fait mon devoir              	| fr     	| bar          	    |
| 3  	| Hello, it's very nice to meet you.       	| en     	| foobar       	    |

### API Token (`#API_key`)

The API token can be obtained in the credentials section of the [Google Cloud Console](https://console.cloud.google.com/apis/credentials). The API token must have translation allowed, otherwise the component will fail.

### Target language (`target_language`)

An [ISO-639-1 language identifier](https://cloud.google.com/translate/docs/languages) of the language to which all text will be translated.

## Output

The output of the component is a table with translated rows. The table can be loaded as full or incremental load type, also you can define the PK. [More information about storing tables is here](https://help.keboola.com/storage/tables/#incremental-loading).  

The table contains the following columns:

- `id` - identificator of text request. Relates to input table and is used as PK,
- `translatedText` - a translation of the text in the target language,
- `detectedSourceLanguage` - if `source` is not specified, the column contains information on detected language in the text. Otherwise it is equal to `source`.

The output table will therefore take the following form:

| id 	| translatedText                        	| detectedSourceLanguage 	|
|----	|---------------------------------------	|------------------------	|
| 1  	| I drove my motorbike when I fell down 	| vi                     	|
| 2  	| I did not do my homework              	| fr                     	|
| 3  	| Hello, it's very nice to meet you.    	| en                     	|

## Development

For development purposes, the container needs to be built and image ran. Use following commands:

```
docker-compose build dev
docker-compose run --rm dev
```

or 

```
docker-compose up
```