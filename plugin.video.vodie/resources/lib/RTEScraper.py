#!/usr/bin/python

"""
    VODie
    kitesurfing@kitesurfing.ie
    
    modified: liam.friel@gmail.com
"""

import re
import sys
from BeautifulSoup import BeautifulStoneSoup
import urllib, urllib2
from TVSeriesUtil import Util
import MenuConstants
import simplejson as S

# Player Constants
CONFIGURL = 'http://www.rte.ie/player/config/config.xml'
DEFAULTSWFURL = 'http://www.rte.ie/player/assets/player_458.swf'
PAGEURL = 'http://www.rte.ie/player/ie/'

# RTE site change: hacky way of parsing returned data
# The VODie 2.x code from doctormo does this better, and it would be better for the VODie plugin to migrate to that way
EPISODE = "http://feeds.rasset.ie/rteavgen/player/playlist?type=iptv1&showId=%s"

# PROGRAM = "http://feeds.rasset.ie/rteavgen/player/programme/?id=%s"
    
# URL Constants
PROGRAMME_URL    = 'http://dj.rte.ie/vodfeeds/feedgenerator/programme/?id='
SHOW_BY_TYPE_URL = 'http://feeds.rasset.ie/rteavgen/player/%s/'
LIVEURL          = 'http://dj.rte.ie/vodfeeds/feedgenerator/live/'
FEATURES         = 'features'
LATEST           = 'latest'
LASTCHANCE       = 'lastchance'
GENRELIST        = 'genrelist'
LIVE             = 'live'

# Channel Constants
CHANNEL = 'RTE'
LOGOICON = 'http://www.rte.ie/iptv/images/logo.gif'

# Main Menu Items
LIVEMENU =      {'Thumb'    : LOGOICON,
                 'Channel'  : CHANNEL,
                 'Title'    : 'Live',
                 'url'      : LIVE,
                 'mode'     : MenuConstants.MODE_CREATEMENU ,
                 'Plot'     : 'Watch Live'
                 }
FEATMENU =      {'Thumb'    : LOGOICON,
                 'Channel'  : CHANNEL,
                 'Title'    : 'Features'            ,
                 'url'      : FEATURES      ,
                 'mode'     : MenuConstants.MODE_CREATEMENU ,
                 'Plot'     : 'Features'
                 }
LTSTMENU =      {'Thumb'    : LOGOICON,
                 'Channel'  : CHANNEL,
                 'Title'    : 'Latest',
                 'url'      : LATEST,
                 'mode'     : MenuConstants.MODE_CREATEMENU ,
                 'Plot'     : 'Latest'
                 }
LASTMENU =      {'Thumb'    : LOGOICON,
                 'Channel'  : CHANNEL,
                 'Title'    : 'Last Chance',
                 'url'      : LASTCHANCE,
                 'mode'     : MenuConstants.MODE_CREATEMENU ,
                 'Plot'     : 'Last Chance'
                 }
ATOZMENU =      {'Thumb'    : LOGOICON,
                 'Channel'  : CHANNEL,
                 'Title'    : 'Search by A-Z',
                 'url'      : MenuConstants.MODE_ATOZ,
                 'mode'     : MenuConstants.MODE_CREATEMENU ,
                 'Plot'     : 'Search by A to Z'
                 }
CATYMENU =      {'Thumb'    : LOGOICON,
                 'Channel'  : CHANNEL,
                 'Title'    : 'Search by Category',
                 'url'      : MenuConstants.MODE_CATEGORY ,
                 'mode'     : MenuConstants.MODE_CREATEMENU ,
                 'Plot'     : 'Search by Category'
                 }

class RTE:    
    def __init__(self):
        # We'll try to keep this up to date automatically, but this is a good starting guess
        self.SWFURL = DEFAULTSWFURL
        
    def getShows(self,type, params=''):
        # Live show list comes from a different URL 
        if type == LIVE:
            url = LIVEURL
        else:
            url = SHOW_BY_TYPE_URL%(type) + params
        page = urllib2.urlopen(url)
		
        self.soup = BeautifulStoneSoup(page, selfClosingTags=['link','category','media:player','media:thumbnail'])
        page.close()

        items = self.soup.findAll('entry')
        for item in items:
            id = str(item.id.string).strip()
            title = str(item.title.string).strip()

            pic = LOGOICON                    

            if type == "live":
                # For "live" items, just yield when Now-next is "NOW"
                if item.find(term="NOW"):
                    yield { "id": id, "title":title, "thumb":str(pic)}                 
            else:
                yield { "id": id, "title":title, "thumb":str(pic)}


    def getChannelDetail(self):
        return {'Channel': CHANNEL,
                'Thumb':LOGOICON,
                'Title':'RTE',
                'mode':MenuConstants.MODE_MAINMENU,
                'Plot':'RTE'}

    def getStringFor(self, parent, tagName, attrName = None, default = 'None'):
        if parent.find(tagName):
            if attrName is None:
                return str(parent.find(tagName).string).strip()
            else:
                return str(parent.find(tagName)[attrName])
        else:
            print "Error: Cannot find tagName: %s in %s"%(tagName, parent)
            return default
        
    def updateSWFURL(self):
        f = urllib2.urlopen(CONFIGURL)
        text = f.read()
        f.close()
        
        try:
            for mymatch in re.findall('Player version="(.*?)"', text, re.MULTILINE):
                self.SWFURL = 'http://www.rte.ie/player/assets/player_%s.swf' % mymatch
        except:
            pass        
        
    def getVideoDetails(self, url, includeAds = True):
    
        self.updateSWFURL()
        
        page = urllib2.urlopen(url)
        soup = BeautifulStoneSoup(page, selfClosingTags=['link','category','media:player','media:thumbnail','rte:valid', 'rte:duration', 'rte:statistics'])
        page.close()
        
        entry = soup.find('entry')
        
        published  = self.getStringFor(entry, 'published')
        plot       = self.getStringFor(entry, 'content')
        # This doesn't seem to make any difference
        # Plus, it's often incorrect (for recordings in multiple parts)
        duration   = self.getStringFor(entry, 'rte:duration','formatted')
        rating     = self.getStringFor(entry, 'media:rating')
        copyright  = self.getStringFor(entry, 'media:copyright')
        title      = self.getStringFor(entry, 'title')        
        id         = self.getStringFor(entry, 'id')

        categories = entry.findAll('category')
        categories_str = u''
        for category in categories:
            categories_str = categories_str + u', ' + category['term']
                
        contents = entry.findAll('media:content')
        for content in contents:
            if content['rte:format'] == 'content':
                # Build the RTMP url for XBMC to play the Stream
                RTE_RTMPE_SERVER = str(content['rte:server'])
                RTE_APP = 'rtevod/'
                mp4url = '%s app=%s swfUrl=%s swfVfy=1 playpath=%s'%(RTE_RTMPE_SERVER, RTE_APP, self.SWFURL, str(content['url'])[len(RTE_RTMPE_SERVER):])
                
                # Grab the Part number to add it to the Title.
                # Streams are split into parts due to ads break
                partre = '\_part(\d)\_'
                partMatches = re.findall(partre, mp4url)
                if len(partMatches) > 0:
                    duration = str(content['rte:end'])
                    newtitle = '%s - Part %s' % (title, partMatches[0])
                else:
                    newtitle = title
                
                # Return this show
                yield {'Channel'      : CHANNEL,
                       'TVShowTitle'  : newtitle,
                       'Title'        : newtitle,
                       'MPAA'         : rating,
                       'Director'     : copyright,
                       'Duration'     : duration,
                       'Genre'        : categories_str,
                       'Plot'         : plot,
                       'PlotOutline'  : plot,
                       'id'           : id,
                       'url'          : mp4url,
                       'Date'         : "%s-%s-%s" % ( published[ 8 : 10], published[ 5 : 7 ], published[ : 4 ], )}
            # Direct Links
            elif content['rte:format'] == 'string' and includeAds:
                yield {'Channel'      : CHANNEL,
                       'TVShowTitle'  : content['url'],
                       'Title'        : content['url'],
                       'Plot'         : '',
                       'PlotOutline'  : '',
                       'id'           : id,
                       'url'          : content['url'] }
            # Live Shows
            elif content['rte:format'] == 'live':
                RTE_RTMPE_SERVER = str(content['rte:server'])
                RTE_APP = 'live'
                mp4url = "%s playpath=%s swfUrl=%s swfVfy=1 app=%s pageUrl=%s live=true" % (RTE_RTMPE_SERVER, str(content['url'])[len(RTE_RTMPE_SERVER):], self.SWFURL, RTE_APP, PAGEURL)
                yield {'Channel'      : CHANNEL,
                       'TVShowTitle'  : content['url'],
                       'Title'        : urllib.unquote(content['url']),
                       'Plot'         : '',
                       'PlotOutline'  : '',
                       'id'           : id,
                       'url'          : mp4url }
            # FLV Advertisement
            elif content['rte:format'] == 'advertising' and includeAds:
                page = urllib2.urlopen(content['url'])
                soup = BeautifulStoneSoup(page, selfClosingTags=['CustomParameters','ISCI'])
                page.close()

                for bandwidth_value in ['high', 'medium', 'low']:
                    results = soup.findAll('flv', bandwidth=bandwidth_value)
                    for result in results:
                        if result.contents[0].string != ' ':
                            yield {'Channel'     : CHANNEL,
                                   'TVShowTitle' : result.contents[0].string,
                                   'Title'       : result.contents[0].string,
                                   'Plot'        : '',
                                   'PlotOutline' : '',
                                   'id'          : result.contents[0].string,
                                   'url'         : result.contents[0].string }

    def getMainMenu(self):
# For the moment, remove LIVE. RTMP URL for Live has changed apparently and no longer works
#        return [LIVEMENU,
#                FEATMENU,
#                LTSTMENU,
#                LASTMENU,
#                ATOZMENU,
#                CATYMENU] 
        return [LTSTMENU,
                LASTMENU,
                ATOZMENU,
                CATYMENU] 

    def getEpisodes(self, combinedShowID):
        
        # A bit hacky ...
        # Split into "title" style id and URL
        splitString = re.findall('(.*)__(.*)',combinedShowID)
        titleShowID = str(splitString[0][0])
        showId = str(splitString[0][1]).split('=')[-1]
               
        page = urllib2.urlopen(PROGRAMME_URL + titleShowID)
        soup = BeautifulStoneSoup(page, selfClosingTags=['link','category','media:player','media:thumbnail'])
        page.close()
        
        items = soup.findAll('entry')
        if not items:
            # That works for some things, but not this show ... 
            # OK, that didn't work. Try using the ID to search for episodes
            urlShowID = EPISODE%(showId)            
            page = urllib2.urlopen(urlShowID)
            soup = BeautifulStoneSoup(page, selfClosingTags=['link','category','media:player','media:thumbnail'])
            page.close()            
            items = soup.findAll('entry')
            
        for item in items:
            # This finds the entire element ... get the bit we want
            linkElement = item.find(attrs={'type' : 'application/atom+xml'})
            mymatch = re.findall('href="(.*)"' , str(linkElement)) 
            title = self.getStringFor(item, 'title')
            published = self.getStringFor(item, 'published')
            desc =  self.getStringFor(item, 'media:description')
            thumb =  self.getStringFor(item, 'media:thumbnail', 'url', LOGOICON)
            # Duration doesn't seem to make any difference ... 
            duration = str(int(self.getStringFor(item, 'rte:duration','ms'))/1000/60)
            
            yield { 'PlotOutline'  : title,
                    'Duration'     : duration,
                    'Studio'       : CHANNEL,
                    'Year'         : int("%s" % (published[ : 4 ])),
                    'Date'         : "%s-%s-%s" % ( published[ 8 : 10], published[ 5 : 7 ], published[ : 4 ]),
                    'Thumb'        : thumb,
                    'Channel'      : CHANNEL,
                    'url'          : mymatch[0],
                    'Title'        : title,
                    'mode'         : MenuConstants.MODE_PLAYVIDEO,
                    'Plot'         : desc
                    }
            
    def getMenuItems(self, type, params = '', mode = MenuConstants.MODE_GETEPISODES):
        # the problem is in here
        # for some shows which have several episodes, the correct thing to return is the title (like here)
        # but for some, it seems like the show['id'] would be better
        # this would allow us to find the correct episodes
        # so what we need to do is return both and sort it out when getting the episode
        for show in self.getShows(type, params):
            if type == LIVE:
                yield {'Title':show['title'],
                       'Channel': CHANNEL,
                       'Thumb':show['thumb'],
                       'mode':MenuConstants.MODE_PLAYVIDEO,
                       'url':show['id'],
                       #'Fanart_Image':fanart
                       }
            else:
                yield {'Title':show['title'],
                       'Channel': CHANNEL,
                       'Thumb':show['thumb'],
                       'mode':mode,
                       'url': urllib.quote(show['title']) + "__" + show['id']
                       #'Fanart_Image':fanart
                       }
                        
    def SearchByCategory(self, genre = None):
        if genre == None or genre == '' or genre == 'Search by Category':
            categories = []
            for category in self.getMenuItems(type='genrelist', mode=MenuConstants.MODE_CREATEMENU):
                category['url'] = MenuConstants.MODE_CATEGORY
                categories.append(category)
            return categories
            
        else:
            return self.getMenuItems(type='genre', params='?id=%s'%(urllib.quote(genre)))

    def SearchAtoZ(self, letter = None):
        if letter == None or letter == '' or letter == 'Search by A-Z':
            for item in 'ABCDEFGHIJKLMNOPQRSTUVWXZ':
                yield {'Thumb':LOGOICON,
                       'Channel': CHANNEL,
                       'Title':item,
                       'url':MenuConstants.MODE_ATOZ,
                       'mode':MenuConstants.MODE_CREATEMENU,
                       'Plot':item}
        else:
            for item in self.getMenuItems(type='az', params='?id=%s'%(letter)):
                yield item
                        
if __name__ == '__main__':
    # Test Main Menu
    print RTE().getMainMenu()
    
