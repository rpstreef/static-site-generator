#!/usr/bin/python3.6
"""
Generates static site from CodeCommit source and deploys to production S3 Bucket
Many thanks to MMusket and Alestic from which i adapted their code.
https://github.com/mmusket/s3-hosting-guide
https://github.com/alestic/aws-lambda-codepipeline-site-generator-hugo
"""

from __future__ import print_function
import os
import zipfile
import gzip
import tempfile
import shutil
import subprocess
import traceback
from mimetypes import MimeTypes
from multiprocessing.pool import ThreadPool
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

DONOTZIP = ['.jpg', '.png', '.ttf', '.woff', '.woff2', '.gif']

CP = boto3.client('codepipeline')
S3 = boto3.client('s3', config=Config(signature_version='s3v4'))
DEV = False

def setup(event):
    """ Setup all properties"""
    job_id = event['CodePipeline.job']['id']
    job_data = event['CodePipeline.job']['data']
    input_artifact = job_data['inputArtifacts'][0]
    from_bucket = input_artifact['location']['s3Location']['bucketName']
    from_key = input_artifact['location']['s3Location']['objectKey']
    # environment variable passed along by CloudFormation template
    to_bucket = os.environ['SiteBucket']

    return (job_id, from_bucket, from_key, to_bucket)

def download_source(from_bucket, from_key, source_dir):
    """ Download source code to be generated """
    with tempfile.NamedTemporaryFile() as tmp_file:
        S3.download_file(from_bucket, from_key, tmp_file.name)
        with zipfile.ZipFile(tmp_file.name, 'r') as zipobj:
            zipobj.extractall(source_dir)

def upload_site(site_dir, to_bucket):
    """
    Upload generated code to S3 site bucket, clean existing data on copy
    Create gzip from all files, except images, then copy to site bucket
    """
    staging_dir = '/tmp/staging/'

    [zip_file(x, staging_dir + x) if is_zip_file(x) else copy_file(x, staging_dir + x) for x in get_files(site_dir)]
    pool = ThreadPool(processes=5)
    pool.map(lambda x: upload_file(to_bucket, x, staging_dir, site_dir), get_files(staging_dir))

def generate_static_site(source_dir, site_dir):
    """Generate static site using hugo."""
    command = ["./hugo", "--source=" + source_dir, "--destination=" + site_dir]

    print(command)
    try:
        print(subprocess.check_output(command, stderr=subprocess.STDOUT))
    except subprocess.CalledProcessError as error:
        print("ERROR return code: ", error.returncode)
        print("ERROR output: ", error.output)
        raise

def get_files(base_folder):
    """ Returns an array containing all the filepaths """
    file_paths = []
    # os.walk will yield 3 parameter tuple
    for root, directory, files in os.walk(base_folder):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths

def zip_file(input, output):
    """ GZip's file """
    if DEV:
        print('Zipping ' + input)
    dirname = os.path.dirname(output)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(input, 'rb') as f_in, gzip.open(output, 'wb') as f_out:
        f_out.writelines(f_in)

def copy_file(input, output):
    """ Copy to staging directory before we copy to the dest bucket """
    if DEV:
        print('Copying ' + input)
    dirname = os.path.dirname(output)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    shutil.copyfile(input, output)

def is_zip_file(file_name):
    """ doc string """
    extension = os.path.splitext(file_name)[1]
    if extension in DONOTZIP:
        return False
    return True

def upload_file(bucket_name, file_path, staging_dir, site_dir):
    """ Upload file by file, before upload it will set the encoding for the file """
    destname = file_path.replace(staging_dir, "/")
    destname = destname.replace(site_dir + "/", "")

    if DEV:
        print("Uploading file " + file_path + ' to ' + destname)
    try:
        data = open(file_path, 'rb')
        ftype, encoding = MimeTypes().guess_type(file_path)
        con_type = ftype if ftype is not None else encoding if encoding is not None else 'text/plain'
        enc_type = 'gzip' if is_zip_file(file_path) else ''
        S3.put_object(Bucket=bucket_name, Key=destname, Body=data,
                      ContentEncoding=enc_type, ContentType=con_type, ACL='public-read')
    except ClientError as err:
        print("Failed to upload artefact to S3.\n" + str(err))
        return False
    except IOError as err:
        print("Failed to access artefact in this directory.\n" + str(err))
        return False
    return True

def handler(event, context):
    """ Program event flow"""
    try:
        (job_id, from_bucket, from_key, to_bucket) = setup(event)
        source_dir = tempfile.mkdtemp()
        site_dir = tempfile.mkdtemp()

        download_source(from_bucket, from_key, source_dir)
        generate_static_site(source_dir, site_dir)
        upload_site(site_dir, to_bucket)

        CP.put_job_success_result(jobId=job_id)

    except Exception as exception:
        print("ERROR: " + repr(exception))
        traceback.print_exc()
        CP.put_job_failure_result(
            jobId=job_id, failureDetails={'message': exception, 'type': 'JobFailed'})

    finally:
        shutil.rmtree(source_dir)
        shutil.rmtree(site_dir)

    return "complete"
