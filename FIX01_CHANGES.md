# FIX-01変更と再現

1. tests/test_acceptance.py: preserve()導入、排他UTF8新規作成とsymlink祖先拒否。39ケースの入力・期待値は未変更。
2. sci.py: float直変換を十進数精度チェック付きhookへ置換。扱えない値はUNKNOWN専用reason/ruleを返す。
3. tests/test_fix01.py: 証拠競合3、NP4、allow、数値等値、bool区別、exact小数、巨大指数/整数、入れ子の計14件。
4. README日英・仕様・規則・SECURITY・CHANGELOG・報告を同期。正確なdiffはFIX01.patch。

通常: SCI_EVIDENCE=fresh python3.13 -m unittest discover -s tests -v
回帰: python3.13 -m unittest discover -s tests -p test_fix01.py -v
数値例: old={"enum":[1.0000000000000001]}, new={"enum":[1]}をUTF8ファイルへ保存し通常CLIで比較。
修正後UNKNOWN/2。--unknown allowでUNKNOWN表示のまま0。

競合: 一時領域のevidence/required.jsonへ合成markerを置き全discoverを実行。
旧版39PASSで上書き、修正版53件実行の非ゼロ・hash不変をbefore/after_conflictに保存。
file/dir symlink回帰も同じ前後hashを保存。既存ファイルを削除して成功させない。
numeric_before_after.jsonにNP4件の正確な入力文字列と旧/新CLI判定を保存。
旧成果物・旧証拠を改変せず別ディレクトリで是正。
