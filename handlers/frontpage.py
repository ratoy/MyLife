import webapp2, datetime, random
from templates import get_template
from models.post import Post
from models.postcounter import PostCounter
from models.settings import Settings
from models.slug import Slug
from models.dailymail import DailyMail

class FrontPageHandler(webapp2.RequestHandler):
	def get(self):
		settings = Settings.get() #Force email address update...
		posts = Post.query().order(-Post.date).fetch(1)
		is_newest = True
		if posts:
			post = posts[0]
			is_oldest = post.date == Post.min_date()
		else:
			post = None
			is_oldest = True


		#See if this is the very first time we've been here. In that case
		#send an email immediately to get people started...
		first_time = False
		
		if not Slug.query().get() and not Post.query().get():
			first_time = True
			DailyMail().send(True)

		self.response.write(get_template('frontpage.html').render(
			{
				"page":"frontpage", 
				"post":post, 
				"is_oldest" : is_oldest,
				"is_newest" : is_newest,
				"first_time" : first_time,
				"email" : settings.email_address
			}))

class FrontPagePostHandler(webapp2.RequestHandler):
	def get(self, year, month, day, type):
		date = datetime.date(int(year), int(month), int(day))
		min_date, max_date = Post.min_date(), Post.max_date()
		if type == 'prev':
			posts = Post.query(Post.date < date).order(-Post.date).fetch(1)
		elif type == 'next':
			posts = Post.query(Post.date > date).order(Post.date).fetch(1)
		elif type == 'random':
			count = PostCounter.get().count
			posts = Post.query().fetch(1, offset=random.randint(0, count-1))

		post = None
		if posts:
			post = posts[0]

		self.response.write(get_template('frontpagepost.html').render(
			{
				"page":"frontpage", 
				"post":post,
				"is_newest":post.date == max_date,
				"is_oldest":post.date == min_date
			}))

