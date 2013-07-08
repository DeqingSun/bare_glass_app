
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import db
import logging

DEFAULT_ADDRESS_BOOK_NAME = 'default_addressbook'


def addressbook_key(addressbook_name=DEFAULT_ADDRESS_BOOK_NAME):
    """Constructs a Datastore key for a Addressbook entity with addressbook_name."""
    return db.Key.from_path('Addressbook', addressbook_name)


class Address_pair(db.Model):
    address = db.StringProperty()
    userid = db.StringProperty()

def set_addr_id(addr,id):                  
    memcache.set('ADDR of ' + id , addr)
    memcache.set('ID of ' + addr , id)
    q=Address_pair.all().ancestor(addressbook_key(DEFAULT_ADDRESS_BOOK_NAME))
    q.filter('userid =', id)
    entity = q.get()
    if entity is not None:
        entity.address = addr
        entity.put()
    else:
        address_pair = Address_pair(parent=addressbook_key(DEFAULT_ADDRESS_BOOK_NAME))
        address_pair.address = addr
        address_pair.userid = id
        address_pair.put()

def get_addr_from_id(id):
    addr=memcache.get('ADDR of ' + id)
    if addr is not None:
        return addr
    else:
        q=Address_pair.all().ancestor(addressbook_key(DEFAULT_ADDRESS_BOOK_NAME))
        q.filter('userid =', id)
        entity = q.get()
        if entity is not None:
            addr = entity.address
        else:
            addr = None        
        memcache.set('ADDR of ' + id , addr)
        return addr
