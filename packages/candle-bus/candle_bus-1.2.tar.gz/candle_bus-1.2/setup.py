from setuptools import setup, Extension

long_description = open('README.md').read()

setup(
    name='candle_bus',
    version='1.2',
    description='Python Can plugin with windows candle driver.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    maintainer='robottime',
    maintainer_email='lab@robottime.cn',
    author='song',
    author_email='zhaosongy@126.com',
    keywords=['candle', 'python_can', 'can'],
    python_requires='>=3.6',
    license='MIT License',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
    ],
    packages=['candle_bus'],
    ext_modules=[
        Extension(
            "candle_driver",
            sources=[
                "candle_driver/src/py_candle_driver.c",
                "candle_driver/src/py_candle_device.c",
                "candle_driver/src/py_candle_channel.c",
                "candle_driver/src/fifo.c",
                "candle_driver/src/candle_api/candle.c",
                "candle_driver/src/candle_api/candle_ctrl_req.c",
            ],
            include_dirs=['candle_driver/candle_api'],
            libraries=[
                "SetupApi",
                "Ole32",
                "winusb",
            ],
        )
    ],
    install_requires=['python-can>=3.2.0, <4.0'],
    entry_points={
        'can.interface': [
            "candle=candle_bus.candle_bus:CandleBus",
        ]
    },
)
