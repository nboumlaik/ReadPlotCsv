#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
import Tkinter
#import MainCalcSession
import ttk
import time
import threading
import Init
import ConfigParser
import pdb
import sys, getopt
import TSession

global oSession

class gui_main (Tkinter.Tk):
    
    def __init__ (self, parent):
        Tkinter.Tk.__init__ (self, parent)
        self.parent = parent
        try:
            pp = r'D:\Dropbox\temp\Nouveau dossier\exe\advestis.gif'
            photo = Tkinter.PhotoImage (file = pp )
        except:
            photo = Tkinter.PhotoImage (file = 'advestis.gif')
            
        self.photo = photo
        
        #advestis picture:
        can1 = Tkinter.Canvas (self, width = 190, height = 190, bg = 'white')
        can1.create_image (100,100, image = self.photo)
        can1.grid (row = 0, column = 2, rowspan = 10, padx = 10, pady = 5)
        
        self.entry_dault ()
        self.initialize ()
        
    def initialize (self):    
        # Création le bouton importer 
        Boutonread = Tkinter.Button ( self, text = 'Lancer les calculs', command = lambda  : self.main_calc () )
        Boutonread.grid (row = 5, column = 1)

        # Création le bouton importer 
        Boutonread = Tkinter.Button ( self, text = 'Valeurs par defaut', command = lambda  : self.entry_dault () )
        Boutonread.grid (row = 6, column = 1)
        
        #bouton quitter
        BoutonQuitter = Tkinter.Button (self, text = 'Quitter', command = self.destroy)
        BoutonQuitter.grid (row = 7, column = 1)
        
    def entry_dault (self):  
        self.dicEntry = {}
        self.dic_tex = {'Section Global':'global_20V', 'Repertoire':'4 Gestion', 'Fichier de configuration':'SessionConfig_Alloc_{Prod_Dec14}.cfg', 'Session':'Session_Alloc_Prod{Py=Dec14}'}
        self.dic_keyargv = {'Section Global':'-g', 'Repertoire':'-p', 'Fichier de configuration':'-f', 'Session':'-s'}
        r = 0
        
        for line, item in enumerate(['Section Global', 'Repertoire', 'Fichier de configuration', 'Session']):
            text = self.dic_tex [item]
            l = Tkinter.Label (self, text = item, width = 20,)
            self.dicEntry [item] = Tkinter.Entry (self, width = 35)
            l.grid (row=line, column = 0)
            self.dicEntry [item].insert(0, text)
            self.dicEntry [item].grid (row = line, column = 1)
        
        self.argv = []
        for key in self.dic_keyargv:
            var1 = self.dic_keyargv [key]
            var2 = self.dic_tex [key]
            self.argv += [var1]
            self.argv += [var2]
            
    def update_values_entry (self):
        self.argv = ['-g', self.dicEntry ['Section Global'].get(),
                      '-p', self.dicEntry ['Repertoire'].get()+'/',
                       '-f', self.dicEntry ['Fichier de configuration'].get(),
                        '-s', self.dicEntry ['Session'].get()]
        return self.argv

    def main_calc (self):
        arv = self.update_values_entry ()
        self.main (arv)
        print arv
        
        
    def main (self, argv):
    
       try:
          opts, args = getopt.getopt (argv,"hg:p:f:s:c:",["global=","configpath=","configfile=", "section=", "command="])
       except getopt.GetoptError:
          print 'MainCalcSession.py -p <configpath> -f <configfile> -s <section> -c <command>'
          sys.exit(2)
    
       command = 'calc'
       for opt, arg in opts:
          if opt == '-h':
             print 'MainCalcSession.py -p <configpath> -f <configfile> - s <section> - c <command>'
             sys.exit()
          elif opt in ('-g', '--global'):
             globalsection = arg            
          elif opt in ("-p", "--configpath"):
             cfgpath = arg
          elif opt in ("-f", "--configfile"):
             cfgfile = arg
          elif opt in ("-s", "--section"):
             cfgsection = arg
          elif opt in ("-c", "--command"):
             command = arg         
    
       #print opts
       Init.main (['-s ' + globalsection])
       global oSession
       oSession = TSession.TSession ()
       #pdb.set_trace()
       oSession.loadData (cfgpath, cfgfile, cfgsection)
       
       if command != 'loadonly':
       #Calculer les positions cibles des fonds
           if oSession._bdoCalcTargets:
              oSession.doGetFundHTargetPositions ()
        
              if oSession._bdoRisks:
                  oSession.doCalcHRiskFactors ()
        
              if oSession._bdoResults:
                  if oSession._bdoFundResults:
                      oSession.doCalcFundHResults ()
                  elif oSession._bdoStratResults:
                      oSession.doCalcStratHResults ()              
                  oSession.doCalcHReturnOfRiskFactors ()
              
              if oSession._bdoMetrics:
                  #pdb.set_trace()
                  oSession.doCalcHMetrics ()
                  oSession.doGetRiskReport ()
        
              oSession.doSaveHTargetPositions ()
        
        #       if oSession._bdoPredStats:
        #          oSession.doWritePredStats ()
           
              #calculer les opérations du jour
              if oSession._bdoDayTrades:
                 oSession.doGetFundDayTrades ()
                 oSession.doSaveFundDayTrades ()      
        
              if oSession._bdoAudit:
                  oSession.doWriteAuditData ()
        
        
           if oSession._bdoHistoTrades:
              oSession.doAnalyzeHistoTrades ()
              oSession.doSaveHistoPosAndTrades ()
              if oSession._bdoCalcTargets:
                  #import pdb; pdb.set_trace ()
                  oSession.doWriteFundResultBreakdownReport()
              
           if oSession._bdoPredStats:
               oSession.doGetTrainingVariablesReport()
               oSession.doWritePredStats ()
        
        
    #     #recuperer oSession
    #     with open('donnees', 'rb') as fichier:
    #         mon_depickler = pickle.Unpickler(fichier)
    #         df_recupere = mon_depickler.load()
        
           Init.closeLogFile ()
        
if __name__ == "__main__":
    app = gui_main (None)
    app.title ('Main Session')
    app.mainloop ()
    