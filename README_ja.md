# Schema Change Inspector

**2つのJSON Schemaの「入力受理の後方互換性」を検査し、判断できない変更を安全と断定しないローカルCLI。**

**v0.1.0 · 実験版 · Python 3.11以上 · 標準ライブラリのみ · MIT**

[English](README.md) | **日本語**

## 何を判定するか

旧スキーマで許容されるJSONインスタンスの集合を `L(old)`、新スキーマを `L(new)` としたとき、**`L(old) ⊆ L(new)`** が成り立つかを調べます。対象は入力受理の互換性だけで、**出力スキーマの互換性やOpenAPI全体の変更検査ではありません**。

対応済みの限定的なJSON Schema 2020-12サブセット内で包含の十分条件が成立すれば`NON_BREAKING`、旧版では有効・新版では無効な検証済み実例があれば`BREAKING`、証明も実例も得られない場合や未対応構文がある場合は`UNKNOWN`です。JSON Schema 2020-12の完全実装や完全な包含判定器ではありません。

## すぐ試す

Python 3.11以上が必要です。追加パッケージ、アカウント、通信接続は不要です。リポジトリのルートで実行します。

```sh
python sci.py --old samples/old.json --new samples/new.json --out example-breaking
python sci.py --old samples/new.json --new samples/old.json --out example-reverse
```

最初の例は旧版に存在しない必須項目`name`が新版で追加されるため、意図的に`BREAKING`（終了1）になります。出力先は毎回**新しいディレクトリ**を指定してください。既存ディレクトリへの保存は拒否します。Windowsでは`py -3`でも実行できます。

結果は標準出力のJSONと出力先の`report.json`に記録され、入力ファイルは変更しません。

| 判定 | 既定の終了コード | 意味 |
| --- | ---: | --- |
| `NON_BREAKING` | 0 | 対応サブセット内で包含の十分条件を証明 |
| `BREAKING` | 1 | 旧版で有効、新版で無効な具体的な反例を検証 |
| `UNKNOWN` | 2 | 互換性を確定できない。安全とは扱わない |
| `INVALID_SCHEMA` | 2 | 不正スキーマ・入力・環境・出力先などの問題 |

`--unknown allow`を明示すると、`UNKNOWN`の**表示は変えず終了コードだけ0**にできます。CIの例外ポリシーであり、安全の証拠ではありません。

## 対応範囲

`type`（unionとinteger/number関係を含む）、`properties`、`required`、有限の`enum`、真偽値の`additionalProperties`、入れ子object、null、真偽値スキーマ、`title`・`description`注釈などの限定条件を扱います。

`oneOf`、`allOf`、`anyOf`、`$ref`、`$dynamicRef`、`pattern`、`items`や複雑な配列制約などは**`UNKNOWN`**です。array型自体を扱えても要素の制約までは証明しません。外部参照の取得やコード生成・任意命令実行は行いません。

**FIX-01 数値精度の制約：** 元のJSON数値字句と、変換先binary64の数学的な値が完全に一致する場合のみ解析を継続します。`0.1`、`1.0000000000000001`、`1e-400`など、変換すると丸めや桁落ちが生じる数値は`UNSUPPORTED_NUMERIC_PRECISION`の`UNKNOWN`です。`1`と`1.0`は同値、`true`と`1`は別値、`1.5`は精確に扱えます。

数値トークン256文字、指数絶対値400かつ指数部4桁まで、整数128桁の上限があります。有効なJSON数値でも、この制限を超えるものは`UNKNOWN`です。NaNなどの非標準トークンと重複JSONキーは不正入力として拒否します。

**注意：** Pythonの`compare(old,new)`へ外部でデコードした辞書を渡すと、呼出側が先に失った数値精度を復元できません。数値精度を重視する場合は、本製品の`parse()`またはCLIを使用してください。

## レポートと検証

レポートには`classification`、`rule_id`、変更箇所のJSON Pointer、変更前後の値と、検証可能なら反例を含みます。JSON Pointerは変更位置を示すだけで、その行単独で破壊的変更を証明するものではありません。`counterexample_available`は反例なしとJSONの`null`反例を区別します。

受入済みFIX-01版には、**旧39件＋回帰14件＝53件の自動テスト**が含まれます。独立したLinux／Python 3.13.5で53件全件合格、数値境界と証拠保存の衝突条件も確認済みです。

```sh
python -m unittest discover -s tests -v
```

GitHub Actionsは**Ubuntu・Windows × Python 3.11／3.12／3.13**を対象とします。最新の実行結果は[Actions](https://github.com/KenKan964/schema-change-inspector/actions)で確認してください。`evidence/ci_status.json`は**リポジトリ登録前の履歴資料**であり、現時点のCI結果ではありません。

テスト証拠を保存する場合は、新しい`SCI_EVIDENCE`ディレクトリを指定します。既存ファイルやsymlinkがあるとテストは失敗し、証拠を上書きしません。敵対的な同時パス変更への完全な隔離までは保証しません。

## 安全性と限界

入力は各64KiB以下、字句nest32、スキーマnest12、objectごとのプロパティ16、反例探索深さ5・fuel2000などの制限があります。これらは悪意ある入力からの完全隔離を意味しません。

レポートには元スキーマ断片と反例が含まれるため、`enum`などへ機密情報を埋め込まないでください。**対応範囲外の互換性を`NON_BREAKING`とは断定しません**。既存OSSより優れた精度・開発工数削減・ROI・市場需要は実証されていません。

## 資料・ライセンス

[English](README.md) · [規則一覧](RULES.md) · [技術仕様](TECHNICAL_SPEC.md) · [セキュリティ](SECURITY.md) · [OSS比較](OSS_COMPARISON.md) · [FIX-01](FIX01_CHANGES.md) · [開発報告](REPORT_ja.md) · [変更履歴](CHANGELOG.md) · [MITライセンス](LICENSE)

**ライセンス：** MIT · Copyright (c) 2026 KenKan964。
