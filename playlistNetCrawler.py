import mechanize
import cookielib
import time
import bs4

AGENT_ALIASES = {
    'Mechanize' : "Mechanize/#{VERSION} Ruby/#{ruby_version} (http://github.com/sparklemotion/mechanize/)",
    'Linux Firefox' : 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.1) Gecko/20100122 firefox/3.6.1',
    'Linux Konqueror' : 'Mozilla/5.0 (compatible; Konqueror/3; Linux)',
    'Linux Mozilla' : 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.4) Gecko/20030624',
    'Mac Firefox' : 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6',
    'Mac Mozilla' : 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X Mach-O; en-US; rv:1.4a) Gecko/20030401',
    'Mac Safari 4' : 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_2; de-at) AppleWebKit/531.21.8 (KHTML, like Gecko) Version/4.0.4 Safari/531.21.10',
    'Mac Safari' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/534.51.22 (KHTML, like Gecko) Version/5.1.1 Safari/534.51.22',
    'Windows Chrome' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.32 Safari/537.36',
    'Windows IE 6' : 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Windows IE 7' : 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Windows IE 8' : 'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Windows IE 9' : 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Windows Mozilla' : 'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.4b) Gecko/20030516 Mozilla Firebird/0.6',
    'iPhone' : 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1C28 Safari/419.3',
    'iPad' : 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10',
    'Android' : 'Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13'
}

class PlaylistNetCrawler():
    br = None  # Main browser object
    dbConnection = None
    genres  = ['alternative','blues','classical','comedy','compilation','country','dance','disco','electronica','folk','heavy-metal','hip-hoprap','house','jazz','latin','pop','punk','rb','reggae','rock','soul','soundtrack','techno','world']
    moods   = ['angry','chillout','cool','dark','dramatic','energetic','funny','futuristic','groovy','happy','intimate','party']
    #USERNAME = "raytrashmail@yahoo.com"        #Not used, can scrape without login
    #PASSWORD = "supermanfly"
    baseURL = "http://playlists.net"
    crawlQueue = []
    completedPages = []

    '''
    Initialized cookiejar, and browser object
    '''
    def __init__(self):
        self.br = mechanize.Browser()
        # Cookie Jar
        cj = cookielib.LWPCookieJar()
        self.br.set_cookiejar(cj)
        # Browser options
        self.br.set_handle_equiv(True)
        self.br.set_handle_gzip(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        # Follows refresh 0 but not hangs on refresh > 0
        self.br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        # Want debugging messages?
        #br.set_debug_http(True)
        #br.set_debug_redirects(True)
        #br.set_debug_responses(True)
        #br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        self.br.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36')]


    '''
    Loads up the initial pages from the genres/moods, appends them to crawlQueue 
    '''
    def crawlCategory(self):
        for genre in self.genres[:1]:
            self.crawlQueue.append("".join(("/playlists/",genre,"/page/1/orderby/most-played")))
            self.processCrawlQueue()


    '''
    While loop, which continues until crawlQueue is empty. This method calls addPagesToQueue , and loadPlaylistURL
    sends the playlist URL on page, to the page scraper, and then after all done, adds more pages"if any" to crawlQueue
    Also adds to completed pages.
    '''
    def processCrawlQueue(self):
        while len(self.crawlQueue) >= 1:
            print 
            print "Crawl Queue",self.crawlQueue
            print "Completed Pages",self.completedPages

            url = self.crawlQueue.pop(0)
            self.completedPages.append(url)
            time.sleep(1)
            r = self.br.open(self.baseURL+url)
            soup = bs4.BeautifulSoup(r.read())
            
            #Gets playlists on page
            self.loadPlaylistURL(soup.find_all('ul'))
            
            #Sends the "Pagination" section of playlists.net to addPages to Queue,
            self.addPagesToQueue(soup.find_all('div'))

    '''
    Takes in the "pagination" section from the html on playlists.net 
    addes new pages to self.crawlQueue, as long as new URL is not located in completedPages or crawlQueue
    '''
    def addPagesToQueue(self,soupObj):
        for item in soupObj:
            if item.get("class"):
                if "paging" in item.get("class"):
                    nextPages = item.find_all("a")
                    for np in nextPages:
                        if "Last" not in np.text.encode("utf-8"):
                            toAddURL = np.get("href")
                            if toAddURL not in self.completedPages and toAddURL not in self.crawlQueue:
                                #print "Added Page:",toAddURL
                                self.crawlQueue.append(toAddURL)

    '''
    Takes in the "playlist" section of a page, and starts segregating the playlists
    '''
    def loadPlaylistURL(self,soupObj):
        for item in soupObj:
            if item.get("class"):
                if 'playlists' in item.get('class'):
                    playlistURL = item.find_all('a')
                    for plurl in playlistURL:
                        if plurl.get('href'):
                            self.scrapePage(plurl.get('href'))

    '''
    scrapes the page and gets necessary information, sends to DB controller
    '''
    def scrapePage(self,url):
        time.sleep(1)
        print url
        r = self.br.open(self.baseURL+"/"+url)
        soup = bs4.BeautifulSoup(r.read())
        print soup



p = PlaylistNetCrawler()
print
p.crawlCategory()




            # print 
            # print "Crawl Queue",self.crawlQueue
            # print "Completed Pages",self.completedPages