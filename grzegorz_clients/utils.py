from functools import wraps
import threading
import youtube_dl

class Namespace(object): pass

def get_youtube_metadata(url, ydl = youtube_dl.YoutubeDL()):
	#todo: check if url is valid
	
	#todo, stop it from doung the whole playlist
	resp = ydl.extract_info(url, download=False)
	#print resp.keys()
	
	title = resp.get('title')
	length = resp.get('duration')
	
	#print( title, "%i:%.2i" % (length//60, length%60))
	return title, "%i:%.2i" % (length//60, length%60)

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
