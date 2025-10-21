from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='ruft',
  version='0.1',
  author='Olegs Verhodubs',
  author_email='oleg.verhodub@inbox.lv',
  description='This is a prototype package for generating rules from raw text',
  install_requires=['nltk>=3.9.2'],
  classifiers=[
    'Programming Language :: Python :: 3.13',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent'
  ],
  keywords='rules text natural_language_processing python',
  python_requires='>=3.13'
)