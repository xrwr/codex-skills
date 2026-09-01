# Python Stack

## Selection Contract

Repositoryに既存のdependency declarationとlockfileがあれば、それを正本にする。Greenfieldでは`uv`をdefaultのenvironment・dependency managerとし、必要なlibraryだけを`pyproject.toml`へ追加して`uv.lock`へ解決結果を保存する。Library versionはこのreferenceへ固定しない。

次の表は一括installするbundleではない。現在のtaskに該当する行だけを選ぶ。

| Category | Default candidate | 選ぶ条件 | 追加しない条件 |
|---|---|---|---|
| Array・数値計算 | NumPy | ndarray interoperability、数値処理 | Python標準型だけで十分 |
| 表形式data | pandas | 一般的なtable IO・集計・ecosystem連携 | 表形式処理がない |
| 大規模table | Polars | lazy executionやcolumnar処理の利益を確認できる | pandasと併用する理由がない |
| 古典的ML | scikit-learn | baseline、preprocessing、CV、metric | 深層学習frameworkだけで完結する |
| 深層学習 | PyTorch | tensor modelとGPU trainingが必要 | 既存frameworkが別にある |
| Training framework | Lightning | loop、distributed、checkpoint処理が反復する | 小さなcustom loopで明瞭に保てる |
| Config composition | Hydra | task、component、experimentのcompositionが必要 | 単一configやCLI引数で十分 |
| Experiment tracking | W&B | 利用者またはrepositoryがrun trackingを採用する | local artifactだけが契約 |
| Test | pytest | Python behaviorを継続検証する | test対象のPython codeがない |
| Tensor typing | jaxtyping | module境界でshape・dtype contractが有用 | annotationが実装より複雑になる |
| Static plot | Matplotlib | artifactとして保存するfigure | 可視化要求がない |
| Statistical plot | seaborn | pandasベースの統計plotを簡潔に書く | Matplotlibだけで十分 |
| Interactive plot | Plotly | 少量のinteractive figureで目的を満たす | 本格的なviewerが必要 |
| Console UX | Rich | 長時間CLIのstatusやtable表示が必要 | 通常のloggingで十分 |

## Domain Libraries

Domain libraryはtaskが確定してから追加する。

| Domain | Candidate | Boundary |
|---|---|---|
| Image backbone | timm | model familyを実際に使う場合だけ |
| Language・multimodal model | Transformers | pretrained model/APIが必要な場合だけ |
| Image segmentation | segmentation-models-pytorch | 対応architectureを採用する場合だけ |
| Image augmentation | Albumentations | image transform pipelineが必要な場合だけ |

Optimizer packageや特定optimizerをproject-wide defaultにしない。Optimizer、scheduler、lossは比較するexperimentの設定として所有させる。Viewerやapplication frameworkもdata-science projectへ自動追加せず、実際のdelivery surfaceから選ぶ。

## Python Conventions

- Repositoryのsupported Python versionを`pyproject.toml`へ宣言し、必要なら`.python-version`を揃える。
- `dict`、`list`、`tuple`など組み込みgenericを使い、対応versionで不要な`typing.Dict`等を増やさない。
- Tensor shapeがinterface contractになる箇所ではjaxtypingを使えるが、内部の一時変数まで過剰に注釈しない。
- Dependency追加後はlockfile、import、最小entrypointまたは対象testを同じenvironmentで確認する。
