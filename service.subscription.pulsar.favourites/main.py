# coding: utf-8
import subscription
import xml.etree.ElementTree as ET
import re
import time
import xbmc
import json

# this read the settings of add on
settings = subscription.Settings()
path = xbmc.translatePath('special://userdata')
tree = ET.parse("%sfavourites.xml" % path)
root = tree.getroot()

# check movies
listing = []
ID = []
for child in root:
    data = child.text
    if 'plugin://plugin.video.pulsar/movie/' in data:
        listing.append(child.attrib['name'])
        ID.append(re.search('plugin://plugin.video.pulsar/movie/(.*?)/', data).group(1))
if len(listing) > 0:
    subscription.integration(listing, ID,'MOVIE', settings.movie_folder, True)


# check movies sections
listing = []
ID = []
browser = subscription.Browser()
for child in root:
    data = child.text.replace('"plugin://plugin.video.pulsar/movies/"', '')  # remove movies root
    if 'plugin://plugin.video.pulsar/movies/' in data:
        section = re.search('plugin://plugin.video.pulsar/movies/(.*?)"', data).group(1)
        # get the list of movies
        browser.open('http://localhost:65251/movies/%s' % section)
        data = json.loads(browser.content)
        for item in data['items']:
            if 'title' in item['info'] and item['info'].has_key('code'):
                listing.append(item['info']['title'].encode('ascii', 'ignore') + ' ' + str(item['info']['year']))
                ID.append(item['info']['code'])
if len(listing) > 0:
    subscription.integration(listing, ID,'MOVIE', settings.movie_folder, True)


# check tv shows
listing = []
ID = []
for child in root:
    data = child.text
    if 'plugin://plugin.video.pulsar/show/' in data:
        listing.append(child.attrib['name'])
        ID.append(re.search('plugin://plugin.video.pulsar/show/(.*?)/', data).group(1))
if len(listing) > 0:
    subscription.integration(listing, ID,'SHOW', settings.show_folder, True)