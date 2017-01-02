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


from resources.lib.modules import trakt
from resources.lib.modules import cleantitle
from resources.lib.modules import cleangenre
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import client_genesis
from resources.lib.modules import cache
from resources.lib.modules import metacache
from resources.lib.modules import playcount
from resources.lib.modules import workers
from resources.lib.modules import views

import os,sys,re,json,urllib,urlparse,datetime,base64,urllib2,xbmcplugin,xbmcgui,xbmc,xbmcaddon,xbmcvfs,time

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')

control.moderator()

addon_id = 'plugin.video.exodusSDP'
selfAddon = xbmcaddon.Addon(id=addon_id)
logado = selfAddon.getSetting('loggedin')


class tvshows:
    def __init__(self):
        self.list = []

        self.tmdb_key = base64.urlsafe_b64decode('M2U3ODA3YzRhMDFmMTgyOThmNjQ2NjJiMjU3ZDcwNTk=')

        self.imdb_link = 'http://www.imdb.com'
        self.trakt_link = 'http://api-v2launch.trakt.tv'
        self.tvmaze_link = 'http://www.tvmaze.com'
        self.tvdb_key = 'MUQ2MkYyRjkwMDMwQzQ0NA=='
        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        self.trakt_user = control.setting('trakt.user').strip()
        self.imdb_user = control.setting('imdb.user').replace('ur', '')
        self.fanart_tv_user = control.setting('fanart.tv.user')
        self.user = control.setting('fanart.tv.user') + str('')
        self.lang = control.apiLanguage()['tvdb']

        self.search_link = 'http://api-v2launch.trakt.tv/search?type=show&limit=20&page=1&query='
        self.tvmaze_info_link = 'http://api.tvmaze.com/shows/%s'
        self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/%s.xml' % (self.tvdb_key.decode('base64'), '%s', self.lang)
        self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/tv/%s'
        self.fanart_tv_level_link = 'http://webservice.fanart.tv/v3/level'
        self.tvdb_by_imdb = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s'
        self.tvdb_by_query = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s'
        self.imdb_by_query = 'http://www.omdbapi.com/?t=%s&y=%s'
        self.tvdb_image = 'http://thetvdb.com/banners/'
        self.tmdb_image = 'http://image.tmdb.org/t/p/original'
        self.tmdb_poster = 'http://image.tmdb.org/t/p/w500'

        self.persons_link = 'http://www.imdb.com/search/name?count=100&name='
        self.personlist_link = 'http://www.imdb.com/search/name?count=100&gender=male,female'
        self.popular_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&languages=en&num_votes=100,&release_date=,date[0]&sort=moviemeter,asc&count=40&start=1'
        self.airing_link = 'http://www.imdb.com/search/title?title_type=tv_episode&release_date=date[1],date[0]&sort=moviemeter,asc&count=40&start=1'
        #self.active_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=10,&production_status=active&sort=moviemeter,asc&count=40&start=1'
        self.active_link = 'http://api.themoviedb.org/3/tv/on_the_air?api_key=%s&page=1'#active
        self.premiere_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&languages=en&num_votes=10,&release_date=date[60],date[0]&sort=moviemeter,asc&count=40&start=1'
        self.rating_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=5000,&release_date=,date[0]&sort=user_rating,desc&count=40&start=1'
        self.views_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&num_votes=100,&release_date=,date[0]&sort=num_votes,desc&count=40&start=1'
        self.person_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&role=%s&sort=year,desc&count=40&start=1'
        self.genre_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&genres=%s&sort=moviemeter,asc&count=40&start=1'
        self.certification_link = 'http://www.imdb.com/search/title?title_type=tv_series,mini_series&release_date=,date[0]&certificates=us:%s&sort=moviemeter,asc&count=40&start=1'
        self.trending_link = 'http://api-v2launch.trakt.tv/shows/trending?limit=40&page=1'

        self.traktlists_link = 'http://api-v2launch.trakt.tv/users/me/lists'
        self.traktlikedlists_link = 'http://api-v2launch.trakt.tv/users/likes/lists?limit=1000000'
        self.traktlist_link = 'http://api-v2launch.trakt.tv/users/%s/lists/%s/items'
        self.traktcollection_link = 'http://api-v2launch.trakt.tv/users/me/collection/shows'
        self.traktwatchlist_link = 'http://api-v2launch.trakt.tv/users/me/watchlist/shows'
        self.traktfeatured_link = 'http://api-v2launch.trakt.tv/recommendations/shows?limit=40'
        self.imdblists_link = 'http://www.imdb.com/user/ur%s/lists?tab=all&sort=modified:desc&filter=titles' % self.imdb_user
        self.imdblist_link = 'http://www.imdb.com/list/%s/?view=detail&sort=title:asc&title_type=tv_series,mini_series&start=1'
        self.imdblist2_link = 'http://www.imdb.com/list/%s/?view=detail&sort=created:desc&title_type=tv_series,mini_series&start=1'
        self.imdbwatchlist_link = 'http://www.imdb.com/user/ur%s/watchlist?sort=alpha,asc' % self.imdb_user
        self.imdbwatchlist2_link = 'http://www.imdb.com/user/ur%s/watchlist?sort=date_added,desc' % self.imdb_user

        self.imdbcodes = []
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'utf-8;q=0.7,*;q=0.7', 'Content-Type': 'application/json'}
        self.API_SITE = base64.urlsafe_b64decode('aHR0cDovL215YXBpbXAudGsvYXBpLw==')
        self.user = selfAddon.getSetting('mrpiracy_user')
        self.password = selfAddon.getSetting('mrpiracy_password')
        self.imdb_by_query = 'http://www.omdbapi.com/?type=series&t=%s&y=%s'
        self.tralhas = "http://tralhas.xyz/geturl/url.txt"
        self.base_link = self.rato_base_url()
        #self.search_link = '?do=search&subaction=search&search_start=1&story='
        self.userRato = selfAddon.getSetting('ratotv_user')
        self.passwordRato = selfAddon.getSetting('ratotv_password')

    def get(self, url, idx=True):
        try:
            try: url = getattr(self, url + '_link')
            except: pass

            try: u = urlparse.urlparse(url).netloc.lower()
            except: pass

            sourceDict = []

            threads = []

            file = open(control.dataPath+'filmes.txt', 'r')
            
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

            try: progressDialog.close()
            except: pass

            file = open(control.dataPath+'filmes.txt', 'r')
            for linha in file:   
                if 'SDPSearch' in str(linha):
                    next = 'SDPSearch'
                    break
                else: next = 'SDPtodos'
            file.close()
          
            slist = []
            for i in self.list:
                if i!='0':
                    if 'tt' not in i: i='tt'+i
                    slist.append(i.replace(' ',''))
            slist=list(set(slist))

            self.list = []
            for i in slist:
                self.list.append({'title': '0', 'originaltitle': '0', 'year': '0', 'rating': '0', 'plot': '0', 'imdb': i, 'tvdb': '0', 'poster': '0', 'next': next})
 
            if idx == True:
                self.worker()
                self.tvshowDirectory(self.list)
            return self.list
        except:
            pass

    
################################################################################################################

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
                result = client.request(self.API_SITE+'series/pesquisa',post=json.dumps(post), headers=self.headers)

                acesso = self.verificar_acesso(result)
                if acesso == 'retry': result = client.request(self.API_SITE+'series/pesquisa',post=json.dumps(post), headers=self.headers)

                result = json.loads(result)
                #print result

                next = 'SDPSearch'
                
            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()
            
            for i in result['data']:
                result_imdb= re.compile("u'IMBD': u'(.+?)'").findall(str(i))[0]
                self.list.append(result_imdb.replace('/',''))
                
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
            urllink=link_url
            link_url=link_url.replace('QUERY','')

            imdbcodes = []
            
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
                self.list.append(result_imdb.replace('/',''))
                
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
                self.list.append(result_imdb.replace('/',''))
                
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
                    next = re.compile('http://tugaflix.com/Series[?]T=[&]G=[&]O=1[&]P=(.*)').findall(link_url)[0]
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
                self.list.append(result_imdb.replace('/',''))
                
            return next,self.list
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
                
            result_div = re.compile('<a class="imdb-link" href="/serie/(.+?)" target="_blank">').findall(result)
            
            if 'QUERY' not in urllink:
                try:
                    next = re.compile('/series/(.*)').findall(link_url)[0]
                    prev = 'series/'+str(next)
                    next = int(next)+1
                    next = 'series/'+str(next)
                    next = link_url.replace(prev,next).replace('\n','')
                except:
                    next = ''
            else:
                next = 'SDPSearch'

            file = open(control.dataPath+'filmes.txt', 'a')
            if next != '': file.write(str(next)+os.linesep)
            file.close()
            
            for result_imdb in result_div:
                self.list.append(result_imdb.replace('/',''))
                
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
                self.list.append(result_imdb.replace('/',''))
                
            return next,self.list
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
            #print str(len(result))

            threads = []   
            for results in result:
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                try: threads.append(workers.Thread(self.filmeshareImdb_list, result_url))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]

            for i in self.imdbcodes:
                self.list.append(i.replace('/',''))
                
            return next,self.list
        except:
            return

    def filmeshareImdb_list(self, linkurl):
        try:
            try: result = client.request(linkurl)
            except: result = ''
            
            try:result_title = re.compile('<b>Nome original</b><span itemprop="name">(.+?)</span>').findall(result)[0]
            except:result_title = ''
            try:result_year = re.compile('<b>Ano de lançamento</b><span><a href=".+?" rel="tag">(.+?)</a>').findall(result)[0]
            except: result_year = ''
            
            try:
                urli = 'http://www.omdbapi.com/?type=series&t=%s&y=%s' % (urllib.quote_plus(result_title), str(result_year))
                item = client.request(urli, timeout='10')
                item = json.loads(item)    
                result_imdb = item['imdbID']
            except: result_imdb = '0'

            self.imdbcodes.append(result_imdb.replace('/',''))
            return self.imdbcodes
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

            for i in self.imdbcodes:
                self.list.append(i.replace('/',''))
                
            return next,self.list
        except:
            return

    def tugafreeImdb_list(self, linkurl):
        try:
            
            try: result = client.request(linkurl)
            except: result = ''

            try:result_imdb = re.compile('data-title="(.+?)"').findall(result)[0]
            except:result_imdb='0'
            if result_imdb == '0':                   
                try:result_imdb = re.compile('imdb.com/title/(.+?)/').findall(result)[0]
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
                
            result = client.parseDOM(result, 'div', attrs = {'class': 'boxinfo'})

            threads = []   
            for results in result:
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                #print result_url
                try: threads.append(workers.Thread(self.moviefreeptImdb_list, result_url))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]

            for i in self.imdbcodes:
                self.list.append(i.replace('/',''))
                
            return next,self.list
        except:
            return

    def moviefreeptImdb_list(self, linkurl):
        try:
            try: result = client.request(linkurl)
            except: result = ''
                    
            try: result_title = re.compile('<b>Original name</b><span>(.+?)</span>').findall(result.replace('\n',''))[0]
            except: result_title = ''

            try:
                ano = re.compile('tvshows-release-year/(.+?)/" rel="tag">').findall(result.replace('\n',''))[0]
                ano = ano.replace(' ','')
            except: ano = ''
            
            urli = self.imdb_by_query % (urllib.quote_plus(result_title), str(ano))
            item = client.request(urli, timeout='10')
            item = json.loads(item)    
            result_imdb = item['imdbID']

            if result_imdb == '' or result_imdb == []: result_imdb == '0'

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
                
            if 'animacao' not in link_url: result = client.parseDOM(result, 'div', attrs = {'class': 'image'})
            else: result = client.parseDOM(result, 'div', attrs = {'class': 'boxinfo'})

            threads = []   
            for results in result:
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                try: threads.append(workers.Thread(self.movi3centerImdb_list, result_url))
                except: pass
            [i.start() for i in threads]
            [i.join() for i in threads]

            for i in self.imdbcodes:
                self.list.append(i.replace('/',''))
                
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

            for i in self.imdbcodes:
                self.list.append(i.replace('/',''))
                
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
            except:
                try: result_title = re.compile('<li><span class="type">TÍTULO ORIGINAL:</span><p class="text"><strong>(.+?)</strong></p></li>').findall(result.replace('  ',''))[0]
                except: result_title = ''

            try:
                ano = re.compile('<spanclass="type">Ano:</span><pclass="text">(.+?)</p>').findall(result.replace(' ',''))[0]
                ano = ano.replace(' ','')
            except:
                try:
                    ano = re.compile('<spanclass="type">ANO:</span><pclass="text">(.+?)</p>').findall(result.replace(' ',''))[0]
                    ano = ano.replace(' ','')
                except: ano = ''
            if ano == '':
                try:
                    ano = re.compile('<div class="rip border-3">(.+?)</div>').findall(result.replace(' ',''))[0]
                    ano = ano.replace(' ','')
                except: ano = ''

            try:result_imdb = re.compile('data-title="(.+?)"').findall(result)[0]
            except:result_imdb='0'
            if result_imdb == '0':
                try:result_imdb = re.compile('imdb.com/title/(.+?)/').findall(result)[0]
                except:result_imdb='0'

            if result_imdb == '0':
                urli = self.imdb_by_query % (urllib.quote_plus(result_title.replace('('+ano+')','')), ano)
                item = client.request(urli, timeout='10')
                item = json.loads(item)    
                result_imdb = item['imdbID']

            if result_imdb == '' or result_imdb == []: result_imdb == '0'

            self.imdbcodes.append(result_imdb.replace('/',''))
            return self.imdbcodes
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
                
            result_div = re.compile('"http://www.imdb.com/title/(.+?)"').findall(result)

            try:
                next = re.compile("<a class='blog-pager-older-link' href='(.+?)' id='Blog1_blog-pager-older-link' title='Next Post'>").findall(result.replace('\n',''))[0]
            except:
                next = ''

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


    def searchSDP(self):
        try:
            control.makeFile(control.dataPath)
            
            control.idle()

            t = control.lang(32010).encode('utf-8')
            k = control.keyboard('', t) ; k.doModal()
            q = k.getText() if k.isConfirmed() else None

            if (q == None or q == ''): return

            query = 'QUERY'+urllib.quote_plus(q)+'QUERY'
            
            SDPlinks = [#'http://www.filmesportuguesesonline.com/search?q='+query,
                    self.base_link+'?do=search&subaction=search&search_start=1&story='+query,
                    'http://toppt.net/?s='+query,
                    #'http://cinematuga.top/?s='+query,
                    'http://tugaflix.com/Series?G=&O=1&T='+query,
                    'http://tugafree.com/?s='+query,
                    'http://www.redcouch.xyz/index.php?do=search&subaction=search&catlist[]=2&story='+query,
                    'http://www.moviefree.eu/?s='+query,
                   # 'http://movi3center.net/?s='+query,
                    'http://www.filmeshare.net/?s='+query,
                    'http://vizer.tv/search'+query,
                    'http://sembilhete.ga/search/'+query,
                    self.API_SITE+'series/pesquisa'+query
                    ]
            file = open(control.dataPath+'filmes.txt', 'w')                
            for link in SDPlinks:
                file.write(str(link)+os.linesep)
            file.close()
            
            url = '%s?action=tvshowPagePall&url=SDPtodos' % (sys.argv[0])
            control.execute('Container.Update(%s)' % url)
        except:
            return


    def person(self):
        try:
            control.idle()

            t = control.lang(32010).encode('utf-8')
            k = control.keyboard('', t) ; k.doModal()
            q = k.getText() if k.isConfirmed() else None

            if (q == None or q == ''): return

            url = self.persons_link + urllib.quote_plus(q)
            url = '%s?action=tvPersons&url=%s' % (sys.argv[0], urllib.quote_plus(url))
            control.execute('Container.Update(%s)' % url)
        except:
            return


    def genres(self):
        genres = [
        ('Action', 'action'),
        ('Adventure', 'adventure'),
        ('Animation', 'animation'),
        ('Biography', 'biography'),
        ('Comedy', 'comedy'),
        ('Crime', 'crime'),
        ('Drama', 'drama'),
        ('Family', 'family'),
        ('Fantasy', 'fantasy'),
        ('Game-Show', 'game_show'),
        ('History', 'history'),
        ('Horror', 'horror'),
        ('Music ', 'music'),
        ('Musical', 'musical'),
        ('Mystery', 'mystery'),
        ('News', 'news'),
        ('Reality-TV', 'reality_tv'),
        ('Romance', 'romance'),
        ('Science Fiction', 'sci_fi'),
        ('Sport', 'sport'),
        ('Talk-Show', 'talk_show'),
        ('Thriller', 'thriller'),
        ('War', 'war'),
        ('Western', 'western')
        ]

        for i in genres: self.list.append({'name': cleangenre.lang(i[0], self.lang), 'url': self.genre_link % i[1], 'image': 'genres.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list


    def networks(self):
        networks = [
        ('A&E', '/networks/29/ae'),
        ('ABC', '/networks/3/abc'),
        ('AMC', '/networks/20/amc'),
        ('AT-X', '/networks/167/at-x'),
        ('Adult Swim', '/networks/10/adult-swim'),
        ('Amazon', '/webchannels/3/amazon'),
        ('Animal Planet', '/networks/92/animal-planet'),
        ('Audience', '/networks/31/audience-network'),
        ('BBC America', '/networks/15/bbc-america'),
        ('BBC Four', '/networks/51/bbc-four'),
        ('BBC One', '/networks/12/bbc-one'),
        ('BBC Three', '/webchannels/71/bbc-three'),
        ('BBC Two', '/networks/37/bbc-two'),
        ('BET', '/networks/56/bet'),
        ('Bravo', '/networks/52/bravo'),
        ('CBC', '/networks/36/cbc'),
        ('CBS', '/networks/2/cbs'),
        ('CTV', '/networks/48/ctv'),
        ('CW', '/networks/5/the-cw'),
        ('CW Seed', '/webchannels/13/cw-seed'),
        ('Cartoon Network', '/networks/11/cartoon-network'),
        ('Channel 4', '/networks/45/channel-4'),
        ('Channel 5', '/networks/135/channel-5'),
        ('Cinemax', '/networks/19/cinemax'),
        ('Comedy Central', '/networks/23/comedy-central'),
        ('Crackle', '/webchannels/4/crackle'),
        ('Discovery Channel', '/networks/66/discovery-channel'),
        ('Discovery ID', '/networks/89/investigation-discovery'),
        ('Disney Channel', '/networks/78/disney-channel'),
        ('Disney XD', '/networks/25/disney-xd'),
        ('E! Entertainment', '/networks/43/e'),
        ('E4', '/networks/41/e4'),
        ('FOX', '/networks/4/fox'),
        ('FX', '/networks/13/fx'),
        ('Freeform', '/networks/26/freeform'),
        ('HBO', '/networks/8/hbo'),
        ('HGTV', '/networks/192/hgtv'),
        ('Hallmark', '/networks/50/hallmark-channel'),
        ('History Channel', '/networks/53/history'),
        ('ITV', '/networks/35/itv'),
        ('Lifetime', '/networks/18/lifetime'),
        ('MTV', '/networks/22/mtv'),
        ('NBC', '/networks/1/nbc'),
        ('National Geographic', '/networks/42/national-geographic-channel'),
        ('Netflix', '/webchannels/1/netflix'),
        ('Nickelodeon', '/networks/27/nickelodeon'),
        ('PBS', '/networks/85/pbs'),
        ('Showtime', '/networks/9/showtime'),
        ('Sky1', '/networks/63/sky-1'),
        ('Starz', '/networks/17/starz'),
        ('Sundance', '/networks/33/sundance-tv'),
        ('Syfy', '/networks/16/syfy'),
        ('TBS', '/networks/32/tbs'),
        ('TLC', '/networks/80/tlc'),
        ('TNT', '/networks/14/tnt'),
        ('TV Land', '/networks/57/tvland'),
        ('Travel Channel', '/networks/82/travel-channel'),
        ('TruTV', '/networks/84/trutv'),
        ('USA', '/networks/30/usa-network'),
        ('VH1', '/networks/55/vh1'),
        ('WGN', '/networks/28/wgn-america')
        ]

        for i in networks: self.list.append({'name': i[0], 'url': self.tvmaze_link + i[1], 'image': 'networks.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list


    def certifications(self):
        certificates = ['TV-G', 'TV-PG', 'TV-14', 'TV-MA']

        for i in certificates: self.list.append({'name': str(i), 'url': self.certification_link % str(i).replace('-', '_').lower(), 'image': 'certificates.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list


    def persons(self, url):
        if url == None:
            self.list = cache.get(self.imdb_person_list, 24, self.personlist_link)
        else:
            self.list = cache.get(self.imdb_person_list, 1, url)

        for i in range(0, len(self.list)): self.list[i].update({'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list


    def userlists(self):
        try:
            userlists = []
            if trakt.getTraktCredentialsInfo() == False: raise Exception()
            activity = trakt.getActivity()
        except:
            pass

        try:
            if trakt.getTraktCredentialsInfo() == False: raise Exception()
            try:
                if activity > cache.timeout(self.trakt_user_list, self.traktlists_link, self.trakt_user): raise Exception()
                userlists += cache.get(self.trakt_user_list, 720, self.traktlists_link, self.trakt_user)
            except:
                userlists += cache.get(self.trakt_user_list, 0, self.traktlists_link, self.trakt_user)
        except:
            pass
        try:
            self.list = []
            if self.imdb_user == '': raise Exception()
            userlists += cache.get(self.imdb_user_list, 0, self.imdblists_link)
        except:
            pass
        try:
            self.list = []
            if trakt.getTraktCredentialsInfo() == False: raise Exception()
            try:
                if activity > cache.timeout(self.trakt_user_list, self.traktlikedlists_link, self.trakt_user): raise Exception()
                userlists += cache.get(self.trakt_user_list, 720, self.traktlikedlists_link, self.trakt_user)
            except:
                userlists += cache.get(self.trakt_user_list, 0, self.traktlikedlists_link, self.trakt_user)
        except:
            pass

        self.list = userlists
        for i in range(0, len(self.list)): self.list[i].update({'image': 'userlists.png', 'action': 'tvshows'})
        self.addDirectory(self.list)
        return self.list

    def tmdb_list(self, url):
        print url
        try:
            result = client.request(url % self.tmdb_key)
            result = json.loads(result)
            print result
            try: items = result['results']
            except: items = result['tv_credits']['cast']
        except:
            return

        try:
            next = str(result['page'])
            total = str(result['total_pages'])
            if next == total: raise Exception()
            if not 'page=' in url: raise Exception()
            next = '%s&page=%s' % (url.split('&page=', 1)[0], str(int(next)+1))
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:
                title = item['name']
                title = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', title)
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = item['first_air_date']
                year = re.compile('(\d{4})').findall(year)[-1]
                year = year.encode('utf-8')

                tmdb = item['id']
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                poster = item['poster_path']
                if poster == '' or poster == None: raise Exception()
                else: poster = '%s%s' % (self.tmdb_poster, poster)
                poster = poster.encode('utf-8')

                try: fanart = item['backdrop_path']
                except: fanart = '0'
                if fanart == '' or fanart == None: fanart = '0'
                if not fanart == '0': fanart = '%s%s' % (self.tmdb_image, fanart)
                fanart = fanart.encode('utf-8')

                premiered = item['first_air_date']
                try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')

                try: rating = str(item['vote_average'])
                except: rating = '0'
                if rating == '' or rating == None: rating = '0'
                rating = rating.encode('utf-8')

                try: votes = str(item['vote_count'])
                except: votes = '0'
                try: votes = str(format(int(votes),',d'))
                except: pass
                if votes == '' or votes == None: votes = '0'
                votes = votes.encode('utf-8')

                try: plot = item['overview']
                except: plot = '0'
                if plot == '' or plot == None: plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': '0', 'genre': '0', 'duration': '0', 'rating': rating, 'votes': votes, 'mpaa': '0', 'cast': '0', 'plot': plot, 'name': title, 'code': '0', 'imdb': '0', 'tmdb': tmdb, 'tvdb': '0', 'tvrage': '0', 'poster': poster, 'banner': '0', 'fanart': fanart, 'next': next})
            except:
                pass

        return self.list


    def trakt_list(self, url, user):
        try:
            dupes = []

            q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
            q.update({'extended': 'full,images'})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            u = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q

            result = trakt.getTrakt(u)
            result = json.loads(result)

            items = []
            for i in result:
                try: items.append(i['show'])
                except: pass
            if len(items) == 0:
                items = result
        except:
            return

        try:
            q = dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))
            if not int(q['limit']) == len(items): raise Exception()
            q.update({'page': str(int(q['page']) + 1)})
            q = (urllib.urlencode(q)).replace('%2C', ',')
            next = url.replace('?' + urlparse.urlparse(url).query, '') + '?' + q
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:
                title = item['title']
                title = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', title)
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = item['year']
                year = re.sub('[^0-9]', '', str(year))
                year = year.encode('utf-8')

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = item['ids']['imdb']
                if imdb == None or imdb == '': imdb = '0'
                else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                imdb = imdb.encode('utf-8')

                tvdb = item['ids']['tvdb']
                tvdb = re.sub('[^0-9]', '', str(tvdb))
                tvdb = tvdb.encode('utf-8')

                if tvdb == None or tvdb == '' or tvdb in dupes: raise Exception()
                dupes.append(tvdb)

                try: premiered = item['first_aired']
                except: premiered = '0'
                try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')

                try: studio = item['network']
                except: studio = '0'
                if studio == None: studio = '0'
                studio = studio.encode('utf-8')

                try: genre = item['genres']
                except: genre = '0'
                genre = [i.title() for i in genre]
                if genre == []: genre = '0'
                genre = ' / '.join(genre)
                genre = genre.encode('utf-8')

                try: duration = str(item['runtime'])
                except: duration = '0'
                if duration == None: duration = '0'
                duration = duration.encode('utf-8')

                try: rating = str(item['rating'])
                except: rating = '0'
                if rating == None or rating == '0.0': rating = '0'
                rating = rating.encode('utf-8')

                try: votes = str(item['votes'])
                except: votes = '0'
                try: votes = str(format(int(votes),',d'))
                except: pass
                if votes == None: votes = '0'
                votes = votes.encode('utf-8')

                try: mpaa = item['certification']
                except: mpaa = '0'
                if mpaa == None: mpaa = '0'
                mpaa = mpaa.encode('utf-8')

                try: plot = item['overview']
                except: plot = '0'
                if plot == None: plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': '0', 'next': next})
            except:
                pass

        return self.list


    def trakt_user_list(self, url, user):
        try:
            result = trakt.getTrakt(url)
            items = json.loads(result)
        except:
            pass

        for item in items:
            try:
                try: name = item['list']['name']
                except: name = item['name']
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                try: url = (trakt.slug(item['list']['user']['username']), item['list']['ids']['slug'])
                except: url = ('me', item['ids']['slug'])
                url = self.traktlist_link % url
                url = url.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

        self.list = sorted(self.list, key=lambda k: re.sub('(^the |^a )', '', k['name'].lower()))
        return self.list


    def imdb_list(self, url):
        try:
            dupes = []

            for i in re.findall('date\[(\d+)\]', url):
                url = url.replace('date[%s]' % i, (self.datetime - datetime.timedelta(days = int(i))).strftime('%Y-%m-%d'))

            def imdb_watchlist_id(url):
                return client.parseDOM(client.request(url).decode('iso-8859-1').encode('utf-8'), 'meta', ret='content', attrs = {'property': 'pageId'})[0]

            if url == self.imdbwatchlist_link:
                url = cache.get(imdb_watchlist_id, 8640, url)
                url = self.imdblist_link % url

            elif url == self.imdbwatchlist2_link:
                url = cache.get(imdb_watchlist_id, 8640, url)
                url = self.imdblist2_link % url

            result = client.request(url)

            result = result.replace('\n','')
            result = result.decode('iso-8859-1').encode('utf-8')

            items = client.parseDOM(result, 'div', attrs = {'class': 'lister-item mode-advanced'})
            items += client.parseDOM(result, 'div', attrs = {'class': 'list_item.+?'})
        except:
            return

        try:
            next = client.parseDOM(result, 'a', ret='href', attrs = {'class': 'lister-page-next.+?'})

            if len(next) == 0:
                next = client.parseDOM(result, 'div', attrs = {'class': 'pagination'})[0]
                next = zip(client.parseDOM(next, 'a', ret='href'), client.parseDOM(next, 'a'))
                next = [i[0] for i in next if 'Next' in i[1]]

            next = url.replace(urlparse.urlparse(url).query, urlparse.urlparse(next[0]).query)
            next = client.replaceHTMLCodes(next)
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:
                title = client.parseDOM(item, 'a')[1]
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = client.parseDOM(item, 'span', attrs = {'class': 'lister-item-year.+?'})
                year += client.parseDOM(item, 'span', attrs = {'class': 'year_type'})
                year = re.findall('(\d{4})', year[0])[0]
                year = year.encode('utf-8')

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = client.parseDOM(item, 'a', ret='href')[0]
                imdb = re.findall('(tt\d*)', imdb)[0]
                imdb = imdb.encode('utf-8')

                if imdb in dupes: raise Exception()
                dupes.append(imdb)

                try: poster = client.parseDOM(item, 'img', ret='loadlate')[0]
                except: poster = '0'
                if '/nopicture/' in poster: poster = '0'
                poster = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
                poster = client.replaceHTMLCodes(poster)
                poster = poster.encode('utf-8')

                rating = '0'
                try: rating = client.parseDOM(item, 'span', attrs = {'class': 'rating-rating'})[0]
                except: pass
                try: rating = client.parseDOM(rating, 'span', attrs = {'class': 'value'})[0]
                except: rating = '0'
                try: rating = client.parseDOM(item, 'div', ret='data-value', attrs = {'class': '.*?imdb-rating'})[0]
                except: pass
                if rating == '' or rating == '-': rating = '0'
                rating = client.replaceHTMLCodes(rating)
                rating = rating.encode('utf-8')

                plot = '0'
                try: plot = client.parseDOM(item, 'p', attrs = {'class': 'text-muted'})[0]
                except: pass
                try: plot = client.parseDOM(item, 'div', attrs = {'class': 'item_description'})[0]
                except: pass
                plot = plot.rsplit('<span>', 1)[0].strip()
                plot = re.sub('<.+?>|</.+?>', '', plot)
                if plot == '': plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'rating': rating, 'plot': plot, 'imdb': imdb, 'tvdb': '0', 'poster': poster, 'next': next})
            except:
                pass

        return self.list


    def imdb_person_list(self, url):
        try:
            result = client.request(url)
            result = result.decode('iso-8859-1').encode('utf-8')
            items = client.parseDOM(result, 'tr', attrs = {'class': '.+? detailed'})
        except:
            return

        for item in items:
            try:
                name = client.parseDOM(item, 'a', ret='title')[0]
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = client.parseDOM(item, 'a', ret='href')[0]
                url = re.findall('(nm\d*)', url, re.I)[0]
                url = self.person_link % url
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                image = client.parseDOM(item, 'img', ret='src')[0]
                if not ('._SX' in image or '._SY' in image): raise Exception()
                image = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', image)
                image = client.replaceHTMLCodes(image)
                image = image.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'image': image})
            except:
                pass

        return self.list


    def imdb_user_list(self, url):
        try:
            result = client.request(url)
            result = result.decode('iso-8859-1').encode('utf-8')
            items = client.parseDOM(result, 'div', attrs = {'class': 'list_name'})
        except:
            pass

        for item in items:
            try:
                name = client.parseDOM(item, 'a')[0]
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = client.parseDOM(item, 'a', ret='href')[0]
                url = url.split('/list/', 1)[-1].replace('/', '')
                url = self.imdblist_link % url
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass

        self.list = sorted(self.list, key=lambda k: re.sub('(^the |^a )', '', k['name'].lower()))
        return self.list


    def tvmaze_list(self, url):
        try:
            result = client.request(url)
            result = client.parseDOM(result, 'section', attrs = {'id': 'this-seasons-shows'})

            items = client.parseDOM(result, 'li')
            items = [client.parseDOM(i, 'a', ret='href') for i in items]
            items = [i[0] for i in items if len(i) > 0]
            items = [re.findall('/(\d+)/', i) for i in items]
            items = [i[0] for i in items if len(i) > 0]
            items = items[:50]
        except:
            return

        def items_list(i):
            try:
                url = self.tvmaze_info_link % i

                item = client.request(url)
                item = json.loads(item)

                title = item['name']
                title = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', title)
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = item['premiered']
                year = re.findall('(\d{4})', year)[0]
                year = year.encode('utf-8')

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = item['externals']['imdb']
                if imdb == None or imdb == '': imdb = '0'
                else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                imdb = imdb.encode('utf-8')

                tvdb = item['externals']['thetvdb']
                tvdb = re.sub('[^0-9]', '', str(tvdb))
                tvdb = tvdb.encode('utf-8')

                if tvdb == None or tvdb == '': raise Exception()
 
                try: poster = item['image']['original']
                except: poster = '0'
                if poster == None or poster == '': poster = '0'
                poster = poster.encode('utf-8')

                premiered = item['premiered']
                try: premiered = re.findall('(\d{4}-\d{2}-\d{2})', premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')

                try: studio = item['network']['name']
                except: studio = '0'
                if studio == None: studio = '0'
                studio = studio.encode('utf-8')

                try: genre = item['genres']
                except: genre = '0'
                genre = [i.title() for i in genre]
                if genre == []: genre = '0'
                genre = ' / '.join(genre)
                genre = genre.encode('utf-8')

                try: duration = item['runtime']
                except: duration = '0'
                if duration == None: duration = '0'
                duration = str(duration)
                duration = duration.encode('utf-8')

                try: rating = item['rating']['average']
                except: rating = '0'
                if rating == None or rating == '0.0': rating = '0'
                rating = str(rating)
                rating = rating.encode('utf-8')

                try: plot = item['summary']
                except: plot = '0'
                if plot == None: plot = '0'
                plot = re.sub('<.+?>|</.+?>|\n', '', plot)
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                try: content = item['type'].lower()
                except: content = '0'
                if content == None or content == '': content = '0'
                content = content.encode('utf-8')

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'content': content})
            except:
                pass

        try:
            threads = []
            for i in items: threads.append(workers.Thread(items_list, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

            filter = [i for i in self.list if i['content'] == 'scripted']
            filter += [i for i in self.list if not i['content'] == 'scripted']
            self.list = filter

            return self.list
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
        print str(timeout)

        sourceLabel = [i['imdb'] for i in self.list]

        progressDialog = control.progressDialog if control.setting('progress.dialog') == '0' else control.progressDialogBG
        progressDialog.create(control.addonInfo('name'), '')
        progressDialog.update(0)

        string1 = control.lang(32404).encode('utf-8')
        print string1
        string2 = control.lang(32405).encode('utf-8')
        print string2
        string3 = 'A procurar Metadata %s'
        print string3
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

        self.list = [i for i in self.list if not i['tvdb'] == '0']

        if self.fanart_tv_user == '':
            for i in self.list: i.update({'clearlogo': '0', 'clearart': '0'})


    def super_info(self, i):
        try:
            #if self.list[i]['metacache'] == True: raise Exception()

            imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
            tvdb = self.list[i]['tvdb'] if 'tvdb' in self.list[i] else '0'

            if imdb == '0':
                url = self.imdb_by_query % (urllib.quote_plus(self.list[i]['title']), self.list[i]['year'])

                imdb = client.request(url, timeout='10')
                try: imdb = json.loads(imdb)['imdbID']
                except: imdb = '0'

                if imdb == None or imdb == '' or imdb == 'N/A': imdb = '0'


            if tvdb == '0' and not imdb == '0':
                url = self.tvdb_by_imdb % imdb

                result = client.request(url, timeout='10')

                try: tvdb = client.parseDOM(result, 'seriesid')[0]
                except: tvdb = '0'

                try: name = client.parseDOM(result, 'SeriesName')[0]
                except: name = '0'
                dupe = re.findall('[***]Duplicate (\d*)[***]', name)
                if dupe: tvdb = str(dupe[0])

                if tvdb == '': tvdb = '0'


            if tvdb == '0':
                url = self.tvdb_by_query % (urllib.quote_plus(self.list[i]['title']))

                years = [str(self.list[i]['year']), str(int(self.list[i]['year'])+1), str(int(self.list[i]['year'])-1)]

                tvdb = client.request(url, timeout='10')
                tvdb = re.sub(r'[^\x00-\x7F]+', '', tvdb)
                tvdb = client.replaceHTMLCodes(tvdb)
                tvdb = client.parseDOM(tvdb, 'Series')
                tvdb = [(x, client.parseDOM(x, 'SeriesName'), client.parseDOM(x, 'FirstAired')) for x in tvdb]
                tvdb = [(x, x[1][0], x[2][0]) for x in tvdb if len(x[1]) > 0 and len(x[2]) > 0]
                tvdb = [x for x in tvdb if cleantitle.get(self.list[i]['title']) == cleantitle.get(x[1])]
                tvdb = [x[0][0] for x in tvdb if any(y in x[2] for y in years)][0]
                tvdb = client.parseDOM(tvdb, 'seriesid')[0]

                if tvdb == '': tvdb = '0'


            url = self.tvdb_info_link % tvdb
            item = client.request(url, timeout='10')
            if item == None: raise Exception()

            if imdb == '0':
                try: imdb = client.parseDOM(item, 'IMDB_ID')[0]
                except: pass
                if imdb == '': imdb = '0'
                imdb = imdb.encode('utf-8')


            try: title = client.parseDOM(item, 'SeriesName')[0]
            except: title = ''
            if title == '': title = '0'
            title = client.replaceHTMLCodes(title)
            title = title.encode('utf-8')

            try: year = client.parseDOM(item, 'FirstAired')[0]
            except: year = ''
            try: year = re.compile('(\d{4})').findall(year)[0]
            except: year = ''
            if year == '': year = '0'
            year = year.encode('utf-8')

            try: premiered = client.parseDOM(item, 'FirstAired')[0]
            except: premiered = '0'
            if premiered == '': premiered = '0'
            premiered = client.replaceHTMLCodes(premiered)
            premiered = premiered.encode('utf-8')

            try: studio = client.parseDOM(item, 'Network')[0]
            except: studio = ''
            if studio == '': studio = '0'
            studio = client.replaceHTMLCodes(studio)
            studio = studio.encode('utf-8')

            try: genre = client.parseDOM(item, 'Genre')[0]
            except: genre = ''
            genre = [x for x in genre.split('|') if not x == '']
            genre = ' / '.join(genre)
            if genre == '': genre = '0'
            genre = client.replaceHTMLCodes(genre)
            genre = genre.encode('utf-8')

            try: duration = client.parseDOM(item, 'Runtime')[0]
            except: duration = ''
            if duration == '': duration = '0'
            duration = client.replaceHTMLCodes(duration)
            duration = duration.encode('utf-8')

            try: rating = client.parseDOM(item, 'Rating')[0]
            except: rating = ''
            if 'rating' in self.list[i] and not self.list[i]['rating'] == '0':
                rating = self.list[i]['rating']
            if rating == '': rating = '0'
            rating = client.replaceHTMLCodes(rating)
            rating = rating.encode('utf-8')

            try: votes = client.parseDOM(item, 'RatingCount')[0]
            except: votes = ''
            if 'votes' in self.list[i] and not self.list[i]['votes'] == '0':
                votes = self.list[i]['votes']
            if votes == '': votes = '0'
            votes = client.replaceHTMLCodes(votes)
            votes = votes.encode('utf-8')

            try: mpaa = client.parseDOM(item, 'ContentRating')[0]
            except: mpaa = ''
            if mpaa == '': mpaa = '0'
            mpaa = client.replaceHTMLCodes(mpaa)
            mpaa = mpaa.encode('utf-8')

            try: cast = client.parseDOM(item, 'Actors')[0]
            except: cast = ''
            cast = [x for x in cast.split('|') if not x == '']
            try: cast = [(x.encode('utf-8'), '') for x in cast]
            except: cast = []
            if cast == []: cast = '0'

            try: plot = client.parseDOM(item, 'Overview')[0]
            except: plot = ''
            if plot == '': plot = '0'
            plot = client.replaceHTMLCodes(plot)
            plot = plot.encode('utf-8')

            try: poster = client.parseDOM(item, 'poster')[0]
            except: poster = ''
            if not poster == '': poster = self.tvdb_image + poster
            else: poster = '0'
            if 'poster' in self.list[i] and poster == '0': poster = self.list[i]['poster']
            poster = client.replaceHTMLCodes(poster)
            poster = poster.encode('utf-8')

            try: banner = client.parseDOM(item, 'banner')[0]
            except: banner = ''
            if not banner == '': banner = self.tvdb_image + banner
            else: banner = '0'
            banner = client.replaceHTMLCodes(banner)
            banner = banner.encode('utf-8')

            try: fanart = client.parseDOM(item, 'fanart')[0]
            except: fanart = ''
            if not fanart == '': fanart = self.tvdb_image + fanart
            else: fanart = '0'
            fanart = client.replaceHTMLCodes(fanart)
            fanart = fanart.encode('utf-8')


            try:
                artmeta = True
                if self.fanart_tv_user == '': raise Exception()

                art = client.request(self.fanart_tv_art_link % tvdb, headers=self.fanart_tv_headers, timeout='10', error=True)
                try: art = json.loads(art)
                except: artmeta = False
            except:
                pass

            try:
                poster2 = art['tvposter']
                poster2 = [x for x in poster2 if x.get('lang') == 'en'][::-1] + [x for x in poster2 if x.get('lang') == '00'][::-1]
                poster2 = poster2[0]['url'].encode('utf-8')
            except:
                poster2 = '0'

            try:
                fanart2 = art['showbackground']
                fanart2 = [x for x in fanart2 if x.get('lang') == 'en'][::-1] + [x for x in fanart2 if x.get('lang') == '00'][::-1]
                fanart2 = fanart2[0]['url'].encode('utf-8')
            except:
                fanart2 = '0'

            try:
                banner2 = art['tvbanner']
                banner2 = [x for x in banner2 if x.get('lang') == 'en'][::-1] + [x for x in banner2 if x.get('lang') == '00'][::-1]
                banner2 = banner2[0]['url'].encode('utf-8')
            except:
                banner2 = '0'

            try:
                if 'hdtvlogo' in art: clearlogo = art['hdtvlogo']
                else: clearlogo = art['clearlogo']
                clearlogo = [x for x in clearlogo if x.get('lang') == 'en'][::-1] + [x for x in clearlogo if x.get('lang') == '00'][::-1]
                clearlogo = clearlogo[0]['url'].encode('utf-8')
            except:
                clearlogo = '0'

            try:
                if 'hdclearart' in art: clearart = art['hdclearart']
                else: clearart = art['clearart']
                clearart = [x for x in clearart if x.get('lang') == 'en'][::-1] + [x for x in clearart if x.get('lang') == '00'][::-1]
                clearart = clearart[0]['url'].encode('utf-8')
            except:
                clearart = '0'

            item = {'title': title, 'originaltitle': title, 'year': year, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'poster2': poster2, 'banner': banner, 'banner2': banner2, 'fanart': fanart, 'fanart2': fanart2, 'clearlogo': clearlogo, 'clearart': clearart, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'cast': cast, 'plot': plot}
            item = dict((k,v) for k, v in item.iteritems() if not v == '0')
            self.list[i].update(item)

            if artmeta == False: raise Exception()

            meta = {'imdb': imdb, 'tvdb': tvdb, 'lang': self.lang, 'user': self.user, 'item': item}
            self.meta.append(meta)
        except:
            pass


    def tvshowDirectory(self, items):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        traktCredentials = trakt.getTraktCredentialsInfo()

        try: isOld = False ; control.item().getArt('type')
        except: isOld = True

        indicators = playcount.getTVShowIndicators(refresh=True) if action == 'tvshows' else playcount.getTVShowIndicators()

        flatten = True if control.setting('flatten.tvshows') == 'true' else False

        watchedMenu = control.lang(32068).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32066).encode('utf-8')

        unwatchedMenu = control.lang(32069).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32067).encode('utf-8')

        queueMenu = control.lang(32065).encode('utf-8')

        traktManagerMenu = control.lang(32070).encode('utf-8')

        nextMenu = control.lang(32053).encode('utf-8')


        for i in items:
            try:
                label = i['title']
                systitle = sysname = urllib.quote_plus(i['originaltitle'])
                sysimage = urllib.quote_plus(i['poster'])
                imdb, tvdb, year = i['imdb'], i['tvdb'], i['year']

                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
                meta.update({'mediatype': 'tvshow'})
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, sysname)})
                if not 'duration' in i: meta.update({'duration': '60'})
                elif i['duration'] == '0': meta.update({'duration': '60'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except: pass

                try:
                    overlay = int(playcount.getTVShowOverlay(indicators, tvdb))
                    if overlay == 7: meta.update({'playcount': 1, 'overlay': 7})
                    else: meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass


                if flatten == True:
                    url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s' % (sysaddon, systitle, year, imdb, tvdb)
                else:
                    url = '%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tvdb=%s' % (sysaddon, systitle, year, imdb, tvdb)


                cm = []

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                cm.append((watchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&query=7)' % (sysaddon, systitle, imdb, tvdb)))

                cm.append((unwatchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tvdb=%s&query=6)' % (sysaddon, systitle, imdb, tvdb)))

                cm.append((control.lang(30268).encode('utf-8'), 'RunPlugin(%s?action=tvshowToLibrary&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&tvrage=%s)' % (sysaddon, systitle, year, imdb, '0', tvdb, '0')))

                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&tvdb=%s&content=tvshow)' % (sysaddon, sysname, tvdb)))

                if isOld == True:
                    cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))


                item = control.item(label=label)

                art = {}

                if 'poster' in i and not i['poster'] == '0':
                    art.update({'icon': i['poster'], 'thumb': i['poster'], 'poster': i['poster']})
                #elif 'poster2' in i and not i['poster2'] == '0':
                    #art.update({'icon': i['poster2'], 'thumb': i['poster2'], 'poster': i['poster2']})
                else:
                    art.update({'icon': addonPoster, 'thumb': addonPoster, 'poster': addonPoster})

                if 'banner' in i and not i['banner'] == '0':
                    art.update({'banner': i['banner']})
                #elif 'banner2' in i and not i['banner2'] == '0':
                    #art.update({'banner': i['banner2']})
                elif 'fanart' in i and not i['fanart'] == '0':
                    art.update({'banner': i['fanart']})
                else:
                    art.update({'banner': addonBanner})

                if 'clearlogo' in i and not i['clearlogo'] == '0':
                    art.update({'clearlogo': i['clearlogo']})

                if 'clearart' in i and not i['clearart'] == '0':
                    art.update({'clearart': i['clearart']})

                if settingFanart == 'true' and 'fanart' in i and not i['fanart'] == '0':
                    item.setProperty('Fanart_Image', i['fanart'])
                #elif settingFanart == 'true' and 'fanart2' in i and not i['fanart2'] == '0':
                    #item.setProperty('Fanart_Image', i['fanart2'])
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setArt(art)
                item.addContextMenuItems(cm)
                item.setInfo(type='Video', infoLabels = meta)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass
            
        if items[0]['next'] != 'SDPSearch':
            try:
##            url = items[0]['next']
##            if url == '': raise Exception()

                icon = control.addonNext()
                url = '%s?action=tvshowPagePall&url=%s' % (sysaddon, 'SDPtodos')#urllib.quote_plus(url))

                item = control.item(label=nextMenu)

                item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
                if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        control.content(syshandle, 'tvshows')
        control.directory(syshandle, cacheToDisc=True)
        views.setView('tvshows', {'skin.confluence': 500})


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


