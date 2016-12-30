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


import os,sys,re,json,urllib,urllib2,urlparse,base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
#from resources.lib.modules import cloudflare
from resources.lib.modules import resolversSdP

class source:
    def __init__(self):
        print '##############################################'
        self.tmdbkey_key = '/?api_key='+base64.urlsafe_b64decode('OWY2YmIzYWE5ZGQ1NzliNGNmZjNmYmUxZGM4ODA5YzZiYzZmYTY0YQ==')
        self.basemovie_link = base64.urlsafe_b64decode('aHR0cDovL3NlbWJpbGhldGUudHYvL2FwaS92MS9jb250ZW50Lw==')
        self.basetvshow_link = base64.urlsafe_b64decode('aHR0cDovL3NlbWJpbGhldGUudHYvL2FwaS92MS9jb250ZW50Lw==')
        self.tmdbkey_user = '&username='+base64.urlsafe_b64decode('dGlja2V0')
        #self.search_link = '/?s=%s'
        

    def movie(self, imdb, title, year):
        try:
            url=self.basemovie_link+imdb+self.tmdbkey_key+self.tmdbkey_user
            url='http://sembilhete.ga/movie/'+imdb
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, year):

        try:
            url=self.basetvshow_link+imdb
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = url+'/season/'+str(season)+self.tmdbkey_key+self.tmdbkey_user
            url = url + 'EPISODIO'+episode+'EPISODIO'
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
##        sources = []
##        sources.append({'source': 'gvideo', 'quality': 'HD', 'provider': 'CinematugaHD'+url, 'url': url, 'direct': False, 'debridonly': False})
        try:
            sources = []

            if url == None: return sources

            procura = 'FILME'
            
            if 'EPISODIO' in url:
                procura = 'EPISODIO'
                url = re.compile('(.+?)EPISODIO(\d+)EPISODIO').findall(url)
                episodio = str(url[0][1])
                url = url[0][0]

                result = client.source(url.replace('/content/','/serie/'))
                result = json.loads(result)

                for i in result[u'episodes']:
                    if str(i[u'episode_number']) == episodio:
                        imdb = str(i[u'imdb_id'])
                        url = self.basemovie_link+imdb+self.tmdbkey_key+self.tmdbkey_user
                        break

                result = client.source(url.replace('/content/','/content/request/'))
                result = json.loads(result)
                print url.replace('/content/','/content/request/')+'#########################################'
                videourl = str(result[u'url'])
                
                ########
                try:
                    if 'uptostream' in videourl:
                        options = resolversSdP.resolve_upstream(videourl)
                    elif 'drive.google' in videourl:
                        options = resolversSdP.resolve_gdrive(videourl)
                    for i in options:
                        quality = str(i['quality'])
                        try:
                            quality = quality.strip().upper()
                            if '1080P' in quality: quality = '1080p'
                            elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or '480P' in quality: quality = 'HD'
                            elif 'SCREENER' in quality: quality = 'SCR'
                            elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                            else: quality = 'SD'
                        except: quality = 'SD'
                        sources.append({'source': str(i['provider']), 'quality': quality, 'provider': 'SemBilhete', 'url': str(i['url']), 'direct': True, 'debridonly': False})

                        #sources.append({'source': str(i['provider']), 'quality': quality, 'provider': 'SemBilhete', 'url': str(i['url'])})
                except: pass
                ########

            else:
                result = client.source(url.replace('/content/','/content/request/'))
                result = json.loads(result)

                videourl = str(result[u'url'])
                
                ########
                try:
                    if 'uptostream' in videourl:
                        options = resolversSdP.resolve_upstream(videourl)
                    elif 'drive.google' in videourl:
                        options = resolversSdP.resolve_gdrive(videourl)
                    for i in options:
                        print i
                        quality = str(i['quality'])
                        try:
                            quality = quality.strip().upper()
                            if '1080P' in quality: quality = '1080p'
                            elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or '480P' in quality: quality = 'HD'
                            elif 'SCREENER' in quality: quality = 'SCR'
                            elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                            else: quality = 'SD'
                        except: quality = 'SD'
                        sources.append({'source': str(i['provider']), 'quality': quality, 'provider': 'SemBilhete', 'url': str(i['url']), 'direct': True, 'debridonly': False})                

                        #sources.append({'source': str(i['provider']), 'quality': quality, 'provider': 'SemBilhete', 'url': str(i['url'])})
                except: pass
                #####
##                        
##                if 'uptostream' not in videourl and 'drive.google' not in videourl:
##                    sources.append({'source': 'SemBilhete', 'quality': 'HD', 'provider': 'SemBilhete'+videourl, 'url': videourl})
                

##            try:audiopt = re.compile('<b>AUDIO:</b>(.+?)<br/>').findall(result.replace(" ",''))[0]
##            except:audiopt = 'audio'
##            if 'PT' in audiopt.upper(): audio_filme = ' | PT-PT'
##            else: audio_filme = ''
##
##            try:
##                try:quality = re.compile('<b>VERS.+?:</b>(.+?)<br/>').findall(result.replace(' ',''))[0]
##                except:quality = re.compile('<b>RELEASE:</b>(.+?)<br/>').findall(result.replace(' ',''))[0]
##                quality = quality.strip().upper()
##                if 'CAM' in quality or 'TS' in quality: quality = 'CAM'
##                elif 'SCREENER' in quality: quality = 'SCR'
##                elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or 'HDTV' in quality or '720P' in quality: quality = 'HD'
##                elif '1080P' in quality: quality = '1080p'
##                else: quality = 'SD'
##            except: quality = 'SD'

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


