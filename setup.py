from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='PieRakNet',
    version='1.0.0-Beta',
    author='lapismyt',
    author_email='nikitagavrilin005@gmail.com',
    description='RakNet implementation, written in Python. Created for PieMC.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/PieMC-Dev/PieRakNet',
    packages=find_packages(),
    # install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: GPL-3.0 License',
        'Operating System :: OS Independent'
    ],
    keywords='python python3 raknet rak-net mcpe bedrock rak_net',
    project_urls={
        'GitHub': 'https://github.com/PieMC-Dev/PieRakNet',
        'Example': 'https://github.com/PieMC-Dev/PieRakNet/tree/main/EXAMPLE.md',
        'Developer': 'https://github.com/PieMC-Dev'
    },
    python_requires='>=3.10'
)
