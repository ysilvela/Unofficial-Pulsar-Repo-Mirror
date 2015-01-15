# coding: utf-8
import re
import subscription

# this read the settings
settings = subscription.Settings()
# define the browser
browser = subscription.Browser()

list = settings.dialog.input('www.listal.com/list/', 'listals-100-films-see-before-3479')
if list != '':
    url_search = "http://www.listal.com/list/%s" % list
    listing = []
    ID = []  # IMDB_ID or thetvdb ID
    if browser.open(url_search):
        data = browser.content
        data = data.replace('</a></span>', '')
        for line in re.findall("style='font-weight:bold;font-size:110%;'>(.*?)>(.*?)</div>",data, re.S):
            listing.append(line[1].replace('\r', '').replace('\n', '').replace('\t', ''))
    else:
        print '[script.subscription.pulsar] %s' % browser.status
        settings.dialog.notification('Pulsar List integration',browser.status, settings.icon, 5000)
    subscription.integration(listing, ID,'MOVIE', settings.movie_folder)
else:
    settings.dialog.ok('Pulsar IMDB List','Empty List! Nothing added.')