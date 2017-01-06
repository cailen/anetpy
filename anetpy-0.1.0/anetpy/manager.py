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
import json as jason

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
        json = self.request('list-instances')
        return json['list-instancesresponse']['instancesSet']

    def new_cloudserver(self, servername, planname, imageid, vm_location,
                        key_id=None, enablebackup=False):
        params = {
            'servername': str(servername),
            'planname': str(planname),
            'imageid': str(imageid),
            'vm_location': str(vm_location),
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
        return json['reboot-instanceresponse']['instancesSet']

    def destroy_cloudserver(self, instanceid):
        params = {
            'instanceid': instanceid
        }
        json = self.request('terminate-instance', params)
        json.pop('status', None)
        return json['terminate-instanceresponse']['instancesSet']

## images==========================================
#    def all_images(self):
#        params = {}
#        json = self.request(params)
#        return json['describe-image']['imagesset']

#    def show_image(self, imageid):
#        params = {
#            'imageid': imageid
#        }
#        json = self.request('describe-image', params)
#        return json['describe-imageresponse']['imagesset']

# ssh_keys=========================================
    def all_ssh_keys(self):
        json = self.request('list-sshkeys')
        return json['list-sshkeysresponse']['KeysSet']

## plans============================================
#    def all_plans(self, plan_name=None):
#        params = {
#            'Action': 'describe-plan',
#        }
#        json = self.request(params)
#        return json['describe-planresponse']['plans']

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

        orderparams = urllib.urlencode(orderparams)
        
        try:
            resp = requests.get(url, params=orderparams, timeout=60)
            json_resp = jason.loads(resp.content)
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

    #Generate the API signature
    def signature_request(self, string_to_sign, private_key):

        signature = hmac.new(
            self.private_key, string_to_sign, hashlib.sha256).digest()
        signature = base64.encodestring(signature)
        signature = signature.rstrip()

        return signature

if __name__ == '__main__':
    import os
    public_key = os.environ['ANET_PRIVATE_KEY']
    private_key = os.environ['ANET_PUBLIC_KEY']
    #public_key = 'ATL8f59337f60fb45e4ff600c38e62ab540'
    #private_key = '66f002a2b6c5d742a9ce6d6e4de333534c73b128'
    #anet = AnetManager(public_key, private_key, "2010-12-30")
    #Cloudserver.setup(public_key, private_key)
    #cloudservers = Cloudserver.list_all()
    #cloudserver = Cloudserver.add(
    #    servername='TESTING',
    #    planname='G2.2GB',
    #    imageid='ubuntu-14.04_64bit',
    #    vm_location='USEAST1',
    #    )
    #if cloudserver.ensure_powered_on():
    #    changed = True
    #    msg = "New server credentials:"
    #    print "Test"
    #print "Something"
    import sys
    fname = sys.argv[1]
    import pprint
    # size_id: 66, image_id: 1601, region_id: 1
    pprint.pprint(getattr(anet, fname)(*sys.argv[2:]))
