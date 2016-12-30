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
from resources.lib.modules import cache
from resources.lib.modules import playcount
from resources.lib.modules import workers
from resources.lib.modules import metacache
from resources.lib.modules import views

import os,sys,re,json,zipfile,StringIO,urllib,urllib2,urlparse,datetime,base64

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')

control.moderator()


class channels:
    def __init__(self):
        self.list = [] ; self.items = [] ; self.listEpisodes = []

        self.uk_datetime = self.uk_datetime()
        self.uk_datetime_mais = self.uk_datetime_mais()
        self.systime = (self.uk_datetime).strftime('%Y%m%d%H%M%S%f')
        self.imdb_by_query = 'http://www.omdbapi.com/?t=%s&y=%s'
        self.tm_img_link = 'https://image.tmdb.org/t/p/w%s%s'

        self.sky_now_link = 'http://epgservices.sky.com/5.1.1/api/2.0/channel/json/%s/now/nn/0'
        self.sky_programme_link = 'http://tv.sky.com/programme/channel/%s/%s/%s.json'

        ###########################

        self.trakt_link = 'http://api-v2launch.trakt.tv'
        self.tvmaze_link = 'http://api.tvmaze.com'
        self.tvdb_key = 'MUQ2MkYyRjkwMDMwQzQ0NA=='
        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
        self.today_date = (self.datetime).strftime('%Y-%m-%d')
        self.trakt_user = control.setting('trakt.user').strip()
        self.lang = control.apiLanguage()['tvdb']

        self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/all/%s.zip' % (self.tvdb_key.decode('base64'), '%s', '%s')
        self.tvdb_image = 'http://thetvdb.com/banners/'
        self.tvdb_poster = 'http://thetvdb.com/banners/_cache/'

        self.added_link = 'http://api.tvmaze.com/schedule'
        self.mycalendar_link = 'http://api-v2launch.trakt.tv/calendars/my/shows/date[29]/60/'
        self.trakthistory_link = 'http://api-v2launch.trakt.tv/users/me/history/shows?limit=300'
        self.progress_link = 'http://api-v2launch.trakt.tv/users/me/watched/shows'
        self.hiddenprogress_link = 'http://api-v2launch.trakt.tv/users/hidden/progress_watched?limit=1000&type=show'
        self.calendar_link = 'http://api.tvmaze.com/schedule?date=%s'

        self.traktlists_link = 'http://api-v2launch.trakt.tv/users/me/lists'
        self.traktlikedlists_link = 'http://api-v2launch.trakt.tv/users/likes/lists?limit=1000000'
        self.traktlist_link = 'http://api-v2launch.trakt.tv/users/%s/lists/%s/items'

        self.lang = control.apiLanguage()['tvdb']
        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        self.today_date = (self.datetime).strftime('%Y-%m-%d')
        self.tvdb_key = 'MUQ2MkYyRjkwMDMwQzQ0NA=='

        self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/all/%s.zip' % (self.tvdb_key.decode('base64'), '%s', '%s')
        self.tvdb_by_imdb = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s'
        self.tvdb_by_query = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s'
        self.imdb_by_query = 'http://www.omdbapi.com/?t=%s&y=%s'
        self.tvdb_image = 'http://thetvdb.com/banners/'
        self.tvdb_poster = 'http://thetvdb.com/banners/_cache/'


    def get(self): 
        channels = [
##                ('1', 'RTP 1', 'RTP1'),
##                ('2', 'RTP 2', 'RTP2'),
##                ('3', 'SIC', 'SIC'),
##                ('4', 'TVI', 'TVI'),
##                ('5', 'SIC Notícias', 'SICN'),
##                ('6', 'SIC Mulher', 'SICM'),
##                ('7', 'SIC Radical', 'SICR'),
##                ('8', 'RTP Memória', 'RTPM'),
##                ('9', 'RTP África', 'RTPA'),
##                ('10', 'SPORT.TV1', 'SPTV1'),
##                ('11', 'SPORT.TV2', 'SPTV2'),
##                ('12', 'SPORT.TV3', 'SPTV3'),
##                ('13', 'Eurosport', 'EURSP'),
##                ('14', 'Eurosport 2', 'EURS2'),
##                ('15', 'Eurosport News', 'EURSN'),
##                ('16', 'Benfica TV 1', 'SLB'),
                ('17', 'Cartoon Network', 'CART'),
##                ('18', 'Motors TV', 'MOTOR'),
##                ('19', 'PFC', 'PFC'),
##                ('20', 'Real Madrid', 'RMTV'),
                ('21', 'Panda', 'PANDA'),
##                ('22', 'TVCine 1', 'TVC1'),
##                ('23', 'TVCine 2', 'TVC2'),
##                ('24', 'TVCine 3', 'TVC3'),
##                ('25', 'Hollywood', 'HOLLW'),
##                ('26', 'AXN', 'AXN'),
##                ('27', 'FOX', 'FOX'),
##                ('28', 'FOX Crime', 'FOXCR'),
##                ('29', 'MTV Portugal', 'MTV'),
##                ('30', 'E! ENTERTAINMENT', 'E!'),
##                ('31', 'Globo Premium', 'GLOBO'),
##                ('32', 'Eurochannel', 'EURCH'),
##                ('33', 'Discovery Channel', 'DISCV'),
##                ('34', 'Odisseia', 'ODISS'),
##                ('35', 'National Geographic', 'NGC'),
##                ('36', 'Nat Geo Wild', 'NGWIL'),
##                ('37', 'História', 'HIST'),
##                ('38', 'Travel Channel', 'TRAV'),
##                ('39', 'MCM TOP', 'MCM T'),
##                ('40', 'MCM POP', 'MCM P'),
##                ('41', 'Trace TV', 'TRACE'),
##                ('42', 'VH1', 'VH1'),
##                ('43', 'Afro Music', 'AFRO'),
##                ('44', 'C-Music', 'C-MUS'),
##                ('45', 'MEZZO', 'MEZZO'),
##                ('46', 'Euronews', 'EURN'),
##                ('47', 'CNN', 'CNN'),
##                ('48', 'FOX News', 'FNEWS'),
##                ('49', 'BBC World', 'BBC W'),
##                ('50', 'Aljazeera', 'ALJAZ'),
##                ('51', 'France 24 (I)', 'FR24I'),
##                ('52', 'TVE24H', 'TVE24'),
##                ('53', 'ARTV', 'ARTV'),
##                ('54', 'M6', 'M6'),
##                ('55', 'FR24F', 'FR24F'),
##                ('56', 'CNBC Europe', 'CNBC'),
##                ('57', 'Bloomberg', 'BLOOM'),
##                ('58', 'TV Galicia', 'TVGAL'),
##                ('59', 'TVEi', 'TVEI'),
##                ('60', 'Cubavisión', 'CUBAV'),
##                ('61', 'TV5 Monde', 'TV5'),
##                ('62', 'Portuguesa', 'M POR'),
##                ('63', 'POP/ROCK', 'M POP'),
##                ('64', 'DISCO', 'M DIS'),
##                ('65', 'Funky & Hip Hop', 'M FNK'),
##                ('66', 'MÚSICA ALTERNATIVA', 'M ALT'),
##                ('67', 'Brasileira', 'M BRA'),
##                ('68', 'Romântica', 'M ROM'),
##                ('69', 'Jazz&Blues', 'M J&B'),
##                ('70', 'Clássica', 'M CLS'),
##                ('71', 'Ambiente', 'M AMB'),
##                ('72', 'Infantil', 'M INF'),
##                ('73', 'National Geographic HD', 'NGHD'),
##                ('74', 'LUXE TV HD', 'LUXHD'),
##                ('75', 'Eurosport HD', 'EURHD'),
##                ('76', 'Jukebox Mix', 'JUKE'),
##                ('77', 'Playboy TV', 'PLAY'),
##                ('78', 'RTP Madeira', 'RTPMD'),
##                ('79', 'RTP Açores', 'RTPAC'),
                ('80', 'Disney Channel', 'DISNY'),
##                ('81', 'JimJam', 'JJAM'),
                ('82', 'AXN HD', 'AXNHD'),
##                ('83', 'BRAVA HDTV', 'BVAHD'),
##                ('84', 'Sky News', 'SKYN'),
##                ('85', 'Deutsche Welle', 'DW-TV'),
##                ('86', 'SET Asia', 'SETAS'),
##                ('87', 'RTP1 HD', 'RTP1HD'),
##                ('88', 'Q', 'Q'),
                ('89', 'FOX HD', 'FOXHD'),
                ('90', 'FOX Life', 'FLIFE'),
                ('91', 'SyFy HD', 'SYFHD'),
##                ('92', 'FTV HD', 'FTVHD'),
##                ('93', 'CAÇAVISION', 'CAÇAV'),
##                ('94', 'TPA Internacional', 'TPA'),
##                ('95', 'INTER+', 'INTER+'),
##                ('96', 'CHANNEL 1 RUSSIA', '1RUSS'),
##                ('97', 'Russia Today', 'RUSST'),
##                ('98', 'PRO TV Internacional', 'PROTV'),
##                ('99', 'BNT', 'BNT'),
##                ('100', 'Phoenix CNE', 'PHCNE'),
##                ('101', 'SET MAX', 'MAX'),
##                ('102', 'Novidades', 'M NOV'),
##                ('103', 'Vénus', 'VENUS'),
##                ('104', 'Barça TV', 'BARCA'),
##                ('105', 'SyFy', 'SYFY'),
##                ('106', 'Food Network', 'FOOD'),
##                ('107', 'Food Network HD', 'FOODH'),
##                ('108', 'Globovision', 'G VIS'),
##                ('109', 'HOT', 'HOT'),
##                ('110', 'Mezzo Live HD', 'MEZHD'),
##                ('111', 'Travel Channel HD', 'TRVHD'),
##                ('112', 'TVI24', 'TVI24'),
##                ('113', 'Porto Canal', 'PORTO'),
                ('114', 'BBC Entertainment', 'BBC E'),
                ('115', 'AXNBL', 'AXNBL'),
                ('116', 'AXBHD', 'AXBHD'),
##                ('117', 'TVCine 4', 'TVC4'),
##                ('118', 'Baby First TV', 'BABYT'),
                ('119', 'Hollywood HD', 'HOLHD'),
##                ('120', 'iConcerts', 'ICOHD'),
##                ('121', 'MEO 3D', 'MEO3D'),
##                ('122', 'RTP 1', 'RTP H'),
##                ('123', 'SIC', 'SIC H'),
##                ('124', 'TVIH', 'TVI H'),
##                ('125', 'SIC Notícias', 'SICNH'),
##                ('126', 'Fox Movies', 'FOXM'),
##                ('127', 'Trace TV HD', 'TRAHD'),
##                ('128', 'TVSéries', 'TVSER'),
                ('129', 'TLC', 'TLC'),
##                ('130', 'TOROTV', 'TOROTV'),
##                ('131', 'NHK World', 'NHK'),
##                ('132', 'Record News', 'RECNEW'),
##                ('133', 'E! Entertainment HD', 'E! HD'),
##                ('134', 'AXN White', 'AXNWH'),
                ('135', 'AXN White HD', 'AXWHD'),
                ('136', 'Panda Biggs', 'BIGGS'),
##                ('137', 'HOT HD', 'HOTHD'),
##                ('138', 'Nat Geo Wild HD', 'NGWHD'),
##                ('139', 'FOX Life HD', 'FLIFEH'),
##                ('140', 'A Bola TV', 'ABOLA'),
##                ('141', 'TVI Ficção', 'TVIFIC'),
                ('142', 'FOX Crime HD', 'FOXCHD'),
##                ('143', '24Kitchen HD', '24KTHD'),
##                ('144', 'CBS Reality', 'CBSR'),
##                ('145', 'Localvisão TV', 'LVTV'),
##                ('146', 'Localvisão TV HD', 'LVTVHD'),
                ('147', 'SIC K', 'SICK'),
##                ('148', 'KBS World', 'KBS'),
##                ('149', 'Canal MEO Destaques', 'DEST'),
##                ('150', 'CMTV', 'CMTV'),
##                ('151', 'CMTV', 'CMTVHD'),
##                ('152', 'Destaques MEO Videoclube', 'VOD'),
                ('153', 'Disney Junior', 'DISNYJ'),
##                ('154', 'Benfica TV HD', 'SLBHD'),
##                ('155', 'ZEE TV', 'ZEETV'),
##                ('156', 'ZEE CINEMA', 'ZEECIN'),
                ('157', 'TVCine 1 HD', 'TVC1HD'),
                ('158', 'TVCine 2 HD', 'TVC2HD'),
                ('159', 'TVCine 3 HD', 'TVC3HD'),
                ('160', 'TVCine 4 HD', 'TVC4HD'),
                ('161', 'TVSÉries HD', 'TVSEHD'),
##                ('162', 'Caça e Pesca', 'CAÇAP'),
##                ('163', 'CCTV News', 'CCTVN'),
##                ('164', 'CCTV 4', 'CCTV4'),
##                ('165', 'Playboy TV HD', 'PBTVHD'),
##                ('166', 'SexTreme', 'SEXTRM'),
##                ('167', 'TCV Internacional', 'TCV'),
##                ('168', 'SPORT.TV4', 'SPTV4'),
##                ('169', 'SPORT.TV5', 'SPTV5'),
##                ('170', 'SPORT.TV4 HD', 'SPT4HD'),
##                ('171', 'SPORT.TV5 HD', 'SPT5HD'),
##                ('172', 'CINEMUNDO', 'CINE'),
                ('173', 'CINEMUNDO HD', 'CINEHD'),
##                ('174', 'TV Record', 'TVREC'),
##                ('175', 'Sporting TV', 'SCP'),
##                ('176', 'Sporting TV HD', 'SCPHD'),
##                ('177', 'TV Record HD', 'REC HD'),
##                ('178', 'AMC', 'AMC'),
##                ('179', 'AE', 'AE'),
##                ('180', 'DOGTV', 'DOGTV'),
                ('181', 'AMC HD', 'AMCHD'),
##                ('182', 'FTV', 'FTV'),
##                ('183', 'Mas Chic', 'MCHIC'),
##                ('184', 'RTP 3', 'RTP3'),
##                ('185', 'RTP3 UPSCALE', 'RTP3H'),
##                ('186', 'i24 News (I)', 'I24I'),
##                ('187', 'i24 News (F)', 'I24F'),
##                ('188', 'FOX Comedy', 'FOXCOM'),
                ('189', 'FOX Comedy HD', 'FOXCOH'),
##                ('190', 'Canção Nova', 'CNOVA'),
##                ('191', 'TV Mundial', 'TVMUND'),
##                ('192', 'MCS Lifestyle', 'MCSL'),
##                ('193', 'MCS Lifestyle HD', 'MCSLH'),
##                ('194', 'Porto Canal HD', 'PORTHD'),
##                ('195', 'SIC Caras', 'SICC'),
##                ('196', 'Eurosport 2 HD', 'EURS2H'),
                ('197', 'FOX Movies HD', 'FOXMH'),
##                ('198', 'Purescreens Nature HD', 'PNAT'),
##                ('199', 'Purescreens Museums Eng', 'PMUSE'),
##                ('200', 'Purescreens Museums Fr', 'PMUSF'),
##                ('201', 'Sport TV2 HD', 'SPT2HD'),
##                ('202', 'Sport TV1 HD', 'SPT1HD'),
##                ('203', 'Sport TV3 HD', 'SPT3HD'),
##                ('204', 'Clubbing TV HD', 'CLUBHD'),
##                ('205', 'Clubbing TV', 'CLUBB'),
##                ('206', '24 Kitchen', '24KITC'),
##                ('207', 'RTP Mobile', 'RTM'),
##                ('208', 'MTV Music', 'MTMM')
                ]

        threads = []
        for i in channels: threads.append(workers.Thread(self.MEO_list, i[0], i[1], i[2]))
        [i.start() for i in threads]
        [i.join() for i in threads]

        threads = []
        for i in range(0, len(self.items)):
            if 'Ep.' not in self.items[i][0]: threads.append(workers.Thread(self.movieChannel_list, self.items[i]))
        [i.start() for i in threads]
        [i.join() for i in threads]

        threads = []
        for i in range(0, len(self.items)):
            if 'Ep.' in self.items[i][0]: threads.append(workers.Thread(self.tvChannel_list, self.items[i]))
        [i.start() for i in threads]
        [i.join() for i in threads]

        self.list = metacache.local(self.list, self.tm_img_link, 'poster2', 'fanart')

        try: self.list = sorted(self.list, key=lambda k: k['channel'])
        except: pass

        self.channelDirectory(self.list)
        return self.list


    def MEO_list(self, num, channel, id):
##        urlP = 'http://services.sapo.pt/EPG/GetChannelListJSON?ESBToken=01.eY-ccS4OiD_gqhIixwE1xg'
##        result = client.request(urlP, timeout='10')
##        result = json.loads(result)
##        l=1
##        for i in result['GetChannelListResponse']['GetChannelListResult']['Channel']:
##            print "('"+str(l)+"', '"+i['Name'].encode('utf-8')+"', '"+i['Sigla'].encode('utf-8')+"'),"
##            l=l+1
        try:
            dt1 = (self.uk_datetime).strftime('%Y-%m-%d+%H:%M:%S')
            dt2 = str((self.uk_datetime_mais).strftime('%Y-%m-%d+%H:%M:%S'))

            urlCanal = 'http://services.sapo.pt/EPG/GetChannelListByDateIntervalJSON?ESBToken=01.eY-ccS4OiD_gqhIixwE1xg&channelSiglas='+id+'&startDate='+str(dt1)+'&endDate='+str(dt2)

            result = client.request(urlCanal, timeout='10')
            result = json.loads(result)

            try:
                title = result['GetChannelListByDateIntervalResponse']['GetChannelListByDateIntervalResult']['Channel']['Programs']['Program'][0]['Title']
            except:
                title = result['GetChannelListByDateIntervalResponse']['GetChannelListByDateIntervalResult']['Channel']['Programs']['Program']['Title']

            title = title.encode('utf-8')

            year = ''
            self.items.append((title, year, channel, num))
        except:
            pass


    def movieChannel_list(self, i):
        #print i[0]
        titulo = i[0]
        try:
            url = self.imdb_by_query % (urllib.quote_plus(i[0]), i[1])
            item = client.request(url, timeout='10')
            item = json.loads(item)
                
            if 'Movie not found' in str(item):
                urli = 'http://www.imdb.com/find?ref_=nv_sr_fn&q=%s&s=all' % (urllib.quote_plus(i[0]))
                item_imdb = client.request(urli, timeout='10')
                item_imdb = client.parseDOM(item_imdb, 'td', attrs = {'class': 'primary_photo'})[0]
                item_imdb = client.parseDOM(item_imdb, 'a', ret="href" )[0]
                item_imdb = re.compile('/title/(.+?)/').findall(item_imdb)[0]
                url = 'http://www.omdbapi.com/?i='+urllib.quote_plus(item_imdb)+'&plot=short&r=json'
                item = client.request(url, timeout='10')
                item = json.loads(item)

            title = item['Title']
            title = client.replaceHTMLCodes(title)
            title = title.encode('utf-8')

            try:
                year = item['Year']
                year = re.sub('[^0-9]', '', str(year))
                year = year.encode('utf-8')
            except:
                try:
                    year = item['Released']
                    year = re.findall('(\d{4})', year)[0]
                    year = year.encode('utf-8')
                except:
                    year = '0'

            try:
                imdb = item['imdbID']
                if imdb == None or imdb == '' or imdb == 'N/A': raise Exception()
                imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                imdb = imdb.encode('utf-8')
            except: imdb = '0'

            try:
                poster = item['Poster']
                if poster == None or poster == '' or poster == 'N/A': poster = '0'
                if '/nopicture/' in poster: poster = '0'
                poster = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
                poster = poster.encode('utf-8')
            except: poster = '0'

            try:
                genre = item['Genre']
                if genre == None or genre == '' or genre == 'N/A': genre = '0'
                genre = genre.replace(', ', ' / ')
                genre = genre.encode('utf-8')
            except: genre = '0'

            try:
                duration = item['Runtime']
                if duration == None or duration == '' or duration == 'N/A': duration = '0'
                duration = re.sub('[^0-9]', '', str(duration))
                duration = duration.encode('utf-8')
            except: duration = '0'

            try:
                rating = item['imdbRating']
                if rating == None or rating == '' or rating == 'N/A' or rating == '0.0': rating = '0'
                rating = rating.encode('utf-8')
            except: rating = '0'
                
            try:
                votes = item['imdbVotes']
                try: votes = str(format(int(votes),',d'))
                except: pass
                if votes == None or votes == '' or votes == 'N/A': votes = '0'
                votes = votes.encode('utf-8')
            except: votes = '0'

            try:
                mpaa = item['Rated']
                if mpaa == None or mpaa == '' or mpaa == 'N/A': mpaa = '0'
                mpaa = mpaa.encode('utf-8')
            except: mpaa = '0'

            try:                
                director = item['Director']
                if director == None or director == '' or director == 'N/A': director = '0'
                director = director.replace(', ', ' / ')
                director = re.sub(r'\(.*?\)', '', director)
                director = ' '.join(director.split())
                director = director.encode('utf-8')
            except: director = '0'
            
            try:                
                writer = item['Writer']
                if writer == None or writer == '' or writer == 'N/A': writer = '0'
                writer = writer.replace(', ', ' / ')
                writer = re.sub(r'\(.*?\)', '', writer)
                writer = ' '.join(writer.split())
                writer = writer.encode('utf-8')
            except: writer = '0'

            try:                
                cast = item['Actors']
                if cast == None or cast == '' or cast == 'N/A': cast = '0'
                cast = [x.strip() for x in cast.split(',') if not x == '']
                try: cast = [(x.encode('utf-8'), '') for x in cast]
                except: cast = []
                if cast == []: cast = '0'
            except: cast = '0'
                
            try:                
                plot = item['Plot']
                if plot == None or plot == '' or plot == 'N/A': plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')
            except: plot = '0'
                    
            self.list.append({'title': title, 'originaltitle': title, 'year': year, 'genre': genre, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'imdb': imdb, 'poster': poster, 'channel': i[2], 'num': i[3], 'action': 'movie'})
        except: #pass
            self.list.append({'title': titulo, 'originaltitle': titulo, 'year': '0', 'genre': '0', 'rating': '0', 'votes': '0', 'mpaa': '0', 'director': '0', 'writer': '0', 'cast': '0', 'plot': '0', 'imdb': '0', 'poster': '0', 'channel': i[2], 'num': i[3], 'action': 'movie'})


    def tvChannel_list(self, i):
        titulo = i[0].replace('Simpson ','Simpsons ')#.encode('utf-8')
        season_episode = ''
        #print str(i[2])+'-'+titulo+'«««««««««««««««««««««'
        
        try:
            t = re.compile(' T(.+?) - Ep.').findall(titulo)
            print t
            if t ==[]:season = '1'
            else: season = str(t[0].replace(' ',''))
            #print season
        except: season = '1'
        try:
            episode = re.compile('- Ep. (.*)').findall(titulo)[0]
            episode = str(episode.replace(' ',''))
            #print episode
        except: episode = '1'
        
        tituloProcura = titulo
        tituloProcura = tituloProcura.replace(' T'+str(season)+' - Ep. '+str(episode),'')
        tituloProcura = tituloProcura.replace(' - Ep. '+str(episode),'')
        tituloProcura = tituloProcura.replace(' Ep. '+str(episode),'')
        season_episode = titulo.replace(tituloProcura,'')

        url = 'http://www.imdb.com/find?ref_=nv_sr_fn&q=%s&s=all&title_type=tv_series' % (urllib.quote_plus(tituloProcura))                
        result = client.request(url, timeout='10')
        try:            
            imdb = client.parseDOM(result, 'td', attrs = {'class': 'primary_photo'})[0]
            imdb = client.parseDOM(imdb, 'a', ret="href" )[0]
            imdb = re.compile('/title/(.+?)/').findall(imdb)[0]
        except:
            imdb = '0'
        try:
            tvshowtitle = client.parseDOM(result, 'td', attrs = {'class': 'result_text'})[0]
            tvshowtitle = re.compile('fn_al_tt_1" >(.+?)</a>').findall(tvshowtitle)[0]
        except:
            tvshowtitle = tituloProcura
        try:
            year = client.parseDOM(result, 'td', attrs = {'class': 'result_text'})[0]
            year = re.compile('</a> [(](.+?)[)] [(].+?[)]').findall(year)[0]
        except:
            year = ''

##        print tvshowtitle
##        print imdb
##        print year
        tvdb = '0'
        
        try:
            #print '------------'
            if imdb == '0':
                #print '1sim'
                url = self.imdb_by_query % (urllib.quote_plus(tvshowtitle), year)

                imdb = client.request(url, timeout='10')
                try: imdb = json.loads(imdb)['imdbID']
                except: imdb = '0'

                if imdb == None or imdb == '' or imdb == 'N/A': imdb = '0'


            if tvdb == '0' and not imdb == '0':
                #print '2sim'
                url = self.tvdb_by_imdb % imdb

                result = client.request(url, timeout='10')

                try: tvdb = client.parseDOM(result, 'seriesid')[0]
                except: tvdb = '0'

                if tvdb == '': tvdb = '0'
                #print tvdb

            if tvdb == '0' and not imdb == '0':
                url = 'http://api.tvmaze.com/lookup/shows?imdb=' + urllib.quote_plus(imdb)
                result = client.request(url, timeout='10')

                items = json.loads(result)
                tvmaze = items['id']
                tvdb = items['externals']['thetvdb']
                #print tvdb


            if tvdb == '0':
                url = self.tvdb_by_query % (urllib.quote_plus(tvshowtitle))
                result = client.request(url, timeout='10')
                tvdb = re.findall('<seriesid>(.+?)</seriesid>', result, re.DOTALL)
                if tvdb != []: tvdb = tvdb[0]
                else: tvdb = '0'

                if tvdb == '': tvdb = '0'
                #print tvdb
                
            #print '---------'
        except:
            pass
        
        try:
            url = self.tvdb_info_link % (tvdb, 'en')
            data = urllib2.urlopen(url, timeout=30).read()

            zip = zipfile.ZipFile(StringIO.StringIO(data))
            result = zip.read('%s.xml' % 'en')
            artwork = zip.read('banners.xml')
            zip.close()

            item = client.parseDOM(result, 'Series')[0]    

            try: poster = client.parseDOM(item, 'poster')[0]
            except: poster = ''
            if not poster == '': poster = self.tvdb_image + poster
            else: poster = '0'
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

            if not poster == '0': pass
            elif not fanart == '0': poster = fanart
            elif not banner == '0': poster = banner

            if not banner == '0': pass
            elif not fanart == '0': banner = fanart
            elif not poster == '0': banner = poster
        except:
            poster = '0'
            fanart = '0'
            banner = '0'

        self.list.append({'title': titulo , 'season': str(season), 'episode': str(episode), 'tvshowtitle': tvshowtitle, 'year': '0', 'premiered': '0', 'status': '0', 'studio': '0', 'genre': '0', 'duration': '0', 'rating': '0', 'votes': '0', 'mpaa': '0', 'director': '0', 'writer': '0', 'cast': '0', 'plot': '0', 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'banner': banner, 'fanart': fanart, 'thumb': '0', 'snum': '0', 'enum': '0', 'channel': i[2], 'num': i[3], 'action': 'episodes'})

        return ################


        try:
            #if tvdb == '0': return

            url = self.tvdb_info_link % (tvdb, 'en')
            data = urllib2.urlopen(url, timeout=30).read()

            zip = zipfile.ZipFile(StringIO.StringIO(data))
            result = zip.read('%s.xml' % 'en')
            #print result
            artwork = zip.read('banners.xml')
            zip.close()

            item = client.parseDOM(result, 'Series')[0]
            episodes = client.parseDOM(result, 'Episode')

            episodes = [i for i in episodes if '<SeasonNumber>%s</SeasonNumber>' % str(season) in i]
            episodes = [i for i in episodes if '<EpisodeNumber>%s</EpisodeNumber>' % str(episode) in i]

            print str(len(episodes))

            tvshowtitle = client.parseDOM(item, 'SeriesName')[0]
            if tvshowtitle == '': tvshowtitle = '0'
            tvshowtitle = client.replaceHTMLCodes(tvshowtitle)
            tvshowtitle = tvshowtitle.encode('utf-8')       

            try: poster = client.parseDOM(item, 'poster')[0]
            except: poster = ''
            if not poster == '': poster = self.tvdb_image + poster
            else: poster = '0'
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

            if not poster == '0': pass
            elif not fanart == '0': poster = fanart
            elif not banner == '0': poster = banner

            if not banner == '0': pass
            elif not fanart == '0': banner = fanart
            elif not poster == '0': banner = poster

            try: status = client.parseDOM(item, 'Status')[0]
            except: status = ''
            if status == '': status = 'Ended'
            status = client.replaceHTMLCodes(status)
            status = status.encode('utf-8')

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
            if rating == '': rating = '0'
            rating = client.replaceHTMLCodes(rating)
            rating = rating.encode('utf-8')

            try: votes = client.parseDOM(item, 'RatingCount')[0]
            except: votes = '0'
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

            try: label = client.parseDOM(item2, 'SeriesName')[0]
            except: label = '0'
            label = client.replaceHTMLCodes(label)
            label = label.encode('utf-8')

            try: plot = client.parseDOM(item2, 'Overview')[0]
            except: plot = ''
            if plot == '': plot = '0'
            plot = client.replaceHTMLCodes(plot)
            plot = plot.encode('utf-8')
        except:
            pass


        for item in episodes:
            print item
            if item!='':
                premiered = client.parseDOM(item, 'FirstAired')[0]
                if premiered == '' or '-00' in premiered: premiered = '0'
                premiered = client.replaceHTMLCodes(premiered)
                premiered = premiered.encode('utf-8')

##                if status == 'Ended': pass
##                elif premiered == '0': raise Exception()
##                elif int(re.sub('[^0-9]', '', str(premiered))) > int(re.sub('[^0-9]', '', str(self.today_date))): raise Exception()

                season = client.parseDOM(item, 'SeasonNumber')[0]
                season = '%01d' % int(season)
                season = season.encode('utf-8')

                episode = client.parseDOM(item, 'EpisodeNumber')[0]
                episode = re.sub('[^0-9]', '', '%01d' % int(episode))
                episode = episode.encode('utf-8')

                title = client.parseDOM(item, 'EpisodeName')[0]
                if title == '': title = '0'
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                try: thumb = client.parseDOM(item, 'filename')[0]
                except: thumb = ''
                if not thumb == '': thumb = self.tvdb_image + thumb
                else: thumb = '0'
                thumb = client.replaceHTMLCodes(thumb)
                thumb = thumb.encode('utf-8')

                if not thumb == '0': pass
                elif not fanart == '0': thumb = fanart.replace(self.tvdb_image, self.tvdb_poster)
                elif not poster == '0': thumb = poster

                try: rating = client.parseDOM(item, 'Rating')[0]
                except: rating = ''
                if rating == '': rating = '0'
                rating = client.replaceHTMLCodes(rating)
                rating = rating.encode('utf-8')

                try: director = client.parseDOM(item, 'Director')[0]
                except: director = ''
                director = [x for x in director.split('|') if not x == '']
                director = ' / '.join(director)
                if director == '': director = '0'
                director = client.replaceHTMLCodes(director)
                director = director.encode('utf-8')

                try: writer = client.parseDOM(item, 'Writer')[0]
                except: writer = ''
                writer = [x for x in writer.split('|') if not x == '']
                writer = ' / '.join(writer)
                if writer == '': writer = '0'
                writer = client.replaceHTMLCodes(writer)
                writer = writer.encode('utf-8')

                try:
                    local = client.parseDOM(item, 'id')[0]
                    local = [x for x in locals if '<id>%s</id>' % str(local) in x][0]
                except:
                    local = item

                label = client.parseDOM(local, 'EpisodeName')[0]
                if label == '': label = '0'
                label = client.replaceHTMLCodes(label)
                label = label.encode('utf-8')

                try: episodeplot = client.parseDOM(local, 'Overview')[0]
                except: episodeplot = ''
                if episodeplot == '': episodeplot = '0'
                if episodeplot == '0': episodeplot = plot
                episodeplot = client.replaceHTMLCodes(episodeplot)
                try: episodeplot = episodeplot.encode('utf-8')
                except: pass

                self.list.append({'title': title, 'label': label, 'season': str(season), 'episode': str(episode), 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': status, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': episodeplot, 'imdb': imdb, 'tvdb': tvdb, 'poster': poster, 'banner': banner, 'fanart': fanart, 'thumb': thumb, 'snum': str(season), 'enum': str(episode), 'channel': i[2], 'num': i[3], 'action': 'episodes'})
##            except:
##                self.list.append({'title': titulo , 'season': str(season), 'episode': str(episode), 'tvshowtitle': tituloProcura, 'year': '0', 'premiered': '0', 'status': '0', 'studio': '0', 'genre': '0', 'duration': '0', 'rating': '0', 'votes': '0', 'mpaa': '0', 'director': '0', 'writer': '0', 'cast': '0', 'plot': '0', 'imdb': '0', 'tvdb': '0', 'poster': '0', 'banner': '0', 'fanart': '0', 'thumb': '0', 'snum': '0', 'enum': '0', 'channel': i[2], 'num': i[3], 'action': 'episodes'})


    def uk_datetime(self):
        dt = datetime.datetime.utcnow() + datetime.timedelta(hours = 0)
        d = datetime.datetime(dt.year, 4, 1)
        dston = d - datetime.timedelta(days=d.weekday() + 1)
        d = datetime.datetime(dt.year, 11, 1)
        dstoff = d - datetime.timedelta(days=d.weekday() + 1)
        if dston <=  dt < dstoff:
            return dt + datetime.timedelta(hours = 1)
        else:
            return dt

    def uk_datetime_mais(self):
        dt = datetime.datetime.utcnow() + datetime.timedelta(hours = 1)
        d = datetime.datetime(dt.year, 4, 1)
        dston = d - datetime.timedelta(days=d.weekday() + 1)
        d = datetime.datetime(dt.year, 11, 1)
        dstoff = d - datetime.timedelta(days=d.weekday() + 1)
        if dston <=  dt < dstoff:
            return dt + datetime.timedelta(hours = 1)
        else:
            return dt


    def channelDirectory(self, items):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        try: isOld = False ; control.item().getArt('type')
        except: isOld = True

        isPlayable = 'true' if not 'plugin' in control.infoLabel('Container.PluginName') else 'false'

        playbackMenu = control.lang(32063).encode('utf-8') if control.setting('hosts.mode') == '2' else control.lang(32064).encode('utf-8')

        queueMenu = control.lang(32065).encode('utf-8')

        refreshMenu = control.lang(32072).encode('utf-8')


        for i in items:
            print i
            if i:
                ano = i['year']

                if ano == '0':
                    label = '[B]%s[/B] : %s %s' % (i['channel'].upper(), i['title'], '')
                    sysname = urllib.quote_plus('%s %s' % (i['title'], ''))
                else:
                    label = '[B]%s[/B] : %s (%s)' % (i['channel'].upper(), i['title'], i['year'])
                    sysname = urllib.quote_plus('%s (%s)' % (i['title'], i['year']))
                
                systitle = urllib.quote_plus(i['title'])
                imdb, year = i['imdb'], i['year']

                if year == '0': year = ''

                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
                meta.update({'mediatype': 'movie'})
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, sysname)})
                #meta.update({'trailer': 'plugin://script.extendedinfo/?info=playtrailer&&id=%s' % imdb})
                meta.update({'playcount': 0, 'overlay': 6})
                try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except: pass

                sysmeta = urllib.quote_plus(json.dumps(meta))

                if i['action'] == 'movie':
                    url = '%s?action=play&title=%s&year=%s&imdb=%s&meta=%s&t=%s' % (sysaddon, systitle, year, imdb, sysmeta, self.systime)
                    sysurl = urllib.quote_plus(url)
                else:
                    imdb, tvdb, year, season, episode = i['imdb'], i['tvdb'], i['year'], i['season'], i['episode']

                    systitle = urllib.quote_plus(i['title'])
                    systvshowtitle = i['tvshowtitle']
                    syspremiered = urllib.quote_plus(i['premiered'])
                    
                    url = '%s?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s&t=%s' % (sysaddon, systitle, year, imdb, tvdb, season, episode, systvshowtitle, syspremiered, sysmeta, self.systime)
                    sysurl = url

                    path = '%s?action=play&title=%s&year=%s&imdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s' % (sysaddon, systitle, year, imdb, tvdb, season, episode, systvshowtitle, syspremiered)


                cm = []

                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                cm.append((refreshMenu, 'RunPlugin(%s?action=refresh)' % sysaddon))

                cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))

                if isOld == True:
                    cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))


                item = control.item(label=label)

                art = {}

                if 'poster2' in i and not i['poster2'] == '0':
                    art.update({'icon': i['poster2'], 'thumb': i['poster2'], 'poster': i['poster2']})
                elif 'poster' in i and not i['poster'] == '0':
                    art.update({'icon': i['poster'], 'thumb': i['poster'], 'poster': i['poster']})
                else:
                    art.update({'icon': addonPoster, 'thumb': addonPoster, 'poster': addonPoster})

                art.update({'banner': addonBanner})

                if settingFanart == 'true' and 'fanart' in i and not i['fanart'] == '0':
                    item.setProperty('Fanart_Image', i['fanart'])
                elif not addonFanart == None:
                    item.setProperty('Fanart_Image', addonFanart)

                item.setArt(art)
                item.addContextMenuItems(cm)
                item.setProperty('IsPlayable', isPlayable)
                item.setInfo(type='Video', infoLabels = meta)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
##            except:
##                pass

        control.content(syshandle, 'movies')
        control.directory(syshandle, cacheToDisc=True)

