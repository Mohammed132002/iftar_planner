import json
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

# the address is fixed in the program, the user never types it
BASE_URL = 'http://127.0.0.1:5050'
TIMEOUT = 5


class ServerError(Exception):
    """One clear message for the window, whatever went wrong."""


class DishClient:
    """Sends the HTTP requests of the window to Flask."""

    def request(self, path, values=None):
        # without data urlopen sends GET, with data it sends POST
        data = None
        if values is not None:
            data = urlencode(values).encode('utf-8')

        try:
            with urlopen(BASE_URL + path, data=data, timeout=TIMEOUT) as reply:
                return json.loads(reply.read().decode('utf-8'))

        except HTTPError as error:
            # Flask answered with 400 or 404, its JSON is in error.read()
            try:
                body = json.loads(error.read().decode('utf-8'))
                message = body['error']
            except (ValueError, KeyError):
                message = 'The server answered with status ' + str(error.code) + '.'
            raise ServerError(message)

        except socket.timeout:
            raise ServerError('The server took too long to answer. Try again.')

        except URLError as error:
            # a timeout while connecting arrives wrapped inside URLError
            if isinstance(error.reason, socket.timeout):
                raise ServerError('The server took too long to answer. Try again.')
            raise ServerError('Cannot reach the server. Start Flask, then try again.')

        except ValueError:
            # json.loads failed, so the reply was not JSON
            raise ServerError('The server sent an unreadable reply.')

    def list_dishes(self):
        # GET: the list of dictionaries
        return self.request('/dishes')['dishes']

    def total(self):
        # GET: the total estimated cost
        return self.request('/dishes/total')['total']

    def add(self, name, category, cost):
        # POST: returns the reply with the message and the new record
        values = {'name': name, 'category': category, 'cost': cost}
        return self.request('/dishes/add', values)

    def edit(self, dish_id, name, category, cost):
        # POST: the id says which dish to change
        values = {'id': dish_id, 'name': name, 'category': category, 'cost': cost}
        return self.request('/dishes/edit', values)

    def delete(self, dish_id):
        # POST: the id says which dish to delete
        return self.request('/dishes/delete', {'id': dish_id})
