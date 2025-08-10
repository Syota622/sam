import boto3
import json

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('products')
 
def put_products(requestJSON):
    table.update_item(
        Key={
            'id': requestJSON['id']
        },
        UpdateExpression="SET #name = :newName, price = :newPrice",
        ExpressionAttributeNames= {
        '#name' : 'name'
        },
        ExpressionAttributeValues={
            ':newName': requestJSON['name'],
            ':newPrice': requestJSON['price']
        },
    )

def lambda_handler(event, context):
    requestJSON = json.loads(event['body'])
    put_products(requestJSON)