import requests
from bs4 import BeautifulSoup
import app_data
import guiloader
import json
from urllib3 import disable_warnings, exceptions
import re
import os, subprocess
from geopy.geocoders import Nominatim
import threading
from tkinter import SUNKEN, RAISED
import xlsxwriter
import zipfile, io
from string import ascii_uppercase as alp

disable_warnings(exceptions.InsecureRequestWarning)

#login Handler //If you want to add a login
class loginHandler:
	def __init__(self, data):
		self.loginapp = guiloader.loginApp(self)
		self.data = data

	def login(self, e = None):
		r = requests.post(self.data.api_url+"keylogin", data={"key":self.loginapp.key.get()})
		result = json.loads(r.text)["result"]
		if result == "true":
			self.stop()
			handlerMain = handler(self.data)
			handlerMain.run()

		elif result == "false":
			self.loginapp.messageBox("error","Wrong login","The serial key was wrong!")
		elif result == "expired":
			self.loginapp.messageBox("error","Expired","The serial key has expired!")
		else:
			self.loginapp.messageBox("error","Error","The programs had an error!")		

	def run(self):
		self.loginapp.ct.run()

	def stop(self):
		self.loginapp.ct.stop()

#Main gui handler
class handler:
	def __init__(self, data):
		self.data = data
		self.mainapp = guiloader.mainApp(data, self)
		self.checkUpdate()

	def getValue(self, input):
		return self.mainapp.inputs[input].get()
		
	def start(self, data):
		#Check for emptys
		if data[0]=="":
			return self.mainapp.messageBox("error","Input error","Please don't leave the query empty.")
		else:
			self.scraper = scraper(data[0],data[1], data[2], data[3], self)
			self.scraper.start()
			self.mainapp.navbuttons[0].config(relief=SUNKEN)

	def stop(self):
		if(self.scraper.is_alive()):
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

	def checkUpdate(self):
		r = requests.post(self.data.api_url+"checkupdate", data={"v":self.data.app_version,"a":self.data.app_name})
		answer = json.loads(r.text)
		if answer["result"]=="false":
			return False
		else:
			if self.mainapp.messageBox("askyesorno","Update","An update was found! Do you want to update?"):
				self.mainapp.ct.stop()
				url = answer["update"]
				r = requests.get(url, headers={"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"})				
				open('update.exe', 'wb').write(r.content)
				subprocess.Popen("update.exe -y -o.", shell=True)
				os._exit(0)
			else:
				return True

	def clear(self):
		self.mainapp.datatable.delete(*self.mainapp.datatable.get_children())

	def insert(self, data):
		self.mainapp.datatable.insert("",'end',values=tuple(data))

	def run(self):
		self.mainapp.run()

class scraper(threading.Thread):
	def __init__(self, query, location, maxpage, emailscrp,  handler):
		threading.Thread.__init__(self)
		self.query = query
		self.location = location
		self.handler = handler
		self.maxpage = maxpage
		self.emailscrp = emailscrp
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
		decode = self.getNumbers(str(s.find_all("style")[1]))
		contact = s.find("div",{"class":"paddingR0"})
		category = ', '.join([i['title'] for i in contact.find_all("a",{"class":"lng_also_lst1"})])
		company = s.find("span",{"class":"fn"}).text
		address = contact.find("span",{"class":"lng_add"}).text
		
		numbers = []
		for c in contact.find_all("a",{"class":"tel"}):
			numbers.append(''.join([decode[a['class'][1].split("-")[1]] for a in c.find_all("span",{"class":"mobilesv"})]))
		numbers = ', '.join(numbers)
		try:
			location = self.geolocator.geocode(address.split("-")[0])
			latitude = location.latitude
			longitude = location.longitude
		except:
			latitude, longitude = "",""

		votes = s.find("span",{"class":"votes"}).text
		try:
			rating = s.find("span",{"class":"value-titles"}).text
		except:
			rating = "0"

		verified = s.find("span",{"class":"jd_verified"})!=None
		trusted = s.find("span",{"class":"jd_trusted"})!=None

		try:
			website = contact.find("i",{"class":"web_ic"}).find_next_sibling().findChild()['href']
		except:
			website = ""

		if self.emailscrp:
			try:
				r = requests.get(website, verify=False, headers=self.headers)
				email = re.search(self.EMAIL_REGEX, r.text).group()
			except:
				email = ""
		else:
			email = ""

		return [category, company, address, email, numbers, latitude, longitude, rating, votes, verified, trusted, website]

	def run(self):
		page = 1
		while self._running and page <= int(self.maxpage):
			for link in self.getUrls(page):
				if(self._running):
					try:
						self.handler.insert(self.getData(link))
					except Exception as e:
						print("[ERROR] Error with url: "+str(e))
						pass
			page += 1
		if(self._running):
			self.handler.stop()
			self.handler.mainapp.messageBox("info","Success","Scraper has finished!")
	def stop(self):
		self._running = False

if __name__ == '__main__':
	data = app_data.justdial()
	loginHandler = loginHandler(data)
	loginHandler.run()