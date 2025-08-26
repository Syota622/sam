# AWS主要サービスの性能制限比較表

## CloudFront

| 項目 | デフォルト値 | 最大値 | 緩和可否 | 東京リージョン | オレゴンリージョン | メトリクス監視 |
| --- | --- | --- | --- | --- | --- | --- |
| リクエストレート | 10,000 RPS/ディストリビューション | 250,000 RPS | 可能 | グローバルサービスのため同一 | グローバルサービスのため同一 | **Requests**: 全リクエスト数<br>**BytesDownloaded**: クライアントへの転送バイト数<br>**BytesUploaded**: オリジンへの転送バイト数 |
| 転送レート | 40 Gbps | 150 Gbps | 可能 | グローバルサービスのため同一 | グローバルサービスのため同一 | **BytesDownloaded**: ダウンロード転送量（バイト）<br>**BytesUploaded**: アップロード転送量（バイト） |
| オリジン応答タイムアウト | 30秒 | 180秒 | 可能（設定+申請） | グローバルサービスのため同一 | グローバルサービスのため同一 | **OriginLatency**: オリジンへのリクエスト応答時間（ミリ秒） |
| オリジンKeep-Aliveタイムアウト | 5秒 | 60秒 | 可能（設定変更） | グローバルサービスのため同一 | グローバルサービスのため同一 | **OriginLatency**: オリジン接続の応答時間（ミリ秒） |
| キャッシュヒット率 | - | - | - | グローバルサービスのため同一 | グローバルサービスのため同一 | **CacheHitRate**: キャッシュヒット率（%） |
| エラー率 | - | - | - | グローバルサービスのため同一 | グローバルサービスのため同一 | **4xxErrorRate**: 4xxエラー率（%）<br>**5xxErrorRate**: 5xxエラー率（%） |

## API Gateway (REST API)

| 項目 | デフォルト値 | 最大値 | 緩和可否 | 東京リージョン | オレゴンリージョン | メトリクス監視 |
| --- | --- | --- | --- | --- | --- | --- |
| スロットリングレート | 10,000 RPS | 10,000 RPS以上 | 可能 | 10,000 RPS | 10,000 RPS | **Count**: API呼び出し総数<br>**4XXError**: クライアントエラー数<br>**5XXError**: サーバーエラー数 |
| バーストレート | 5,000リクエスト | 5,000リクエスト以上 | 可能 | 5,000 | 5,000 | **ConcurrentExecutions**: 同時実行数 |
| ペイロードサイズ（リクエスト） | 10MB | 10MB | 不可 | 10MB | 10MB | - |
| ペイロードサイズ（レスポンス） | 10MB | 10MB | 不可 | 10MB | 10MB | - |
| 統合タイムアウト | 29秒 | 29秒 | 不可 | 29秒 | 29秒 | **IntegrationLatency**: バックエンド統合の応答時間（ミリ秒）<br>**Latency**: リクエスト全体のレイテンシー（ミリ秒） |

## DynamoDB

| 項目 | デフォルト値 | 最大値 | 緩和可否 | 東京リージョン | オレゴンリージョン | メトリクス監視 |
| --- | --- | --- | --- | --- | --- | --- |
| 読み込みキャパシティユニット（RCU）/テーブル | 40,000 | 40,000以上 | 可能 | 40,000 | 40,000 | **ConsumedReadCapacityUnits**: 消費された読み込みキャパシティ<br>**ProvisionedReadCapacityUnits**: プロビジョンされた読み込みキャパシティ |
| 書き込みキャパシティユニット（WCU）/テーブル | 40,000 | 40,000以上 | 可能 | 40,000 | 40,000 | **ConsumedWriteCapacityUnits**: 消費された書き込みキャパシティ<br>**ProvisionedWriteCapacityUnits**: プロビジョンされた書き込みキャパシティ |
| オンデマンドピーク読み込み | 40,000 RRU/秒 | 上限緩和可能 | 可能 | 40,000 RRU/秒 | 40,000 RRU/秒 | **AccountProvisionedReadCapacityUtilization**: アカウント全体の読み込みキャパシティ使用率（%） |
| オンデマンドピーク書き込み | 40,000 WRU/秒 | 上限緩和可能 | 可能 | 40,000 WRU/秒 | 40,000 WRU/秒 | **AccountProvisionedWriteCapacityUtilization**: アカウント全体の書き込みキャパシティ使用率（%） |
| アイテムサイズ | 400KB | 400KB | 不可 | 400KB | 400KB | - |
| バッチ書き込みアイテム数 | 25 | 25 | 不可 | 25 | 25 | - |
| トランザクションアイテム数 | 100 | 100 | 不可 | 100 | 100 | - |
| スロットリングイベント | - | - | - | - | - | **UserErrors**: リクエストエラー数（スロットリング含む）<br>**SystemErrors**: システムエラー数 |
| レイテンシー | - | - | - | - | - | **SuccessfulRequestLatency**: 成功したリクエストのレイテンシー（ミリ秒） |

## S3

| 項目 | デフォルト値 | 最大値 | 緩和可否 | 東京リージョン | オレゴンリージョン | メトリクス監視 |
| --- | --- | --- | --- | --- | --- | --- |
| リクエストレート（GET/HEAD） | 5,500 RPS/プレフィックス | 5,500 RPS以上 | 自動スケール | 5,500 RPS | 5,500 RPS | **AllRequests**: 全リクエスト数<br>**GetRequests**: GETリクエスト数<br>**HeadRequests**: HEADリクエスト数 |
| リクエストレート（PUT/COPY/POST/DELETE） | 3,500 RPS/プレフィックス | 3,500 RPS以上 | 自動スケール | 3,500 RPS | 3,500 RPS | **PutRequests**: PUTリクエスト数<br>**PostRequests**: POSTリクエスト数<br>**DeleteRequests**: DELETEリクエスト数 |
| リクエストレート（LIST） | 5,500 RPS/プレフィックス | 5,500 RPS以上 | 自動スケール | 5,500 RPS | 5,500 RPS | **ListRequests**: LISTリクエスト数 |
| マルチパートアップロード並列数 | 10,000パーツ | 10,000パーツ | 不可 | 10,000 | 10,000 | - |
| 転送速度（単一接続） | - | 10 Gbps程度 | ネットワーク依存 | 東京リージョン内 | オレゴンリージョン内 | **BytesDownloaded**: ダウンロードバイト数<br>**BytesUploaded**: アップロードバイト数 |
| レイテンシー | - | - | - | - | - | **FirstByteLatency**: 最初のバイトまでのレイテンシー（ミリ秒）<br>**TotalRequestLatency**: リクエスト全体のレイテンシー（ミリ秒） |
| エラー率 | - | - | - | - | - | **4xxErrors**: 4xxエラー数<br>**5xxErrors**: 5xxエラー数 |

## Cognito

| 項目 | デフォルト値 | 最大値 | 緩和可否 | 東京リージョン | オレゴンリージョン | メトリクス監視 |
| --- | --- | --- | --- | --- | --- | --- |
| UserAuthentication API呼び出しレート | 25 RPS | 120 RPS | 可能 | 25 RPS | 25 RPS | **SignUpSuccesses**: サインアップ成功数<br>**SignInSuccesses**: サインイン成功数 |
| UserCreation/Read/Update APIレート | 15 RPS | 50 RPS | 可能 | 15 RPS | 15 RPS | **AccountTakeOverRisk**: アカウント乗っ取りリスク検出数<br>**CompromisedCredentialsRisk**: 漏洩した認証情報リスク検出数 |
| UserList/Search APIレート | 5 RPS | 30 RPS | 可能 | 5 RPS | 5 RPS | - |
| AdminInitiateAuth APIレート | 30 RPS | 120 RPS | 可能 | 30 RPS | 30 RPS | **SignInSuccesses**: 認証成功回数<br>**SignInThrottles**: 認証スロットリング発生数 |
| トークン検証レート | 無制限 | 無制限 | - | 無制限 | 無制限 | **TokenRefreshSuccesses**: トークン更新成功数<br>**TokenRefreshFailures**: トークン更新失敗数 |
| フェデレーション認証レート | 25 RPS | 25 RPS | 可能 | 25 RPS | 25 RPS | **FederationSuccesses**: フェデレーション成功数<br>**FederationFailures**: フェデレーション失敗数 |
| スロットリング | - | - | - | - | - | **ThrottledCount**: スロットリング発生数 |

## 注記

- **緩和可否**: 「可能」= AWSサポートへの申請により緩和可能、「不可」= ハードリミット（緩和不可）、「自動スケール」= 自動的に拡張
- **東京とオレゴンの違い**: 基本的にサービスクォータは全リージョン共通。CloudFrontはグローバルサービスのため地域差なし
- **RPS**: Requests Per Second（秒間リクエスト数）
- **RCU/WCU**: Read/Write Capacity Units（4KB単位の読み書き性能）
- **RRU/WRU**: Read/Write Request Units（オンデマンドモードのリクエスト単位）
- **メトリクス**: CloudWatchで監視可能な主要メトリクス

## メトリクス監視の活用方法

### パフォーマンス監視のポイント

1. **スループット監視**
   - Requests、Count、AllRequestsなどでリクエスト数を監視
   - 制限値に対する使用率を把握

2. **レイテンシー監視**
   - Latency、IntegrationLatency、OriginLatencyで応答時間を監視
   - SLAやユーザー体験の管理

3. **エラー率監視**
   - 4xxErrors、5xxErrors、UserErrorsでエラー発生状況を監視
   - スロットリングやシステム問題の早期検知

4. **キャパシティ監視**
   - ConsumedCapacityUnits、ProvisionedCapacityUnitsで使用率を監視
   - 自動スケーリングのトリガー設定

## 性能最適化の推奨事項

1. **CloudFront**: キャッシュヒット率を80%以上に維持し、オリジンへの負荷を削減
2. **API Gateway**: キャッシング有効化とバーストトラフィックへの対策実施
3. **DynamoDB**: ホットパーティション回避とオンデマンドモードの活用検討
4. **S3**: プレフィックスの適切な設計とTransfer Accelerationの活用
5. **Cognito**: トークンキャッシングとバッチ処理によるAPI呼び出し削減

最新の情報や詳細な制限については、AWS公式ドキュメントの「Service Quotas」を参照することをお勧めします。