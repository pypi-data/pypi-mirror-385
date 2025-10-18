from setuptools import setup, find_packages

VERSION = '0.1.1' 
DESCRIPTION = 'CodeBase of important Functions'
LONG_DESCRIPTION = 'Contains Pytorch/ TensorFlow algorithms I have found in a single module'

# Setting up
setup(
        name="dycomutils", 
        version=VERSION,
        author="Devin De Silva",
        author_email="desild@rpi.edu",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'codebase'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3.9",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)