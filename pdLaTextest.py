# -*- coding=latin - 1 -*-
import argparse
import subprocess
import shlex
import os
import sys
import shutil
import pandas as pd

path_script = os.path.dirname(os.path.realpath(sys.argv[0]))
dir_save = 'C:/Users/nboumlaik/workspace/'

path_csv = r'C:\Users\nboumlaik\Desktop\Analyse.csv'

df = pd.read_csv(path_csv, index_col = 0)

df = df.ix[:10] [df.columns [:5]]

# \begin{figure}[htb]
#   \includegraphics[scale=1]{df_WNDevPriceZscoreBy10Sector.png}
# \end{figure}

df_latex = str(df.to_latex ())

df_latex = df_latex.replace ("\\begin{tabular}", """\\begin{table}[ht]
\\resizebox{\\textwidth}{!}{%
\\begin{tabular}""")

    

df_latex= df_latex.replace ("\\end{tabular}","""\\end{tabular}%
}
  \\caption{Test Table}\\label{tab:label_test}
\\end{table}""")

"--------------------------------------------------------------------------------------------"
#df_latex = str(df.to_latex ()) .replace ('r'*len (df.columns), '|p{0.5cm}|'*len (df.columns))

content = r'''
\documentclass{article}
\usepackage[margin=2cm]{geometry}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage[latin1]{inputenc}  
\usepackage[T1]{fontenc}  
\usepackage{graphicx}  
\usepackage{sidecap}

\title{Reporting de la stratégie}

\date{\today}

\newcolumntype{Y}{>{\raggedleft\arraybackslash}X}

\begin{document}
\maketitle

\begin{center}
\author{\includegraphics[height=1cm,width=2cm]{advs.png}}
\end{center}


''' + df_latex + '\n' + r'''

\begin{center} 

\begin{figure}[hb]
 \centering
 \includegraphics[width=4in]{strat.png}
 \caption[]
   {Test graph strat}
 
\end{figure} 
  
\end{center}

Metuentes igitur idem latrones Lycaoniam magna parte campestrem cum se inpares nostris fore congressione stataria documentis frequentibus scirent, tramitibus deviis petivere Pamphyliam diu quidem intactam sed timore populationum et caedium, milite per omnia diffuso propinqua, magnis undique praesidiis conmunitam.
\end{document}'''



with open('cover.tex','w') as f:
    f.write(content)

proc=subprocess.Popen(['pdflatex', 'cover.tex'])
proc.communicate ()

shutil.move ('cover.pdf', dir_save + 'cover.pdf')

os.unlink('cover.tex')
os.unlink('cover.log')
os.unlink('cover.aux')