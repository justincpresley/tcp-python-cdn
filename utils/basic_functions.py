import requests
import os
from urllib.parse import urljoin, urlparse
import time
import re
import contextlib
import mmap

# directory functions
def delete_file_in_cwd(filename):
    if os.path.isfile(filename):
        os.remove(filename)

# ip functions
regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$'''

def validate_ip(ip):
    if(re.search(regex, ip)):
        return True
    else:
        return False

# url functions
def make_proper_url(url):
    result = rid_params_of_url(url)
    return ensure_http_url(result)
def validate_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)
def rid_params_of_url(url):
    parse = urlparse(url)
    if not parse.path.endswith(('/feed/', '.png', '.jpg', '.gif')):
        return urljoin(url, parse.path)
    else:
        return url
def ensure_http_url(url):
    parse = urlparse(url)
    if not re.match(r'^[a-zA-Z]+://', url):
        return parse._replace(**{"scheme": "http"}).geturl().replace('///', '//')
    else:
        return url
def download_url(url, filename):
    response = requests.head(url)
    try:
        content_type = response.headers.get('Content-Type').split(';')[0]
    except:
        content_type = None

    if content_type == 'text/html' or content_type == None:
        response = requests.get(url)
        with open(filename, mode='w', encoding='utf-8') as cache:
            cache.write(response.text)
    else:
        print('Ignoring non-HTML content type "{}"'.format(content_type))

# byte functions
def how_many_chunks_in_file(filename, chunk_size=88):
    num_bytes = get_num_bytes_from_file(filename)
    num_chunks = num_bytes//chunk_size
    if num_bytes%chunk_size!=0:
        num_chunks += 1
    return num_chunks
def read_bytes_chunk_from_file(filename, chunk_size=88, chunk=0):
    curr_chunk = 0
    memory = b''
    with open(filename, 'r+') as f:
        with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)) as m:
            while curr_chunk<chunk+1:
                memory = m.read(chunk_size)
                curr_chunk += 1
    return memory
def get_num_bytes_from_file(filename):
    return len(bytes(open(filename, "rb").read()))
def push_bytes_to_file(filename, bytes):
    f = open(filename, 'ab')
    f.seek(0, os.SEEK_END)
    f.write(bytearray(bytes))
    f.close()