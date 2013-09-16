import bs4
#import urllib2
import mechanize
import cookielib
#import time


url = "http://playlists.net/indie-feel-good"
#url = "http://playlists.net/elephantine-the-best-elephant-6-single"
USERNAME = "raytrashmail@yahoo.com"        #Not used, can scrape without login
PASSWORD = "supermanfly"


br = mechanize.Browser()
# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)
# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# Want debugging messages?
#br.set_debug_http(True)
#br.set_debug_redirects(True)
#br.set_debug_responses(True)
#br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
br.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36')]


'''
Crawling page to get spotify user and spotify playlist
'''
# r = br.open(url)
# br.select_form(nr=0)
# br.form['login_username'] = USERNAME
# br.form['login_password'] = PASSWORD
# br.submit()
# 
# 
# soup = bs4.BeautifulSoup(br.response().read())
# 
# results = soup.find_all("a")
# for tag in results:
# 	
# 	if "data-desktop-uri" in tag.attrs:
# 		link = tag.attrs["data-desktop-uri"].encode("utf-8").split("%253A")
# 		spotifyUser = link[link.index("user")+1]
# 		spotifyPlaylist = link[link.index("playlist")+1]
# 		print "User: ",spotifyUser, "Playlist: ",spotifyPlaylist

spotifyUser = "napstersean"
spotifyPlaylist = "3vxotOnOGDlZXyzJPLFnm2"

url = "".join(("https://embed.spotify.com/?uri=spotify:user:",spotifyUser,":playlist:",spotifyPlaylist))

r = br.open(url)
print url
soup = bs4.BeautifulSoup(br.response().read())
results = soup.find_all("ul")
for tag in results:
	if "class" in tag.attrs:
		trackInfo = tag.children
		trackTitle = ''
		artist = ''
		order = 0
		for track in trackInfo:
			if isinstance(track,bs4.element.Tag):
				if "track-title" in track['class']:
					trackTitle = track.string
					order = trackTitle[0:trackTitle.find(".")]
					trackTitle = trackTitle[trackTitle.find(".")+2:]
					
				elif "artist" in track['class']:
					artist = track.string
		print trackTitle, artist, "Source: Spotify", spotifyUser, spotifyPlaylist,order 	 



