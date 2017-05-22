#!/usr/bin/python3.6
""" Generates static site from CodeCommit source and deploys to production S3 Bucket """

from __future__ import print_function
import os
import zipfile
import tempfile
import shutil
import subprocess
import traceback
import boto3
from botocore.client import Config

CP = boto3.client('codepipeline')
S3 = boto3.client('s3', config=Config(signature_version='s3v4'))

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
    """ Upload generated code to S3 site bucket, clean existing data on copy """
    command = ["./aws", "s3", "sync", "--acl", "public-read", "--delete",
               site_dir + "/", "s3://" + to_bucket + "/"]
    print(command)
    print(subprocess.check_output(command, stderr=subprocess.STDOUT))

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
