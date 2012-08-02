# Copyright (c) 2012, Tom SF Haines
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#  * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



import sys
import os.path
import tempfile
import shutil

from distutils.core import setup, Extension
import distutils.ccompiler
import distutils.dep_util



try:
  __default_compiler = distutils.ccompiler.new_compiler()
except:
  __default_compiler = None



def make_mod(name, base, source, openCL = False):
  """Uses distutils to compile a python module - really just a set of hacks to allow this to be done 'on demand', so it only compiles if the module does not exist or is older than the current source, and after compilation the program can continue on its merry way, and immediatly import the just compiled module. Note that on failure erros can be thrown - its your choice to catch them or not. name is the modules name, i.e. what you want to use with the import statement. base is the base directory for the module, which contains the source file - often you would want to set this to 'os.path.dirname(__file__)', assuming the .py file that imports the module is in the same directory as the code. It is this directory that the module is output to. source is the filename of the source code to compile. openCL indicates if OpenCL is used by the module, in which case it does all the necesary setup - done like this so these setting can be kept centralised, so when they need to be different for a new platform they only have to be changed in one place."""

  if __default_compiler==None: raise Exception('No compiler!')

  # Work out the various file names - check if we actually need to do anything...
  source_path = os.path.join(base, source)
  library_path = os.path.join(base, __default_compiler.shared_object_filename(name))

  if distutils.dep_util.newer(source_path, library_path):
    try:
      # Backup the argv variable and create a temporary directory to do all work in...
      old_argv = sys.argv[:]
      temp_dir = tempfile.mkdtemp()

      # Prepare the extension...
      sys.argv = ['','build_ext','--build-lib', base, '--build-temp', temp_dir]

      if openCL:
        ext = Extension(name, [source_path], include_dirs=['/usr/local/cuda/include', '/opt/AMDAPP/include'], libraries = ['OpenCL'], library_dirs = ['/usr/lib64/nvidia', '/opt/AMDAPP/lib/x86_64'])
      else:
        ext = Extension(name, [source_path])

      # Compile...
      setup(name=name, version='1.0.0', ext_modules=[ext])

    finally:
      # Cleanup the argv variable and the temporary directory...
      sys.argv = old_argv
      shutil.rmtree(temp_dir, True)
