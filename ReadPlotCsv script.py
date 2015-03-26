#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
import Tkinter
import tkFileDialog
import pandas as pd
from matplotlib import pyplot as plt
import getpass
import collections
import matplotlib.patches as mpatches
import numpy as np
import FileDialog
from scipy.special import _ufuncs_cxx
from scipy.sparse.csgraph import _validation
from scipy import stats
import tkMessageBox


class guiplot_tk (Tkinter.Tk):
    
    def __init__ (self, parent):
        Tkinter.Tk.__init__ (self, parent)
        self.parent = parent
        self.chemin_ = None
        self.user = getpass.getuser ()
        try:
            pp = r'D:\Dropbox\temp\Nouveau dossier\exe\advestis.gif'
            photo = Tkinter.PhotoImage (file = pp )
        except:
            photo = Tkinter.PhotoImage (file = 'advestis.gif')
            
        self.photo = photo
        self.colors = ['b','g','r','c','m','olive','orange','dodgerblue']
        self.do_indicateurs = Tkinter.IntVar ()
        self.do_stats = Tkinter.IntVar ()
        self.new_graph = Tkinter.IntVar ()
        self.In_sample = Tkinter.IntVar ()
        self.listbox = None
        self.Dic = None
        self.In_sample.set (1)
        
        self.init_params ()
        self.initialize ()
        
    def init_params (self):
        #plt.close ('all')
        self.figure = plt.figure()
        self.do_fill_between = True
        self.df_ploted = None
        self.max_insample = None
        self.i_color = 0
        self.i_text = 0.01
        self.i_text_u = 0.97
        
    def initialize (self):
        # Création le bouton importer 
        Boutonread = Tkinter.Button ( self, text = 'Importer', command = lambda  : self.dolistbox () )
        Boutonread.grid ()
        
        #bouton quitter
        BoutonQuitter = Tkinter.Button (self, text = 'Quitter', command = self.destroy)
        BoutonQuitter.grid ()
        
        #advestis picture:
        can1 = Tkinter.Canvas (self, width = 190, height = 190, bg = 'white')
        can1.create_image (100,100, image = self.photo)
        can1.grid (row = 0, column = 2, rowspan = 10, padx = 10, pady = 5)
        
    def Ftext (self, string, car1 = '_' , car2 = '(', n = 1 ):
        
        i_debut = string.find (car1) + n
        i_fin = string [i_debut+1:].find (car2) + i_debut +1
        string = string [i_debut:i_fin]
        
        return string
        
    def ReadCsv (self):
        '''importe un/des csv, et renvoi un dic'''

        if self.chemin_ is None:
            fpath = tkFileDialog.askopenfilenames (defaultextension = ".csv", initialfile='*.csv', initialdir='C:/Users/%s' % self.user)
        else:
            fpath = tkFileDialog.askopenfilenames (defaultextension = ".csv", initialfile='*.csv', initialdir = self.chemin_)
            
        chemin = fpath [:fpath.rfind ("/")]
        
        if chemin == '':
            if self.chemin_ is None:
                self.chemin_ = 'C:/Users/%s' % self.user
        else:
            self.chemin_ = chemin
            
        try:
            #construire la liste de(s) chemin(s)
            fpath = self.splitlist (fpath)
            dic = {}
            if len (fpath) == 1:
                fpath = fpath[0]
                nom_ = fpath [fpath.rfind ("/"):]
                if len (nom_)> 30:
                    nom = self.Ftext (nom_)

                else:
                    nom = nom [1:-4]
                    
                if nom == "":
                    nom = nom_ [1:-4]
                df = pd.read_csv (fpath, index_col = 0, sep =",")
                if len (df.columns) == 0:
                    df = pd.read_csv (fpath, index_col = 0, sep =";")
                df.index = pd.DatetimeIndex (df.index)
                dic [nom] = df
            
            elif len (fpath) > 1:
                #on stock les df dans dic
                for p in fpath:
                    nom_ = p [p.rfind ("/"):]
                    if len (nom_)> 30:
                        nom = self.Ftext (nom_)

                    else:
                        nom = nom [1:-4]
                        
                    if nom == "":
                        nom = nom_ [1:-4]
                        
                    df = pd.read_csv (p, index_col = 0)
                    df.index = pd.DatetimeIndex (df.index)
                    dic [nom] = df

            return dic
            
        except IOError:
            if fpath == '':
                return None
            else:
                print "le chemin n'existe pas"

    #affiche la listbox dans une nouvelle fenetre
    def dolistbox (self):
        '''Creation de la liste et de la fenetre des columns de(s) DF importe. Affiche le boutton "plot" afin de faire les graphiques'''
        #on importe le(s) csv dans un dictionnaire
        Dic = self.ReadCsv ()
        
        #on traite le dictionnaire
        if Dic == {}:
            return
        
        elif Dic is not None:
            #test des colonnes vides (messageBox)
            self.controle_nan (Dic)
            
            columns = ()
            #creation d'une nouvelle fenetre
            tk_listbox = Tkinter.Toplevel ()
            tk_listbox.title ('Les colonnes')
            scrollbar = Tkinter.Scrollbar (tk_listbox, orient="vertical")
            
            #grab_set: makes sure that no mouse or keyboard events are sent to the wrong window
            tk_listbox.grab_set ()
            
            #affecter la listbox a la nouvelle fenetre
            listbox = Tkinter.Listbox (tk_listbox, width = 30, height = 20, yscrollcommand = scrollbar.set)
            scrollbar.config (command = listbox.yview)
            scrollbar.pack (side = "right", fill = "y")
            listbox.pack (side = "left",fill = "both", expand = True)
            
            #EXTENDED: pour selectioner plusierus items
            listbox.config (selectmode = Tkinter.EXTENDED)
            listbox.pack ()
            Nfiles = 0
            
            for key in Dic.keys ():
                df = Dic [key]
                Nfiles += 1
                columns = columns + tuple (df.columns)
            
            self.Dic = Dic
            columns = [x for x, y in collections.Counter(columns).items () if y == Nfiles]
            columns.sort ()
            #afficher les colonnes de df dans la listbox
            for item in columns:
                listbox.insert (Tkinter.END, item)
                
            self.listbox = listbox
            
            #case pour Indicateurs de performance
            BoutonChoser = Tkinter.Checkbutton(tk_listbox, variable = self.do_indicateurs, text = "Indicateurs de performance")
            BoutonChoser.pack ()
        
            #case pour statistiques
            BoutonChoser = Tkinter.Checkbutton(tk_listbox, variable = self.do_stats, text = "Statistique")
            BoutonChoser.pack ()

            #case pour garder le mm graph
            BoutonChoser = Tkinter.Checkbutton(tk_listbox, variable = self.new_graph, text = "Nouveau graphique")
            BoutonChoser.pack ()
            
            #case pour insample
            BoutonChoser = Tkinter.Checkbutton(tk_listbox, variable = self.In_sample, text = "In Sample")
            BoutonChoser.pack ()
            
            #bouton pour faire le graphique
            Boutonplot = Tkinter.Button (tk_listbox, text ='plot', command = lambda : self.plot ())
            Boutonplot.pack ()
            
            #bouton pour fermer la fenetre cree
            Boutonrest = Tkinter.Button (tk_listbox, text ='fermer', command = tk_listbox.destroy)
            Boutonrest.pack ()

    def getselection (self, listbox):
        '''Renvois le(s) colonnes selectionnee dans la listebox'''
        
        #une seule selection
        try:
            selection = [listbox.get (listbox.curselection ())]
            
        #multi selection
        except Tkinter.TclError:
            selection = listbox.curselection()
            selection = [ int(i) for i in selection]
            itms = []
            for i in selection:
                itms.insert ( len(itms), listbox.get (i))
            selection = itms
        
        return selection
    
    def controle_nan (self, dic):
        columns_vide = {}
        for key in dic.keys ():
            first = True
            df = dic [key]
            for column in df.columns:
                if len (df [column].dropna ()) == 0 and first:
                    columns_vide [key] = [column]
                    first = False
                elif len (df [column].dropna ()) == 0 and first == False:
                    columns_vide [key] += [column]
                    
        if len (columns_vide.keys()) > 0:
            for key in columns_vide.keys ():
                columns_text = ' ,'.join(map(str, columns_vide [key] ))
                tkMessageBox.showinfo ("Attention", "Dans le fichier: " + key + " ,les colonnes suivantes sont vides: " + columns_text)
                
        return columns_vide
    
    def dic_to_df (self, dic, selection_):
        df = pd.DataFrame ()
        selection = []
        for key in dic.keys ():
            df_ = dic [key]
            for column in df_:
                df [column+'_'+key] = df_ [column]
                if column in selection_:
                    selection  = selection + [column + '_' + key]
        if len (selection) == 1:
            selection = selection [0]
        
        return df, selection
    
    def max_Insample_inDic (self, dic, selection):
        if self.In_sample.get() == 1:
            max_insample = None
            
            for key in dic.keys ():
                df = dic [key]
                
                if 'InSample' not in df.columns:
                    df ['InSample'] = 0
                    
                if max_insample is None:
                    max_insample = df ['InSample'].dropna () 
                     
                else:
                    if len (df.index) < len (max_insample.index):
                        df = df.reindex (index = max_insample.index, method = 'ffill')
                        
                    elif len (df.index) > len (max_insample.index):
                        max_insample = max_insample.reindex (index = df.index, method = 'ffill', inplace = True)
                        
                    max_insample = np.maximum (df ['InSample'], max_insample)
        else:
            max_insample = 0
        return max_insample
    
    def do_LaTex_legende (self, stats):
        rdmt =  stats ['rdmt']*100
        vol = stats ['vol']*100
        sharpe_ratio = stats ['sharpe_ratio']
        mean_f = stats ['mean_f']
        max_f = stats ['max_f']
        min_f = stats ['min_f']
        DD = stats ['DD']*100
        skew = stats ['skew']
        kur = stats ['kur']
        sortino = stats ['Sortino']
        
        if stats ['coef'] == 100:
            str_precent = '\%'
        else:
            str_precent = ''
        
        rdmt_str = '$\mu=' + str("%.2f" % rdmt) + '\% $'
        vol_str = ' $\sigma=' + str("%.2f" % vol) + '\% $'
        sharpe_ratio_str = ' $ \\frac{\mu}{\sigma}=' + str("%.2f" % sharpe_ratio) + '$'
        DD_str = ' $\mathrm{DDmax}=' + str("%.2f" % DD) + '\% $'
        sortino_str = ' $\mathrm{Sortino}=' + str("%.2f" % sortino) + '$'
        
        max_str = ' $\mathrm{max}=' + str("%.2f" % max_f) + str_precent+'$'
        min_str = ' $\mathrm{min}=' + str("%.2f" % min_f) + str_precent+'$'
        mean_str = ' $\mathrm{mean}=' + str("%.2f" % mean_f) + str_precent+'$'
        skew_str = ' $\mathrm{Skewness}=' + str("%.2f" % skew)+ '$'
        kur_str = ' $\mathrm{Kurtosis}=' + str("%.2f" % kur) + '$'
        
        text_indic =  rdmt_str + vol_str + sharpe_ratio_str + DD_str + sortino_str
        text_stats = max_str + min_str + mean_str + skew_str + kur_str
        text_indic_stats = text_indic + ' ' + text_stats
        
        return text_indic, text_stats, text_indic_stats
    
    def choice_user_indi (self, stats):
        text_indic, text_stats, text_indic_stats = self.do_LaTex_legende (stats)
        
        if self.do_indicateurs.get () == 1 and self.do_stats.get () != 1:
            #textstr = '$\mu_{'+ k_+ '}=%.2f$\n$\sigma_{'+ k_+ '}=%.2f$\n$\mathrm{ratio\ de\ sharpe}=%.2f$'%(rdmt*100, vol*100, sharp_ratio)
            textstr = text_indic
            
        elif self.do_indicateurs.get () == 1 and self.do_stats.get () == 1:
            textstr = text_indic_stats

        elif self.do_stats.get () == 1 and self.do_indicateurs.get () != 1:
            textstr = text_stats
            
        return textstr
                
    def plot (self):
        ''' faire un graph de(s) label(s) selectionne de(s) df dans dic, ainsi que les stats et les indicateur des perfs'''
        
        #la selection de l'utilisateur
        selection_init = self.getselection (listbox = self.listbox)
        
        #le dictionnaire de(s) DataFrame(s)
        dic = self.Dic
        
        if selection_init == []:
            tkMessageBox.showinfo ("Attention", 'Il faut choisir une colonne')
            return
        
        if self.new_graph.get() == 1 and self.df_ploted is not None:
            self.init_params ()
        
        self.max_insample = self.max_Insample_inDic (dic, selection_init)
        df, selection = self.dic_to_df (dic, selection_init)
        
        max_value, min_value = np.max (df [selection]), np.min (df [selection])
        
        while type (max_value) != np.float64:
            max_value = np.max (max_value) * 1.
            
        while type (min_value) != np.float64:
            min_value = np.min (min_value) * 1.
        
        df ['InSample'] = self.max_insample
        if isinstance (selection, str) or isinstance (selection, unicode):
            selection = [selection]
        
        ax = self.figure.add_subplot (111)
        for label in selection:
            if self.i_color >= len (self.colors):
                self.i_color = 0
                self.i_text_u = 0.97
                
            colore = self.colors [self.i_color]
            
            if 'InSample' in df.columns and (self.do_indicateurs.get () == 1 or self.do_stats.get () == 1):
                
                out_of_sample = df [df ['InSample']<1].copy ()
                out_of_sample = out_of_sample [label].dropna ()

                stats = self.calc_stats (out_of_sample)
                textstr = self.choice_user_indi (stats)
                    
                if self.df_ploted is None:
                    self.df_ploted = pd.DataFrame (df [label])
                else:
                    self.df_ploted [label] = df [label]
                    
                props = dict (boxstyle = 'round', facecolor = colore, alpha = 0.2)  
                ax.text (self.i_text, self.i_text_u, textstr, transform=ax.transAxes, fontsize=18,
                        verticalalignment='center', bbox=props)
                #represantation de la zone d'apprentissage
                if sum (df['InSample'].dropna()) > 1 and self.do_fill_between:
                    ax.fill_between(df.index, min_value, max_value+0.1*max_value, where = df['InSample']>0, facecolor='gray', interpolate = False, alpha = 0.2)
                    
                    green_patch = mpatches.Patch (color = 'gray', label = 'In Sample', alpha = 0.2)
                    legende_sample = ax.legend (handles = [green_patch])
                    self.do_fill_between = False
                    
                ax.plot (self.df_ploted.index, self.df_ploted [label], label = label, color = colore)
                self.i_color += 1
                self.i_text_u -= 0.055 

            else:
                if self.df_ploted is None:
                    self.df_ploted = pd.DataFrame (df [label])
                else:
                    self.df_ploted [label] = df [label]
                
                ax.plot (self.df_ploted.index, self.df_ploted [label], label = label,  color = colore)
                ax.legend()
                self.i_color += 1
            
        if self.do_indicateurs.get () == 1 or self.do_stats.get () == 1:
            #self.i_text_u -= 0.055  
            ax.legend (loc = 4)
        else:
            ax.legend (loc = 2)
        ax.grid (True)
                
        plt.show ()
        
    def calc_stats (self, serie):
        serie = serie.dropna ()
        if serie.name == 'GAV_pct' or serie.name == 'NAV_pct':
            i = 0
            while serie [i] == 0:
                i += 1
        else:
            i = 0
            
        serie = serie.iloc [i:-1].copy ()
        rdmt_days = serie.diff ().dropna ()
        rdmt_days_neg = rdmt_days [rdmt_days < 0.]
        vol_rdmNeg = np.std (rdmt_days_neg) * np.sqrt (260)
        
        diff_days = len (pd.date_range (serie.index [0], serie.index [-1]))
        rdmt = (serie.values [-1] - serie.values [0]) * (365. / diff_days)
        vol = np.std (rdmt_days) * np.sqrt (260)
        sharpe_ratio = rdmt / vol
        mean_f = np.mean (serie)
        max_f = max (serie)
        min_f = min (serie)
        max_rolling = pd.expanding_max (serie)
        kur = stats.kurtosis (rdmt_days)
        skew = stats.skew (rdmt_days)
        sortino = rdmt / vol_rdmNeg
        
        if abs (mean_f) <= 1:
            coef = 100
        else:
            coef = 1
            
        DD = min ((serie - max_rolling).dropna ())
        dic_stat = {}
        dic_stat['rdmt'] = rdmt
        dic_stat['vol'] = vol
        dic_stat['sharpe_ratio'] = sharpe_ratio
        dic_stat['mean_f'] =  mean_f * coef
        dic_stat['max_f'] =  max_f * coef
        dic_stat['min_f'] =  min_f * coef
        dic_stat['DD'] =  DD
        dic_stat['kur'] =  kur
        dic_stat['skew'] =  skew
        dic_stat['coef'] = coef
        dic_stat['Sortino'] = sortino
        
        return dic_stat

if __name__ == "__main__":
    app = guiplot_tk (None)
    app.title ('Graphique')
    app.mainloop ()
