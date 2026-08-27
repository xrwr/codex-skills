# Run Lifecycle

## Identity

Experiment identityを、検証する仮説、入力、split、意味上の変更で定義する。Attempt/run identityを、そのexperimentを実行した個々の試行とresolved configに割り当てる。同じexperimentでもattempt/run IDは一意にする。

仮説が同じretryではexperiment IDを維持する。新しいattempt/run IDを発行し、旧outputを失敗attemptとして退役またはarchiveしてから、空のcanonical outputへ実行する。仮説または意味上の比較対象が変わる場合だけ新experimentにする。

## Artifact Evidence

依頼とrepositoryから、必要artifact contractを先に確定する。YAML、job、process終了、checkpointの存在だけでexperimentをcompleteまたはverifiedにしない。Artifactのrun ID、resolved config、log、timestamp、生成記録を照合し、current attemptへ帰属できる証拠だけを使う。

| 状態 | 必要な証拠 |
|---|---|
| `queued` | Queueへ登録済みで、開始していない記録 |
| `running` | Current attemptのactive processまたは更新中のlog |
| `failed` | Current attemptのerror、非正常終了、または失敗記録 |
| `partial` | 帰属確認済みartifactはあるが、必要artifact contractが未充足 |
| `verified` | 必要artifactがすべて存在し、検証済みで、current attemptへ帰属する |
| `unknown` | 証拠がない、古い、または相互に矛盾する |

Job manager、tracking service、framework固有の状態は、それらがrepositoryで既存かつ利用可能な場合だけ補助証拠にする。

## Retry Procedure

1. 仮説、入力、split、意味上の変更が同じか確認する。
2. 旧attemptのresolved config、log、checkpoint、metricを記録する。
3. 旧outputをattempt ID付きの退役先へarchiveする。削除しない。
4. 同じexperiment IDと新attempt/run IDで、空のcanonical outputを使う。
5. 新artifactのprovenanceと必要artifact contractを再検証する。

依頼なしにrunをstart/stopせず、outputやartifactをdeleteしない。破壊的操作が必要なら対象と影響を示して承認を求める。
