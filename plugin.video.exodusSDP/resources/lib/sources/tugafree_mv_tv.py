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
from resources.lib.modules import jsunpacker

pastaLegendasSDP = os.path.join(control.dataPath,'legendasSDP')
if not os.path.exists(pastaLegendasSDP): control.makeFile(pastaLegendasSDP)

class source:
    def __init__(self):
        self.base_link = 'http://tugafree.com'
        self.search_link = '/?s='


    def movie(self, imdb, title, year):
        try:
            
            query = self.base_link+self.search_link+str(title.replace(' ','+'))
            #print query+'-----------------------------------'

            try: result = client_genesis.request(query)
            except: result = ''

            result = client.parseDOM(result, 'div', attrs = {'class': 'article'})[0]
            result = client.parseDOM(result, 'div', attrs = {'class': 'post-data-container'})
            
            a = str(len(result))
            
            for results in result:
                result_url = client.parseDOM(results, 'a', ret='href')[0]

                try: result = client_genesis.request(result_url)
                except: result = ''
                
                try:result_imdb = re.compile('imdb.com/title/(.+?)/').findall(result)[0]
                except:result_imdb='result_imdb'
                
                if imdb == result_imdb:                                
                        url = result_url+'IMDB'+imdb+'IMDB'
                        break
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, year):
        try:

            query = self.base_link+self.search_link+str(tvshowtitle.replace(' ','+'))

            try: result = client_genesis.request(query)
            except: result = ''
            result = re.compile('<h2 class="title post-title">(.+?)</h2>').findall(result)
            
            a = str(len(result))
            
            for results in result:
                result_url = re.compile('href="(.+?)"').findall(results)[0]
                try: result = client_genesis.request(result_url)
                except: result = ''
                try:result_imdb = re.compile('imdb.com/title/(.+?)/').findall(result)[0]
                except:result_imdb='result_imdb'                
                if imdb == result_imdb:                                
                        url = result_url+'IMDB'+imdb+'IMDB'
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
##        sources.append({'source': 'TugaFree', 'quality': 'HD', 'provider': 'TugaFree'+url, 'url': url, 'direct': False, 'debridonly': False})
        try:
            sources = []
            
            leg = []

            legendas = ''
            
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
                url = url[0][0]
                result = client_genesis.request(url)
                result = client.parseDOM(result.replace('\n',''), 'div', attrs = {'class': 'su-spoiler su-spoiler-style-fancy su-spoiler.+?'})
                for results in result:
                    if 'Episodio '+episodio in results or 'Episodio '+str(int(episodio)-1)+' e '+episodio: result = results
            else:
                try: result = client_genesis.request(url)
                except: result = ''
            
            try:
                quality = url.strip().upper()
                if '1080P' in quality: quality = '1080p'
                elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality: quality = 'HD'
                elif 'SCREENER' in quality: quality = 'SCR'
                elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                else: quality = 'SD'
            except: quality = 'HD'
            
            audio_filme = ''
            try:
                audio = url.upper()
                if 'PT-PT' in audio or 'PORTUGU' in audio: audio_filme = ' | PT-PT'
                else:
                    audio_filme = ''
                    legendas = 'AUDIO PT'
            except:
                audio_filme = ''
                legendas = ''

            resultado = re.compile('data-mfp-src="(.+?)"').findall(result.replace('\n','').replace(' ',''))
            
            for host_url in resultado:
                                
                host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                host = client.replaceHTMLCodes(host)
                host = host.encode('utf-8')

                if 'rapidvideo' in host.lower():
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
                            else:legendas = legendas
                            try:
                                quality = quality.upper()
                                if '1080P' in quality: quality = '1080p'
                                elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or '480P' in quality: quality = 'HD'
                                elif 'SCREENER' in quality: quality = 'SCR'
                                elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                                else: quality = 'SD'
                            except: quality = 'SD'
                            sources.append({'source': host, 'quality': quality, 'provider': 'TugaFree'+audio_filme, 'url': ru, 'direct': True, 'debridonly': False, 'legendas': legendas})
                            if len(leg) == 1: i = 0
                            else: i = i + 1
                    except: pass

                elif 'vidzi' in host:
                    try:
                        vidzi = Vidzi(host_url)
                        urli = vidzi.getMediaUrl()
                        lege = vidzi.getSubtitle()
                        if lege: legendas = lege.replace('\/','/')
                        else: legendas = legendas
                        leg.append(str(legendas))
                        ##print 'vidzi------------'+legendas
                    except: pass
                    
                if 'youtube' not in host.lower() and 'rapidvideo' not in host.lower():
                    sources.append({'source': host, 'quality': quality, 'provider': 'TugaFree'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False})
                    
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
        

    def resolve(self, url):
        if 'openload' in url:
            url = openload.OpenLoad(url).getMediaUrl()
        return url

class Vidzi():
	def __init__(self, url):
		self.url = url
		#self.net = Net()
		self.id = str(self.getId())
		#self.messageOk = xbmcgui.Dialog().ok
		self.site = 'http://vidzi.tv'
		self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}
		self.subtitle = ''

	def getId(self):
		return re.compile('http\:\/\/vidzi.tv\/embed-(.+?)-').findall(self.url)[0]

	def getNewHost(self):
		return 'http://vidzi.tv/embed-%s.html' % (self.id)

	def getMediaUrl(self):
		sourceCode = client.request(self.getNewHost(), headers=self.headers)#.content

		match = re.search('file\s*:\s*"([^"]+)', sourceCode)
		if match:
			return match.group(1) + '|Referer=http://vidzi.tv/nplayer/jwpayer.flash.swf'
		else:
			for pack in re.finditer('(eval\(function.*?)</script>', sourceCode, re.DOTALL):
				dataJs = jsunpacker.unpack(pack.group(1)) # Unpacker for Dean Edward's p.a.c.k.e.r | THKS

				##print dataJs
				#pprint.pprint(dataJs)

				stream = re.search('file\s*:\s*"([^"]+)', dataJs)
				try:
					subtitle = re.compile('tracks:\[\{file:"(.+?)\.srt"').findall(dataJs)[0]
					subtitle += ".srt"
				except:
					try:
						subtitle = re.compile('tracks:\[\{file:"(.+?)\.vtt"').findall(dataJs)[0]
						subtitle += ".vtt"
					except:
						subtitle = ''
				self.subtitle = subtitle

				if stream:
					return stream.group(1)


	def getSubtitle(self):
		return self.subtitle

