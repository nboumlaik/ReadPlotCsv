#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
import Tkinter
import tkFileDialog
import pandas as pd
import matplotlib
from cProfile import label
matplotlib.use ('TkAgg')
from matplotlib import pyplot as plt
import getpass
import collections
import matplotlib.patches as mpatches
import numpy as np
import FileDialog  # @UnusedImport
from scipy import stats
import tkMessageBox
from scipy.special import _ufuncs_cxx #pour py2exe @UnusedImport
from scipy.sparse.csgraph import _validation #pour py2exe @UnusedImport
import os
import ttk
import datetime


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
        self.legend_out = Tkinter.IntVar ()
        self.do_rebase = Tkinter.IntVar ()
        self.analyse = Tkinter.IntVar ()
        self.format_date = Tkinter.StringVar()
        self.header = Tkinter.StringVar()
        self.rebase_serie_chekb = False
        
        self.listbox = None
        self.Dic = None
        self.In_sample.set (1)
        self.new_graph.set (1)
        self.nb_plot = 0
        self.index_fin = None
        self.df_rebase = pd.DataFrame ()
        self.style = Tkinter.StringVar ()

        self.ddate_analyse = None
        self.fdate_analyse = None
        
        self.init_params ()
        self.initialize ()
        
    def init_params (self):
        #plt.close ('all')
        self.figure = plt.figure ()
        self.do_fill_between = True
        self.df_ploted = None
        self.max_insample = None
        self.i_color = 0
        self.i_text = 0.01
        self.i_text_u = 0.97
        self.index_fin = None

    def initialize (self):
        # Création le bouton importer 
        Boutonread = Tkinter.Button ( self, text = 'Importer', command = lambda  : self.dolistbox () )
        Boutonread.grid ()
        
        #bouton quitter
        BoutonQuitter = Tkinter.Button (self, text = 'Quitter', command = self.destroy)
        BoutonQuitter.grid ()
        
        label = Tkinter.Label (self, text = 'Format date', width = 20)
        label.grid ()
        
        e = Tkinter.Entry (self, textvariable = self.format_date)
        e.grid ()
        self.format_date.set ('%Y-%m-%d')
        
        label = Tkinter.Label (self, text = 'Header', width = 20)
        label.grid ()
        
        e = Tkinter.Entry (self, textvariable = self.header)
        e.grid ()
        self.header.set (0)
        
        #advestis picture:
        can1 = Tkinter.Canvas (self, width = 190, height = 190, bg = 'white')
        can1.create_image (100, 100, image = self.photo)
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
        
        try:
            #construire la liste de(s) chemin(s)
            fpath = self.splitlist (fpath)
            chemin = fpath [0]
            chemin = chemin [:chemin.rfind ("/")]
        except:
            if self.chemin_ is not None:
                return
            else:
                chemin = ''
        
        if chemin == '':
            self.chemin_ = 'C:/Users/%s' % self.user
        else:
            self.chemin_ = chemin
            
        try:
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
                if len (df.columns) == 0:
                    try:
                        int (self.header.get ())
                    except:
                        tkMessageBox.showinfo ("Format incorrect de Header", 'Il faut renseigner un intier')
                        return
                    df = pd.read_csv (p, index_col = 0, sep = ";", header = int (self.header.get ()) )
                
#                 try:
#                     df.index = pd.DatetimeIndex (df.index)
#                 except:
#                     pass
                try:
                    if self.format_date.get() != '':
                        df.index = pd.to_datetime (df.index, format = self.format_date.get())
                    else:
                        pass
                except Exception as e:
                    tkMessageBox.showinfo ("Date", str(e) + ' , please try again')
                    return
                    
                df.sort (axis = 1, inplace = True)
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
            self.Dic = Dic
            
            columns = ()
            #creation d'une nouvelle fenetre
            self.tk_listbox = Tkinter.Toplevel ()
            self.tk_listbox.title ('Les colonnes')
            scrollbar = Tkinter.Scrollbar (self.tk_listbox, orient="vertical")
            
            #grab_set: makes sure that no mouse or keyboard events are sent to the wrong window
            self.tk_listbox.grab_set ()
            
            #affecter la listbox a la nouvelle fenetre
            listbox = Tkinter.Listbox (self.tk_listbox, width = 30, height = 20, yscrollcommand = scrollbar.set)
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
            
            columns = [x for x, y in collections.Counter(columns).items () if y == Nfiles]
            columns.sort ()
            
            #afficher les colonnes de df dans la listbox
            for item in columns:
                listbox.insert (Tkinter.END, item)
                
            self.listbox = listbox
            
            #case pour Indicateurs de performance
            BoutonChoser = Tkinter.Checkbutton(self.tk_listbox, variable = self.do_indicateurs, text = "Indicateurs de performance")
            BoutonChoser.pack ()
        
            #case pour statistiques
            BoutonChoser = Tkinter.Checkbutton(self.tk_listbox, variable = self.do_stats, text = "Statistique")
            BoutonChoser.pack ()

            #case pour garder le mm graph
            BoutonChoser = Tkinter.Checkbutton(self.tk_listbox, variable = self.new_graph, text = "Nouveau graphique")
            BoutonChoser.pack ()
            
            #case pour insample
            BoutonChoser = Tkinter.Checkbutton(self.tk_listbox, variable = self.In_sample, text = "In Sample")
            BoutonChoser.pack ()
                      
            #case pour la legend
            BoutonChoser = Tkinter.Checkbutton (self.tk_listbox, variable = self.legend_out, text = "No legend")
            BoutonChoser.pack ()
            
            BoutonChoser = Tkinter.Checkbutton (self.tk_listbox, variable = self.do_rebase, text = "Rebaser")
            BoutonChoser.pack ()
            
            BoutonChoser = Tkinter.Checkbutton (self.tk_listbox, variable = self.analyse, text = "Analyse")
            BoutonChoser.pack ()
            
            label = Tkinter.Label (self.tk_listbox, text = 'Style des graphiques')
            label.pack ()
            
            combo = ttk.Combobox (self.tk_listbox, textvariable = self.style, state = 'readonly')
            combo ['values'] = [u'dark_background', u'bmh', u'grayscale', u'ggplot', u'fivethirtyeight']
            combo.pack ()
            combo.set ('grayscale')
            combo.bind ('<<ComboboxSelected>>', self.set_sele_lb)
            
            #bouton pour faire le graphique
            Boutonplot = Tkinter.Button (self.tk_listbox, text ='plot', command = lambda : self.plot ())
            Boutonplot.pack ()
            
            #bouton pour faire le diagrame
            Boutonplot = Tkinter.Button (self.tk_listbox, text ='histogramme', command = lambda : self.plot (do_hist = True, do_graphe = False))
            Boutonplot.pack ()
            
            #bouton pour faire le diagrame
            Boutonplot = Tkinter.Button (self.tk_listbox, text = "Dates d'analyse", command = lambda : self.rebase_serie ())
            Boutonplot.pack ()
            
#             Bouton = Tkinter.Button (self.tk_listbox, text = "Format de date", command = lambda : self.update_format_date ())
#             Bouton.pack ()
            
            #bouton pour fermer la fenetre cree
            Boutonrest = Tkinter.Button (self.tk_listbox, text ='fermer', command = self.tk_listbox.destroy)
            Boutonrest.pack ()
            
            def selection_listbox (ev):
                self.selection_lisbox = self.getselection (listbox = self.listbox)
                
            self.listbox.bind ('<<ListboxSelect>>', selection_listbox)
            
    def update_format_date (self):
        root = Tkinter.Toplevel ()
        label = Tkinter.Label (root, text = 'Format', width = 20)
        root.grab_set ()
        label.pack (padx = 5, pady = 5)
        
        date_varcombo = Tkinter.StringVar()
        
        combo = ttk.Combobox (root, textvariable = date_varcombo, width = 40)
        combo ['values'] = ['%Y-%m-%-d', '%Y/%m/%/d', '%Y %m %% d','%Y%m%d']
        combo.pack ()
        
        def update ():
            format_date = date_varcombo.get ()
    
            for key in self.Dic.keys ():
                df = self.Dic [key]
                df.index = pd.to_datetime (df.index, format = format_date)
                df.sort (inplace = True)
                self.Dic [key] = df
                print df
                print format_date
        Bouton = Tkinter.Button (root, text = 'Valider', command = lambda : update () )
        Bouton.pack (padx = 5, pady = 5)
        
    def set_sele_lb (self, ev):
        
        try:
            selection = self.selection_listbox
            for i, _ in enumerate (selection):
                self.listbox.selection_set (selection [i])
        except:
            pass
            
    def rebase_serie (self):
        
        self.sel_set = self.listbox.curselection()
        
        self.rebase_serie_chekb = True
        
        selection_init = self.getselection (listbox = self.listbox)
        df, selection = self.dic_to_df (self.Dic, selection_init)
        
        if selection == []:
            tkMessageBox.showinfo ("Attention", 'Il faut choisir une colonne')
            return
        
        self.df_rebase = pd.DataFrame (df [selection].copy ())
        
        ddate_varcombo = Tkinter.StringVar()
        fdate_varcombo = Tkinter.StringVar()
        root = Tkinter.Toplevel ()
        root.title ('Rebaser')
        root.grab_set ()
        
        label = Tkinter.Label (root, text = "Date de depart", width = 20)
        label.pack (padx = 5, pady = 5)
        
        combo_d = ttk.Combobox (root, textvariable = ddate_varcombo, state = 'readonly', width = 40)
        combo_d ['values'] = self.df_rebase.index.tolist ()
        try:
            combo_d.set(self.ddate_analyse)
        except:
            pass
        combo_d.pack ()
        
        label = Tkinter.Label (root, text = "Date de fin", width = 20)
        label.pack (padx = 5, pady = 5)
        
        combo_f = ttk.Combobox (root, textvariable = fdate_varcombo, state = 'readonly', width = 40)
        combo_f ['values'] = self.df_rebase.index.tolist ()
        try:
            combo_f.set(self.fdate_analyse)
        except:
            pass
        combo_f.pack ()
        
        Bouton = Tkinter.Button (root, text = 'Valider', command = lambda : get_value_comb () )
        Bouton.pack (padx = 5, pady = 5)
        
        if type (selection) == str:
            selection = [selection]
            
        def get_value_comb ():
            for i, _ in enumerate (self.sel_set):
                self.listbox.selection_set (self.sel_set[i])
            
            try:
                self.ddate_analyse = datetime.datetime.strptime (ddate_varcombo.get (), "%Y-%m-%d %H:%M:%S")
            except:
                pass
            
            try:
                self.fdate_analyse = datetime.datetime.strptime (fdate_varcombo.get (), "%Y-%m-%d %H:%M:%S")
            except:
                pass
            
            try:
                self.label_dfdepart_.forget ()
            except:
                pass
            
            self.label_dfdepart_ = Tkinter.Label (self.tk_listbox, text = 'de '  + str(self.ddate_analyse)[:10] + " à " +  str(self.fdate_analyse)[:10])
            self.label_dfdepart_.pack ()
                
            if self.ddate_analyse != '':
                for col in selection:
                    self.df_rebase [col] = self.df_rebase [col] / self.df_rebase [col].loc [self.ddate_analyse]
                    self.rebase_date = self.ddate_analyse
                    
            try:
                self.label_dfdepart.forget ()
            except:
                pass
            
            self.label_dfdepart = Tkinter.Label (root, text = 'de '  + str(self.ddate_analyse)[:10] + " à " +  str(self.fdate_analyse)[:10])
            self.label_dfdepart.pack ()
        
            root.destroy ()
                
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
                
    def get_min_max (self, serie):
        
        max_value, min_value = np.max (serie), np.min (serie)
        
        while type (max_value) != np.float64:
            max_value = np.max (max_value) * 1.
            
        while type (min_value) != np.float64:
            min_value = np.min (min_value) * 1.
            
        return max_value, min_value
    
    def plot (self, do_graphe = True, do_hist = False):
        ''' faire un graph de(s) ou un histogramme label(s) selectionne de(s) df dans dic, ainsi que les stats et les indicateur des perfs'''
        #self.clear_ ()
        #la selection de l'utilisateur
        selection_init = self.getselection (listbox = self.listbox)
        
        #le dictionnaire de(s) DataFrame(s)
        dic = self.Dic
        
        if selection_init == []:
            tkMessageBox.showinfo ("Attention", 'Il faut choisir une colonne')
            return
        
        if self.do_rebase.get() and len (self.df_rebase) == 0:
            tkMessageBox.showinfo ("Attention", "Il faut rebaser une série, ou découchez la case 'Rebase'")
            return
        
        if self.new_graph.get() == 1 and self.df_ploted is not None:
            self.init_params ()
            
        #on calcul self.index_fin
        try:
            self.calc_index_fin ()
        except:
            self.index_fin = None
        
        self.max_insample = self.max_Insample_inDic (dic, selection_init)
        df, selection = self.dic_to_df (dic, selection_init)
        self.selection = selection
        
        if self.do_rebase.get ():
            try:
                max_value, min_value = self.get_min_max (self.df_rebase [selection])
#                 self.df_rebase ['InSample'] = 1
#                 self.df_rebase ['InSample'].loc [df.index > self.rebase_date] = 0
#                 df ['InSample'] = self.df_rebase ['InSample']
                self.df_rebase ['InSample'] = self.max_insample
                df ['InSample'] = self.max_insample
            except KeyError:
                str_list = ""
                for column_rebase in self.df_rebase.columns:
                    str_list += "'" + column_rebase + "' "
                tkMessageBox.showinfo ("Attention", "La série séléctionnée n'est pas rebasée. Les séries rebasées: " + str_list)
                return
        else:
            max_value, min_value = self.get_min_max (df [selection])
            df ['InSample'] = self.max_insample
            
        
        if isinstance (selection, str) or isinstance (selection, unicode):
            selection = [selection]
        
        #on calcul le nombre des bins pour l'histogramme
        if do_hist:
            bin_init = 200
            for column in selection:
                bin = len (df [column].dropna()) / 20  # @ReservedAssignment
                bin = min (bin, bin_init)  # @ReservedAssignment
        #[u'dark_background', u'bmh', u'grayscale', u'ggplot', u'fivethirtyeight']
        #plt.style.use (self.style.get())
        with plt.style.context((self.style.get())): 
            ax = self.figure.add_subplot (111)
            for label in selection:
                if self.i_color >= len (self.colors):
                    self.i_color = 0
                    self.i_text_u = 0.97
                    
                colore = self.colors [self.i_color]
                
                if ('InSample' in df.columns or 'InSample' in self.df_rebase.columns)  and (self.do_indicateurs.get () == 1 or self.do_stats.get () == 1):
                    
                    if self.do_rebase.get ():
                        out_of_sampleOrAnalyse = self.df_rebase.loc [(df.index >= self.ddate_analyse) & (df.index <= self.fdate_analyse)] 
                        out_of_sampleOrAnalyse = pd.DataFrame (out_of_sampleOrAnalyse)
                        if self.analyse.get ():
                            if self.ddate_analyse is None and self.fdate_analyse is None:
                                tkMessageBox.showinfo ("Attention", "Il faut choisir une periode pour l'analyse")
                                return
                            out_of_sampleOrAnalyse = out_of_sampleOrAnalyse.loc [(out_of_sampleOrAnalyse.index >= self.ddate_analyse) & (out_of_sampleOrAnalyse.index <= self.fdate_analyse)].dropna()
                            df ['Analyse'] = 0
                            df ['Analyse'].loc [(df.index >= self.ddate_analyse) & (df.index <= self.fdate_analyse)] = 1
                        
                    elif self.analyse.get () and not self.do_rebase.get ():
                        if self.ddate_analyse is None and self.fdate_analyse is None:
                            tkMessageBox.showinfo ("Attention", "Il faut choisir une periode pour l'analyse")
                            return
                        out_of_sampleOrAnalyse = df.loc [(df.index >= self.ddate_analyse) & (df.index <= self.fdate_analyse)].dropna()
                        df ['Analyse'] = 0
                        df ['Analyse'].loc [(df.index >= self.ddate_analyse) & (df.index <= self.fdate_analyse)] = 1
                    else:
                        out_of_sampleOrAnalyse = df [df ['InSample']<1].copy ()
                        
                    out_of_sampleOrAnalyse = out_of_sampleOrAnalyse [label].dropna ()
                    
                    stats = self.calc_stats (out_of_sampleOrAnalyse)
                    textstr = self.choice_user_indi (stats)
                    
                    if self.df_ploted is None:
                        self.df_ploted = pd.DataFrame (df [label])
                    else:
                        self.df_ploted [label] = df [label]
                    
                    props = dict (boxstyle = 'round', facecolor = colore, alpha = 0.2)  
                    ax.text (self.i_text, self.i_text_u, textstr, transform=ax.transAxes, fontsize=18,
                            verticalalignment='center', bbox=props)
                    
                    #la fin de la periode de backtest
                    if self.index_fin is not None:
                        ax.fill_between (df.index, min_value, max_value + 0.1 * max_value, where = df.index>=self.index_fin, facecolor='gray', interpolate = False, alpha = 0.2)
                    #represantation de la zone d'apprentissage
                    if sum (df['InSample'].dropna()) > 1 and self.do_fill_between:
                        ax.fill_between (df.index, min_value, max_value + 0.1 * max_value, where = df['InSample'] > 0, facecolor='gray', interpolate = False, alpha = 0.2)
                            
                        green_patch = mpatches.Patch (color = 'gray', label = 'In Sample', alpha = 0.2)
                        legende_sample = ax.legend (handles = [green_patch])  # @UnusedVariable
                        self.do_fill_between = False

                    
                    if self.do_rebase.get():
                        ax.plot (self.df_rebase.index, self.df_rebase [label], label = label,  color = colore) 
                         
                    elif do_graphe:
                        ax.plot (self.df_ploted.index, self.df_ploted [label], label = label,  color = colore)
                        
                    elif do_hist:
                        ax.hist(self.df_ploted [label], bins = bin, alpha=0.5, label = label)
                        
                    self.i_text_u -= 0.055
                    self.i_color += 1
    
                else:
                    if self.df_ploted is None:
                        self.df_ploted = pd.DataFrame (df [label])
                    else:
                        self.df_ploted [label] = df [label]
                    
                    if self.do_rebase.get ():
                        ax.plot (self.df_rebase.index, self.df_rebase [label], label = label,  color = colore) 
                         
                    elif do_graphe:
                        ax.plot (self.df_ploted.index, self.df_ploted [label], label = label,  color = colore)
                        
                    elif do_hist:
                        ax.hist(self.df_ploted [label].dropna(), bins = bin, alpha = 0.5, label = label)
                        
                    ax.legend()
                    self.i_color += 1
                    
            if self.analyse.get () and self.ddate_analyse is not None and self.fdate_analyse is not None:
                ax.fill_between (df.index, min_value, max_value + 0.1 * max_value, where = df ['Analyse'] > 0, facecolor='green', interpolate = False, alpha = 0.2)
                
            if self.do_indicateurs.get () == 1 or self.do_stats.get () == 1:
                self.i_text_u -= 0.055  
                ax.legend (loc = 4)
            else:
                ax.legend (loc = 2)
            if self.legend_out.get():
                #ax.legend (loc = 'center left', bbox_to_anchor = (1, 0.5))
                ax.legend_.remove ()
            ax.grid (True)
        
        self.nb_plot += 1
        if self.analyse.get () and (self.do_indicateurs.get () == 1 or self.do_stats.get () == 1):
            title = 'From '  + str(self.ddate_analyse)[:10] + " to " +  str(self.fdate_analyse)[:10]
            
        elif (self.do_indicateurs.get () == 1 or self.do_stats.get () == 1):
            title = 'From '  + str(out_of_sampleOrAnalyse.index[0])[:10] + " to " +  str(out_of_sampleOrAnalyse.index[-1])[:10]
        else:
            title = ""
            
        plt.title (title)
        plt.show ()
              
    def int_to_month (self, int_month):
        int_month = int (int_month)
        list_month = ['', 'Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']
        return list_month [int_month]
    
    def calc_index_fin (self):
        for key in self.Dic.keys():
            df = self.Dic [key].copy()
            df.dropna (inplace = True)
            if 'NAV_pct' in df.columns:
                serie = df ['NAV_pct']
                rdm_ = serie.diff()
                i = -1
                rdm_i = 0
                #tol_iter = -10
                while rdm_i == 0:
                    index_fin = rdm_.index [i]
                    rdm_i = rdm_.loc [index_fin]
                    i -= 1
                    
                serie = serie.loc [serie.index [0]:index_fin].copy()
                if self.index_fin is not None:
                    if index_fin < self.index_fin:
                        self.index_fin = index_fin
                else:
                    self.index_fin = index_fin
                               
        return df
    
    def calc_stats (self, serie):
        
        try:
            fdate = self.fdate_analyse
        except:
            fdate = self.index_fin
            
        serie = serie.loc [serie.index [0]:fdate].copy()
        
        if serie.name == 'GAV_pct' or serie.name == 'NAV_pct':
            i = 0
            while serie [i] == 0:
                i += 1
        else:
            i = 0
            
        #serie = serie.iloc [i:-1].copy ()
        rdmt_days = (serie.diff () / serie).dropna ()
        rdmt_days_neg = rdmt_days [rdmt_days < 0.]
        vol_rdmNeg = np.std (rdmt_days_neg) * np.sqrt (260)
        
        diff_days = len (pd.date_range (serie.index [0], serie.index [-1]))
        rdmt = ((serie.values [-1] - serie.values [0]) / serie.values [0]) * (365. / diff_days)
        vol = np.std (rdmt_days) * np.sqrt (260)
        sharpe_ratio = rdmt / vol
        mean_f = np.mean (serie)
        max_f = max (serie)
        min_f = min (serie)
        
        kur = stats.kurtosis (rdmt_days)
        skew = stats.skew (rdmt_days)
        sortino = rdmt / vol_rdmNeg
        
        rdmt_days_byYM = rdmt_days.groupby([lambda x: x.year,lambda x: x.month]).sum()
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
        
        max_rolling = pd.expanding_max (serie)
        serieDD = (serie / max_rolling - 1).dropna ()
        DD = min (serieDD)
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
        clear = lambda: os.system ('cls')
        clear()

if __name__ == "__main__":
    app = guiplot_tk (None)
    app.title ('Graphique')
    app.mainloop ()
