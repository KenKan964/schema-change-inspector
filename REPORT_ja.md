# SCI-DEV-001 / FIX-01 是正報告 2026-11-14

2項目を限定修正し独立再審査へ提出。一般公開HOLD。
既存39ケースの入力・期待値を保持し、回帰14件を追加、Python3.13.5/3.12.14で各53/53、skip0。
証拠はtests313.log/tests312.logと各acceptanceディレクトリ。

証拠出力は排他open x。既存required.json、file symlink、directory symlink・祖先を拒否。
衝突はテスト非ゼロ終了、保護対象hash不変。新規先では実際に証拠保存して全件PASS。
元39件PASSのまま上書きする現象も隔離markerで再現し、before/after_conflictへ保存。

数値は選択肢B。元の十進数をDecimalで確認しbinary64の数学的値と厳密一致する場合だけ解析を継続。
NP01〜04は修正前NON_BREAKING/0→修正後UNKNOWN/2。正確な原文と結果はnumeric_before_after.json。
1と1.0は同値、trueと1は異型、1.5は正確に扱えて反例を生成可能。新たな虚偽反例を生成しない。
数値未対応rule_idはUNSUPPORTED_NUMERIC_PRECISION。UNKNOWN allowだけ明示的に終了0、分類はUNKNOWN。
数値token256文字、指数絶対400/指数桁4、整数128桁の制限。超過した有効数値もUNKNOWN。
0.1等の一般的な非二進有理小数もUNKNOWNになる保守的制約をREADMEで明記。
Python辞書APIは呼出側で失われた数値精度を復元できない。原文検査は付属parse/CLIを使う。
false/trueスキーマ、null反例、入れ子、required、enum拡大縮小、未知構文UNKNOWNは従来試験で維持。

JSON Schema完全実装や包含完全決定を主張しない。安全条件/スキーマ機能の全面再設計はしていない。
6環境CIはGitHub登録後の独立確認が残るため全件NOT_RUN。コード修正のみでCI成功としない。
研究継続GO、公開HOLD、独立再審査待ち。工数削減・ROI・商用需要・総合性能優位は未実証。
全ソース・CLI証拠・ログ・変更一覧・日英README・仕様・両ZIPと全ファイルhashを提出。
各MANIFEST.sha256は自己ファイルを除外して生成・照合済み。
