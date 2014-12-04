#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import httplib2
import sys
import json

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

client_params = json.load(open('client.json', 'r'))
client_id = client_params['client_id']
client_secret = client_params['client_secret']
redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

# The scope URL for read/write access to a user's calendar data
scope = ('email', 'profile','https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.readonly','https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/drive.appdata', 'https://www.googleapis.com/auth/drive.apps.readonly')

# Create a flow object. This object holds the client_id, client_secret, and
# scope. It assists with OAuth 2.0 steps to get user authorization and
# credentials.
flow = OAuth2WebServerFlow(client_id, client_secret, " ".join(scope), redirect_uri)

def main():
  # Create a Storage object. This object holds the credentials that your
  # application needs to authorize access to the user's data. The name of the
  # credentials file is provided. If the file does not exist, it is
  # created. This object can only hold credentials for a single user, so
  # as-written, this script can only handle a single user.
  storage = Storage('credentials.dat')

  # The get() function returns the credentials for the Storage object. If no
  # credentials were found, None is returned.
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    print "No credentials"
    #credentials = run(flow, storage)
    auth_uri = flow.step1_get_authorize_url()
    print "open this in your browser:", auth_uri
    code = raw_input("enter code:")
    credentials = flow.step2_exchange(code)
    storage.put(credentials)
    #flow_info = flow.step1_get_device_and_user_codes()
    #print "Enter the following code at %s: %s" % (flow_info.verification_url,
    #flow_info.user_code)
    #print "Then press Enter."
    #raw_input()
    #credentials = flow.step2_exchange(device_flow_info=flow_info)
    #print "Access token:", credentials.access_token
    #print "Refresh token:", credentials.refresh_token

  # Create an httplib2.Http object to handle our HTTP requests, and authorize it
  # using the credentials.authorize() function.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # The apiclient.discovery.build() function returns an instance of an API service
  # object can be used to make API calls. The object is constructed with
  # methods specific to the calendar API. The arguments provided are:
  #   name of the API ('calendar')
  #   version of the API you are using ('v3')
  #   authorized httplib2.Http() object that can be used for API calls
  service = build('drive', 'v2', http=http)

  try:

    # The Calendar API's events().list method returns paginated results, so we
    # have to execute the request in a paging loop. First, build the
    # request object. The arguments provided are:
    #   primary calendar for user
    files = service.files().list(q="title contains 'bug'").execute()
    print files
    # Loop until all pages have been processed.

    #while request != None:
      # Get the next page.
    #  response = request.execute()
      # Accessing the response like a dict object with an 'items' key
      # returns a list of item objects (events).
    #  for event in response.get('items', []):
        # The event object is a dict object with a 'summary' key.
    #    print repr(event.get('summary', 'NO SUMMARY')) + '\n'
      # Get the next request object by passing the previous request object to
      # the list_next method.
    #  request = service.events().list_next(request, response)

  except AccessTokenRefreshError:
    # The AccessTokenRefreshError exception is raised if the credentials
    # have been revoked by the user or they have expired.
    print ('The credentials have been revoked or expired, please re-run'
           'the application to re-authorize')

if __name__ == '__main__':
  main()
