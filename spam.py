import mechanize, os, re, sys, termios, tty, argparse, socks, socket
from datetime import datetime
import http.cookiejar as cookielib
from texttable import Texttable
from pathlib import Path
from queue import Queue, Empty
import threading
from threading import Thread

parser = argparse.ArgumentParser(description='Spam web phising dengan script ini')
parser.add_argument('-u', '--url', dest='url', help='Phising URL destination (you can define a .list file)', default='')
parser.add_argument('-m', '--message', dest='message', help='Message for phising creator', default='')
parser.add_argument('-py', '--proxy', dest='proxy', help='Use proxy during spamming (example: 127.0.0.1:8080 or a .list file)', default='')
args = parser.parse_args()
class main:
	__br = ''
	__url = list()
	__message = ''
	__jml = ''
	__proxy = None
	def __init__(self, args):
		self.__url.append(self.__setFFile(args.url)) if self.__isfile(args.url) else self.__url.append(args.url) if args.url != '' else self.__url.append(self.__ask("Insert url destination (you can define .list file):\n->","url"))
		self.__jml = self.__askJml()
		self.__message = args.message if args.message != '' else self.__ask('insert message for creator phising:\n->', 'message')
		self.__proxy = list(self.__setFFile(args.proxy)) if self.__isfile(args.proxy) else args.proxy
	def main(self):
		clear = lambda: os.system('clear')
		clear()
		self.count = 0
		self.gagal = 0
		tabhead = ['url'.upper(),'message'.upper(),'number of spam'.upper()]
		(tabhead.insert(2,'proxy') if len(self.__proxy) != 0 else '')
		tabrows = [self.__url[0] if len(self.__url) == 1 else self.__url, self.__message, self.__jml]
		(tabrows.insert(2,self.__proxy[0] if len(self.__proxy) == 1 else self.__proxy) if len(self.__proxy) != 0 else '')
		print(self.__printTable(tabhead, tabrows))
		l, c = self.__getpos()
		headinfo = ['packet send','success','failed','time']
		pool = ThreadPool(20)
		while(self.count != self.__jml):
			try:
				[[(pool.add_task(Post().setProxy(prox)),pool.add_task(Post().sendRequest(url=url, message=self.__message))) for prox in self.__proxy for url in self.__url] if isinstance(self.__proxy, list) else [(pool.add_task(Post().setProxy(proxy=self.__proxy)), pool.add_task(Post().sendRequest(url=url,message=self.__message))) for url in self.__url] if self.__proxy != '' else pool.add_task(Post().sendRequest(url=url, message=self.__message)) for url in self.__url] and pool.wait_completion()
				rowsinfo = [self.count, '0' if (self.count - self.gagal) <= 0 else self.count-self.gagal, self.gagal, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
				info = self.__printTable(headinfo, rowsinfo)
				print(("\x1b[K%s{}" % ("\x1b["+str(l)+";0H")).format(info))
				#print(len(self.__proxy))
			except KeyboardInterrupt:
				print('good bye')
				break
			#except:
			#	gagal+=1
			#	count+=1
			#	rowsinfo = [count, '0' if (count-gagal) <= 0 else count-gagal, gagal, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
			#	info = self.__printTable(headinfo, rowsinfo)
			#	print(("\x1b[K%s{}" % ("\x1b["+str(l)+";0H")).format(info))
	def __printTable(self, header, rows):
		table = Texttable()
		col, line = os.get_terminal_size()
		table.set_max_width(col)
		table.header(header)
		table.add_rows([rows], header = False)
		return table.draw()
	def __isfile(self, path):
		if Path(path).is_file():
			if Path(path).suffix == '.list':
				return True
			else:
				print('please define .list file')
		else:
			return False
	def __setFFile(self, path):
		a = []
		with open(path, 'r') as fp:
			for i in fp:
				if i.strip() != '':
					a.append(i.strip())
		return a
	def __ask(self, text, var):
		while True:
			a = input(text)
			if self.__isfile(a):
				return self.__setFFile(a)
			else:
				if a != '':
					a = a
					break
				else:
					print("please fill {}".format(var))
		return a
	def __askJml(self):
		jml = input('insert number of spam (leave empty for unlimited):\n->')
		try:
			jml = int(jml)
		except ValueError:
			try:
				jml = float(jml)
				jml = int(round(jml))
			except ValueError:
				jml = str('unlimited')
		return jml
	def __getpos(self):
		buf = ""
		stdin = sys.stdin.fileno()
		tattr = termios.tcgetattr(stdin)
		try:
			tty.setcbreak(stdin, termios.TCSANOW)
			sys.stdout.write("\x1b[6n")
			sys.stdout.flush()
			while True:
				buf += sys.stdin.read(1)
				if buf[-1] == "R":
					break
		finally:
			termios.tcsetattr(stdin, termios.TCSANOW, tattr)
		try:
			matches = re.match(r"^\x1b\[(\d*);(\d*)R", buf)
			groups = matches.groups()
		except AttributeError:
			return None
		return (int(groups[0]), int(groups[1]))
class Post(mechanize.Browser):
	def __init__(self):
		mechanize.Browser.__init__(self)
		self.set_cookiejar(cookielib.LWPCookieJar())
		self.set_handle_equiv( True )
		self.set_handle_gzip( True )
		self.set_handle_redirect( True )
		self.set_handle_referer( True )
		self.set_handle_robots( False )
		self._factory.is_html = True
		self.set_handle_refresh( mechanize._http.HTTPRefreshProcessor(), max_time = 1)
		self.addheaders = [('User-agent', 'Mozilla/5.0 (x11; U; Linuxi686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'), ('Accept', '*/*')]
	def setProxy(self, proxy):
		#print(option[0])
		host, port = proxy.split(':')
		socks.set_default_proxy(socks.PROXY_TYPE_HTTP, host, int(port))
		socket.socket = socks.socksocket
	def sendRequest(self, **opt):
		try:
			#print(opt['url'])
			self.open(opt['url'], timeout=2)
			fsp = 0
			for html in self.forms():
				html.set_all_readonly(False)
				self.select_form(nr=fsp)
				for input in html.controls:
					if str(input.type) != 'hidden' and str(input.type) != 'select' and str(input.type) != 'submitbutton'  and input.name != None:
						self[str(input.name)] = opt['message']
					elif input.type == 'select':
						for item in self.find_control(input.name).items:
							if str(item) != '*':
								item.selected = True
								break
				self.submit()
				self.back()
				fsp+=1
			spam.count+=1
		except Exception as e:
			spam.count += 1
			spam.gagal += 1
			#raise e
class Worker(Thread):
	_TIMEOUT = 10
	def __init__(self, tasks, th_num):
		Thread.__init__(self)
		self.tasks = tasks
		self.daemon, self.th_num = True, th_num
		self.done = threading.Event()
		self.start()
	def run(self):
		while not self.done.is_set():
			try:
				func, args, kwargs = self.tasks.get(block=True,timeout=self._TIMEOUT)
				try:
					func(*args, **kwargs)
				except Exception as e:
					pass
				finally:
					self.tasks.task_done()
			except Empty as e:
				pass
	def signal_exit(self):
		self.done.set()
class ThreadPool:
	def __init__(self, num_threads, tasks=[]):
		self.tasks = Queue(num_threads)
		self.workers = []
		self.done = False
		self._init_workers(num_threads)
		for task in tasks:
			self.tasks.put(task)
	def _init_workers(self, num_threads):
		for i in range(num_threads):
			self.workers.append(Worker(self.tasks, i))
	def add_task(self, func, *args, **kwargs):
		self.tasks.put((func, args, kwargs))
	def _close_all_threads(self):
		for workr in self.workers:
			workr.signal_exit()
		self.workers = []
	def wait_completion(self):
		self.tasks.join()
	def __del__(self):
		self._close_all_threads()
spam = main(args)
spam.main()
