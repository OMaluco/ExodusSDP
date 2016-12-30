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

from resources.lib.modules import cleantitle
from resources.lib.modules import cloudflare
from resources.lib.modules import client
from resources.lib.modules import client_genesis
from resources.lib.modules import jsunpack
from resources.lib.modules import resolversSdP
from resources.lib.modules import openload

addon_id = 'plugin.video.exodusSDP'
selfAddon = xbmcaddon.Addon(id=addon_id)

class source:
    def __init__(self):
        self.base_link = 'http://tugahd.com'
##        self.search_link = '/index.php/component/search/?tmpl=raw&type=json&ordering=&searchphrase=all&searchword='#'/index.php/component/search/?'#'/index.php/component/finder/search?q='
##        self.search_link = '/index.php/component/finder/search?q='
        self.user = selfAddon.getSetting('tugahd_user')
        self.password = selfAddon.getSetting('tugahd_password')
        
        self.loginview = 'http://tugahd.com/index.php/a-minha-conta/editar-perfil/?view=login'
        self.login = 'http://tugahd.com/index.php/a-minha-conta/editar-perfil?task=user.login'
        self.logout = 'http://tugahd.com/index.php/a-minha-conta/editar-perfil'
        self.search = 'http://tugahd.com/index.php/component/search/'


    def movie(self, imdb, title, year):
        try:
            if (self.user == '' or self.password == ''): raise Exception()
            
            result = client.request(self.loginview, output='extended', close=False)
            #print result
            if 'O pedido mais recente foi rejeitado porque continha um certificado' not in result:
                cookie = result[4]
                #print '1 -------------'+ cookie
    ##            headers = {'User-Agent': result[3]['User-Agent'], 'Cookie': result[4]}
    ##            print headers
                result=str(result)
                result = client.parseDOM(result, 'div', attrs = {'class': 'login'})[0]
                ret = client.parseDOM(result, "input", attrs = { "type": "hidden" }, ret = "name")
                ret1 = client.parseDOM(result, "input", attrs = { "type": "hidden" }, ret = "value")
                #print result
                #print ret
                #print ret1
                post = urllib.urlencode({'username': self.user, 'password': self.password, ret[0]: ret1[0], ret[1]: '1'})
                #print post
                r = client.request(self.login, post=post, cookie=cookie, output='extended', close=False)
                #print r
                cookie = str(cookie.replace(' ','|'))+'|'
                #print '1.1++++++++++'+cookie
                cookie = re.compile('__cfduid[=](.+?)[|]cf_clearance[=](.+?)[|].+?[|]').findall(cookie)
                #print cookie[0][0]
                #print cookie[0][1]
                cookie = '__cfduid=' + str(cookie[0][0]) + ' ' + 'cf_clearance=' + str(cookie[0][1]) + ' ' + r[4]
                #print '2 -------------'+cookie
            else:
                cookie = result[1]
                #print '3 --------------'+cookie

            #print cookie
            post = urllib.urlencode({'searchword':title, 'task': 'search', 'option': 'com_search', 'Itemid': '200'})
            result = client.request(self.search, post=post, cookie=cookie, output='extended', close=False)
            #cookie = result[1]
            result=str(result)            
            #print '+++++++++'+cookie
            #print result
                                                 
##            post = urllib.urlencode({'Submit': 'Terminar sessão', 'option': 'com_users', 'task': 'user.logout', ret[0]: ret[0], ret[1]: '1'})
##            r = client.request(logout, post=post, output='extended', cookie=cookie)
##            print r

            result = client.parseDOM(result, 'article', attrs = {'class': 'uk-article'})

            urls = ''
            for results in result:
                result_url = re.compile('href="(.+?)"').findall(results)[0]
                result_url = self.base_link + result_url
                #print result_url
                try:
                    resultado = client.request(result_url, cookie=cookie, output='extended')
                    resultado = str(resultado)
                except: resultado = ''
                #print resultado
                try:
                    #result_imdb = re.compile('<a class="imdb" href="https://www.imdb.com/title/(.+?)/" target="_blank">').findall(resultado)[0]
                    result_imdb = client.parseDOM(resultado, "a", attrs = { "class": "imdb" }, ret = "href")[0]
                except:result_imdb='result_imdb'
                if imdb in result_imdb:
                    id_source = client.parseDOM(resultado, "div", attrs = { "class": "nn_tabs outline_handles outline_content align_left top" })[0]
                    id_source = client.parseDOM(id_source, "div", attrs = { "class": "tab-pane nn_tabs-pane" })
                    #print id_source
                    for i in range(len(id_source)):
                        ids_sources = str(id_source[i])
                        id_ = client.parseDOM(ids_sources, 'a', ret = 'id')[0]
                        source_url = client.parseDOM(ids_sources, 'iframe', ret='src')[0]
                        #print source_url
                        #print id_
                        if 'trailer' not in id_:
                            source_url = self.base_link + source_url
                            source_url = client.request(source_url)
                            source_url = client.parseDOM(source_url, 'iframe', ret='src')[0]
                            urls = urls + 'id='+id_ +'url='+ source_url + '|'
                    break

            if urls != '': url = urls
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, year):
        try:
##            
##            result = client.request(self.loginview, output='extended', close=False)
##
##            if 'O pedido mais recente foi rejeitado porque continha um certificado' not in result:
##                cookie = result[4]
##                result=str(result)
##                result = client.parseDOM(result, 'div', attrs = {'class': 'login'})[0]
##                ret = client.parseDOM(result, "input", attrs = { "type": "hidden" }, ret = "name")
##                ret1 = client.parseDOM(result, "input", attrs = { "type": "hidden" }, ret = "value")
##
##                post = urllib.urlencode({'username': self.user, 'password': self.password, ret[0]: ret1[0], ret[1]: '1'})
##
##                r = client.request(self.login, post=post, cookie=cookie, output='extended', close=False)
##
##                cookie = str(cookie.replace(' ','|'))+'|'
##
##                cookie = re.compile('__cfduid[=](.+?)[|]cf_clearance[=](.+?)[|].+?[|]').findall(cookie)
##
##                cookie = '__cfduid=' + str(cookie[0][0]) + ' ' + 'cf_clearance=' + str(cookie[0][1]) + ' ' + r[4]
##
##            else:
##                cookie = result[1]
##
##            post = urllib.urlencode({'searchword':tvshowtitle, 'task': 'search', 'option': 'com_search', 'Itemid': '200'})
##            result = client.request(self.search, post=post, cookie=cookie, output='extended', close=False)
##            
##            result=str(result)            
##
##            result = client.parseDOM(result, 'article', attrs = {'class': 'uk-article'})
##
##            for results in result:
##                result_url = re.compile('href="(.+?)"').findall(results)[0]
##                result_url = self.base_link + result_url
##
##                try:
##                    resultado = client.request(result_url, cookie=cookie, output='extended')
##                    resultado = str(resultado)
##                except: resultado = ''
##                               
##                try:
##                    result_imdb = client.parseDOM(resultado, "a", attrs = { "class": "imdb" }, ret = "href")[0]
##                except:result_imdb='result_imdb'
##                
##                if imdb in result_imdb:
##                    url = result_url
##                    break
            url = 'http://'+imdb+'/'+tvshowtitle+'|'
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            
            it = re.compile('http://(.+?)/(.+?)[|]').findall(url)
            imdb = it[0][0]
            tvshowtitle = it[0][1]

            result = client.request(self.loginview, output='extended', close=False)

            if 'O pedido mais recente foi rejeitado porque continha um certificado' not in result:
                cookie = result[4]
                #print 'Cookie1 ------------------' +cookie
                result=str(result)
                result = client.parseDOM(result, 'div', attrs = {'class': 'login'})[0]
                ret = client.parseDOM(result, "input", attrs = { "type": "hidden" }, ret = "name")
                ret1 = client.parseDOM(result, "input", attrs = { "type": "hidden" }, ret = "value")

                post = urllib.urlencode({'username': self.user, 'password': self.password, ret[0]: ret1[0], ret[1]: '1'})

                r = client.request(self.login, post=post, cookie=cookie, output='extended', close=False)

                cookie = str(cookie.replace(' ','|'))+'|'

                cookie = re.compile('__cfduid[=](.+?)[|]cf_clearance[=](.+?)[|].+?[|]').findall(cookie)

                cookie = '__cfduid=' + str(cookie[0][0]) + ' ' + 'cf_clearance=' + str(cookie[0][1]) + ' ' + r[4]
                #print 'Cookie2 ------------------' +cookie

            else:
                cookie = result[1]
                #print 'Cookie3 ------------------' +cookie

            post = urllib.urlencode({'searchword':tvshowtitle, 'task': 'search', 'option': 'com_search', 'Itemid': '200'})
            result = client.request(self.search, post=post, cookie=cookie, output='extended', close=False)
            
            result=str(result)            

            result = client.parseDOM(result, 'article', attrs = {'class': 'uk-article'})
            urls=''
            for results in result:
                result_url = re.compile('href="(.+?)"').findall(results)[0]
                result_url = self.base_link + result_url + '|'

                #print '+++++++++++++++++++'+result_url
                se = re.compile('http://tugahd.com/index.php/series/ordem-alfabetica/.+?/(.+?)/(.+?)[|]').findall(result_url)
                result_url = result_url.replace(se[0][0],season+'-temporada').replace(se[0][1],'episodio-'+episode).replace('|','')
                #print '+++++++++++++++++++'+result_url

                try:
                    resultado = client.request(result_url, cookie=cookie, output='extended')
                    resultado = str(resultado)
                    #print resultado
                except: resultado = ''

                id_source = client.parseDOM(resultado, "div", attrs = { "class": "nn_tabs outline_handles outline_content align_left top" })[0]
                id_source = client.parseDOM(id_source, "div", attrs = { "class": "tab-pane nn_tabs-pane" })
                #print id_source
                for i in range(len(id_source)):
                    ids_sources = str(id_source[i])
                    id_ = client.parseDOM(ids_sources, 'a', ret = 'id')[0]
                    host_url = client.parseDOM(ids_sources, 'iframe', ret='src')[0]
                    #print host_url
                    #print id_
                    if 'trailer' not in id_:
                        host_url = self.base_link + host_url.replace(' ','%20')
                        #print host_url
##                        print cookie
##                        page = urllib.urlopen(host_url).read()
##                        print page
                        host_url = client.request(host_url)
                        #print host_url
##                        host_url = str(host_url)
##                        print host_url
##                        host_url = client.parseDOM(host_url, 'iframe', ret='src')[0]
##                        urls = urls + 'id='+id_ +'url='+ host_url + '|'

                try:
                    result_imdb = client.parseDOM(resultado, "a", attrs = { "class": "imdb" }, ret = "href")[0]
                except:result_imdb='result_imdb'
                
                if imdb in result_imdb:
                    url = result_url
                    break
                        
##            if url == None: return
##            print '========================='+url
##            #url = '%s S%02dE%02d' % (url, int(season), int(episode))
##            url = url + 'EPISODIO'+episode+'EPISODIOSEASON'+season+'SEASON'
##            url = client.replaceHTMLCodes(url)
##            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
##        sources = []
##        sources.append({'source': 'TugaHD', 'quality': 'HD', 'provider': 'TugaHD'+url, 'url': url, 'direct': False, 'debridonly': False})
        try:
            sources = []
            
            if url == None: return sources

            procura = 'FILME'
            
##            if 'EPISODIO' in url:
##                
##                result = client.request(self.loginview, output='extended', close=False)
##
##                if 'O pedido mais recente foi rejeitado porque continha um certificado' not in result:
##                    cookie = result[4]
##                    result=str(result)
##                    result = client.parseDOM(result, 'div', attrs = {'class': 'login'})[0]
##                    ret = client.parseDOM(result, "input", attrs = { "type": "hidden" }, ret = "name")
##                    ret1 = client.parseDOM(result, "input", attrs = { "type": "hidden" }, ret = "value")
##
##                    post = urllib.urlencode({'username': self.user, 'password': self.password, ret[0]: ret1[0], ret[1]: '1'})
##
##                    r = client.request(self.login, post=post, cookie=cookie, output='extended', close=False)
##
##                    cookie = str(cookie.replace(' ','|'))+'|'
##
##                    cookie = re.compile('__cfduid[=](.+?)[|]cf_clearance[=](.+?)[|].+?[|]').findall(cookie)
##
##                    cookie = '__cfduid=' + str(cookie[0][0]) + ' ' + 'cf_clearance=' + str(cookie[0][1]) + ' ' + r[4]
##
##                else:
##                    cookie = result[1]
##                    print '-----------------'+ cookie
##                    
##                procura = 'EPISODIO'
##                url = re.compile('(.+?)EPISODIO(\d+)EPISODIOSEASON(\d+)SEASON').findall(url)
##                episodio = str(url[0][1])
##                season = str(url[0][2])
##                if int(episodio) < 10: e = 'E0'+episodio
##                else: e = 'E'+episodio
##                if int(season) < 10: t = 'S0'+season
##                else: t = 'S'+season
##                S_E = t+e
##                url = url[0][0]+'|'
##
##                print '+++++++++++++++++++'+url
##                se = re.compile('http://tugahd.com/index.php/series/ordem-alfabetica/.+?/(.+?)/(.+?)[|]').findall(url)
##                url = url.replace(se[0][0],season+'-temporada').replace(se[0][1],'episodio-'+episodio).replace('|','')
##                print '+++++++++++++++++++'+url
##                try:
##                    resultado = client.request(url, cookie=cookie)#, output='extended')
##                    resultado = str(resultado)
##                except: resultado = ''
##                print resultado
##                
##                id_source = client.parseDOM(resultado, "div", attrs = { "class": "nn_tabs outline_handles outline_content align_left top" })[0]
##                id_source = client.parseDOM(id_source, "div", attrs = { "class": "tab-pane nn_tabs-pane" })
##                print id_source
##                for i in range(len(id_source)):
##                    ids_sources = str(id_source[i])
##                    id_ = client.parseDOM(ids_sources, 'a', ret = 'id')[0]
##                    host_url = client.parseDOM(ids_sources, 'iframe', ret='src')[0]
##                    print host_url
##                    print id_
##                    if 'trailer' not in id_:
##                        host_url = self.base_link + host_url
##                        print host_url
##                        print cookie
##                        host_url = client.request(host_url)
##                        print host_url
##                        host_url = str(host_url)
##                        print host_url
##                        host_url = client.parseDOM(host_url, 'iframe', ret='src')[0]
##                        #urls = urls + 'id='+id_ +'url='+ source_url + '|'
##
##                        audio_filme = ''
##                        if 'pt-pt' in id_: audio_filme = ' | PT-PT'
##                       # elif 'v-o' in id_: audio_filme = ' | V.O.'
##                        else: audio_filme = ''
##                        
##                        try:
##                            quality = id_.strip().upper()
##                            if '1080P' in quality: quality = '1080p'
##                            elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or 'HDTV' in quality or '720P' in quality: quality = 'HD'
##                            elif 'SCREENER' in quality: quality = 'SCR'
##                            elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
##                            else: quality = 'SD'
##                        except: quality = 'HD'
##
##                        #host_url = re.compile('url=(.*)').findall(host)[0]
##
##                        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
##                        host = client.replaceHTMLCodes(host)
##                        host = host.encode('utf-8')
##
##                        sources.append({'source': host, 'quality': quality, 'provider': 'TugaHD'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False})
            
            
            if procura == 'FILME':
                ids = re.compile('(.+?)[|]').findall(url)
                for i in ids:
                    print i
                    id_ = re.compile('id=(.+?)url').findall(i)[0]
                    
                    audio_filme = ''
                    if 'pt-pt' in id_: audio_filme = ' | PT-PT'
                   # elif 'v-o' in id_: audio_filme = ' | V.O.'
                    else: audio_filme = ''
                    
                    try:
                        quality = id_.strip().upper()
                        if '1080P' in quality: quality = '1080p'
                        elif 'BRRIP' in quality or 'BDRIP' in quality or 'HDRIP' in quality or 'HDTV' in quality or '720P' in quality: quality = 'HD'
                        elif 'SCREENER' in quality: quality = 'SCR'
                        elif 'CAM' in quality or 'TS' in quality: quality = 'CAM'
                        else: quality = 'SD'
                    except: quality = 'HD'

                    host_url = re.compile('url=(.*)').findall(i)[0]

                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host_url.strip().lower()).netloc)[0]
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    sources.append({'source': host, 'quality': quality, 'provider': 'TugaHD'+audio_filme, 'url': host_url, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources


    def resolve(self, url):
        if 'openload' in url:
            url = openload.OpenLoad(url).getMediaUrl()
        return url


    
def createCookie(url,cj=None,agent='Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0'):
    urlData=''
    try:
        import urlparse,cookielib,urllib2

        class NoRedirection(urllib2.HTTPErrorProcessor):    
            def http_response(self, request, response):
                return response

        def parseJSString(s):
            try:
                offset=1 if s[0]=='+' else 0
                val = int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:]))
                return val
            except:
                pass

        #agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'
        if cj==None:
            cj = cookielib.CookieJar()

        opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', agent)]
        response = opener.open(url)
        result=urlData = response.read()
        response.close()
#        print result
#        print response.headers
        jschl = re.compile('name="jschl_vc" value="(.+?)"/>').findall(result)[0]

        init = re.compile('setTimeout\(function\(\){\s*.*?.*:(.*?)};').findall(result)[0]
        builder = re.compile(r"challenge-form\'\);\s*(.*)a.v").findall(result)[0]
        decryptVal = parseJSString(init)
        lines = builder.split(';')

        for line in lines:
            if len(line)>0 and '=' in line:
                sections=line.split('=')

                line_val = parseJSString(sections[1])
                decryptVal = int(eval(str(decryptVal)+sections[0][-1]+str(line_val)))

#        print urlparse.urlparse(url).netloc
        answer = decryptVal + len(urlparse.urlparse(url).netloc)

        u='/'.join(url.split('/')[:-1])
        query = '%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s' % (u, jschl, answer)

        if 'type="hidden" name="pass"' in result:
            passval=re.compile('name="pass" value="(.*?)"').findall(result)[0]
            query = '%s/cdn-cgi/l/chk_jschl?pass=%s&jschl_vc=%s&jschl_answer=%s' % (u,urllib.quote_plus(passval), jschl, answer)
            xbmc.sleep(4*1000) ##sleep so that the call work
            
 #       print query
#        import urllib2
#        opener = urllib2.build_opener(NoRedirection,urllib2.HTTPCookieProcessor(cj))
#        opener.addheaders = [('User-Agent', agent)]
        #print opener.headers
        response = opener.open(query)
 #       print response.headers
        #cookie = str(response.headers.get('Set-Cookie'))
        #response = opener.open(url)
        #print cj
#        print response.read()
        response.close()

        return urlData
    except:
        traceback.print_exc(file=sys.stdout)
        return urlData



                

