# library to access URL, translation title and filtering
__author__ = 'mancuniancol'
import re 
import xbmcaddon
import xbmc
import xbmcgui
import os
import time

class Settings:
    def __init__(self):
        import shelve
        self.dialog = xbmcgui.Dialog()
        self.settings = xbmcaddon.Addon()
        self.id_addon = self.settings.getAddonInfo('id')  # gets name
        self.icon = self.settings.getAddonInfo('icon')
        self.name_provider = self.settings.getAddonInfo('name')  # gets name
        self.name_provider = re.sub('.COLOR (.*?)]', '', self.name_provider.replace('[/COLOR]', ''))
        type_library = self.settings.getSetting('type_library')
        if "Local"in type_library:
            self.settings.setSetting('library', self.name_provider)
        else:
            self.settings.setSetting('library', 'global')
        self.movie_folder = ''
        self.show_folder = ''
        while self.movie_folder =='' and self.show_folder == '':
            self.movie_folder = self.settings.getSetting('movie_folder')
            self.show_folder = self.settings.getSetting('show_folder')
            if self.movie_folder == '' or self.show_folder == '':
                self.dialog.ok('Subscription Pulsar list', 'Movie or show fold cannot be empty!')
                self.settings.openSettings()
        # remove .strm
        self.remove_strm = self.settings.getSetting('remove_strm')
        self.library = self.settings.getSetting('library')
        if self.remove_strm == 'true':
                import shelve
                self.dialog.notification('Subscription Pulsar list', 'Removing .strm files...', self.icon, 1000)
                path = xbmc.translatePath('special://temp')
                database = shelve.open(path + 'pulsar-subscription-%s.db' % self.library)
                for item in database:
                    data = database[item]
                    if os.path.exists(data['path']):
                        if '.strm' in data['path']:
                                os.remove(data['path'])
                        else:
                            files = os.listdir(data['path'])
                            for file in files:
                                if '.strm' in file and os.path.exists(data['path'] + file):
                                    os.remove(data['path'] + file)
                xbmc.log('All .strm files removed!', xbmc.LOGINFO)
                self.dialog.notification('Subscription Pulsar list', 'All .strm files removed!', self.icon, 1000)
                self.settings.setSetting('remove_strm', 'false')
        # clear the database
        self.clear_database = self.settings.getSetting('clear_database')
        if self.clear_database == 'true':
            self.dialog.notification('Subscription Pulsar list', 'Erasing Database...', self.icon, 1000)
            path = xbmc.translatePath('special://temp')
            database = shelve.open(path + 'pulsar-subscription-%s.db' % self.library)
            database.clear()
            database.close()
            self.settings.setSetting('clear_database', 'false')
        # rest
        self.number_files = int('0%s' % self.settings.getSetting('number_files'))
        self.dialog = xbmcgui.Dialog()

class Browser:
    def __init__(self):
        import cookielib
        self._cookies = None
        self.cookies = cookielib.LWPCookieJar()
        self.content = None
        self.status = None

    def create_cookies(self, payload):
        import urllib
        self._cookies = urllib.urlencode(payload)

    def open(self,url):
        import urllib2
        result = True
        if self._cookies is not None:
            req = urllib2.Request(url,self._cookies)
            self._cookies = None
        else:
            req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36')
        req.add_header("Accept-Encoding", "gzip")
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))#open cookie jar
        try:
            response = opener.open(req)  # send cookies and open url
            #borrow from provider.py Steeve
            if response.headers.get("Content-Encoding", "") == "gzip":
                import zlib
                self.content = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(response.read())
            else:
                self.content = response.read()
            response.close()
            self.status = 200
        except urllib2.URLError as e:
            self.status = e.reason
            result = False
        except urllib2.HTTPError as e:
            self.status = e.code
            result = False
        return result

    def login(self, url, payload, word):
        result = False
        self.create_cookies(payload)
        if self.open(url):
            result = True
            data = self.content
            if word in data:
                self.status = 'Wrong Username or Password'
                result = False
        return result


# find the name in different language
def translator(imdb_id, language):
    import unicodedata
    import json
    browser1 = Browser()
    keywords = {'en': '', 'de': '', 'es': 'espa', 'fr': 'french', 'it': 'italian', 'pt': 'portug'}
    url_themoviedb = "http://api.themoviedb.org/3/find/%s?api_key=8d0e4dca86c779f4157fc2c469c372ca&language=%s&external_source=imdb_id" % (imdb_id, language)
    if browser1.open(url_themoviedb):
        movie = json.loads(browser1.content)
        title0 = movie['movie_results'][0]['title'].replace(u'\xf1', '*')
        title_normalize = unicodedata.normalize('NFKD', title0)
        title = title_normalize.encode('ascii', 'ignore').replace(':', '')
        title = title.decode('utf-8').replace('*', u'\xf1').encode('utf-8')
        original_title = movie['movie_results'][0]['original_title']
        if title == original_title:
            title += ' ' + keywords[language]
    else:
        title = 'Pas de communication avec le themoviedb.org'
    return title.rstrip()


class TV_Show():
    def __init__(self, name):
        import json
        import urllib

        browser = Browser()
        if browser.open('http://localhost:65251/shows/search?q=%s' % urllib.quote(name)):
            data = json.loads(browser.content)
            if len(data['items']) > 0:
                self.code = data['items'][0]['path'].replace('plugin://plugin.video.pulsar/show/','').replace('/seasons','')
                time.sleep(0.002)
                browser.open('http://localhost:65251/show/%s/seasons' % self.code)
                data = json.loads(browser.content)
                seasons =[]
                for item in data['items']:
                    seasons.append(int(item['label'].replace('Season ','').replace('Specials', '0')))
                seasons.sort()
                episodes = {}
                for season in seasons:
                    time.sleep(0.002)
                    browser.open('http://localhost:65251/show/%s/season/%s/episodes' % (self.code, season))
                    data = json.loads(browser.content)
                    episodes[season] = len(data['items'])
                if len(seasons) > 0:
                    self.first_season = seasons[0]
                    self.last_season = seasons[-1]
                else:
                    self.first_season = 0
                    self.last_season = 0
                self.last_episode = episodes
            else:
                self.code = None
        else:
            self.code =None
        del browser

class TV_Show_code():
    def __init__(self, code, episodes = {}, last_season=0):
        import json
        import urllib
        browser = Browser()
        self.code = code
        browser.open('http://localhost:65251/show/%s/seasons' % self.code)
        data = json.loads(browser.content)
        seasons =[]
        for item in data['items']:
            seasons.append(int(item['label'].replace('Season ','').replace('Specials', '0')))
        seasons.sort()
        if episodes.has_key(0):
            del episodes[0]
        if last_season is not 0:
            del episodes[last_season]
        for season in seasons:
            if not episodes.has_key(season):
                time.sleep(0.002)
                browser.open('http://localhost:65251/show/%s/season/%s/episodes' % (self.code, season))
                data = json.loads(browser.content)
                episodes[season] = len(data['items'])
        if len(seasons) > 0:
            self.first_season = seasons[0]
            self.last_season = seasons[-1]
        else:
            self.first_season = 0
            self.last_season = 0
        self.last_episode = episodes
        del browser


class Movie():
    def __init__(self, name):
        import json
        import urllib

        if ')' in name and '(' in name:
            try:
                year_movie = int(name[name.find("(")+1:name.find(")")])
                name = name.replace('(%s)' % year_movie, '').rstrip()
            except:
                year_movie = None
        else:
            year_movie = None
        browser = Browser()
        time.sleep(0.002)
        if browser.open('http://localhost:65251/movies/search?q=%s' % urllib.quote(name)):
            data = json.loads(browser.content)
            if len(data['items']) > 0:
                if year_movie is not None:
                    for movie in data['items']:
                        label = movie['label']
                        path = movie['path']
                        if movie['info'].has_key('year'):
                            year = movie['info']['year']
                        else:
                            year = 0000
                        if year == year_movie:
                            break
                else:
                    label = data['items'][0]['label']
                    path = data['items'][0]['path']
                    year = data['items'][0]['info']['year']
                self.code = path.replace('plugin://plugin.video.pulsar/movie/', '').replace('/play', '')
                self.label = label
            else:
                self.code = None
                self.label = name
        else:
            self.code = None
            self.label = name
        del browser


def integration(listing, ID, type_list, folder, silence=False, message=''):
    import shelve

    dialog = xbmcgui.Dialog()
    action = xbmcaddon.Addon().getSetting('action')  # gets action
    specials = xbmcaddon.Addon().getSetting('specials')  # gets action
    detailed_log = xbmcaddon.Addon().getSetting('detailed_log')
    library = xbmcaddon.Addon().getSetting('library')
    total = len(listing)
    if total > 0:
        if not silence:
            answer = dialog.yesno('Pulsar list integration: %s items\nDo you want to subscribe this list?' % total, '%s' % listing)
        else:
            answer = True
        if answer:
            pDialog = xbmcgui.DialogProgress()
            if not silence:
                pDialog.create('Pulsar list integration', 'Checking for %sS\n%s' % (type_list, message))
            else:
                dialog.notification('', 'Pulsar list integration\nChecking for %sS\n%s' % (type_list, message), xbmcgui.NOTIFICATION_INFO, 1000)
            path = xbmc.translatePath('special://temp')
            database = shelve.open(path + 'pulsar-subscription-%s.db' % library)
            cont = 0
            directory = ''
            for cm, item in enumerate(listing):
                item = ' '.join(item.split()).replace(':', '').replace('/', '-')
                if database.has_key(item):
                    data = database[item]
                    if type_list == 'SHOW':  # update the database to find new episodes
                        tv_show = TV_Show_code(ID[cm], data['last_episode'], data['last_season'])
                        data['first_season'] = tv_show.first_season
                        data['last_season'] = tv_show.last_season
                        data['last_episode'] = tv_show.last_episode
                else:
                    # create the item
                    data = {}
                    if len(ID)> 0:
                        data['ID'] = ID[cm]
                        if type_list == 'SHOW':
                            tv_show = TV_Show_code(ID[cm])
                            data['first_season'] = tv_show.first_season
                            data['last_season'] = tv_show.last_season
                            data['last_episode'] = tv_show.last_episode
                    else:
                        if type_list == 'MOVIE':
                            movie = Movie(item)  # name of the movie with (year) format: Frozen (2013)
                            data['ID'] = movie.code  # search the IMDB id
                        elif type_list == 'SHOW':
                            tv_show = TV_Show(item)
                            data['ID'] = tv_show.code
                            if data['ID'] is not None:
                                data['first_season'] = tv_show.first_season
                                data['last_season'] = tv_show.last_season
                                data['last_episode'] = tv_show.last_episode
                    data['type'] = type_list
                    data['season'] = 0
                    data['episode'] = 0
                if type_list == 'MOVIE' and data['type'] == 'MOVIE' and data['episode'] == 0 and data['ID'] is not None:  # add movies
                    cont += 1
                    directory = folder + item + folder[-1]
                    data['path'] = directory
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    if detailed_log == 'true':
                        xbmc.log('[service.subscription] Code %s=%s' % (type_list, data['ID']))
                    link = 'plugin://plugin.video.pulsar/movie/%s/%s' % (data['ID'], action)
                    with open("%s%s.strm" % (directory, item), "w") as text_file:  # create .strm
                        text_file.write(link)
                    data['path'] = '%s%s.strm' % (directory, item)
                    data['episode'] = 1
                    if not silence: pDialog.update(int(float(cm) / total * 100), 'Creating %s%s.strm...' % (directory, item))
                    if cont % 100 == 0:
                        dialog.notification('', 'Pulsar list integration\n%s %sS found - Still working...\n%s'
                                            % (cont, type_list, message), xbmcgui.NOTIFICATION_INFO, 1000)
                    xbmc.log('%s%s.strm added' % (directory, item), xbmc.LOGINFO)
                elif type_list == 'SHOW' and data['type'] == 'SHOW' and data['ID'] is not None:  # add shows
                    if specials == 'false' and data['first_season'] == 0:
                        data['first_season'] = 1
                    directory = folder + item + folder[-1]
                    data['path'] = directory
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    if detailed_log == 'true':
                        xbmc.log('[service.subscription] Code %s=%s\n%s' % (type_list, data['ID'], message))
                        xbmc.log('[service.subscription] %s %s-%s: %s' % ( item, data['first_season'], data['last_season'], data['last_episode']))
                    for season in range(max(data['season'], data['first_season']), data['last_season'] + 1):
                        for episode in range(data['episode'] + 1, data['last_episode'][season] + 1):
                            cont += 1
                            link = 'plugin://plugin.video.pulsar/show/%s/season/%s/episode/%s/%s' % (data['ID'], season, episode, action)
                            if not silence: pDialog.update(int(float(cm) / total * 100), "%s%s S%02dE%02d.strm" % (directory, item, season, episode))
                            if cont % 100 == 0:
                                dialog.notification('', 'Pulsar list integration\n%s %sS found - Still working...\n%s'
                                                    % (cont, type_list, message), xbmcgui.NOTIFICATION_INFO, 1000)
                            with open("%s%s S%02dE%02d.strm" % (directory, item, season, episode), "w") as text_file:  # create .strm
                                text_file.write(link)
                                xbmc.log('[service.subscription] %s S%02dE%02d.strm added' % (item, season, episode))
                                if not silence:
                                    if pDialog.iscanceled():
                                        break
                        data['episode'] = 0 # change to new season and reset the episode to 1
                        if not silence:
                            if pDialog.iscanceled():
                                break
                    data['season'] = data['last_season']
                    data['episode'] = data['last_episode'][data['last_season']]
                    if not silence: pDialog.update(int(float(cm) / total * 100), 'Creating %s%s.strm...' % (directory, item))
                    xbmc.log('%s%s.strm added' % (directory, item), xbmc.LOGINFO)
                # update database
                if data['ID'] is not None:
                    database[item] = data
                    database.sync()
                if not silence:
                    if pDialog.iscanceled():
                        break
            # confirmation and close database
            database.close()
            pDialog.close()
            del pDialog
            if cont > 0:
                xbmc.log('%s %sS added./n%s' % (cont, type_list, message), xbmc.LOGINFO)
                if not silence:
                    dialog.ok('Integration is done!!', '%s %sS added.\n%s\nYou need to update your library' % (cont, type_list, message))
                else:
                    dialog.notification('', 'Pulsar list integration\n%s %sS added.\n%s' % (cont, type_list, message), xbmcgui.NOTIFICATION_INFO, 1000)
            else:
                xbmc.log('[service.subscription] No new %sS\n%s' % (type_list, message))
                if not silence:
                    dialog.ok('Integration is done!!', 'No new %sS\n%s' % (type_list, message))
                else:
                    dialog.notification('', 'Pulsar list integration\nNo new %sS\n%s' % (type_list, message), xbmcgui.NOTIFICATION_INFO, 1000)
    else:
        xbmc.log('[service.subscription] Empty List')
        if not silence: dialog.ok('Empty List!!', 'Try another list number, please')
    del dialog


class parseXML():
    def __init__(self, data):
        self.listing = []
        self.magnet = []
        self.ID = []
        items = re.findall('<item>(.*?)</item>', data, re.S)
        for item in items:
            title = re.findall('<title>(.*?)</title>', item)
            if title is not []:
                self.listing.append(title[0])
                # the rest inside
                imdb = re.findall('www.imdb.com/title/(.*?)/', item)
                imdb.append('')
                self.ID.append(imdb[0])

