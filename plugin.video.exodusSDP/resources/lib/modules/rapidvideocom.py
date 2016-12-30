# -*- coding: utf-8 -*-
"""
urlresolver XBMC Addon
Copyright (C) 2011 t0mm0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import re
import random
import urlresolver
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
from urlresolver.plugins.lib import helpers


class RapidVideoResolver(UrlResolver):
    name = "rapidvideo.com"
    domains = ["rapidvideo.com"]
    pattern = '(?://|\.)(rapidvideo\.com)/(?:embed/|\?v=)?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        #print web_url
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        data = helpers.get_hidden(html)
        data['confirm.y'] = random.randint(0, 120)
        data['confirm.x'] = random.randint(0, 120)
        headers['Referer'] = web_url
        post_url = web_url + '#'
        html = self.net.http_POST(post_url, form_data=data, headers=headers).content.encode('utf-8')
##        sources = helpers.parse_sources_list(html)
##        try: sources.sort(key=lambda x: x[0], reverse=True)
##        except: pass
##        return helpers.pick_source(sources)

        sourc = []
        legenda = []
        try:
            le = re.compile('"file":"([^"]+)","label":".+?","kind":"captions"').findall(html)
            for l in le:
                legenda.append(l.replace('\/', '/'))
        except: pass
        match = re.search('''['"]?sources['"]?\s*:\s*\[(.*?)\]''', html, re.DOTALL)
        if match:
            sourc = [(match[1], match[0].replace('\/', '/')) for match in re.findall('''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([^'"]*)''', match.group(1), re.DOTALL)]        
        return sourc,legenda

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://www.rapidvideo.com/embed/{media_id}')
