#!/usr/bin/python

"""
    VODie
    
    AerTV scraper, new Brightcove site
    
    liam.friel@gmail.com
    
"""

import re
import sys
import random
import urllib, urllib2, cookielib, httplib
import time
from brightcove import BrightcoveBaseChannel

import MenuConstants
import simplejson as S

try:
    import xbmcaddon
    # Settings are not really required in this version
    # AerTV site does not require login, and there is no obvious benefit from it, so we're not going to login
    __settings__ = xbmcaddon.Addon(id='plugin.video.vodie')
    getLS = __settings__.getLocalizedString
except ImportError, e:
    pass # module doesn't exist, deal with it.


# Player Constants
RTMP_URL = 'rtmp://85.91.5.163:1935/'
APP_STRING = 'videoId=%s&lineUpId=&pubId=%s&playerId=%s&affiliateId='
PAGEURL = 'http://www.aertv.ie'

# URL Constants
MAIN_REQUEST_URL = 'http://www.aertv.ie/?'

# Channel Constants
CHANNEL = 'Aer TV'
LOGOICON = 'http://www.aertv.ie/wp-content/themes/aertv/images/logo.png'

# To work outside of Ireland
FORWARDED_FOR_IP = '79.97.%d.%d' % (random.randint(0, 255), random.randint(0, 254)) 

class AerTV(BrightcoveBaseChannel):
        
    def __init__(self, loadSettings = True):
        # Set some defaults for the Brightcove API
        self.flashWidth  = 750
        self.flashHeight = 423
        self.flash_experience_id = 'aertv'
        self.bgColour = '#FFFFFF'
        self.flashwmode='transparent'
        self.autoStart='yes'
        
        # Fetch the settings, even though at the moment we don't use them
        if loadSettings:
            self.getSettings()
        else:
            self.settings = dict()
            self.settings['aertv_username'] = os.environ['AERTV_USERNAME']
            self.settings['aertv_password'] = os.environ['AERTV_PASSWORD']


    def getSettings(self):
        self.settings = dict()
        self.settings['aertv_username'] = __settings__.getSetting('aertv_username')
        self.settings['aertv_password'] = __settings__.getSetting('aertv_password')

    # Not really the URL passed in, just the slug name
    def getVideoDetails(self, stub):
        
        self.login()
        
        (opener, req) = self.makeOpenerAndRequest()
        
        # Returns a JSON data array, sorta. Wrapped in "()" for some reason
        request_data = urllib.urlencode({'source':'player', 'type':'name', 'val':stub})
        f = opener.open(req, request_data)
        stuff = f.read()
        f.close()        
        
        self.logout()
        
        playerJSON = S.loads(stuff[1:-1])        
              
        # playerURLs
        # JSON data contains the necessary information
        self.playerId = playerJSON['data']['playerId']
        self.publisherId = playerJSON['data']['publisherId']
        self.videoId = playerJSON['data']['videoId']
        showName = playerJSON['data']['show']
        
        qualifierString = APP_STRING % (self.videoId, self.publisherId, self.playerId)
        appString = 'rtplive?' + qualifierString
        url = RTMP_URL + appString
        
        self.get_swf_url()
        
        playpath="%smpegts.stream?%s" % (self.getTSQualifier(stub),qualifierString)
              
        # Pity it's python 2.4 ... string formatting is a pain
        playerURL = '%s app=%s playpath=%s swfUrl=%s pageUrl=%s' % (url, appString, playpath, self.swf_url, PAGEURL)
        
        yield {'Channel'     : CHANNEL,
               'Title'       : CHANNEL,
               'Director'    : CHANNEL,
               'Genre'       : CHANNEL,
               'Plot'        : CHANNEL,
               'PlotOutline' : CHANNEL,
               'id'          : stub,
               'url'         : playerURL
               }

    def getChannelDetail(self):
        return {'Channel': CHANNEL,
                'Thumb':   LOGOICON,
                'Title':   CHANNEL,
                'mode':    MenuConstants.MODE_MAINMENU,
                'Plot':    CHANNEL}

                   
    def getMainMenu(self):
        # Load up the AerTV page, request the EPG data
        # This is overkill, but allows us to build the full channel list easily, and allows us to fetch channel logos and so on
        
        self.login()
        
        (opener, req) = self.makeOpenerAndRequest()

        # This is what we ask for: EPG data.
        # Returns a JSON data array, sorta. Wrapped in "()" for some reason
        request_data = urllib.urlencode({'source':'epg', 'type':'basic', 'length':'2'})
        f = opener.open(req, request_data)
        stuff = f.read()
        f.close()
                
        epgJSON = S.loads(stuff[1:-1])

        self.logout()
           
        for channelEntry in epgJSON['data']:
               yield {'Channel' : CHANNEL,
                      'Thumb'   : channelEntry['channel']['logo'].encode("utf-8"),
                      'url'     : channelEntry['channel']['slug'].encode("utf-8"),
                      'Title'   : channelEntry['channel']['title'].encode("utf-8"),
                      'mode'    : MenuConstants.MODE_PLAYVIDEO}
    
               
    def makeOpenerAndRequest(self):        
        epochTimeMS = int(round(time.time() * 1000.0))
        callbackToken =  "jQuery1610%s_%s" % ( random.randint(3000000, 90000000000), epochTimeMS)
        
        # Change the User Agent, probably doesn't matter but pretend to be a Windows 7/64 machine running Chrome 17
        USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.46 Safari/535.11'

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        req = urllib2.Request( MAIN_REQUEST_URL + callbackToken)
        req.add_header('X_REQUESTED_WITH','XMLHttpRequest')
        req.add_header('Content-type', 'application/x-www-form-urlencoded')
        req.add_header('Accept', 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript')
        req.add_header('User-Agent', USER_AGENT)
        req.add_header('X-Forwarded-For', FORWARDED_FOR_IP)
        
        return (opener, req)    
    
    # I have not figured out how to get this from the network traffic ... cannot find it being passed
    # So for now, code the lookup here
    def getTSQualifier(self, stub): 
        return {
                'rte-one' : 'RTE',
                'rte-two' : 'RTE2',
                'tv3' : 'TV3',
                'tg4' : 'TG4Sec',
                '3e' : '3E',
                'rte-one1' : 'RTEplus1',
                'rte-news-now' : 'RTENEWSNOW',
                'france24' : 'FRANCE24', 
                'rt' : 'RUSSIATODAY', 
                'rtejr' : 'RTEjunior'
                }.get(stub, "RTE")
                
    def login(self):
        # If the user has set his settings, use them
        # Otherwise, do nothing ...
        if self.settings['aertv_username']:
            (opener, req) = self.makeOpenerAndRequest()
        
            # Returns a JSON data array, sorta. Wrapped in "()" for some reason
            request_data = urllib.urlencode({'frontend':'true', 'opt':'doLogin', 'userid': self.settings['aertv_username'], 'pwd': self.settings['aertv_password']})
        
            f = opener.open(req, request_data)
            stuff = f.read()
            f.close()
            
            # Could parse the JSON but just ignore for now 
        else:
            pass
        
    
    def logout(self):
        # If the user has set his settings, use them
        # Otherwise, do nothing
        if self.settings['aertv_username']:
            (opener, req) = self.makeOpenerAndRequest()
        
            # Returns a JSON data array, sorta. Wrapped in "()" for some reason
            request_data = urllib.urlencode({'frontend':'true', 'opt':'destroySession'})
        
            f = opener.open(req, request_data)
            stuff = f.read()
            f.close()
            
            # Could parse the JSON but just ignore for now 
        else:
            pass
                                                  
if __name__ == '__main__':
    for menu in AerTV(False).getMainMenu():
        print menu
        
    for menu in AerTV(False).getEpisodes('9'):
        print menu
        for detail in AerTV(False).getVideoDetails(menu['url']):
            print detail

