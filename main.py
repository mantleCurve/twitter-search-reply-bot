#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import datetime
from google.appengine.ext import db
import webapp2
import time
import sys
import random
from twython import Twython, TwythonError
from google.appengine.ext import db

class LastTweet(db.Model):
    tweetId = db.StringProperty()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        idnum = 0
        lastTweet = db.GqlQuery("SELECT * FROM LastTweet").fetch(1)[0]
#        try:
#            lastTweet = LastTweet.all()
#        except:
#            lastTweet = None
#        if lastTweet != None:
#            idnum = lastTweet.tweetId
#        else:
#            idnum = "0"
        apiKey = '*****'
        apiSecret = '******'
        accessToken = '******'
        accessTokenSecret = '******'
        twitter = Twython(apiKey,apiSecret,accessToken,accessTokenSecret)
        message = "This book can help improve vocabulary in a natural manner. Its available on Kindle http://goo.gl/Wrrydb"
        search_results = twitter.search(q="your_search_query", since_id = idnum, count=20)
        print(search_results)
        for tweet in search_results["statuses"]:
            screenname = "@" + tweet["user"]["screen_name"]+" ";
            print tweet["id_str"]
            try:
                #self.response.write('Hello world!')
                twitter.update_status(status=screenname + message, in_reply_to_status_id=tweet["id_str"])
            except TwythonError:
                pass
            idnum = tweet["id_str"]
            print(idnum)
        if search_results:
            lastTweet.tweetId = idnum
            lastTweet.put()

       # self.response.write('Hello world!')

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
