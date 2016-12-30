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


import re,urllib,urllib2,urlparse,xbmcaddon

import sys,traceback,urllib2,re, urllib,xbmc

from array import array
from resources.lib.modules import cleantitle
from resources.lib.modules import cloudflare
from resources.lib.modules import client
from resources.lib.modules import client_genesis
from resources.lib.modules import jsunpack

class source:
    def __init__(self):
        self.base_link = 'http://anituga.net/'
        self.search = 'http://anituga.net/index.php'


    def movie(self, imdb, title, year):
        try:

            titulo = title
            genero = ''
            try: genero = self.get_genre(imdb)                
            except: pass
            if genero == 'Animation':
                try:
                    titulo = self.get_portuguese_name(imdb)
                    titulo = titulo.replace('+',' ')
                except: titulo = title
            
            cookie = client.request(self.base_link, output='cookie', close=False)

##            print 'anituga---------'+titulo
##            print 'anituga---------'+cookie

            post = urllib.urlencode({'do': 'search', 'subaction': 'search', 'story': titulo})
            result = client.request(self.base_link, post=post, cookie=cookie, close=False)

            result = re.compile('<p class="search-page-p">(.+?)<div class="clearfix"></div>').findall(result.replace('\n',''))[0]
            result=str(result)
##            print result
            result = client.parseDOM(result, 'div', attrs = {'class': 'short-images radius-3'})

            for results in result:
##                print results
                result_url = client.parseDOM(results, 'a', ret = 'href')[0]
                result_title = client.parseDOM(results, 'img', ret = 'alt')[0]
##                print result_url
##                print '1------'+result_title
##                try:
##                    resultado = client.request(result_url, cookie=cookie)
##                    resultado = str(resultado)
##                except: resultado = ''
##                print resultado
                cleantitle.get(titulo)
                cleantitle.get(result_title)
##                print '2-----'+titulo.replace(' ','').upper()
##                print '3----------'+result_title.replace(' ','').upper()
                if titulo.replace(' ','').upper() in result_title.replace(' ','').upper():
                    url = result_url+'|'+str(cookie)
                    break

            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, year):
        try:
            titulo = tvshowtitle
##            genero = ''
##            try: genero = self.get_genre(imdb)                
##            except: pass
##            if genero == 'Animation':
##                try:
##                    titulo = self.get_portuguese_name(imdb)
##                    titulo = titulo.replace('+',' ')
##                except: titulo = tvshowtitle
            
            cookie = client.request(self.base_link, output='cookie', close=False)

##            print 'anituga---------'+titulo
##            print 'anituga---------'+cookie

            post = urllib.urlencode({'do': 'search', 'subaction': 'search', 'story': titulo})
            result = client.request(self.base_link, post=post, cookie=cookie, close=False)

            result = re.compile('<p class="search-page-p">(.+?)<div class="clearfix"></div>').findall(result.replace('\n',''))[0]
            result=str(result)
##            print result
            result = client.parseDOM(result, 'div', attrs = {'class': 'short-images radius-3'})

            for results in result:
                result_url = client.parseDOM(results, 'a', ret = 'href')[0]
                result_title = client.parseDOM(results, 'a', ret = 'title')[0]
##                print result_url
##                print result_title
##                try:
##                    resultado = client.request(result_url, cookie=cookie)
##                    resultado = str(resultado)
##                except: resultado = ''
##                print resultado

                if tvshowtitle.upper() in result_title.upper():
                    url = result_url+'|'+str(cookie)
                    break
                
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            #url = '%s S%02dE%02d' % (url, int(season), int(episode))
            url = url + 'EPISODIO'+episode+'EPISODIOSEASON'+season+'SEASON'
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
####        sources = []
####        sources.append({'source': 'Anituga', 'quality': 'HD', 'provider': 'Anituga'+url, 'url': url, 'direct': False, 'debridonly': False})
        try:
            sources = []
            
            if url == None: return sources

            if 'EPISODIO' not in url:
                procura = 'FILME'
                uc = re.compile('(.+?)[|](.*)').findall(url)
                url = uc[0][0]
                cookie = uc[0][1]
            else:
                procura = 'EPISODIO'
                uc = re.compile('(.+?)[|](.+?)EPISODIO(\d+)EPISODIOSEASON(\d+)SEASON').findall(url)
                url = uc[0][0]
                cookie = uc[0][1]
                episodio = str(uc[0][2])
                season = str(uc[0][3])
                if int(episodio) < 10: e = 'E0'+episodio
                else: e = 'E'+episodio
                if int(season) < 10: t = 'S0'+season
                else: t = 'S'+season
                S_E = t+e


            if procura == 'FILME':
                
                try:
                    resultado = client.request(url, cookie=cookie)#, output='extended')
                    resultado = str(resultado)
                except: resultado = ''
                print resultado
                
                id_ = client.parseDOM(resultado, "div", attrs = { "class": "tab-pane fade" }, ret="id")
                idd_ = client.parseDOM(resultado, "div", attrs = { "class": "tab-pane fade in active" }, ret="id")
                ids_ = []
                ids_.append(str(idd_[0]))
                for i in id_:
                    ids_.append(str(i))
                
                id_source = client.parseDOM(resultado, "div", attrs = { "class": "video-responsive" })
                r = 0
                for i in range(len(id_source)):
                    ids_sources = str(id_source[i])
                    if 'iframe' not in ids_sources:
                        host_url = client.parseDOM(ids_sources, "script", ret="src")[0]
                        print host_url

                        audio_filme = ''
                        versao = re.compile('<li><a href="#'+str(ids_[r])+'" role="tab" data-toggle="tab">(.+?)</a></li>').findall(resultado)[0]
                        if 'DOBRADO PT' in versao.upper(): audio_filme = ' | PT-PT'
                        else: audio_filme = ''
                        
                        try:
                            quality = versao.upper()
                            if '1080P' in quality: quality = '1080p'
                            elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or 'HDTV' in quality or '720P' in quality: quality = 'HD'
                            elif 'SCREENER' in quality: quality = 'SCR'
                            elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                            else: quality = 'SD'
                        except: quality = 'HD'

                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')

                        sources.append({'source': host, 'quality': quality, 'provider': 'Anituga'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False})

                        r = r + 1
                        
            elif procura == 'EPISODIO':
##                print '+++++++++++++++++++'+url
##                se = re.compile('http://tugahd.com/index.php/series/ordem-alfabetica/.+?/(.+?)/(.+?)[|]').findall(url)
##                url = url.replace(se[0][0],season+'-temporada').replace(se[0][1],'episodio-'+episodio).replace('|','')
##                print '+++++++++++++++++++'+url
                try:
                    resultado = client.request(url, cookie=cookie)#, output='extended')
                    resultado = str(resultado)
                except: resultado = ''
                #print resultado
                    
                id_ = client.parseDOM(resultado, "div", attrs = { "class": "tab-pane fade" }, ret="id")
                idd_ = client.parseDOM(resultado, "div", attrs = { "class": "tab-pane fade in active" }, ret="id")
                ids_ = []
                ids_.append(str(idd_[0]))
                for i in id_:
                    ids_.append(str(i))
                
                id_source = client.parseDOM(resultado, "div", attrs = { "class": "video-responsive" })
                r = 0
                for i in range(len(id_source)):
                    ids_sources = str(id_source[i])
                    if 'iframe' not in ids_sources:
                        host_url = client.parseDOM(ids_sources, "script", ret="src")[0]
                        print host_url

                        audio_filme = ''
                        versao = re.compile('<li><a href="#'+str(ids_[r])+'" role="tab" data-toggle="tab">(.+?)</a></li>').findall(resultado)[0]
                        if 'DOBRADO PT' in versao.upper(): audio_filme = ' | PT-PT'
                        else: audio_filme = ''
                        
                        try:
                            quality = versao.upper()
                            if '1080P' in quality: quality = '1080p'
                            elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or 'HDTV' in quality or '720P' in quality: quality = 'HD'
                            elif 'SCREENER' in quality: quality = 'SCR'
                            elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                            else: quality = 'SD'
                        except: quality = 'HD'

                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')

                        sources.append({'source': host, 'quality': quality, 'provider': 'Anituga'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False})

                        r = r + 1
            
            return sources
        except:
            return sources

    def get_portuguese_name(self, imdb):

        titulo = ''

        query = 'http://www.imdb.com/title/'+str(imdb)
       
        try:
            req = urllib2.Request(query)
            req.add_header('User-Agent','Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko')
            response = urllib2.urlopen(req)
            result=response.read()
            response.close()

            t = re.compile('<title>(.+?)</title>').findall(result.replace('\n',''))[0]
            t = str(re.compile('(.+?)[(]').findall(t)[0])
            t = t.replace('í','i')
            print t
            
            genre = re.compile('<span class="itemprop" itemprop="genre">(.+?)</span></a>').findall(result.replace('\n',''))
            for i in genre:
                print i
                if 'Animation' in i:
                    titulo = t
                    break
              
            return urllib.quote_plus(titulo)
        except:
            return

    def get_genre(self, imdb):

        genero = ''

        query = 'http://www.imdb.com/title/'+str(imdb)
       
        try:
            req = urllib2.Request(query)
            req.add_header('User-Agent','Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko')
            response = urllib2.urlopen(req)
            result=response.read()
            response.close()
            
            genre = re.compile('<span class="itemprop" itemprop="genre">(.+?)</span></a>').findall(result.replace('\n',''))
            for i in genre:
                if 'Animation' in i:
                    genero = 'Animation'
                    break
              
            return urllib.quote_plus(genero)
        except:
            return

        
    def resolve(self, url):
        return url


