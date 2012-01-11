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

# URL Constants http://www.tg4.ie/en/programmes.html

TG4_URL          = 'http://www.tg4.ie/en/programmes'
MAINURL          = TG4_URL 
VIDEO_DETAIL_URL = TG4_URL 
#VIDEO_DETAIL_URL = TG4_URL % ('ajax_controller.aspx?cmd=play&level=&deliverymethod=stream&contentid=%s&istrailer=false&priceid=0&machineid=&bitrate=-1&deliverdrm=false&silent=false&format=mp4&subscriberObjectIdForRegisterPlaybackAction=0&subscriptionpurchase=false')

# Channel constants
CHANNEL = 'TG4'
LOGOICON = 'http://www.tg4.ie/assets/templates/tg4/images/logo-trans.png'

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
        f = urllib2.urlopen(MAINURL)
        text = f.read()
        
        PAGE_REGEXP = '<div id="inner_content1" class="content_box">(.*)</div>'
        PROG_REGEXP = '<div id="schedule_Holder">(.*?)<div class="schedule_Cell1"><a href="(.*?)"><img src="(.*?)" alt="" class="imgBdr" /></a></div>(.*?)<div class="schedule_Cell2"><b>(.*?)</b></div>(.*?)<div class="schedule_Cell6">(.*?)</div>(.*?)</div>'
        
        for mymatch in re.findall(PAGE_REGEXP, text, re.DOTALL):
            for progMatch in re.findall(PROG_REGEXP, mymatch, re.DOTALL):
                yield {'Channel'  : CHANNEL,
                       'Thumb'    : progMatch[2],
                       'url'      : progMatch[1],
                       'Title'    : str(progMatch[4]),
                       'mode'     : MenuConstants.MODE_GETEPISODES,
                       'Plot'     : progMatch[6]}

    def getMenuItems(self, type):
        if type == MenuConstants.MODE_MAINMENU:
            return self.getMainMenu()
        else:
            return self.getMainMenu(level = type, mode = MenuConstants.MODE_GETEPISODES)
        
    def getEpisodes(self, showID):
        
        print showID
        # Load and Read URL
        f = urllib2.urlopen(MAINURL)
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
            
