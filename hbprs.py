"""
hbprs.py

Headless Browser Page Rendering Service (HBPRS)

Send a POST request to the service where body is just the URL to GET

Then it sends back rendered page source

Eventually it'll all be formatted as follows...

    {
        html : base64-encoded string of the page's rendered html
        errors : list of strings for javascript error() messages
        messages : list of strings for javascript console.log() messages
        confirms : list of strings for javascript confirm() messages
        prompts : list of strings for javascript prompt() messages
    }

"""

from flask import Flask, request, Response
from selenium import webdriver

import atexit
import time

def exit_handler():
    driver.quit()

app = Flask(__name__)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')

driver = webdriver.Chrome(chrome_options = chrome_options)

@app.route('/', methods=['POST'])
def get_and_render():
    target = request.get_data().decode('utf-8')
    driver.get(target)
    return Response(str(driver.page_source), status=200, mimetype='text/plain')

if __name__ == '__main__':
    atexit.register(exit_handler)
    app.run(port=9009)
