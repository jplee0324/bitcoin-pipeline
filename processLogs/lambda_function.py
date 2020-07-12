import json
import urllib.parse
import boto3
from datetime import datetime, timezone
import os
import pymysql
import pytz

print('Loading function')

s3 = boto3.client('s3')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    
    print('Establishing Amazon RDS MySQL database connection')
    try: 
        conn = pymysql.connect(host = os.environ["RDS_LAMBDA_HOSTNAME"], port = int(os.environ["RDS_LAMBDA_PORT"]), user = os.environ["RDS_LAMBDA_USERNAME"], password = os.environ["RDS_LAMBDA_PASSWORD"], database="cryptotrades")
    except Exception as e:
        print(e)
        print("Connection to MySQL database - FAILED")
        raise e
        
    print('Connection to MySQL database - SUCCESSFUL')
    
    cursor = conn.cursor()
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        # filter out all excess text and get only json messages with transaction data
        content = response['Body'].read().decode('utf-8').replace('\"\\\"', '').replace('\\\\\\', '')
        content_lines = content.splitlines()
        content_lines = [content[11:].split("\\")[0] for content in content_lines]
        
        converted = (datetime.strptime(key[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('US/Eastern'))).strftime("%Y-%m-%d %H:%M:%S")

        aggregated = {
            "TOTAL_COUNT_BUY" : 0,
            "TOTAL_COUNT_SELL" : 0,
            "TOTAL_BTC_BUY" : 0,
            "TOTAL_BTC_SELL" : 0,
            "TOTAL_USD_BUY" : 0,
            "TOTAL_USD_SELL" : 0,
            "TIME" : converted
        }
        
        # aggregate total counts across all transactions that occured in this minute
        for line in content_lines:
            loaded = json.loads(line)
            bos = "BUY" if loaded["m"] == True else "SELL"
            aggregated["TOTAL_COUNT_" + bos] += 1
            aggregated["TOTAL_BTC_" + bos] += float(loaded["q"])
            aggregated["TOTAL_USD_" + bos] += float(loaded["p"])*float(loaded["q"])
        
        aggregated["TOTAL_USD_BUY"] = round(aggregated["TOTAL_USD_BUY"], 2)
        aggregated["TOTAL_USD_SELL"] = round(aggregated["TOTAL_USD_SELL"], 2)

        # insert aggregated values into MySQL database
        vals = [str(val) for val in aggregated.values()]

        try:
            q = """INSERT INTO cryptotrades.TRANSACTIONS
            VALUES (NULL, {}, {});""".format(', '.join(vals[:-1]), "'"+vals[-1]+"'")
            cursor.execute(q)
        except Exception as e:
            print(e)
            print('Error inserting into database')
            raise e
        
        conn.commit()    
        conn.close()
        print("CONTENT TYPE: " + response['ContentType'])
        
        s3.delete_object(Bucket=bucket, Key=key)
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
