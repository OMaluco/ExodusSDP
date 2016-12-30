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
from resources.lib.modules import openload
from resources.lib.modules import control
from resources.lib.modules import rapidvideocom

pastaLegendasSDP = os.path.join(control.dataPath,'legendasSDP')
if not os.path.exists(pastaLegendasSDP): control.makeFile(pastaLegendasSDP)

class source:
    def __init__(self):
        self.base_link = 'http://www.moviefree.eu'
        self.search_link = '/?s='


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

            try: result = client_genesis.request(query)
            except: result = ''
            
            result = client.parseDOM(result, 'div', attrs = {'class': 'boxinfo'})            
            result = str(result)
            result = client.parseDOM(result, 'a', ret='href')
            
            urls = ''
            for result_url in result:
                try: result_imdb = client_genesis.request(result_url)
                except: result_imdb = ''
                try: result_imdb = client.parseDOM(result_imdb, 'div', attrs = {'class': 'imdb_r'})[0]
                except: result_imdb = ''
                if imdb in result_imdb:                                
                    urls = urls+result_url+'|'
            if urls != '': url = urls+'IMDB'+imdb+'IMDB'

            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, year):
        try:

            query = self.base_link+self.search_link+str(tvshowtitle.replace(' ','+'))

            try: result = client_genesis.request(query)
            except: result = ''
            
            result = client.parseDOM(result, 'div', attrs = {'class': 'boxinfo'})            
            #result = str(result)
            
            #print result

            for results in result:
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                result_title = re.compile('<span class="tt">(.+?)</span>').findall(results)[0]
                if result_title.upper() == tvshowtitle.upper():
                    url = result_url
                    break
            
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            #url = '%s S%02dE%02d' % (url, int(season), int(episode))
            url = url + 'EPISODIO'+episode+'EPISODIOSEASON'+season+'SEASONIMDB'+imdb+'IMDB'
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
##        sources = []
##        sources.append({'source': 'moviefree', 'quality': 'HD', 'provider': 'moviefree'+url, 'url': url, 'direct': False, 'debridonly': False})

        try:
            sources = []

            leg = []
            
            if url == None: return sources

            idb = re.compile('IMDB(.+?)IMDB').findall(url)[0]
            url = re.compile('(.+?)IMDB.+?IMDB').findall(url)[0]

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
                url = url[0][0].replace('tvshows','episodes')+'=='
                url = url.replace('/==','')+'-'+season+'x'+episodio

                try: result = client_genesis.request(url)
                except: result = ''

                #hosts = client.parseDOM(result, 'div', attrs = {'class': 'movieplay'})
                #hosts = re.compile('<iframe(.+?)</iframe>').findall(result.replace('\n',''))
                hosts = client.parseDOM(result, 'iframe', ret='src')
                for host_url in hosts:
                        
                    #host_url = re.compile('src="(.+?)"').findall(host_urls)[0]

                    audio_filme = ''
                    try:
                        titulo = re.compile('<h1 class="title">(.+?)</h1>').findall(result)[0]
                        if 'PT-PT' in titulo.upper() or 'PORTUGU' in titulo.upper(): audio_filme = ' | PT-PT'
                        else: audio_filme = ''
                    except: audio_filme = ''
                    try:
                        quality = host_url.strip().upper()
                        if '1080P' in quality: quality = '1080p'
                        elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality: quality = 'HD'
                        elif 'SCREENER' in quality: quality = 'SCR'
                        elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                        else: quality = 'SD'
                    except: quality = 'SD'
                        
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    sources.append({'source': host, 'quality': quality, 'provider': 'Moviefreept'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False})
   
                
            if procura == 'FILME':
                
                result = re.compile('(.+?)[|]').findall(url)

                for url in result:

                    legendas = ''
                    lele = ''

                    try: result = client_genesis.request(url)
                    except: result = ''

                    hosts = client.parseDOM(result, 'div', attrs = {'class': 'movieplay'})
                    #hosts = re.compile('<iframe(.+?)</iframe>').findall(result.replace('\n',''))
                    for host_urls in hosts:
                        
                        host_url = re.compile('src="(.+?)"').findall(host_urls)[0]

                        audio_filme = ''
                        try:
                            titulo = re.compile('<h1 class="title">(.+?)</h1>').findall(result)
                            if titulo: titulo = titulo[0]
                            else: titulo = ''
                            if 'PT-PT' in titulo.upper() or 'PORTUGU' in titulo.upper() or 'PORTUGU' in host_url.upper() or 'PT-PT' in host_url.upper():
                                audio_filme = ' | PT-PT'
                                legendas = 'AUDIO PT'
                            else:
                                audio_filme = ''
                                legendas = lele
                        except:
                            audio_filme = ''
                            legendas = lele
                        try:
                            quality = host_url.strip().upper()
                            if '1080P' in quality: quality = '1080p'
                            elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality: quality = 'HD'
                            elif 'SCREENER' in quality: quality = 'SCR'
                            elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                            else: quality = 'SD'
                        except: quality = 'SD'
                        
                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        print '-----------------------mooviefreept'+host_url
                        if 'rapidvideo' in host:
                            try:
                                padrao = re.compile('(?://|\.)(rapidvideo\.com)/(?:embed/|\?v=)?([0-9A-Za-z]+)').findall(host_url)
                                rapidurl = []
                                l = []
                                rapidurl,l = rapidvideocom.RapidVideoResolver().get_media_url(padrao[0][0],padrao[0][1])
                                if l != []:
                                    for ll in l:
                                        leg.append(str(ll))
                                i = 0
                                for rl in rapidurl:
                                    quality = rl[0]
                                    ru = rl[1]
                                    if l[i]:legendas = l[i]
                                    else:legendas = lele
                                    try:
                                        quality = quality.upper()
                                        if '1080P' in quality: quality = '1080p'
                                        elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or '480P' in quality: quality = 'HD'
                                        elif 'SCREENER' in quality: quality = 'SCR'
                                        elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                                        else: quality = 'SD'
                                    except: quality = 'SD'
                                    sources.append({'source': host, 'quality': quality, 'provider': 'Moviefreept'+audio_filme, 'url': ru, 'direct': True, 'debridonly': False, 'legendas': legendas})
                                    if len(leg) == 1: i = 0
                                    else: i = i + 1
                                    lele = legendas
                            except: pass
                            
                        elif 'rapidvideo' not in host:
                            
                            sources.append({'source': host, 'quality': quality, 'provider': 'Moviefreept'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False, 'legendas': legendas})
            try:
                leg = list(set(leg))
                if leg != []:
                    tempImdb = os.path.join(pastaLegendasSDP, str(idb)+'.txt')
                    file = open(tempImdb, 'r')
                    leitura=''
                    for linha in file:
                        leitura = leitura + str(linha)               
                    file.close()

                    file = open(tempImdb, 'a')                
                    for sub in leg:
                        if sub not in leitura: file.write(str(sub)+os.linesep)                
                    file.close()
            except:pass  
                        
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
        if 'openload' in url:
            url = openload.OpenLoad(url).getMediaUrl()
        return url
        

    def abrir_url(self, url):            
        req = urllib2.Request(url)
        req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link

