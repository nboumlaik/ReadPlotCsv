# -*- coding: cp1252 -*-
from Tkinter import *
import tkFileDialog
import pandas as pd
import pdb
from matplotlib import pyplot as plt
import re
import getpass
import Tix

user = getpass.getuser()

def ReadCsv():
    global chemin
    global nom
    
    try:
        fpath = tkFileDialog.askopenfilename (initialdir = chemin)
    except:
        fpath = tkFileDialog.askopenfilename (initialdir='C:/Users/%s' % user)
        
    chemin = fpath [:fpath.rfind ("/")]
    nom = fpath [fpath.rfind ("/"):]
    nom = Ftext ( nom)
##    if '_' in nom:
##        car1 = nom[0]
##        nom = Ftext (nom, car1 = car1, car2='_')
##        nom = car1 + nom

    #pdb.set_trace()
    df = pd.read_csv (fpath)
    
    return df

#affiche la listbox dans une nouvelles fenetre
def dolistbox (Df):
    #creation d'une nouvelle fenetre
    t=Toplevel ()
    
    #grab_set: makes sure that no mouse or keyboard events are sent to the wrong window
    t.grab_set ()
    
    #affecter la listbox a la nouvelle fenetre
    listbox = Listbox (t)
    
    #EXTENDED: pour selectioner plusierus items
    listbox.config (selectmode = EXTENDED)
    listbox.grid ()

    #afficher les colonnes de df dans la listbox
    for item in Df.columns:
        listbox.insert (END, item)
    
    #bouton pour faire le graphique
    Boutonplot = Button (t, text ='plot', command = lambda : plot (df=Df , label_=getindex (listbox = listbox)))
    Boutonplot.grid ()

    #bouton pour fermer la fenetre cree
    Boutonrest = Button (t, text ='fermer', command = t.destroy)
    Boutonrest.grid ()


#recuperer les noms selectionne sur listbox --> retourn la liste des noms de colonnes ou un str pour un seul nom  
def getindex (listbox):
    #si une seule selection
    try:
        sel = listbox.get (listbox.curselection ())
        
    #si multi selection
    except TclError:
        sel = listbox.curselection()
        sel = [ int(i) for i in sel]
        itms = []
        for i_index in sel:
            itms.insert ( len(itms), listbox.get (i_index))
        sel = itms
    
    return sel

#la fonction pour faire les graphiques    
def plot (df, label_):
    Df = pd.DataFrame (df)

    #transformer index en format date  
    if 'Unnamed: 0' in df.columns:
        try:
            df = pd.DataFrame (df)
            df = df.set_index ('Unnamed: 0')
            df.index = [ re.sub ('-', '', i) for i in df.index ]
            df.index = [ str (i) for i in df.index ]
            df.index = [ pd.datetime.strptime (i, '%Y%m%d') for i in df.index ]
        except ValueError:
            df = Df
    
    #pdb.set_trace()
    ax = plt.subplot ()
    if type (label_ )!= str:
        for l in label_:
            l_ = l+'_'+nom
            ax.plot ( df.index, df [l], label = l_ ) # nom est une variable globale declare dans la fonction ReadCsv ()
    else:
        ax.plot ( df.index, df [label_], label = label_+'_'+nom )
        
    ax.legend (loc = 2)
    ax.grid (True)
    plt.show ()
    
def Ftext (string, car1 = '_' , car2 = '(', n = 1 ):
    
    d = string.find (car1) + n
    f = string [d+1:].find (car2) + d+1
    string = string [d:f]

    return string


import urllib2
import time
import datetime
import numpy as np
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.finance import candlestick
import matplotlib
import pylab
matplotlib.rcParams.update({'font.size': 9})



def rsiFunc(prices, n=14):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1] # cause the diff is 1 shorter

        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return rsi

def movingaverage(values,window):
    weigths = np.repeat(1.0, window)/window
    smas = np.convolve(values, weigths, 'valid')
    return smas # as a numpy array

def ExpMovingAverage(values, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a =  np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a


def computeMACD(x, slow=26, fast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
    return value is emaslow, emafast, macd which are len(x) arrays
    """
    emaslow = ExpMovingAverage(x, slow)
    emafast = ExpMovingAverage(x, fast)
    return emaslow, emafast, emafast - emaslow


def graphData(stock,MA1,MA2):
    '''
        Use this to dynamically pull a stock:
    '''
    try:
        print 'Currently Pulling',stock
        print str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
        #Keep in mind this is close high low open data from Yahoo
        urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=10y/csv'
        stockFile =[]
        try:
            sourceCode = urllib2.urlopen(urlToVisit).read()
            splitSource = sourceCode.split('\n')
            for eachLine in splitSource:
                splitLine = eachLine.split(',')
                if len(splitLine)==6:
                    if 'values' not in eachLine:
                        stockFile.append(eachLine)
        except Exception, e:
            print str(e), 'failed to organize pulled data.'
    except Exception,e:
        print str(e), 'failed to pull pricing data'
    try:   
        date, closep, highp, lowp, openp, volume = np.loadtxt(stockFile,delimiter=',', unpack=True,
                                                              converters={ 0: mdates.strpdate2num('%Y%m%d')})
        x = 0
        y = len(date)
        newAr = []
        while x < y:
            appendLine = date[x],openp[x],closep[x],highp[x],lowp[x],volume[x]
            newAr.append(appendLine)
            x+=1
            
        Av1 = movingaverage(closep, MA1)
        Av2 = movingaverage(closep, MA2)

        SP = len(date[MA2-1:])
            
        fig = plt.figure(facecolor='#07000d')

        ax1 = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4, axisbg='#07000d')
        candlestick(ax1, newAr[-SP:], width=.6, colorup='#53c156', colordown='#ff1717')

        Label1 = str(MA1)+' SMA'
        Label2 = str(MA2)+' SMA'

        ax1.plot(date[-SP:],Av1[-SP:],'#e1edf9',label=Label1, linewidth=1.5)
        ax1.plot(date[-SP:],Av2[-SP:],'#4ee6fd',label=Label2, linewidth=1.5)
        
        ax1.grid(True, color='w')
        ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.yaxis.label.set_color("w")
        ax1.spines['bottom'].set_color("#5998ff")
        ax1.spines['top'].set_color("#5998ff")
        ax1.spines['left'].set_color("#5998ff")
        ax1.spines['right'].set_color("#5998ff")
        ax1.tick_params(axis='y', colors='w')
        plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
        ax1.tick_params(axis='x', colors='w')
        plt.ylabel('Stock price and Volume')

        maLeg = plt.legend(loc=9, ncol=2, prop={'size':7},
                   fancybox=True, borderaxespad=0.)
        maLeg.get_frame().set_alpha(0.4)
        textEd = pylab.gca().get_legend().get_texts()
        pylab.setp(textEd[0:5], color = 'w')

        volumeMin = 0
        
        ax0 = plt.subplot2grid((6,4), (0,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
        rsi = rsiFunc(closep)
        rsiCol = '#c1f9f7'
        posCol = '#386d13'
        negCol = '#8f2020'
        
        ax0.plot(date[-SP:], rsi[-SP:], rsiCol, linewidth=1.5)
        ax0.axhline(70, color=negCol)
        ax0.axhline(30, color=posCol)
        ax0.fill_between(date[-SP:], rsi[-SP:], 70, where=(rsi[-SP:]>=70), facecolor=negCol, edgecolor=negCol, alpha=0.5)
        ax0.fill_between(date[-SP:], rsi[-SP:], 30, where=(rsi[-SP:]<=30), facecolor=posCol, edgecolor=posCol, alpha=0.5)
        ax0.set_yticks([30,70])
        ax0.yaxis.label.set_color("w")
        ax0.spines['bottom'].set_color("#5998ff")
        ax0.spines['top'].set_color("#5998ff")
        ax0.spines['left'].set_color("#5998ff")
        ax0.spines['right'].set_color("#5998ff")
        ax0.tick_params(axis='y', colors='w')
        ax0.tick_params(axis='x', colors='w')
        plt.ylabel('RSI')

        ax1v = ax1.twinx()
        ax1v.fill_between(date[-SP:],volumeMin, volume[-SP:], facecolor='#00ffe8', alpha=.4)
        ax1v.axes.yaxis.set_ticklabels([])
        ax1v.grid(False)
        ax1v.set_ylim(0, 3*volume.max())
        ax1v.spines['bottom'].set_color("#5998ff")
        ax1v.spines['top'].set_color("#5998ff")
        ax1v.spines['left'].set_color("#5998ff")
        ax1v.spines['right'].set_color("#5998ff")
        ax1v.tick_params(axis='x', colors='w')
        ax1v.tick_params(axis='y', colors='w')

        
        ax2 = plt.subplot2grid((6,4), (5,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')

        

        # START NEW INDICATOR CODE #

        

        # END NEW INDICATOR CODE #

        

        
        plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
        ax2.spines['bottom'].set_color("#5998ff")
        ax2.spines['top'].set_color("#5998ff")
        ax2.spines['left'].set_color("#5998ff")
        ax2.spines['right'].set_color("#5998ff")
        ax2.tick_params(axis='x', colors='w')
        ax2.tick_params(axis='y', colors='w')
        ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='upper'))




        
        for label in ax2.xaxis.get_ticklabels():
            label.set_rotation(45)

        plt.suptitle(stock.upper(),color='w')

        plt.setp(ax0.get_xticklabels(), visible=False)
        plt.setp(ax1.get_xticklabels(), visible=False)
        
        '''ax1.annotate('Big news!',(date[510],Av1[510]),
            xytext=(0.8, 0.9), textcoords='axes fraction',
            arrowprops=dict(facecolor='white', shrink=0.05),
            fontsize=14, color = 'w',
            horizontalalignment='right', verticalalignment='bottom')'''

        plt.subplots_adjust(left=.09, bottom=.14, right=.94, top=.95, wspace=.20, hspace=0)
        plt.show()
        fig.savefig('example.png',facecolor=fig.get_facecolor())
           
    except Exception,e:
        print 'main loop',str(e)

##while True:
##    stock = raw_input('Stock to plot: ')
##    graphData(stock,10,50)


def table_map ( table ) :
    
    table = table.set_index ('Unnamed: 0')

    nba = table
    nba = nba.drop ('TIME_V!MOIS')
    del nba ['Total']
    nba.fillna(value = 0.0, inplace = True)

    # Normalize data columns
    nba_norm = (nba - nba.mean ()) / (nba.max () - nba.min ())

    # Plot it out
    fig, ax = plt.subplots ()
    heatmap = ax.pcolor (nba_norm, cmap = plt.cm.Blues, alpha = 0.8)

    # Format
    fig = plt.gcf ()
    fig.set_size_inches (2, 2)
    plt.subplots_adjust(left = 0.35, bottom = -0.01, right = 0.65, top=  None,
                    wspace = None, hspace = None)
    # turn off the frame
    ax.set_frame_on (False)

    # put the major ticks at the middle of each cell
    ax.set_yticks (np.arange(nba_norm.shape [0]) + 0.5, minor = False)
    ax.set_xticks (np.arange(nba_norm.shape [1]) + 0.5, minor = False)

    # want a more natural, table-like display
    ax.invert_yaxis ()
    ax.xaxis.tick_top ()

    # Set the labels

    # labels
    labels = nba.columns
    # note I could have used nba_sort.columns but made "labels" instead
    ax.set_xticklabels (labels, minor = False)
    ax.set_yticklabels (nba_norm.index, minor = False)
    fig.suptitle ('VarCount VIX1d', fontsize = 14, fontweight = 'bold')
    #ax.set_title('VarCount VIX1d')
    # rotate the
    plt.xticks (rotation = 35)

    ax.grid (False)

    # Turn off all the ticks
    ax = plt.gca()

    for t in ax.xaxis.get_major_ticks ():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks ():
        t.tick1On = False
        t.tick2On = False



    plt.show()


# Création de la fenêtre principale (main window)
root = Tix.Tk ()
root.title ( "Advestis-conseil" )
# création du notebook : à la manière de Tix:
monnotebook = Tix.NoteBook (root)
monnotebook.add ("page1", label = "Graphiques")
monnotebook.add ("page2", label = "RIC | MAP")

p1 = monnotebook.subwidget_list ["page1"]
p2 = monnotebook.subwidget_list ["page2"]

# création d'un frame à droite
frame_lateral = Frame (root)
frame_lateral.pack (side = RIGHT)

Mafenetre = Frame (p1)
Mafenetre.pack ()

Mafenetre2 = Frame (p2)
Mafenetre2.pack ()

monnotebook.pack (side = LEFT, fill = Tix.BOTH, expand = 1, padx = 5, pady = 5)
##Mafenetre = Tk ()
##Mafenetre.title ('Graphiques')
#Mafenetre.geometry ('300x100+400+400')
 
# Création de bouton importer 
Boutonread = Button ( Mafenetre, text = 'Importer', command = lambda  : dolistbox ( ReadCsv ()) )
Boutonread.grid ()

#bouton quitter
BoutonQuitter = Button (Mafenetre, text = 'Quitter', command = root.destroy)
BoutonQuitter.grid ()

######
Label (Mafenetre2, text = "RIC :").grid (row = 3)
entry = Entry ( Mafenetre2 )
entry.grid (row = 4, column = 0, padx = 20, pady = 0) 

#bouton plot stock
BoutonPlotStock = Button (Mafenetre2, text = 'OK', command = lambda : graphData ( entry.get(),10,50))
BoutonPlotStock.grid (row = 4, column = 1)

# Création de bouton importer and show 
Boutonread = Button ( Mafenetre2, text = 'Importe and show map', command = lambda  : table_map ( ReadCsv ()) )
Boutonread.grid ()


#advestis picture:
can1 = Canvas (frame_lateral, width = 190, height = 190, bg = 'white')
photo = PhotoImage (file = 'advestis.gif')
can1.create_image (100, 100, image = photo)
can1.grid (padx = 10, pady = 5)



Mafenetre.mainloop ()
