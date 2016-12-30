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


import os,re,urllib,urllib2,urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import cloudflare
from resources.lib.modules import client_genesis
from resources.lib.modules import client
from resources.lib.modules import jsunpack
from resources.lib.modules import resolversSdP

from resources.lib.modules import recaptcha_v2
from resources.lib.modules import control

from resources.lib.modules import openload


class source:
    def __init__(self):
        self.base_link = 'http://tugaflix.com'
        self.search_link = '/Filmes?G=&O=1&T='
        self.searchSeries_link = '/Series?G=&O=1&T='


    def movie(self, imdb, title, year):
        try:
##            titulo = title
##            genero = ''
##            try: genero = self.get_genre(imdb)                
##            except: pass
##            if genero == 'Animation':
##                try: titulo = self.get_portuguese_name(imdb)                
##                except: titulo = title
            
            query = self.base_link+self.search_link+str(title.replace(' ','+'))

            result = client_genesis.request(query)
            
            result = client.parseDOM(result, 'div', attrs = {'class': 'browse-movie-bottom'})
            result = str(result)
            result = client.parseDOM(result, 'a', ret='href')
            #result = re.compile('<div class="browse-movie-wrap.+?"> <a href="(.+?)" class="browse-movie-link"> <figure>').findall(result)
            
            for result_url in result:
                try:result_imdb = re.compile('=(.*)').findall(result_url)[0]
                except:result_imdb='result_imdb'                
                if imdb == 'tt'+result_imdb:                                
                        url = self.base_link+'/Filme?F='+result_imdb
                        break
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, year):
        try:
            query = self.base_link+self.searchSeries_link+str(tvshowtitle.replace(' ','+'))

            result = client_genesis.request(query)
            result = client.parseDOM(result, 'div', attrs = {'class': 'browse-movie-bottom'})
            result = str(result)
            result = client.parseDOM(result, 'a', ret='href')
            #result = re.compile('<div class="browse-movie-wrap.+?"> <a href="(.+?)" class="browse-movie-link"> <figure>').findall(result)
            
            for result_url in result:
                try:result_imdb = re.compile('=(.*)').findall(result_url)[0]
                except:result_imdb='result_imdb'                
                if imdb == 'tt'+result_imdb:                                
                        url = self.base_link+'/Serie?S='+result_imdb
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

##        sources = []
##        sources.append({'source': 'TugaFlix', 'quality': 'HD', 'provider': 'TugaFlix'+url, 'url': url, 'direct': False, 'debridonly': False})

        try:
            sources = []
            
            if url == None: return sources

            referer_url = url

            procura = 'FILME'
            
            if 'EPISODIO' in url:
                procura = 'EPISODIO'
                url = re.compile('(.+?)EPISODIO(\d+)EPISODIOSEASON(\d+)SEASON').findall(url)
                episodio = str(url[0][1])
                season = str(url[0][2])
                if int(episodio) < 10: e = 'E0'+episodio
                else: e = 'E'+episodio
                if int(season) < 10: t = 'S0'+season
                else: t = 'S'+season
                S_E = t+e
                url = url[0][0]

            try: result = client_genesis.request(url)
            except: result = ''
            
            audio_filme = ''
            try:
                titulo = client.parseDOM(result, 'h1', attrs = {'class': 'title'})[0]
                if 'PT-PT' in titulo or 'PORTUGU' in titulo: audio_filme = ' | PT-PT'
                else: audio_filme = ''
            except: audio_filme = ''
            try:
                quality = url.strip().upper()
                if '1080P' in quality: quality = '1080p'
                elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or 'HDTV' in quality or '720P' in quality: quality = 'HD'
                elif 'SCREENER' in quality: quality = 'SCR'
                elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                else: quality = 'SD'
            except: quality = 'SD'

            if procura == 'EPISODIO':
                #result = client.parseDOM(result, 'a', attrs = {'class': 'browse-movie-link'})
                result = re.compile('<a class="browse-movie-link"(.+?)<h6 class="gridepisode2">').findall(result)
                for results in result:
                    #print results
                    if S_E in results.upper():
                        url = re.compile('href="(.+?)"><figure>').findall(results)[0]
                        url = self.base_link+url
                        sources.append({'source': 'TugaFlix', 'quality': 'HD', 'provider': 'TugaFlix', 'url': url, 'direct': False, 'debridonly': False})
            elif procura == 'FILME':
                sources.append({'source': 'TugaFlix', 'quality': 'HD', 'provider': 'TugaFlix', 'url': url, 'direct': False, 'debridonly': False})
            
            return sources
        except:
            return sources
        

    def resolve(self, url):
        try:cookie = client.request(url+'&HD', output='cookie')
        except:cookie = client.request(url, output='cookie')
        ##print 'COOKIE -++++++++++++++++++++++ '+cookie
        
        try: result = client_genesis.request(url)
        except: result = ''
        
        key=re.compile('data-sitekey="(.+?)">').findall(result)[0]
        ##print 'KEY -++++++++++++++++++++++ '+key
        
        token=recaptcha_v2.UnCaptchaReCaptcha().processCaptcha(key,'pt-Pt')
        ##print 'TOKEN +++++++++++++++++++++ '+token
        
        post = urllib.urlencode({'g-recaptcha-response': token})
        try:result = client.request(url+'&HD', post=post, cookie=cookie)
        except:result = client.request(url, post=post, cookie=cookie)
        ##print result

        url = re.compile('<iframe src="(.+?)" scrolling="no"').findall(result)[0]

        if 'openload' in url:
            url = openload.OpenLoad(url).getMediaUrl()
        ##print 'URL -++++++++++++++++++++++ '+url

        return url
##        try:
##            if 'Video?V=http://servidor' in url:
##                url = resolversSdP.tugaflixPlayer(url)
##            return url
##        except:
##            return
        

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
            #print t
            
            genre = re.compile('<span class="itemprop" itemprop="genre">(.+?)</span></a>').findall(result.replace('\n',''))
            for i in genre:
                #print i
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
        

    def abrir_url(self, url):            
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
