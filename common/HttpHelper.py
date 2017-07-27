import urllib
import urllib2


def httpGet(url):
    # print url
    req = urllib2.Request(url)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res
