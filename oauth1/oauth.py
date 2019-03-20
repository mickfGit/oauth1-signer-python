#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#
# Copyright (c) 2019 MasterCard International Incorporated
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of
# conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or other materials
# provided with the distribution.
# Neither the name of the MasterCard International Incorporated nor the names of its
# contributors may be used to endorse or promote products derived from this software
# without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
from random import randint
import time

import oauth1.coreutils as util
from OpenSSL import crypto


class OAuth():

    def get_authorization_header(self, uri, method, payload, consumer_key, signing_key):

        # Get all the base parameters such as nonce and timestamp
        oauth_parameters = OAuthParameters()
        oauth_parameters.set_oauth_consumer_key(consumer_key)
        oauth_parameters.set_oauth_nonce(OAuth.get_nonce())
        oauth_parameters.set_oauth_timestamp(OAuth.get_timestamp())
        oauth_parameters.set_oauth_signature_method("RSA-SHA256")
        oauth_parameters.set_oauth_version("1.0")
        if method != "GET" and method != "DELETE" and method != "HEAD":
            encoded_hash = util.base64_encode(util.sha256_encode(payload))
            oauth_parameters.set_oauth_body_hash(encoded_hash)

        # Get the base string
        base_string = OAuth.get_base_string(uri, method, oauth_parameters, oauth_parameters.get_base_parameters_dict())

        # Sign the base string using the private key
        signature = OAuth.sign_message(self, base_string, signing_key)

        # Set the signature in the Base parameters
        oauth_parameters.set_oauth_signature(signature)

        # Get the updated base parameteres dict
        oauth_base_parameters_dict = oauth_parameters.get_base_parameters_dict()

        # Generate the header value for OAuth Header
        oauth_key = OAuthParameters.OAUTH_KEY+" "+ \
                    ",".join([util.uri_rfc3986_encode(str(key)) + "=\"" +
                              util.uri_rfc3986_encode(str(value)) + "\"" for (key, value) in oauth_base_parameters_dict.items()])
        return oauth_key


    def get_base_string(url, method, query_params, oauth_parameters):
        # Merge the query string parameters
        merge_params = oauth_parameters.copy()
        #  merge_params.update(query_params)
        return "{}&{}&{}".format(util.uri_rfc3986_encode(method.upper()),
                                 util.uri_rfc3986_encode(util.normalize_url(url)),
                                 util.uri_rfc3986_encode(util.normalize_params(url, merge_params)))

    def sign_message(self, message, signing_key):
        #    Signs the message using the private key with sha1 as digest
        sign = crypto.sign(signing_key, message.encode("utf-8"),'SHA256')
        return util.base64_encode(sign)



    def get_timestamp():
        """
        Returns the UTC timestamp (seconds passed since epoch)
        """
        return int(time.time())

    def get_nonce(length = 16):
        """
        Returns a random string of length=@length
        """
        characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        charlen    = len(characters)
        return "".join([characters[randint(0,charlen-1)] for i in range(0,length)])


class OAuthParameters(object):
    """
    Stores the OAuth parameters required to generate the Base String and Headers constants
    """

    OAUTH_BODY_HASH_KEY = "oauth_body_hash"
    OAUTH_CONSUMER_KEY = "oauth_consumer_key"
    OAUTH_NONCE_KEY = "oauth_nonce"
    OAUTH_KEY = "OAuth"
    AUTHORIZATION = "Authorization"
    OAUTH_SIGNATURE_KEY = "oauth_signature"
    OAUTH_SIGNATURE_METHOD_KEY = "oauth_signature_method"
    OAUTH_TIMESTAMP_KEY = "oauth_timestamp"
    OAUTH_VERSION = "oauth_version"

    def __init__(self):
        self.base_parameters = {}

    def put(self, key, value):
        self.base_parameters[key] = value

    def set_oauth_consumer_key(self, consumer_key):
        self.put(OAuthParameters.OAUTH_CONSUMER_KEY, consumer_key)

    def set_oauth_nonce(self, oauth_nonce):
        self.put(OAuthParameters.OAUTH_NONCE_KEY, oauth_nonce)

    def set_oauth_timestamp(self, timestamp):
        self.put(OAuthParameters.OAUTH_TIMESTAMP_KEY, timestamp)

    def set_oauth_signature_method(self, signature_method):
        self.put(OAuthParameters.OAUTH_SIGNATURE_METHOD_KEY, signature_method)

    def set_oauth_signature(self, signature):
        self.put(OAuthParameters.OAUTH_SIGNATURE_KEY, signature)

    def set_oauth_body_hash(self, body_hash):
        self.put(OAuthParameters.OAUTH_BODY_HASH_KEY, body_hash)

    def set_oauth_version(self, version):
        self.put(OAuthParameters.OAUTH_VERSION, version)

    def get_base_parameters_dict(self):
        return self.base_parameters
