from setuptools import setup
setup(name = 'pyauric',
      packages = ['pyauric'], # this must be the same as the name above
      version = '0.2',
      description = 'A python interface for the AURIC model.',
      author = 'George Geddes',
      author_email = 'george_geddes@student.uml.edu',
      keywords = ['AURIC','auric','radiative transfer','radiative transport'], # arbitrary keywords
      install_requires = ['numpy', 'fortranformat', 'pandas', 'matplotlib'],
      test_suite = "tests.test_all",
)
