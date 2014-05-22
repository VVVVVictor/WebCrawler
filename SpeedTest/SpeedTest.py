import urllib, urllib2, socket
import time, string, os

hostName = ["baidu", "kickstarter", "prosper", "indiegogo", "lendingclub"]
hostAddr = ["http://www.baidu.com","https://www.kickstarter.com", "https://www.prosper.com", "https://www.indiegogo.com/", "https://www.lendingclub.com/"]
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36'}

def speedtest():
    loopTimes = 10
    for i in range(5):
        print u'['+hostName[i]+']',
        starttime = time.clock()
        
        try:
            for j in range(loopTimes):
                req = urllib2.Request(hostAddr[i], headers = headers)
                res = urllib2.urlopen(req)
                #m = res.read()
            endtime = time.clock()
            print('[connet time]: ' + str((endtime-starttime)/loopTimes) + 's')
        except urllib2.URLError:
            print('CANNOT CONNECT WEBSITE: '+hostAddr[i])
        except KeyboardInterrupt:
            return
        except:
            print('UNKNOWN ERROR WHEN CONNECT '+hostAddr[i])
        
    return

def main():
    try:
        print("*******************************************************************")
        print("* A small tool for testing access speed of some overseas websites.*")
        print("*       baidu  kickstarter  prosper  indiegogo  lendingclub       *")
        print("*******************************************************************")
        print("")
        speedtest()
        #print "Press ENTER to exit...",
        os.system('pause')
    except KeyboardInterrupt:
        print('\nCancelling...')


if __name__ == '__main__':
    main()