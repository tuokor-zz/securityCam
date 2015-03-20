#!/usr/bin/python

import httplib2
import sys
import json
import time
import pprint
import simplejson
import os

import apiclient.http
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from apiclient import errors


class DriveUp:

    def __init__(self, configfile):
        self.client_params = json.load(open(configfile, 'r'))
        self.client_id = self.client_params['client_id']
        self.client_secret = self.client_params['client_secret']
        self.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        self.scope = ('email', 'profile','https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.readonly','https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/drive.appdata', 'https://www.googleapis.com/auth/drive.apps.readonly')
        self.service = None

    def authenticate(self):
        flow = OAuth2WebServerFlow(self.client_id, self.client_secret, " ".join(self.scope), self.redirect_uri)
        storage = Storage('credentials.dat')
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

        self.service = build('drive', 'v2', http=http)

    def upload(self, filepath):
        if self.service is None:
            raise ValueError("run authenticate before uploading")
        try:
            folder_id = None
            files = self.service.files().list(q="title = 'SecurityCam' and mimeType = 'application/vnd.google-apps.folder'").execute()
            if len(files['items']) == 0:
                print("no folder found");
                folder = {'mimeType': "application/vnd.google-apps.folder" , 'title': "SecurityCam"}
                resp = self.service.files().insert(body=folder).execute()
                folder_id = resp['id']
                print("folder created {0}".format(resp))
            else:
                print("SecurityCam folder present uploading given file")
                folder_id = files['items'][0]['id']
                print("folder id:{0}".format(folder_id))

                print("going to upload:{0}".format(filepath))
                try:
                    f = filepath
                    name = os.path.split(f)
                    media_body = apiclient.http.MediaFileUpload(f, resumable=True)
                    metadata = {
                        'title': name[1],  #"snapshot_{0}".format(int(time.time()*1000)),
                        'parents': [
                            {
                                'kind': "drive#parentReference",
                                'id': folder_id
                            }
                        ]

                    }

                    new_file = self.service.files().insert(body=metadata, media_body=media_body).execute()
                    #pprint.pprint(new_file)
                    print("upload successful, removing file")
                    os.remove(f)
                except errors.HttpError, e:
                    try:
                        error = simplejson.loads(e.content)
                        print("error code: {0}".format(error.get('code')))
                        print("error msg: {0}".format(error.get('message')))
                    except ValueError:
                        print("HTTP statuscode:{0}".format(e.resp.status))
                        print("HTTP reason:{0}".format(e.resp.reason))
                except:
                    print("unknown error: {0}".format(sys.exc_info()[0]))
                    raise

        except AccessTokenRefreshError:
            print("access tokens revoked, please re-authenticate")

if __name__ == '__main__':
    up = DriveUp('client.json')
    up.authenticate()
    up.upload(sys.argv[1])
