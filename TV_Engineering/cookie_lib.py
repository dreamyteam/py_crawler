#encoding: utf-8
import cookielib
import urllib2

from pymongo import MongoClient

def get_db():
    #建立连接
    client = MongoClient("112.74.106.159", 27017)
    db = client.develop
    return db

def get_collection(db):

    collection = db['hotWord']
    return collection


def update(collection,id,cookie):
    collection.update({"_id":id},{"$set":{"cookie":cookie}})


def HandleCookie():
    
    db=get_db()
    collection=get_collection(db)
    content = list(collection.find())
    map(map_page, content)

def map_page(page):
    wid=page['wid']
    cookie = cookielib.CookieJar();
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)
    url='http://data.weibo.com/index/hotword?wid='+wid
    print(url)
    response = opener.open(url)
    ll=''
    for item in cookie:
        ll+=item.name + "=" + item.value + ";"
    print(ll)
    update(collection,page['_id'],ll)





# class HotWord:
#      id=0;
#      wid=''
#      wname=''
#      title=''
#      def __init__(self,id,wid,wname,title):
#         self.id =id
#         self.wid = wid
#         self.wname = wname
#         self.title = title
# def convert_to_dict(obj):
#   dict = {}
#   dict.update(obj.__dict__)
#   return dict





if __name__ == "__main__":
    HandleCookie()