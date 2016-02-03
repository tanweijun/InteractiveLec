# Interactive Lecture Environment
Interactive Lecture Environment or simply, ILE, is a webapp that allows a lecture to be more interesting through interaction. It stores file URLs, has an interactive chatbox which allows questions to be answered and has more features to come.

## Self-Hosting  (http://ile2015-988.appspot.com/)
The webapp may be currently down due to the overquota issue with appspot since we are hosting as a free user. You may want to host it yourself to alleviate this issue. Google App Engine's quota resets daily at 3pm.

### Requirements
Before you host the website, you must have the follwing installed:
- Google App Engine
- Python
- Jinja2
- Git

## Technologies Used
The shoutbox implements AJAX and GAE's ndb to store and retrieve messages. Search and view functions uses AJAX. For files, the Google Docs API is used for embedding through the site.

### Supported Platforms
Currently tested with the latest Google Chrome without issues.
It should work with modern browsers without an issue.

Not working on your platform? Make a new issue on GitHub.
