#!/usr/bin/env python
# coding: utf-8
"""
This module simply sends request to the Atlantic.Net API,
and returns their response as a dict.
"""

import time
import uuid
import urllib
import hmac
import hashlib
import base64
from collections import OrderedDict
import requests

API_ENDPOINT = 'https://cloudapi.atlantic.net/'


class AnetError(RuntimeError):
    """Passes any errors received after the REST request comes back."""
    pass


class AnetManager(object):
    def __init__(self, public_key, private_key, api_version="2010-12-30"):
        self.api_endpoint = API_ENDPOINT
        self.public_key = public_key
        self.private_key = private_key

    def all_active_cloudservers(self):
        json_resp = self.request('list-instances')
        return json_resp['list-instancesresponse']['instancesSet']

    def new_cloudserver(self, servername, planname, imageid, vm_location, server_qty,
                        key_id=None, enablebackup=False):

        params = {
            'servername': str(servername),
            'planname': str(planname),
            'imageid': str(imageid),
            'vm_location': str(vm_location),
            'server_qty': str(server_qty),
            'key_id': str(key_id),
            'enablebackup': str(enablebackup).lower()
        }

        json = self.request('run-instance', params)
        return json['run-instanceresponse']['instancesSet']

    def show_cloudserver(self, instanceid):
        params = {
            'instanceid': instanceid,
        }
        json = self.request('describe-instance', params)
        return json['describe-instanceresponse']['instanceSet']

    def power_cycle_cloudserver(self, instanceid, reboottype):
        params = {
            'instanceid': instanceid,
            'reboottype': reboottype
        }
        json = self.request('reboot-instance', params)
        json.pop('status', None)
        return json['reboot-instanceresponse']

    def destroy_cloudserver(self, instanceid):
        params = {
            'instanceid': instanceid
        }
        #count = 0
        #for instanceid in instanceids:
        #    count += 1
        #    params['instanceid_' + count] = instanceid

        json = self.request('terminate-instance', params)
        json.pop('status', None)
        return json['terminate-instanceresponse']['instancesSet']

    def populate_cloudserver_ips(self, cloudserver):
        return False
    #    cloudserver[u'ip_address'] = ''
    #    for networkIndex in range(len(cloudserver['networks']['v4'])):
    #        network = cloudserver['networks']['v4'][networkIndex]
    #        if network['type'] == 'public':
    #            cloudserver[u'ip_address'] = network['ip_address']
    #        if network['type'] == 'private':
    #            cloudserver[u'private_ip_address'] = network['ip_address']

# images==========================================
    def all_images(self):
        params = {}
        json = self.request(params)
        return json['describe-image']['imagesset']

    def show_image(self, imageid):
        params = {
            'imageid': imageid
        }
        json = self.request('describe-image', params)
        return json['describe-imageresponse']['imagesset']

# ssh_keys=========================================
    def all_ssh_keys(self):
        params = {
            'Action': 'list-sshkeys',
        }
        json = self.request(params)
        return json['list-sshkeysresponse']['KeysSet']

# plans============================================
    def plans(self, plan_name=None):
        params = {
            'Action': 'describe-plan',
        }
        json = self.request(params)
        return json['describe-planresponse']['plans']

# low_level========================================
    def request(self, action, params={}, method='GET'):
        random_guid = str(uuid.uuid4())
        time_since_epoch = int(time.time())
        string_to_sign = str(time_since_epoch) + str(random_guid)
        url = API_ENDPOINT
        signature = self.signature_request(string_to_sign, self.private_key)

        orderparams = OrderedDict()
        orderparams['Action'] = action
        orderparams['Format'] = "json"
        orderparams['Version'] = "2010-12-30"
        orderparams['ACSAccessKeyId'] = str(self.public_key)
        orderparams['Timestamp'] = str(time_since_epoch)
        orderparams['Rndguid'] = str(random_guid)
        orderparams['Signature'] = str(signature)

        for k, v in params.iteritems():
            orderparams[k] = v

        resp = self.request_v1(url, orderparams, method=method)

        return resp

    def signature_request(self, string_to_sign, private_key):
        signature = hmac.new(
            self.private_key, string_to_sign, hashlib.sha256).digest()
        signature = base64.encodestring(signature)
        signature = signature.rstrip()

        return signature

    def request_v1(self, url, params={}, method='GET'):
        params = urllib.urlencode(params)
        try:
            resp = requests.get(url, params=params, timeout=60)
            json_resp = resp.json()
        except ValueError:  # requests.models.json.JSONDecodeError
            raise ValueError(
                "The API server doesn't respond with a valid json")
        except requests.RequestException as e:  # errors from requests
            raise RuntimeError(e, resp)

        if resp.status_code != requests.codes.ok:
            if json_resp:
                if 'error_message' in json_resp:
                    raise AnetError(json_resp['message'])
                elif 'message' in json_resp:
                    raise AnetError(json_resp['message'])
            # The JSON reponse is bad, so raise an exception with the HTTP
            # status
            resp.raise_for_status()
        if str(json_resp.get('error')).lower() != 'none':
            raise AnetError(json_resp['error']['message'])

        return json_resp

if __name__ == '__main__':
    import os
    public_key = os.environ['ANET_PRIVATE_KEY']
    private_key = os.environ['ANET_PUBLIC_KEY']
    anet = AnetManager(public_key, private_key, "2010-12-30")
    import sys
    fname = sys.argv[1]
    import pprint
    # size_id: 66, image_id: 1601, region_id: 1
    pprint.pprint(getattr(anet, fname)(*sys.argv[2:]))
