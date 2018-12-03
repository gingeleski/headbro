"""
headbro.py

Headless browser rendering service for HTTP responses.

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
import os
import psutil
import time
import validators

########################################################################################################################

BROWSERMOB_PROXY_PATH = os.path.join('dependencies', 'browsermob-proxy-2.1.4', 'bin', 'browsermob-proxy')

########################################################################################################################

def exit_handler():
    browsermob_server.stop()
    driver.quit()

def request_string_is_valid(rs):
    if rs.startswith('GET /') or rs.startswith('POST /') or rs.startswith('PUT /') or rs.startswith('DELETE /'):
        if 'HTTP/1.1' in rs:
            if 'Host: ' in rs or 'Origin: ' in rs:
                return True
    return False

def derive_url_from_request_string(rs):
    derived_url = ''
    # Relative target - get from the first "/"" to " HTTP/"
    rel_target_part = rs.startswith(' HTTP/')[0]
    if rs.startswith('GET ') or rs.startswih('PUT '):
        rel_target = rel_target_part[4:]
    elif rs.startswith('POST '):
        rel_target = rel_target_part[5:]
    elif rs.startswith('DELETE '):
        rel_target = rel_target_part[7:]
    # Target domain will come from Host or Origin header of request string
    rs_lines = rs.splitlines()
    for rs_line in rs_lines:
        if rs_line.startswith('Host: '):
            derived_url = 'http://' + rs_line[6:] + rel_target
            break
        elif rs_line.startswith('Origin: '):
            derived_url = 'http://' + rs_line[8:] + rel_target
            break
    return derived_url

def get_headers_from_request_string(rs):
    headers = {}
    rs_lines = rs.splitlines()
    for rs_line in rs_lines:
        if rs_line.contains('HTTP/1.1'):
            continue
        elif rs_line.contains(': '):
            header_parts = rs_line.split(': ')
            headers[header_parts[0]] = header_parts[1]
        else:
            # Assume we've hit the line break before request body
            break
    return headers

########################################################################################################################

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

# Set up the Selenium driver for headless Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument('proxy-server={0}'.format(proxy.proxy))
# Start: "Pen testing" options
chrome_options.add_argument('disable-web-security')
chrome_options.add_argument('allow-running-insecure-content')
chrome_options.add_argument('disable-client-side-phishing-detection')
chrome_options.add_argument('disable-extensions')
chrome_options.add_argument('disable-offer-store-unmasked-wallet-cards')
chrome_options.add_argument('disable-offer-upload-credit-cards')
chrome_options.add_argument('disable-popup-blocking')
chrome_options.add_argument('disable-signin-promo')
chrome_options.add_argument('disable-suggestions-ui')
chrome_options.add_argument('disable-sync')
chrome_options.add_argument('disable-xss-auditor')
chrome_options.add_argument('ignore-certificate-errors')
chrome_options.add_argument('reduce-security-for-testing')
chrome_options.add_argument('safe-browsing-disable-auto-update')
chrome_options.add_argument('safe-browsing-disable-download-protection')
chrome_options.add_argument('safe-browsing-disable-extension-blacklist')
# End: "Pen testing" options
driver = webdriver.Chrome(chrome_options = chrome_options)
driver.set_page_load_timeout(10) # 10 second timeout on any page loads

########################################################################################################################

"""
ROUTES

/render (POST)
/render/string (POST)
"""

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
                        return Response('Input JSON has invalid "method": %s' % parsed_method,\
                                                                            status=400, mimetype='text/plain')
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
                # Prep a har object to get this from the proxy
                proxy.new_har('this_request')
                # Execute request with headless Chrome
                try:
                    driver.get(target_url) # TODO eventually handle other HTTP methods about here
                except:
                    # *Right now assuming exception is for timeout*
                    return Response('Request timed out', status=504, mimetype='text/plain')
                output = {}
                try:
                    status_code_via_proxy = proxy.har['log']['entries'][0]['response']['status']
                    output['status_code'] = status_code_via_proxy
                except:
                    output['status_code'] = 0
                try:
                    response_headers_via_proxy = proxy.har['log']['entries'][0]['response']['headers']
                    output['headers'] = response_headers_via_proxy
                except:
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

@app.route('/render/string', methods=['POST'])
def render_via_string():
    request_body = request.get_data().decode('utf-8')
    try:
        request_json = json.loads(request_body)
        if 'request_string' in request_json:
            request_string = request_json['request_json']
            if request_string_is_valid(request_string):
                if 'url' in request_json:
                    url = request_json['url']
                else:
                    url = derive_url_from_request_string(request_string)
                print('DEBUG: url = ' + url)
                headers = get_headers_from_request_string(request_string)
                # TODO
                return Response('OK', status=200, mimetype='text/plain')
            return Response('Functionality not yet implemented', status=501, mimetype='text/plain')
        elif 'response_string' in request_json:
            # TODO
            return Response('Functionality not yet implemented', status=501, mimetype='text/plain')
        else:
            return Response('Input JSON object missing required field', status=400, mimetype='text/plain')
    except ValueError as error:
        return Response('Invalid JSON: %s' % error, status=400, mimetype='text/plain')

########################################################################################################################

if __name__ == '__main__':
    atexit.register(exit_handler)
    app.run(port=9009)
