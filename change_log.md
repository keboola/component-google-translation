**0.3.5**
Added sample table examples.
Changed component descriptions.

**0.3.4**
Corrected logging level. Changed support from multiple tables to only a single table. Multiple tables support might be re-added in the future.

**0.3.3**
Language sanitization added. Previously, when language wasn't specified in lowercase, it'd not be properly identified.

**0.3.2**
Changed post_raw method from `requests.post` to `HttpClientBase.post_raw`

**0.3.1**
Added fix for empty input mapping. When the input is not specified, an error will be raised.

**0.3.0**
Changed the component source code to use the newest KBCEnvHandler library. Added retry for failed requests and exponential backoff for requests over the limit.