"""
TOV Extravaganza - Python toolkit for solving TOV equations and computing neutron star properties
"""

from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import sys


class PostInstallCommand(install):
    """Post-installation message"""
    def run(self):
        install.run(self)
        print("\n" + "="*70)
        print("  TOV Extravaganza v1.0.1 - Successfully Installed!")
        print("="*70)
        print("\n  Quick Start (3 commands):")
        print("    1. tovx-demo              # Get example EOS files")
        print("    2. tovx-wizard            # Interactive guided workflow")
        print("    OR")
        print("    2. tovx inputCode/hsdd2.csv  # Direct analysis")
        print("\n  Console Commands Available:")
        print("    • tovx-demo       - Get example files")
        print("    • tovx            - Main TOV + Tidal solver")
        print("    • tovx-radial     - Generate radial profiles")
        print("    • tovx-converter  - Convert EOS units")
        print("    • tovx-wizard     - Interactive wizard")
        print("\n  Documentation:")
        print("    • README: https://github.com/PsiPhiDelta/TOVExtravaganza")
        print("    • Usage: Run 'tovx --help' or 'tovx-wizard'")
        print("\n  Citation:")
        print("    • Software: DOI 10.5281/zenodo.xxxxx")
        print("    • Paper: arXiv:2411.04064")
        print("\n  Oh boy oh boy! Happy computing!")
        print("="*70 + "\n")

# Read the README for long description
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

setup(
    name='tovextravaganza',
    version='1.0.1',
    author='Hosein Gholami',
    author_email='mohogholami@gmail.com',
    description='Python toolkit for solving the Tolman-Oppenheimer-Volkoff (TOV) equations and exploring neutron star properties',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/PsiPhiDelta/TOVExtravaganza',
    project_urls={
        'Bug Reports': 'https://github.com/PsiPhiDelta/TOVExtravaganza/issues',
        'Source': 'https://github.com/PsiPhiDelta/TOVExtravaganza',
        'Documentation': 'https://github.com/PsiPhiDelta/TOVExtravaganza#readme',
    },
    packages=find_packages(exclude=['tests', 'docs', 'maxwellConstructorEoS', 'ToCSV']),
    package_data={
        'tovextravaganza': ['inputCode/*.csv'],
    },
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.19.0',
        'scipy>=1.5.0',
        'matplotlib>=3.3.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'tovx=tov:main',
            'tovx-radial=radial:main',
            'tovx-converter=converter:main',
            'tovx-wizard=tov_wizard:main',
            'tovx-demo=demo:main',
        ],
    },
    py_modules=['tov', 'radial', 'converter', 'tov_wizard', 'demo'],
    cmdclass={
        'install': PostInstallCommand,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Astronomy',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    keywords='neutron-stars tov equation-of-state tidal-deformability gravitational-waves astrophysics',
    license='MIT',
)

