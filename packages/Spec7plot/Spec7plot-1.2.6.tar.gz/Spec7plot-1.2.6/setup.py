from setuptools import setup, find_packages

setup(
    name='Spec7plot',
    version='1.2.6',
    description='Spectral figure plotting package for 7-Dimensional Telescope users by Won-Hyeong Lee',
    author='Won-Hyeong Lee',
    author_email='wohy1220@gmail.com',
    url='https://github.com/Yicircle/Spec7plot',
    install_requires=[
        'numpy',
        'astropy',
        'matplotlib',
        'seaborn',
        'pathlib',
        'photutils',
        'reproject',
    ],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    keywords=[''],
    python_requires='>=3.10',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
)