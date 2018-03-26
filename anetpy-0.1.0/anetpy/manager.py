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
#API
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
                        key_id=None, enablebackup='N'):
        params = {
            'servername': str(servername),
            'planname': str(planname),
            'imageid': str(imageid),
            'vm_location': str(vm_location),
            'key_id': str(key_id),
            'enablebackup': str(enablebackup)
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

    def shutdown_cloudserver(self, instanceid, shutdowntype):
        params = {
            'instanceid': instanceid,
            'shutdowntype': shutdowntype
        }
        json = self.request('shutdown-instance', params)
        json.pop('status', None)
        return json['shutdown-instanceresponse']['instancesSet']

    def poweron_cloudserver(self, instanceid)
        params = {
            'instanceid': instanceid
        }
        json = self.request('power-on-instance', params)
        json.pop('status', None)
        return json['power-on-instanceresponse']['instancesSet']

    def resize_cloudserver(self, instanceid, planname)
        params = {
            'instanceid': instanceid,
            'planname': planname
        }
        json = self.request('resize-instance', params)
        json.pop('status', None)
        return json['resize-instanceresponse']['instancesSet']

    def reprovision_cloudserver(self, instanceid, planname, imageid)
        params = {
            'instanceid': instanceid,
            'planname': planname,
            'imageid': imageid
        }
        json = self.request('reprovision-instance', params)
        json.pop('status', None)
        return json['reprovision-instanceresponse']['instancesSet']
    
## images==========================================
    def all_images(self):
        params = {}
        json = self.request('describe-image')
        return json['describe-imageresponse']['imagesset']

    def show_image(self, imageid):
        params = {
            'imageid': imageid
        }
        json = self.request('describe-image', params)
        return json['describe-imageresponse']['imagesset']

# ssh_keys=========================================
    def all_ssh_keys(self):
        json = self.request('list-sshkeys')
        return json['list-sshkeysresponse']['KeysSet']

    def add_ssh_key(self, keyname, publickey):
        params = {
            'keyname': keyname,
            'publickey': publickey
        }
        json= self.request('add-sshkey')
        json.pop('status', None)
        return json['add-sshkeyresponse']

    def delete_ssh_key(self, keyid):
        params = {
            'keyid': keyid,
        }
        json= self.request('delete-sshkey')
        json.pop('status', None)
        return json['delete-sshkeyresponse']

## plans===========================================
    def plans(self, plan_name=None):
        params = {}
        json = self.request('describe-plan')
        return json['describe-planresponse']['plans']

## public_ips======================================
    def list_public_ips(self, location=None, ip_address=None):
        params = {}
        json = self.request('list-public-ips')
        return json['list-public-ipsresponse']['KeysSet']
    
    def reserve_public_ip(self, location, qty=1):
        params = {
            'location': location,
            'qty': qty
        }
        json = self.request('reserve-public-ip')
        return json['reserve-public-ipresponse']['reserve-ip']

    def release_public_ip(self, ip_address):
        params = {
            'ip_address': ip_address
        }
        json = self.request('release-public-ip')
        return json['release-public-ipresponse']['release-ip']

    def assign_public_ip(self, instanceid, ip_address):
        params = {
            'instanceid': instanceid,
            'ip_address': ip_address
        }
        json = self.request('assign-public-ip')
        return json['assign-public-ipresponse']['assign-ip']

    def unassign_public_ip(self, ip_address):
        params = {
            'ip_address': ip_address
        }
        json = self.request('unassign-public-ip')
        return json['unassign-public-ipresponse']['unassign-ip']

# private_networks=================================
    def list_private_networks(self):
        params = {}
        json = self.request('list-private-networks')
        return json['list-private-networksresponse']['KeysSet']

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
    import sys
    fname = sys.argv[1]
    import pprint
    pprint.pprint(getattr(anet, fname)(*sys.argv[2:]))
