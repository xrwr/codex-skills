---
name: summarizing-experiments
description: Use when summarizing or comparing repository experiments, interpreting their results, or reviewing the research direction and next verification from experiment evidence.
---

# Summarizing Experiments

## Overview

同じexperiment内のtrialを比較し、実験全体の仮説について何が分かり、次に何を確かめるかを、根拠に戻れる短いサマリにする。証拠・判定・表示形式は[report contract](references/report-contract.md)に従う。テーマ階層やtrialごとの説明ファイルは要求しない。

## Workflow

1. 既存の実験記録、config、評価・予測などの成果物を確認し、対象experiment、基準trial、fold、採用attemptと派生元を特定する。指標の解釈より先に、何を検証したい実験か、学習・調整・評価にどのデータを使ったかを調べ、その評価で言える範囲を定める。評価の妥当性が未確認なら、数値の増減から目的上の改善を結論づけない。
2. 実験全体の事前仮説・検証計画と複数trialの結果を照合し、効いた条件・効かなかった条件・未確認をまとめる。総合指標だけでは説明できない変化があれば、条件別の差、改善・悪化例、分布などから必要な追加分析を選ぶ。個別例の観察と集計を行き来し、根拠となる成果物やsample IDを残す。
3. 観察に合う説明を考え、別の原因や反例で区別できるかを検討する。因果を断定せず、不足する観測は不足として残す。
4. 関連実験の知見と照合し、全体の見立てを更新する。同じ失敗の反復や予想外の結果、方針の節目では、現在の解き方の前提や扱えていない情報まで見直す。必要なら元データやドメイン資料に戻る。
5. 次の推奨を根拠・予測・判定方法とともに示す。過去のexperimentへのtrial追加・retry・新experimentのどれに当たるかを検証計画と照合する。現在の方針を詰める検証と、前提を確かめる検証を考慮し、追加分析・判断保留・停止も選ぶ。短期のスコア改善や検証の安さだけで候補を選ばない。
6. experiment単位の同じ個別サマリと、全体の見立て・系統図・5列の一覧を更新する。各trialや再実行を全体一覧の別実験にしない。過去の提案を機械的に持ち越さず、今も有効かを確認する。冒頭は短くし、判断に必要な根拠と再現情報を後ろへ置く。

要約の依頼は、新たな学習・重い再評価・実験投入の許可ではない。依頼範囲の保存済み成果物の分析で不足する場合は、次の行動として記録する。
