#!/usr/bin/python
#
# Copyright (c) 2013 - 2015, Bob Arnott
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from pymongo import MongoClient
import requests

# Your Untappd details...
untappd_user = ''
untappd_client_id = ''
untappd_client_secret = ''

# Connect to the local MongoDB instance...
client = MongoClient()
db = client[untappd_user]

# Does the user have any checkins already...?
if 'checkins' in db.collection_names():
    print 'Dropping previously slurped checkins...'
    db.drop_collection('checkins')

# Create a new collection so we can slurp checkins into it...
checkins = db.create_collection('checkins')

# We don't have any checkin info at the moment, so don't set the checkin max_id
max_id = None

# Connect to Untappd and pull down some checkins...
while True:
    # These are the parameters we send every time...
    parameters = {'client_id': untappd_client_id, 'client_secret': untappd_client_secret, 'limit': 50}

    # Each time we go round the loop apply the max_id...
    if max_id != None:
        parameters['max_id'] = max_id

    # Get some checkins...
    r = requests.get('http://api.untappd.com/v4/user/checkins/' + untappd_user, params=parameters)
    json = r.json()

    if json['meta']['code'] == 200:
        # Update the max_id...
        max_id = json['response']['pagination']['max_id']

        # Load the checkins into mongo...
        checkins.insert(json['response']['checkins']['items'])

        # If we didn't get 50 checkins then we're done, so break out...
        count = json['response']['checkins']['count']
        print "Inserting %i checkins into mongo..." % count
        if count < 50:
            break
    else:
        print json['meta']['error_detail']
        break

print "%s now has %i Untappd checkins in MongoDB..." % (untappd_user, checkins.count())
