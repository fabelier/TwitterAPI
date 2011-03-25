import simplejson
from twisted.web import client
from twisted.internet import reactor
import datetime

import base64

class GetStream:
    username = "your_twitter_id"
    password = "the_corresponding_password"
    def __init__(self):
        self.start()
        self.chunk = ""
        self.stats = Stats()


    def __makeAuthHeader(self, headers={}):
        authorization = base64.encodestring('%s:%s'
            % (self.username, self.password))[:-1]
        headers['Authorization'] = "Basic %s" % authorization
        return headers
        
    def start(self):
        client.downloadPage("http://stream.twitter.com/1/statuses/sample.json",
                            self,  #file
                            headers = self.__makeAuthHeader()
                            ).addBoth(self.stopped)
       
    def stopped(self, data):
        self.chunk = ""
        reactor.callLater(10.0, self.start)

    def write(self, b):  self.process(b)
    def close(self):  pass
    def open(self): pass
    def read(self): return None
    
    def process(self,s):
        statuses = s.split('\r')
        statuses[0]=self.chunk+statuses[0]
        self.chunk = statuses[-1]
        for status_json in statuses[:-1]:
            try:
                status = simplejson.loads(status_json)
                if 'limit' in status or 'delete' in status: continue
                self.stats.nb_of_tweets+=1
                text = safe_str(status["text"])
                if '#' not in text: continue
                #print text
                hashtags = status.get("entities",dict()).get("hashtags",[])
                hashtags = [safe_str(e.get("text")).lower() for e in hashtags if "text" in e]
                for hashtag in hashtags:
                    self.stats._hashtags[hashtag] = self.stats._hashtags.get(hashtag,0)+1
                    
                    if not self.stats._hashtags_timeline.get(hashtag):      self.stats._hashtags_timeline[hashtag] = []
                    self.stats._hashtags_timeline[hashtag].insert(0,datetime.datetime.utcnow())

            except Exception, e:
                #continue
                print 50*"*"
                print e
                print 50*"-"
                print status_json
                print 50*"*"
                
        if datetime.datetime.utcnow() - self.stats.last_cleanup_time > datetime.timedelta(minutes=1): self.stats.clean_up()

class Stats:
    def __init__(self):
        self.nb_of_tweets = 0
        self._hashtags = dict()
        self._hashtags_timeline = dict()
        self.last_cleanup_time = datetime.datetime.utcnow()
        
    def clean_up(self):
        for h, tl in self._hashtags_timeline.items():
            while tl:
                old = tl.pop()
                if not ( datetime.datetime.utcnow() - old > datetime.timedelta(hours=1) ):
                    tl.append(old)
                    break
            self._hashtags[h] = len(tl)
            if not tl:
                try: del(self._hashtags[h])
                except: pass
                try: del(self._hashtags_timeline[h])
                except: pass
        self.last_cleanup_time = datetime.datetime.utcnow()




def safe_str(obj):
    """ return the byte string representation of obj """
    try:
        return str(obj)
    except UnicodeEncodeError:
        # obj is unicode
        return unicode(obj).encode('unicode_escape')
                

