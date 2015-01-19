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
        #while self.movie_folder =='' and self.show_folder == '':
        while self.movie_folder == '':
            self.movie_folder = self.settings.getSetting('movie_folder')
            self.show_folder = self.settings.getSetting('show_folder')
            #if self.movie_folder == '' or self.show_folder == '':
            if self.movie_folder == '' :
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
def integration(title, magnet, type_list, folder, silence=False, message=''):
    import shelve

    dialog = xbmcgui.Dialog()
    action = xbmcaddon.Addon().getSetting('action')  # gets action
    library = xbmcaddon.Addon().getSetting('library')
    total = len(title)
    if total > 0:
        if not silence:
            answer = dialog.yesno('Pulsar list integration: %s items\nDo you want to subscribe this list?' % total, '%s' % title)
        else:
            answer = True
        if answer:
            pDialog = xbmcgui.DialogProgress()
            if not silence:
                pDialog.create('Pulsar list integration', 'Checking for %sS\n%s' % (type_list, message))
            else:
                dialog.notification('', 'Pulsar list integration\nChecking for %sS\n%s' % (type_list, message), xbmcgui.NOTIFICATION_INFO, 1000)
            cont = 0
            directory = ''
            for cm, name in enumerate(title):
                cont += 1
                name = name.replace(':', ' ')
                directory = folder + name + folder[-1]
                if not os.path.exists(directory):
                    os.makedirs(directory)
                #link = 'plugin://plugin.video.pulsar/play?uri=magnet:?xt=urn:btih:%s' % infohash[cm]
                link = 'plugin://plugin.video.pulsar/play?uri=%s' % magnet[cm]
                with open("%s%s.strm" % (directory, name), "w") as text_file:  # create .strm
                    text_file.write(link)
                if not silence: pDialog.update(int(float(cm) / total * 100), 'Creating %s%s.strm...' % (directory, name))
                if cont % 100 == 0:
                    dialog.notification('', 'Pulsar list integration\n%s %sS found - Still working...\n%s'
                                        % (cont, type_list, message), xbmcgui.NOTIFICATION_INFO, 1000)
                xbmc.log('%s%s.strm added' % (directory, name), xbmc.LOGINFO)
            pDialog.close()
            if cont > 0:
                xbmc.log('%s %sS added./n%s' % (cont, type_list, message), xbmc.LOGINFO)
                if not silence:
                    dialog.ok('Integration is done!!', '%s %sS added.\n%s\nYou need to update your library' % (cont, type_list, message))
                else:
                    dialog.notification('', 'Pulsar list integration\n%s %sS added.\n%s' % (cont, type_list, message), xbmcgui.NOTIFICATION_INFO, 1000)
            else:
                xbmc.log('[script.rss2pulsar] No new %sS\n%s' % (type_list, message))
                if not silence:
                    dialog.ok('Integration is done!!', 'No new %sS\n%s' % (type_list, message))
                else:
                    dialog.notification('', 'Pulsar list integration\nNo new %sS\n%s' % (type_list, message), xbmcgui.NOTIFICATION_INFO, 1000)
    else:
        xbmc.log('[script.rss2pulsar] Empty List')
        if not silence: dialog.ok('Empty List!!', 'Try another list number, please')