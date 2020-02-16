from numpy.distutils.core  import setup, Extension
import os, sys, subprocess

dir_bufrlib = 'Bufrlib'

dir_library      = os.path.join(dir_bufrlib, 'src')
dir_source_file  = os.path.join(dir_bufrlib, 'src/_bufrlib.pyf')
dir_bufrlib_file = os.path.join(dir_bufrlib, 'src/libbufr.a')

extension_bufrlib = Extension(name  = '_bufrlib',
                        sources       = [dir_source_file],
                        libraries     = ['bufr'],
                        library_dirs  = [dir_library])

if not os.path.isfile(dir_bufrlib_file):
    command = 'cd {}; sh makebufrlib.sh'.format(dir_library)
    sys.stdout.write('Executando {}\n'.format(command))
    subprocess.call(command, shell = True)

if __name__ == "__main__":
    setup(name = 'Bufrlib',
          version           = "1.0.0",
          description       = "Wrapper in python for NCEP BUFRLIB, in Fortran77. ICEA, 2020.",
          author            = "Adrisson Samersla",
          author_email      = "adrissonsamersla@gmail.com",
          url               = "",
          ext_modules       = [extension_bufrlib],
          packages          = ['Bufrlib'],
          )
