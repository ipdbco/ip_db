from .database import tor_database
from .database import maxmind_database
from threading import Thread
import asyncio
import time

name = "ip_db"

class ip_db(object):
    '''
    Main class to start and query the ip dataase.
    
    The databases are all async because the update themselves
    in the background. This class is use to combine the
    databases and wrap then into synchronous functions.

    '''
    def __init__(self):
        self.tor_db = tor_database.TorDatabase()
        self.maxmind_db = maxmind_database.MaxmindDatabase()
        self.is_ready = False

    def async_loop_worker(self, loop):
        asyncio.set_event_loop(loop)
        tasks = [loop.create_task(self.tor_db.auto_update_loop()),
            loop.create_task(self.maxmind_db.auto_update_loop())]
        loop.run_until_complete(asyncio.wait(tasks))

    def run_async_loop(self):
        new_loop = asyncio.new_event_loop()
        t = Thread(target=self.async_loop_worker, args=(new_loop,))
        t.daemon = True
        t.start()

        # wait for all the database to finish downloading
        while True: 
            downloaded = [self.tor_db.db, self.maxmind_db.db]
            time.sleep(1)
            if all(downloaded):
                self.is_ready = True
                break
        
        print("Finished downloading databases.")

    def get_ip(self, ip):
        '''
        query all databases for ip address.
        :return:dict: a dictionary of the results
        '''
        if self.is_ready:
            results = self.maxmind_db.get_ip(ip)
            results['threat'] = self.tor_db.get_ip(ip)
            return results
        else:
            return {}
