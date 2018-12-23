
# headbro

Headless browser rendering service for HTTP responses. Uses Google Chrome.

## Setup

First download [**chromedriver.exe**](https://sites.google.com/a/chromium.org/chromedriver/downloads) (>= v2.32) into the repo directory.

Then you'll also need to download the [**BrowserMob v2.1.4 binaries**](https://github.com/lightbody/browsermob-proxy/releases/download/browsermob-proxy-2.1.4/browsermob-proxy-2.1.4-bin.zip), altering the script's `BROWSERMOB_PROXY_PATH` var to point where you extract the folder inside.

BrowserMob relies on Java so ensure that's on the path such that you can run `java` from a prompt.

You'll find an SSL certificate you need to install within that BrowserMob zip. This is in order to view `https://` traffic. The filename to look for is `ca-certificate-rsa.cer`.

The main code is Python 3.x based, in case that's not clear. You need `python` and `pip` to be available from your prompt.

Now do the following from your prompt, ideally in a [**virtual environment**](https://docs.python.org/3/library/venv.html).

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

## Testing

There is some test webpage content in `test/`.

You can - in a different prompt than where you'll run headbro - make that the present working directory then run `python -m http.server`.

Finally, request that headbro render test pages by giving URLs like `http://127.0.0.1:8000/everything1.html`.

## Credit

This project takes inspiration from the original release of [**xssmap**](https://github.com/secdec/xssmap), which included a [**phantomjs**](https://en.wikipedia.org/wiki/PhantomJS) rendering engine. It was used there for security stuff (like the creation of this was for) but designed generally (also like this).

Credit also goes to Google Chrome's own [**rendertron**](https://github.com/GoogleChrome/rendertron) for some implementation ideas. This is not a direct copy, however... see issue [**#2**](https://github.com/gingeleski/headbro/issues/2) on that.
