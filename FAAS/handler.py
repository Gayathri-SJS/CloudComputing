import os
import imutils
import cv2
import json
from PIL import Image, ImageDraw, ImageFont
from facenet_pytorch import MTCNN, InceptionResnetV1
from shutil import rmtree
import numpy as np
import torch
import boto3

AWS_ACCESS_KEY_ID = #access key
AWS_SECRET_ACCESS_KEY = #secret access key

client_s3 = boto3.client('s3',region_name='us-east-1',aws_access_key_id= AWS_ACCESS_KEY_ID, aws_secret_access_key= AWS_SECRET_ACCESS_KEY)
os.environ['TORCH_HOME'] = '/tmp'

mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embeding conversion

def face_recognition_function(key_path):
    # Face extraction
    img = cv2.imread(key_path, cv2.IMREAD_COLOR)
    boxes, _ = mtcnn.detect(img)

    # Face recognition
    key = os.path.splitext(os.path.basename(key_path))[0].split(".")[0]
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    face, prob = mtcnn(img, return_prob=True, save_path=None)
    saved_data = torch.load('/tmp/data.pt')  # loading data.pt file
    if face != None:
        emb = resnet(face.unsqueeze(0)).detach()  # detech is to make required gradient false
        embedding_list = saved_data[0]  # getting embedding data
        name_list = saved_data[1]  # getting list of names
        dist_list = []  # list of matched distances, minimum distance is used to identify the person
        for idx, emb_db in enumerate(embedding_list):
            dist = torch.dist(emb, emb_db).item()
            dist_list.append(dist)
        idx_min = dist_list.index(min(dist_list))

        # Save the result name in a file
        with open("/tmp/" + key + ".txt", 'w+') as f:
            f.write(name_list[idx_min])
        return name_list[idx_min]
    else:
        print(f"No face is detected")
    return

def handler(event, context):
    print(event)
    bucket_in= event['bucket_name']
    bucket_out= '1230360484-output'
    bucket_data= 'sjsdata'
    key = event['image_file_name'] #event['Records'][0]['s3']['object']['key']
    print(key, event)
    if not os.path.exists('/tmp'):
        os.makedirs('/tmp')
    client_s3.download_file(bucket_in, key, '/tmp/'+key)
    print('file downloaded')
    client_s3.download_file(bucket_data, 'data.pt', '/tmp/data.pt')
    print('data file downloaded')
    face_recognition_function('/tmp/'+key) #output_imgs /tmp/test_99
    key = key.split(".")[0]
    print(key)
    response = client_s3.upload_file('/tmp/'+key+'.txt', bucket_out, key+'.txt')
    
