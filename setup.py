from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()


setup(
    name='PieRakNet',
    version='1.0.7',
    author='lapismyt',
    author_email='PieMC.Developers@gmail.com',
    description='RakNet implementation, written in Python. Created for PieMC.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/PieMC-Dev/PieRakNet',
    packages=find_packages(),
    # install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking'
    ],
    keywords='python python3 raknet rak-net mcpe bedrock rak_net piemc pieraknet',
    project_urls={
        'Example': 'https://github.com/PieMC-Dev/PieRakNet/tree/main/EXAMPLE.md',
        'Developer': 'https://github.com/PieMC-Dev'
    },
    python_requires='>=3.10'
)
