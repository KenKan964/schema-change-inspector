# OSS比較報告

一次資料を2026-11-14に参照。外部ツールの実行ベンチマークは未実施。

|対象|資料上の用途|今回の位置づけ|
|---|---|---|
|oasdiff|OpenAPIのAPI変更とbreaking/changelog検査|OpenAPI全体を扱う既存方式。SCIは上位互換を主張しない|
|getsentry/json-schema-diff|JSON Schema間の変更差分|同じ領域に既存OSSがある。SCIの原理の新規性は未実証|
|SCI|標準Pythonだけの明示サブセット、入力集合包含、検証反例、UNKNOWN|39件のローカル受入試験を実行|

https://github.com/oasdiff/oasdiff/blob/main/docs/BREAKING-CHANGES.md
https://github.com/getsentry/json-schema-diff
https://json-schema.org/specification

直接比較の精度、性能、工数は未測定。対応範囲の狭さと保守的UNKNOWNを特徴として明示する。
実装可能な同等手段を排除せず、包括的な互換性診断性能や工数削減率・ROI・需要を主張しない。
