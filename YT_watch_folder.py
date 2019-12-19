import os
from threading import Thread
import sys
from os import listdir
import time
import datetime
from mp4file.mp4file import Mp4File
import json
import csv
import shutil

class CountdownTask:

        def youtuberun(self, n):
                os.system('python Youtube_contentID.py')

def go():
    upload = CountdownTask ()

    try:
        youtube_up = Thread (target=upload.youtuberun, args=(10,))
        youtube_up.start()

    except:
        print"upload to Youtube FAIL!!"


def reset_date():
    data1 = {}
    data1['video'] = []
    data1['video'].append({ 'name': 'SHIT'})
    with open('C:\Users\Win7 - 1\PycharmProjects\Upload Video independent\status/YT_data.txt', 'w') as outfile:
        json.dump(data1, outfile)

while 1==1:
    yt = ""
    print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +"  Youtube keeps detecting"

    #print "uploading"
    read = open("C:\Users\Win7 - 1\PycharmProjects\Upload Video independent\status/youtube.txt", 'r')
    for line in read:
       if "1" in line:
           yt = "1"
       else:
           yt = "0"
    path = "C:\Users\Win7 - 1\Desktop\Upload\\news_youtube/"
    upath = unicode(path, 'utf-8')
    onlyfiles = listdir(upath)
    if onlyfiles and yt =="0":
        with open('C:\Users\Win7 - 1\PycharmProjects\Upload Video independent\status/YT_data.txt') as json_file:
            data = json.load(json_file)
            for p in data['video']:
                # print( p['name'])
                if p['name'] == "SHIT":
                    break
                elif p['name'] != "\n":
                    aa = p['name']
                    print p['name']
                    print aa, "is being moved"
                    name = path + "/" + str(aa)
                    a = name.decode('utf8')
                    dest = "C:\Users\Win7 - 1\Desktop\Upload\Uploaded_Live\media/" + str(aa)
                    b = dest.decode('utf8')
                    shutil.move(name, dest)
                    print aa, "is moved"
                else:
                    continue
                print "Done!!!"
            for no in onlyfiles:
                if no.endswith('.mp4'):
                    go()
                    break
            reset_date()
            time.sleep(60)
    time.sleep(120)




