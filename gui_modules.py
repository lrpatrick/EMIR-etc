"""
Author: XXX (probably CG)
Date: XXX
Description (LRP): Defines the appearance of the gui (I think)
This file defines the appearance of the starter page. I think this actually has nothing 
to do with the gui
Update:
Author: LRP
Date: 28-11-2016
Description: Include a button for the Y filter


"""
from Tkinter import *
from etc_config import get_config, get_params, get_filter, get_grism, get_skymag, get_models
#
#	This is an envelope for all the gui appaerance configuration
#
def load_gui(parent,self):
	self.myParent = parent  ### (7) remember my parent, the root
	self.myParent.title('EMIR ETC v1.0.4')
	self.myContainer_end = Frame(parent)
	self.myContainer_end.pack()
	#
	#	Source configuration
	#
	self.myContainer1 = Frame(parent)
	self.myContainer1.pack(fill=X)
	self.lbl = Label(self.myContainer1,text="Source configuration",bg="gray")
	self.lbl.pack(fill=X)
	#
	self.myContainer2 = Frame(parent)
	self.myContainer2.pack(fill=X)
	self.lbl2 = Label(self.myContainer2,text='Magnitude:')
	self.lbl2.pack(side=LEFT)
	self.mag=0.0
	self.magbutton = Entry(self.myContainer2,width=6)
	self.magbutton.pack(side=LEFT)
	self.magbutton.insert(0,'0.0')
	self.magbutton.focus_set()
	self.lbl2 = Label(self.myContainer2,text='Vega system')
	self.lbl2.pack(side=LEFT)
	#
	self.myContainer3 = Frame(parent)
	self.myContainer3.pack(fill=X)
	self.source_type=StringVar()
	self.source_type.set('Point')
	self.lbl3 = Label(self.myContainer3,text='Source type:')
	self.lbl3.pack(side=LEFT)
	self.menu_source = OptionMenu(self.myContainer3,self.source_type,"Point",\
		"Extended")
	self.menu_source.pack(side=LEFT)
	#
	#	Model selection
	#
	self.myContainer12 = Frame(parent)
	self.myContainer12.pack(fill=X, pady=5)
	self.lbl = Label(self.myContainer12,text="Spectral template",bg="gray")
	self.lbl.pack(fill=X)
	#
	self.modeltype = StringVar()
	mmodel=Radiobutton(self.myContainer12, text="Model library", variable=self.modeltype,\
		value="model")
	mmodel.pack(side=LEFT, padx=5)
	mbb=Radiobutton(self.myContainer12, text="Black body", variable=self.modeltype,\
		value="bb")
	mbb.pack(side=LEFT, padx=5)
	memlin=Radiobutton(self.myContainer12, text="Emission line", variable=self.modeltype,\
		value="line")
	memlin.pack(side=LEFT, padx=5)
	mline=Radiobutton(self.myContainer12, text="Model file", variable=self.modeltype,\
		value="own")
	mline.pack(side=LEFT, padx=5)
	mbb.select()
	separator = Frame(height=2, bd=1, relief=SUNKEN)
	separator.pack(fill=X, padx=5, pady=5)
	#
	#	Model
	#
	self.myContainer13 = Frame(parent)
	self.myContainer13.pack(fill=X)
	self.available,modelorder=get_models()
	self.lbl3 = Label(self.myContainer13,text='Model:')
	self.lbl3.pack(side=LEFT)
	self.model_lib=StringVar()
	self.model_lib.set(modelorder[34])
	self.menu_source = OptionMenu(self.myContainer13,self.model_lib,*modelorder)
	self.menu_source.pack(side=LEFT)
	separator = Frame(height=2, bd=1, relief=SUNKEN)
	separator.pack(fill=X, padx=5, pady=5)
	#
	#	BBody
	#
	self.myContainer13 = Frame(parent)
	self.myContainer13.pack(fill=X)
	self.lbl3 = Label(self.myContainer13,text='B. Body temperature:')
	self.lbl3.pack(side=LEFT)
	self.bbbutton = Entry(self.myContainer13,width=6)
	self.bbbutton.pack(side=LEFT)
	self.bbbutton.insert(0,'10000')
	self.bbbutton.focus_set()
	self.lbl3 = Label(self.myContainer13,text='K')
	self.lbl3.pack(side=LEFT)
	separator = Frame(height=2, bd=1, relief=SUNKEN)
	separator.pack(fill=X, padx=5, pady=5)
	#
	#	Line
	#
	self.myContainer14 = Frame(parent)
	self.myContainer14.pack(fill=X)
	self.lbl3 = Label(self.myContainer14,text='Line center:')
	self.lbl3.grid(row=0,column=0, sticky=W)
	self.lcenterbutton = Entry(self.myContainer14,width=6)
	self.lcenterbutton.grid(row=0,column=1, sticky=W)
	self.lcenterbutton.insert(0,'1.5')
	self.lcenterbutton.focus_set()
	self.lbl3 = Label(self.myContainer14,text='microns')
	self.lbl3.grid(row=0,column=2, sticky=W)
	self.lbl3 = Label(self.myContainer14,text='Line FWHM:')
	self.lbl3.grid(row=1,column=0, sticky=W)
	self.lwidthbutton = Entry(self.myContainer14,width=6)
	self.lwidthbutton.grid(row=1,column=1, sticky=W)
	self.lwidthbutton.insert(0,'1.5')
	self.lwidthbutton.focus_set()
	self.lbl3 = Label(self.myContainer14,text='Angstroms')
	self.lbl3.grid(row=1,column=2, sticky=W)
	self.lbl3 = Label(self.myContainer14,text='Line peak flux:')
	self.lbl3.grid(row=2,column=0, sticky=W)
	self.lfluxbutton = Entry(self.myContainer14,width=6)
	self.lfluxbutton.grid(row=2,column=1, sticky=W)
	self.lfluxbutton.insert(0,'1.0')
	self.lfluxbutton.focus_set()
	self.lbl3 = Label(self.myContainer14,text='x10E-16 erg/s/cm2')
	self.lbl3.grid(row=2,column=2, sticky=W)
	separator = Frame(height=2, bd=1, relief=SUNKEN)
	separator.pack(fill=X, padx=5, pady=5)
	#
	#	Own model
	#
	def load_file():
		import tkFileDialog
		from etc_modules import getdata
		self.fname = tkFileDialog.askopenfilename()
		try:
			test=getdata(self.fname)
		except:
			top = Toplevel()
			top.title("Load file")
			testfile=Text(top)
			testfile.insert(INSERT, "ERROR\n",)
			testfile.insert(INSERT, self.fname+" not found\n",)
			testfile.config(state=DISABLED)
			testfile.pack()
		if test['unit_y'] == 'W/m2/nm':
 			unity='ok'
 		elif test['unit_y'] == 'W/m2/micron':
 			unity='ok'
 		elif test['unit_y'] == 'photon/s/m2/micron/arcsec2':
 			unity='ok'
 		elif test['unit_y'] == 'photon/s/m2/nm/arcsec2':
 			unity='ok'
 		elif test['unit_y'] == 'normal_flux':
 			unity='ok'
 		elif test['unit_y'] == 'normal_photon':
 			unity='ok'
 		else:
 			unity='error'
 		if test['unit_x'] == 'nm':
 			unitx='ok'
 		elif test['unit_x'] == 'micron':
 			unitx='ok'
 		elif test['unit_x'] == 'ang':
 			unitx='ok'
 		else:
 			unitx='error'
 		#
 		top = Toplevel()
		top.title("Load file")
 		if (unitx == 'ok') & (unity == 'ok'):
			testfile=Text(top)
			testfile.insert(INSERT, self.fname+" successfully loaded\n")
			testfile.config(state=DISABLED)
			testfile.pack()
		else:
			testfile=Text(top)
			testfile.insert(INSERT, self.fname+" successfully loaded\n")
			testfile.insert(INSERT, "There has been an ERROR on the units\n")
			if unitx != 'ok':
				testfile.insert(INSERT, "Wavelength units are "+test['unit_x']+"\n")
				testfile.insert(INSERT, "While allowed units are ang, nm or micron.\n")
			if unity != 'ok':
				testfile.insert(INSERT, "Flux units are "+test['unit_y']+"\n")
				testfile.insert(INSERT, "While allowed units are W/m2/nm, W/m2/micron, ")
				testfile.insert(INSERT, "photon/s/m2/micron/arcsec2, normal_flux or normal_photon.\n")
			testfile.config(state=DISABLED)
			testfile.pack()
	#
	self.myContainer14 = Frame(parent)
	self.myContainer14.pack(fill=X)
	self.lbl4 = Label(self.myContainer14,text="Model file:")
	self.lbl4.pack(side=LEFT)
	self.buttonown = Button(self.myContainer14, text="Choose file", command=load_file, width=10)
	self.buttonown.pack(side=LEFT)
	#
	#	Observation
	#
	self.myContainer4 = Frame(parent)
	self.myContainer4.pack(fill=X, pady=5)
	self.lbl4 = Label(self.myContainer4,text="Observation configuration",bg="gray")
	self.lbl4.pack(fill=X)
	#
	self.myContainer5 = Frame(parent)
	self.myContainer5.pack(fill=X)
	self.lbl5 = Label(self.myContainer5,text='Airmass:')
	self.lbl5.pack(side=LEFT)
	self.airmass=1.5
	self.airbutton = Entry(self.myContainer5,width=6)
	self.airbutton.pack(side=LEFT)
	self.airbutton.insert(0,'1.5')
	self.airbutton.focus_set()
	#
	self.myContainer8 = Frame(parent)
	self.myContainer8.pack(fill=X)
	self.lbl8 = Label(self.myContainer8,text='Seeing:')
	self.lbl8.pack(side=LEFT)
	self.seeing=0.8
	self.seeingbutton = Entry(self.myContainer8,width=6)
	self.seeingbutton.pack(side=LEFT)
	self.seeingbutton.insert(0,'0.8')
	self.seeingbutton.focus_set()
	self.lbl8 = Label(self.myContainer8,text='arcsec')
	self.lbl8.pack(side=LEFT)
	#
	#	Photometry
	#
	self.myContainer7 = Frame(parent)
	self.myContainer7.pack(fill=X, pady=5)
	self.lbl9 = Label(self.myContainer7,text="Photometry",bg="gray")
	self.lbl9.pack(fill=X)
	#
	self.myContainer11 = Frame(parent)
	self.myContainer11.pack(fill=X)
	self.lbl8 = Label(self.myContainer11,text='Exp. time:')
	self.lbl8.pack(side=LEFT)
	self.exptimeph='1'
	self.expbuttonph = Entry(self.myContainer11,width=9)
	self.expbuttonph.pack(side=LEFT)
	self.expbuttonph.insert(0,'1-10')
	self.expbuttonph.focus_set()
	self.lbl8 = Label(self.myContainer11,text='seconds')
	self.lbl8.pack(side=LEFT)
	#
	self.myContainer25 = Frame(parent)
	self.myContainer25.pack(fill=X)
	self.lbl8 = Label(self.myContainer25,text='Number of frames:')
	self.lbl8.pack(side=LEFT)
	self.lbl8 = Label(self.myContainer25,text='Object')
	self.lbl8.pack(side=LEFT)
	self.nobjph = Entry(self.myContainer25,width=5)
	self.nobjph.pack(side=LEFT)
	self.nobjph.insert(0,'1')
	self.nobjph.focus_set()
	self.nobj='1'
	self.lbl8 = Label(self.myContainer25,text='Sky')
	self.lbl8.pack(side=LEFT)
	self.nskyph = Entry(self.myContainer25,width=5)
	self.nskyph.pack(side=LEFT)
	self.nskyph.insert(0,'1')
	self.nskyph.focus_set()
	self.nsky='1'
	#
	self.myContainer10 = Frame(parent)
	self.myContainer10.pack(fill=X)
	self.lbl10 = Label(self.myContainer10,text='Filter:')
	self.lbl10.pack(side=LEFT)
	self.filtbutton = StringVar()
	ry=Radiobutton(self.myContainer10, text="Y", variable=self.filtbutton, value="Y")  # Added LRP 28-11-2016
	ry.pack(side=LEFT, padx=5)  # Added LRP 28-11-2016
	rj=Radiobutton(self.myContainer10, text="J", variable=self.filtbutton, value="J")
	rj.pack(side=LEFT, padx=5)
	rh=Radiobutton(self.myContainer10, text="H", variable=self.filtbutton, value="H")
	rh.pack(side=LEFT, padx=5)
	rk=Radiobutton(self.myContainer10, text="Ks", variable=self.filtbutton, value="Ks")
	rk.pack(side=LEFT, padx=5)
	rb=Radiobutton(self.myContainer10, text="BrG", variable=self.filtbutton, value="BrG")
	rb.pack(side=LEFT, padx=5)
	rf=Radiobutton(self.myContainer10, text="FeII", variable=self.filtbutton, value="FeII")
	rf.pack(side=LEFT, padx=5)
	rfm=Radiobutton(self.myContainer10, text="F123M", variable=self.filtbutton, value="F123M") # Added LRP 05-12-2016
	rfm.pack(side=LEFT, padx=5) # Added LRP 05-12-2016
	rk.select()
	#
	self.myContainer9 = Frame(parent)
	self.myContainer9.pack(fill=X)
	self.button1 = Button(self.myContainer9)
	self.button1.configure(text="Calculate")
	self.button1.pack(side=TOP)
	self.button1.bind("<Button-1>", self.button1Click) ### (1)
	#
	#	Spectroscpy
	#
	#
	self.myContainer20 = Frame(parent)
	self.myContainer20.pack(fill=X, pady=5)
	self.lbl9 = Label(self.myContainer20,text="Spectroscopy",bg="gray")
	self.lbl9.pack(fill=X)
	#
	self.myContainer22 = Frame(parent)
	self.myContainer22.pack(fill=X)
	self.lbl10 = Label(self.myContainer22,text='Grism:')
	self.lbl10.pack(side=LEFT)
	self.grismbutton = StringVar()
	rj=Radiobutton(self.myContainer22, text="J", variable=self.grismbutton, value="J")
	rj.pack(side=LEFT)
	rh=Radiobutton(self.myContainer22, text="H", variable=self.grismbutton, value="H")
	rh.pack(side=LEFT)
	rk=Radiobutton(self.myContainer22, text="K", variable=self.grismbutton, value="K")
	rk.pack(side=LEFT)
	rk.select()
	ryj=Radiobutton(self.myContainer22, text="YJ", variable=self.grismbutton, value="YJ")
	ryj.pack(side=LEFT)
	rhk=Radiobutton(self.myContainer22, text="HK", variable=self.grismbutton, value="HK")
	rhk.pack(side=LEFT)
	rhk.select()
	#
	self.myContainer23 = Frame(parent)
	self.myContainer23.pack(fill=X)
	self.lbl5 = Label(self.myContainer23,text='Slit width:')
	self.lbl5.pack(side=LEFT)
	self.slitwidth=0.8
	self.slwdbutton = Entry(self.myContainer23,width=6)
	self.slwdbutton.pack(side=LEFT)
	self.slwdbutton.insert(0,'0.8')
	self.slwdbutton.focus_set()
	self.lbl5 = Label(self.myContainer23,text='arcsec')
	self.lbl5.pack(side=LEFT)
	#
	self.myContainer24 = Frame(parent)
	self.myContainer24.pack(fill=X)
	self.lbl8 = Label(self.myContainer24,text='Exp. time:')
	self.lbl8.pack(side=LEFT)
	self.exptime_sp='100'
	self.expbuttonsp = Entry(self.myContainer24,width=9)
	self.expbuttonsp.pack(side=LEFT)
	self.expbuttonsp.insert(0,'100')
	self.expbuttonsp.focus_set()
	self.lbl8 = Label(self.myContainer24,text='seconds')
	self.lbl8.pack(side=LEFT)
	#
	self.myContainer26 = Frame(parent)
	self.myContainer26.pack(fill=X)
	self.lbl8 = Label(self.myContainer26,text='Number of frames:')
	self.lbl8.pack(side=LEFT)
	self.lbl8 = Label(self.myContainer26,text='Object')
	self.lbl8.pack(side=LEFT)
	self.nobjsp = Entry(self.myContainer26,width=5)
	self.nobjsp.pack(side=LEFT)
	self.nobjsp.insert(0,'1')
	self.nobjsp.focus_set()
	self.nobj='1'
	self.lbl8 = Label(self.myContainer26,text='Sky')
	self.lbl8.pack(side=LEFT)
	self.nskysp = Entry(self.myContainer26,width=5)
	self.nskysp.pack(side=LEFT)
	self.nskysp.insert(0,'1')
	self.nskysp.focus_set()
	self.nsky='1'
	#
	self.myContainer21 = Frame(parent)
	self.myContainer21.pack(fill=X)
	self.button2 = Button(self.myContainer21)
	self.button2.configure(text="Calculate")
	self.button2.pack(side=TOP)
	self.button2.bind("<Button-1>", self.button2Click) ### (1)
	#
