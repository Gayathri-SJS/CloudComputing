import csv
from flask import Flask, request
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import csv
import boto3
import base64


app = Flask(__name__)
executor = ThreadPoolExecutor()
Dict=defaultdict(str)
AWS_ACCESS_KEY_ID = #access key
AWS_SECRET_ACCESS_KEY = #secret access key

client_sqs = boto3.client('sqs',region_name='us-east-1',aws_access_key_id= AWS_ACCESS_KEY_ID, aws_secret_access_key= AWS_SECRET_ACCESS_KEY)

def process_image( filename, file_binary):
    try:
        file_string = base64.b64encode(file_binary).decode('utf-8')
        print("Sending Message to App Tier")
        response = client_sqs.send_message(
                    QueueUrl='https://sqs.us-east-1.amazonaws.com/590183841764/1230360484-req-queue',
                    MessageBody = file_string,
                    MessageAttributes={
                        'ID': {
                            'StringValue': filename,
                            'DataType': 'String'
                        }
                    }
                )
        
        while True:
            print(filename, filename in Dict)
            message = client_sqs.receive_message(
                    QueueUrl='https://sqs.us-east-1.amazonaws.com/590183841764/1230360484-resp-queue',
                    MessageAttributeNames=['ID'],
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=5,
                )
            ans=''
            if 'Messages' in message:
                if filename in Dict:
                    prediction_result=Dict.pop(filename)
                    ans=f"{filename}:{prediction_result}"
                prediction_result= message['Messages'][0]['Body']
                ID=message['Messages'][0]['MessageAttributes']['ID']['StringValue']
                if ID==filename:
                    ans=f"{filename}:{prediction_result}"
                else:
                    Dict[ID]=prediction_result
                response = client_sqs.delete_message(
                QueueUrl='https://sqs.us-east-1.amazonaws.com/590183841764/1230360484-resp-queue',
                ReceiptHandle=message['Messages'][0]['ReceiptHandle']
                )
            if filename in Dict:
                prediction_result=Dict.pop(filename)
                ans = f"{filename}:{prediction_result}"
            if ans!='':
                return ans
    except Exception as e:
        return f"Error processing {filename}: {str(e)}"
    

@app.route('/', methods=['POST'])
def handle_request():
    try:
        if 'inputFile' not in request.files:
            return "Error: No 'inputFile' key in request"
        print("Request received")
        image_file = request.files['inputFile']
        file_binary=image_file.read()
        filename = image_file.filename.split(".")[0]
        # future = executor.submit(process_image, filename, file_binary)
        answer = process_image(filename, file_binary)
        return answer

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, threaded = True)
