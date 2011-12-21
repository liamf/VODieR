#!/usr/bin/python

"""
    VODie
    kitesurfing@kitesurfing.ie
"""

import re
import sys
from BeautifulSoup import BeautifulStoneSoup
import urllib, urllib2, cookielib
from TVSeriesUtil import Util
import MenuConstants
import simplejson as S
from datetime import date
import random

try:
    import xbmcaddon
    __settings__ = xbmcaddon.Addon(id='plugin.video.vodie')
    getLS = __settings__.getLocalizedString
except ImportError, e:
    pass # module doesn't exist, deal with it.


# Player Constants
SWFURL = 'https://www.aertv.ie/players/jwplayer/player.swf'
PAGEURL = 'http://www.rte.ie/player/'

# URL Constants
MAIN_URL = 'https://www.aertv.ie/'
LOGIN_URL = MAIN_URL + 'web/j_spring_security_check'
LOGOUT_URL = MAIN_URL + 'web/j_spring_security_logout'
NOWANDNEXT_URL = MAIN_URL + 'web/api/listings/nowandnext'
DEVICE_IOS = 'ios'
DEVICE_WEBUI = 'webui'
STREAM_URL = MAIN_URL + 'web/api/streams/%s?refresh=false&device=%s'

# Channel Constants
CHANNEL = 'Aer TV'
LOGOICON = 'https://www.aertv.ie/images/logo.png'
LOGOURL = 'https://www.aertv.ie/images/logos/'

# To work outside of Ireland
FORWARDED_FOR_IP = '79.97.%d.%d' % (random.randint(0, 255), random.randint(0, 254)) 

class Magnet:
        
    def __init__(self, loadSettings = True):
        if loadSettings:
            self.getSettings()
        else:
            self.settings = dict()
            self.settings['magnet_username'] = os.environ['MAGNET_USERNAME']
            self.settings['magnet_password'] = os.environ['MAGNET_PASSWORD']

    def getSettings(self):
        self.settings = dict()
        self.settings['magnet_username'] = __settings__.getSetting('magnet_username')
        self.settings['magnet_password'] = __settings__.getSetting('magnet_password')

    def getVideoDetails(self, url):
        # Login
        opener = self.login(self.settings['magnet_username'], self.settings['magnet_password'])
        
        # Load read JSON Decode the output
        req = urllib2.Request(STREAM_URL % (url, DEVICE_IOS))
        req.add_header('X-Forwarded-For', FORWARDED_FOR_IP)
        resp = opener.open(req)
        data = S.loads(resp.read())
        
        # Build the iOS path (Not used but could be handy)
        ios_playUrl = data['protocol'] + "://" + data['hostname'] + ":" + data['port'] + "/" + data['path'] + "/" + data['fileName'] + "."+ data['extension']
        if not data['extension'] == 'mp4':
            ios_playUrl = ios_playUrl + "/playlist.m3u8?token=" + data['st']
        
        print data['fileName']
        print data['extension']
        print data['st']
        
        # Build the play path
        if data['extension'] == 'mp4':
            rtmpServer = "http://" + data['hostname'] + ":" + data['port'] + "/" + data['path']
            playUrl = data['fileName'] + "."+ data['extension'];
            rtmp_playUrl = '%s/%s' % (rtmpServer, playUrl)
        else:
            rtmpServer = "rtmpe://" + data['hostname'] + ":" + data['port'] + "/" + data['path']
            playUrl = data['fileName'] + "."+ data['extension'] + "?token=" + data['st'];
            rtmp_playUrl = '%s playpath=%s live=true' % (rtmpServer, playUrl)

        # Close the response        
        resp.close()
        
        # Logout
        self.logout(opener)

        yield {'Channel'     : CHANNEL,
               'Title'       : CHANNEL,
               'Director'    : CHANNEL,
               'Genre'       : CHANNEL,
               'Plot'        : CHANNEL,
               'PlotOutline' : CHANNEL,
               'id'          : url,
               'url'         : rtmp_playUrl
               }

    def getChannelDetail(self):
        # Only return the Channel details if the username and password were provided for Magnet
        if self.settings['magnet_username'] == '' and self.settings['magnet_password'] == '':
            return None
        else: 
            return {'Channel': CHANNEL,
                    'Thumb':LOGOICON,
                    'Title':CHANNEL,
                    'mode':MenuConstants.MODE_MAINMENU,
                    'Plot':CHANNEL}

    def convertHTML(self, text):
        if not text == '':
            return BeautifulStoneSoup(text, 
                       convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0].encode( "utf-8" )
        else:
            return 'None'
                   
    def getMainMenu(self):
        # Login to Magnet Web TV
        opener = self.login(self.settings['magnet_username'], self.settings['magnet_password'])
        
        # Load and Decode JSON the output
        req = urllib2.Request(NOWANDNEXT_URL)
        req.add_header('X-Forwarded-For', FORWARDED_FOR_IP)
        resp = opener.open(req)
        nowandnext = S.loads(resp.read())
        resp.close()
        
        # Logout
        self.logout(opener)
        
        # Return the TV Channel available
        for channel in nowandnext:
            yield {'Channel' : CHANNEL,
                   'Thumb'   : LOGOURL + str(channel['channel']['id']) + '.png',
                   'url'     : str(channel['channel']['id']),
                   'Title'   : self.convertHTML(channel['channel']['name']),
                   'mode'    : MenuConstants.MODE_GETEPISODES}
            
    def getEpisodes(self, showID):
        # Login to Magnet Web TV
        opener = self.login(self.settings['magnet_username'], self.settings['magnet_password'])
        
        # Load and Decode JSON object
        req = urllib2.Request(NOWANDNEXT_URL)
        req.add_header('X-Forwarded-For', FORWARDED_FOR_IP)
        resp = opener.open(req)
        channels = S.loads(resp.read())
        resp.close()
        
        # Logout
        self.logout(opener)
        
        # Return the shows for this channel
        for channel in channels:
            if showID == str(channel['channel']['id']):
                for video in channel['videos']:
                    # Calculate Start time
                    x = video['startTime'] / 1000
                    start_seconds = x % 60
                    x /= 60
                    start_minutes = x % 60
                    x /= 60
                    start_hours = x % 24

                    # Calculate End Time
                    x = video['endTime'] / 1000
                    end_seconds = x % 60
                    x /= 60
                    end_minutes = x % 60
                    x /= 60
                    end_hours = x % 24
                    
                    showtime = "%02d:%02d-%02d:%02d" % (start_hours, start_minutes, end_hours, end_minutes)
                    
                    # 1800 -> 30mins
                    # 3000 -> 50mins
                    
                    title = self.convertHTML(video['name'])
                    
                    details = Util().getSeriesDetailsByName(title)
                    if details is None:
                        pic = LOGOICON
                    elif 'Poster' in details.keys():
                        pic = details['Poster']
                    elif 'Season' in details.keys():
                        pic = details['Season']
                    else:
                        pic = LOGOICON
                    
                    yield {'Channel'      : CHANNEL,
                            'Thumb'       : pic,
                            'url'         : str(video['id']),
                            'Title'       : "%s - %s" % (showtime, title),
                            'mode'        : MenuConstants.MODE_PLAYVIDEO,
                            'Plot'        : self.convertHTML(video['description']),
                            'plotoutline' : self.convertHTML(video['name']),
                            'Date'        : date.today().strftime("%d-%m-%Y"),
                            'Duration'    : str(video['duration']/60),
                            }

    def login(self, username, password):
        
        # Change the User Agent, dont think it matters anymore
        USER_AGENT = 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10'
                
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        login_data = urllib.urlencode({'j_username' : username, 'j_password' : password, 'IpicDeviceId' : 'webui'})
        
        req = urllib2.Request(LOGIN_URL)
        req.add_header('User-Agent', USER_AGENT)
        req.add_header('X-Forwarded-For', FORWARDED_FOR_IP)

        opener.open(req, login_data)
        
        return opener
    
    def logout(self, opener):
        opener.open(LOGOUT_URL)
                        
if __name__ == '__main__':
    for menu in Magnet(False).getMainMenu():
        print menu
        
    for menu in Magnet(False).getEpisodes('9'):
        print menu
        for detail in Magnet(False).getVideoDetails(menu['url']):
            print detail

