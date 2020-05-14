import tkinter as tk
from tkinter import W,E,S,N

#Input and Columns template
class justdial:
	def __init__(self):
		self.app_version = "0.2"
		self.app_name = "just-dial"
		self.api_url = "https://datascraper-database.herokuapp.com/api/"
		self.columns = ["Category","Company","Address","Email","Numbers","Latitude","Longitude","Rating","Reviews","Verified","Trusted","Website"]
	def loadInputs(self, frame):

		tk.Label(frame, text="Query").grid(row=0, column=0)
		query = tk.Entry(frame)
		query.grid(row=1, column=0, ipadx=70)

		tk.Label(frame, text="City (Default Mumbai)").grid(row=2, column=0)
		location = tk.Entry(frame)
		location.grid(row=3, column=0, ipadx=70)

		tk.Label(frame, text="Max page").grid(row=4, column=0)
		maxpage = tk.Spinbox(frame, from_=1, to=100)
		maxpage.grid(row=5, column=0, ipadx=70)

		emailscrp = tk.BooleanVar() 
		emailcheck = tk.Checkbutton(frame, text="Email scraping (Beta)", var=emailscrp)
		emailcheck.grid(row=6, column=0, ipadx=70)

		return [query,location,maxpage,emailscrp]