#!/usr/bin/python

"""
    VODie
    kitesurfing@kitesurfing.ie
"""

import re
import sys
from BeautifulSoup import SoupStrainer, MinimalSoup as BeautifulSoup, BeautifulStoneSoup
import urllib, urllib2, cookielib
import time

KNOWN_TV3_SHOWS_URL  = 'http://xbmc-vodie.googlecode.com/svn/trunk/plugin.video.vodie/xml/tv3shows.json'
GET_SERIES_URL    = 'http://www.thetvdb.com/api/GetSeries.php?seriesname=%s'
SERIE_DETAILS_URL = 'http://cache.thetvdb.com/api/1D62F2F90030C444/series/%s/banners'

BANNER_URL = 'http://cache.thetvdb.com/banners/%s'

KNOWN_SHOWS = {
               "Castle" : {"TVDBName":"Castle (2009)",},
               }

IGNORE_SHOWS = ["The Daily Show",
                "Dermot's Secret Garden",
                "Champions League Magazine",
                "Cheltenham Festival",
                "About the House",
                "Against The Head",
                "Airtricity League Live: St Patrick's Athletic V Bohemians",
                "The All Ireland Talent Show",
                "The All Ireland Talent Show - Backstage",
                "The All Ireland Talent Show - Results",
                "Animal Clinic",
                "Anonymous",
                "Eco Eye",
                "Election 2011",
                "Elev8",
                "The Frontline",
                "Families in the Wild",
                "Four Live",
                "From Here to Maternity",
                "Give Up Yer Aul Sins",
                "Grubz Up!",
                "Hill Walks",
                "How to Create a Garden",
                "hubble",
                "International Soccer Friendly Highlights: Republic of Ireland v Uruguay",
                "iWitness",
                "Katherine Lynch's Wagons' Den",
                "Last Lioness",
                "Leaders' Questions",
                "League Sunday",
                "Living The Wildlife",
                "Lotto",
                "The Late Late Show",
                "Magners League: Munster v Leinster",
                "Magners League: Munster v Newport-Gwent Dragons",
                "Magners League: Newport v Leinster",
                "Mass for St Patrick's Day",
                "Mass on Sunday",
                "MasterChef: The Professionals",
                "Mattie",
                "MNS",
                "The Meaning of Life with Gay Byrne",
                "The Mountain",
                "Nationwide",
                "Nine News",
                "News on Two and World Forecast",
                "News2Day",
                "Nuacht and News with Signing",
                "National Lottery Skyfest",
                "Neven Maguire: Home Chef",
                "Now That's What You Called News 2010",
                "Oireachtas Report",
                "One News",
                "Octonauts",
                "Off the Rails - On Tour",
                "Prime Time",
                "Pro Box Live",
                "Red",
                "Republic of Telly",
                "The Restaurant",
                "The Rumour Room",
                "RED Radar",
                "Roomers",
                "Scannal",
                "Services of the Word",
                "Six Nations Championship: France v Wales",
                "Six Nations Championship: Ireland v England",
                "Six Nations Championship: Rugby Extra",
                "Six Nations Championship: Scotland v Italy",
                "Six One News",
                "St Patrick's Day Festival Parade",
                "St Patrick's Day Highlights",
                "StoryLand: Free House",
                "StoryLand: Lucky Run",
                "StoryLand: Rent A Friend Promo",
                "StoryLand: Street Cobra",
                "StoryLand: The Last Security Man",
                "StoryLand: The Last Security Man promo",
                "StoryLand: The Masterplan",
                "StoryLand: The Outlaw Concy Ryan",
                "StoryLand: WartGirl",
                "StoryLand: Rent A Friend",
                "Six Nations U20's Internationals: Ireland v England",
                "Stuck for Words",
                "The Saturday Night Show",
                "The Week in Politics",
                "Val Falvey T.D.",
                "Wagons' Den",
                "Winning Streak"
                ]

class Util:
    
    def saveSerieDetail(self, serieName, serie):
        if not serieName in KNOWN_SHOWS.keys():
            KNOWN_SHOWS[serieName] = {"TVDBName":serieName}

        KNOWN_SHOWS[serieName]['id'] = str(serie.id.string)
        KNOWN_SHOWS[serieName]['banner'] = str(BANNER_URL % (serie.banner.string))
        
        print 'IMDB'
        print str(serie.imdb_id.string)
        KNOWN_SHOWS[serieName]['IMDB_ID'] = str(serie.imdb_id.string)
        
        #self.getDetailsForSerieByID(serieName, KNOWN_SHOWS[serieName]['id'])
        
    def getSeriesDetailsByName(self, serieName):
        
        if serieName in IGNORE_SHOWS:
            return None
        
        print 'checking: ' + serieName
        
        if serieName in KNOWN_SHOWS.keys():
            url = GET_SERIES_URL % (urllib.quote(KNOWN_SHOWS[serieName]['TVDBName']))
        else:
            url = GET_SERIES_URL % (urllib.quote(serieName))
                
        try:
            # Change the User Agent
            USER_AGENT = 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10'
                    
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            
            req = urllib2.Request(url)
            req.add_header('User-Agent', USER_AGENT)
    
            resp = opener.open(req)
            
            soup = BeautifulStoneSoup(resp.read())
            resp.close()
            
            if len(soup.findAll('series')) == 1:
                self.saveSerieDetail(serieName, soup.series) 
            else:
                for serie in soup.findAll('series'):
                    if serie.seriesname.string == serieName:
                        self.saveSerieDetail(serieName, serie)
            
            if serieName in KNOWN_SHOWS.keys():
                return KNOWN_SHOWS[serieName]
            return None
        except:
            print 'Error: ' + url
            return None
        
    def getDetailsForSerieByID(self, serieName, serieID):
        url = SERIE_DETAILS_URL % (urllib.quote(serieID))

        try:
            # Change the User Agent
            USER_AGENT = 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10'
                    
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            
            req = urllib2.Request(url)
            req.add_header('User-Agent', USER_AGENT)
    
            resp = opener.open(req)
            
            soup = BeautifulStoneSoup(resp.read())
            resp.close()
            
            for banner in soup.banners.findAll('banner'):
                if banner.language.string == 'en':
                    if not 'Fanart' in KNOWN_SHOWS[serieName].keys() and banner.bannertype.string == 'fanart':
                        KNOWN_SHOWS[serieName]['Fanart'] = str(BANNER_URL % (banner.bannerpath.string))
                        if banner.thumbnailpath:
                            KNOWN_SHOWS[serieName]['FanartThumb'] = str(BANNER_URL % (banner.thumbnailpath.string))
                    elif not 'Poster' in KNOWN_SHOWS[serieName].keys() and banner.bannertype.string == 'poster':
                        KNOWN_SHOWS[serieName]['Poster'] = str(BANNER_URL % (banner.bannerpath.string))
                        if banner.thumbnailpath:
                            KNOWN_SHOWS[serieName]['PosterThumb'] = str(BANNER_URL % (banner.thumbnailpath.string))
                    elif not 'Season' in KNOWN_SHOWS[serieName].keys() and banner.bannertype.string == 'season':
                        KNOWN_SHOWS[serieName]['Season'] = str(BANNER_URL % (banner.bannerpath.string))
                        if banner.thumbnailpath:
                            KNOWN_SHOWS[serieName]['SeasonThumb'] = str(BANNER_URL % (banner.thumbnailpath.string))
                    elif not 'Series' in KNOWN_SHOWS[serieName].keys() and banner.bannertype.string == 'series':
                        KNOWN_SHOWS[serieName]['Series'] = str(BANNER_URL % (banner.bannerpath.string))
                        if banner.thumbnailpath:
                            KNOWN_SHOWS[serieName]['SeriesThumb'] = str(BANNER_URL % (banner.thumbnailpath.string))
                            
            return KNOWN_SHOWS[serieName]
        except:
            print 'Error: ' + url
            return None

if __name__ == '__main__':
    #print KNOWN_SHOWS
    
    print Util().getSeriesDetailsByName('Home and Away')
    
    time.sleep(5)
    #print Util().getSeriesDetailsByName('Castle')
    #print Util().getSeriesDetailsByName('Casualty')
    print Util().getSeriesDetailsByName('Desperate Housewives')
    
    #print KNOWN_SHOWS
