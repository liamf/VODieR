#!/usr/bin/python

"""
    VODie
    kitesurfing@kitesurfing.ie
"""

import re
import sys
from BeautifulSoup import SoupStrainer, MinimalSoup as BeautifulSoup, BeautifulStoneSoup
import urllib, urllib2
import MenuConstants

# URL Constants
TG4_URL          = 'http://live.tg4.ie/%s'
MAINURL          = TG4_URL % ('main.aspx?level=%s')
VIDEO_DETAIL_URL = TG4_URL % ('ajax_controller.aspx?cmd=play&level=&deliverymethod=stream&contentid=%s&istrailer=false&priceid=0&machineid=&bitrate=-1&deliverdrm=false&silent=false&format=mp4&subscriberObjectIdForRegisterPlaybackAction=0&subscriptionpurchase=false')

# Channel constants
CHANNEL = 'TG4'
LOGOICON = 'http://www.tg4.ie/bearla/pics/tg4-logo.gif'

class TG4:

    def getChannelDetail(self):
        return {'Channel'  : CHANNEL,
                'Thumb'    : LOGOICON,
                'Title'    : CHANNEL,
                'mode'     : MenuConstants.MODE_MAINMENU,
                'Plot'     : CHANNEL}
        
    def getVideoDetails(self, url, includeAds = True):
        # Load and Read the URL
        f = urllib2.urlopen(VIDEO_DETAIL_URL%(url))
        text = f.read()
        f.close()
        
        REGEXP = "\'asseturl\':\'(.*?)\'"
        for mymatch in re.findall(REGEXP, text):
            # Load and Read found URL
            f = urllib2.urlopen(mymatch)
            text = f.read()
            f.close()
            
            # Grabbing the MetaBase
            METABASE_REGEXP = '<meta base="(.*?)" />'
            for mymatch2 in re.findall(METABASE_REGEXP, text):
                metabase = mymatch2
            
            # Grabbing the mp4 path
            MP4_REGEXP = '<video src="(.*?)" system-bitrate="1200000" />'
            for mymatch2 in re.findall(MP4_REGEXP, text):
                mp4 = mymatch2

            yield {'Channel'     : CHANNEL,
                   'Title'       : CHANNEL,
                   'Director'    : CHANNEL,
                   'Genre'       : CHANNEL,
                   'Plot'        : CHANNEL,
                   'PlotOutline' : CHANNEL,
                   'id'          : url,
                   'url'         : '%s playpath=%s'%(metabase,mp4)
                   }

    def getMainMenu(self, level = '', mode = MenuConstants.MODE_CREATEMENU):
        # Load and Read URL
        f = urllib2.urlopen(MAINURL%(level))
        text = f.read()
        f.close()
        
        PAGE_REGEXP = '<div id="pageMenu">(.*?)</div>'
        LINK_REGEXP = '<a href="main.aspx\?level=(.*?)"( class="active")?>(.*?)</a>'
        for mymatch in re.findall(PAGE_REGEXP, text):
            for mymatch2 in re.findall(LINK_REGEXP, mymatch):
                yield {'Channel'  : CHANNEL,
                       'Thumb'    : LOGOICON,
                       'url'      : mymatch2[0],
                       'Title'    : str(mymatch2[2]),
                       'mode'     : mode,
                       'Plot'     : 'Alexis'}

    def getMenuItems(self, type):
        if type == MenuConstants.MODE_MAINMENU:
            return self.getMainMenu()
        else:
            return self.getMainMenu(level = type, mode = MenuConstants.MODE_GETEPISODES)
        
    def getEpisodes(self, showID):
        # Load and Read URL
        f = urllib2.urlopen(MAINURL%(showID))
        text = f.read()
        f.close()
        
        LIST_REGEXP = '<div id="mainContentListContent">(.*?)</div></div></div>'
        EPISODE_REGEXP = '<img src="(.*?)" alt="cover art"></div></a><h1><a href="(.*?content=(.*?))" title="Show more info" class="moreinfo">(.*?)</a></h1><p class="shortDescription"><a href="(.*?)" title="Show more info" class="moreinfo">(.*?)</a>'
        for mymatch in re.findall(LIST_REGEXP, text, re.MULTILINE):
            for mymatch2 in re.findall(EPISODE_REGEXP, mymatch, re.MULTILINE):
                # Try to get the required data for this episode
                try:
                    day   = int(mymatch2[5][:2])
                    month = int(mymatch2[5][3:5])
                    year  = int(mymatch2[5][6:8])
                    date  = "%2d-%2d-20%2d" % (day,month,year)
                except (ValueError, IndexError):
                    date  = 'None'
                    year  = 2011
                
                yield {'Channel'     : CHANNEL,
                        'Thumb'      : TG4_URL%(mymatch2[0]),
                        'url'        : mymatch2[2],
                        'Title'      : mymatch2[3],
                        'mode'       : MenuConstants.MODE_PLAYVIDEO,
                        'Plot'       : mymatch2[5],
                        'plotoutline': mymatch2[3],
                        'Date'       : date,
                        'Year'       : year,
                        'Studio'     : CHANNEL}


if __name__ == '__main__':
    for item in TG4().getMainMenu():
        print item
        for episode in TG4().getEpisodes(item['url']):
            print episode
            for video in TG4().getVideoDetails(episode['url']):
                print video
            
