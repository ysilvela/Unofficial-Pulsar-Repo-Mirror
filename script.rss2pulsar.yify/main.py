# coding: utf-8
import re
import rss

# this read the settings
settings = rss.Settings()
# define the browser
browser = rss.Browser()

quality = settings.dialog.select('Quality:', ['720p', '1080p', '3D'])
sort = settings.dialog.select('Sorting by:', ['Popular', 'Year', 'Rating', 'Latest'])
number= settings.dialog.numeric(0, 'Number of Movies:', "50")
url_search = "https://yts.re/api/list.xml?limit=%s&quality=%s&sort=%s&order=desc" % (number, quality, sort)
print url_search
title = []
ID = []  # IMDB_ID or thetvdb ID
if browser.open(url_search):
    data = browser.content
    #magnet = re.findall('<TorrentHash>(.*?)</TorrentHash>',data)
    magnet = re.findall('<TorrentMagnetUrl>(.*?)</TorrentMagnetUrl>',data)
    name = re.findall('<MovieTitleClean>(.*?)</MovieTitleClean>', data)
    year = re.findall('<MovieYear>(.*?)</MovieYear>', data)
    for name1, year1 in zip(name, year):
        title.append(name1 + ' (' + year1 + ')')
# else:
#     provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
#     provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
#     results = []
rss.integration(title, magnet,'MOVIE', settings.movie_folder, message='YIFY')