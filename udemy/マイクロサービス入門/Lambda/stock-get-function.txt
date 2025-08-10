const AWS = require('aws-sdk');
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.handler = (event, context) => {
  // テーブル名(TableName)とキー項目(Key)のオブジェクト
  const params = { 
    TableName: "stock",
    Key: {
      id: event.id
    },
  };

  // DynamoDBからのデータ取得
  return dynamoDb.get(params, function(err, data) {
    if (err) {
      // エラー時
      context.fail(err);
    } else {
      // 正常時
      JSON.stringify(context.succeed(data.Item));
    }
  });
};