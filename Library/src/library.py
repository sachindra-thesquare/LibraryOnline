from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template


class LibraryModel(ndb.Model):
    author      = ndb.UserProperty(required=True)
    bookname = ndb.StringProperty(required=True)
    bookid = ndb.StringProperty(required=True)
    issuedate = ndb.StringProperty(required=True)
    duedate = ndb.StringProperty(required=True)
    bookauthor = ndb.StringProperty(required=True)
    status = ndb.StringProperty(required=False)
    finished         = ndb.BooleanProperty()

nobooks=0
# The main page where the user can login and logout
# MainPage is a subclass of webapp.RequestHandler and overwrites the get method
class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
                    
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
# GQL is similar to SQL             
        books = LibraryModel.gql("WHERE author = :author and finished=false",
               author=users.get_current_user())
        global nobooks
        
        values = {
            'books': books,
            'numberbooks' : books.count(),
            'nbook' : books.count()-nobooks,
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
        }
        self.response.out.write(template.render('index.html', values))



# This class creates a new book issue model
class New(webapp.RequestHandler):
    def post(self):
        book = LibraryModel(author  = users.get_current_user(),
                bookname= self.request.get('bookname'),
                bookid = self.request.get('bookid'),
		bookauthor= self.request.get('bookauthor'),
                issuedate = self.request.get('issuedate'),
		duedate = self.request.get('duedate'),
		status = 'Issued',
		finished = False)
        book.put();
        self.redirect('/')  
 
class Done(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            raw_id = self.request.get('id')
            Id = int(raw_id)
            book = LibraryModel.get_by_id(Id)
        book.status='Returned'
        global nobooks
        nobooks=nobooks+1
        book.put()	    
        self.redirect('/')
       
# Register the URL with the responsible classes


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/new', New), ('/done', Done)],
                                     debug=True)

# Register the wsgi application to run
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main() 
