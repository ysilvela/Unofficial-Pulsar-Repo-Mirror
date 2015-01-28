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


# Las siguientes funciones son invocadas desde Pulsar directamente
def extract_torrents(data, query):
    try:
        filters.information()  # Pintamos las opciones de filtrado en el log
        data = common.clean_html(data) # Elimina los comentarios que haya ('<!--(.*?)-->')
        cont = 0
        last_item = ''
        pattern = r'<a\shref=[\'"]?([^\'" >]+%s)' % query
        for cm,item in enumerate(re.findall(pattern, data)): #http://www.newpct1.com/descarga-torrent/pelicula/interstellar/
            if last_item != item or last_item='':
                next_url = item.replace(".com/",".com/descarga-torrent/") + "/"
                browser.open(next_url)
                provider.log.info('Next Url : ' + next_url)
                data_next = browser.content
                pattern_next = '<a href="([^"]+)" title="[^"]+" class="btn-torrent" target="_blank">'
                # Con el patron anterior obtengo <a href="http://tumejorjuego.com/download/index.php?link=descargar-torrent/058310_yo-frankenstein-blurayrip-ac3-51.html" title="Descargar torrent de Yo Frankenstein " class="btn-torrent" target="_blank">Descarga tu Archivo torrent!</a>

                link =re.findall(pattern_next,data_next)
                provider.log.info('Link : ' + link[0])
                partes = link[0].split("/")
                cadena = partes[ len(partes)-1 ]
                torrent = cadena.split("_")
                provider.log.info('Torrent : ' + torrent[0])
                cadena = torrent[1].split(".")
                titulo = cadena[0]
                provider.log.info('Titulo : ' + titulo)
        
                if filters.verify(titulo, None):
                    yield {"name": titulo + ' - ' + settings.name_provider, "uri": link[0]}  # devuelve el torrent
                    cont += 1
                else:
                    provider.log.warning(filters.reason)
                if cont == settings.max_magnets:  # limit magnets
                    break  
            last_item = item
        provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')
    except:
        provider.log.error('>>>>>>>ERROR parsing data from newpct1<<<<<<<')
        provider.notify(message='ERROR parsing data', header=None, time=5000, image=settings.icon)


def search(query):
    global filters
    filters.title = query  # to do filtering by name
    query += ' ' + settings.extra
    if settings.time_noti > 0: provider.notify(message="Searching: " + query.encode('utf-8','ignore').title() + '...', header=None, time=settings.time_noti, image=settings.icon)
    query = provider.quote_plus(query.lstrip())
    url_search = "%s/buscar/index.php?page=buscar&q=%s&ordenar=Nombre&inon=Ascendente" % (settings.url,query)
    provider.log.info(url_search)
    if browser.open(url_search):
        results = extract_torrents(browser.content, query)
    else:
        provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
        provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
        results = []
    return results


def search_movie(info):
    filters.use_movie()
    query = common.translator(info['imdb_id'], 'es') #define query in spanish
    provider.log.error('Query extracted using IMDB: %s' % query)
    return search(query)


def search_episode(info):
    filters.use_TV()
    query =  common.clean(info['title']) + ' %dx%02d'% (info['season'],info['episode'])  # define query
    return search(query)

# Hay que registar el modulo para poderlo usar
provider.register(search, search_movie, search_episode)
