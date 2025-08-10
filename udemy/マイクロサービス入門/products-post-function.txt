import boto3
import json

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('products')
 
def post_products(requestJSON):
    table.put_item(Item={'id': requestJSON['id'], 'name': requestJSON['name'], 'price': requestJSON['price']})

def lambda_handler(event, context):
    requestJSON = json.loads(event['body'])
    post_products(requestJSON)