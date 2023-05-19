import setuptools

setuptools.setup(
                 name='reportgen',
                 version='0.1',
                 description='The report generator library for the Fiddler platform',
                 url='https://github.com/shuds13/pyexample',
                 author='Bashir R',
                 author_email='bashir@fiddler.ai',
                 license='BSD 2-clause',
                 packages=['reportgen'],
                 install_requires=['numpy',
                                   'scipy',
                                   'pandas',
                                   'fiddler-client',
                                   'Jinja2',
                                   'scikit-learn',
                                   'python-docx',
                                   'docxtpl',
                                   'matplotlib',
                                   'docx2pdf',
                                   ],
)
