了解です。主要な“性能・スループット系”の値と「デフォルト／Max（上限）／増枠や回避可否／東京(ap-northeast-1)とオレゴン(us-west-2)の違い」を、サービスごとにMarkdown表で整理しました。必要なところはAWS公式の根拠も付けています。

# CloudFront

| 項目                                  |                      デフォルト値 |                               Max/上限 | 緩和・増枠可否                                                   | 東京 vs オレゴン          |
| ----------------------------------- | --------------------------: | -----------------------------------: | --------------------------------------------------------- | ------------------- |
| リクエスト数（RPS）/ディストリビューション             |                 250,000 RPS |                             増枠で引き上げ可 | **可**（Service Quotasで申請） ([AWS ドキュメント][1])                | グローバルサービスのため同一（差なし） |
| 転送レート/ディストリビューション                   |                    150 Gbps |                             増枠で引き上げ可 | **可**（申請） ([AWS ドキュメント][1])                               | 同一                  |
| オリジン応答タイムアウト（OriginReadTimeout）     |                         30秒 | 1–120秒（設定範囲）、一部ナレッジでは**最大180秒まで増枠可** | 設定で変更可／**更なる増枠は申請** ([AWS ドキュメント][2], [Repost][3])        | 同一                  |
| オリジンKeep-Aliveタイムアウト（Custom Origin） |                          5秒 |                                  60秒 | 設定で変更可（S3オリジンを除く） ([AWS ドキュメント][2], [Terraform レジストリ][4]) | 同一                  |
| 同時インバリデーション件数（進行中）                  | 個別パス合計3,000ファイル、ワイルドカード15パス |                                   固定 | **不可**（設計で回避） ([AWS ドキュメント][5])                           | 同一                  |

> 補足：CloudFrontは自動スケールで“プレウォーム不要”。RPSやスループットは増枠申請＋キャッシュ/TTL設計で緩和可能です。([AWS ドキュメント][1])

---

# API Gateway

| 項目                              |                デフォルト値 |            Max/上限 | 緩和・増枠可否                                                    | 東京 vs オレゴン                                                          |
| ------------------------------- | --------------------: | ----------------: | ---------------------------------------------------------- | ------------------------------------------------------------------- |
| アカウント単位のスロットリング（RPS/Region）     | 10,000 RPS（バースト5,000） |             申請で増枠 | **可**（Service Quotas） ([AWS ドキュメント][6])                    | **同一**（どちらも標準の10k/5k。※一部新規リージョンのみ2,500/1,250の例あり） ([AWS ドキュメント][6]) |
| 統合タイムアウト（REST：Regional/Private） |                   29秒 | **29秒超に延長可**（要調整） | **可**（>29秒へ延長可。RPS上限の引き下げとトレードオフになる場合あり） ([AWS ドキュメント][7]) | 同一                                                                  |
| 統合タイムアウト（HTTP API）              |                  ～30秒 |               30秒 | **不可**（設計で回避） ([Repost][8])                                | 同一                                                                  |
| ペイロードサイズ（REST/HTTP、非WebSocket）  |                 10 MB |             10 MB | **不可**（S3直PUT等で回避） ([AWS ドキュメント][9])                       |                                                                     |

> 回避例：大きな処理はStep Functions等で**非同期化**、大容量アップロードは**S3プリサインURL**を利用。([AWS ドキュメント][10], [AWS in Plain English][11])

---

# DynamoDB

| 項目                      |                  デフォルト値 | Max/上限 | 緩和・増枠可否                                                   | 東京 vs オレゴン |
| ----------------------- | ----------------------: | -----: | --------------------------------------------------------- | ---------- |
| パーティション当たりの最大スループット     |   3,000 RCU / 1,000 WCU |     固定 | **不可**（ハード制限。キー設計/シャーディングで緩和） ([AWS ドキュメント][12])          | 同一         |
| アイテムサイズ                 |             400 KB/アイテム | 400 KB | **不可**（S3へ本体、DynamoDBにポインタで緩和） ([AWS ドキュメント][13])         | 同一         |
| テーブルあたりスループット上限（初期クォータ） | 40,000 RRU / 40,000 WRU |  申請で増枠 | **可**（Service Quotas。オンデマンド/プロビジョンド双方） ([AWS ドキュメント][14]) |            |

> 補足：トラフィック偏りは**アダプティブキャパシティ**で一部救済されますが、基本は**良いパーティションキー設計**が前提です。([AWS ドキュメント][15])

---

# S3

| 項目                       |                      デフォルト値 |                   Max/上限 | 緩和・増枠可否                                     | 東京 vs オレゴン                                  |
| ------------------------ | --------------------------: | -----------------------: | ------------------------------------------- | ------------------------------------------- |
| リクエストレート（1プレフィックスあたりの目安） | ≥ 3,500 書込系 / 5,500 読取系 RPS |      プレフィックスを増やして水平方向に拡張 | **設計で緩和**（プレフィックス分割・並列化） ([AWS ドキュメント][16]) | 同一（レイテンシは地理で差。遠距離はTAで緩和） ([AWS ドキュメント][17]) |
| オブジェクトサイズ（単一PUT）         |                       ～5 GB |                     5 GB | **不可**（マルチパート推奨） ([AWS ドキュメント][18])         | 同一                                          |
| オブジェクトサイズ（マルチパート）        |                           – |                    ～5 TB | **不可**（仕様） ([AWS ドキュメント][19])               |                                             |
| 長距離転送の性能                 |                        通常転送 | Transfer Accelerationで改善 | **機能で緩和**（有効化するだけ） ([AWS ドキュメント][17])       | **東京⇄オレゴン等の跨地域で効果大** ([AWS ドキュメント][17])     |

---

# Cognito（User Pools ほか）

| 項目（カテゴリー）                                      |         デフォルト値（RPS） | Max/上限 | 緩和・増枠可否                            | 東京 vs オレゴン                                     |
| ---------------------------------------------- | ------------------: | -----: | ---------------------------------- | ---------------------------------------------- |
| UserAuthentication（サインイン/トークン等）                |             120 RPS |  申請で増枠 | **可**（有償の増枠） ([AWS ドキュメント][20])    | **同一**（クォータはRegion毎だが数値は同じ） ([AWS ドキュメント][20]) |
| UserCreation（SignUp等）                          |              50 RPS |  申請で増枠 | **可** ([AWS ドキュメント][20])           | 同一                                             |
| UserRead                                       |             120 RPS |  申請で増枠 | **可** ([AWS ドキュメント][20])           | 同一                                             |
| UserAccountRecovery（ForgotPassword等）           |              30 RPS |     固定 | **不可**（設計で緩和） ([AWS ドキュメント][20])   | 同一                                             |
| Hosted UI ドメインのバルクリミット（1 IP / 1クライアント / 1ドメイン） | 300 / 300 / 500 RPS |     固定 | **不可**（WAF等で保護） ([AWS ドキュメント][20]) |                                                |

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
