from datetime import datetime
#from tempfile import TemporaryFile
import tarfile
import requests
import logging
import asyncio
import io
import maxminddb
from .database import Database

class MaxmindDatabase(Database):

    UPDATE_URL = 'https://ipdb-d6756.firebaseio.com/database/maxmind.json'

    def __init__(self, database_type = 'lite_city'):
        super().__init__()
        self.database_type = database_type
        self.UPDATE_DELAY = 60*60*24 # once a day

    async def start(self):
        '''
        The necessary startup function to start the database
        '''
        info = await self.get_update_info()
        self.md5 = info[self.database_type]['md5']
        self.download_link = info[self.database_type]['download']
        self.last_updated = info[self.database_type]['generated_on']
        await self.download()

    async def get_update_info(self):
        '''
        Get the information about the latest version of the database such as
        md5, download link, and time of generation.

        :return:dictionary: a dict with information about the latest copy of
        the database.t
        '''
        info = requests.get(self.UPDATE_URL).json()
        return info

    async def auto_update_loop(self):
        '''
        A infinite loop to check for updates and automatically update the database.
        Consider this the main of the database. Just call this in a async loop.
        '''
        missing = [not self.db, not self.last_updated, not self.md5, not self.download_link]
        if any(missing):
            await self.start()

        self.logger.info("Starting maxmind database update loop")
        while True:
            # get the latest update info
            update_info = await self.get_update_info()
            latest_md5 = update_info[self.database_type]['md5']
            latest_last_updated = update_info[self.database_type]['generated_on']
            latest_download_link = update_info[self.database_type]['download']
            
            # compare md5 to see if file has changed, if different set the
            # new attribute values and download the new database
            if self.md5 != latest_md5:
                # set the attribute
                self.download_link = latest_download_link
                self.md5 = latest_md5
                self.last_updated = latest_last_updated
                await self.download()

            self.logger.debug("Maxmind {0} database update loop sleeping for {1} hour".format(
                self.database_type, self.UPDATE_DELAY/60/60))
            await asyncio.sleep(self.UPDATE_DELAY)

    async def download(self):
        '''
        Takes care of downloading, parsing, and setting setting the self.db according
        to the type of database
        '''
        self.logger.info("Downloading Maxmind {} database.".format(self.database_type))
        resp = requests.get(self.download_link)
        db_content = await self.untar_mmdb(resp)
        self.db = await self.parse_mmdb(db_content)
        
    async def untar_mmdb(self, resp):
        '''
        untar the download and extract the .mmdb file
        :param:resp: response from downloading the .tar.gz
        :return: content of .mmdb file in bytes array
        '''
        mmdb_content = None
        self.logger.info("Un-taring .tar.gz")
        tar = tarfile.open(fileobj=io.BytesIO(resp.content))
        for member in tar.getmembers():
            if '.mmdb' in member.name:
                mmdb_content = tar.extractfile(member).read()
        tar.close()
        return mmdb_content

    async def parse_mmdb(self, mmdb):
        '''
        create and return mmdb reader of the mmdb
        :param:mmdb: the byte array of the .mmdb file
        '''
        # maminddb expects a file or file descriptor, 
        # use Tempfile to createa a file pointer
        '''
        tfile = TemporaryFile()
        tfile.write(mmdb)
        # after writing must seek back to the begggining
        tfile.seek(0)
        reader = maxminddb.open_database(tfile, mode=maxminddb.MODE_MMAP_EXT)
        tfile.close()
        '''
        temp_file = '/tmp/maxmin.db'
        with open(temp_file, 'wb+') as tf:
            tf.write(mmdb)
        reader = None
        try:
            reader = maxminddb.open_database(temp_file, mode=maxminddb.MODE_MMAP_EXT)
        except:
            reader = maxminddb.open_database(temp_file)
        return reader

    def get_ip(self, ip):
        '''
        Function to look up the ip address using the appropriate methods for self.db.

        :param:ip:string: string representation of the IP address e.g "127.0.0.1"
        '''
        if self.db:
            return self.db.get(ip)
        else:
            return {}
 
