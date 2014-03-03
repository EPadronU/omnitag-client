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


#~ Controllers ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form = SettingsForm(request)
        errors = form.validate()
        if not errors: form.update_settings(manager.get('settings'))
        return render_template('index.html', settings=manager.get('settings'), errors=errors)

    return render_template('index.html', settings=manager.get('settings'))


@app.route("/black-list", methods=['GET'])
def render_black_list_entries():
    return jsonify({
        'html': render_template("entries.html", entries=enumerate(manager.get('black-list'))),
    })


@app.route("/black-list", methods=['POST'])
def new_black_list_entry():
    path = request.get_json().get('path', '')

    if path and manager.add_to_black_list(path):
        return jsonify({'status': 'success'}), 200

    return jsonify({'status': 'failure'}), 204


@app.route("/black-list", methods=['DELETE'])
def delete_black_list_entry():
    dirpath = request.get_json().get('entry-path', '')

    if dirpath in manager.get('black-list'):
        manager.get('black-list').remove(dirpath)
        return jsonify({'status': 'success'}), 200

    return jsonify({'status': 'failure'}), 204


@app.route("/explorer", methods=['GET'])
def explorer():
    path = request.args.get('path', os.path.expanduser(u'~'))

    if os.path.exists(path):
        dirnames = filter(
            lambda dirname: os.path.isdir(os.path.join(path, dirname)) and dirname[0] != u'.',
            os.listdir(path)
        )
        dirnames.sort()

        return jsonify({
            'html': render_template(
                "explorer.html",
                dirname=os.path.basename(path),
                dirpath=path,
                directories=((os.path.join(path, dirname), dirname) for dirname in dirnames),
                parent=os.path.dirname(path),
            ),
            'status': 'success',
        }), 200

    else:
        return jsonify({
            'message': 'The given path does not exists',
            'status': 'failure',
        }), 404


@app.route("/white-list", methods=['GET'])
def render_white_list_entries():
    return jsonify({
        'html': render_template("entries.html", entries=enumerate(manager.get('white-list'))),
    })


@app.route("/white-list", methods=['POST'])
def new_white_list_entry():
    path = request.get_json().get('path', '')

    if path and manager.add_to_white_list(path):
        return jsonify({'status': 'success'}), 200

    return jsonify({'status': 'failure'}), 204


@app.route("/white-list", methods=['DELETE'])
def delete_white_list_entry():
    dirpath = request.get_json().get('entry-path', '')

    if dirpath in manager.get('white-list'):
        manager.get('white-list').remove(dirpath)
        return jsonify({'status': 'success'}), 200

    return jsonify({'status': 'failure'}), 204
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~ Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    manager.start_backup_daemon()
    manager.start_sync_daemon()

    host, port = manager.get('settings')['client'].split(':')
    app.run(host, int(port), use_reloader=False)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
