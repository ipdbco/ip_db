![ip_db (IP_Database)](img/ip_database_350x350.png?raw=true "ip_db")

A Python 3 module to manage IP address databases used for resolving geolocation and detecting IP address threat. ip_db uses freely available databases.

## Features

- Free
- Auto Updating
- Asynchronous
- Detect Tor IP address

## Requirements

- Python 3.6+
- Internet Connection (to pull down databases)

## Installation

### Manual Installation

Install Python 3.6+ from https://www.python.org/downloads/

Install Python package manager [pip](https://pip.pypa.io/en/stable/installing/) 

Clone this repo:
```bash
git clone https://github.com/ipdbco/ip_db
```

Install using setuptools
```bash
python setup.py  install
```


## Usage

### Importing and using module
```python
import ip_db

# initialize ip_db object
db = ip_db.ip_db()

# start update loop to pull down necessary databases
# this step takes ~ 20-50 seconds depending on network speed.
db.run_async_loop()

# get information about an IP address such as city, country, and
# if it is a tor exit node
db.get_ip("1.1.1.1")
```

Example output `1.1.1.1`
```javascript
{'city': {'geoname_id': 2151718, 'names': {'en': 'Research'}},
 'continent': {'code': 'OC',
  'geoname_id': 6255151,
  'names': {'de': 'Ozeanien',
   'en': 'Oceania',
   'es': 'Oceanía',
   'fr': 'Océanie',
   'ja': 'オセアニア',
   'pt-BR': 'Oceania',
   'ru': 'Океания',
   'zh-CN': '大洋洲'}},
 'country': {'geoname_id': 2077456,
  'iso_code': 'AU',
  'names': {'de': 'Australien',
   'en': 'Australia',
   'es': 'Australia',
   'fr': 'Australie',
   'ja': 'オーストラリア',
   'pt-BR': 'Austrália',
   'ru': 'Австралия',
   'zh-CN': '澳大利亚'}},
 'location': {'accuracy_radius': 1000,
  'latitude': -37.7,
  'longitude': 145.1833,
  'time_zone': 'Australia/Melbourne'},
 'postal': {'code': '3095'},
 'registered_country': {'geoname_id': 2077456,
  'iso_code': 'AU',
  'names': {'de': 'Australien',
   'en': 'Australia',
   'es': 'Australia',
   'fr': 'Australie',
   'ja': 'オーストラリア',
   'pt-BR': 'Austrália',
   'ru': 'Австралия',
   'zh-CN': '澳大利亚'}},
 'subdivisions': [{'geoname_id': 2145234,
   'iso_code': 'VIC',
   'names': {'en': 'Victoria', 'pt-BR': 'Vitória', 'ru': 'Виктория'}}],
 'threat': {'is_tor': False}
}
```

Example output `8.8.8.8`
```javascript
{'continent': {'code': 'NA',
  'geoname_id': 6255149,
  'names': {'de': 'Nordamerika',
   'en': 'North America',
   'es': 'Norteamérica',
   'fr': 'Amérique du Nord',
   'ja': '北アメリカ',
   'pt-BR': 'América do Norte',
   'ru': 'Северная Америка',
   'zh-CN': '北美洲'}},
 'country': {'geoname_id': 6252001,
  'iso_code': 'US',
  'names': {'de': 'USA',
   'en': 'United States',
   'es': 'Estados Unidos',
   'fr': 'États-Unis',
   'ja': 'アメリカ合衆国',
   'pt-BR': 'Estados Unidos',
   'ru': 'США',
   'zh-CN': '美国'}},
 'location': {'accuracy_radius': 1000,
  'latitude': 37.751,
  'longitude': -97.822},
 'registered_country': {'geoname_id': 6252001,
  'iso_code': 'US',
  'names': {'de': 'USA',
   'en': 'United States',
   'es': 'Estados Unidos',
   'fr': 'États-Unis',
   'ja': 'アメリカ合衆国',
   'pt-BR': 'Estados Unidos',
   'ru': 'США',
   'zh-CN': '美国'}},
 'threat': {'is_tor': False}
}
 ```


## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## History

init: Initial Commit

## Credits

[Torproject](https://torproject.org): Tor database

[Maxmind](https://www.maxmind.com/en/geoip2-databases): Maxmind database

[tuangeek](https://github.com/tuangeek): initial coder

## License

[License](license): GNU General Public License v3.0
