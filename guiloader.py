import pygubu
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

class controller:
	def __init__(self, file):
		self.builder = builder = pygubu.Builder()
		builder.add_from_file(file)
	#Just saving some lines with this
	def ld(self, obj):
		return self.builder.get_object(obj)
	def run(self):
		self.ld("root").mainloop()

class loginApp:
	def __init__(self):
		self.ct = controller("gui\login.ui")

		#Funcs
		self.loadVars()
		self.loadConfig()
		self.run()

	def loadVars(self):
		ct = self.ct
		self.root = ct.ld("root")
		self.key = ct.ld("key")
		self.submit = ct.ld("submit")

	def loadConfig(self):
		self.key.bind("<Return>", self.login)
		self.submit.config(command=self.login)

	def run(self):
		self.ct.run()

	def login(self):
		if(self.key.get()=="admin"):
			print("success")
		else:
			messagebox.showerror("Wrong login","The serial key was wrong!")

class mainApp:
	def __init__(self, data, handler):
		#main stuff
		self.ct = controller("gui\main.ui")
		self.data = data
		self.columns = data.columns
		self.handler = handler
		#Loads
		self.loadVars()
		self.loadGrids()
		self.loadConfig()
		self.loadColumns()	

	#Load functions
	def loadVars(self):
		ct = self.ct
		self.root = ct.ld("root")
		self.main = ct.ld("main")
		#Left
		self.left = ct.ld("left")
		self.nav = ct.ld("nav")
		self.separator = ct.ld("separator_1")
		self.inputframe = ct.ld("inputframe")
		self.navbuttons = [ct.ld("startbt"), ct.ld("stopbt"), ct.ld("exportbt"), ct.ld("clearbt")]
		#Dataframe
		self.dataframe = ct.ld("dataframe")
		self.datatable = ct.ld("datatable")
		self.scrollbars = [ct.ld("scrollbar_x"), ct.ld("scrollbar_y")]
		#Inputs
		self.inputs = self.data.loadInputs(self.inputframe)

	def loadConfig(self):
		scrollx = self.scrollbars[0]
		scrolly = self.scrollbars[1]
		datatable = self.datatable

		self.navbuttons[0].config(command=lambda: self.handler.start(self.getInputVals()))
		self.navbuttons[1].config(command=lambda: self.handler.stop())
		self.navbuttons[2].config(command=lambda: self.handler.export())
		self.navbuttons[3].config(command=lambda: self.handler.clear())

		scrollx.config(command = datatable.xview)
		scrolly.config(command = datatable.yview)

		datatable.configure(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

	def loadGrids(self):
		root = self.root
		left = self.left
		nav = self.nav
		datatable = self.datatable
		dataframe = self.dataframe
		main = self.main
		scrollx = self.scrollbars[0]
		scrolly = self.scrollbars[1]
		inputframe = self.inputframe
		navbuttons = self.navbuttons
		separator = self.separator

		root.grid_columnconfigure(0,minsize=1500,weight=1)
		root.grid_rowconfigure(0,minsize=800,weight=1)

		main.grid_rowconfigure(0, minsize=800, weight=1)
		#Left
		main.grid_columnconfigure(0, minsize=400)
		left.grid_rowconfigure(0,weight=1)
			#nav
		left.grid_columnconfigure(0,minsize=80)
		nav.grid_columnconfigure(0, weight=1)
		nav.grid_rowconfigure(2, minsize=20)
			#inputframe
		left.grid_columnconfigure(1,minsize=320)
		inputframe.grid_columnconfigure(0,weight=1)
		#Dataframe
		main.grid_columnconfigure(1,minsize=1100, weight=1)

		#scrollwheels
		dataframe.grid_columnconfigure(0,weight=1)
		dataframe.grid_rowconfigure(0,weight=1)

		#Expands
		main.grid(sticky=W+E+N+S)
		left.grid(sticky=W+E+N+S)
		dataframe.grid(sticky=W+E+N+S)
		scrollx.grid(sticky=W+E+N+S)
		scrolly.grid(sticky=W+E+N+S)
		datatable.grid(sticky=W+E+N+S)
		inputframe.grid(sticky=W+E+N+S)
		nav.grid(sticky=N+S+E+W)
		separator.grid(sticky=E+W)
		for a in navbuttons:
			a.grid(sticky=E+W)

	def loadColumns(self):
		self.datatable['show'] = 'headings'
		self.datatable["columns"] = tuple([str(i) for i in range(1,len(self.columns)+1)])
		for a in range(1,len(self.columns)+1):
			self.datatable.column(str(a), width=100, anchor="c")
			self.datatable.heading(str(a), text=self.columns[a-1])

	#Mics and utils functions
	def getInputVals(self):
		vals = []
		for a in self.inputs:
			vals.append(a.get())
		return vals
	def messageBox(self, type, title, txt):
		if type=="error":
			return messagebox.showerror(title, txt)
		if type=="info":
			return messagebox.showinfo(title, txt)
		if type=="waring":
			return messagebox.showwarning(title, txt)
	#Run
	def run(self):
		self.ct.run()

