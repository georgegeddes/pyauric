from setuptools import setup
setup(name = 'pyauric'
      , packages = ['pyauric'] # this must be the same as the name above
      , version = '0.1'
      , description = 'A python interface for the AURIC model.'
      , author = 'George Geddes'
      , author_email = 'georgegdds@gmail.com'
      , keywords = ['AURIC','auric','radiative transfer','radiative transport'] # arbitrary keywords
      , install_requires=['numpy','fortranformat']
      , extras_require={'pandas':['pandas']
                        ,'plotting':['matplotlib']}
      , classifiers = []
)
