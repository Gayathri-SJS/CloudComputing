import json
import boto3
import os
#import ffmpeg
import subprocess
import math

AWS_ACCESS_KEY_ID = #access key
AWS_SECRET_ACCESS_KEY = #secret access key

client_s3 = boto3.client('s3',region_name='us-east-1',aws_access_key_id= AWS_ACCESS_KEY_ID, aws_secret_access_key= AWS_SECRET_ACCESS_KEY)
client = boto3.client('lambda',region_name='us-east-1',aws_access_key_id= AWS_ACCESS_KEY_ID, aws_secret_access_key= AWS_SECRET_ACCESS_KEY)
def video_splitting_cmdline(video_filename):
    filename = os.path.basename(video_filename)
    outfile = os.path.splitext(filename)[0] + ".jpg"

    split_cmd = '/opt/bin/ffmpeg -i ' + video_filename + ' -vframes 1 ' + '/tmp/' + outfile
    try:
        subprocess.check_call(split_cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)

    fps_cmd = 'ffmpeg -i ' + video_filename + ' 2>&1 | sed -n "s/.*, \\(.*\\) fp.*/\\1/p"'
    fps = subprocess.check_output(fps_cmd, shell=True).decode("utf-8").rstrip("\n")
    return outfile
    
def lambda_handler(event, context):
    bucket_in= '1230360484-input'
    bucket_out= '1230360484-stage-1'
    key = event['Records'][0]['s3']['object']['key'] #'test_99.mp4'
    if not os.path.exists('/tmp'):
        os.makedirs('/tmp')
    client_s3.download_file(bucket_in, key, '/tmp/'+key)
    output_imgs = video_splitting_cmdline('/tmp/'+key) #output_imgs /tmp/test_99
    response = client_s3.upload_file('/tmp'+'/'+output_imgs, bucket_out, output_imgs)
    print(output_imgs)
    response = client.invoke(
    FunctionName='face-recognition',
    InvocationType='Event',
    Payload= '{{"bucket_name":"1230360484-stage-1", "image_file_name":"{}"}}'.format(output_imgs)
)

  
