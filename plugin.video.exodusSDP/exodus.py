# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 Exodus

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import os,urlparse,sys,base64

from resources.lib.modules import control

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')

name = params.get('name')

title = params.get('title')

year = params.get('year')

imdb = params.get('imdb')

tvdb = params.get('tvdb')

tmdb = params.get('tmdb')

tvrage = params.get('tvrage')

season = params.get('season')

episode = params.get('episode')

tvshowtitle = params.get('tvshowtitle')

premiered = params.get('premiered')

url = params.get('url')

image = params.get('image')

meta = params.get('meta')

select = params.get('select')

query = params.get('query')

source = params.get('source')

content = params.get('content')


if action == None:
    from resources.lib.indexers import navigator
    navigator.navigator().root()

elif action == 'movieNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().movies()

elif action == 'movieliteNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().movies(lite=True)

elif action == 'mymovieNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().mymovies()

elif action == 'mymovieliteNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().mymovies(lite=True)

elif action == 'tvNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().tvshows()

elif action == 'tvliteNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().tvshows(lite=True)

elif action == 'mytvNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().mytvshows()

elif action == 'mytvliteNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().mytvshows(lite=True)

elif action == 'downloadNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().downloads()

elif action == 'toolNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().tools()

elif action == 'searchNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().search()

elif action == 'viewsNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().views()

elif action == 'clearCache':
    from resources.lib.indexers import navigator
    navigator.navigator().clearCache()

elif action == 'movies':
    from resources.lib.indexers import movies
    movies.movies().get(url)
    
##############################################
elif action == 'searchSDPNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().searchSDP()

elif action == 'movieSDPSearch':
    from resources.lib.indexers import moviesPall
    moviesPall.movies().searchSDP()

elif action == 'tvSDPSearch':
    from resources.lib.indexers import tvshowsPall
    tvshowsPall.tvshows().searchSDP()
    
elif action == 'moviesP':
    from resources.lib.indexers import moviesP
    moviesP.movies().get(url)

elif action == 'moviePageP':
    from resources.lib.indexers import moviesP
    moviesP.movies().get(url)

elif action == 'moviesPall':
    
    API_SITE = base64.urlsafe_b64decode('aHR0cDovL215YXBpbXAudGsvYXBpLw==')
    if 'animacao' in url:
        SDPlinks = ['http://www.filmesportuguesesonline.com/search/label/Animação',
                    'http://ratotv.win/tags/Animação/page/1/',
                    'http://toppt.net/category/animacao/',
                    'http://cinematugahd.net/category/animation/',
                    'http://tugaflix.com/Filmes?T=&G=Anima%C3%A7%C3%A3o&O=1&P=1',
                    'http://tugafree.com/category/filmes/animacao/page/1',
                    'http://www.redcouch.xyz/animacao/page/1',
                    'http://www.moviefree.eu/category/animation/page/1',
                    'http://movi3center.net/filmes/animacao/page/1',
                    'http://movi3center.net/filmes/animacao-em-portugues/page/1',
                    'http://www.filmeshare.net/category/animacao/page/1',
                    'http://vizer.tv/movies-category-animation/page/0',
                    #'http://lausse.blogspot.pt/search/label/Anima%C3%A7%C3%A3o',
                    API_SITE+'filmes/categoria/14']
    else:
        SDPlinks = ['http://www.filmesportuguesesonline.com/',
                    'http://ratotv.win/movies',
                    'http://toppt.net/category/filmes/',
                    'http://cinematugahd.net',
                    'http://tugaflix.com/Filmes?T=&G=&O=1&P=1',
                    'http://tugafree.com/category/filmes/page/1',
                    'http://www.redcouch.xyz/filmes/page/1',
                    'http://www.moviefree.eu/48-2/page/1',
                    'http://movi3center.net/page/1',
                    'http://www.filmeshare.net/filmes/page/1',
                    'http://sembilhete.ga/movies/1',
                    'http://vizer.tv/movies/page/0',
                    API_SITE+'filmes']
    if 'SDPtodos' not in url:
        file = open(control.dataPath+'filmes.txt', 'w')                
        for link in SDPlinks:
            if 'animacaopt' in url and 'animacao-em-portugues' in link:
                file.write(str(link)+os.linesep)
                break
            elif url.replace('animacao','') in link:
                file.write(str(link)+os.linesep)
                break
        file.close()
    else:
        file = open(control.dataPath+'filmes.txt', 'w')                
        for link in SDPlinks:
            file.write(str(link)+os.linesep)                
        file.close()
        
    from resources.lib.indexers import moviesPall
    moviesPall.movies().get(url)

elif action == 'tvshowsPall':
    
    API_SITE = base64.urlsafe_b64decode('aHR0cDovL215YXBpbXAudGsvYXBpLw==')
    if 'animacao' in url:
        SDPlinks = [#'http://www.filmesportuguesesonline.com/',
                    'http://ratotv.win/movies',
                    'http://toppt.net/category/series/animacao/',
                    #'http://cinematugahd.net/category/animation/',
                    'http://tugaflix.com/Series?T=&G=Anima%C3%A7%C3%A3o&O=1&P=1',
                    #'http://tugafree.com/category/series/animacao/page/1',
                    #'http://www.redcouch.xyz/animacao/page/1',
                    'http://www.moviefree.eu/tvshows-genre/animation/page/1',
                    #'http://movi3center.net/series/animacao/page/1',
                    'http://www.filmeshare.net/tvshows-genre/animacao/page/1',
                    API_SITE+'series/categoria/14']
    elif 'animes' in url:
        SDPlinks = [#'http://www.filmesportuguesesonline.com/',
                    'http://ratotv.win/animes',
                    'http://toppt.net/category/animacao/',
                    #'http://cinematugahd.net/category/animation/',
                    'http://tugaflix.com/Series?T=&G=Anima%C3%A7%C3%A3o&O=1&P=1',
                    'http://tugafree.com/category/filmes/animacao/page/1',
                    'http://www.redcouch.xyz/animes/page/1',
                    'http://www.moviefree.eu/tvshows-genre/animation/page/1',
                    #'http://movi3center.net/page/1',
                    'http://www.filmeshare.net/tvshows-genre/animacao/page/1',
                    API_SITE+'animes']
    else:
        SDPlinks = [#'http://www.filmesportuguesesonline.com/',
                    'http://ratotv.win/tvshows',
                    'http://toppt.net/category/series/',
                    #'http://cinematugahd.net',
                    'http://tugaflix.com/Series?T=&G=&O=1&P=1',
                    'http://tugafree.com/category/series/page/1',
                    'http://www.redcouch.xyz/series/page/1',
                    'http://www.moviefree.eu/tvshows/page/1',
                    #'http://movi3center.net/page/1',
                    'http://www.filmeshare.net/tvshows/page/1',
                    'http://sembilhete.ga/series/1',
                    API_SITE+'series']
    if 'SDPtodos' not in url:
        file = open(control.dataPath+'filmes.txt', 'w')                
        for link in SDPlinks:
            if url.replace('animacao','').replace('animes','') in link:
                file.write(str(link)+os.linesep)
                break
        file.close()
    else:
        file = open(control.dataPath+'filmes.txt', 'w')                
        for link in SDPlinks:
            file.write(str(link)+os.linesep)                
        file.close()
        
    from resources.lib.indexers import tvshowsPall
    tvshowsPall.tvshows().get(url)

elif action == 'moviePagePall':
    from resources.lib.indexers import moviesPall
    moviesPall.movies().get(url)

elif action == 'tvshowPagePall':
    from resources.lib.indexers import tvshowsPall
    tvshowsPall.tvshows().get(url)

elif action == 'episodesP':
    from resources.lib.indexers import episodesP
    episodesP.episodes().get()#tvshowtitle, year, imdb, tvdb, season, episode)

elif action == 'channelsP':
    from resources.lib.indexers import channelsP
    channelsP.channels().get()

elif action == 'movieToLibrary':
    from resources.lib.modules import libtools
    libtools.libmovies().add(name, title, year, imdb, tmdb)

elif action == 'moviesToLibrary':
    from resources.lib.modules import libtools
    libtools.libmovies().range(url)

elif action == 'tvshowToLibrary':
    from resources.lib.modules import libtools
    libtools.libtvshows().add(tvshowtitle, year, imdb, tmdb, tvdb, tvrage)

elif action == 'tvshowsToLibrary':
    from resources.lib.modules import libtools
    libtools.libtvshows().range(url)

elif action == 'updateLibrary':
    from resources.lib.modules import libtools
    libtools.libepisodes().update(query)

elif action == 'service':
    from resources.lib.modules import libtools
    libtools.libepisodes().service()

elif action == 'libtoolNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().library()

elif action == 'moviesSDPNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().moviesSDPNavigator()

elif action == 'tvshowsSDPNavigator':
    from resources.lib.indexers import navigator
    navigator.navigator().tvshowsSDPNavigator()
    
##############################################
    
elif action == 'moviePage':
    from resources.lib.indexers import movies
    movies.movies().get(url)

elif action == 'movieWidget':
    from resources.lib.indexers import movies
    movies.movies().widget()

elif action == 'movieSearch':
    from resources.lib.indexers import movies
    movies.movies().search()

elif action == 'moviePerson':
    from resources.lib.indexers import movies
    movies.movies().person()

elif action == 'movieGenres':
    from resources.lib.indexers import movies
    movies.movies().genres()

elif action == 'movieLanguages':
    from resources.lib.indexers import movies
    movies.movies().languages()

elif action == 'movieCertificates':
    from resources.lib.indexers import movies
    movies.movies().certifications()

elif action == 'movieYears':
    from resources.lib.indexers import movies
    movies.movies().years()

elif action == 'moviePersons':
    from resources.lib.indexers import movies
    movies.movies().persons(url)

elif action == 'movieUserlists':
    from resources.lib.indexers import movies
    movies.movies().userlists()

elif action == 'channels':
    from resources.lib.indexers import channels
    channels.channels().get()

elif action == 'tvshows':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().get(url)

elif action == 'tvshowPage':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().get(url)

elif action == 'tvSearch':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().search()

elif action == 'tvPerson':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().person()

elif action == 'tvGenres':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().genres()

elif action == 'tvNetworks':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().networks()

elif action == 'tvCertificates':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().certifications()

elif action == 'tvPersons':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().persons(url)

elif action == 'tvUserlists':
    from resources.lib.indexers import tvshows
    tvshows.tvshows().userlists()

elif action == 'seasons':
    from resources.lib.indexers import episodes
    episodes.seasons().get(tvshowtitle, year, imdb, tvdb)

elif action == 'episodes':
    from resources.lib.indexers import episodes
    episodes.episodes().get(tvshowtitle, year, imdb, tvdb, season, episode)

elif action == 'calendar':
    from resources.lib.indexers import episodes
    episodes.episodes().calendar(url)

elif action == 'tvWidget':
    from resources.lib.indexers import episodes
    episodes.episodes().widget()

elif action == 'calendars':
    from resources.lib.indexers import episodes
    episodes.episodes().calendars()

elif action == 'episodeUserlists':
    from resources.lib.indexers import episodes
    episodes.episodes().userlists()

elif action == 'refresh':
    from resources.lib.modules import control
    control.refresh()

elif action == 'queueItem':
    from resources.lib.modules import control
    control.queueItem()

elif action == 'openSettings':
    from resources.lib.modules import control
    control.openSettings(query)

elif action == 'artwork':
    from resources.lib.modules import control
    control.artwork()

elif action == 'addView':
    from resources.lib.modules import views
    views.addView(content)

elif action == 'moviePlaycount':
    from resources.lib.modules import playcount
    playcount.movies(imdb, query)

elif action == 'episodePlaycount':
    from resources.lib.modules import playcount
    playcount.episodes(imdb, tvdb, season, episode, query)

elif action == 'tvPlaycount':
    from resources.lib.modules import playcount
    playcount.tvshows(name, imdb, tvdb, season, query)

elif action == 'trailer':
    from resources.lib.modules import trailer
    trailer.trailer().play(name, url)

elif action == 'traktManager':
    from resources.lib.modules import trakt
    trakt.manager(name, imdb, tvdb, content)

elif action == 'authTrakt':
    from resources.lib.modules import trakt
    trakt.authTrakt()

elif action == 'rdAuthorize':
    from resources.lib.modules import debrid
    debrid.rdAuthorize()

elif action == 'download':
    import json
    from resources.lib.sources import sources
    from resources.lib.modules import downloader
    try: downloader.download(name, image, sources().sourcesResolve(json.loads(source)[0], True))
    except: pass

elif action == 'play':
    from resources.lib.sources import sources
    sources().play(title, year, imdb, tvdb, season, episode, tvshowtitle, premiered, meta, select)

elif action == 'addItem':
    from resources.lib.sources import sources
    sources().addItem(title)

elif action == 'playItem':
    from resources.lib.sources import sources
    sources().playItem(title, source)

elif action == 'alterSources':
    from resources.lib.sources import sources
    sources().alterSources(url, meta)

elif action == 'clearSources':
    from resources.lib.sources import sources
    sources().clearSources()


