# Google Translate Extractor

## Overview

The extractor for Google Translate allows to translate text into a desired language using Google Translate API. The Cloud Translation is a paid service serviced by Google and is subject to [Google Cloud's Terms & Condition](https://cloud.google.com/terms/). For pricing information, please visit the [support pages](https://cloud.google.com/translate/pricing).

## Requirements

The component requires valid Google Cloud API token with translation allowed. The API token is subject to [limits](https://cloud.google.com/translate/quotas) thus you will need to set up the translation limits according to your needs. The component uses exponential backoff to overcome Google's 100 second limit in case it is reached.