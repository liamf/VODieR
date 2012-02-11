#!/usr/bin/python

"""
    Brightcove class
    Based on version from andrepl repository @ git://github.com/andrepl/plugin.video.canada.on.demand.git
"""

import time
import cgi
import datetime
import httplib
import urllib
import xbmcplugin
import xbmc
import re

try:
    from pyamf import remoting
    has_pyamf = True
except ImportError:
    has_pyamf = False
    
   
# Base class ... helps with channels which are Brightcove served (AerTV and TG4)
class BrightcoveBaseChannel:
    
    def __init(self):
        pass
       
    def get_swf_url(self):
        conn = httplib.HTTPConnection('c.brightcove.com')
        qsdata = dict(width=self.flashWidth, height=self.flashHeight, flashID=self.flash_experience_id, 
                      bgcolor=self.bgColour, playerID=self.playerId, publisherID=self.publisherId,
                      isSlim='true', wmode=self.flashwmode, optimizedContentLoad='true', autoStart=self.autoStart, debuggerID='')
        qsdata['@videoPlayer'] = self.videoId
        conn.request("GET", "/services/viewer/federated_f9?&" + urllib.urlencode(qsdata))
        resp = conn.getresponse()
        location = resp.getheader('location')
        base = location.split("?",1)[0]
        location = base.replace("BrightcoveBootloader.swf", "federatedVideoUI/BrightcoveBootloader.swf")
        self.swf_url = location 
        
    



    
    