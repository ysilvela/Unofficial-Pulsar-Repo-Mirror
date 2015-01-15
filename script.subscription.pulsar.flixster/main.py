# coding: utf-8
import re
import subscription

# this read the settings
settings = subscription.Settings()
# define the browser
browser = subscription.Browser()

url_search = "http://www.flixster.com"
listing = []
ID = []  # IMDB_ID or thetvdb ID
if browser.open(url_search):
    data = browser.content
    data = data[data.find('Top DVD Rentals'):]  # narrow the file
    listing = re.findall('<div class="movie-title">(.*?)</div>',data)
# else:
#     provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
#     provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
#     results = []
subscription.integration(listing, ID,'MOVIE', settings.movie_folder)