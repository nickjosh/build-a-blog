
import webapp2
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

class MainHandler(Handler):
    def get(self):
        self.redirect("/blog")


class MainPage(Handler):
    def render_front(self, subject="", content="", error="", article=""):
        article = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5 OFFSET 0")
        self.render("front.html", subject=subject, content=content, error=error, article=article)

    def get(self):
        self.render_front()
        #self.render("newpost.html")

class NewPost(Handler):
    def get(self):
        self.render("newpost.html")
        #self.response.write(response)

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            a = Blog(subject = subject, content = content)
            a.put()

            number=a.key().id()

            #redirect sends browser to the url in the parenthesis
            string="/blog/{0}".format(number)

            self.redirect(string)

        else:
            error = "we need both subject and content"
            self.render("newpost.html", subject=subject, content=content, error=error)

class ViewPostHandler(Handler):
    def get(self, id):

        post = Blog.get_by_id(int(id))

        if not post:
            self.error(404)
            return
        self.render("post.html", post=post)
        #self.render("permalink.html", post=post)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', MainPage),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
    #('/blog/postpage', PostPage),
    #('/blog/<id:\d+>', ViewPostHandler)
    ], debug=True)
     #webapp2.Route('/blog/<id:\d+>', ViewPostHandler)#('/blog/?', BlogFront),
