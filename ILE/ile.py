import urllib
import webapp2
import jinja2
import os
import datetime
from datetime import timedelta
#import pytz
#from pytz import timezone

from google.appengine.ext import ndb
from google.appengine.api import memcache
#from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))
	
class BaseHandler(webapp2.RequestHandler):
	def generate(self, template_name, template_values={}):
		#Respond to the request by rendering the template
		template = jinja_environment.get_template(template_name)
		self.response.out.write(template.render(template_values))
			
class HomePage(BaseHandler):
    # Handler for the home page.
	def get(self):
		self.generate('home.html', {});
		
class AboutPage(BaseHandler):
    # Handler for the about page.
    def get(self):
        self.generate('about.html', {});

class ChatLog(ndb.Model):
	author = ndb.StringProperty()
	content = ndb.StringProperty()
	question = ndb.StringProperty()
	date = ndb.DateTimeProperty()
		
class ChatsRequestHandler(BaseHandler):
	def renderChats(self):
		#ndb query order by date in ChatLog
		chatLog_query = ChatLog.query().order(-ChatLog.date)
		chats = (chatLog_query.fetch(60))
		
		template_values = {
			'chats': chats,
		}
	
		return self.generate('chats.html', template_values)
      
	def getChats(self):
		chats = memcache.get("chats")
	
		if chats is not None:
			return chats
		else:
			chats = self.renderChats()
			return chats
    
	def get(self):
		self.getChats()

	def post(self):
		chatLog = ChatLog()
		chatLog.content = self.request.get('content')
		chatLog.author = self.request.get('author')
		chatLog.question = self.request.get('question')
		#Add 8 hours to UTC time for our timezone(GMT+8)
		chatLog.date = datetime.datetime.now() + datetime.timedelta(hours=8)
		"""
		current = datetime.datetime.now()
		#Returns County code like SG, IN etc.
		county_code = self.request.headers['X-Appengine-Country']
		tz = pytz.country_timezones(county_code)
		current = current.replace(tzinfo=pytz.utc).astimezone(tz)
		chatLog.date = current
		"""
		chatLog.put()

		self.getChats()	
		
		
app = webapp2.WSGIApplication([
    ("/", HomePage),
	("/about", AboutPage),
	('/getchats', ChatsRequestHandler)], 
	debug=True)
	