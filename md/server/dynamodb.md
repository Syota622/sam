DynamoDBのスロットリングエラーの調査をしてます。
AWSから以下の回答をもらいました。
これをもとに、AWS CLIを使って、実際にスロットリングエラーをわざと発生させることはできますか？
DynamoDBはオンデマンドモードです。
```
DynamoDB では読み込みの場合、項目サイズを 4 KB の倍数に切り上げてから 4 KB あたり以下の RCU が消費されます [1][2]。
- 強力な整合性のある読み込みリクエストは 1 RCU
- 結果整合性のある読み込みリクエストは 0.5 RCU 
- トランザクション読み込みリクエストは 2 RCU

例えばクエリ結果合計サイズが 40 KB の GetItem 操作を、強力な整合性読み取り [3] を有効にして実行する場合には、の 1 リクエストあたり 10 RCU 消費されます。
そのため、3000 RCU を消費するにはこのリクエストを同じ単一の項目に対して 3000 RCU / 10 RCU = 300 リクエスト実行する必要がございます。

◼︎ ConsumedThroughputUnits の計算式
> >そのため、ConsumedThroughputUnits の数値をもとに消費された RCU や WCU の傾向をご確認いただけますと幸いです。
> こちらRCUの場合で構いませんので、実際の計算方法を例をもとにご教示いただきたいです。

前回のご案内の通り、ConsumedThroughputUnits は以下のように定義されております [4]。

ConsumedThroughputUnits = (3 x WCU) + RCU

そのため、当該の項目に読み込みリクエストのみ発生している場合には、ConsumedThroughputUnits がその項目について消費された RCU となる想定です。
```

AWSの回答を基に、DynamoDBオンデマンドモードでスロットリングエラーを意図的に発生させる方法をご説明します。

スロットリング発生の仕組み
DynamoDBオンデマンドモードでは、以下の条件でスロットリングが発生する可能性があります：

急激なトラフィック増加：短時間で大量のリクエストが集中する
ホットパーティション：特定のパーティションキーに集中的にアクセスする
大きなアイテムサイズ：大容量のデータを頻繁に読み書きする
AWS CLIを使った検証方法
1. テストテーブルとデータの準備
bash
# テストテーブル作成（オンデマンドモード）
aws dynamodb create-table \
    --table-name throttle-test \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

# 40KBの大きなアイテムを作成（Base64エンコードで約40KB）
LARGE_DATA=$(python3 -c "import base64; print(base64.b64encode(b'x' * 30000).decode())")

aws dynamodb put-item \
    --table-name throttle-test \
    --item "{\"id\": {\"S\": \"test-item\"}, \"data\": {\"S\": \"$LARGE_DATA\"}}"
2. 集中的な読み込みでスロットリングを発生させる
AWSの回答によると、40KBのアイテムを強整合性読み込みで300回実行すると3000 RCUを消費します。これを短時間で実行してスロットリングを誘発します：

bash
#!/bin/bash
# throttle_test.sh

TABLE_NAME="throttle-test"
ITEM_KEY='{"id": {"S": "test-item"}}'

echo "スロットリングテストを開始..."

# 並列で大量のGetItemリクエストを実行
for i in {1..500}; do
    {
        aws dynamodb get-item \
            --table-name $TABLE_NAME \
            --key "$ITEM_KEY" \
            --consistent-read \
            --no-cli-pager 2>&1 | grep -E "(ProvisionedThroughputExceededException|ThrottlingException)" && echo "スロットリング発生: リクエスト $i"
    } &
    
    # 50個ごとにプロセス数を制限
    if (( i % 50 == 0 )); then
        wait
    fi
done

wait
echo "テスト完了"
3. より効率的なスロットリング発生方法
bash
#!/bin/bash
# intensive_throttle_test.sh

TABLE_NAME="throttle-test"

# 複数のアイテムを同じパーティション内に作成
for i in {1..10}; do
    LARGE_DATA=$(python3 -c "import base64; print(base64.b64encode(b'x' * 50000).decode())")
    aws dynamodb put-item \
        --table-name $TABLE_NAME \
        --item "{\"id\": {\"S\": \"item-$i\"}, \"data\": {\"S\": \"$LARGE_DATA\"}}" &
done

wait

# 同時に大量のクエリを実行
for i in {1..1000}; do
    {
        aws dynamodb get-item \
            --table-name $TABLE_NAME \
            --key "{\"id\": {\"S\": \"item-$(( (i % 10) + 1 ))\"}}" \
            --consistent-read \
            --no-cli-pager 2>&1
    } &
    
    # CPUリソースを考慮して100個ごとに待機
    if (( i % 100 == 0 )); then
        sleep 0.1
    fi
done
4. スロットリング確認とメトリクス収集
bash
# CloudWatchメトリクスでスロットリングを確認
aws cloudwatch get-metric-statistics \
    --namespace AWS/DynamoDB \
    --metric-name ThrottledRequests \
    --dimensions Name=TableName,Value=throttle-test \
    --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
    --period 300 \
    --statistics Sum

# ConsumedReadCapacityUnitsも確認
aws cloudwatch get-metric-statistics \
    --namespace AWS/DynamoDB \
    --metric-name ConsumedReadCapacityUnits \
    --dimensions Name=TableName,Value=throttle-test \
    --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
    --period 300 \
    --statistics Sum
注意事項
コスト: オンデマンドモードでは使用量に応じて課金されるため、テスト時間を制限してください
レート制限: AWS CLIには独自のレート制限があるため、--cli-read-timeoutや--cli-connect-timeoutオプションの調整が必要な場合があります
エラーハンドリング: スロットリングが発生した場合、指数バックオフでリトライするのが推奨されます
このテストを実行することで、実際のスロットリング動作とCloudWatchメトリクスの関係を確認できるはずです。