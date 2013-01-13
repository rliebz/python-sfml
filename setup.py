#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pySFML - Python bindings for SFML
# Copyright 2012-2013, Jonathan De Wachter <dewachter.jonathan@gmail.com>,
#				  Edwin Marshall <emarshall85@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import platform
from subprocess import call
from distutils.core import setup, Command, Extension


# python 2.* compatability
try: input = raw_input
except NameError: pass

class PyTest(Command):
	user_options = []

	def initialize_options(self): pass
	def finalize_options(self): pass
	def run(self):
		errno = call([sys.executable, 'runtests.py'])
		raise SystemExit(errno)

class Cython(Command):
	user_options = []

	def initialize_options(self): pass
	def finalize_options(self): pass
	def run(self):
		srcdir = 'src/sfml/'

		modules = ['system.pyx', 'window.pyx', 'graphics.pyx', 'audio.pyx',
				   'network.pyx']
		if platform.system() != 'Windows': modules.append('x11.pyx')

		for module in modules:
			try:
				errno = call('cython --cplus {0}{1} -Iinclude'.format(srcdir, module),
							 shell=True)
			except OSError:
				errno = 1
				print("Please install cython and try again.")
			finally:
				raise SystemExit(errno)


# check if cython is needed (if c++ files are generated or not)
NEED_CYTHON = not all(map(os.path.exists, [
	'src/sfml/x11.cpp',
	'src/sfml/system.cpp',
	'src/sfml/window.cpp',
	'src/sfml/graphics.cpp',
	'src/sfml/audio.cpp',
	'src/sfml/network.cpp']))

try:
	USE_CYTHON = NEED_CYTHON or bool(int(os.environ.get('USE_CYTHON', 0)))
except ValueError:
	USE_CYTHON = NEED_CYTHON or bool(os.environ.get('USE_CYTHON'))

if USE_CYTHON:
	x11_source = 'src/sfml/x11.pyx'
	system_source = 'src/sfml/system.pyx'
	window_source = 'src/sfml/window.pyx'
	graphics_source = 'src/sfml/graphics.pyx'
	audio_source = 'src/sfml/audio.pyx'
	network_source = 'src/sfml/network.pyx'

else:
	x11_source = 'src/sfml/x11.cpp'
	system_source = 'src/sfml/system.cpp'
	window_source = 'src/sfml/window.cpp'
	graphics_source = 'src/sfml/graphics.cpp'
	audio_source = 'src/sfml/audio.cpp'
	network_source = 'src/sfml/network.cpp'

extension = lambda name, files, libs: Extension(
	'sfml.' + name,
	files,
	['include', 'src/sfml'], language='c++',
	libraries=libs)

x11 = extension('x11', [x11_source], ['X11'])

system = extension(
	'system',
	[system_source, 'src/sfml/error.cpp'],
	['sfml-system', 'sfml-graphics'])

window = extension(
	'window', [window_source, 'src/sfml/derivablewindow.cpp'],
	['sfml-system', 'sfml-window'])

graphics = extension(
	'graphics',
	[graphics_source, 'src/sfml/derivablerenderwindow.cpp', 'src/sfml/derivabledrawable.cpp'],
	['sfml-system', 'sfml-window', 'sfml-graphics'])

audio = extension(
	'audio',
	[audio_source, 'src/sfml/derivablesoundrecorder.cpp', 'src/sfml/derivablesoundstream.cpp'],
	['sfml-system', 'sfml-audio'])

network = extension(
	'network',
	[network_source],
	['sfml-system', 'sfml-network'])


# install the C/Cython API in the python directory (its location varies)
# on Windows: C:\PythonXY\include\pysfml\*.pxd and *.h
# on Unix:    /usr/include/pythonX.Y/sfml/*.pxd and *.h

# define the include directory
if platform.system() == 'Windows':
	include_dir = sys.prefix + "\\include\\pysfml\\"
else:
	major, minor, _, _ , _ = sys.version_info
	include_dir = sys.prefix + "/include/python{0}.{1}/pysfml/".format(major, minor)

# list all relevant headers (find in include/ and src/sfml/)
# key: directory, value: list of headers to place in the directory
destinations = dict()

for path, subdirs, files in os.walk("include"):
	# don't forget to remove include/ from the path
	destination = include_dir + path[8:]
	destinations[destination] = []

	for name in files:
		destinations[destination].append(os.path.join(path, name))

for path, subdirs, files in os.walk("src/sfml"):
	for name in files:
		if name.endswith(".h"):
			destinations[include_dir].append(os.path.join(path, name))

# format data (list of tuple)
data_files = []
for key in destinations:
	data_files.append((key, destinations[key]))

with open('README.rst', 'r') as f:
	long_description = f.read()

if platform.system() == 'Windows':
	ext_modules=[system, window, graphics, audio, network]
else:
	ext_modules=[x11, system, window, graphics, audio, network]

kwargs = dict(
			name='pySFML',
			ext_modules=ext_modules,
			package_dir={'': 'src'},
			packages=['sfml'],
			data_files=data_files,
			version='1.2.0',
			description='Python bindings for SFML',
			long_description=long_description,
			author='Jonathan de Wachter, Edwin O Marshall',
			author_email='dewachter.jonathan@gmail.com, emarshall85@gmail.com',
			url='http://python-sfml.org',
			license='LGPLv3',
			classifiers=['Development Status :: 5 - Production/Stable',
						'Intended Audience :: Developers',
						'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
						'Operating System :: OS Independent',
						'Programming Language :: Cython',
						'Programming Language :: C++',
						'Programming Language :: Python',
						'Topic :: Games/Entertainment',
						'Topic :: Multimedia',
						'Topic :: Software Development :: Libraries :: Python Modules'],
			cmdclass={'test': PyTest, 'build_ext': Cython})

setup(**kwargs)
