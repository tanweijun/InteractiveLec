import urllib
import webapp2
import jinja2
import os
import datetime

from google.appengine.ext import ndb
#from google.appengine.api import users
from google.appengine.api import memcache

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
	date = ndb.DateTimeProperty(auto_now_add=True)
		
class ChatsRequestHandler(BaseHandler):
	def renderChats(self):
		#ndb query order by date in ChatLog
		chatLog_query = ChatLog.query().order(-ChatLog.date)
		#reverse the fetched content to print latest chats later from bottom to top
		chats = reversed(chatLog_query.fetch(60))

		template_values = {
			'chats': chats,
		}
	
		return self.generate('chats.html', template_values)
      
	def getChats(self):#, _use_Cache=True):
		#if _use_Cache is False:
		#	chats = self.renderChats()
		#	if not memcache.set("chat", chats, 60):
		#		logging.error("Memcache set failed:")
		#	return chats
      
		chats = memcache.get("chats")
	
		if chats is not None:
			return chats
		else:
			chats = self.renderChats()
		#	if not memcache.set("chat", chats, 60):
		#		logging.error("Memcache set failed:")
			return chats
    
	def get(self):
		self.getChats()

	def post(self):
		chatLog = ChatLog()
		chatLog.content = self.request.get('content')
		chatLog.author = self.request.get('author')
		chatLog.put()
    
		self.getChats()#False)		
		
		
app = webapp2.WSGIApplication([
    ("/", HomePage),
	("/about", AboutPage),
	('/getchats', ChatsRequestHandler)], 
	debug=True)
	