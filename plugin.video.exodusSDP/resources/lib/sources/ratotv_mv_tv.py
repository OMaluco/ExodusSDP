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


import re,urllib,urllib2,urlparse,xbmcaddon,xbmc,xbmcplugin,xbmcgui,xbmcvfs

import os
import traceback

from resources.lib.modules import cleantitle
from resources.lib.modules import cloudflare
from resources.lib.modules import client
from resources.lib.modules import client_genesis
from resources.lib.modules import jsunpack
from resources.lib.modules import resolversSdP
from resources.lib.modules import openload
from resources.lib.modules import jsunpacker
from resources.lib.modules import control

addon_id = 'plugin.video.exodusSDP'
selfAddon = xbmcaddon.Addon(id=addon_id)

pastaLegendasSDP = os.path.join(control.dataPath,'legendasSDP')
if not os.path.exists(pastaLegendasSDP): control.makeFile(pastaLegendasSDP)

class source:
    def __init__(self):
        self.tralhas = "http://tralhas.xyz/geturl/url.txt"
        self.base_link = self.rato_base_url()
        self.search_link = '?do=search&subaction=search&search_start=1&story='
        self.user = selfAddon.getSetting('ratotv_user')
        self.password = selfAddon.getSetting('ratotv_password')

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


    def movie(self, imdb, title, year):
        try:
            
            if (self.user == '' or self.password == ''): raise Exception()

            query = self.base_link
            post = urllib.urlencode({'login': 'submit', 'login_name': self.user, 'login_password': self.password})
            cookie = client_genesis.source(query, post=post, output='cookie')

            query = self.base_link+self.search_link+str(title.replace(' ','+'))
            result = client_genesis.request(query, post=post, cookie=cookie, referer=self.base_link)
            
            result = client.parseDOM(result, 'div', attrs = {'class': 'shortpost'})
            urls = ''
            for results in result:
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                print result_url
                try:
                    result_imdb = re.compile('imdb.com/title/(.+?)/"').findall(results.replace(' ',''))[0]
                except:
                    result_imdb='result_imdb'
                if imdb == result_imdb:                                
                        urls = urls+result_url+'|'
            if urls != '': url = urls+'IMDB'+imdb+'IMDB'
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, year):

        try:
            if (self.user == '' or self.password == ''): raise Exception()

            query = self.base_link
            post = urllib.urlencode({'login': 'submit', 'login_name': self.user, 'login_password': self.password})
            cookie = client_genesis.source(query, post=post, output='cookie')
            
            query = self.base_link+self.search_link+str(tvshowtitle.replace(' ','+'))
            result = client_genesis.request(query, post=post, cookie=cookie, referer=self.base_link)

            if cookie: a = cookie
            else: a = 'nao'
            
            result = client.parseDOM(result, 'div', attrs = {'class': 'shortpost'})
            
            urls = ''
            for results in result:                
                result_url = client.parseDOM(results, 'a', ret='href')[0]
                try:
                    result_imdb = re.compile('imdb.com/title/(.+?)/"').findall(results.replace(' ',''))[0]
                except:
                    result_imdb='result_imdb'
                if imdb == result_imdb:                                
                        urls = urls+result_url+'|'
            if urls != '': url = urls
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = url.replace('|','')
            #url = '%s S%02dE%02d' % (url, int(season), int(episode))
            url = url + 'EPISODIO'+episode+'EPISODIOSEASON'+season+'SEASONIMDB'+imdb+'IMDB'
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
##        sources = []
##        sources.append({'source': 'gdrive', 'quality': 'HD', 'provider': 'RatoTV', 'url': 'https://drive.google.com/file/d/0B8kCEtrnzKhDUzJrckloQURXVDA/edit', 'direct': False, 'debridonly': False})
        try:
            sources = []

            if url == None: return sources

            options = []
            leg = []
            legendas = ''

            idb = re.compile('IMDB(.+?)IMDB').findall(url)[0]
            url = re.compile('(.+?)IMDB.+?IMDB').findall(url)[0]

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

                options = resolversSdP.series_seasons(url,season,episodio,self.user,self.password)
                for i in options:
                    nome_source = str(i['source'])
                    leg.append(str(i['subs']))
                    legendas = str(i['subs'])
                    if nome_source == 'NONE':
                        host_url = i['url']
                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')

                        sources.append({'source': host, 'quality': 'SD', 'provider': 'RatoTV', 'url': host_url, 'direct': False, 'debridonly': False, 'legendas': legendas})
                    else:
                        quality = str(i['quality'])
                        try:
                            quality = quality.strip().upper()
                            if '1080P' in quality: quality = '1080p'
                            elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or '480P' in quality: quality = 'HD'
                            elif 'SCREENER' in quality: quality = 'SCR'
                            elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                            else: quality = 'SD'
                        except: quality = 'SD'
                        sources.append({'source': str(i['source']), 'quality': quality, 'provider': 'RatoTV', 'url': str(i['url']), 'direct': True, 'debridonly': False, 'legendas': legendas})
            else:
                result = re.compile('(.+?)[|]').findall(url)
                for url in result:
                    options = self.get_host_options(url)
                    #if options == '': break
                    
                    for i in options:
                        print 'legendas------------------'+str(i['subs'])
                        if i['subs']:
                            leg.append(str(i['subs']))
                            legendas = str(i['subs'])
                        else: legendas = legendas
                        nome_source = str(i['source'])
                        if nome_source == 'NONE':
                            host_url = i['url']
                            host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                            host = client.replaceHTMLCodes(host)
                            host = host.encode('utf-8')
                            
                            sources.append({'source': host, 'quality': 'SD', 'provider': 'RatoTV', 'url': host_url, 'direct': False, 'debridonly': False, 'legendas': legendas})
                        else:
                            quality = str(i['quality'])
                            try:
                                quality = quality.upper()
                                if '1080P' in quality: quality = '1080p'
                                elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or '480P' in quality: quality = 'HD'
                                elif 'SCREENER' in quality: quality = 'SCR'
                                elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                                else: quality = 'SD'
                            except: quality = 'SD'
                            sources.append({'source': str(i['source']), 'quality': quality, 'provider': 'RatoTV', 'url': str(i['url']), 'direct': True, 'debridonly': False, 'legendas': legendas})
                            
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
        

    def get_host_options(self, url):#, sourc=None):
        opcoes = []
        try:
            opcoes = resolversSdP.get_options(url, self.user, self.password)#, sourc)
        except: pass
        return opcoes
    

    def resolve(self, url):
        u = url
        if 'openload' in url:
            try:
                url = openload.OpenLoad(url).getMediaUrl()
            except: url = u
        return url
                

