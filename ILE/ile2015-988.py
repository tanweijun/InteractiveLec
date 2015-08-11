import urllib
import webapp2
import jinja2
import os
import re
import datetime
from datetime import timedelta

from google.appengine.ext import ndb
from urlparse import urlparse
from google.appengine.api import users


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))
	
class BaseHandler(webapp2.RequestHandler):
	def generate(self, template_name, template_values={}):
		#Respond to the request by rendering the template
		template = jinja_environment.get_template(template_name)
		self.response.out.write(template.render(template_values))

class HomePage(BaseHandler):
	def get(self):
		self.generate('home.html')
		
class HomePageUser(BaseHandler):
	def get(self):
		user = users.get_current_user()
		if user:  # signed in already
			nickname = users.get_current_user().nickname()
			template_values = {
				'nickname': nickname,
				'logout': users.create_logout_url(self.request.host_url),
			}
			self.generate('homeuser.html', template_values)
		else:
			self.redirect(self.request.host_url)

class Files(ndb.Model):
	modCode = ndb.StringProperty()
	description = ndb.TextProperty()
	fileUrl = ndb.StringProperty()
	date = ndb.DateTimeProperty()
	uploadedBy = ndb.UserProperty()
	
class Upload(BaseHandler):
	def get(self, template_values={}):
		user = users.get_current_user()
		if user:  # signed in already
			nickname = users.get_current_user().nickname()
			template_values.update({
				'nickname': nickname,
				'logout': users.create_logout_url(self.request.host_url),
			})
		self.generate('upload.html', template_values)

	def post(self):
		file = Files()
		error = ''
		success = ''
		
		try:
			file.modCode = self.request.get('modCode').upper()
			if not re.match("^[\w+\s\w+]+$", file.modCode):
				error = error + 'Error: Special characters not allowed in module code. '
		except Exception, e:
			error = error + 'Error: Problem with Module Code. '
		try:
			file.description = self.request.get('desc')
			if not re.match("^[\w+\s\w+.,]*$", file.description):
				error = error + 'Error: Special characters not allowed in file description. '
		except Exception, e:
			error = error + 'Error: Problem with file Description. '
		try:
			file.fileUrl = self.request.get('fileUrl')
			# Check that file url scheme is http or https
			if (urlparse(file.fileUrl).scheme != 'http') and (urlparse(file.fileUrl).scheme != 'https'):
				error = error + 'Error: Url must be http or https. '
		except Exception, e:
			error = error + 'Error: Problem with file URL. '
			
		#Add 8 hours to UTC time for our timezone(GMT+8)
		file.date = datetime.datetime.now() + datetime.timedelta(hours=8)
		user = users.get_current_user()
		if user:  # signed in already
			file.uploadedBy = users.get_current_user()
		
		# No error case
		if error == '' and user:
			file.put()
			success = 'File uploaded successfully.'
			template_values = {
				'error': error,
                'success': success,
            }
			self.get(template_values)
		else:
			template_values = {
                'error': error,
				'success': success,
            }
			self.get(template_values)
	
class ChatLog(ndb.Model):
	author = ndb.StringProperty()
	content = ndb.StringProperty()
	question = ndb.StringProperty()
	date = ndb.DateTimeProperty()
		
class ChatsRequestHandler(BaseHandler):
	def renderChats(self):
		#ndb query order by date in ChatLog
		chatLog_query = ChatLog.query().order(-ChatLog.date)
		chats = chatLog_query.fetch(60)
		template_values = {
			'chats': chats,
		}
		self.generate('chats.html', template_values)
    
	def get(self):
		self.renderChats()

	def post(self):
		chatLog = ChatLog()
		chatLog.content = self.request.get('content')
		chatLog.author = users.get_current_user().nickname()
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
		user = users.get_current_user()
		if user:  # signed in already
			chatLog.put()
		self.renderChats()
		
class SearchHandler(BaseHandler):
	def post(self):
		#ndb query order by date
		target = self.request.get('modcode').upper()
		files = Files.query(Files.modCode == target).order(-Files.date)
		
		template_values = {
			'modCode': target,
			'files': files,
		}
	
		self.generate('searchresults.html', template_values)

class ViewHandler(BaseHandler):
	def post(self):
		target = self.request.get('url')
		viewer = "http://docs.google.com/gview?url=" + target + "&embedded=true"
		
		template_values = {
			'url': viewer,
		}
	
		self.generate('embed.html', template_values)		
		
app = webapp2.WSGIApplication([
    ('/', HomePage),
	('/home', HomePageUser),
	('/upload', Upload),
	('/getchats', ChatsRequestHandler),
	('/getfiles', SearchHandler),
	('/view', ViewHandler)], 
	debug=True)
	