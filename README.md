
# headbro

Headless browser rendering service for HTTP responses. Uses Google Chrome.

## Setup

First download [**chromedriver.exe**](https://sites.google.com/a/chromium.org/chromedriver/downloads) (>= v2.32) into the repo directory.

Then you can do the following from your prompt... and I recommend doing so from a [**virtual environment**](https://docs.python.org/3/library/venv.html).

```
pip install -r requirements.txt
python hbprs.py
```

## Credit

This project takes inspiration from the original release of [**xssmap**](https://github.com/secdec/xssmap), which included a [**phantomjs**](https://en.wikipedia.org/wiki/PhantomJS) rendering engine. It was used there for security stuff (like the creation of this was for) but designed generally (also like this).

Credit also goes to Google Chrome's own [**rendertron**](https://github.com/GoogleChrome/rendertron) for some implementation ideas. This is not a direct copy, however... see issue [**#2**](https://github.com/gingeleski/headbro/issues/2) on that.
