# Run Lifecycle

## Identity

Experiment identityを、検証する仮説、入力、split、意味上の変更で定義する。Attempt/run identityを、そのexperimentを実行した個々の試行とresolved configに割り当てる。同じexperimentでもattempt/run IDは一意にする。

仮説が同じretryではexperiment IDを維持する。新しいattempt/run IDを発行し、旧outputを失敗attemptとして退役またはarchiveしてから、空のcanonical outputへ実行する。仮説または意味上の比較対象が変わる場合だけ新experimentにする。

## GPU Resource Contract

複数GPUマシンでは、ユーザーから別の明示的な指示がない限り、Pueueを既定として複数experiment、fold、trialを独立した1-GPU jobで実行する。GPUが複数あることを理由に、DDP、DataParallel、model sharding、1 jobでの複数GPU利用を選ばない。

投入前にGPUの台数、model、VRAM、稼働状況と、Pueueのgroup、`parallel`、既存の投入wrapperを検査する。GPUごとに固定groupを1つ対応させ、各groupを`parallel=1`にする。投入wrapperまたはtaskの環境で対応GPUを`CUDA_VISIBLE_DEVICES`へbindし、すべてのGPU jobを対応group経由に統一する。

```bash
pueue add --group gpu-0 --label 042-attempt-01 \
  'CUDA_VISIBLE_DEVICES=0 uv run python scripts/train.py experiment=042_full_ft'
```

Repository固有のgroup名、entrypoint、config overrideに置き換える。Pueue groupはそれ自体ではGPUをbindせず、`parallel=1`も同じgroup内だけを制限する。複数groupを同じGPUへ対応させたり、group外から直接GPU jobを起動したりすると相互排他が崩れる。Pueueが未設定なら勝手にDDPや直接実行へ切り替えず、必要なgroupとbinding方法を提案して未実行とする。

AttemptごとにPueue job ID、group、割当GPU、GPU model、host、launch commandをresolved configまたはrun記録へ残す。同じexperimentのretryを別GPUへ移す場合も、experiment IDを維持して新attemptとし、旧attemptの出力を混在させない。

ユーザーがDDPまたは1 jobでの複数GPU利用を明示的に指示した場合だけ、repositoryの対応状況と比較条件への影響を別途調査して設計する。この指示がない状態でdistributed実行を実装、設定、投入しない。

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
