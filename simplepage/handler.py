

import webapp2
from google.appengine.api import memcache


class SimplePageHandler(webapp2.RequestHandler):
	def get(self):
		data = memcache.get("recent_message")
		if data is None:
			self.response.out.write('!!!no reply yet!!!')			
		else:
			self.response.out.write('%s' %(data))	



SIMPLEPAGE_ROUTES = [('/simplepage', SimplePageHandler)]
