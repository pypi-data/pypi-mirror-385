from setuptools import setup, find_packages

setup(
    name='pyparti',
    version='0.1',
    packages=find_packages(),
    description='Pareto Task Inference Analysis (ParTI) in Python',
    author='ggit12',
    # author_email='your.email@example.com',
    license='BSD-3-Clause',
    install_requires=[
        # list of packages this package depends on
        'anndict @ git+https://github.com/ggit12/anndictionary.git',
        'lib_unmixing @ git+https://github.com/ggit12/lib_unmixing.git',
    ],
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.org/classifiers/
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    include_package_data=True,  # Ensures data files are included
    package_data={
        # Include all CSV files in the `dat` folder within the `pyparti` package
        'pyparti': ['dat/*.csv'],
    },
)
