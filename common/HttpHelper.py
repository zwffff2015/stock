import urllib
import urllib2
import StringIO, gzip
import chardet


def httpGet(url, headers=None):
    # print url
    req = urllib2.Request(url)
    if headers is not None:
        for key in headers:
            req.add_header(key, headers.get(key))
            # req.add_header(key, "http://www.iwencai.com/stockpick/search?ts=1&f=1&qs=stockhome_topbar_click&w=pe%3E0")
    res_data = urllib2.urlopen(req)
    contentEncoding = res_data.headers.get('Content-Encoding')
    if contentEncoding is not None and contentEncoding == 'gzip':
        return gzipDecode(res_data.read())
    else:
        return res_data.read()


def getEncoding(data):
    detectedEncodingDict = chardet.detect(data)
    return detectedEncodingDict.get('encoding')


def gzipDecode(data):
    compressedstream = StringIO.StringIO(data)
    gziper = gzip.GzipFile(fileobj=compressedstream)
    data2 = gziper.read()
    return data2
