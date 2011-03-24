from nevow import rend
import datetime
from string import Template

class StatsServer(rend.Page):
    addSlash = True
    
    def __init__(self, scanner):
        print "started"
        self.start_time = datetime.datetime.utcnow()
        self.scanner = scanner
    
    def renderHTTP(self, ctx):
        pagestr = """
            <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">
            <html><head><title>stats</title>
                    <meta http-equiv="pragma" content="no-cache">
                    <meta http-equiv="expires" content="0">
            </head><body>
            time elapsed = $time_elapsed ( hh:mm:ss.xxxxxx)<br/>
            tweets per hour = $tweets_per_hour <br/>
            tweets per day = $tweets_per_day <br/>
        """
        time_elapsed = datetime.datetime.utcnow() - self.start_time

        pagestr = Template(pagestr).safe_substitute(
            time_elapsed = str(time_elapsed),
            tweets_per_hour = str(int(self.scanner.stats.nb_of_tweets*3600.0/time_elapsed.seconds)),
            tweets_per_day = str(int(self.scanner.stats.nb_of_tweets*3600.0*24/time_elapsed.seconds)),
        )
        zeigeist= sorted(self.scanner.stats._hashtags.items(), key=lambda x:-x[1])
        for i in xrange(20):
            try:
                h = zeigeist[i][0]
                url = "http://twitter.com/#!/search/%23"+h
                pagestr+="<a href='%s'>%s</a>"%(url,h)+','+str(zeigeist[i][1])+"<br/>"
            except: break

        pagestr+="""</body></html>"""
        return pagestr

