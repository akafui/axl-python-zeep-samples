"""AXL <removeLine>, <removePhone>, <removeUser> sample script, using the zeep library

Install Python 3.7
On Windows, choose the option to add to PATH environment variable

If this is a fresh installation, update pip (you may need to use `pip3` on Linux or Mac)

    $ python -m pip install --upgrade pip

Script Dependencies:
    lxml
    requests
    zeep

Dependency Installation:

    $ pip install zeep

This will install automatically all of zeep dependencies, including lxml, requests

Copyright (c) 2018 Cisco and/or its affiliates.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth

from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.plugins import HistoryPlugin
from zeep.exceptions import Fault

# The WSDL is a local file
WSDL_FILE = 'schema/AXLAPI.wsdl'

# Configure CUCM location and AXL credentials in creds.py
import creds

# Change to true to enable output of request/response headers and XML
DEBUG = False

# If you have a pem file certificate for CUCM, uncomment and define it here

#CERT = 'some.pem'

LINEDN = '1111'
PHONEID = 'SEP151515151515'
USERFNAME = 'johnq'
USERLNAME = 'public'
USERPASS = 'public'

# This class lets you view the incoming and outgoing http headers and/or XML
class MyLoggingPlugin( Plugin ):

    def egress( self, envelope, http_headers, operation, binding_options ):
        print(
'''Request
-------
Headers:
{headers}

Body:
{xml}

'''.format( headers = http_headers, 
            xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode') )
        )

    def ingress( self, envelope, http_headers, operation ):
        print('\n')
        print(
'''Response
-------
Headers:
{headers}

Body:
{xml}

'''.format( headers = http_headers, 
            xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode' ) )
        )


session = Session()

# We avoid certificate verification by default, but you can uncomment and set
# your certificate here, and comment out the False setting

#session.verify = CERT
session.verify = False
session.auth = HTTPBasicAuth( creds.USERNAME, creds.PASSWORD )

# Create a Zeep transport and set a reasonable timeout value
transport = Transport( session = session, timeout = 10 )

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings( strict=False, xml_huge_tree=True )

# If debug output is requested, add the MyLoggingPlugin callback
plugin = [ MyLoggingPlugin() ] if DEBUG else [ ]

# Create the Zeep client with the specified settings
client = Client( WSDL_FILE, settings = settings, transport = transport,
        plugins = plugin )

# service = client.create_service("{http://www.cisco.com/AXLAPIService/}AXLAPIBinding", CUCM_URL)
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                'https://{cucm}:8443/axl/'.format( cucm = creds.CUCM_ADDRESS ))

line_data = {
    'pattern' : LINEDN
}

try:
	line_resp = service.removeLine(**line_data)
except Fault as err:
	print( '\nZeep error: {0}'.format( err ) )
else:
	l = line_resp
	print( '\nremoveLine response:\n' )
	print( l, '\n')

phone_data = {
    'name': PHONEID
}

try:
	phone_resp = service.removePhone(**phone_data)
except Fault as err:
	print( '\nZeep error: {0}'.format( err ) )
else:
	p = phone_resp
	print( '\nremovePhone response:\n' )
	print( p, '\n' )

user_data = {
    'userid': USERFNAME
}

try:
	user_resp = service.removeUser(**user_data)
except Fault as err:
	print( '\nZeep error: {0}'.format( err ) )
else:
	u = user_resp
	print( '\nremoveUser response:\n' )
	print( u, '\n' )
