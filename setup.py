from distutils.core import setup

setup(
    name='auction-keeper',
    version='1.0.0',
    packages=[
        'auction_keeper',
    ],
    url='https://github.com/captain13128/auction-keeper',
    license='',
    author='',
    author_email='',
    description='',
    install_requires=[
        # "-e git+https://install-utils-user:mYmm%x|8KorJbyS3dxf@github.com/captain13128/pymaker.git#egg=pymaker",
        # "-e git+https://install-utils-user:mYmm%x|8KorJbyS3dxf@github.com/captain13128/pygasprice-client.git#egg=pygasprice-client",
        "forex_python",
        "ccxt",
    ]
)
