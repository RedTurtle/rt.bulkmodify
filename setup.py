from setuptools import setup, find_packages
import os

version = '0.4'

tests_require = ['plone.app.testing', ]

setup(name='rt.bulkmodify',
      version=version,
      description="An administration tool for performing mass text substitution on Plone contents",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        ],
      keywords='plone batch bulk regex',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/rt.bulkmodify',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rt'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          'Products.CMFPlone>4.0b1',
          'plone.uuid',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
