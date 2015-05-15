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
from scipy import stats
import tkMessageBox
from scipy.special import _ufuncs_cxx #pour py2exe
from scipy.sparse.csgraph import _validation #pour py2exe
import os
from pandas.tseries.offsets import BDay
from msilib.schema import ListBox



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
        
        self.figure = plt.figure()
        self.do_indicateurs = Tkinter.IntVar ()
        self.do_stats = Tkinter.IntVar ()
        self.new_graph = Tkinter.IntVar ()
        self.In_sample = Tkinter.IntVar ()
        self.legend_out = Tkinter.IntVar ()
        self.In_sample.set (1)
        self.new_graph.set (1)
        self.label_matrice = Tkinter.Label ()
        self.label_strat = Tkinter.Label ()
        self.label_appr = Tkinter.Label ()
        
        self.legend_list_rule_colore = []
        self.legend_list_rule_label = []
        
        self.do_fill_between_bool = True
        self.df_ploted = None
        self.max_insample = None
        self.listbox = None
        self.Dic = None
        self.matrice = None
        self.appr = None
        self.strat = None
        self.rules_viz = False
        self.root_rules = None
        
        self.i_colore_rule = 0
        self.i_colore_rule = 0
        self.nb_plot = 0
        self.index_fin = -1
        self.i_color = 0
        self.i_text = 0.01
        self.i_text_u = 0.97
        
        self.init_params ()
        self.initialize ()
        
    def init_params (self):
        #plt.close ('all')
        if self.new_graph.get() == 1 and self.df_ploted is not None:
            self.figure = plt.figure()
            self.do_fill_between_bool = True
            self.df_ploted = None
            self.max_insample = None
            self.i_color = 0
            self.i_text = 0.01
            self.i_text_u = 0.97
            self.legend_list_rule_colore = []
            self.legend_list_rule_label = []
            self.i_colore_rule = 0
        
    def initialize (self):
        # Création le bouton importer 
        Boutonread = Tkinter.Button ( self, text = 'Importer', command = lambda  : self.dolistbox (Dic = self.ReadCsv ()) )
        Boutonread.grid ()
        
        # Création le bouton Visu reg 
        Boutonread = Tkinter.Button ( self, text = 'Visualisation des regles', command = lambda  : self.visureg () )
        Boutonread.grid ()
        
        #bouton quitter
        BoutonQuitter = Tkinter.Button (self, text = 'Quitter', command = self.destroy)
        BoutonQuitter.grid ()
        
        #advestis picture:
        can1 = Tkinter.Canvas (self, width = 190, height = 190, bg = 'white')
        can1.create_image (100, 100, image = self.photo)
        can1.grid (row = 0, column = 2, rowspan = 10, padx = 10, pady = 5)
        
    def visureg (self):
        self.root_rules = Tkinter.Toplevel ()
        self.root_rules.geometry("270x145")
        self.root_rules.title ('Importation des fichiers')
        self.root_rules.grab_set ()
        
        Boutonread_matrice = Tkinter.Button ( self.root_rules, text = 'Importer la matrice', command = lambda  : self.ReadCsv (df_str = 'Matrice' ) )
        Boutonread_matrice.grid (padx=10, pady=5)
        
        Boutonread_appr = Tkinter.Button ( self.root_rules, text = "Importer l'apprentissage", command = lambda  : self.ReadCsv (df_str = 'Appr') )
        Boutonread_appr.grid (padx=10, pady=5)
        
        Boutonread_strat = Tkinter.Button ( self.root_rules, text = 'Importer strat/fond', command = lambda  : self.ReadCsv ('Strat') )
        Boutonread_strat.grid (padx=10, pady=5)
            
        Boutonr = Tkinter.Button ( self.root_rules, text = 'Reinitialisation', command = lambda  : self.reini_rules () )
        Boutonr.grid (padx=10, pady=5)
    
    def reini_rules (self):
        self.strat = None
        self.appr = None
        self.matrice = None
        self.label_matrice.grid_forget()
        self.label_strat.grid_forget()
        self.label_appr.grid_forget()
        
    def Ftext (self, string, car1 = '_' , car2 = '(', n = 1 ):
        i_debut = string.find (car1) + n
        i_fin = string [i_debut+1:].find (car2) + i_debut +1
        string = string [i_debut:i_fin]
        
        return string

    def get_title_ask (self, df_str = None):  
         
        if df_str == 'Matrice':
            title_ask = 'Ouvrir la Matrice'
            
        elif df_str == 'Appr':
            title_ask = "Ouvrir le fichier des regles"
            
        elif df_str == 'Strat':
            title_ask = 'Ouvrir le fond ou un portfeuille ou une strategie'
        
        else:
            title_ask = 'Ouvrir'
            
        return title_ask

    def get_path (self, title_ask):
        if self.chemin_ is None:
            fpath = tkFileDialog.askopenfilenames (title = title_ask, defaultextension = ".csv", initialfile = '*.csv', initialdir = 'C:/Users/%s' % self.user)
        else:
            fpath = tkFileDialog.askopenfilenames (title = title_ask, defaultextension = ".csv", initialfile = '*.csv', initialdir = self.chemin_)
            
        chemin = fpath [:fpath.rfind ("/")]
        
        if chemin == '':
            self.chemin_ = 'C:/Users/%s' % self.user
        else:
            self.chemin_ = chemin
        
        return fpath
        
    def ReadCsv (self, df_str = None):
        '''importe un/des csv, et renvoi un dic'''
        title_ask = self.get_title_ask (df_str)
        fpath = self.get_path (title_ask)

        try:
            #construire la liste de(s) chemin(s)
            fpath = self.splitlist (fpath)
            dic = {}
            #on stock les df dans dic
            for p in fpath:
                try:
                    p.decode()
                except:
                    p = p.decode('utf-8')
                    
                nom_init = p [p.rfind ("/"):]
                
                if len (nom_init) > 30:
                    nom = self.Ftext (nom_init)

                else:
                    nom = nom_init [1:-4]
                    
                if nom == "":
                    nom = nom_init [1:-4]
                
                  
                df = pd.read_csv (p, index_col = 0)
                if len (df.columns)  == 0:
                    try:
                        df = pd.read_csv (p, index_col = 0, sep = ";")
                    except:
                        pass
                try:
                    df.index = pd.DatetimeIndex (df.index)
                except:
                    pass
                try:
                    df.index = pd.to_datetime (df.index, format='%Y%m%d')
                except:
                    pass
                dic [nom] = df
                
            if df_str == None:
                return dic
            
            elif df_str == 'Matrice' and len (dic.keys()) !=0:
                self.matrice = dic
                self.root_rules
                self.label_matrice = Tkinter.Label (self.root_rules, text = "Ok")
                self.label_matrice.grid (column = 1, row = 0, padx = 10, pady = 5)
                
            elif df_str == 'Appr' and len (dic.keys()) !=0:
                self.appr = dic
                self.label_appr = Tkinter.Label (self.root_rules, text = "Ok")
                self.label_appr.grid (column = 1, row = 1, padx = 10, pady = 5)
                
            elif df_str == 'Strat' and len (dic.keys()) !=0:
                self.strat = dic
                self.label_strat = Tkinter.Label (self.root_rules,text = "Ok")
                self.label_strat.grid (column = 1, row = 2, padx = 10, pady = 5)
            
            self.do_listbox_rules ()
            
        except IOError:
            if fpath == '':
                return None
            else:
                print "le chemin n'existe pas"
                
    def do_listbox_rules (self):
        if self.strat != None and self.appr != None and self.matrice != None:
            self.rules_viz = True
            self.dolistbox (self.appr)
    
    def do_new_lisbox (self, title):
        tk_listbox = Tkinter.Toplevel ()

        tk_listbox.title (title)
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
        
        return listbox, tk_listbox
    
    def get_common_columns (self, dic_of_df):
        Nfiles = 0
        columns = ()
        for key in dic_of_df.keys ():
            df = dic_of_df [key]
            Nfiles += 1
            if self.rules_viz:
                columns = columns + tuple (df.index)
            else:
                columns = columns + tuple (df.columns)
        
        columns = [x for x, y in collections.Counter(columns).items () if y == Nfiles]
        columns.sort ()
        
        return columns
    
    #affiche la listbox dans une nouvelle fenetre
    def dolistbox (self, Dic):
        '''Creation de la liste et de la fenetre des columns de(s) DF importe. Affiche le boutton "plot" afin de faire les graphiques'''
        #on importe le(s) csv dans un dictionnaire
        #Dic = self.ReadCsv ()
        
        #on traite le dictionnaire
        if Dic == {}:
            return
        
        elif Dic is not None:
            #test des colonnes vides (messageBox)
            self.controle_nan (Dic)
            self.Dic = Dic
            
            if self.rules_viz:
                title = 'Regles'
            else:
                title = 'Les colonnes'
                
            #creation d'une nouvelle fenetre
            listbox, tk_listbox = self.do_new_lisbox (title)
            
            columns = self.get_common_columns (Dic)
            
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
                      
            #case pour la legend
            BoutonChoser = Tkinter.Checkbutton(tk_listbox, variable = self.legend_out, text = "Decaler la legend")
            BoutonChoser.pack ()
            
            #bouton pour faire le graphique
            if self.rules_viz:
                Boutonplot = Tkinter.Button (tk_listbox, text ='plot', command = lambda : self.plot_rule ())
                Boutonplot.pack ()           
            else:
                Boutonplot = Tkinter.Button (tk_listbox, text ='plot', command = lambda : self.plot ())
                Boutonplot.pack ()
            
            if not self.rules_viz:
                #bouton pour faire le diagrame
                Boutonplot = Tkinter.Button (tk_listbox, text ='histogramme', command = lambda : self.plot (do_hist = True, do_graphe = False))
                Boutonplot.pack ()
        
            Boutonplot = Tkinter.Button (tk_listbox, text ='fermer tout les graphes', command = lambda : plt.close ('all'))
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
    
    def dic_to_df (self, dic, selection_init):
        '''transforme le dic des df en un seul df, avec que les colonnes selectionnees par l'utilisateur'''
        df = pd.DataFrame ()
        
        selection = []
        for key in dic.keys ():
            df_ = dic [key]
            for column in df_:
                #nom de la calonne + le nom du fichier
                df [column+'_'+key] = df_ [column]
                if column in selection_init:
                    selection  = selection + [column + '_' + key]
                    
        if isinstance (selection, str) or isinstance (selection, unicode):
            selection = [selection]
        
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
        DDmu = stats ['DD/mu']
        dateDD = stats ['DateDD']
        bm = stats['BM'][0]
        wm = stats['WM'][0]
        dtbm = stats['BM'][1]
        dtwm = stats['WM'][1]
        
        if stats ['coef'] == 100:
            str_precent = '\%'
        else:
            str_precent = ''
        
        rdmt_str = '$\mu=' + str("%.2f" % rdmt) + '\% $'
        vol_str = ' $\sigma=' + str("%.2f" % vol) + '\% $'
        sharpe_ratio_str = ' $ \\frac{\mu}{\sigma}=' + str("%.2f" % sharpe_ratio) + '$'
        DD_str = ' $\mathrm{DDmax}=' + str("%.2f" % DD) + '\%('+ dateDD + ')$'
        sortino_str = ' $\mathrm{Sortino}=' + str("%.2f" % sortino) + '$'
        DDmu_str = ' $\\frac{DD}{\mu}=' + str("%.2f" % DDmu) + '$'
        BM = ' $\mathrm{BM}=' + str("%.2f" % bm) + '\% (' + dtbm + ')$'
        WM = ' $\mathrm{WM}=' + str("%.2f" % wm) + '\% (' + dtwm + ')$'
        
        max_str = ' $\mathrm{max}=' + str("%.2f" % max_f) + str_precent+'$'
        min_str = ' $\mathrm{min}=' + str("%.2f" % min_f) + str_precent+'$'
        mean_str = ' $\mathrm{mean}=' + str("%.2f" % mean_f) + str_precent+'$'
        skew_str = ' $\mathrm{Skewness}=' + str("%.2f" % skew)+ '$'
        kur_str = ' $\mathrm{Kurtosis}=' + str("%.2f" % kur) + '$'
        
        text_indic =  rdmt_str + vol_str + sharpe_ratio_str + DD_str + sortino_str + DDmu_str + BM + WM
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
    
    def get_index_rule (self, selection):         
        clem = self.matrice.keys () [0]
        clea = self.appr.keys () [0]
        
        matrice = self.matrice [clem]
        appr = self.appr [clea]
        
        df_rule = pd.DataFrame (appr.ix [selection])
        for col in df_rule.columns:
            len_column = len (df_rule [col].dropna())
            if len_column == 0:
                del df_rule [col]
        
        dic_var = {}
        dic_rule = {}
        n_variable = len (df_rule.columns) 
        n_variable /= 3
        
        for i in range (n_variable):
            i += 1
            for rule in selection:
                var = df_rule ['Var'+str(i)].loc [rule]
                max = df_rule ['Max'+str(i)].loc [rule]
                min = df_rule ['Min'+str(i)].loc [rule]
                dic_var [var] = [max, min]
                if rule in dic_rule:
                    dic_var_ = dic_rule [rule]
                    dic_var_ [var] = [max, min]
                    dic_rule [rule] = dic_var_
                else:
                    dic_rule [rule] = dic_var
                #reinisialiser le dic des var
                dic_var = {}
                
        df_rule = pd.DataFrame (index = matrice.index)
        for rule in dic_rule.keys ():
            df_rule [rule] = 1
            dic_var = dic_rule [rule]
            
            for var in dic_var.keys ():
                max, min = dic_var [var] [0], dic_var [var] [1]
                index = matrice .loc [(matrice [var] >= min) & (matrice [var] <= max), var].index
                df_rule [var] = 0
                df_rule [var].loc [index] = 1
                df_rule [rule] *=  df_rule [var]
            
        return pd.DataFrame (df_rule [dic_rule.keys ()])


    def plot_rule (self):
        #la selection de l'utilisateur
        selection_init = self.getselection (listbox = self.listbox)
        
        #le dictionnaire de(s) DataFrame(s)
        dic = self.Dic
        
        if selection_init == []:
            tkMessageBox.showinfo ("Attention", 'Il faut choisir une colonne')
            return
        
        if self.new_graph.get() == 1 and self.df_ploted is not None:
            self.init_params ()
        
        selection = 'NAV_pct'
        
        cle_strat = self.strat.keys() [0]
        df = self.strat [cle_strat]
        
        if 'InSample' in df.columns:
            self.max_insample = df ['InSample']
        
        df_rules = self.get_index_rule (selection_init)
        df_rules = df_rules .loc [df.index] 
        max_value, min_value = np.max (df [selection]), np.min (df [selection])
        
        while type (max_value) != np.float64:
            max_value = np.max (max_value) * 1.
            
        while type (min_value) != np.float64:
            min_value = np.min (min_value) * 1.
        
        if isinstance (selection, str) or isinstance (selection, unicode):
            selection = [selection]
                
        ax = self.figure.add_subplot (111)
        for label in selection_init:
            if self.i_color >= len (self.colors):
                self.i_color = 0
                self.i_text_u = 0.97
                
            colore = self.colors [self.i_color]
            plt.title ('NAV_pct') 
                
            ax.fill_between (df_rules.index, min_value, max_value+0.1*max_value, where = df_rules [label] > 0, facecolor=colore, interpolate = True, alpha = 0.2)
            self.legend_list_rule_colore += [plt.Rectangle((0, 0), 1, 1, fc=colore)]
            self.legend_list_rule_label += [label]
            #legende_sample = ax.legend (handles = [_patch])
            #ax.legend(handles=[red_patch])

                    
            if 'InSample' in df.columns and (self.do_indicateurs.get () == 1 or self.do_stats.get () == 1 or self.In_sample.get() == 1):
                
                try:
                    out_of_sample = df [df ['InSample']<1].copy ()
                    out_of_sample = out_of_sample [label].dropna ()
                    
                    stats = self.calc_stats (out_of_sample)
                    textstr = self.choice_user_indi (stats)
                          
                    props = dict (boxstyle = 'round', facecolor = colore, alpha = 0.2)  
                    ax.text (self.i_text, self.i_text_u, textstr, transform=ax.transAxes, fontsize=18,
                            verticalalignment='center', bbox=props)
                except:
                    pass
                
                #la fin de la periode de backtest
                self.index_fin = self.calc_index_fin (serie = df ['NAV_pct']) [1]
                if self.index_fin is not None:
                    ax.fill_between (df.index, min_value, max_value+0.15*max_value, where = df.index>self.index_fin, facecolor='gray', interpolate = False, alpha = 0.3)
                    
                #represantation de la zone d'apprentissage
                if sum (df['InSample'].dropna()) > 1 and self.do_fill_between:
                    ax.fill_between (df.index, min_value, max_value+0.15*max_value, where = df['InSample']>0, facecolor='gray', interpolate = False, alpha = 0.3)
                    
                    #_patch = mpatches.Patch (color = 'gray', label = 'In Sample', alpha = 0.4)
                    #legende_sample = ax.legend (handles = [_patch])
                    self.do_fill_between = False
                    
            if self.df_ploted is None:
                self.df_ploted = pd.DataFrame (df ['NAV_pct'])
                
            else:
                self.df_ploted [label] = df ['NAV_pct']      
                    
            if self.nb_plot == 0 or self.new_graph.get() == 1:
                ax.plot (self.df_ploted.index, self.df_ploted ['NAV_pct'], label = 'NAV_pct',  color = 'darksage')
                ax.legend ()
            

            self.i_text_u -= 0.055
            self.i_color += 1
        
        if self.do_indicateurs.get () == 1 or self.do_stats.get () == 1:
            self.i_text_u -= 0.055  
            ax.legend (loc = 4)
            
        else:
            ax.legend (loc = 2)
            
        ax.grid (True)
        self.nb_plot += 1
        ax.legend(self.legend_list_rule_colore, self.legend_list_rule_label)
        
        if self.legend_out.get():
            #ax.legend(loc = 'center left', bbox_to_anchor = (1, 0.5))
            ax.legend_.remove()
            
        plt.show ()
        
    def get_max_min (self, serie):
        max_value, min_value = np.max (serie), np.min (serie)
        
        while type (max_value) != np.float64:
            max_value = np.max (max_value) * 1.
            
        while type (min_value) != np.float64:
            min_value = np.min (min_value) * 1.
            
        return max_value, min_value

    def get_bins (self, bin_init = 200): 
                
        bin_init = 200
        for column in selection:
            bin = len (df [column].dropna()) / 20
            bin = min (bin, bin_init)
        return bin
    
    def get_colore (self):
        
        if self.i_color >= len (self.colors):
            self.i_color = 0
            self.i_text_u = 0.97
        colore = self.colors [self.i_color]
        
        return colore
    
    def get_text_stats (self, df, label):
        
        out_of_sample = df [df ['InSample']<1].copy ()
        out_of_sample = out_of_sample [label].dropna ()

        stats = self.calc_stats (out_of_sample)
        textstr = self.choice_user_indi (stats)
        
        return textstr

    def update_df_ploted (self, serie):

        if self.df_ploted is None:
            self.df_ploted = pd.DataFrame (serie)
        else:
            self.df_ploted [serie.name] = serie
            
    def do_fill_between_for_end_index (self, serie, ax): 
                
        self.index_fin = self.calc_index_fin (serie = serie) [1]
        if self.index_fin is not None:
            ax.fill_between (df.index, min_value, max_value+0.1*max_value, where = df.index>self.index_fin, facecolor='gray', interpolate = False, alpha = 0.2)
        
        return ax
    
    def add_text_to_ax (self, ax, colore, textstr):
        
        props = dict (boxstyle = 'round', facecolor = colore, alpha = 0.2)  
        ax.text (self.i_text, self.i_text_u, textstr, transform = ax.transAxes, fontsize = 18,
                verticalalignment = 'center', bbox = props)
        
        return ax

    def do_fill_between (self, df, selection, ax):
        
        max_value, min_value = self.get_max_min (df [selection])
        
        if sum (df['InSample'].dropna()) > 1 and self.do_fill_between_bool and self.In_sample.get() == 1:
            ax.fill_between (df.index, min_value, max_value + 0.1 * max_value, where = df['InSample'] > 0, facecolor='gray', interpolate = False, alpha = 0.2)
            
            green_patch = mpatches.Patch (color = 'gray', label = 'In Sample', alpha = 0.2)
            legende_sample = ax.legend (handles = [green_patch])
            self.do_fill_between_bool = False
            
        return ax

    def do_legend (self, ax):
               
        if self.do_indicateurs.get () == 1 or self.do_stats.get () == 1:
            self.i_text_u -= 0.055  
            ax.legend (loc = 4)
        else:
            ax.legend (loc = 2)
            
        if self.legend_out.get():
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            
        return ax
        
    def plot (self, do_graphe = True, do_hist = False):
        ''' faire un graph de(s) ou un histogramme label(s) selectionne de(s) df dans dic, ainsi que les stats et les indicateur des perfs'''
        #la selection de l'utilisateur
        selection_init = self.getselection (listbox = self.listbox)
        
        #le dictionnaire de(s) DataFrame(s)
        dic = self.Dic
        
        if selection_init == []:
            tkMessageBox.showinfo ("Attention", 'Il faut choisir une colonne')
            return
        
        self.init_params ()
        self.max_insample = self.max_Insample_inDic (dic, selection_init)
        df, selection = self.dic_to_df (dic, selection_init)
        df ['InSample'] = self.max_insample

        #on calcul le nombre des bins pour l'histogramme
        if do_hist:
            bin = self.get_bins (bin_init = 200)
                
        ax = self.figure.add_subplot (111)
        for label in selection:
            
            colore = self.get_colore ()
            if 'InSample' in df.columns and (self.do_indicateurs.get() or self.do_stats.get ()):
                text_stats = self.get_text_stats (df, label)
                ax = self.add_text_to_ax (ax, colore, text_stats)
                ax = self.do_fill_between_for_end_index (serie = df [label], ax = ax)
                #represantation de la zone d'apprentissage
                ax = self.do_fill_between (df, selection, ax)
                       
                self.i_text_u -= 0.055
                self.i_color += 1

            self.update_df_ploted (df [label])
            if do_graphe:
                ax.plot (self.df_ploted.index, self.df_ploted [label], label = label,  color = colore)
                
            elif do_hist:
                ax.hist (self.df_ploted [label].dropna (), bins = bin, alpha = 0.5, label = label)
                    
            ax.legend()
            self.i_color += 1
        
        ax = self.do_legend (ax)
            
        ax.grid (True)
        
        self.nb_plot += 1  
        plt.show ()
        
        
    def int_to_month (self, int_month):
        int_month = int (int_month)
        list_month = ['', 'Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']
        return list_month [int_month]
    
    def calc_index_fin (self, serie):
        if 'NAV' in serie.name or 'GAV' in serie.name:
            rdm_ = serie.diff()
            i = -1
            rdm_i = 0
            tol_iter = -10
            while rdm_i == 0:
                index_fin = rdm_.index [i]
                rdm_i = rdm_.loc [index_fin]
                i -= 1
                
            serie = serie.loc [serie.index [0]:index_fin].copy()
        else:
            index_fin = None
        
        return (serie, index_fin)
    
    def calc_stats (self, serie):
        serie = self.calc_index_fin (serie=serie)  [0]
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
        
        rdmt_days_byYM = rdmt_days.groupby ([lambda x: x.year,lambda x: x.month]).sum()
        BM = max (rdmt_days_byYM)
        WM = min (rdmt_days_byYM)
        
        date_BM = rdmt_days_byYM.loc [rdmt_days_byYM == BM].index[0]
        date_WM = rdmt_days_byYM.loc [rdmt_days_byYM == WM].index[0]
        
        dtBM = date_BM
        mois = self.int_to_month (dtBM[1])
        dtBM = mois + ' ' + str (dtBM[0])
        
        dtWM = date_WM
        mois = self.int_to_month (dtWM[1])
        dtWM = mois + ' ' + str (dtWM[0])

        serieDD = (serie - max_rolling).dropna ()
        DD = min ((serie - max_rolling).dropna ())
        dateDD = serieDD.loc [(serieDD==DD)].index [0]
        mois = self.int_to_month (dateDD.month)
        dateDD = str (dateDD.day) + ' ' + mois + ' ' + str (dateDD.year)
        
        if abs (mean_f) <= 1:
            coef = 100
        else:
            coef = 1
        
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
        dic_stat['DD/mu'] = abs (DD)/rdmt
        dic_stat['DateDD'] = dateDD
        dic_stat['BM'] = (BM * 100, dtBM)
        dic_stat['WM'] = (WM * 100, dtWM)
        
        return dic_stat
    
    def clear_ (self):
        clear = lambda: os.system('cls')
        clear()

if __name__ == "__main__":
    app = guiplot_tk (None)
    app.title ('Graphique')
    app.mainloop ()
