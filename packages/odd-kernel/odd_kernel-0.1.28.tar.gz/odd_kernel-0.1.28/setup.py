from setuptools import setup, find_packages

setup(
    name='odd_kernel',
    version='0.1.28',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "odd_kernel.util": ["assets/*"],
    },
    install_requires=[
        "pygame",
        "yfinance",
        "pandas",
        "numpy",
    ],
    description='Some wrappers for python utilities.',
    author='OddKernel',
    author_email='odd.kernel.sl@gmail.com',
    url='https://github.com/pereradrian/odd-kernel',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)