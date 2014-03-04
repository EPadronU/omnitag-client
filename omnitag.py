#!/usr/bin/env python

#~ omnitag.py ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# System's main file.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Modules ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from fso import utils
from fso import manager
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Global configuration ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
DEBUG = True
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Main initialization ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
app = Flask(__name__)
app.config.from_object(__name__)
manager = manager.Manager()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SettingsForm(object):
    def __init__(self, request):
        self.user_token = request.form.get('user-token')
        self.device_token = request.form.get('device-token')
        self.client = request.form.get('client')
        self.server = request.form.get('server')
        self.backup_interval = request.form.get('backup-interval')
        self.sync_interval = request.form.get('sync-interval')

    def validate(self):
        errors = []

        if not self.user_token or not utils.test_value('token', self.user_token):
            errors.append('Please, introduce a valid user token')

        if not self.device_token or not utils.test_value('token', self.device_token):
            errors.append('Please, introduce a valid device token')

        if not self.client or not utils.test_value('url', self.client):
            errors.append('Please, introduce a valid URL for the client')

        if not self.server or not utils.test_value('url', self.server):
            errors.append('Please, introduce a valid URL for the server')

        if not self.backup_interval or not self.backup_interval.isdigit():
            errors.append('Bad backup interval')

        if not self.sync_interval or not self.sync_interval.isdigit():
            errors.append('Bad sync interval')

        return errors

    def update_settings(self, settings):
        settings['user-token'] = self.user_token
        settings['device-token'] = self.device_token
        settings['client'] = self.client
        settings['server'] = self.server
        settings['backup']['interval'] = int(self.backup_interval)
        settings['sync']['interval'] = int(self.sync_interval)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def delete_from_list(dirpath, dirlist):
    assert isinstance(dirpath, str) or isinstance(dirpath, unicode)
    assert isinstance(dirlist, set)

    if dirpath and dirpath in dirlist:
        dirlist.remove(dirpath)
        return '', 200

    return '', 204


def render_list(dirlist):
    assert isinstance(dirlist, set)

    return jsonify({'html': render_template('entries.html', entries=dirlist)})


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Controllers ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form = SettingsForm(request)
        errors = form.validate()
        if not errors: form.update_settings(manager.get('settings'))
        return render_template('index.html', settings=manager.get('settings'), errors=errors)

    return render_template('index.html', settings=manager.get('settings'))


@app.route('/black-list', methods=['GET'])
def render_black_list_entries():
    return render_list(manager.get('black-list'))


@app.route('/black-list', methods=['POST'])
def new_black_list_entry():
    dirpath = request.get_json().get('path')

    if dirpath and manager.add_to_black_list(dirpath):
        return '', 200

    return '', 204


@app.route('/black-list', methods=['DELETE'])
def delete_black_list_entry():
    return delete_from_list(request.get_json().get('entry-path'), manager.get('black-list'))


@app.route('/explorer', methods=['GET'])
def explorer():
    current_dir = request.args.get('path', os.path.expanduser(u'~'))

    if os.path.isdir(current_dir):
        directories = (os.path.join(current_dir, dirname) for dirname in os.listdir(current_dir) if dirname[0] != u'.')
        directories = filter(lambda dirpath: os.path.isdir(dirpath), directories)
        directories.sort()

        return jsonify({
            'html': render_template(
                'explorer.html',
                dirname=os.path.basename(current_dir),
                dirpath=current_dir,
                directories=((dirpath, os.path.basename(dirpath)) for dirpath in directories),
                parent=os.path.dirname(current_dir),
            ),
            'status': 'success',
        }), 200

    return jsonify({'message': 'The given path does not exists', 'status': 'failure'}), 404


@app.route('/white-list', methods=['GET'])
def render_white_list_entries():
    return render_list(manager.get('white-list'))


@app.route('/white-list', methods=['POST'])
def new_white_list_entry():
    dirpath = request.get_json().get('path')

    if dirpath and manager.add_to_white_list(dirpath):
        return '', 200

    return '', 204


@app.route('/white-list', methods=['DELETE'])
def delete_white_list_entry():
    return delete_from_list(request.get_json().get('entry-path'), manager.get('white-list'))


@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'System shutting down...', 200
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    manager.start_backup_daemon()
    manager.start_sync_daemon()

    host, port = manager.get('settings')['client'].split(':')
    app.run(host, int(port), use_reloader=False)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
