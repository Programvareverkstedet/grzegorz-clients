from functools import wraps
from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode
import threading
import youtube_dl
from youtube_dl.utils import DownloadError

class Namespace(object): pass

def filter_query_params(url, allowed=[]):
	split_url = urlsplit(url)
	
	qs = parse_qs(split_url.query)
	print(qs)
	for key in list(qs.keys()):
		if key not in allowed:
			del qs[key]
	
	return urlunsplit((
		split_url.scheme, 
		split_url.netloc, 
		split_url.path, 
		urlencode(qs, doseq=True), 
		split_url.fragment,
		))

def get_youtube_metadata(url, ydl = youtube_dl.YoutubeDL()):
	if urlsplit(url).netloc.lower() in ("www.youtube.com", "youtube.com", "youtub.be"):
		#Stop it from doing the whole playlist
		url = filter_query_params(url, allowed=["v"])
	
	try:
		resp = ydl.extract_info(url, download=False)
	except DownloadError:
		return None
	#print resp.keys()
	
	title = resp.get('title')
	length = resp.get('duration')
	
	#print( title, "%i:%.2i" % (length//60, length%60))
	return {"title":title, "length":seconds_to_timestamp(length)}

def seconds_to_timestamp(s):
	return "%i:%.2i" % (s//60, s%60)

# decorator:
def call_as_thread(func): # This will discard any return value!
	@wraps(func)
	def new_func(*args, **kwargs):
		threading.Thread(
			target = func,
			args = args,
			kwargs = kwargs
			).start()
	return new_func
