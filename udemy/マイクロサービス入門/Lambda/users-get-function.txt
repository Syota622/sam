import boto3
 
dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('users')

#リクエストパラメータでIDが指定される場合、該当IDのユーザ情報を取得して返す
def get_user(id):
    response = table.get_item(
            Key={
                 'id': id
            }
        )
    return response['Item']

#リクエストパラメータでIDが指定されない場合、全ユーザ情報を取得して返す
def get_users():
    response = table.scan()
    return response['Items']
         
def lambda_handler(event, context):
    return get_users() if event['id'] == '' else get_user(event['id'])