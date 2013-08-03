# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Request Handler for /upload endpoint."""


import io
import logging
import webapp2

import XMPP_addr_access


from apiclient.http import MediaIoBaseUpload
from oauth2client.appengine import StorageByKeyName



from model import Credentials
import util
from google.appengine.api import memcache



class UploadHandler(webapp2.RequestHandler):
  def post(self):
    xmpp_addr=self.request.get('xmpp_addr')
    msg=self.request.get('msg')
    logging.info('post test')
    #logging.info("ImagestoreHandler#post %s", self.request.path)
    fileupload = self.request.POST.get("file",None)
    if fileupload is None : return self.error(400) 
    # it doesn't seem possible for webob to get the Content-Type header for the individual part, 
    # so we'll infer it from the file name.
    contentType = getContentType( fileupload.filename )
    if contentType is None: 
      self.error(400)
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write( "Unsupported image type: " + fileupload.filename )
      return
    logging.info( "File upload: %s, mime type: %s", fileupload.filename, contentType )
    file_data= fileupload.file.read()
    self.response.out.write('Got a '+str(len(file_data))+' bytes file\n')
       
    if xmpp_addr:
      self.response.out.write('XMPP address: '+xmpp_addr+'\n')
      id=XMPP_addr_access.get_id_from_addr(xmpp_addr)
      if id is not None:
        creds=StorageByKeyName(Credentials, id, 'credentials').get()
        mirror_service = util.create_service('mirror', 'v1', creds)
        logging.info('insert IMG')
        body = {'notification': {'level': 'DEFAULT'}}		
        if msg is not None: body['text'] = msg
        media = MediaIoBaseUpload(io.BytesIO(file_data), mimetype='image/jpeg', resumable=True)
        mirror_service.timeline().insert(body=body, media_body=media).execute()     
    else:
      self.response.out.write('no XMPP address')

  def get(self):
    self.response.out.write('An upload page')



def getContentType( filename ): # lists and converts supported file extensions to MIME type
  ext = filename.split('.')[-1].lower()
  if ext == 'jpg' or ext == 'jpeg': return 'image/jpeg'
  if ext == 'png': return 'image/png'
  if ext == 'gif': return 'image/gif'
  if ext == 'svg': return 'image/svg+xml'
  return None


UPLOAD_ROUTES = [
    ('/upload', UploadHandler)
]
