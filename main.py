import requests
from bs4 import BeautifulSoup
import app_data
import guiloader
import json
from urllib3 import disable_warnings, exceptions
import re
from geopy.geocoders import Nominatim
import threading
from tkinter import SUNKEN, RAISED
import xlsxwriter
from string import ascii_uppercase as alp

disable_warnings(exceptions.InsecureRequestWarning)

#login Handler
class loginHandler:
	def __init__(self):
		self.loginapp = guiloader.loginApp(self)

	def login(self, e=None):
		if(self.loginapp.key.get()=="test"):
			data = app_data.justdial()

			self.stop()

			handlerMain = handler(data)			
			handlerMain.run()
		else:
			self.loginapp.messageBox("error","Wrong login","The serial key was wrong!")
		
	def run(self):
		self.loginapp.ct.run()

	def stop(self):
		self.loginapp.ct.stop()
#Main gui handler
class handler:
	def __init__(self, data):
		self.mainapp = guiloader.mainApp(data, self)

	def getValue(self, input):
		return self.mainapp.inputs[input].get()
		
	def start(self, data):
		#Check for emptys
		if data[0]=="":
			return self.mainapp.messageBox("error","Input error","Please don't leave the query empty.")
		else:
			self.scraper = scraper(data[0],data[1], data[2], self)
			self.scraper.start()
			self.mainapp.navbuttons[0].config(relief=SUNKEN)
	def stop(self):
		if(self.scraper.isAlive()):
			self.scraper.stop()
			self.mainapp.navbuttons[0].config(relief=RAISED)
		else:
			self.mainapp.messageBox("error","Error","There isn't a program running")

	def export(self):
		file = xlsxwriter.Workbook("export.xlsx")
		sheet = file.add_worksheet()

		a=0
		for column in self.mainapp.columns:
			sheet.write(alp[a]+"1", column)
			a+=1
		a = 2
		for child in self.mainapp.datatable.get_children():
			values = self.mainapp.datatable.item(child)["values"]
			b = 0
			for value in range(0, len(values)):
				sheet.write(alp[b]+str(a), values[value])
				b += 1
			a += 1
		file.close()
		self.mainapp.messageBox("info","Exported","Exported entries to file export.xlsx")
	def clear(self):
		self.mainapp.datatable.delete(*self.mainapp.datatable.get_children())

	def insert(self, data):
		self.mainapp.datatable.insert("",'end',values=tuple(data))

	def run(self):
		self.mainapp.run()

class scraper(threading.Thread):
	def __init__(self, query, location, maxpage, handler):
		threading.Thread.__init__(self)
		self.query = query
		self.location = location
		self.handler = handler
		self.maxpage = maxpage
		self._running = True
		self.url = "https://www.justdial.com/functions/ajxsearch.php?national_search=0&act=pagination&city="+location+"&search="+query+"&page={0}"
		self.headers = {
			"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
			"Referer": "https://www.justdial.com/"+location+"/"+query
			}
		self.cookies = self.getSession()
		self.geolocator = Nominatim(user_agent="scraper")
		self.EMAIL_REGEX = r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+"

	def getSession(self):
		r = requests.get("https://justdial.com", verify=False, headers = self.headers)
		return r.cookies.get_dict()

	#Get links from the html
	def getUrls(self, page):
		r = requests.get(self.url.format(str(page)), verify=False, headers=self.headers, cookies=self.cookies)
		s = BeautifulSoup(json.loads(r.text)["markup"],"html.parser")
		urls = []

		for a in s.find_all("li", {"class":"cntanr"}):
			urls.append(a["data-href"])

		return urls
	#Convert icons to numbers
	def getNumbers(self, html):
		snippet = re.search(r'grayscale}(.*?).mobilesv{', html).group(1)
		codes = snippet.split(".")
		decode={}
		for a in range(0,11):
			if(a+1==11):
				decode[re.search(r'icon-(.*?):bef', codes[a+1]).group(1)]="+"
				continue
			decode[re.search(r'icon-(.*?):bef', codes[a+1]).group(1)]=str(a)
		return decode
	#Get data from the links
	def getData(self, url):
		r = requests.get(url, verify=False, headers=self.headers, cookies=self.cookies)
		s = BeautifulSoup(r.text, "lxml")
		decode = self.getNumbers(s.find_all("style")[1].text)
		contact = s.find("div",{"class":"paddingR0"})
		category = ', '.join([i['title'] for i in contact.find_all("a",{"class":"lng_also_lst1"})])
		company = s.find("span",{"class":"fn"}).text
		address = contact.find("span",{"class":"lng_add"}).text
		
		numbers = []
		for c in contact.find_all("a",{"class":"tel ttel"}):
			numbers.append(''.join([decode[a['class'][1].split("-")[1]] for a in c.find_all("span",{"class":"mobilesv"})]))

		try:
			location = self.geolocator.geocode(address.split("-")[0])
			latitude = location.latitude
			longitude = location.longitude
		except:
			latitude, longitude = "",""

		votes = s.find("span",{"class":"votes"}).text
		rating = s.find("span",{"class":"value-titles"}).text
		verified = s.find("span",{"class":"jd_verified"})!=None
		trusted = s.find("span",{"class":"jd_trusted"})!=None

		try:
			website = contact.find("i",{"class":"web_ic"}).find_next_sibling().findChild()['href']
		except:
			website = ""
		try:
			r = requests.get(website, verify=False, headers=self.headers)
			email = re.search(self.EMAIL_REGEX, r.text).group()
		except:
			email = ""

		return [category, company, address, email, numbers, latitude, longitude, rating, votes, verified, trusted, website]
	def run(self):
		page = 1
		while self._running and page <= int(self.maxpage):
			for link in self.getUrls(page):
				if(self._running):
					self.handler.insert(self.getData(link))
			page += 1
		if(self._running):
			self.handler.mainapp.messageBox("info","Success","Scraper has finished!")
	def stop(self):
		self._running = False

if __name__ == '__main__':
	login = loginHandler()
	login.run()