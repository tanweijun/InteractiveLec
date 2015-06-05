import urllib
import webapp2
import jinja2
import os
import datetime

from google.appengine.ext import ndb
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class HomePage(webapp2.RequestHandler):
    # Handler for the home page.
    def get(self):
        template = jinja_environment.get_template('home.html')
        self.response.out.write(template.render())
		
class AboutPage(webapp2.RequestHandler):
    # Handler for the about page.
    def get(self):
        template = jinja_environment.get_template('about.html')
        self.response.out.write(template.render())

		
app = webapp2.WSGIApplication([
    ("/", HomePage),
	("/about", AboutPage)], 
	debug=True)
