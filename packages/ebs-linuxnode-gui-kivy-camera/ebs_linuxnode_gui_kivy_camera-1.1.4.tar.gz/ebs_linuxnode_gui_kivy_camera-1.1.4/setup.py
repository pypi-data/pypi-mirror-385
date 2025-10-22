import setuptools

_requires = [
    'setuptools-scm',
    'kivy_garden.ebs.camera>=1.2.0',
    'ebs-linuxnode-camera>=1.1.3',
    'ebs-linuxnode-gui-kivy-core>=2.0',
]

setuptools.setup(
    name='ebs-linuxnode-gui-kivy-camera',
    url='https://github.com/ebs-universe/ebs-linuxnode-kivy-camera',

    author='Chintalagiri Shashank',
    author_email='shashank.chintalagiri@gmail.com',

    description='Camera infrastructure for linuxnode applications',
    long_description='',

    packages=setuptools.find_packages(),
    install_requires=_requires,

    setup_requires=['setuptools_scm'],
    use_scm_version=True,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
    ],
)
