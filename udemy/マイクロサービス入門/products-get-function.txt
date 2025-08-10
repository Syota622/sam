import boto3
 
dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('products')

#リクエストパラメータでIDが指定される場合、該当IDの商品情報を取得して返す
def get_product(id):
    response = table.get_item(
            Key={
                 'id': id
            }
        )
    return response['Item']

#リクエストパラメータでIDが指定されない場合、全商品情報を取得して返す
def get_products():
    response = table.scan()
    return response['Items']
         
def lambda_handler(event, context):
    return get_products() if event['id'] == '' else get_product(event['id'])