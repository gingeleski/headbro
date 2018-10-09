
# headbro

Headless browser rendering service for HTTP responses. Uses Google Chrome.

## Setup

First download [**chromedriver.exe**](https://sites.google.com/a/chromium.org/chromedriver/downloads) (>= v2.32) into the repo directory.

Then you can do the following from your prompt... and I recommend doing so from a [**virtual environment**](https://docs.python.org/3/library/venv.html).

```
pip install -r requirements.txt
python headbro.py
```

At this point the service should be up on `localhost:9009` for you to hit with requests.

## API

`POST /render`

- Input (JSON object)
    - `url`
        - required
        - string
    - `method`
        - optional
            - defaults to `get`
        - string
        - must be one of the following (case-insensitive)
            - `get`
            - `post` *unsupported right now*
            - `put` *unsupported right now*
            - `delete` *unsupported right now*
    - `invoke_events`
        - optional
            - defaults to `[]` (none)
        - list of strings
        - valid options are the following (case-insensitive)
            - `click` *unsupported right now*
            - `mouseover` *unsupported right now*
- Output (JSON object)
    - `body`
        - string
    - `status_code`
        - number/integer
    - `errors`
        - list of strings
        - error messages written to JS console
    - `messages`
        - list of strings
        - info messages written to JS console
    - `alerts`
        - list of strings
        - alert popups
    - `confirms`
        - list of strings
        - confirm popups
    - `prompts`
        - list of strings
        - prompt popups
       
`POST /configure`

*Planned, will allow service-wide configuration changes to the driver.*

`GET /cookies`

*Planned, will just return all the browser's cookies.*

`POST /cookies/clear`

*Planned, will delete cookies, can specify the scope.*

## Credit

This project takes inspiration from the original release of [**xssmap**](https://github.com/secdec/xssmap), which included a [**phantomjs**](https://en.wikipedia.org/wiki/PhantomJS) rendering engine. It was used there for security stuff (like the creation of this was for) but designed generally (also like this).

Credit also goes to Google Chrome's own [**rendertron**](https://github.com/GoogleChrome/rendertron) for some implementation ideas. This is not a direct copy, however... see issue [**#2**](https://github.com/gingeleski/headbro/issues/2) on that.
