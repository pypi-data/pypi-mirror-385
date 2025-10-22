import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyBacmman",
    version="0.6.5",
    author="Jean Ollion",
    author_email="jean.ollion@polytechnique.org",
    description="Utilities for analysis of data generated from bacmman software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeanollion/PyBacmman.git",
    download_url = 'https://github.com/jeanollion/PyBacmman/archive/v0.6.4.tar.gz',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        "Operating System :: OS Independent",
    ],
    keywords = ['bacmman', 'pandas', 'data analysis'],
    python_requires='>=3',
    install_requires=['py4j', 'pandas']

)
