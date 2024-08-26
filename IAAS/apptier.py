import boto3
import base64
from face_recognition import face_match
from PIL import Image
import io
import os

new_folder_path ="folder/"



AWS_ACCESS_KEY_ID = #access key
AWS_SECRET_ACCESS_KEY = #secret access key

client_sqs = boto3.client('sqs',region_name='us-east-1',aws_access_key_id= AWS_ACCESS_KEY_ID, aws_secret_access_key= AWS_SECRET_ACCESS_KEY)
sqs_s3= boto3.client('s3',region_name='us-east-1',aws_access_key_id= AWS_ACCESS_KEY_ID, aws_secret_access_key= AWS_SECRET_ACCESS_KEY)

def Prediction(imagepath, fileID):
    print("received image")
    answer= face_match(imagepath, fileID)
    print(answer)
    sqs_s3.put_object(
        Body=answer,
        Bucket="1230360484-out-bucket",
        Key=fileID
)
    response = client_sqs.send_message(
                    QueueUrl='https://sqs.us-east-1.amazonaws.com/590183841764/1230360484-resp-queue',
                    MessageBody = answer,
                    MessageAttributes={
                        'ID': {
                            'StringValue': fileID,
                            'DataType': 'String'
                        }
                    }
                )
    return




while True:
    message_response=  client_sqs.receive_message(
                    QueueUrl='https://sqs.us-east-1.amazonaws.com/590183841764/1230360484-req-queue',
                    MessageAttributeNames=['ID'],
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=5,
                )
    if 'Messages' in message_response:
        messages = message_response['Messages'][0]
        ID=messages['MessageAttributes']['ID']['StringValue']
        message= messages['Body']
        message_binary= base64.b64decode(message.encode('utf-8'))
        # image = Image.open(io.BytesIO(message_binary))
        # image.save(os.path.join(new_folder_path, ID+".jpg"))
        with open(os.path.join(new_folder_path, ID+".jpg"), 'wb') as f:
                f.write(message_binary)
        image_path= new_folder_path + ID +'.jpg'
        sqs_s3.upload_file(
             image_path,
             "1230360484-in-bucket",
             ID
        )
        Prediction(image_path,ID)
        response = client_sqs.delete_message(
                    QueueUrl='https://sqs.us-east-1.amazonaws.com/590183841764/1230360484-req-queue',
                    ReceiptHandle=messages['ReceiptHandle']
                    )
