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
        
        # DynamoDBからのデータ取得
        response = table.get_item(
            Key={
                'id': event['id']
            }
        )
        
        print(f"DynamoDB response: {response}")
        
        # アイテムが存在するかチェック
        if 'Item' in response:
            item = response['Item']
            print(f"Item found: {item}")
            
            # numberフィールドの存在をチェック
            if 'number' not in item:
                print(f"Warning: 'number' field not found in item. Available fields: {list(item.keys())}")
                # numberフィールドが存在しない場合は0を設定
                item['number'] = 0
            
            # 元のNode.js版と同じ構造で返す（dataキーなしで直接アイテムを返す）
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(item, cls=DecimalEncoder)
            }
        else:
            print(f"No item found for id: {event['id']}")
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Stock not found',
                    'id': event['id']
                })
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
                'message': 'Error retrieving stock',
                'error': str(error)
            })
        } 