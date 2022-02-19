from functools import wraps
import threading

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
