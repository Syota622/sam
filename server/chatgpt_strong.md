# AWS主要サービスの性能制限比較表

# CloudFront

| 項目 | デフォルト値 | Max/上限 | 緩和・増枠可否 | 東京 vs オレゴン | メトリクス監視 |
| ----------------------- | ----------------------: | -----: | --------------------------------------------------------- | ---------- | ---------------------- |
| リクエスト数（RPS）/ディストリビューション | 250,000 RPS |  増枠で引き上げ可 | **可**（Service Quotasで申請） | グローバルサービスのため同一（差なし） | `Requests`（リクエスト数合計）と `TotalErrorRate`／`4xxErrorRate`／`5xxErrorRate` を監視。急増・エラー率上昇を検知。 :contentReference[oaicite:0]{index=0} |
| 転送レート/ディストリビューション | 150 Gbps |  増枠で引き上げ可 | **可**（申請） | 同一 | `BytesDownloaded`／`BytesUploaded`（転送バイト）で実効帯域の傾向を把握。ピーク帯域の超過兆候を検知。 :contentReference[oaicite:1]{index=1} |
| オリジン応答タイムアウト（OriginReadTimeout） | 30秒 |  1–120秒（設定範囲） | 設定で変更可／**更なる増枠は申請** | 同一 | `OriginLatency`（オリジンTTFB）とステータス別エラー率を監視。遅延上昇＝タイムアウト接近の兆候。 :contentReference[oaicite:2]{index=2} |
| オリジンKeep-Aliveタイムアウト（Custom Origin） | 5秒 |  60秒 | 設定で変更可（S3オリジン除く） | 同一 | `OriginLatency` と `5xxErrorRate` を併観。Keep-Alive不整合時の遅延・エラーを検知。 :contentReference[oaicite:3]{index=3} |
| 同時インバリデーション件数（進行中） | 個別パス合計3,000ファイル、ワイルドカード15パス |  固定 | **不可**（設計で回避） | 同一 | 専用メトリクスなし。`CreateInvalidation` を CloudTrail で監査、負荷影響は `Requests`／エラー率で間接監視。 :contentReference[oaicite:4]{index=4} |

> 補足：CloudFrontは自動スケールで“プレウォーム不要”。RPSやスループットは増枠申請＋キャッシュ/TTL設計で緩和可能です。([AWS ドキュメント][1])

---

# API Gateway

| 項目 | デフォルト値 | Max/上限 | 緩和・増枠可否 | 東京 vs オレゴン | メトリクス監視 |
| ----------------------- | ----------------------: | -----: | --------------------------------------------------------- | ---------- | ---------------------- |
| アカウント単位のスロットリング（RPS/Region） | 10,000 RPS（バースト5,000） |  申請で増枠 | **可**（Service Quotas） | 同一 | `Count`（処理数）と `4XXError`／`5XXError`、`Latency` を基本監視。閾値超でスロットル兆候を検出。 :contentReference[oaicite:5]{index=5} |
| 統合タイムアウト（REST：Regional/Private） | 29秒 |  固定 | **不可**（値自体は固定／設計対応） | 同一 | `IntegrationLatency` と `Latency` を p95/p99 で監視。29秒接近でアラート。 :contentReference[oaicite:6]{index=6} |
| 統合タイムアウト（HTTP API） | ～30秒 |  30秒 | **不可** | 同一 | `Latency` と `IntegrationLatency`、`DataProcessed` を監視（ルート別は詳細メトリクス有効化）。 :contentReference[oaicite:7]{index=7} |
| ペイロードサイズ（REST/HTTP、非WebSocket） | 10 MB |  10 MB | **不可**（S3直PUT等で回避） | 同一 | `DataProcessed`（処理バイト）で大型ペイロードの傾向を可視化。エラー率も併観。 :contentReference[oaicite:8]{index=8} |

> 回避例：大きな処理はStep Functions等で**非同期化**、大容量アップロードは**S3プリサインURL**を利用。([AWS ドキュメント][10], [AWS in Plain English][11])

---

# DynamoDB

| 項目 | デフォルト値 | Max/上限 | 緩和・増枠可否 | 東京 vs オレゴン | メトリクス監視 |
| ----------------------- | ----------------------: | -----: | --------------------------------------------------------- | ---------- | ---------------------- |
| パーティション当たりの最大スループット | 3,000 RCU / 1,000 WCU |  固定 | **不可**（キー設計で緩和） | 同一 | `ConsumedReadCapacityUnits`／`ConsumedWriteCapacityUnits` と `ThrottledRequests`／`Read/WriteThrottleEvents` を監視。偏り・スパイク検知。 :contentReference[oaicite:9]{index=9} |
| アイテムサイズ | 400 KB/アイテム |  400 KB | **不可**（S3分離で回避） | 同一 | `SuccessfulRequestLatency`（サービス内レイテンシ）とエラー系を監視。サイズ超過はアプリ側検知と併用。 :contentReference[oaicite:10]{index=10} |
| テーブルあたりスループット上限（初期クォータ） | 40,000 RRU / 40,000 WRU |  申請で増枠 | **可**（Service Quotas） | 同一 | `Consumed*` と `ProvisionedRead/WriteCapacityUnits` の比率、`ThrottledRequests` を組み合わせてアラート。 :contentReference[oaicite:11]{index=11} |

> 補足：トラフィック偏りは**アダプティブキャパシティ**で一部救済されますが、基本は**良いパーティションキー設計**が前提です。([AWS ドキュメント][15])

---

# S3

| 項目 | デフォルト値 | Max/上限 | 緩和・増枠可否 | 東京 vs オレゴン | メトリクス監視 |
| ----------------------- | ----------------------: | -----: | --------------------------------------------------------- | ---------- | ---------------------- |
| リクエストレート（1プレフィックスあたりの目安） | ≥ 3,500 書込系 / 5,500 読取系 RPS |  プレフィックス分割で水平拡張 | **設計で緩和** | 同一（遅延は地理差） | リクエストメトリクス `AllRequests`、`Get/Put/Delete/ListRequests`、`4xxErrors`／`5xxErrors`、`FirstByteLatency`／`TotalRequestLatency` を有効化・監視。 :contentReference[oaicite:12]{index=12} |
| オブジェクトサイズ（単一PUT） | ～5 GB |  5 GB | **不可**（マルチパート推奨） | 同一 | `BytesUploaded`／`BytesDownloaded` とレイテンシ系でアップロード健全性を監視。 :contentReference[oaicite:13]{index=13} |
| オブジェクトサイズ（マルチパート） | – |  ～5 TB | **不可** | 同一 | 大容量転送時の `Bytes*`、`FirstByteLatency`／`TotalRequestLatency` を監視。失敗は `5xxErrors` を確認。 :contentReference[oaicite:14]{index=14} |
| 長距離転送の性能 | 通常転送 |  Transfer Acceleration で改善 | **機能で緩和** | 東京⇄オレゴン等で効果大 | `AllRequests`／レイテンシ系の地域別比較で効果検証（TA有効・無効の差分を見る）。 :contentReference[oaicite:15]{index=15} |

---

# Cognito（User Pools ほか）

| 項目（カテゴリー） | デフォルト値（RPS） | Max/上限 | 緩和・増枠可否 | 東京 vs オレゴン | メトリクス監視 |
| ----------------------- | ----------------------: | -----: | --------------------------------------------------------- | ---------- | ---------------------- |
| UserAuthentication（サインイン/トークン等） | 120 RPS |  申請で増枠 | **可**（Service Quotas） | 同一 | `SignInSuccesses`／`SignInThrottles`、`TokenRefreshSuccesses`／`TokenRefreshThrottles` を監視。成功率とスロットル検知。 :contentReference[oaicite:16]{index=16} |
| UserCreation（SignUp等） | 50 RPS |  申請で増枠 | **可** | 同一 | `SignUpSuccesses`／`SignUpThrottles` を監視。招待・登録スパイク時の健全性を把握。 :contentReference[oaicite:17]{index=17} |
| UserRead | 120 RPS |  申請で増枠 | **可** | 同一 | `CallCount`／`ThrottleCount`（使用量とスロットル）を監視。API別ディメンションで詳細化。 :contentReference[oaicite:18]{index=18} |
| UserAccountRecovery（ForgotPassword等） | 30 RPS |  固定 | **不可**（設計で緩和） | 同一 | `CallCount`／`ThrottleCount` に加え、失敗時はアプリ側のエラー率を併観。 :contentReference[oaicite:19]{index=19} |
| Hosted UI ドメインのバルクリミット（1 IP / 1クライアント / 1ドメイン） | 300 / 300 / 500 RPS |  固定 | **不可**（WAF等で保護） | 同一 | 直接メトリクスは限定的。`CallCount`／`ThrottleCount` と外側のWAF計測を併用。 :contentReference[oaicite:20]{index=20} |****                                          |

> 補足：Cognitoのクォータは**アカウント×リージョン**単位で適用。増枠は**Service Quotas**から「購入（有償）」でリクエストします。([AWS ドキュメント][20])

---

## メモ（読み方・実務の着地）

* **“増枠可”**＝Service Quotasやサポート経由で上げられる“ソフトリミット”。**“不可”**＝仕様上の“ハードリミット”で、\*\*設計（キャッシュ・並列化・分割・非同期化）\*\*で回避します。([AWS ドキュメント][21])
* **東京とオレゴンの数値差**は、上記いずれのサービスでも**基本なし**（例外はAPI Gatewayの一部新興リージョンのデフォルトRPSが低いだけ）。性能体感は**ネットワーク遅延**の差が支配的です。([AWS ドキュメント][6])
* 迷ったら：

  * **高RPS** → CloudFrontキャッシュ／API GWの使用量制御
  * **長時間処理** → Step Functions等**非同期**、API GW統合タイムアウト延長（REST Regional/Privateのみ） ([AWS ドキュメント][7])
  * **大容量** → **S3直アップロード（プリサインURL）**、DynamoDBは**S3ポインタ**で分離 ([AWS ドキュメント][9])

必要なら、上記表をそのままWiki/READMEに貼れる形で**英語版**も用意します。さらに「想定ピークRPSやオブジェクトサイズ」を教えていただければ、具体的な**設計上の緩和策**（キャッシュ戦略やキー設計、プレフィックス分割数の目安、WAFレート制御例）も併記します。

[1]: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html?utm_source=chatgpt.com "Quotas - Amazon CloudFront"
[2]: https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CustomOriginConfig.html?utm_source=chatgpt.com "CustomOriginConfig - Amazon CloudFront"
[3]: https://repost.aws/knowledge-center/cloudfront-custom-origin-response?utm_source=chatgpt.com "Increase custom origin response time in CloudFront"
[4]: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudfront_distribution?utm_source=chatgpt.com "aws_cloudfront_distribution | Resources | hashicorp/aws"
[5]: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/InvalidationLimits.html?utm_source=chatgpt.com "Concurrent invalidation request maximum"
[6]: https://docs.aws.amazon.com/apigateway/latest/developerguide/limits.html?utm_source=chatgpt.com "Amazon API Gateway quotas"
[7]: https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-execution-service-limits-table.html?utm_source=chatgpt.com "Quotas for configuring and running a REST API in API ..."
[8]: https://repost.aws/knowledge-center/api-gateway-504-errors?utm_source=chatgpt.com "Troubleshoot API Gateway HTTP 504 timeout errors"
[9]: https://docs.aws.amazon.com/general/latest/gr/apigateway.html?utm_source=chatgpt.com "Amazon API Gateway endpoints and quotas"
[10]: https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/process-events-asynchronously-with-amazon-api-gateway-and-aws-lambda.html?utm_source=chatgpt.com "Process events asynchronously with Amazon API Gateway ..."
[11]: https://aws.plainenglish.io/beyond-the-10mb-limit-the-smart-way-to-handle-file-uploads-in-aws-dfeb2ee08724?utm_source=chatgpt.com "Beyond the 10MB Limit: The Smart Way to Handle File ..."
[12]: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html?utm_source=chatgpt.com "Best practices for designing and using partition keys ..."
[13]: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Constraints.html?utm_source=chatgpt.com "Constraints in Amazon DynamoDB - AWS Documentation"
[14]: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ServiceQuotas.html?utm_source=chatgpt.com "Quotas in Amazon DynamoDB - AWS Documentation"
[15]: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/burst-adaptive-capacity.html?utm_source=chatgpt.com "DynamoDB burst and adaptive capacity"
[16]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html "Best practices design patterns: optimizing Amazon S3 performance - Amazon Simple Storage Service"
[17]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance-guidelines.html?utm_source=chatgpt.com "Performance guidelines for Amazon S3"
[18]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/upload-objects.html?utm_source=chatgpt.com "Uploading objects - Amazon Simple Storage Service"
[19]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/qfacts.html?utm_source=chatgpt.com "Amazon S3 multipart upload limits"
[20]: https://docs.aws.amazon.com/cognito/latest/developerguide/quotas.html "Quotas in Amazon Cognito - Amazon Cognito"
[21]: https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html?utm_source=chatgpt.com "AWS service quotas - AWS General Reference"


