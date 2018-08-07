import setuptools

with open("README.md", "rb") as fh:
    long_description = fh.read().decode('utf-8')
with open("LICENSE", "rb") as fh:
    license = fh.read().decode('utf-8')

requirements = [
    'requests',
    'maxminddb'
]

setuptools.setup(
    name="ip_db",
    version="0.0.1",
    author="ipdbco_tuan",
    author_email="41750787+ipdbco@users.noreply.github.com",
    description="A small Python 3 module to manage IP address databases used for resolving geolocation and getting threat information aboutIP address",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ipdbco/ip_db",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3.0",
        "Operating System :: OS Independent",
    ),
    install_requires=requirements,
    license=license,
)
