# coding: utf-8
import re
import subscription

# this read the settings
settings = subscription.Settings()
# define the browser
browser = subscription.Browser()

categories = {'Movies Popular': 'http://trakt.tv/movies/popular',
              'Movies Trending': 'http://trakt.tv/movies/trending',
              'TV Popular': 'http://trakt.tv/shows/popular',
              'TV trending': 'http://trakt.tv/shows/trending'
              }
options = categories.keys()
options.sort()
ret = settings.dialog.select('Choose a category:', options)
url_search = categories[options[ret]]
listing = []
ID = []  # IMDB_ID or thetvdb ID
if browser.open(url_search):
    data = browser.content
    if options[ret] == 'Movies Popular' or options[ret] == 'Movies Trending':
        items = re.findall('data-type="movie" data-url="http://trakt.tv/movies/(.*?)"',data)
        listing = [item[:-4].replace('-', ' ') + ' (' + item[-4:] + ')' for item in items]
        subscription.integration(listing, ID, 'MOVIE', settings.movie_folder)
    else:
        items = re.findall('data-type="show" data-url="http://trakt.tv/shows/(.*?)"',data)
        listing = [item.replace('-', ' ') for item in items]
        subscription.integration(listing, ID, 'SHOW', settings.show_folder)
# else:
#     provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
#     provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
#     results = []
