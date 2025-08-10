const AWS = require('aws-sdk');
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = (event, context) => {
  //JSONをJSのオブジェクトに変換
  const data = JSON.parse(event.body);

  //テーブル名(TableName)とキー項目(Key)のオブジェクト
  const params = {
    TableName: "stock",
    Key: {
      id: data.id
    },
    UpdateExpression: 'SET #number = :newNumber',
    ExpressionAttributeNames: {
      '#number' : 'number'
    },
    ExpressionAttributeValues: {
      ':newNumber': data.number
    }
  };
  
  //DynamoDBへのデータ更新
  dynamoDb.update(params, function(err, data) {
    if (err) {
      context.fail(err); // エラー時
    } else {
      JSON.stringify(context.succeed(data.Item)); // 正常時
    }
  });
};
