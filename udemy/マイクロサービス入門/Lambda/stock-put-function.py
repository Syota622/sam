import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('stock')

# Decimal型をintに変換するカスタムJSONエンコーダー
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        print(f"Received event: {event}")
        
        # JSONをPythonのオブジェクトに変換
        data = json.loads(event['body'])
        print(f"Parsed data: {data}")
        
        # DynamoDBへのデータ更新
        response = table.update_item(
            Key={
                'id': data['id']
            },
            UpdateExpression='SET #number = :newNumber',
            ExpressionAttributeNames={
                '#number': 'number'
            },
            ExpressionAttributeValues={
                ':newNumber': data['number']
            },
            ReturnValues='ALL_NEW'
        )
        
        print(f"Update response: {response}")
        
        # 元のNode.js版と同じ構造で返す（dataキーなしで直接アイテムを返す）
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response['Attributes'], cls=DecimalEncoder)
        }
        
    except Exception as error:
        print(f'Error: {error}')
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Error updating stock',
                'error': str(error)
            })
        } 