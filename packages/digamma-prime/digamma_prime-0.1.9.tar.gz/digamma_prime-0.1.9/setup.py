from setuptools import setup, find_packages

setup(
    name='digamma_prime',
    version='0.1.9',
    packages=find_packages(include=["epe_maria", "epe_maria.*"]),
    install_requires=[
        'sympy',
        'numpy',
        'matplotlib'
    ],
    author='Cerene Salt',
    author_email='letskikyou@email.com',
    description='Symbolic audit engine for divergence detection and structural analysis',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Cerene-Salt/Digamma-Prime-Framework',
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
    license='MIT'
)
