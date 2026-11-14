# Stable rules v1

|規則ID|意味|
|---|---|
|SUBSET_SUFFICIENT_PROOF|対応サブセット内で包含の十分条件成立|
|VALIDATED_COUNTEREXAMPLE|旧valid・新invalidの反例成立|
|INCLUSION_UNPROVEN|十分条件不成立、探索でも反例未生成|
|UNSUPPORTED_KEYWORD|未対応キーワードまたはdialect|
|INVALID_SCHEMA|既知構文の不正・構造/深さ制限|
|INPUT_OR_OUTPUT_ERROR|ファイル・JSON・出力先・引数異常|

report schema_version=sci-report-v1、rule_version=sci-rules-v1。
NON_BREAKINGの十分条件: old=falseまたはnew=true、old enum全値の受理、型集合包含、
objectではnew required⊆old required、各プロパティ/追加プロパティの再帰包含。
numberはintegerを含む。properties/requiredはobject以外に作用しない。
新enumは旧enumからの列挙証明がない限り一般に証明を行わず反例探索へ進む。
探索失敗はUNKNOWN。十分条件は完全な包含決定手続ではない。
JSON PointerはRFC6901の~0/~1をエスケープする。
変更項目はグローバルな判定と反例を共有する。個別ポインタ単独で破壊原因と断定しない。

UNSUPPORTED_NUMERIC_PRECISION: valid numeric syntax cannot be preserved within supported representation/limits; UNKNOWN, no witness. Default exit2, explicit unknown allow0.
