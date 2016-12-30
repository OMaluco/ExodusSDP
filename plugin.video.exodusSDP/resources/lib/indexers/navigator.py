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


import os,sys,urlparse,base64

from resources.lib.modules import control
from resources.lib.modules import trakt


sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1]) ; control.moderator()

artPath = control.artPath() ; addonFanart = control.addonFanart()

imdbCredentials = False if control.setting('imdb.user') == '' else True

traktCredentials = trakt.getTraktCredentialsInfo()

traktIndicators = trakt.getTraktIndicatorsInfo()

queueMenu = control.lang(32065).encode('utf-8')

traktMode = False if control.setting('trakt_user') == '' else True

imdbMode = False if control.setting('imdb_user') == '' else True


class navigator:
    
    def __init__(self):
        
        self.SDP=' [COLOR green]S[/COLOR][COLOR yellow]d[/COLOR][COLOR red]P[/COLOR]'
        
    def root(self):        
        
        self.addDirectoryItem(32001, 'movieNavigator', 'movies.png', 'DefaultMovies.png')

        self.addDirectoryItem('Filmes'+self.SDP, 'moviesSDPNavigator', 'movies.png', 'DefaultMovies.png')
        
        self.addDirectoryItem(32002, 'tvNavigator', 'tvshows.png', 'DefaultTVShows.png')
        
        self.addDirectoryItem('Séries'+self.SDP, 'tvshowsSDPNavigator', 'tvshows.png', 'DefaultTVShows.png')

        if not control.setting('movie.widget') == '0':
            self.addDirectoryItem(32005, 'movieWidget', 'latest-movies.png', 'DefaultRecentlyAddedMovies.png')

        self.addDirectoryItem('Filmes Novos'+self.SDP, 'moviesPall&url=SDPtodos', 'latest-movies.png', 'DefaultRecentlyAddedMovies.png')#########

        if (traktIndicators == True and not control.setting('tv.widget.alt') == '0') or (traktIndicators == False and not control.setting('tv.widget') == '0'):
            self.addDirectoryItem(32006, 'tvWidget', 'latest-episodes.png', 'DefaultRecentlyAddedEpisodes.png')

        self.addDirectoryItem('Episódios Novos'+self.SDP, 'episodesP', 'latest-episodes.png', 'DefaultRecentlyAddedEpisodes.png')##########

        self.addDirectoryItem(32007, 'channels', 'channels.png', 'DefaultMovies.png')

        self.addDirectoryItem('Canais'+self.SDP, 'channelsP', 'channels.png', 'DefaultMovies.png')#########

        self.addDirectoryItem(32010, 'searchNavigator', 'search.png', 'DefaultFolder.png')

        self.addDirectoryItem('Pesquisar'+self.SDP, 'searchSDPNavigator', 'search.png', 'DefaultFolder.png')

        self.addDirectoryItem(32008, 'toolNavigator', 'tools.png', 'DefaultAddonProgram.png')

        downloads = True if control.setting('downloads') == 'true' and (len(control.listDir(control.setting('movie.download.path'))[0]) > 0 or len(control.listDir(control.setting('tv.download.path'))[0]) > 0) else False
        if downloads == True:
            self.addDirectoryItem(32009, 'downloadNavigator', 'downloads.png', 'DefaultFolder.png')

        self.endDirectory()

    def moviesSDPNavigator(self):
        t = '[COLOR blue] Animação[/COLOR]'
        sourcesTugaUp = ['Anituga','Cinematugahd','Filmeshare','FilmesPortuguesesOnline','Lausse','Moviefree','Movi3center','MrPiracy','RatoTv','Redcouch','Sembilhete','Toppt','Tugaflix','Tugafree','Tugahd','Vizer']

        self.addDirectoryItem('Pesquisar Filmes'+self.SDP, 'movieSDPSearch', 'search.png', 'DefaultMovies.png')
        self.addDirectoryItem('Filmes Novos'+self.SDP, 'moviesPall&url=SDPtodos', 'latest-movies.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem('Filmes Novos Animação'+self.SDP, 'moviesPall&url=SDPtodosanimacao', 'latest-movies.png', 'DefaultRecentlyAddedMovies.png')
        
        for s in sourcesTugaUp:
            n=s
            if s == 'MrPiracy': s='myapimp'
            self.addDirectoryItem(str(n), 'moviesPall&url='+str(s.lower()), 'movies.png', 'DefaultMovies.png')
            self.addDirectoryItem(str(n)+t, 'moviesPall&url='+str(s.lower())+'animacao', 'movies.png', 'DefaultMovies.png')
            if s == 'Movi3center': self.addDirectoryItem(str(n)+t+'[COLOR blue] PT-PT[/COLOR]', 'moviesPall&url='+str(s.lower())+'animacaopt', 'movies.png', 'DefaultMovies.png')

        self.endDirectory()

    def tvshowsSDPNavigator(self):
        t = '[COLOR blue] Animação[/COLOR]'
        t1 = '[COLOR blue] Animes[/COLOR]'
        #sourcesTugaUp = ['Anituga','Cinematugahd','Filmeshare','FilmesPortuguesesOnline','Lausse','Moviefree','Movi3center','MrPiracy','RatoTv','Redcouch','Sembilhete','Toppt','Tugaflix','Tugafree','Tugahd','Vizer']
        sourcesTugaUp = ['Anim3center','Anituga','Filmeshare','Lausse','Moviefree','MrPiracy','RatoTv','Redcouch','Sembilhete','Toppt','Tugaflix','Tugafree','Tugahd','Vizer']
        
        self.addDirectoryItem('Pesquisar Séries'+self.SDP, 'tvSDPSearch', 'search.png', 'DefaultTVShows.png')
        self.addDirectoryItem('Séries Novas'+self.SDP, 'tvshowsPall&url=SDPtodos', 'new-tvshows.png', 'DefaultTVShows.png')
        self.addDirectoryItem('Séries Animação Novas'+self.SDP, 'tvshowsPall&url=SDPtodosanimacao', 'new-tvshows.png', 'DefaultTVShows.png')
        self.addDirectoryItem('Séries Animes Novas'+self.SDP, 'tvshowsPall&url=SDPtodosanimes', 'new-tvshows.png', 'DefaultTVShows.png')
        
        for s in sourcesTugaUp:
            n=s
            if s == 'MrPiracy': s='myapimp'
            if s != 'Anim3center' and s != 'Anituga':
                self.addDirectoryItem(str(n), 'tvshowsPall&url='+str(s.lower()), 'tvshows.png', 'DefaultTVShows.png')
            if s == 'myapimp' or s == 'RatoTv' or s == 'Anituga' or s == 'Redcouch' or s == 'Anim3center':
                self.addDirectoryItem(str(n)+t1, 'tvshowsPall&url='+str(s.lower())+'animes', 'tvshows.png', 'DefaultTVShows.png')
            if s != 'Tugafree' and s != 'Redcouch' and s != 'Anim3center':
                self.addDirectoryItem(str(n)+t, 'tvshowsPall&url='+str(s.lower())+'animacao', 'tvshows.png', 'DefaultTVShows.png')

        self.endDirectory()


    def movies(self, lite=False):
        if not control.setting('lists.widget') == '0':
            self.addDirectoryItem('[COLOR white]Os Meus Filmes[/COLOR]', 'mymovieNavigator', 'mymovies.png', 'DefaultVideoPlaylists.png')
        self.addDirectoryItem(32011, 'movieGenres', 'genres.png', 'DefaultMovies.png')
        self.addDirectoryItem(32012, 'movieYears', 'years.png', 'DefaultMovies.png')
        self.addDirectoryItem(32013, 'moviePersons', 'people.png', 'DefaultMovies.png')
        self.addDirectoryItem(32014, 'movieLanguages', 'languages.png', 'DefaultMovies.png')
        self.addDirectoryItem(32015, 'movieCertificates', 'certificates.png', 'DefaultMovies.png')
        self.addDirectoryItem(32017, 'movies&url=trending', 'people-watching.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(32018, 'movies&url=popular', 'most-popular.png', 'DefaultMovies.png')
        self.addDirectoryItem(32019, 'movies&url=views', 'most-voted.png', 'DefaultMovies.png')
        self.addDirectoryItem(32020, 'movies&url=boxoffice', 'box-office.png', 'DefaultMovies.png')
        self.addDirectoryItem(32021, 'movies&url=oscars', 'oscar-winners.png', 'DefaultMovies.png')
        self.addDirectoryItem(32022, 'movies&url=theaters', 'in-theaters.png', 'DefaultRecentlyAddedMovies.png')
        self.addDirectoryItem(32005, 'movies&url=featured', 'latest-movies.png', 'DefaultRecentlyAddedMovies.png')

        if lite == False:
            if not control.setting('lists.widget') == '0':
                self.addDirectoryItem(32003, 'mymovieliteNavigator', 'mymovies.png', 'DefaultVideoPlaylists.png')

            self.addDirectoryItem(32028, 'moviePerson', 'people-search.png', 'DefaultMovies.png')
            self.addDirectoryItem(32010, 'movieSearch', 'search.png', 'DefaultMovies.png')

        self.endDirectory()


    def mymovies(self, lite=False):
        self.accountCheck()

        if traktCredentials == True and imdbCredentials == True:
            self.addDirectoryItem(32032, 'movies&url=traktcollection', 'trakt.png', 'DefaultMovies.png', queue=True)
            self.addDirectoryItem(32033, 'movies&url=traktwatchlist', 'trakt.png', 'DefaultMovies.png', queue=True)
            self.addDirectoryItem(32034, 'movies&url=imdbwatchlist', 'imdb.png', 'DefaultMovies.png', queue=True)

        elif traktCredentials == True:
            self.addDirectoryItem(32032, 'movies&url=traktcollection', 'trakt.png', 'DefaultMovies.png', queue=True)
            self.addDirectoryItem(32033, 'movies&url=traktwatchlist', 'trakt.png', 'DefaultMovies.png', queue=True)

        elif imdbCredentials == True:
            self.addDirectoryItem(32032, 'movies&url=imdbwatchlist', 'imdb.png', 'DefaultMovies.png', queue=True)
            self.addDirectoryItem(32033, 'movies&url=imdbwatchlist2', 'imdb.png', 'DefaultMovies.png', queue=True)

        if traktCredentials == True:
            self.addDirectoryItem(32035, 'movies&url=traktfeatured', 'trakt.png', 'DefaultMovies.png', queue=True)

        elif imdbCredentials == True:
            self.addDirectoryItem(32035, 'movies&url=featured', 'imdb.png', 'DefaultMovies.png', queue=True)

        if traktIndicators == True:
            self.addDirectoryItem(32036, 'movies&url=trakthistory', 'trakt.png', 'DefaultMovies.png', queue=True)

        self.addDirectoryItem(32039, 'movieUserlists', 'userlists.png', 'DefaultMovies.png')

        if lite == False:
            self.addDirectoryItem(32031, 'movieliteNavigator', 'movies.png', 'DefaultMovies.png')
            self.addDirectoryItem(32028, 'moviePerson', 'people-search.png', 'DefaultMovies.png')
            self.addDirectoryItem(32010, 'movieSearch', 'search.png', 'DefaultMovies.png')

        self.endDirectory()
        

    def tvshows(self, lite=False):
        if not control.setting('lists.widget') == '0':
            self.addDirectoryItem('[COLOR white]As Minhas Séries[/COLOR]', 'mytvNavigator', 'mytvshows.png', 'DefaultVideoPlaylists.png')
        self.addDirectoryItem(32011, 'tvGenres', 'genres.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32015, 'tvCertificates', 'certificates.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32016, 'tvNetworks', 'networks.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32017, 'tvshows&url=trending', 'people-watching.png', 'DefaultRecentlyAddedEpisodes.png')
        self.addDirectoryItem(32018, 'tvshows&url=popular', 'most-popular.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32023, 'tvshows&url=rating', 'highly-rated.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32019, 'tvshows&url=views', 'most-voted.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32024, 'tvshows&url=airing', 'airing-today.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32025, 'tvshows&url=active', 'returning-tvshows.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32026, 'tvshows&url=premiere', 'new-tvshows.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32006, 'calendar&url=added', 'latest-episodes.png', 'DefaultRecentlyAddedEpisodes.png', queue=True)
        self.addDirectoryItem(32027, 'calendars', 'calendar.png', 'DefaultRecentlyAddedEpisodes.png')

        if lite == False:
            if not control.setting('lists.widget') == '0':
                self.addDirectoryItem(32004, 'mytvliteNavigator', 'mytvshows.png', 'DefaultVideoPlaylists.png')

            self.addDirectoryItem(32028, 'tvPerson', 'people-search.png', 'DefaultTVShows.png')
            self.addDirectoryItem(32010, 'tvSearch', 'search.png', 'DefaultTVShows.png')

        self.endDirectory()


    def mytvshows(self, lite=False):
        self.accountCheck()

        if traktCredentials == True and imdbCredentials == True:
            self.addDirectoryItem(32032, 'tvshows&url=traktcollection', 'trakt.png', 'DefaultTVShows.png')
            self.addDirectoryItem(32033, 'tvshows&url=traktwatchlist', 'trakt.png', 'DefaultTVShows.png')
            self.addDirectoryItem(32034, 'tvshows&url=imdbwatchlist', 'imdb.png', 'DefaultTVShows.png')

        elif traktCredentials == True:
            self.addDirectoryItem(32032, 'tvshows&url=traktcollection', 'trakt.png', 'DefaultTVShows.png')
            self.addDirectoryItem(32033, 'tvshows&url=traktwatchlist', 'trakt.png', 'DefaultTVShows.png')

        elif imdbCredentials == True:
            self.addDirectoryItem(32032, 'tvshows&url=imdbwatchlist', 'imdb.png', 'DefaultTVShows.png')
            self.addDirectoryItem(32033, 'tvshows&url=imdbwatchlist2', 'imdb.png', 'DefaultTVShows.png')

        if traktCredentials == True:
            self.addDirectoryItem(32035, 'tvshows&url=traktfeatured', 'trakt.png', 'DefaultTVShows.png')

        elif imdbCredentials == True:
            self.addDirectoryItem(32035, 'tvshows&url=trending', 'imdb.png', 'DefaultMovies.png', queue=True)

        if traktIndicators == True:
            self.addDirectoryItem(32036, 'calendar&url=trakthistory', 'trakt.png', 'DefaultTVShows.png', queue=True)
            self.addDirectoryItem(32037, 'calendar&url=progress', 'trakt.png', 'DefaultRecentlyAddedEpisodes.png', queue=True)
            self.addDirectoryItem(32038, 'calendar&url=mycalendar', 'trakt.png', 'DefaultRecentlyAddedEpisodes.png', queue=True)

        self.addDirectoryItem(32040, 'tvUserlists', 'userlists.png', 'DefaultTVShows.png')

        if traktCredentials == True:
            self.addDirectoryItem(32041, 'episodeUserlists', 'userlists.png', 'DefaultTVShows.png')

        if lite == False:
            self.addDirectoryItem(32031, 'tvliteNavigator', 'tvshows.png', 'DefaultTVShows.png')
            self.addDirectoryItem(32028, 'tvPerson', 'people-search.png', 'DefaultTVShows.png')
            self.addDirectoryItem(32010, 'tvSearch', 'search.png', 'DefaultTVShows.png')

        self.endDirectory()


    def tools(self):
        self.addDirectoryItem(32043, 'openSettings&query=0.0', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32044, 'openSettings&query=3.1', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32045, 'openSettings&query=1.0', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32046, 'openSettings&query=5.0', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32047, 'openSettings&query=2.0', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32048, 'openSettings&query=4.0', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32049, 'viewsNavigator', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32050, 'clearSources', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32052, 'clearCache', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30121, 'libtoolNavigator', 'tools.jpg', 'DefaultAddonProgram.png')

        self.endDirectory()


    def library(self):
        self.addDirectoryItem(30131, 'openSettings&query=7.0', 'settings.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30132, 'updateLibrary&query=tool', 'update.jpg', 'DefaultAddonProgram.png')
        self.addDirectoryItem(30133, control.setting('movie_library'), 'movies.jpg', 'DefaultMovies.png', isAction=False)
        self.addDirectoryItem(30134, control.setting('tv_library'), 'tvshows.jpg', 'DefaultTVShows.png', isAction=False)

        if traktMode == True:
            self.addDirectoryItem(30135, 'moviesToLibrary&url=traktcollection', 'moviesTraktcollection.jpg', 'DefaultMovies.png')
            self.addDirectoryItem(30136, 'moviesToLibrary&url=traktwatchlist', 'moviesTraktwatchlist.jpg', 'DefaultMovies.png')
            self.addDirectoryItem(30137, 'tvshowsToLibrary&url=traktcollection', 'tvshowsTraktcollection.jpg', 'DefaultTVShows.png')
            self.addDirectoryItem(30138, 'tvshowsToLibrary&url=traktwatchlist', 'tvshowsTraktwatchlist.jpg', 'DefaultTVShows.png')

        if imdbMode == True:
            self.addDirectoryItem(30139, 'moviesToLibrary&url=imdbwatchlist', 'moviesImdbwatchlist.jpg', 'DefaultMovies.png')
            self.addDirectoryItem(30140, 'tvshowsToLibrary&url=imdbwatchlist', 'tvshowsImdbwatchlist.jpg', 'DefaultTVShows.png')

        self.endDirectory()


    def downloads(self):
        movie_downloads = control.setting('movie.download.path')
        tv_downloads = control.setting('tv.download.path')

        if len(control.listDir(movie_downloads)[0]) > 0:
            self.addDirectoryItem(32001, movie_downloads, 'movies.png', 'DefaultMovies.png', isAction=False)
        if len(control.listDir(tv_downloads)[0]) > 0:
            self.addDirectoryItem(32002, tv_downloads, 'tvshows.png', 'DefaultTVShows.png', isAction=False)

        self.endDirectory()


    def search(self):
        self.addDirectoryItem(32001, 'movieSearch', 'search.png', 'DefaultMovies.png')
        self.addDirectoryItem(32002, 'tvSearch', 'search.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32029, 'moviePerson', 'people-search.png', 'DefaultMovies.png')
        self.addDirectoryItem(32030, 'tvPerson', 'people-search.png', 'DefaultTVShows.png')

        self.endDirectory()

    def searchSDP(self):
        self.addDirectoryItem('Filmes'+self.SDP, 'movieSDPSearch', 'search.png', 'DefaultMovies.png')
        self.addDirectoryItem('Séries'+self.SDP, 'tvSDPSearch', 'search.png', 'DefaultTVShows.png')
##        self.addDirectoryItem(32029, 'moviePerson', 'people-search.png', 'DefaultMovies.png')
##        self.addDirectoryItem(32030, 'tvPerson', 'people-search.png', 'DefaultTVShows.png')

        self.endDirectory()


    def views(self):
        try:
            control.idle()

            items = [ (control.lang(32001).encode('utf-8'), 'movies'), (control.lang(32002).encode('utf-8'), 'tvshows'), (control.lang(32054).encode('utf-8'), 'seasons'), (control.lang(32038).encode('utf-8'), 'episodes') ]

            select = control.selectDialog([i[0] for i in items], control.lang(32049).encode('utf-8'))

            if select == -1: return

            content = items[select][1]

            title = control.lang(32059).encode('utf-8')
            url = '%s?action=addView&content=%s' % (sys.argv[0], content)

            poster, banner, fanart = control.addonPoster(), control.addonBanner(), control.addonFanart()

            item = control.item(label=title)
            item.setInfo(type='Video', infoLabels = {'title': title})
            item.setArt({'icon': poster, 'thumb': poster, 'poster': poster, 'banner': banner})
            item.setProperty('Fanart_Image', fanart)

            control.addItem(handle=int(sys.argv[1]), url=url, listitem=item, isFolder=False)
            control.content(int(sys.argv[1]), content)
            control.directory(int(sys.argv[1]), cacheToDisc=True)

            from resources.lib.modules import cache
            views.setView(content, {})
        except:
            return


    def accountCheck(self):
        if traktCredentials == False and imdbCredentials == False:
            control.idle()
            control.infoDialog(control.lang(32042).encode('utf-8'), sound=True, icon='WARNING')
            sys.exit()


    def clearCache(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')
        if not yes: return
        from resources.lib.modules import cache
        cache.clear()
        control.infoDialog(control.lang(32057).encode('utf-8'), sound=True, icon='INFO')


    def addDirectoryItem(self, name, query, thumb, icon, queue=False, isAction=True, isFolder=True):
        try: name = control.lang(name).encode('utf-8')
        except: pass
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
        thumb = os.path.join(artPath, thumb) if not artPath == None else icon
        cm = []
        if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
        item = control.item(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb})
        if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
        control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)


    def endDirectory(self):
        control.directory(syshandle, cacheToDisc=True)


