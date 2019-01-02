
import tkinter as tk
import tkinter.font as tkFont
from math import log10, pi, sqrt
from cmath import phase
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg





def drange(start, stop, step):#Generateur pour des doubles
	x = start
	while x <= stop:
		yield x
		x += step

class MyCursor:
	def __init__(self, widgetParent, scaleVariable, description, **kwargs):

		#------Création du frame qui contiendra tous les widgets_________#
		self.frame = tk.Frame(widgetParent)
		self.conteneurText = tk.Frame(self.frame)
		self.conteneurScale = tk.Frame(self.frame)
		self.conteneurText.pack(side=tk.TOP)
		self.conteneurScale.pack(side=tk.TOP)

		#-----------Ajout du label et du champ de saisi-----------------#
		self.text = tk.Label(self.conteneurText, text=description)
		self.saisi = tk.Label(self.conteneurText, textvariable=scaleVariable)
		self.text.pack(side=tk.LEFT, anchor=tk.W)
		self.saisi.pack(side=tk.LEFT, anchor=tk.W)

		#___________Ajout du Scale--------------------------------------#
		self.scale = tk.Scale(self.conteneurScale, length=250, **kwargs)
		self.scale.pack(side=tk.TOP)




class Monappli:

	def __init__(self, parent):
		self.parent = parent
		self.parent.title('Bode Théorique')
		self.parent.geometry("1280x800")


		self.frameApp = tk.Frame(self.parent)
		self.frameApp.pack(side= tk.TOP, fill='both', expand=1)

		#-----------------Définition des variables-------------------------------#
		self.f = [int(10**i) for i in drange(2, 5, 0.01)]
		self.filtreVar = tk.StringVar(value="Passe bas")
		self.frequence = tk.IntVar(value=3100)
		self.facteurQ = tk.DoubleVar(value=2.0)

		self.getGraphValues = self.getGraphValuesPB


		#-----------------Définition du "menu" de gauche------------------------#
		self.frame = tk.Frame(self.frameApp)
		self.frame.pack(side=tk.LEFT, fill='x', expand=tk.YES)

		#-----------------Choix du type de filtre-------------------------------#
		self.filtreFrame = tk.Frame(self.frame)
		self.filtreFrame.pack(side=tk.TOP)
		self.figTF = Figure(figsize=(2,1), dpi=112)
		self.filtres = ["Passe bas", "Passe bande", "Passe haut"]

		
		for filtre in self.filtres:
			self.radioBoutonFiltre = tk.Radiobutton(self.filtreFrame, variable=self.filtreVar,
			 text=filtre, value=filtre)
			self.radioBoutonFiltre.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

		self.figTF.text(0.1, 0.5, r'$H = \dfrac{1}{1-\left(\dfrac{f}{f_0}\right)^2+\dfrac{j}{Q}\dfrac{f}{f_0}}$')
		self.formuleTF = FigureCanvasTkAgg(self.figTF, master=self.frame)
		self.formuleTF.draw()
		self.formuleTF.get_tk_widget().pack(side=tk.TOP)


		#-----------------Choix de omega0 et Q----------------------------------#
		self.scaleFrame = tk.Frame(self.frame)
		self.scaleFrame.pack(side=tk.TOP, fill=tk.X)

		
		self.scaleFrequence = MyCursor(self.scaleFrame, self.frequence, u'Valeur de la fréquence f\u2080 =',
			orient='horizontal', from_=2, to=5, command=self.setValueFrequence, resolution=0.1, showvalue=0)
		self.scaleFrequence.scale.set(log10(3100))
		self.scaleFrequence.frame.pack(side=tk.TOP)

		
		self.scaleFacteurQ = MyCursor(self.scaleFrame, self.facteurQ, 'Valeur du facteur de qualité Q =',
			orient='horizontal', from_=0.3, to=10, resolution=0.1, variable=self.facteurQ, showvalue=0)
		self.scaleFacteurQ.frame.pack(side=tk.TOP)


		#------------Création du graphique et affichage du canvas(à droite)------------#
		
		self.fig = Figure(figsize=(8, 7), dpi=112)
		self.axGain = self.fig.add_subplot(211, ylim=(-60, 20), autoscale_on =0)
		self.axArgument = self.fig.add_subplot(212, sharex=self.axGain, ylim=(-pi, pi))
		self.axGain.set_xlim(100, 100000)
		self.axGain.set_xscale('log')
		self.axGain.grid(which='major', axis='both')
		self.axGain.grid(which='minor', axis='x', linestyle='--', linewidth=0.5)
		self.axArgument.grid(which='major', axis='both')
		self.axArgument.grid(which='minor', axis='x', linestyle='--', linewidth=0.5)
		self.axArgument.set_xlabel('Fréquence (Hz)')
		self.axGain.set_ylabel('Gain (dB)')
		self.axArgument.set_ylabel('Phase (rad)')
		self.axArgument.set_yticks([-pi, -3*pi/4, -pi/2, -pi/4, 0, pi/4, pi/2, 3*pi/4, pi])
		self.axArgument.set_yticklabels([r'-$\pi$', r'$-\dfrac{3\pi}{4}$', r'$-\dfrac{\pi}{2}$', 
			r'$-\dfrac{\pi}{4}$', 0, r'$\dfrac{\pi}{4}$', r'$\dfrac{\pi}{2}$', r'$\dfrac{3\pi}{4}$', r'$\pi$'])

		self.lineGain, = self.axGain.plot([], [], color='red')
		self.lineGainAsymp, = self.axGain.plot([], [], color='green')
		self.lineArgument, = self.axArgument.plot([], [], color='red')
		self.lineArgumentAsymp, = self.axArgument.plot([], [], color='green')

		self.graph = FigureCanvasTkAgg(self.fig, master=self.frameApp)
		self.canvas = self.graph.get_tk_widget()
		self.canvas.pack(side=tk.RIGHT)

		self.fig.tight_layout()

		self.refreshParametre() # Fonction appelé pour mettre à jour Q et f0

		#Mise en place des observer
		self.filtreVar.trace('w', self.typeFiltre)
		self.frequence.trace('w', self.frequenceObserver)
		self.facteurQ.trace('w', self.facteurQObserver)




	#------------------Calculs pour le diagramme de Bode-----------------------------#

	def calculGainPB(self, f):
		return 20*log10(1/sqrt((1-(f/self.frequence.get())**2)**2+(f/(self.facteurQ.get()*self.frequence.get()))**2))

	def calculGainAsympPB(self, f):
		f0 = self.frequence.get()
		if(f <= f0): return 0
		else : return 40*log10(f0/f)

	def calculPhasePB(self, f):
		return -phase(complex(1-(f/self.frequence.get())**2, f/(self.facteurQ.get()*self.frequence.get())))

	def calculPhaseAsympPB(self, f):
		f0 = self.frequence.get()
		if(f < f0): return 0
		elif(f == f0): return -pi/2
		else : return -pi

	def calculGainPH(self, f):
		return 20*log10(1/sqrt((1-(self.frequence.get()/f)**2)**2+(self.frequence.get()/(self.facteurQ.get()*f))**2))

	def calculGainAsympPH(self, f):
		f0 = self.frequence.get()
		if(f >= f0): return 0
		else : return 40*log10(f/f0)

	def calculPhasePH(self, f):
		return -phase(complex(1-(self.frequence.get()/f)**2, -self.frequence.get()/(self.facteurQ.get()*f)))

	def calculPhaseAsympPH(self, f):
		f0 = self.frequence.get()
		if(f > f0): return 0
		elif(f == f0): return pi/2
		else : return pi

	def calculGainPBande(self, f):
		f0 = self.frequence.get()
		return 20*log10(1/sqrt(1+(self.facteurQ.get()*(f/f0-f0/f))**2))

	def calculGainAsympPBande(self, f):
		f0 = self.frequence.get()
		Q = self.facteurQ.get()
		if(f >= f0): return 20*log10(f0/(f*Q))
		else : return 20*log10(f/(f0*Q))

	def calculPhasePBande(self, f):
		f0 = self.frequence.get()
		return -phase(complex(1, self.facteurQ.get()*(f/f0-f0/f)))

	def calculPhaseAsympPBande(self, f):
		f0 = self.frequence.get()
		if(f > f0): return -pi/2
		elif(f == f0): return 0
		else : return pi/2


	#------------------Fonction annexes------------------------------------------#

	def typeFiltre(self, *args):#Fonction appelé lorsque filtreVar est modifiée
		if (self.filtreVar.get() == 'Passe bas'):
			self.getGraphValues = self.getGraphValuesPB
			self.refreshParametre()
			self.figTF.clear()
			self.figTF.text(0.1, 0.5, r'$H = \dfrac{1}{1-\left(\dfrac{f}{f_0}\right)^2+\dfrac{j}{Q}\dfrac{f}{f_0}}$')
			self.formuleTF.draw()

		if (self.filtreVar.get() == 'Passe haut'):
			self.getGraphValues = self.getGraphValuesPH
			self.refreshParametre()
			self.figTF.clear()
			self.figTF.text(0.1, 0.5, r'$H = \dfrac{1}{1-\left(\dfrac{f_0}{f}\right)^2-\dfrac{j}{Q}\dfrac{f_0}{f}}$')
			self.formuleTF.draw()

		if (self.filtreVar.get() == 'Passe bande'):
			self.getGraphValues = self.getGraphValuesPBande
			self.refreshParametre()
			self.figTF.clear()
			self.figTF.text(0.1, 0.5, r'$H = \dfrac{1}{1+jQ\left(\dfrac{f}{f_0}-\dfrac{f_0}{f}\right)}$')
			self.formuleTF.draw()



	def setValueFrequence(self, puissance):#Fonction servant à faire un scroll logarithmique
		self.frequence.set(int(10.0**float(puissance)))

	def frequenceObserver(self, *args):#Fonction appelé lorsque la variable frequence (f0) est modifiée
		#self.scaleFrequence.scale.set(log10(self.frequence.get())) Obsolète avec la nouvelle version
		self.refreshParametre()

	def facteurQObserver(self, *args):#Fonction appelé lorsque la variable facteurQ est modifiée
		self.refreshParametre()



	#Fonction appelées pour le calcul du gain et de la phase.
	def getGraphValuesPB(self):
		gain = [self.calculGainPB(f) for f in self.f]
		gainAsymp = [self.calculGainAsympPB(f) for f in self.f]
		phas = [self.calculPhasePB(f) for f in self.f]
		phasAsymp = [self.calculPhaseAsympPB(f) for f in self.f]
		return (gain, gainAsymp, phas, phasAsymp)

	def getGraphValuesPH(self):
		gain = [self.calculGainPH(f) for f in self.f]
		gainAsymp = [self.calculGainAsympPH(f) for f in self.f]
		phas = [self.calculPhasePH(f) for f in self.f]
		phasAsymp = [self.calculPhaseAsympPH(f) for f in self.f]
		return (gain, gainAsymp, phas, phasAsymp)

	def getGraphValuesPBande(self):
		gain = [self.calculGainPBande(f) for f in self.f]
		gainAsymp = [self.calculGainAsympPBande(f) for f in self.f]
		phas = [self.calculPhasePBande(f) for f in self.f]
		phasAsymp = [self.calculPhaseAsympPBande(f) for f in self.f]
		return (gain, gainAsymp, phas, phasAsymp)


	def refreshParametre(self):#fonction alias permettant de recalculer les valeurs dans le graphique
		self.gain, self.gainAsymp, self.phase, self.phaseAsymp = self.getGraphValues()
		self.refreshGraphique()



	def refreshGraphique(self, *args):#Fonction appelé pour mettre à jour l'affichage dans le graphique
		self.lineGain.set_data(self.f, self.gain)
		self.lineGainAsymp.set_data(self.f, self.gainAsymp)
		self.lineArgument.set_data(self.f, self.phase)
		self.lineArgumentAsymp.set_data(self.f, self.phaseAsymp)
		self.graph.draw()				
			





root = tk.Tk()
fontApp = tkFont.Font(family='Helvetica', size='13')
root.option_add('*font', fontApp)
root.option_add('*background', 'white')
appli = Monappli(root)
root.mainloop()
