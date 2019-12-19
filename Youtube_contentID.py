#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import datetime
import csv
import time
from os import listdir
import httplib
import httplib2
import random
import logging
import sys
import optparse
import os
import sys
import shutil
reload(sys)
sys.setdefaultencoding('utf-8')
from mp4file.mp4file import Mp4File
import ffmpy
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow
import smtplib



# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# See the "Registering your application" instructions for an explanation
# of how to find these values:
# https://developers.google.com/youtube/partner/guides/registering_an_application
CLIENT_SECRETS = 'client_secrets.json'
file_name = "C:\Users\Win7 - 1\Desktop\Upload\Uploaded_Live/Record.csv"
location = "C:\Users\Win7 - 1\Desktop\Upload\\news_youtube"


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected, httplib.IncompleteRead, httplib.ImproperConnectionState, httplib.CannotSendRequest, httplib.CannotSendHeader, httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an appiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


# record the status
status="C:\Users\Win7 - 1\PycharmProjects\Upload Video independent\status/youtube.txt"
record = open(status, "w")
record.close()
record = open(status, "a")
record.write("1")
record.close()


# Helpful message to display if the CLIENT_SECRETS file is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you need to populate the client_secrets.json
file found at:

%s

with information from the Developers Console
<https://console.developers.google.com/>.

""" % os.path.join(os.path.dirname(__file__), CLIENT_SECRETS)

# Set up a Flow object to be used if we need to authenticate.
FLOW = flow_from_clientsecrets(CLIENT_SECRETS, scope='https://www.googleapis.com/auth/youtubepartner', message=MISSING_CLIENT_SECRETS_MESSAGE)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())



def _create_asset(service, title, metadata_type):
    metadata = {'title': title }
    asset_body = {'metadata': metadata, 'type': metadata_type}
    # Retrieve asset service.
    asset_service = service.assets()

    # Create and execute insert request.
    request = asset_service.insert(body=asset_body)
    response = request.execute()
    logger.info('Asset has been created.\n%s', response)
    asset_id = response['id']
    return asset_id


def _create_asset_ownership(service, asset_id, owner_name):
    ownership = {
      'owner': owner_name,
      'ratio': 100,
      'type': 'exclude',
      'territories': []}
    ownership_body = {'general': [ownership]}
    ownership_service = service.ownership()

    request = ownership_service.update(assetId=asset_id, body=ownership_body)
    response = request.execute()
    logger.info('Asset ownership has been created.\n%s', response)


def _create_match_policy(service, asset_id):
    match_policy_service = service.assetMatchPolicy()
    everywhere_policy_condition = {
      'requiredTerritories': {
          'type': 'exclude', 'territories': []},
      'requiredReferenceDuration': [{'low': 3}],
      "matchDuration": [{"low": 3,}],
      'contentMatchType': 'audiovideo'}
    track_everywhere_rule = {
      'action': 'block',
      'condition': everywhere_policy_condition}
    request = match_policy_service.update(
      assetId=asset_id,
      body={
        'name': 'API_block news.',
        'description': 'Block Everywhere matches longer than 3s.',
        'rules': [track_everywhere_rule]})
    response = request.execute()
    logger.info('Asset match policy has been created.\n%s', response)


def _create_reference(service, asset_id, reference_file):
    reference_service = service.references()
    media = MediaFileUpload(reference_file, resumable=True)
    request = reference_service.insert(
      body={'assetId': asset_id, 'contentType': 'video'},
      media_body=media)
    response = None
    error = None
    retry = 0
    print "Uploading file..."
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                logger.info("Uploaded %d%%.", int(status.progress() * 100))
        except HttpError, e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS, e:
            error = "A retriable error occurred: %s" % e
        if error is not None:
            print error
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")
            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print "Sleeping %f seconds and then retrying..." % sleep_seconds
            time.sleep(sleep_seconds)
    logger.info('Reference has been created.\n%s', response)
    return response

def main(argv):
    data = {}
    data['video'] = []
    # If the Credentials don't exist or are invalid run through the native client
    # flow. The Storage object ensures that if successful the good
    # Credentials are written back to a file.
    storage = Storage('yt_partner_api.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(FLOW, storage)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)
    path = location
    upath = unicode (path, 'utf-8')
    onlyfiles = listdir(upath)
    service = build("youtubePartner", "v1", http=http)
    i = 0


    #Core of the uploading process
    for no in onlyfiles:
      if no == "Thumbs.db":
          continue
      #try:
      if no.endswith('.mp4') or no.endswith('.ts') or no.endswith('.m4v'):
          print "now trying"
          video = no
          title = no
          id =""
          resp=""
          name = location + '/' + video
          try:
              asset_id = _create_asset(service, title, 'web')
              id = asset_id
              _create_asset_ownership(service, asset_id, "bcBFXLuHhM2coaE_xqXlEQ")
              _create_match_policy(service, asset_id)
              resp = _create_reference(service, asset_id, name)
          except AccessTokenRefreshError:
              logger.info("The credentials have been revoked or expired, please re-run"
                          " the application to re-authorize")
  
          time.sleep(5)
          record = open(file_name, "a")
          a = datetime.date.today()
          b = datetime.datetime.now().strftime("%H:%M:%S")
          info = str(a) + "," + str(b) + "," + str(no) + ", ,1 , , " + str(id) + "," + str(resp)+ ", TVBI ac"
          print >> record, (info)
          record.close()

          print video, "has uploded"
          data['video'].append({'name': no, })

      else:
          print no + "is not a valid file name for youtube"
          

    with open('C:\Users\Win7 - 1\PycharmProjects\Upload Video independent\status\\YT_data.txt', 'w') as outfile:
      json.dump(data, outfile)
    record = open(status, "w")
    record.close()
    record = open(status, "a")
    record.write("0")
    record.close()


if __name__ == '__main__':
  main(sys.argv)

