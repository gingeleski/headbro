"""
headbro.py

Headless browser rendering service for HTTP responses.

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
import json
import time
import validators

def exit_handler():
    driver.quit()

app = Flask(__name__)

chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument('headless')

driver = webdriver.Chrome(chrome_options = chrome_options)

driver.set_page_load_timeout(10) # 10 second timeout on any page loads

@app.route('/render', methods=['POST'])
def get_and_render():
    request_body = request.get_data().decode('utf-8')
    try:
        request_json = json.loads(request_body)
        if 'url' in request_json:
            target_url = request_json['url']
            if True == validators.url(target_url):
                request_method = 'GET'
                # See if there's another method specified via input
                if 'method' in request_json and str(request_json['method']).lower() != 'get':
                    parsed_method = str(request_json['method']).lower()
                    if parsed_method == 'post':
                        pass # TODO
                    elif parsed_method == 'put':
                        pass # TODO
                    elif parsed_method == 'delete':
                        pass # TODO
                    else:
                        return Response('Input JSON has invalid "method": %s' % parsed_method, status=400, mimetype='text/plain')
                if 'invoke_events' in request_json:
                    parsed_invoke_events = request_json['invoke_events']
                    if type(parsed_invoke_events) is list:
                        for parsed_event in parsed_invoke_events:
                            pass # TODO
                    else:
                        return Response('Input JSON has invalid "invoke_events"', status=400, mimetype='text/plain')
                # Execute request with headless Chrome
                driver.get(target_url) # TODO eventually handle other HTTP methods about here
                output = {}
                output['body'] = driver.page_source
                # TODO - apparently we can't get response status or headers with Selenium
                output['status_code'] = None
                output['headers'] = {}
                # TODO populate the following
                output['errors'] = []
                output['messages'] = []
                output['alerts'] = []
                output['confirms'] = []
                output['prompts'] = []
                return json.dumps(output)
            else:
                return Response('Invalid URL: %s' % target_url, status=400, mimetype='text/plain')
        else:
            return Response('Input JSON object missing required "url" field', status=400, mimetype='text/plain')
    except ValueError as error:
        return Response('Invalid JSON: %s' % error, status=400, mimetype='text/plain')

if __name__ == '__main__':
    atexit.register(exit_handler)
    app.run(port=9009)
