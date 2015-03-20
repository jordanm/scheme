from setuptools import setup, find_packages

setup(
    name='scheme',
    version='2.0',
    description='A declarative schema framework.',
    license=open('LICENSE').read(),
    author='Jordan McCoy',
    author_email='mccoy.jordan@gmail.com',
    url='https://github.com/arterial-io/scheme',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
