const AWS = require('aws-sdk');
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = (event, context) => {
  // JSONをJSのオブジェクトに変換
  const data = JSON.parse(event.body);

  // テーブル名(TableName)と各カラム(Item)のオブジェクト
  const params = { 
    TableName: "stock",
    Item: {
      id: data.id,
      number: data.number,
    },
  };

  // DynamoDBへのデータ登録
  dynamoDb.put(params, function(err, data) {
    if (err) {
      context.fail(err); // エラー時
    } else {
      JSON.stringify(context.succeed(data.Item)); // 正常時
    }
  });
};