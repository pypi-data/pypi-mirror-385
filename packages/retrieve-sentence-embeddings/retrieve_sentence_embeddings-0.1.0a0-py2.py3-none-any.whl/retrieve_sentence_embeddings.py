# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import sys
from json import load, dumps

from typing import List, Text

# urllib differences
if sys.version_info < (3,):
    from urllib2 import Request, urlopen


    def post_request_instance(url, data, headers):
        """Create POST request for Python 2.

        Args:
            url: The target URL for the request
            data: The data to be sent in the request body
            headers: Dictionary of HTTP headers

        Returns:
            Request: A configured POST request object
        """
        return Request(url, data=data, headers=headers)
else:
    from urllib.request import Request, urlopen


    def post_request_instance(url, data, headers):
        """Create POST request for Python 3.

        Args:
            url: The target URL for the request
            data: The data to be sent in the request body
            headers: Dictionary of HTTP headers

        Returns:
            Request: A configured POST request object
        """
        return Request(url, data=data, headers=headers, method=u'POST')


def retrieve_sentence_embeddings(
        api_key,  # type: Text
        base_url,  # type: Text
        model,  # type: Text
        sentences,  # type: List[Text]
):
    # type: (...) -> List[List[float]]
    url = u'%s/embeddings' % base_url
    headers = {
        u'Content-Type': u'application/json',
        u'Authorization': u'Bearer %s' % api_key
    }
    data = dumps({u'input': sentences, u'model': model}).encode('utf-8')
    req = post_request_instance(url, data=data, headers=headers)
    response = urlopen(req)
    response_json = load(response)
    return [
        data_object['embedding']
        for data_object in response_json['data']
    ]
