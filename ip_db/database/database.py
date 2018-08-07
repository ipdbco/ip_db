import logging
import asyncio

class Database(object):
    '''
    Base database class. Server as a interface for suggested functions that various
    database should implement. All class that inherit should override the functions.

    **                                                                      **
        DO NOT USE BASE CLASS. ALL FUNCTIONS WILL RAISE NotImplementedError
    **                                                                      **
    '''

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = None
        self.md5 = None
        self.download_link = None
        self.last_updated = None
        self.UPDATE_DELAY = 60 * 60 # 3600 seconda = 1 hour

    async def start(self):
        '''
        The necessary startup function to start the database
        '''
        raise NotImplementedError

    async def get_update_info(self):
        '''
        Get the information about the latest version of the database such as
        md5, download link, and time of generation.

        :return:dictionary: a dict with information about the latest copy of
        the database.t
        '''
        raise NotImplementedError

    async def auto_update_loop(self):
        '''
        A infinite loop to check for updates and automatically update the database.
        Consider this the main of the database. Just call this in a async loop.
        '''
        raise NotImplementedError

    async def download(self):
        '''
        Takes care of downloading, parsing, and setting setting the self.db according
        to the type of database
        '''
        raise NotImplementedError

    async def get_ip(self, ip):
        '''
        Function to look up the ip address using the appropriate methods for self.db.

        :param:ip:string: string representation of the IP address e.g "127.0.0.1"
        '''
        raise NotImplementedError
    
class TorDatabase(Database):
    '''
    class to manage the tor node database
        usage:
            tordb = TorDatabase()
            tordb.auto_update()
    '''

    UPDATE_URL = 'https://ipdb-d6756.firebaseio.com/database/tor.json'

    def __init__(self):
        super().__init__()
        self.UPDATE_DELAY = 60*60 # one hour

    async def start(self):
        self.logger.info("Initalizing tor database")
        update_info = await self.get_update_info()
        # get the information about the database
        self.download_link = update_info['download']
        self.md5 = update_info['md5']
        self.last_updated = update_info['generated_on']
        await self.download()

    async def get_update_info(self):
        # get info about the database
        resp = requests.get(self.UPDATE_URL)
        return resp.json()
                    
    async def download(self):
        self.logger.info("Downloading latest tor database")
        # the tor database from downlink provided from ipdb.co is in the format of
        # a list if ipv4:port in a text file
        text = requests.get(self.download_link).text
        ips = text.split('\n')
        self.db = ips
         
    async def auto_update_loop(self):
        '''
        continuesly update every UPDATE_DELAY time interval and poll for changes.
        '''
        # start the database if any of the attributes are missing
        missing = [not self.db, not self.last_updated, not self.md5, not self.download_link]
        if any(missing):
            await self.start()
         
        self.logger.info("Starting tor database update loop")
        while True:
            # get the latest update info
            update_info = await self.get_update_info()
            latest_md5 = update_info['md5']
            latest_last_updated = update_info['generated_on']
            latest_download_link = update_info['download']
            
            # compare md5 to see if file has changed, if different set the
            # new attribute values and download the new database
            if self.md5 != latest_md5:
                # set the attribute
                self.download_link = latest_download_link
                self.md5 = latest_md5
                self.last_updated = latest_last_updated
                await self.download()

            self.logger.debug("Tor database update loop sleeping for {} minutes".format(self.UPDATE_DELAY/60))
            await asyncio.sleep(self.UPDATE_DELAY)

    async def get_ip(self, ip):
        result = {'is_tor' : ip in self.db}
        return result

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
        tfile = TemporaryFile()
        tfile.write(mmdb)
        # after writing must seek back to the begggining
        tfile.seek(0)
        reader = maxminddb.open_database(tfile, mode=maxminddb.MODE_FD)
        tfile.close()
        return reader

    async def get_ip(self, ip):
        '''
        Function to look up the ip address using the appropriate methods for self.db.

        :param:ip:string: string representation of the IP address e.g "127.0.0.1"
        '''
        return self.db.get(ip)
 
