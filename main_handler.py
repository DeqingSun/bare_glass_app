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

"""Request Handler for /main endpoint."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import io
import jinja2
import logging
import os
import webapp2
import datetime

from google.appengine.api import memcache
from google.appengine.api import urlfetch

from google.appengine.api import xmpp
from google.appengine.ext.webapp import xmpp_handlers

from oauth2client.client import flow_from_clientsecrets
from model import Credentials

import XMPP_addr_access

import httplib2
from apiclient import errors
from apiclient.http import MediaIoBaseUpload
from apiclient.http import BatchHttpRequest
from oauth2client.appengine import StorageByKeyName

from model import Credentials
import util


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def bare_jid(sender):
    """Identify the user by bare jid."""
    return sender.split('/')[0]


class XmppHandler(xmpp_handlers.CommandHandler):
    """Handler class for all XMPP activity."""


    def unhandled_command(self, message=None):
        message.reply('unhandled')


    def text_message(self, message=None):
        message.reply('got TEXT')


    def echo_command(self, message=None):
        """Handles /echo requests"""
        #message.reply(message.body)
        message.reply(message.arg)

    def info_command(self, message=None):
        """Handles /info requests"""
        message.reply('from: '+ message.sender + ' to: ' + message.to )
        
    def push_command(self, message=None):
        """Handles /push requests"""
        if message.arg:
            id=XMPP_addr_access.get_id_from_addr(message.sender)
            if id is not None:
                creds=StorageByKeyName(Credentials, id, 'credentials').get()
                mirror_service = util.create_service('mirror', 'v1', creds)
                #logging.info('Main handler: cred: %s',creds)  
                body = {'notification': {'level': 'DEFAULT'}}
                body['text'] = message.arg
                mirror_service.timeline().insert(body=body).execute()

class XmppPresenceHandler(webapp2.RequestHandler):
    """Handler class for XMPP status updates."""

    def post(self, status):
        """POST handler for XMPP presence.

        Args:
            status: A string which will be either available or unavailable
               and will indicate the status of the user.
        """
        sender = self.request.get('from')
"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""

class _BatchCallback(object):
  """Class used to track batch request responses."""

  def __init__(self):
    """Initialize a new _BatchCallbaclk object."""
    self.success = 0
    self.failure = 0

  def callback(self, request_id, response, exception):
    """Method called on each HTTP Response from a batch request.

    For more information, see
      https://developers.google.com/api-client-library/python/guide/batch
    """
    if exception is None:
      self.success += 1
    else:
      self.failure += 1
      logging.error(
          'Failed to insert item for user %s: %s', request_id, exception)


class MainHandler(webapp2.RequestHandler):
  """Request Handler for the main endpoint."""

  def _render_template(self, message=None):
    """Render the main page template."""
    template_values = {'userId': self.userid}
    if message:
      template_values['message'] = message
    # self.mirror_service is initialized in util.auth_required.
    try:
      template_values['contact'] = self.mirror_service.contacts().get(
        id='Python Quick Start').execute()
    except errors.HttpError:
      logging.info('Unable to find Python Quick Start contact.')

    timeline_items = self.mirror_service.timeline().list(maxResults=3).execute()
    template_values['timelineItems'] = timeline_items.get('items', [])

    subscriptions = self.mirror_service.subscriptions().list().execute()
    for subscription in subscriptions.get('items', []):
      collection = subscription.get('collection')
      if collection == 'timeline':
        template_values['timelineSubscriptionExists'] = True
      elif collection == 'locations':
        template_values['locationSubscriptionExists'] = True
        
    template_values['XMPPaddr'] = XMPP_addr_access.get_addr_from_id(self.userid)

    template = jinja_environment.get_template('templates/index.html')
    self.response.out.write(template.render(template_values))

  @util.auth_required
  def get(self):
    """Render the main page."""
    # Get the flash message and delete it.
    message = memcache.get(key=self.userid)
    memcache.delete(key=self.userid)
    logging.info('Main handler: id: %s',self.userid) # this is the same id as the one from subscription   
    self._render_template(message)

  @util.auth_required
  def post(self):
    """Execute the request and render the template."""
    operation = self.request.get('operation')
    # Dict of operations to easily map keys to methods.
    operations = { 
        'insertItem': self._insert_item,
        'insertReplyToItem': self._insert_replyto_item,
        'addXmppAddress': self._add_XMPP_address
    }
    if operation in operations:
      message = operations[operation]()
    else:
      message = "I don't know how to " + operation
    # Store the flash message for 5 seconds.
    memcache.set(key=self.userid, value=message, time=5)
    self.redirect('/')

  def _add_XMPP_address(self):
    addr=self.request.get('xmppaddress')
    logging.info('add addr: %s',addr)
    XMPP_addr_access.set_addr_id(addr,self.userid)	#add address and ID pair

    return  'XMPP address added'


  def _insert_item(self):
    """Insert a timeline item."""
    logging.info('Inserting timeline item')
    body = {
        'notification': {'level': 'DEFAULT'}
    }
    if self.request.get('html') == 'on':
      body['html'] = [self.request.get('message')]
    else:
      body['text'] = self.request.get('message')

    media_link = self.request.get('imageUrl')
    if media_link:
      if media_link.startswith('/'):
        media_link = util.get_full_url(self, media_link)
      resp = urlfetch.fetch(media_link, deadline=20)
      media = MediaIoBaseUpload(
          io.BytesIO(resp.content), mimetype='image/jpeg', resumable=True)
    else:
      media = None

    # self.mirror_service is initialized in util.auth_required.
    self.mirror_service.timeline().insert(body=body, media_body=media).execute()
    return  'A timeline item has been inserted.'

  def _insert_replyto_item(self):
    """Insert a timeline test item"""
    logging.info('Inserting timeline item')
    body = {
        'creator': {
            'displayName': 'Glassware Physical Interaction Project',
            'id': 'GLASSWARE_PHYSICAL_INTERACTION_PROJECT'
        },
        'text': 'A test 4 physical interaction',
        'notification': {'level': 'DEFAULT'},
        'menuItems': [{'action': 'REPLY'},{'action': 'TOGGLE_PINNED'}]
    }
    # self.mirror_service is initialized in util.auth_required.
    self.mirror_service.timeline().insert(body=body).execute()
    return 'A test timeline item has been inserted.'


MAIN_ROUTES = [
    ('/', MainHandler),
    ('/_ah/xmpp/message/chat/', XmppHandler),
    ('/_ah/xmpp/presence/(available|unavailable)/', XmppPresenceHandler),
]
