"""
Working out mitmproxy logic here before situating into headbro.py
"""


from mitmproxy import controller, proxy

import datetime
import json
import os
import re
import sys 


class RequestHacks:
    @staticmethod
    def example_com (msg):
        # tamper outgoing requests for https://example.com/api/v2
        if ('example.org' in msg.host) and ('action=login' in msg.content):
            fake_lat, fake_lng = 25.0333, 121.5333
            tampered = re.sub('lat=([\d.]+)&lng=([\d.]+)', 'lat=%s&lng=%s' % (fake_lat, fake_lng), msg.content)
            msg.content = tampered
            print('[RequestHacks][Example.com] Fake location (%s, %s) sent when logging in' % (fake_lat, fake_lng))


class ResponseHacks:
    @staticmethod
    def example_org (msg):
        # simple substitution for https://example.org/api/users/:id.json
        if 'example.org' in msg.request.host:
            regex = re.compile('/api/users/(\d+).json')
            match = regex.search(msg.request.path)
            if match and msg.content:
                c = msg.replace('\'private_data_accessible\':false', '\'private_data_accessible\':true')
                if c > 0:
                    user_id = match.groups()[0]
                    print('[ResponseHacks][Example.org] Private info of user #%s revealed' % user_id)

    @staticmethod
    def example_com (msg):
        # JSON manipulation for https://example.com/api/v2
        if ('example.com' in msg.request.host) and ('action=user_profile' in msg.request.content):
            msg.decode() # need to decode the message first
            data = json.loads(msg.content) # parse JSON with decompressed content
            data['access_granted'] = true
            msg.content = json.dumps(data) # write back our changes
            print('[ResponseHacks][Example.com] Access granted of user profile #%s' % data['id'])

    @staticmethod
    def example_net (msg):
        # Response inspection for https://example.net
        if 'example.net' in msg.request.host:
            data = msg.get_decoded_content() # read decompressed content without modifying msg
            print('[ResponseHacks][Example.net] Respones: %s' % data)


class InterceptingMaster (controller.Master):
    def __init__ (self, server):
        controller.Master.__init__(self, server)

    def run (self):
        while True:
            try:
                controller.Master.run(self)
            except KeyboardInterrupt:
                print('KeyboardInterrupt received. Shutting down')
                self.shutdown()
                sys.exit(0)
            except Exception:
                print('Exception catched. Intercepting proxy restarted')
                pass

    def handle_request (self, msg):
        timestamp = datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S')
        client_ip = msg.client_conn.address[0]
        request_url = '%s://%s%s' % (msg.scheme, msg.host, msg.path)
        print('[%s %s] %s %s' % (timestamp, client_ip, msg.method, request_url))
        RequestHacks.example_com(msg)
        msg.reply()

    def handle_response (self, msg):
        ResponseHacks.example_org(msg)
        ResponseHacks.example_com(msg)
        ResponseHacks.example_net(msg)
        msg.reply()


def main (argv):
    config = proxy.ProxyConfig(
        cacert = os.path('./dependencies/openssl/mitmproxy.pem'),
    )
    server = proxy.ProxyServer(config, 9010)
    print('Intercepting Proxy listening on 9010')
    m = InterceptingMaster(server)
    m.run()

if __name__ == '__main__':
    main(sys.argv)
