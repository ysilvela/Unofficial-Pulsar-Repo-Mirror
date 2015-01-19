from pulsar import provider
import re

# this read the settings
url = provider.ADDON.getSetting('url_address') # url address 
icon = provider.ADDON.getAddonInfo('icon') # gets icon
movies_quality = provider.ADDON.getSetting('movies_quality')
TV_quality = provider.ADDON.getSetting('TV_quality')
name_provider = provider.ADDON.getAddonInfo('name') # gets name
extra = provider.ADDON.getSetting('extra')	# additional info to the query
time_noti = int(provider.ADDON.getSetting('time_noti'))
values3 = {'Tous': 0, 'Films': 0, 'Series': 0, 'Series French': 0,'Series VOSTFR': 0,'Films French': 0, 'Films VOSTFR' : 0, 'Films DVDRIP': 1, 'Films 720p': 2 ,'Films 1080p': 3, "1440p": 4 ,"2K": 5,"4K": 5} #code_resolution steeve
values_recherche = {'Tous': '/', 'Films': '/films/', 'Series': '/series/', 'Series French': '/series-francaise/','Series VOSTFR': '/series-vostfr/','Films French': '/films-french/', 'Films VOSTFR' : '/films-vostfr/',  'Films DVDRIP': '/films-dvdrip/', 'Films 720p': '/720p/' ,'Films 1080p': '/1080p/'}
max_magnets = int(provider.ADDON.getSetting('max_magnets'))  #max_magnets

# find the name in different language
def translator(imdb_id,language):
	import unicodedata
	url_themoviedb = "http://api.themoviedb.org/3/find/%s?api_key=8d0e4dca86c779f4157fc2c469c372ca&language=%s&external_source=imdb_id" % (imdb_id, language)
	response = provider.GET(url_themoviedb)
	if response != (None, None):
		movie = provider.parse_json(response.data)
		title_normalize = unicodedata.normalize('NFKD', movie['movie_results'][0]['title'])
		title = ''.join (c for c in title_normalize if (not unicodedata.combining(c)))
		print movie['movie_results'][0]['title'].encode('ascii', 'ignore'),title
	else:
		title = 'Pas de communication avec le themoviedb.org' 
	provider.log.info(title)
	return title
	
# clean_html
def clean_html(data):
	lines = re.findall('<!--(.*?)-->',data)
	for line in lines:
		data = data.replace(line,'')
	return data

# using function from Steeve to add Provider's name and search torrent
def extract_torrents(data, code_resolution):
	data = clean_html(data)
	size = re.findall(r'class="poid">(.*?)<',data) # find all sizes
	print(size)
	cont = 0
	for cm, torrent in  enumerate(re.findall(r'<div class="ligne."><a href="http://(.*?)/(.*?)/(.*?)/(.*?)/(.*?).html"', data)):
		print(torrent)
		name = torrent[4].replace('-',' ')
		print(name)
		torrent = url + '/telecharge/' + torrent[4] + '.torrent'  # create torrent to send Pulsar
		yield {"name": name.title() + ' - ' + size[cm].replace('&nbsp;',' ') + ' - ' + name_provider, "uri": torrent, 'resolution': code_resolution}
		cont = cm
		if cont == max_magnets: #limit torrents
			break
	provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')

def clean(title):
	title = title.replace('s h i e l d','s.h.i.e.l.d')
	title = title.replace(' s ','s ')
	return title
	
def search(query):
	query+= ' ' + extra
	if time_noti > 0 : provider.notify(message="Searching: " + query + '...', header=None, time=time_noti, image=icon)
	query = query.replace(' ', '-')
	url_search = "%s/recherche/%s.html,trie-seeds-d" % (url,query)
	provider.log.info(url_search)
	response = provider.GET(url_search)
	return extract_torrents(response.data, 0)

def search_movie(info):
	#define query and quality
	query = translator(info['imdb_id'], 'fr')
	if time_noti > 0 : provider.notify(message="Searching in " + movies_quality + ' : ' + query + ' ' + extra + '...', header=None, time=time_noti, image=icon)
	query +=  extra
	query = query.replace(' ', '-')  # starting the query
	url_search = "%s/recherche%s%s.html,trie-seeds-d" % (url,values_recherche[movies_quality],query)
	provider.log.info(url_search)
	response = provider.GET(url_search)
	return extract_torrents(response.data, values3[movies_quality])

def search_episode(info):
	#define query and quality
	query =  clean(info['title']) + ' S%02dE%02d '% (info['season'],info['episode'])
	if time_noti > 0 : provider.notify(message="Searching in " + TV_quality + ' : ' + query  + ' ' + extra +  '...', header=None, time=time_noti, image=icon)
	query +=  extra
	query = query.replace(' ', '-')  # starting the query
	url_search = "%s/recherche%s%s.html,trie-seeds-d" % (url,values_recherche[TV_quality],query)
	provider.log.info(url_search)
	response = provider.GET(url_search)
	return extract_torrents(response.data, values3[TV_quality])

# This registers your module for use
provider.register(search, search_movie, search_episode)