# coding: utf-8
from pulsar import provider
from urllib import unquote_plus
import re
import common

# this read the settings
settings = common.Settings()
# define the browser
browser = common.Browser()
# create the filters
filters = common.Filtering()

#define dictionary for lang
lang_id = {'Any': '0', 'English': '2', 'Albanian': '42', 'Arabic': '7', 'Basque': '44', 'Brazilian': '39',
           'Bulgarian': '37', 'Cantonese': '45', 'Chinese': '10', 'Croatian': '34', 'Czech': '32', 'Danish': '26',
           'Dutch': '8', 'Filipino': '11', 'Finnish': '31',
           'French': '5', 'German': '4', 'Greek': '30', 'Hebrew': '25', 'Hindi': '6', 'Hungarian': '27', 'Italian': '3',
           'Japanese': '15', 'Korean': '16',
           'Lithuanian': '43', 'Malayalam': '21', 'Mandarin': '23', 'Norwegian': '19', 'Persian': '33', 'Polish': '9',
           'Portuguese': '17', 'Punjabi': '35',
           'Romanian': '18', 'Russian': '12', 'Serbian': '28', 'Slovenian': '36', 'Spanish (Latin America)': '41',
           'Spanish (Spain)': '14',
           'Swedish': '20', 'Tamil': '13', 'Telugu': '22', 'Thai': '24', 'Turkish': '29', 'Ukrainian': '40',
           'Vietnamese': '38', 'en': '0'}


# using function from Steeve to add Provider's name and search torrent
def extract_magnets(data):
    try:
        filters.information()  # print filters settings
        data = common.clean_html(data)
        size = re.findall('class="nobr center">(.*?)B', data)  # list the size
        cont = 0
        for cm, magnet in enumerate(re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data)):
            name = re.search('dn=(.*?)&tr=',magnet).group(1)  # find name in the magnet
            name = unquote_plus(name).replace('.', ' ').title() + ' - ' + size[cm].replace('<span>', '') + 'B' + ' - ' + settings.name_provider
            if filters.verify(name, size[cm].replace('<span>', ' ')):
                    yield {"name": name, "uri": magnet}  # return le torrent
                    cont += 1
            else:
                provider.log.warning(filters.reason)
            if cont == settings.max_magnets:  # limit magnets
                break
        provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')
    except:
        provider.log.error('>>>>>>>ERROR parsing data<<<<<<<')
        provider.notify(message='ERROR parsing data', header=None, time=5000, image=settings.icon)


def search(query):
    global filters
    filters.title = query  # to do filtering by name
    query += ' ' + settings.extra
    query = query.rstrip()
    if settings.time_noti > 0: provider.notify(message="Searching: " + query.title() + '...', header=None, time=settings.time_noti, image=settings.icon)
    query += ' lang_id:%s' % lang_id[settings.language] # add code of language
    url_search = "%s/usearch/%s/?field=seeders&sorder=desc" % (settings.url,query.replace(' ','%20'))  # change in each provider
    provider.log.info(url_search)
    if browser.open(url_search):
        results = extract_magnets(browser.content)
    else:
        provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
        provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
        results = []
    return results


def search_movie(info):
    filters.use_movie()
    query = info['title'] + ' ' + str(info['year'])
    return search(query)


def search_episode(info):
    filters.use_TV()
    if info['absolute_number'] == 0:
        query =  info['title'] + ' s%02de%02d'% (info['season'], info['episode'])  # define query
    else:
        query =  info['title'] + ' %02d' % info['absolute_number']  # define query anime
    return search(query)

# This registers your module for use
provider.register(search, search_movie, search_episode)