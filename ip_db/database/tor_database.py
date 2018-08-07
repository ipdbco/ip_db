#! /usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import requests
from dateutil import parser
from .database import Database
 
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

    def get_ip(self, ip):
        if self.db:
            result = {'is_tor' : ip in self.db}
            return result
        else:
            return {}

