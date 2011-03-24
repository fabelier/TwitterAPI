from twisted.application import service, internet

from twisted.web import resource, server


from nevow import appserver

from get_tweets import GetStream 
from stats_server import StatsServer 

http_listening_port = 8082



application = service.Application("scanner")
internet.TCPServer(http_listening_port, appserver.NevowSite(StatsServer(GetStream()))).setServiceParent(application)
print "server running on http://xxxx:%d/"%http_listening_port
