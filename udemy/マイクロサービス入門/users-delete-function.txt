import boto3
 
dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('users')

#リクエストパラメータでIDが指定される場合、該当IDのレコードを削除する
def delete_user(id):
    table.delete_item(
        Key={
            'id': id
        }
    )

#リクエストパラメータでIDが指定されない場合、テーブルを削除する
def delete_users():
    response = table.delete()
         
def lambda_handler(event, context):
    return delete_users() if event['id'] == '' else delete_user(event['id'])