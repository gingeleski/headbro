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

from browsermobproxy import Server
from flask import Flask, request, Response
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotSelectableException, TimeoutException

import atexit
import copy
import json
import psutil
import time
import validators

BROWSERMOB_PROXY_PATH = './dependencies/browsermob-proxy-2.1.4/browsermob-proxy'

def exit_handler():
    browsermob_server.stop()
    driver.quit()

app = Flask(__name__)

# Set up BrowserMob proxy
for proc in psutil.process_iter():
    # Kill BrowserMob if it happens to already be running
    if proc.name() == 'browsermob-proxy':
        proc.kill()
browsermob_options = {'port': 8090}
browsermob_server = Server(path=BROWSERMOB_PROXY_PATH, options=browsermob_options)
browsermob_server.start()
time.sleep(1)
proxy = browsermob_server.create_proxy()
time.sleep(1)
selenium_proxy = proxy.selenium_proxy()

# Set up the Selenium driver for headless Chrome
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
                if 'script' in request_json:
                    script_to_execute = request_json['script']
                    driver.execute_script(script_to_execute)
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
                # TODO - apparently we can't get response status or headers with Selenium
                output['status_code'] = None
                output['headers'] = {}
                output['alerts'] = []
                output['confirms'] = []
                output['prompts'] = []
                # Loop to handle all JavaScript popups
                while True:
                    try:
                        WebDriverWait(driver,1).until(EC.alert_is_present(), 'No JS popups - timed out.')
                        popup = driver.switch_to.alert
                        try:
                            popup.send_keys('test123')
                            # If no exception, this is a *prompt* popup
                            output['prompts'].append(popup.text)
                            popup.accept()
                        except ElementNotSelectableException:
                            try:
                                ###text_backup = copy.deepcopy(popup.text)
                                # FIXME currently can't differentiate between confirms and alerts, put both as alerts
                                output['alerts'].append(popup.text)
                                popup.dismiss()
                                # If no exception, this is a *confirm* popup
                                ###output['confirms'].append(text_backup)
                            except AttributeError:
                                # Must be an *alert* popup at this point
                                ###output['alerts'].append(popup.text)
                                popup.accept()
                    except TimeoutException:
                        # Break on timeout, no (more) popups
                        break
                output['errors'] = []
                output['messages'] = []
                # Get console errors and other messages
                for log in driver.get_log('browser'):
                    if log['level'] and log['level'] == 'SEVERE':
                        # Consider this an error
                        output['errors'].append(log)
                    else:
                        # Everything else we'll call a console message
                        output['messages'].append(log)
                output['body'] = driver.page_source
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
