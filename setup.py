from numpy.distutils.core import setup, Extension
from numpy import get_include
from numpy.version import version as npversion
import generatePyCamb
import os.path
import sys
from subprocess import call
if '--nonstop' in sys.argv:
    sys.argv.remove('--nonstop')
    from nonstopf2py import f2py
else:
    from numpy import f2py

# Get CAMB from http://camb.info, untar and copy *.[fF]90 to src/
# this is done by the script extract_camb.sh
call(["bash", "extract_camb.sh"])

# List of all sources that must be there
cambsources = ['camb/%s' % f for f in [
    'constants.f90',
    'utils.F90',
    'subroutines.f90',
    'inifile.f90',
    'power_tilt.f90',
    'recfast.f90',
    'reionization.f90',
    'modules.f90',
    'bessels.f90',
    'equations.f90',
    'halofit.f90',
    'lensing.f90',
    'SeparableBispectrum.F90',
    'cmbmain.f90',
    'camb.f90',
]]

# Check if all sources are in fact there
for f in cambsources:
    if not os.path.exists(f):
        raise Exception("At least one of CAMB code file: '%s' is not found. Download and extract to camb/" % f)

# Make folder "src" unless already made
try: os.mkdir('src')
except: pass
generatePyCamb.main()

# Generate .pyf wrappers
f2py.run_main(['-m', '_pycamb', '-h', '--overwrite-signature', 'src/py_camb_wrap.pyf',
         'src/py_camb_wrap.f90', 'skip:', 'makeparameters', ':'])

# Newer versions of f2py (from numpy >= 1.6.2) use specific f90 compile args
int_version = int(npversion.replace('.', ''))
if int_version > 161:
    pycamb_ext = Extension("pycamb._pycamb",
                           ['src/py_camb_wrap.pyf'] + cambsources + ['src/py_camb_wrap.f90'],
                           extra_f90_compile_args=['-O0', '-g', '-Dintp=npy_intp', '-fopenmp'],
                           libraries=['gomp'],
                           include_dirs=[get_include()],
                           )
else:
    Extension("pycamb._pycamb",
             ['src/py_camb_wrap.pyf'] + cambsources + ['src/py_camb_wrap.f90'],
             extra_compile_args=['-O0', '-g', '-Dintp=npy_intp'],
             include_dirs=[get_include()],
             )

# Perform setup
setup(name="pycamb", version="0.2",
      author="Joe Zuntz",
      author_email="jaz@astro.ox.ac.uk",
      description="python binding of camb, you need sign agreement and obtain camb source code to build this. Thus we can not GPL this code.",
      url="http://github.com/joezuntz/pycamb",
      download_url="http://web.phys.cmu.edu/~yfeng1/#",
      zip_safe=False,
      install_requires=['numpy'],
      requires=['numpy'],
      packages=[ 'pycamb' ],
      package_dir={'pycamb': 'src'},
      data_files=[('pycamb/camb', ['camb/HighLExtrapTemplate_lenspotentialCls.dat'])],
      scripts=[],
      ext_modules=[pycamb_ext]
    )

