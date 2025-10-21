import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="signalrcore1",
    version="1.1.6",
    author="sipanohanyan",
    author_email="sipanohanyan@gmail.com",
    description="A Python SignalR Core client(json and messagepack), with invocation auth and two way streaming. Compatible with azure / serverless functions. Also with automatic reconnect and manually reconnect.",
    keywords="signalr core client 3.1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license_file="LICENSE",
    url="https://github.com/mandrewcito/signalrcore",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.14"
    ],
    install_requires=[
        "requests>=2.32.3",
        "websocket-client>=1.9.0",
        "msgpack==1.1.0"
    ]
)
