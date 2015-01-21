#!/usr/bin/python

import httplib2
import sys
import json
import time
import pprint
import simplejson

import apiclient.http
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from apiclient import errors

client_params = json.load(open('client.json', 'r'))
client_id = client_params['client_id']
client_secret = client_params['client_secret']
redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

scope = ('email', 'profile','https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.readonly','https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/drive.appdata', 'https://www.googleapis.com/auth/drive.apps.readonly')


flow = OAuth2WebServerFlow(client_id, client_secret, " ".join(scope), redirect_uri)

def main():

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

  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build('drive', 'v2', http=http)

  try:

    folder_id = None
    files = service.files().list(q="title = 'SecurityCam' and mimeType = 'application/vnd.google-apps.folder'").execute()
    if len(files['items']) == 0:
        print("no folder found");
        folder = {'mimeType': "application/vnd.google-apps.folder" , 'title': "SecurityCam"}
        resp = service.files().insert(body=folder).execute()
        folder_id = resp['id']
        print("folder created {0}".format(resp))
    else:
        print("SecurityCam folder present uploading given file")
        folder_id = files['items'][0]['id']
        print("folder id:{0}".format(folder_id))
        if len(sys.argv) < 2:
            print("Missing file parameter")
        else:
            print("going to upload:{0}".format(sys.argv[1]))
            try:
                f = sys.argv[1]
                media_body = apiclient.http.MediaFileUpload(f, resumable=True)
                metadata = {
                    'title': "snapshot_{0}".format(int(time.time()*1000)),
                    'parents': [
                        {
                            'kind': "drive#parentReference",
                            'id': folder_id
                        }
                    ]

                }

                new_file = service.files().insert(body=metadata, media_body=media_body).execute()
                #pprint.pprint(new_file)
                print("upload successful")
            except errors.HttpError, e:
                try:
                    error = simplejson.load(e.content)
                    print("error code: {0}".format(error.get('code')))
                    print("error msg: {0}".format(error.get('message')))
                except ValueError:
                    print("HTTP statuscode:{0}".format(e.resp.status))
                    print("HTTP reason:{0}".format(e.resp.reason))

  except AccessTokenRefreshError:
    # The AccessTokenRefreshError exception is raised if the credentials
    # have been revoked by the user or they have expired.
    print ('The credentials have been revoked or expired, please re-run'
           'the application to re-authorize')

if __name__ == '__main__':
  main()
