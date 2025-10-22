from setuptools import setup, find_packages
import tsme

long_description = "The ``tsme`` package provides estimation methods for ODE or PDE systems using timeseries data. It also includes basic time simulation capabilities by wrapping scipy's initial value problem solver, either using finite differences or pseudo-spectral methods for spatial derivatives."

file = open("requirements.txt")
lines = file.readlines()
packages = [item[:-1] for item in lines]
cut = [i for i, item in enumerate(packages) if item[0] == "#"]
package_list = packages[:cut[0]]
file.close()

setup(
    name='tsme',
    version=tsme.__version__,
    url='https://nonlinear-physics.zivgitlabpages.uni-muenster.de/ag-kamps/tsme/',
    license='GPL',
    author='Oliver Mai',
    author_email='oliver.mai@wwu.de',
    install_requires=package_list,
    scripts=[],
    packages=find_packages(),
    description='A package that provides estimation methods for differential equations of dynamical systems based on timeseries data.',
    long_description=long_description,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Physics'
        ])
