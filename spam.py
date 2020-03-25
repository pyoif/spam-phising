import mechanize, os, re, sys, termios, tty, argparse
from datetime import datetime
import http.cookiejar as cookielib
from texttable import Texttable

parser = argparse.ArgumentParser(description='Spam web phising dengan script ini')
parser.add_argument('-u', '--url', dest='url', help='URL phising tujuan untuk di spam', default='')
parser.add_argument('-p', '--pesan', dest='pesan', help='Pesan untuk pembuat phising', default='')
parser.add_argument('-py', '--proxy', dest='proxy', help='Proxy untuk digunakan spam URL (contoh: 127.0.0.1:8080)', default='')
args = parser.parse_args()

def getpos():

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

    # reading the actual values, but what if a keystroke appears while reading
    # from stdin? As dirty work around, getpos() returns if this fails: None
    try:
        matches = re.match(r"^\x1b\[(\d*);(\d*)R", buf)
        groups = matches.groups()
    except AttributeError:
        return None

    return (int(groups[0]), int(groups[1]))
br = mechanize.Browser()
cookiejar = cookielib.LWPCookieJar()
br.set_cookiejar( cookiejar )
br.set_handle_equiv( True )
br.set_handle_gzip( True )
br.set_handle_redirect( True )
br.set_handle_referer( True )
br.set_handle_robots( False )
br._factory.is_html = True

br.set_handle_refresh( mechanize._http.HTTPRefreshProcessor(), max_time = 1)
br.addheaders = [('User-agent', 'Mozilla/5.0 (x11; U; Linuxi686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'), ('Accept', '*/*')]
(br.set_proxies({"https":args.proxy,"http":args.proxy}) if args.proxy != '' else '')
br.set_handled_schemes(['http', 'https'])

if args.url == '':
	while True:
		url = input('masukan url:')
		if url == '':
			print('url tidak boleh kosong')
		else:
			break
else:
	url = args.url
count = 0
gagal = 0
jml = input('masukan jumlah (kosongkan untuk unlimited):')
try:
	jml = int(jml)
except ValueError:
	try:
		jml = float(jml)
		jml = int(round(jml))
	except ValueError:
		jml = str('unlimited')
if args.pesan == '':
	while True:
		pesan = input('masukan pesan untuk pembuat phising:')
		if pesan == '':
			print('pesan ga boleh kosong')
		else:
			break
else:
	pesan = args.pesan
proxy = args.proxy
clear = lambda: os.system('clear')
clear()
table = Texttable()
tabhead = ['url'.upper(),'pesan'.upper(),'jumlah spam'.upper()]
(tabhead.insert(2,'proxy') if proxy != '' else '')
table.header(tabhead)
col, line = os.get_terminal_size()
table.set_max_width(col)
tabrows = [url, pesan, jml]
(tabrows.insert(2,proxy) if proxy != '' else '')
table.add_rows([tabrows], header=False)
print(table.draw())
l, c = getpos()
while(count != jml):
	info = Texttable()
	headinfo = ['paket terkirim','berhasil','gagal','waktu']
	#(headinfo.insert(3, 'proxy') if args.proxy != '' else '')
	info.header(headinfo)
	col, line = os.get_terminal_size()
	info.set_max_width(col)
	try:
		br.open(url)
		fsp = 0
		for html in br.forms():
			html.set_all_readonly(False)
			#print(html)
			br.select_form(nr=fsp)
			#print(html)
			for input in html.controls:
				if str(input.type) != 'hidden' and str(input.type) != 'select' and input.name != None:
					#print(input.type)
					br[str(input.name)] = pesan
				elif input.type == 'select':
					for item in br.find_control(input.name).items:
						if str(item) != '*':
							item.selected = True
							break
			#print(br.forms()[0])
			br.submit()
			br.back()
			fsp += 1
		count += 1
		rowsinfo = [count, '0' if (count - gagal) <= 0 else count-gagal, gagal, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
		#(rowsinfo.insert(3, args.proxy) if args.proxy != '' else '')
		info.add_rows([rowsinfo], header=False)
		print(("\x1b[K%s{}" % ("\x1b["+str(l)+";0H")).format(info.draw()))
	except KeyboardInterrupt:
		print('selamat tinggal')
		break
	except:
		gagal += 1
		count += 1
		rowsinfo = [count, '0' if (count-gagal) <= 0 else count-gagal, gagal, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
		#(rowsinfo.insert(3, args.proxy) if args.proxy != '' else '')
		info.add_rows([rowsinfo], header=False)
		print(("\x1b[K%s{}" % ("\x1b["+str(l)+";0H")).format(info.draw()))
