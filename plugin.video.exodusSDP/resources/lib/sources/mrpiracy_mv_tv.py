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


import re,urllib,urllib2,urlparse,xbmcaddon,xbmc,xbmcplugin,xbmcgui,xbmcvfs,json

import os
import traceback
import base64

from resources.lib.modules import cleantitle
from resources.lib.modules import cloudflare
from resources.lib.modules import client
from resources.lib.modules import client_genesis
from resources.lib.modules import jsunpack
from resources.lib.modules import resolversSdP
from resources.lib.modules import googlevideo
from resources.lib.modules import openload
from resources.lib.modules import jsunpacker
from resources.lib.modules import control

addon_id = 'plugin.video.exodusSDP'
selfAddon = xbmcaddon.Addon(id=addon_id)
logado = selfAddon.getSetting('loggedin')

pastaLegendasSDP = os.path.join(control.dataPath,'legendasSDP')
if not os.path.exists(pastaLegendasSDP): control.makeFile(pastaLegendasSDP)

class source:
    def __init__(self):
        self.API_SITE = base64.urlsafe_b64decode('aHR0cDovL215YXBpbXAudGsvYXBpLw==')#'http://mrpiracy.win/api/'
        self.base_link = base64.urlsafe_b64decode('aHR0cDovL21ycGlyYWN5Lm1sLw==')#'http://mrpiracy.win/'
        self.SITE = base64.urlsafe_b64decode('aHR0cDovL21ycGlyYWN5Lm1sLw==')
        self.search_movie_link = self.base_link+'procurarf.php'
        self.search_serie_link = self.base_link+'kodi_procurars.php'
        self.search_anime_link = self.base_link+'kodi_procuraranime.php'
        self.user = selfAddon.getSetting('mrpiracy_user')
        self.password = selfAddon.getSetting('mrpiracy_password')
        #self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'} #ISO-8859-1,
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'utf-8;q=0.7,*;q=0.7', 'Content-Type': 'application/json'}
    

    def movie(self, imdb, title, year):
        try:

            if (self.user == '' or self.password == ''): raise Exception()

            #if logado == '': self.login()
            self.login()

            self.headers['Authorization'] = 'Bearer %s' % selfAddon.getSetting('tokenMrpiracy')

            post = {'pesquisa': title}
            result = client.request(self.API_SITE+'filmes/pesquisa',post=json.dumps(post), headers=self.headers)

            acesso = self.verificar_acesso(result)
            if acesso == 'retry': result = client.request(self.API_SITE+'filmes/pesquisa',post=json.dumps(post), headers=self.headers)
            
            result = json.loads(result)
##            print 'ÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇÇ'
##            print result
            urls = ''            
            for i in result['data']:
                result_imdb= re.compile("u'IMBD': u'(.+?)'").findall(str(i))[0]
                if imdb in result_imdb:                        
                    urls = urls + self.API_SITE+'filme/'+str(i['id_video']) + '|'

            if urls != '': url = urls+'IMDB'+imdb+'IMDB'
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, year):
        try:
            if (self.user == '' or self.password == ''): raise Exception()
            
            #if logado == '': self.login()
            self.login()
                
            self.headers['Authorization'] = 'Bearer %s' % selfAddon.getSetting('tokenMrpiracy')

            post = {'pesquisa': tvshowtitle}
            result = client.request(self.API_SITE+'series/pesquisa',post=json.dumps(post), headers=self.headers)

            acesso = self.verificar_acesso(result)
            if acesso == 'retry': result = client.request(self.API_SITE+'series/pesquisa',post=json.dumps(post), headers=self.headers)
            
            result = json.loads(result)
            
            urls = ''            
            for i in result['data']:
                result_imdb= re.compile("u'IMBD': u'(.+?)'").findall(str(i))[0]
                if imdb in result_imdb:
                    url = urls + self.API_SITE+'serie/'+str(i['id_video']) + '|'

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
##        sources.append({'source': 'MrPiracy', 'quality': 'HD', 'provider': 'MrPiracy'+url, 'url': url, 'direct': True, 'debridonly': False})
##
        try:
            sources = []

            leg = []

            legendas = ''
            
            if url == None: return sources

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
                url = url[0][0]+'/temporada/'+season+'/episodio/'+episodio+'|'                

            self.headers['Authorization'] = 'Bearer %s' % selfAddon.getSetting('tokenMrpiracy')
            
            urls = []
            try:
                ls = re.compile('(.+?)[|]').findall(url)
                for l in ls:
                    urls.append(l)
            except: urls.append(url)

            for url in urls:

                subs = ''
                
                resultado = client.request(url, headers=self.headers)
                
                acesso = self.verificar_acesso(resultado)
                if acesso == 'retry':
                    self.headers['Authorization'] = 'Bearer %s' % selfAddon.getSetting('tokenMrpiracy')
                    resultado = client.request(url, headers=self.headers)
                    
                resultado = json.loads(resultado)

                servidores = []
                if resultado['URL'] != '': servidores.append(resultado['URL'])
                if resultado['URL2'] != '': servidores.append(resultado['URL2'])
                try:
                    if resultado['URL3'] != '': servidores.append(resultado['URL3'])
                except: pass
                try:
                    if resultado['URL4'] != '': servidores.append(resultado['URL4'])
                except: pass

                legendas = ''                
		if '://' in resultado['legenda']:
		    legendas = self.SITE+'subs/%s.srt' % resultado['IMBD']
		    leg.append(str(legendas))
		    subs = legendas
		elif resultado['legenda'] != '':
		    if not '.srt' in resultado['legenda']:
			    resultado['legenda'] = resultado['legenda']+'.srt'
		    legendas = self.SITE+'subs/%s' % resultado['legenda']
		    leg.append(str(legendas))
                    subs = legendas

                for host_url in servidores:

                    audio_filme = ''
                    try:
                        categoria = resultado['categoria1']
			if resultado['categoria2'] != '':
				categoria += ','+resultado['categoria2']
			if resultado['categoria3'] != '':
				categoria += ','+resultado['categoria3']
                        au = re.compile("u'IMBD': u'(.+?)',").findall(str(resultado))[0]
                        audio = host_url.upper()
                        if 'PT-PT' in audio or 'PORTUGU' in audio or '-PT' in audio or 'PT' in str(au) or 'Portu' in categoria:
                            audio_filme = ' | PT-PT'
                            legendas = 'AUDIO PT'
                        else:
                            audio_filme = ''
                            legendas = subs
                    except:
                        audio_filme = ''
                        legendas = subs

                    if 'google' in host_url:
                        links = []
                        resulturl = []
                        resposta, links = googlevideo.GoogleResolver()._parse_google(host_url)
                        for i in links:
                            quality = i[0]+"p"
                            try:
                                quality = quality.upper()
                                if '1080P' in quality: quality = '1080p'
                                elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or '480P' in quality: quality = 'HD'
                                elif 'SCREENER' in quality: quality = 'SCR'
                                elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                                else: quality = 'SD'
                            except: quality = 'SD'
                            sources.append({'source': 'gdrive', 'quality': quality, 'provider': 'MrPiracy'+audio_filme, 'url': i[1], 'direct': True, 'debridonly': False, 'legendas': legendas})

                    elif 'uptostreaming' in host_url:#uptostream
                        links = []
                        resulturl = []
                        links = UpToStream(host_url).getMediaUrl()
                        for i in links:
                            print i
                            quality = re.compile('http://.+?/.+?/(.+?)/.+?/.+?').findall(i)[0]
                            quality = quality + "p"
                            try:
                                quality = quality.upper()
                                if '1080P' in quality: quality = '1080p'
                                elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or '480P' in quality: quality = 'HD'
                                elif 'SCREENER' in quality: quality = 'SCR'
                                elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                                else: quality = 'SD'
                            except: quality = 'SD'
                            sources.append({'source': 'uptostream', 'quality': quality, 'provider': 'MrPiracy'+audio_filme, 'url': str(i), 'direct': False, 'debridonly': False, 'legendas': legendas})
                    else:
                        try:
                            quality = host_url.strip().upper()
                            if '1080P' in quality: quality = '1080p'
                            elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality: quality = 'HD'
                            elif 'SCREENER' in quality: quality = 'SCR'
                            elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                            else: quality = 'SD'
                        except: quality = 'HD'
                        
                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        
                        if legendas == '':
                            if 'openload' in host:
                                try:
                                    urli = openload.OpenLoad(host_url).getMediaUrl()
                                    lege = openload.OpenLoad(host_url).getSubtitle()
                                    if lege: legendas = lege.replace('\/','/')
                                    else: legendas = legendas
                                    leg.append(str(legendas))
                                    #print legendas
                                except: pass                            
                            elif 'vidzi' in host:
                                try:
                                    vidzi = Vidzi(host_url)
                                    urli = vidzi.getMediaUrl()
                                    lege = vidzi.getSubtitle()
                                    if lege: legendas = lege.replace('\/','/')
                                    else: legendas = legendas
                                    leg.append(str(legendas))
                                    #print 'vidzi------------'+legendas
                                except: pass
                            elif 'rapidvideo' in host:
                                try:
                                    rapidurl = []
                                    rapid = RapidVideo(host_url)
                                    rapidurl = rapid.getMediaUrl()
                                    lege = rapid.getLegenda()
                                    if lege: legendas = lege.replace('\/','/')
                                    else: legendas = legendas
                                    leg.append(str(legendas))
                                    for rl in rapidurl:
                                        quality = rl[0]
                                        ru = rl[1]
                                        try:
                                            quality = quality.upper()
                                            if '1080P' in quality: quality = '1080p'
                                            elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or '720P' in quality or '480P' in quality: quality = 'HD'
                                            elif 'SCREENER' in quality: quality = 'SCR'
                                            elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                                            else: quality = 'SD'
                                        except: quality = 'SD'
                                        sources.append({'source': host, 'quality': quality, 'provider': 'MrPiracy'+audio_filme, 'url': ru, 'direct': False, 'debridonly': False, 'legendas': legendas})
                                    #print legendas
                                except: pass
                        if 'rapidvideo' not in host:
                            sources.append({'source': host, 'quality': quality, 'provider': 'MrPiracy'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False, 'legendas': legendas})
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
##        elif 'uptostream' in url:
##            url = UpToStream(url).getMediaUrl()
##        elif 'vidzi' in url:
##            try:
##                vidzi = Vidzi(url)
##                url = vidzi.getMediaUrl()
##                legendas = vidzi.getSubtitle()
##                print legendas
##	    except: pass
##        elif 'rapidvideo' in url:
##            try:
##                rapid = RapidVideo(url)
##                url = rapid.getMediaUrl()
##                legendas = rapid.getLegenda()
##                #print legendas
##	    except: pass
	elif 'mail' in url:
            try:
                url, ext_g = CloudMailRu(url).getMediaUrl()
                #print url
            except:pass
        return url

    def login(self):                                                                                                            #pyRmmKK3cbjouoDMLXNtt2eGkyTTAG
        post = {'username': self.user, 'password': self.password,'grant_type': 'password', 'client_id': 'kodi', 'client_secret':'pyRmmKK3cbjouoDMLXNtt2eGkyTTAG' }

        resultado = client.request(self.API_SITE+'login', post=json.dumps(post), headers=self.headers)
        #resultado = self.abrir_url(self.API_SITE+'login', post=json.dumps(post), header=self.headers)

        resultado = json.loads(resultado)

        token = resultado['access_token']
        refresh = resultado['refresh_token']
        headersN = self.headers
        headersN['Authorization'] = 'Bearer %s' % token
                      
        resultado = client.request(self.API_SITE+'me', headers=headersN)
        #resultado = self.abrir_url(self.API_SITE+'me', header=headersN)
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

    def verificar_acesso(self, resultado):
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

    def abrir_url(self, url, post=None, header=None, code=False, erro=False):

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

        """if 'myapimp.tk' in url:
            xbmc.log(url)
            coiso = json.loads(link)
            if 'error' in coiso:
                if coiso['error'] == 'access_denied':
                    xbmc.log("REFRESH")
                    headers['Authorization'] = 'Bearer %s' % addon.getSetting('tokenMrpiracy')
                    dados = {'refresh_token': addon.getSetting('refreshMrpiracy'),'grant_type': 'refresh_token', 'client_id': 'kodi', 'client_secret':'pyRmmKK3cbjouoDMLXNtt2eGkyTTAG' }
                    
                    resultado = abrir_url(base64.urlsafe_b64decode('aHR0cDovL215YXBpbXAudGsvYXBpLw==')+'token/refresh',post=json.dumps(dados), header=headers)

                    resultado = json.loads(resultado)
                    addon.setSetting('tokenMrpiracy', resultado['access_token'])
                    addon.setSetting('refreshMrpiracy', resultado['refresh_token'])
                    if post:
                        return abrir_url(url, post=post, header=header)
                    else:
                        return abrir_url(url, header=header)
                if coiso['error'] == 'invalid_request' and coiso['error_description'] == 'The refresh token is invalid.':
                    xbmc.log("LOGIN")
                    dados = {'username': addon.getSetting('email'), 'password': addon.getSetting('password'),'grant_type': 'password', 'client_id': 'kodi', 'client_secret':'pyRmmKK3cbjouoDMLXNtt2eGkyTTAG' }
                    resultado = abrir_url(base64.urlsafe_b64decode('aHR0cDovL215YXBpbXAudGsvYXBpLw==')+'login',post=json.dumps(dados), header=headers)
                    resultado = json.loads(resultado)
                    addon.setSetting('tokenMrpiracy', resultado['access_token'])
                    addon.setSetting('refreshMrpiracy', resultado['refresh_token'])
                    if post:
                        return abrir_url(url, post=post, header=header)
                    else:
                        return abrir_url(url, header=header)

        """
        if 'judicial' in link:
            return 'DNS'
        if code:
            return str(response.code), link

        response.close()
        return link



class UpToStream():
	def __init__(self, url):
		self.url = url
		#self.net = Net()
		self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'utf-8;q=0.7,*;q=0.7'}

	def getId(self):
		if 'iframe' in self.url:
			return re.compile('http\:\/\/uptostream\.com\/iframe\/(.+)').findall(self.url)[0]
		else:
			return re.compile('http\:\/\/uptostream\.com\/(.+)').findall(self.url)[0]

	def getMediaUrl(self):
		sourceCode = client.request(self.url, headers=self.headers)
                #print str(sourceCode)
		links = re.compile('source\s+src=[\'\"]([^\'\"]+)[\'\"].+?data-res=[\'\"]([^\"\']+)[\'\"]').findall(sourceCode)
		videos = []
		qualidades = []
		for link, qualidade in links:
			if link.startswith('//'):
				link = "http:"+link
			videos.append(link)
			qualidades.append(qualidade)
		videos.reverse()
		qualidades.reverse()
		print videos
		qualidade = xbmcgui.Dialog().select('Escolha a qualidade', qualidades)
		return videos[qualidade]

class RapidVideo():
	def __init__(self, url):
		self.url = url
		#self.net = Net()
		self.headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3"}
		self.legenda = ''
		self.rlinks = []

	def getId(self):
		return urlparse.urlparse(self.url).path.split("/")[-1]

	def getMediaUrl(self):
		try:
			sourceCode = client.request(self.url, headers=self.headers).decode('unicode_escape')
		except:
			sourceCode = client.request(self.url, headers=self.headers)#.content

		sPattern =  '"file":"([^"]+)","label":"([0-9]+)p"'
		aResult = self.parse(sourceCode, sPattern)
		try:
			self.legenda = re.compile('"file":"([^"]+)","label":".+?","kind":"captions"').findall(sourceCode)[0]
		except:
			self.legenda = ''
		videoUrl = ''
		if aResult[0]:
			links = []
			qualidades = []
			for aEntry in aResult[1]:
				links.append(aEntry[0])
				qualidades.append(aEntry[1]+'p')
				self.rlinks.append((str(aEntry[1])+'p', str(aEntry[0])))

			if len(links) == 1:
				videoUrl = links[0]
			elif len(links) > 1:
				links.reverse()
				qualidades.reverse()

##				qualidade = xbmcgui.Dialog().select('Escolha a qualidade', qualidades)
##				videoUrl = links[qualidade]

		return self.rlinks#videoUrl
	def getLegenda(self):
		return self.legenda
	def parse(self, sHtmlContent, sPattern, iMinFoundValue = 1):
		sHtmlContent = self.replaceSpecialCharacters(str(sHtmlContent))
		aMatches = re.compile(sPattern, re.IGNORECASE).findall(sHtmlContent)
		if (len(aMatches) >= iMinFoundValue):
			return True, aMatches
		return False, aMatches
	def replaceSpecialCharacters(self, sString):
		return sString.replace('\\/','/').replace('&amp;','&').replace('\xc9','E').replace('&#8211;', '-').replace('&#038;', '&').replace('&rsquo;','\'').replace('\r','').replace('\n','').replace('\t','').replace('&#039;',"'")

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

				#print dataJs
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
	    

class CloudMailRu():
	def __init__(self, url):
		self.url = url
		#self.net = Net()
		self.headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3"}

	def getId(self):
		return re.compile('(?:\/\/|\.)cloud\.mail\.ru\/public\/(.+)').findall(self.url)[0]
	def getMediaUrl(self):
		conteudo = client.request(self.url)
		ext = re.compile('<meta name=\"twitter:image\" content=\"(.+?)\"/>').findall(conteudo)[0]
		streamAux = clean(ext.split('/')[-1])
		extensaoStream = clean(streamAux.split('.')[-1])
		token = re.compile('"tokens"\s*:\s*{\s*"download"\s*:\s*"([^"]+)').findall(conteudo)[0]
		mediaLink = re.compile('"weblink_get"\s*:\s*\[.+?"url"\s*:\s*"([^"]+)').findall(conteudo)[0]
		videoUrl = '%s/%s?key=%s' % (mediaLink, self.getId(), token)
		return videoUrl, extensaoStream

def clean(text):
    command={'&#8220;':'"','&#8221;':'"', '&#8211;':'-','&amp;':'&','&#8217;':"'",'&#8216;':"'"}
    regex = re.compile("|".join(map(re.escape, command.keys())))
    return regex.sub(lambda mo: command[mo.group(0)], text)


