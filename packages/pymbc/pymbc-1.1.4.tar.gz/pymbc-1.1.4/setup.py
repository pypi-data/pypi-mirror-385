from setuptools import setup

setup(

    name = 'pymbc',    
    version = '1.1.4',   
    description = 'A python package for working with MB Century downhole data.', 
    py_modules = ["pymbc"],
    package_dir = {'':'src'},
    author = 'Richard Williams',
    author_email = 'rwilliams@mbcentury.com',
    long_description = open('README.md').read() + '\n\n' + open('CHANGELOG.md').read(),
    long_description_content_type = "text/markdown",
    url='https://github.com/tricky67/pymbc',

    include_package_data=True,

    classifiers  = [
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Framework :: Matplotlib',
        'Environment :: No Input/Output (Daemon)',
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'Topic :: Text Processing',
        'Topic :: Scientific/Engineering',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
    ],
    
    python_requires='>=3.11',

    install_requires = [
        'numpy  >= 1.24',
        'pandas >= 1.5',
        'matplotlib >= 3.6',
        'scipy >= 1.13.0'
    ],
    
    keywords = ['dab', 'csv', 'pts', 'htcc', 'Century Logger'],
    
)
