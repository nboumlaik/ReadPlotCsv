from distutils.core import setup
import py2exe
import sys, os
import glob
import matplotlib
import tkMessageBox

sys.argv.append ('py2exe')


# We need to exclude matplotlib backends not being used by this executable.  You may find
# that you need different excludes to create a working executable with your chosen backend.
# We also need to include various numerix libraries that the other functions call.

opts = {
  'py2exe': { "includes" : ["matplotlib.backends.backend_tkagg", "tkMessageBox"],

                'excludes': ['_gtkagg', '_tkagg', '_agg2', '_cairo', '_cocoaagg', "matplotlib.numerix.fft","sip", "PyQt4._qt",
                              "matplotlib.backends.backend_qt4agg",
                               "matplotlib.numerix.linear_algebra", "matplotlib.numerix.random_array", '_fltkagg', '_gtk','_gtkcairo' , 'IPython'],
              
              'dll_excludes': ['libgdk-win32-2.0-0.dll',
                                 'libgobject-2.0-0.dll',"MSVCP90.dll"]
              }
       }

## Save matplotlib-data to mpl-data ( It is located in the matplotlib\mpl-data
## folder and the compiled programs will look for it in \mpl-data
## note: using matplotlib.get_mpldata_info
## matplotlib.get_py2exe_datafiles()
##data_files = [(r'mpl-data', glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\*.*')),
##                    # Because matplotlibrc does not have an extension, glob does not find it (at least I think that's why)
##                    # So add it manually here:
##                  (r'mpl-data', [r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\matplotlibrc']),
##                  (r'mpl-data\images',glob.glob(r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\images\*.*')),
##                  (r'mpl-data\fonts',glob.glob(r'C:\Python26\Lib\site-packages\matplotlib\mpl-data\fonts\*.*'))]

# for console program use 'console = [{"script" : "scriptname.py"}] 
setup (windows = [{"script" : "ReadPlotCsv_script.py"}], options = opts,   data_files = matplotlib.get_py2exe_datafiles())
