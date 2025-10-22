from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r', encoding="utf-8") as f:
    return f.read()

setup(
  name='krashemit',
  version='1.0.0',
  author='Krash13',
  author_email='krasheninnikov.r.s@muctr.ru',
  description='Library for solving optimization problems using the interacting countries algorithm',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/Krash13/KrasheMit',
  packages=find_packages(),
  install_requires=['numpy>=1.22.1', 'scipy<=1.13.0', 'numba>=0.58.1', 'graycode>=1.0.5'],
  classifiers=[
    'Programming Language :: Python :: 3.9',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent'
  ],
  keywords='Optimization, evolutionary algorithms, nature-inspired algorithms',
  project_urls={},
  python_requires='>=3.9'
)
