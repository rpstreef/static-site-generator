#!/usr/bin/python3.6
""" Generates static site from CodeCommit source and deploys to production S3 Bucket """

from __future__ import print_function
import zipfile
import tempfile
import shutil
import subprocess
import traceback
import boto3

CP = boto3.client('codepipeline')
S3 = boto3.client('s3')

def setup(event):
    """ Setup all properties"""
    job_id = event['CodePipeline.job']['id']
    job_data = event['CodePipeline.job']['data']
    input_artifact = job_data['inputArtifacts'][0]
    output_artifact = job_data['outputArtifacts'][0]
    from_bucket = input_artifact['location']['s3Location']['bucketName']
    from_key = input_artifact['location']['s3Location']['objectKey']
    to_bucket = output_artifact['location']['s3Location']['bucketName']
    to_key = output_artifact['location']['s3Location']['objectKey']

    return (job_id, from_bucket, from_key, to_bucket, to_key)

def download_source(from_bucket, from_key, source_dir):
    """ Download source code to be generated """
    with tempfile.NamedTemporaryFile() as tmp_file:
        S3.download_file(from_bucket, from_key, tmp_file.name)
        with zipfile.ZipFile(tmp_file.name, 'r') as zipobj:
            zipobj.extractall(source_dir)

def upload_site(site_dir, to_bucket, to_key):
    """ Upload generated code to S3 site bucket """
    with tempfile.NamedTemporaryFile() as tmp_file:
        site_zip_file = shutil.make_archive(tmp_file.name, 'zip', site_dir)
        S3.upload_file(site_zip_file, to_bucket, to_key)

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
        (job_id, from_bucket, from_key, to_bucket, to_key) = setup(event)
        source_dir = tempfile.mkdtemp()
        site_dir = tempfile.mkdtemp()

        download_source(from_bucket, from_key, source_dir)
        generate_static_site(source_dir, site_dir)
        upload_site(site_dir, to_bucket, to_key)
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
