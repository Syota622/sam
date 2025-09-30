平素よりお世話になっております。
この度は回答までお時間をいただき、ありがとうございます。
下記にてお客様のお問い合わせを引用し回答いたします。

> 1.
> ZIPが利用できるとのことで、JMeterのZIP形式とはどのような利用ができるのでしょうか？
> jmxファイルのアップロード後にテストができることは確認済みでございます。
> ※下記は添付画像の記載
> >You can choose either a .$jmx file or a .zip file. Choose .zip file if you have any files to upload other than a .$jmx script file.

CSV ファイルを利用したりスクリプト内で利用するライブラリを jar ファイルとして利用する場合は、.jmx ファイルと一緒に zip ファイル化してアップロードいただけます。[1] 
なお、jmx ファイルのみを利用する場合は jmx ファイルを単体でアップロード可能でございます。

zip ファイルを使用される場合は、下記 3 点にご注意いただければと存じます。

1. zipファイル内で、最初に見つかった .jmx ファイルが JMeter スクリプトとして使用されます。[2] 
そのため、複数 .jmx ファイルを含めた場合、想定と異なる動作となる可能性がございますので 1 つだけ .jmx ファイルを含めることをご検討ください。

2. プラグインを含める場合は、バンドルされた zip ファイルの /plugins サブディレクトリに .jar ファイルを含める必要がございます。

3. 入力ファイルのパスは絶対パスでの指定ができず、相対パスで指定する必要がございます。

ガイド [3] の 15 ~ 16 ページにて DLT にて JMeter スクリプトを使用時の動作や注意点の記載がございますので、宜しければご参照ください。


> 2.
> jmxでは、スレッド数、Ramp-UP 期間、ループ回数の指定ができます。
> DLTの方では、Task CountやRamp-UPの指定が可能です。
> こちらはどのような仕組みなのでしょうか？
> たとえば、1 Taskあたり、jmxの「スレッド数、Ramp-UP 期間、ループ回数」が実行される。そのため、10 Taskであれば、「スレッド数、Ramp-UP 期間、ループ回数」✖️10処理されるなど。
> 上記例以外にも、DLTにはConcurrencyやRamp Up、Hold Forがあり、jmxで設定したものとどのような関係性なのかをご教示いただきたいです。

DLT の各パラメータは下記のように動作いたします。
- Task Count: 負荷テストにおいて利用するタスク数
- Concurrency: 各タスクにて起動するスレッド数
- Ramp Up: 指定した同時実行数に達するまでの時間
- Hold For: 設定した Task Count と Concurrency に到達した後、リクエストを実施する時間

Ramp Up で指定した時間をかけて Task Count と Concurrency の積の数のスレッドを作成し、Hold For で指定した時間、リクエストを次々と送るような挙動となります。

上記の DLT で指定するパラメータは Taurusの JMeter Executor [4] に渡される動作となります。
また JMeter Executor は JMeter のスレッドグループを書き換えて、JMeter シナリオ (jmx ファイル) に指定されたループ数などの設定値を一部上書きしているものとお見受けしております。[5]
本ソリューションで使用されている Taurus および JMeter [4] などは AWS が公式に開発・提供しておらず、サードパーティ製ソフトウェアサポートの対象外 [6] のため、Taurus および JMeter の仕様については各提供元にお問い合わせいただきますようお願いいたします。

実際の動作にご不安がございます場合には、ローカルで Taurus を動かすことや、シンプルな jmx シナリオから始めて徐々に複雑なシナリオをお試しいただくことをご検討いただけますと幸いです。


本回答についてご不明点がございましたらお気軽にご連絡ください。
何卒よろしくお願いいたします。


## 参考資料
[1] 負荷テスト on AWS のすすめ 第 3 回 : 負荷テストを準備・実施しよう
https://aws.amazon.com/jp/builders-flash/202311/distributed-test-on-aws-3/ 
[2] deployment/ecr/distributed-load-testing-on-aws-load-tester/load-test.sh
https://github.com/aws-solutions/distributed-load-testing-on-aws/blob/5f5e9fe071de777382d15213de96e80f73dad2ab/deployment/ecr/distributed-load-testing-on-aws-load-tester/load-test.sh#L45-L69 
[3] AWS での分散負荷テスト - 実装ガイド
https://d1.awsstatic.com/Solutions/ja_JP/distributed-load-testing-on-aws.pdf 
[4] JMeter Executor - Taurus
https://gettaurus.org/docs/JMeter/ 
[5] bzt/modules/jmeter.py
https://github.com/Blazemeter/taurus/blob/f86ba798c187a4259059dddb7e618f312d10dd1e/bzt/modules/jmeter.py 
[6] サードパーティソフトウェア - AWS サポートに関するよくある質問
https://aws.amazon.com/jp/premiumsupport/faqs/ 