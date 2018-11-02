
# headbro

Headless browser rendering service for HTTP responses. Uses Google Chrome.

## Setup

First download [**chromedriver.exe**](https://sites.google.com/a/chromium.org/chromedriver/downloads) (>= v2.32) into the repo directory.

Then you can do the following from your prompt... recommended to do so from a [**virtual environment**](https://docs.python.org/3/library/venv.html).

```
pip install -r requirements.txt
python headbro.py
```

At this point the service should be up on `localhost:9009` for you to hit with requests.

## API

*Note: this is abridged API doc for getting your feet wet.*

`POST /render`

- Input (JSON object)
    - `url`
        - required
        - string
    - `method`
        - optional
            - defaults to `get`
        - string
    - `script`
        - optional
        - string
    - `invoke_events`
        - optional
        - list of strings
- Output (JSON object)
    - `body`
    - `status_code`
    - `errors`
    - `messages`
    - `alerts`
    - `confirms`
    - `prompts`
    
Check out the [**full wiki page**](https://github.com/gingeleski/headbro/wiki/API-documentation) or [**OpenAPI spec**](https://github.com/gingeleski/headbro/blob/master/swagger.json)!!

## Credit

This project takes inspiration from the original release of [**xssmap**](https://github.com/secdec/xssmap), which included a [**phantomjs**](https://en.wikipedia.org/wiki/PhantomJS) rendering engine. It was used there for security stuff (like the creation of this was for) but designed generally (also like this).

Credit also goes to Google Chrome's own [**rendertron**](https://github.com/GoogleChrome/rendertron) for some implementation ideas. This is not a direct copy, however... see issue [**#2**](https://github.com/gingeleski/headbro/issues/2) on that.
