#~ syncAgent.py ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Stablish a connection with the server providing it the crawled files.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Modules ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import json
import utils
from httplib import HTTPConnection
from httplib import HTTPSConnection
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SyncAgent(object):
    def __init__(self, host, user_token, device_token):
        if not utils.test_value('url', host, ['IGNORECASE']):
            raise AssertionError('Invalid host')

        if not utils.test_value('token', user_token):
            raise AssertionError('Wrong user token')

        if not utils.test_value('token', device_token):
            raise AssertionError('Wrong device token')

        self.host = host
        self.user_token = user_token
        self.device_token = device_token

    def __build_connection(self):
        if self.host.find('https') >= 0:
            return HTTPSConnection(self.host[8:])

        elif self.host.find('http') >= 0:
            return HTTPConnection(self.host[7:])

        return HTTPConnection(self.host)

    def __build_request(self, new_resources):
        return {
            'body': json.dumps({
                'user-token': self.user_token,
                'device-token': self.device_token,
                'new-resources': new_resources,
            }),
            'headers': {
                'content-type': 'application/json',
            },
            'method': 'POST',
            'url': '/sync',
        }

    def sync(self, new_resources):
        assert isinstance(new_resources, list)

        connection = self.__build_connection()

        try:
            connection.request(**self.__build_request(new_resources))

        except Exception as new_exception:
            raise new_exception

        else:
            connection.getresponse().read()

        finally:
            connection.close()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    sync_agent = SyncAgent('https://omnitag.herokuapp.com', '2|b66140414104ead8bbb4', '2|b66140414104ead8bbb4')
    sync_agent.sync([])
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
