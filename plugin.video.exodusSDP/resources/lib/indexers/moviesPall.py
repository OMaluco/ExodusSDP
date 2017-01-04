# -*- coding: utf-8 -*-

'''
    Genesis Add-on
    Copyright (C) 2015 lambda

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


import os,sys,re,json,urllib,urlparse,base64,datetime,urllib2,xbmcplugin,xbmcgui,xbmc,xbmcaddon,xbmcvfs,time

from resources.lib.modules import trakt
from resources.lib.modules import cleangenre
from resources.lib.modules import cleantitle
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import client_genesis
from resources.lib.modules import cloudflare
from resources.lib.modules import cache
from resources.lib.modules import metacache
from resources.lib.modules import playcount
from resources.lib.modules import workers
from resources.lib.modules import views

from resources.lib.modules import BeautifulSoup

##import os,sys,re,json,urllib,urlparse,datetime,base64

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')

control.moderator()

addon_id = 'plugin.video.exodusSDP'
selfAddon = xbmcaddon.Addon(id=addon_id)
logado = selfAddon.getSetting('loggedin')


class movies:
    def __init__(self):
        self.list = []

        self.imdb_link = 'http://www.imdb.com'
        self.trakt_link = 'http://api-v2launch.trakt.tv'
        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
        self.trakt_user = control.setting('trakt.user').strip()
        self.imdb_user = control.setting('imdb.user').replace('ur', '')
        self.tm_user = control.setting('tm.user')
        self.fanart_tv_user = control.setting('fanart.tv.user')
        self.user = str(control.setting('fanart.tv.user')) + str(control.setting('tm.user'))
        self.lang = 'en'#control.apiLanguage()['trakt']

        self.search_link = 'http://api-v2launch.trakt.tv/search?type=movie&limit=20&page=1&query='
        self.imdb_info_link = 'http://www.omdbapi.com/?i=%s&plot=full&r=json'
        self.trakt_info_link = 'http://api-v2launch.trakt.tv/movies/%s'
        self.trakt_lang_link = 'http://api-v2launch.trakt.tv/movies/%s/translations/%s'
        self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/movies/%s'
        self.fanart_tv_level_link = 'http://webservice.fanart.tv/v3/level'
        self.tm_art_link = 'http://api.themoviedb.org/3/movie/%s/images?api_key=' + self.tm_user
        self.tm_img_link = 'https://image.tmdb.org/t/p/w%s%s'

        self.persons_link = 'http://www.imdb.com/search/name?count=100&name='
        self.personlist_link = 'http://www.imdb.com/search/name?count=100&gender=male,female'
        self.popular_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&num_votes=1000,&production_status=released&groups=top_1000&sort=moviemeter,asc&count=40&start=1'
        self.views_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&num_votes=1000,&production_status=released&sort=num_votes,desc&count=40&start=1'
        self.featured_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&num_votes=1000,&production_status=released&release_date=date[365],date[60]&sort=moviemeter,asc&count=40&start=1'
        self.person_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&role=%s&sort=year,desc&count=40&start=1'
        self.genre_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&num_votes=100,&release_date=date[730],date[30]&genres=%s&sort=moviemeter,asc&count=40&start=1'
        self.language_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&languages=%s&sort=moviemeter,asc&count=40&start=1'
        self.certification_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&num_votes=100,&production_status=released&certificates=us:%s&sort=moviemeter,asc&count=40&start=1'
        self.year_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&num_votes=100,&production_status=released&year=%s,%s&sort=moviemeter,asc&count=40&start=1'
        self.boxoffice_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&production_status=released&sort=boxoffice_gross_us,desc&count=40&start=1'
        self.oscars_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&production_status=released&groups=oscar_best_picture_winners&sort=year,desc&count=40&start=1'
        self.theaters_link = 'http://www.imdb.com/search/title?title_type=feature&languages=en&num_votes=1000,&release_date=date[365],date[0]&sort=release_date_us,desc&count=40&start=1'
        self.trending_link = 'http://api-v2launch.trakt.tv/movies/trending?limit=40&page=1'

        self.traktlists_link = 'http://api-v2launch.trakt.tv/users/me/lists'
        self.traktlikedlists_link = 'http://api-v2launch.trakt.tv/users/likes/lists?limit=1000000'
        self.traktlist_link = 'http://api-v2launch.trakt.tv/users/%s/lists/%s/items'
        self.traktcollection_link = 'http://api-v2launch.trakt.tv/users/me/collection/movies'
        self.traktwatchlist_link = 'http://api-v2launch.trakt.tv/users/me/watchlist/movies'
        self.traktfeatured_link = 'http://api-v2launch.trakt.tv/recommendations/movies?limit=40'
        self.trakthistory_link = 'http://api-v2launch.trakt.tv/users/me/history/movies?limit=40&page=1'
        self.imdblists_link = 'http://www.imdb.com/user/ur%s/lists?tab=all&sort=modified:desc&filter=titles' % self.imdb_user
        self.imdblist_link = 'http://www.imdb.com/list/%s/?view=detail&sort=title:asc&title_type=feature,short,tv_movie,tv_special,video,documentary,game&start=1'
        self.imdblist2_link = 'http://www.imdb.com/list/%s/?view=detail&sort=created:desc&title_type=feature,short,tv_movie,tv_special,video,documentary,game&start=1'
        self.imdbwatchlist_link = 'http://www.imdb.com/user/ur%s/watchlist?sort=alpha,asc' % self.imdb_user
        self.imdbwatchlist2_link = 'http://www.imdb.com/user/ur%s/watchlist?sort=date_added,desc' % self.imdb_user

        self.filmesportuguesesonline_link = 'http://www.filmesportuguesesonline.com/'
        self.tmdb_key = base64.urlsafe_b64decode('M2U3ODA3YzRhMDFmMTgyOThmNjQ2NjJiMjU3ZDcwNTk=')
        self.tmdb_info_link = 'http://api.themoviedb.org/3/movie/%s?api_key=%s&language=en&append_to_response=credits,releases' % ('%s', self.tmdb_key)#, self.lang)
        self.tmdb_image = 'http://image.tmdb.org/t/p/original'
        self.tmdb_poster = 'http://image.tmdb.org/t/p/w500'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'utf-8;q=0.7,*;q=0.7', 'Content-Type': 'application/json'}
        self.API_SITE = base64.urlsafe_b64decode('aHR0cDovL215YXBpbXAudGsvYXBpLw==')
        self.user = selfAddon.getSetting('mrpiracy_user')
        self.password = selfAddon.getSetting('mrpiracy_password')
        self.imdb_by_query = 'http://www.omdbapi.com/?t=%s&y=%s'
        self.tralhas = "http://tralhas.xyz/geturl/url.txt"
        self.base_link = self.rato_base_url()
        #self.search_link = '?do=search&subaction=search&search_start=1&story='
        self.userRato = selfAddon.getSetting('ratotv_user')
        self.passwordRato = selfAddon.getSetting('ratotv_password')
        #self.slist = []

        ###################################### SdP #########################################
        self.lista = []
        self.imdbcodes = []
        self.lista_urls = []
        self.lista_titulos = []
        self.lista_imdbcodes = []
        self.imdbcodes = []
        self.lista_limpa = []
        self.lista_next = []
        ###################################### SdP #########################################


    def get(self, url, idx=True):
        try:
##            try: url = getattr(self, url + '_link')
##            except: pass
##
##            try: u = urlparse.urlparse(url).netloc.lower()
##            except: pass

            sourceDict = []

            threads = []

            file = open(control.dataPath+'filmes.txt', 'r')

            if url == 'Releases':

                for link in file:
                    
                    try:
                        s = re.compile('//(.+?)[.]com/').findall(str(link))[0]
                        s = s.replace('www.','')
                    except:
                        try:
                            s = re.compile('//(.+?)[.]rocks/').findall(str(link))[0]
                            s = s.replace('www.','')
                        except:
                            try:
                                s = re.compile('//(.+?)[.]ws/').findall(str(link))[0]
                                s = s.replace('www.','')
                            except:
                                try:
                                    s = re.compile('//(.+?)[.]net/').findall(str(link))[0]
                                    s = s.replace('www.','')
                                except: s = ''
                                
                    sourceDict.append(str(s))
                    threads.append(workers.Thread(self.releases_list, link))

            else:
            
                for link in file:
                    
                    if 'ratotv' in link:
                        sourceDict.append('ratotv')
                        ratotv_link = link
                        threads.append(workers.Thread(self.ratotv_list, ratotv_link))
                        
                    elif 'myapimp' in link:
                        sourceDict.append('mrpiracy')
                        mrpiracy_link = link
                        threads.append(workers.Thread(self.mrpiracy_list, mrpiracy_link))
                        
                    elif 'toppt' in link:
                        sourceDict.append('toppt')
                        toppt_link = link
                        threads.append(workers.Thread(self.toppt_list, toppt_link))
                        
                    elif 'cinematuga' in link:
                        sourceDict.append('cinematuga')
                        cinematugahd_link = link
                        threads.append(workers.Thread(self.cinematugahd_list, cinematugahd_link))
                        
                    elif 'filmesportuguesesonline' in link:
                        sourceDict.append('filmesportuguesesonline')
                        filmesportuguesesonline_link = link
                        threads.append(workers.Thread(self.filmesportuguesesonline_list, filmesportuguesesonline_link))
                        
                    elif 'tugaflix' in link:
                        sourceDict.append('tugaflix')
                        tugaflix_link = link
                        threads.append(workers.Thread(self.tugaflix_list, tugaflix_link))
                        
                    elif 'tugafree' in link:
                        sourceDict.append('tugafree')
                        tugafree_link = link
                        threads.append(workers.Thread(self.tugafree_list, tugafree_link))
                        
                    elif 'redcouch' in link:
                        sourceDict.append('redcouch')
                        redcouch_link = link
                        threads.append(workers.Thread(self.redcouch_list, redcouch_link))
                        
                    elif 'moviefree' in link:
                        sourceDict.append('moviefree')
                        moviefreept_link = link
                        threads.append(workers.Thread(self.moviefreept_list, moviefreept_link))
                        
                    elif 'movi3center' in link:
                        sourceDict.append('movi3center')
                        movi3center_link = link
                        threads.append(workers.Thread(self.movi3center_list, movi3center_link))
                        
                    elif 'lausse' in link:
                        sourceDict.append('lausse')
                        lausse_link = link
                        threads.append(workers.Thread(self.lausse_list, lausse_link))
                        
                    elif 'vizer' in link:
                        sourceDict.append('vizer')
                        vizer_link = link
                        threads.append(workers.Thread(self.vizer_list, vizer_link))
                        
                    elif 'filmeshare' in link:
                        sourceDict.append('filmeshare')
                        filmeshare_link = link
                        threads.append(workers.Thread(self.filmeshare_list, filmeshare_link))
                        
                    elif 'tugahd' in link:
                        sourceDict.append('tugahd')
                        tugahd_link = link
                        threads.append(workers.Thread(self.tugahd_list, tugahd_link))
                        
                    elif 'sembilhete' in link:
                        sourceDict.append('sembilhetetv')
                        sembilhete_link = link
                        threads.append(workers.Thread(self.sembilhete_list, sembilhete_link))
                    
            file.close()
                        
            file = open(control.dataPath+'filmes.txt', 'w')
            file.close()

            try: timeout = int(control.setting('scrapers.timeout.1'))
            except: pass

            [i.start() for i in threads]

            sourceLabel = [re.sub('_mv_tv$|_mv$|_tv$', '', i) for i in sourceDict]
            sourceLabel = [re.sub('v\d+$', '', i).upper() for i in sourceLabel]

            progressDialog = control.progressDialog if control.setting('progress.dialog') == '0' else control.progressDialogBG
            progressDialog.create(control.addonInfo('name'), '')
            progressDialog.update(0)

            string1 = control.lang(32404).encode('utf-8')
            string2 = control.lang(32405).encode('utf-8')
            string3 = control.lang(32406).encode('utf-8')
            
            for i in range(0, timeout * 2):
                try:
                    if xbmc.abortRequested == True: return sys.exit()

                    try: info = [sourceLabel[int(re.sub('[^0-9]', '', str(x.getName()))) - 1] for x in threads if x.is_alive() == True]
                    except: info = []


                    try:
                        if progressDialog.iscanceled(): break
                        string4 = string1 % str(int(i * 0.5))
                        if len(info) > 5: string5 = string3 % str(len(info))
                        else: string5 = string3 % str(info).translate(None, "[]'")
                        progressDialog.update(int((100 / float(len(threads))) * len([x for x in threads if x.is_alive() == False])), str(string4), str(string5))
                    except:
                        string4 = string2 % str(int(i * 0.5))
                        if len(info) > 5: string5 = string3 % str(len(info))
                        else: string5 = str(info).translate(None, "[]'")
                        progressDialog.update(int((100 / float(len(threads))) * len([x for x in threads if x.is_alive() == False])), str(string4), str(string5))


                    is_alive = [x.is_alive() for x in threads]
                    if all(x == False for x in is_alive): break
                    time.sleep(0.5)
                except:
                    pass
            for i in range(0, 30 * 2):
                try:
                    if xbmc.abortRequested == True: return sys.exit()

                    try: info = [sourceLabel[int(re.sub('[^0-9]', '', str(x.getName()))) - 1] for x in threads if x.is_alive() == True]
                    except: info = []


                    try:
                        if progressDialog.iscanceled(): break
                        string4 = string1 % str(int(i * 0.5) + timeout)
                        if len(info) > 5: string5 = string3 % str(len(info))
                        else: string5 = string3 % str(info).translate(None, "[]'")
                        progressDialog.update(int((100 / float(len(threads))) * len([x for x in threads if x.is_alive() == False])), str(string4), str(string5))
                    except:
                        string4 = string2 % str(int(i * 0.5) + timeout)
                        if len(info) > 5: string5 = string3 % str(len(info))
                        else: string5 = str(info).translate(None, "[]'")
                        progressDialog.update(int((100 / float(len(threads))) * len([x for x in threads if x.is_alive() == False])), str(string4), str(string5))


                    is_alive = [x.is_alive() for x in threads]
                    if all(x == False for x in is_alive): break
                    if self.sources: break
                    time.sleep(0.5)
                except:
                    pass

            try: progressDialog.close()
            except: pass

            if url == 'Releases': next = 'Releases'
            else:
                file = open(control.dataPath+'filmes.txt', 'r')
                for linha in file:   
                    if 'SDPSearch' in str(linha):
                        next = 'SDPSearch'
                        break
                    else:
                        next = 'SDPtodos'
                file.close()

            slist = []
            for i in self.list:
                if i!='0':
                    if 'tt' not in i: i='tt'+i
                    slist.append(i.replace(' ',''))
            slist=list(set(slist))
            
            self.list = []
            for i in slist:
                print i
                self.list.append({'title': '0', 'originaltitle': '0', 'year': '0', 'premiered': '0', 'genre': '0', 'duration': '0', 'rating': '0', 'votes': '0', 'mpaa': '0', 'plot': '0', 'imdb': i, 'tvdb': '0', 'poster': '0', 'metacache': False, 'next': next})

##            threads = []
##            self.list = []
##            for i in slist:
##                threads.append(workers.Thread(self.SdP_tmdb_info_info, i, next))
##                #self.list.append({'title': '0', 'originaltitle': '0', 'year': '0', 'premiered': '0', 'genre': '0', 'duration': '0', 'rating': '0', 'votes': '0', 'mpaa': '0', 'plot': '0', 'imdb': i, 'tvdb': '0', 'poster': '0', 'next': next})
##            [i.start() for i in threads]
##            [i.join() for i in threads]
            
            if idx == True:
                self.worker()
                self.movieDirectory(self.list)
            return self.list
        except:
            pass

    
################################################################################################################
        
    def releases_list(self, link_url):
        
        if 'www.vcdq.com' not in link_url: urLink = link_url
        else: urlink = link_url.replace('/page','')        

        result = client.request(urLink)
        
        soup = BeautifulSoup.BeautifulSoup(result)
        
	for link in soup.findAll('a', attrs={'href': re.compile("^http://.+?/title/")}):
            
            if '?' in link.get('href'): result_imdb = link.get('href').split("?")[0].split("/title/")[1].replace('/','').replace('awards','').replace('videogallery','')
	    else: result_imdb = link.get('href').split("title")[1].replace('/','').replace('awards','').replace('videogallery','')
	    
            self.list.append(result_imdb)

        try:
            next = re.compile('/page/(.*)').findall(link_url)[0]
            prev = 'page/'+str(next)
            next = int(next)+1
            next = 'page/'+str(next)
            next = link_url.replace(prev,next).replace('\n','')
        except:
            next = ''

        file = open(control.dataPath+'filmes.txt', 'a')
        if next != '': file.write(str(next)+os.linesep)
        file.close()

	return self.list


    def mrpiracy_list(self, link_url):
        try:
            imdbcodes = []
                
            self.login()
                    
            self.headers['Authorization'] = 'Bearer %s' % selfAddon.getSetting('tokenMrpiracy')
            if 'pesquisa' not in link_url:
                result = client.request(link_url, headers=self.headers)

                acesso = self.verificar_acesso(result)
                if acesso == 'retry': result = client.request(link_url, headers=self.headers)

                result = json.loads(result)
                #print result

                try:
                    next = result['meta']['pagination']['links']['next']
                except:
                    next = ''
            else:
                pesquisa = re.compile('QUERY(.+?)QUERY').findall(link_url)[0]
                post = {'pesquisa': pesquisa}
                result = client.request(self.API_SITE+'filmes/pesquisa',post=json.dumps(post), headers=self.headers)

                acesso = self.verificar_acesso(result)
                if acesso == 'retry': result = client.request(self.API_SITE+'filmes/pesquisa',post=json.dumps(post), headers=self.headers)

                result = json.loads(result)
                #print result

                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()
            
            for i in result['data']:
                result_imdb= re.compile("u'IMBD': u'(.+?)'").findall(str(i))[0]
                imdbcodes.append(result_imdb)            

            threads = []
            for i in imdbcodes:
                try: threads.append(workers.Thread(self.SdP_tmdb_info, i, next))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]
                
            return next,self.list
        except:
            return

    def login(self):
        try:
            post = {'username': self.user, 'password': self.password,'grant_type': 'password', 'client_id': 'kodi', 'client_secret':'pyRmmKK3cbjouoDMLXNtt2eGkyTTAG' }

            resultado = client.request(self.API_SITE+'login', post=json.dumps(post), headers=self.headers)

            resultado = json.loads(resultado)

            token = resultado['access_token']
            refresh = resultado['refresh_token']
            headersN = self.headers
            headersN['Authorization'] = 'Bearer %s' % token
                          
            resultado = client.request(self.API_SITE+'me', headers=headersN)
            resultado = json.loads(resultado)

            try:
                username = resultado['username'].decode('utf-8')
            except:
                username = resultado['username'].encode('utf-8')
                                            

            if resultado['email'] == self.user:
                selfAddon.setSetting('tokenMrpiracy', token)
                selfAddon.setSetting('refreshMrpiracy', refresh)
                selfAddon.setSetting('loggedin', username)

            return
        except:
            return

    def verificar_acesso(self, resultado):
        try:
            resultado = json.loads(resultado)        
            if 'error' in resultado and resultado['error'] == 'access_denied':
                novoheaders = self.headers
                novoheaders['Authorization'] = 'Bearer %s' % selfAddon.getSetting('tokenMrpiracy')
                dados = {'refresh_token': selfAddon.getSetting('refreshMrpiracy'),'grant_type': 'refresh_token', 'client_id': 'kodi', 'client_secret':'pyRmmKK3cbjouoDMLXNtt2eGkyTTAG' }
                resultado = client.request('http://myapimp.tk/api/token/refresh',post=json.dumps(dados), headers=novoheaders)
                #resultado = self.abrir_url('http://myapimp.tk/api/token/refresh',post=json.dumps(dados), header=novoheaders)
                resultado = json.loads(resultado)
                selfAddon.setSetting('tokenMrpiracy', resultado['access_token'])
                selfAddon.setSetting('refreshMrpiracy', resultado['refresh_token'])
                return 'retry'
            else: return 'ok'
        except:
            return

    def abrir_url_mrpiracy(self, url, post=None, header=None, code=False, erro=False):
        try:

            if header == None:
                header = self.headers

            if post:
                req = urllib2.Request(url, data=post, headers=header)
            else:
                req = urllib2.Request(url, headers=header)

            try:
                response = urllib2.urlopen(req)
            except urllib2.HTTPError as response:
                if erro == True:
                    return str(response.code), "asd"

            link=response.read()

            response.close()
            return link
        except:
            return
    

    def cinematugahd_list(self, link_url):
        try:

            imdbcodes = []

            urllink=link_url
            link_url=link_url.replace('QUERY','')
            
            try:
                result = client.request(link_url)
            except: result = ''
                
            result_div = re.compile('<a href="http://www.imdb.com/title/(.+?)/" target="_blank">').findall(result)

            if 'QUERY' not in urllink:
                try:
                    next = client.parseDOM(result, 'a', attrs = {'class': 'nextpostslink'}, ret = 'href')[0]
                except:
                    next = ''
            else:
                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()
            
            for result_imdb in result_div:
                imdbcodes.append(result_imdb.replace('/',''))            

            threads = []
            for i in imdbcodes:
                try: threads.append(workers.Thread(self.SdP_tmdb_info, i, next))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]
                
            return next,self.list        
        except:
            return
    

    def ratotv_list(self, link_url):
        try:
            urllink=link_url
            link_url=link_url.replace('QUERY','')
            
            imdbcodes = []

            if 'QUERY' in urllink:

                if (self.userRato == '' or self.passwordRato == ''): raise Exception()

                query = self.base_link
                post = urllib.urlencode({'login': 'submit', 'login_name': self.userRato, 'login_password': self.passwordRato})
                cookie = client_genesis.source(query, post=post, output='cookie')

                result = client_genesis.request(link_url, post=post, cookie=cookie, referer=self.base_link)
            else:
                try:
                    result = client.request(link_url)
                except: result = ''

            if 'QUERY' not in urllink:
                try:next = re.compile('<divclass="next"><ahref="(.+?)"><img').findall(result.replace(' ',''))[0]
                except:next = ''
            else:
                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()
                
            result_div = re.compile('target="_blank">http://www.imdb.com/title/(.+?)/</a>').findall(result)
            
            for result_imdb in result_div:
                imdbcodes.append(result_imdb.replace('/',''))            
                
            threads = []
            for i in imdbcodes:
                try: threads.append(workers.Thread(self.SdP_tmdb_info, i, next))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]
                
            return next,self.list
        except:
            return

    def rato_base_url(self):
        request = urllib2.Request(self.tralhas)
        request.add_header("User-Agent", "Wget/1.15 (linux-gnu)")
        try:
            response =  urllib2.urlopen(request)
            base_url = response.read()
            response.close()
        except:
            traceback.print_exc()
            return
        return base_url
    

    def tugaflix_list(self, link_url):
        try:
            urllink=link_url
            link_url=link_url.replace('QUERY','')
        
            imdbcodes = []
            
            result = client.request(link_url)

            if 'QUERY' not in urllink:
                try:
                    next = re.compile('http://tugaflix.com/Filmes[?]T=[&]G=[&]O=1[&]P=(.*)').findall(link_url)[0]
                    prev = 'P='+str(next)
                    next = int(next)+1
                    next = 'P='+str(next)
                    next = link_url.replace(prev,next).replace('\n','')
                except:
                    next = ''
            else:
                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()
                
            result = client.parseDOM(result, 'div', attrs = {'class': 'browse-movie-bottom'})
            result = str(result)
            result = client.parseDOM(result, 'a', ret='href')
                
            for result_url in result:
                try:result_imdb = re.compile('=(.*)').findall(result_url)[0]
                except:result_imdb='0'                
                imdbcodes.append('tt'+result_imdb.replace('/',''))
                
            threads = []
            for i in imdbcodes:
                try: threads.append(workers.Thread(self.SdP_tmdb_info, i, next))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]
                
            return next,self.list
        except:
            return
    

    def toppt_list(self, link_url):
        try:
            urllink=link_url
            link_url=link_url.replace('QUERY','')
        
            imdbcodes = []
            
            result = client.request(link_url)            
            result_div = client.parseDOM(result, 'div', attrs = {'class': 'post clearfix.+?'})

            if 'QUERY' not in urllink:
                try:
                    next = re.compile('rel="next"href="(.+?)">Seguinte').findall(result.replace(' ',''))[0]
                except:
                    next = ''
            else:
                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()
            
            toppt = 'imdb.com/title/(.+?)/'
            for results in result_div:
                try: result_imdb = str(re.compile(toppt).findall(results)[0])
                except: result_imdb = '0'
                imdbcodes.append(result_imdb.replace('/',''))

            threads = []
            for i in imdbcodes:
                try: threads.append(workers.Thread(self.SdP_tmdb_info, i, next))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]
                
            return next,self.list
        except:
            return
    

    def tugafree_list(self, link_url):
        try:
            urllink=link_url
            link_url=link_url.replace('QUERY','')
        
            urls = []
            
            try:result = client.request(link_url)
            except: result = ''

            if 'QUERY' not in urllink:
                try:
                    next = re.compile('/page/(.*)').findall(link_url)[0]
                    prev = 'page/'+str(next)
                    next = int(next)+1
                    next = 'page/'+str(next)
                    next = link_url.replace(prev,next).replace('\n','')
                except:
                    next = ''
            else:
                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()

            result = client.parseDOM(result, 'div', attrs = {'class': 'article'})[0]
            result = client.parseDOM(result, 'div', attrs = {'class': 'post-data-container'})

            threads = []   
            for results in result:
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                try: threads.append(workers.Thread(self.tugafreeImdb_list, result_url))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]

            threads = []
            for i in self.imdbcodes:
                try: threads.append(workers.Thread(self.SdP_tmdb_info, i, next))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]
                
            return next,self.list
        except:
            return

    def tugafreeImdb_list(self, linkurl):
        try:
            
            try: result = client.request(linkurl)
            except: result = ''
                    
            try:result_imdb = re.compile('imdb.com/title/(.+?)/').findall(result)[0]
            except:result_imdb='0'

            self.imdbcodes.append(result_imdb.replace('/',''))
            return self.imdbcodes
        except:
            return


    def filmeshare_list(self, link_url):
        try:
            urllink=link_url
            link_url=link_url.replace('QUERY','')
        
            urls = []
            
            try:result = client.request(link_url)
            except: result = ''
            
            if 'QUERY' not in urllink:
                try:
                    next = re.compile('/page/(.*)').findall(link_url)[0]
                    prev = 'page/'+str(next)
                    next = int(next)+1
                    next = 'page/'+str(next)
                    next = link_url.replace(prev,next).replace('\n','')
                except:
                    next = ''
            else:
                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()

            result = str(result.replace('\n',''))
            if 'QUERY' not in urllink: result = client.parseDOM(result, 'div', attrs = {'class': 'boxinfo'})
            else: result = client.parseDOM(result, 'div', attrs = {'class': 'image'})

            threads = []   
            for results in result:
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                try: threads.append(workers.Thread(self.filmeshareImdb_list, result_url))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]

            threads = []
            for i in self.imdbcodes:
                try: threads.append(workers.Thread(self.SdP_tmdb_info, i, next))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]
                
            return next,self.list
        except:
            return

    def filmeshareImdb_list(self, linkurl):
        try:
            
            try: result = client.request(linkurl)
            except: result = ''
                    
            try: result_imdb = re.compile('imdb.com/title/(.+?)/').findall(result)[0]
            except:result_imdb='0'

            self.imdbcodes.append(result_imdb.replace('/',''))
            return self.imdbcodes
        except:
            return


    
    def moviefreept_list(self, link_url):
        try:
            urllink=link_url
            link_url=link_url.replace('QUERY','')
        
            urls = []
        
            try:result = client.request(link_url)
            except: result = ''
            
            if 'QUERY' not in urllink:
                try:
                    next = re.compile('/page/(.*)').findall(link_url)[0]
                    prev = 'page/'+str(next)
                    next = int(next)+1
                    next = 'page/'+str(next)
                    next = link_url.replace(prev,next).replace('\n','')
                except:
                    next = ''
            else:
                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()
                
            result = re.compile('<div id=".+?" class="item">(.+?)<span class="calidad2">').findall(result)

            threads = []   
            for results in result:
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                try: threads.append(workers.Thread(self.moviefreeptImdb_list, result_url))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]

            threads = []
            for i in self.imdbcodes:
                try: threads.append(workers.Thread(self.SdP_tmdb_info, i, next))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]
                
            return next,self.list
        except:
            return

    def moviefreeptImdb_list(self, linkurl):
        try:
            try: result = client.request(linkurl)
            except: result = ''
                    
            try:result_imdb = re.compile('imdb.com/title/(.+?)/').findall(result)[0]
            except:result_imdb='0'

            self.imdbcodes.append(result_imdb.replace('/',''))
            return self.imdbcodes
        except:
            return


    def movi3center_list(self, link_url):
        try:
            urllink=link_url
            link_url=link_url.replace('QUERY','')
            
            urls = []
        
            try:result = client.request(link_url)
            except: result = ''
            
            if 'QUERY' not in urllink:
                try:
                    next = re.compile('/page/(.*)').findall(link_url)[0]
                    prev = 'page/'+str(next)
                    next = int(next)+1
                    next = 'page/'+str(next)
                    next = link_url.replace(prev,next).replace('\n','')
                except:
                    next = ''
            else:
                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()
                
            if 'animacao' not in link_url and '/?s' not in link_url: result = client.parseDOM(result, 'div', attrs = {'class': 'image'})
            else: result = client.parseDOM(result, 'div', attrs = {'class': 'boxinfo'})

            threads = []   
            for results in result:
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                try: threads.append(workers.Thread(self.movi3centerImdb_list, result_url))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]

            threads = []
            for i in self.imdbcodes:
                try: threads.append(workers.Thread(self.SdP_tmdb_info, i, next))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]
                
            return next,self.list
        except:
            return

    def movi3centerImdb_list(self, linkurl):
        try:
            try: result = client.request(linkurl)
            except: result = ''
                    
            try:result_imdb = re.compile('imdb.com/title/(.+?)/').findall(result)[0]
            except:result_imdb='0'

            self.imdbcodes.append(result_imdb.replace('/',''))
            return self.imdbcodes
        except:
            return


    def vizer_list(self, link_url):
        try:
            try: pesquisa = re.compile('QUERY(.+?)QUERY').findall(link_url)[0]
            except: pesquisa = ''
            urllink=link_url
            link_url=link_url.replace('QUERY','')
            
            urls = []

            if 'QUERY' not in urllink:
                linkurl = re.compile('(.+?)/page').findall(link_url)[0]
                try: result = client.request(linkurl)
                except: result = ''
                try:
                    next = re.compile('/page/(.*)').findall(link_url)[0]
                    prev = 'page/'+str(next)
                    p = int(next)
                    next = int(next)+8
                    next = 'page/'+str(next)
                    next = link_url.replace(prev,next).replace('\n','')
                except:
                    next = ''
            else:
                try: result = client.request(link_url)
                except: result = ''
                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()

            if 'animation' not in link_url and 'QUERY' not in urllink:
                result = re.compile('<div class="text">Adicionados recentemente</div>(.+?)<div class="inner"').findall(result.replace('\n',''))[0]
                result = re.compile('<a href="(.+?)" class="linker" rel="canonical">').findall(result)
                for result_url in result:
                    urls.append('http://vizer.tv/'+result_url)
                threads = []
                for i in range(p, p+8):
                    try: threads.append(workers.Thread(self.vizerImdb_list, urls[i]))
                    except: pass
                [i.start() for i in threads]
                [i.join() for i in threads]
                
            elif 'animation' in link_url:
                result = re.compile('<div class="item category-item(.+?)<div class="lazy inner"').findall(result.replace('\n',''))              
                for results in result:
                    result_url = client.parseDOM(results, 'a', ret='href')[0]
                    urls.append('http://vizer.tv/'+result_url)
                threads = []
                for i in range(p, p+8):
                    try: threads.append(workers.Thread(self.vizerImdb_list, urls[i]))
                    except: pass
                [i.start() for i in threads]
                [i.join() for i in threads]
                
            elif 'QUERY' in urllink:
                post = urllib.urlencode({'keywords': pesquisa, 'search': ''})
                result = client_genesis.request('http://vizer.tv/search', post=post)

                result = result.replace('\n','')
                result = re.compile('<div class="row movies-list">(.+?)<div id="footer">').findall(result)[0]
                result = client.parseDOM(result, 'a', ret='href')

                threads = []
                for result_url in result:
                    result_url = 'http://vizer.tv/'+result_url
                    try: threads.append(workers.Thread(self.vizerImdb_list, result_url))
                    except: pass
                [i.start() for i in threads]
                [i.join() for i in threads]

            threads = []
            for i in self.imdbcodes:
                try: threads.append(workers.Thread(self.SdP_tmdb_info, i, next))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]
                
            return next,self.list
        except:
            return

    def vizerImdb_list(self, linkurl):
        try:
            try: result = client.request(linkurl)
            except: result = ''
                    
            try:result_imdb = re.compile('imdb.com/title/(.+?)/').findall(result)[0]
            except:result_imdb='0'

            self.imdbcodes.append(result_imdb.replace('/',''))
            return self.imdbcodes
        except:
            return
    

    def redcouch_list(self, link_url):
        try:
            urllink=link_url
            link_url=link_url.replace('QUERY','')
        
            urls = []
            
            try: result = client.request(link_url)
            except: result = ''
            
            if 'QUERY' not in urllink:
                try:
                    next = re.compile('/page/(.*)').findall(link_url)[0]
                    prev = 'page/'+str(next)
                    next = int(next)+1
                    next = 'page/'+str(next)
                    next = link_url.replace(prev,next).replace('\n','')
                except:
                    next = ''
            else:
                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()

            result = client.parseDOM(result, 'div', attrs = {'class': 'short-film'})

            threads = []   
            for results in result:
                try: result_url = client.parseDOM(results, 'a', ret='href')[0]
                except: result_url = ''
                try: threads.append(workers.Thread(self.redcouchImdb_list, result_url))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]

            threads = []
            for i in self.imdbcodes:
                try: threads.append(workers.Thread(self.SdP_tmdb_info, i, next))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]
                
            return next,self.list
        except:
            return

    def redcouchImdb_list(self, linkurl):
        try:
        
            try:
                result = client.request(linkurl)
                result = result.replace('\n','')
            except: result = ''

            try: result_title = re.compile('<li><span class="type">Título original:</span><p class="text"><strong>(.+?)</strong></p></li>').findall(result.replace('  ',''))[0]
            except: result_title = ''

            try:
                ano = re.compile('<spanclass="type">Ano:</span><pclass="text">(.+?)</p>').findall(result.replace(' ',''))[0]
                ano = ano.replace(' ','')
            except: ano = ''
                    
            try:result_imdb = re.compile('imdb.com/title/(.+?)/').findall(result)[0]
            except:result_imdb='0'

            if result_imdb == '0':
                urli = self.imdb_by_query % (urllib.quote_plus(result_title.replace('('+ano+')','')), ano)
                item = client.request(urli, timeout='10')
                item = json.loads(item)    
                result_imdb = item['imdbID']

            self.imdbcodes.append(result_imdb.replace('/',''))
            return self.imdbcodes
        except:
            return
    
    
    def sembilhete_list(self, link_url):
        try:
            urllink=link_url
            link_url=link_url.replace('QUERY','')

            imdbcodes = []
            
            try:
                result = client.request(link_url)
            except: result = ''
                
            result_div = re.compile('<a class="grid-item" href="/movie/(.+?)/">').findall(result)

            if 'QUERY' not in urllink:
                try:
                    next = re.compile('/movies/(.*)').findall(link_url)[0]
                    prev = 'movies/'+str(next)
                    next = int(next)+1
                    next = 'movies/'+str(next)
                    next = link_url.replace(prev,next).replace('\n','')
                except:
                    next = ''
            else:
                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()
            
            for result_imdb in result_div:
                imdbcodes.append(result_imdb.replace('/',''))            

            threads = []
            for i in imdbcodes:
                try: threads.append(workers.Thread(self.SdP_tmdb_info, i, next))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]
                
            return next,self.list
        except:
            return
        

    def filmesportuguesesonline_list(self, link_url):
        try:
            urllink=link_url
            link_url=link_url.replace('QUERY','')

            imdbcodes = []
            
            try:
                result = client.request(link_url)
            except: result = ''            
            
            if 'QUERY' not in urllink:
                try:
                    next = re.compile("<a class='blog-pager-older-link' href='(.+?)' id='Blog1_blog-pager-older-link' title='Next Post'>").findall(result.replace('\n',''))[0]
                except:
                    next = ''
            else:
                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()
                
            result_div = re.compile('"http://www.imdb.com/title/(.+?)"').findall(result)
            for result_imdb in result_div:
                imdbcodes.append(result_imdb.replace('/',''))            

            threads = []
            for i in imdbcodes:
                try: threads.append(workers.Thread(self.SdP_tmdb_info, i, next))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]
                
            return next,self.list
        except:
            return
    

    def SdP_tmdb_info(self, result_imdb, next):

        result_imdb = result_imdb.replace('PT','')
            
        if result_imdb != '0' and result_imdb != '':
            
            if 'tt' not in result_imdb:
                result_imdb = 'tt'+result_imdb

            self.list.append(result_imdb)
            
        return self.list


    def SdP_tmdb_info_info(self, result_imdb, next):

        result_imdb = result_imdb.replace('PT','')
            
        if result_imdb != '0' and result_imdb != '':
            
            if 'tt' not in result_imdb:
                result_imdb = 'tt'+result_imdb

            print result_imdb
            
            try:
                resultado = client.request(self.tmdb_info_link % result_imdb)
                resultado = json.loads(resultado)
            except:
                return
                
            try:
                title = resultado[u'title']
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')
                ##print title

                year = resultado[u'release_date']
                year = re.compile('(\d{4})').findall(year)[-1]
                year = str(year.encode('utf-8'))
                #print year

                name = '%s (%s)' % (title, year)
                try: name = name.encode('utf-8')
                except: pass
                #print name

                tmdb = resultado[u'id']
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')
                #print tmdb

                poster = resultado[u'poster_path']
                if poster == '' or poster == None: raise Exception()
                else: poster = '%s%s' % (self.tmdb_poster, poster)
                poster = poster.encode('utf-8')
                #print poster

                fanart = resultado[u'backdrop_path']
                if fanart == '' or fanart == None: fanart = '0'
                if not fanart == '0': fanart = '%s%s' % (self.tmdb_image, fanart)
                fanart = fanart.encode('utf-8')
                #print fanart

                premiered = resultado[u'release_date']
                try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')
                #print premiered

                rating = str(resultado[u'vote_average'])
                if rating == '' or rating == None: rating = '0'
                rating = rating.encode('utf-8')
                #print rating

                votes = str(resultado[u'vote_count'])
                try: votes = str(format(int(votes),',d'))
                except: pass
                if votes == '' or votes == None: votes = '0'
                votes = votes.encode('utf-8')
                #print votes

                plot = resultado[u'overview']
                if plot == '' or plot == None: plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')
                #print plot
                
                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'genre': '0', 'duration': '0', 'rating': rating, 'votes': votes, 'mpaa': '0', 'plot': plot, 'imdb': result_imdb, 'tvdb': '0', 'poster': '0', 'next': next})
            except:
                pass
        return self.list
    

    def abrir_url(self, url):            
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link


    def searchSDP(self):
        try:
            control.makeFile(control.dataPath)
            
            control.idle()

            t = control.lang(32010).encode('utf-8')
            k = control.keyboard('', t) ; k.doModal()
            q = k.getText() if k.isConfirmed() else None

            if (q == None or q == ''): return

            query = 'QUERY'+urllib.quote_plus(q)+'QUERY'
            
            SDPlinks = ['http://www.filmesportuguesesonline.com/search?q='+query,
                    self.base_link+'?do=search&subaction=search&search_start=1&story='+query,
                    'http://toppt.net/?s='+query,
                    'http://cinematuga.top/?s='+query,
                    'http://tugaflix.com/Filmes?G=&O=1&T='+query,
                    'http://tugafree.com/?s='+query,
                    'http://www.redcouch.xyz/index.php?do=search&subaction=search&catlist[]=1&story='+query,
                    'http://www.moviefree.eu/?s='+query,
                    'http://movi3center.net/?s='+query,
                    'http://www.filmeshare.net/?s='+query,
                    'http://vizer.tv/search'+query,
                    'http://sembilhete.ga/search/'+query,
                    self.API_SITE+'filmes/pesquisa'+query
                    ]
            file = open(control.dataPath+'filmes.txt', 'w')                
            for link in SDPlinks:
                file.write(str(link)+os.linesep)
            file.close()
            
            url = '%s?action=moviePagePall&url=SDPtodos' % (sys.argv[0])
            control.execute('Container.Update(%s)' % url)

        except:
            return
        

    def worker(self, level=1):
        self.meta = []
        total = len(self.list)

        self.fanart_tv_headers = {'api-key': 'YTc2MGMyMTEzYTM1OTk5NzFiN2FjMWU0OWUzMTAyMGQ='.decode('base64')}
        if not self.fanart_tv_user == '':
            self.fanart_tv_headers.update({'client-key': self.fanart_tv_user})

        for i in range(0, total): self.list[i].update({'metacache': False})

        self.list = metacache.fetch(self.list, self.lang, self.user)

        #########################
        try: timeout = int(control.setting('scrapers.timeout.1'))
        except: pass

        sourceLabel = [i['imdb'] for i in self.list]

        progressDialog = control.progressDialog if control.setting('progress.dialog') == '0' else control.progressDialogBG
        progressDialog.create(control.addonInfo('name'), '')
        progressDialog.update(0)

        string1 = control.lang(32404).encode('utf-8')
        string2 = control.lang(32405).encode('utf-8')
        string3 = 'A procurar Metadata %s'
        #########################

        for r in range(0, total, 40):
            threads = []
            for i in range(r, r+40):
                if i <= total: threads.append(workers.Thread(self.super_info, i))
                
            ##########################
            [i.start() for i in threads]
            stringponto = '.'
            for i in range(0, timeout * 2):
                try:
                    if xbmc.abortRequested == True: return sys.exit()

                    try: info = [sourceLabel[int(re.sub('[^0-9]', '', str(x.getName()))) - 1] for x in threads if x.is_alive() == True]
                    except: info = []

                    try:
                        if progressDialog.iscanceled(): break
                        string4 = string1 % str(int(i * 0.5))
                        string5 = string3 % str(stringponto)
                        stringponto = stringponto + '.'
                        progressDialog.update(int((100 / float(len(threads))) * len([x for x in threads if x.is_alive() == False])), str(string4), str(string5))
                    except:
                        string4 = string2 % str(int(i * 0.5))
                        string5 = string3 % str(stringponto)
                        stringponto = stringponto + '.'
                        progressDialog.update(int((100 / float(len(threads))) * len([x for x in threads if x.is_alive() == False])), str(string4), str(string5))


                    is_alive = [x.is_alive() for x in threads]
                    if all(x == False for x in is_alive): break
                    time.sleep(0.5)
                except:
                    pass
            for i in range(0, 30 * 2):
                try:
                    if xbmc.abortRequested == True: return sys.exit()

                    try: info = [sourceLabel[int(re.sub('[^0-9]', '', str(x.getName()))) - 1] for x in threads if x.is_alive() == True]
                    except: info = []


                    try:
                        if progressDialog.iscanceled(): break
                        string4 = string1 % str(int(i * 0.5) + timeout)
                        string5 = string3 % str(stringponto)
                        stringponto = stringponto + '.'
                        progressDialog.update(int((100 / float(len(threads))) * len([x for x in threads if x.is_alive() == False])), str(string4), str(string5))
                    except:
                        string4 = string2 % str(int(i * 0.5) + timeout)
                        string5 = string3 % str(stringponto)
                        stringponto = stringponto + '.'
                        progressDialog.update(int((100 / float(len(threads))) * len([x for x in threads if x.is_alive() == False])), str(string4), str(string5))


                    is_alive = [x.is_alive() for x in threads]
                    if all(x == False for x in is_alive): break
                    if self.sources: break
                    time.sleep(0.5)
                except:
                    pass
            ##########################
                
##            [i.start() for i in threads]
##            [i.join() for i in threads]

            if self.meta: metacache.insert(self.meta)

        try: progressDialog.close()################
        except: pass###########


        self.list = [i for i in self.list if not i['imdb'] == '0']

        self.list = metacache.local(self.list, self.tm_img_link, 'poster3', 'fanart2')

        if self.fanart_tv_user == '':
            for i in self.list: i.update({'clearlogo': '0', 'clearart': '0'})


    def super_info(self, i):
        try:
##            if self.list[i]['metacache'] == True: raise Exception()

            imdb = self.list[i]['imdb']

            url = self.imdb_info_link % imdb

            item = client.request(url, timeout='10')
            item = json.loads(item)

            title = item['Title']
            title = title.encode('utf-8')

            year = item['Year'].replace('-','').replace(' ','')
            year = year.encode('utf-8')

            imdb = item['imdbID']
            if imdb == None or imdb == '' or imdb == 'N/A': imdb = '0'
            imdb = imdb.encode('utf-8')

            premiered = item['Released']
            if premiered == None or premiered == '' or premiered == 'N/A': premiered = '0'
            premiered = re.findall('(\d*) (.+?) (\d*)', premiered)
            try: premiered = '%s-%s-%s' % (premiered[0][2], {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}[premiered[0][1]], premiered[0][0])
            except: premiered = '0'
            premiered = premiered.encode('utf-8')

            genre = item['Genre']
            if genre == None or genre == '' or genre == 'N/A': genre = '0'
            genre = genre.replace(', ', ' / ')
            genre = genre.encode('utf-8')

            duration = item['Runtime']
            if duration == None or duration == '' or duration == 'N/A': duration = '0'
            duration = re.sub('[^0-9]', '', str(duration))
            duration = duration.encode('utf-8')

            rating = item['imdbRating']
            if rating == None or rating == '' or rating == 'N/A' or rating == '0.0': rating = '0'
            rating = rating.encode('utf-8')

            votes = item['imdbVotes']
            try: votes = str(format(int(votes),',d'))
            except: pass
            if votes == None or votes == '' or votes == 'N/A': votes = '0'
            votes = votes.encode('utf-8')

            mpaa = item['Rated']
            if mpaa == None or mpaa == '' or mpaa == 'N/A': mpaa = '0'
            mpaa = mpaa.encode('utf-8')

            director = item['Director']
            if director == None or director == '' or director == 'N/A': director = '0'
            director = director.replace(', ', ' / ')
            director = re.sub(r'\(.*?\)', '', director)
            director = ' '.join(director.split())
            director = director.encode('utf-8')

            writer = item['Writer']
            if writer == None or writer == '' or writer == 'N/A': writer = '0'
            writer = writer.replace(', ', ' / ')
            writer = re.sub(r'\(.*?\)', '', writer)
            writer = ' '.join(writer.split())
            writer = writer.encode('utf-8')

            cast = item['Actors']
            if cast == None or cast == '' or cast == 'N/A': cast = '0'
            cast = [x.strip() for x in cast.split(',') if not x == '']
            try: cast = [(x.encode('utf-8'), '') for x in cast]
            except: cast = []
            if cast == []: cast = '0'

            plot = item['Plot']
            if plot == None or plot == '' or plot == 'N/A': plot = '0'
            plot = client.replaceHTMLCodes(plot)
            plot = plot.encode('utf-8')

            poster = item['Poster']
            if poster == None or poster == '' or poster == 'N/A': poster = '0'
            if '/nopicture/' in poster: poster = '0'
            poster = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
            if 'poster' in self.list[i] and poster == '0': poster = self.list[i]['poster']
            poster = poster.encode('utf-8')


            artmeta = True
            art = client.request(self.fanart_tv_art_link % imdb, headers=self.fanart_tv_headers, timeout='10', error=True)
            try: art = json.loads(art)
            except: artmeta = False

            try:
                poster2 = art['movieposter']
                poster2 = [x for x in poster2 if x.get('lang') == 'en'][::-1] + [x for x in poster2 if x.get('lang') == '00'][::-1]
                poster2 = poster2[0]['url'].encode('utf-8')
            except:
                poster2 = '0'

            try:
                if 'moviebackground' in art: fanart = art['moviebackground']
                else: fanart = art['moviethumb']
                fanart = [x for x in fanart if x.get('lang') == 'en'][::-1] + [x for x in fanart if x.get('lang') == '00'][::-1]
                fanart = fanart[0]['url'].encode('utf-8')
            except:
                fanart = '0'

            try:
                banner = art['moviebanner']
                banner = [x for x in banner if x.get('lang') == 'en'][::-1] + [x for x in banner if x.get('lang') == '00'][::-1]
                banner = banner[0]['url'].encode('utf-8')
            except:
                banner = '0'

            try:
                if 'hdmovielogo' in art: clearlogo = art['hdmovielogo']
                else: clearlogo = art['clearlogo']
                clearlogo = [x for x in clearlogo if x.get('lang') == 'en'][::-1] + [x for x in clearlogo if x.get('lang') == '00'][::-1]
                clearlogo = clearlogo[0]['url'].encode('utf-8')
            except:
                clearlogo = '0'

            try:
                if 'hdmovieclearart' in art: clearart = art['hdmovieclearart']
                else: clearart = art['clearart']
                clearart = [x for x in clearart if x.get('lang') == 'en'][::-1] + [x for x in clearart if x.get('lang') == '00'][::-1]
                clearart = clearart[0]['url'].encode('utf-8')
            except:
                clearart = '0'


            try:
                if self.tm_user == '': raise Exception()

                art2 = client.request(self.tm_art_link % imdb, timeout='10', error=True)
                art2 = json.loads(art2)
            except:
                pass

            try:
                poster3 = art2['posters']
                poster3 = [x for x in poster3 if x.get('iso_639_1') == 'en'] + [x for x in poster3 if not x.get('iso_639_1') == 'en']
                poster3 = [(x['width'], x['file_path']) for x in poster3]
                poster3 = [(x[0], x[1]) if x[0] < 300 else ('300', x[1]) for x in poster3]
                poster3 = self.tm_img_link % poster3[0]
                poster3 = poster3.encode('utf-8')
            except:
                poster3 = '0'

            try:
                fanart2 = art2['backdrops']
                fanart2 = [x for x in fanart2 if x.get('iso_639_1') == 'en'] + [x for x in fanart2 if not x.get('iso_639_1') == 'en']
                fanart2 = [x for x in fanart2 if x.get('width') == 1920] + [x for x in fanart2 if x.get('width') < 1920]
                fanart2 = [(x['width'], x['file_path']) for x in fanart2]
                fanart2 = [(x[0], x[1]) if x[0] < 1280 else ('1280', x[1]) for x in fanart2]
                fanart2 = self.tm_img_link % fanart2[0]
                fanart2 = fanart2.encode('utf-8')
            except:
                fanart2 = '0'


            try:
                if self.lang == 'en': raise Exception()

                url = self.trakt_lang_link % (imdb, self.lang)

                item = trakt.getTrakt(url)
                item = json.loads(item)[0]

                t = item['title']
                if not (t == None or t == ''): title = t
                try: title = title.encode('utf-8')
                except: pass

                t = item['overview']
                if not (t == None or t == ''): plot = t
                try: plot = plot.encode('utf-8')
                except: pass
            except:
                pass


            item = {'title': title, 'originaltitle': title, 'year': year, 'imdb': imdb, 'poster': poster, 'poster2': poster2, 'poster3': poster3, 'banner': banner, 'fanart': fanart, 'fanart2': fanart2, 'clearlogo': clearlogo, 'clearart': clearart, 'premiered': premiered, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot}
            item = dict((k,v) for k, v in item.iteritems() if not v == '0')
            self.list[i].update(item)

            if artmeta == False: raise Exception()

            meta = {'imdb': imdb, 'tvdb': '0', 'lang': self.lang, 'user': self.user, 'item': item}
            self.meta.append(meta)
        except:
            pass


    def movieDirectory(self, items):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        traktCredentials = trakt.getTraktCredentialsInfo()

        try: isOld = False ; control.item().getArt('type')
        except: isOld = True

        isPlayable = 'true' if not 'plugin' in control.infoLabel('Container.PluginName') else 'false'

        indicators = playcount.getMovieIndicators(refresh=True) if action == 'movies' else playcount.getMovieIndicators()

        playbackMenu = control.lang(32063).encode('utf-8') if control.setting('hosts.mode') == '2' else control.lang(32064).encode('utf-8')

        watchedMenu = control.lang(32068).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32066).encode('utf-8')

        unwatchedMenu = control.lang(32069).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32067).encode('utf-8')

        queueMenu = control.lang(32065).encode('utf-8')

        traktManagerMenu = control.lang(32070).encode('utf-8')

        nextMenu = control.lang(32053).encode('utf-8')


        for i in items:
            try:
                label = '%s (%s)' % (i['title'], i['year'])
                imdb, title, year = i['imdb'], i['originaltitle'], i['year']
##                if i['tmdb']: tmdb = str(i['tmdb'])
##                else: tmdb = '0'
                sysname = urllib.quote_plus('%s (%s)' % (title, year))
                systitle = urllib.quote_plus(title)

                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
                meta.update({'mediatype': 'movie'})
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, sysname)})
                #meta.update({'trailer': 'plugin://script.extendedinfo/?info=playtrailer&&id=%s' % imdb})
                if not 'duration' in i: meta.update({'duration': '120'})
                elif i['duration'] == '0': meta.update({'duration': '120'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except: pass

                sysmeta = urllib.quote_plus(json.dumps(meta))

                url = '%s?action=play&title=%s&year=%s&imdb=%s&meta=%s&t=%s' % (sysaddon, systitle, year, imdb, sysmeta, self.systime)
                sysurl = urllib.quote_plus(url)

                path = '%s?action=play&title=%s&year=%s&imdb=%s' % (sysaddon, systitle, year, imdb)


                cm = []

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                try:
                    overlay = int(playcount.getMovieOverlay(indicators, imdb))
                    if overlay == 7:
                        cm.append((unwatchedMenu, 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=6)' % (sysaddon, imdb)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        cm.append((watchedMenu, 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=7)' % (sysaddon, imdb)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass

                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&imdb=%s&content=movie)' % (sysaddon, sysname, imdb)))

                cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))

                cm.append(('Adicionar á Biblioteca', 'RunPlugin(%s?action=movieToLibrary&name=%s&title=%s&year=%s&imdb=%s)' % (sysaddon, sysname, systitle, year, imdb)))

                if isOld == True:
                    cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))


                item = control.item(label=label)

                art = {}

                if 'poster3' in i and not i['poster3'] == '0':
                    art.update({'icon': i['poster3'], 'thumb': i['poster3'], 'poster': i['poster3']})
                elif 'poster' in i and not i['poster'] == '0':
                    art.update({'icon': i['poster'], 'thumb': i['poster'], 'poster': i['poster']})
                elif 'poster2' in i and not i['poster2'] == '0':
                    art.update({'icon': i['poster2'], 'thumb': i['poster2'], 'poster': i['poster2']})
                else:
                    art.update({'icon': addonPoster, 'thumb': addonPoster, 'poster': addonPoster})

                if 'banner' in i and not i['banner'] == '0':
                    art.update({'banner': i['banner']})
                else:
                    art.update({'banner': addonBanner})

                if 'clearlogo' in i and not i['clearlogo'] == '0':
                    art.update({'clearlogo': i['clearlogo']})

                if 'clearart' in i and not i['clearart'] == '0':
                    art.update({'clearart': i['clearart']})


                if settingFanart == 'true' and 'fanart2' in i and not i['fanart2'] == '0':
                    item.setProperty('Fanart_Image', i['fanart2'])
                elif settingFanart == 'true' and 'fanart' in i and not i['fanart'] == '0':
                    item.setProperty('Fanart_Image', i['fanart'])
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setArt(art)
                item.addContextMenuItems(cm)
                item.setProperty('IsPlayable', isPlayable)
                item.setInfo(type='Video', infoLabels = meta)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
            except:
                pass

        if items[0]['next'] != 'SDPSearch':
            try:
                url = items[0]['next']
                if url != 'Releases': url = 'SDPtodos'
                #if url == '': raise Exception()

                icon = control.addonNext()
                url = '%s?action=moviePagePall&url=%s' % (sysaddon, urllib.quote_plus(url))

                item = control.item(label=nextMenu)

                item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
                if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        control.content(syshandle, 'movies')
        control.directory(syshandle, cacheToDisc=True)
        views.setView('movies', {'skin.confluence': 500})


    def addDirectory(self, items, queue=False):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonFanart, addonThumb, artPath = control.addonFanart(), control.addonThumb(), control.artPath()

        queueMenu = control.lang(32065).encode('utf-8')

        for i in items:
            try:
                name = i['name']

                if i['image'].startswith('http'): thumb = i['image']
                elif not artPath == None: thumb = os.path.join(artPath, i['image'])
                else: thumb = addonThumb

                url = '%s?action=%s' % (sysaddon, i['action'])
                try: url += '&url=%s' % urllib.quote_plus(i['url'])
                except: pass

                cm = []

                if queue == True:
                    cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                item = control.item(label=name)

                item.setArt({'icon': thumb, 'thumb': thumb})
                if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

                item.addContextMenuItems(cm)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        control.directory(syshandle, cacheToDisc=True)

