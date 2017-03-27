#!/usr/bin/python

import time
import datetime
import os
import string
import tarfile

from boto.s3.key import Key
from boto.s3.connection import S3Connection

from datetime import timedelta
from time import mktime

# Configuration

aws_access_key = '<your-aws-access-key>'
aws_secret_key = '<your-aws-secret-key>'
aws_bucket = '<your-aws-bucket-name>'
aws_region_host = '<your-aws-region-host>'

mysql_hostname = '127.0.0.1'
mysql_username = ''
mysql_password = ''

		
databases = [
        'database_name_1',
        'database_name_2',
        ]

# Script Configuration
today = datetime.date.today()
# For creating monthly backups
last_backup_date = today - timedelta(days = 7)



# MySQL Backups
for d in dbs:

    d = d.strip()
    file = "/tmp/%s-%s.sql.gz" % (d, today)

    print '[DB] Creating archive for ' + file

     os.system("mysqldump -u %s -p%s  %s | gzip > %s" % (mysql_username, mysql_password, d, file))

# Establish an S3 Connection, remember to get the correct region host value
s3 = boto.s3.connect_to_region(aws_region_host, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, is_secure=True, calling_format = boto.s3.connection.OrdinaryCallingFormat())
bucket = s3.get_bucket(aws_bucket)

# Send Databses to AWS S3
for d in dbs:

    d = d.strip()
    file = "%s-%s.sql.gz" % (d, today)

    print '[S3] Uploading database dump ' + file + '...'

    k = Key(bucket)
    k.key = file
    k.set_contents_from_filename('/tmp/' + file)
    k.set_acl("public-read")

    os.remove('/tmp/' + file);

    print '[S3] Clearing previous database dump ' + file + '...'

    # Remove files older than last_backup_date
    for ekey in bucket.list():
        key_modified_date = datetime.datetime.fromtimestamp(mktime(time.strptime(ekey.last_modified[:19], "%Y-%m-%dT%H:%M:%S"))).date()
        if key_modified_date < last_backup_date:
            ekey.delete()

