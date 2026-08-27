# Deployment Selection

## 原則

Viewer本体を特定のingressやhostへ結合しない。配信は利用者の要求、既存infra、security境界を確認してから最小構成を選ぶ。Tailscaleは任意であり、利用可能な場合だけ候補にする。

## Capability discovery

変更前にread-onlyで確認する。

- repositoryのMakefile、compose、service、hosting設定
- 稼働中process、使用中port、base path
- `tailscale`、Docker、Podman、systemd、Caddy、nginx等が利用可能か
- localのみ、private network、LAN、public internetのどこから閲覧するか
- 認証、TLS、秘密情報、データ持出しの制約

toolが存在するだけで採用しない。既存運用が正常なら、その経路を優先する。

## Selection table

| 要求 | 最小候補 | 注意点 |
|---|---|---|
| 同一PCだけ | loopback bind | `127.0.0.1`を既定にする |
| 一時的に別PCから | SSH tunnel | serverを直接公開しない |
| private network共有 | 既存VPNまたはTailscale Serve | 利用可能性と既存routeを確認する |
| LAN共有 | 明示host bind＋firewall | 認証要否と到達範囲を確認する |
| public公開 | 認証・TLS付きreverse proxyまたはhosting platform | backendを無認証で直接公開しない |
| 環境間移植 | 再現可能なbuildと環境変数 | containerは必要な場合だけ使う |

## Tailscale

private共有が必要で、Tailscaleが利用可能なら既存Serve設定を確認する。他のrouteを上書きせず、loopback上のViewerへproxyする。Funnelはpublic公開の明示要求がない限り使わない。

Tailscaleがない環境では未完成扱いにしない。SSH tunnel、既存VPN、reverse proxy、hosting platformなど、要求に合う別経路を選ぶ。

## Portable runtime

- data root、outputs root、host、port、base pathを環境変数または引数で設定する。
- frontendへhost側の絶対pathを埋め込まない。
- productionでNode runtimeを残すか、build済みassetをbackendへ同梱するかは既存運用へ合わせる。
- container、systemd unit、platform configを最初から全部作らない。
- 異なるarchitectureがscopeでなければmulti-architecture imageを要求しない。

## Remote security

- filesystem path、traceback、source map、秘密情報をresponseとbrowser consoleへ出さない。
- publicまたは広いLANでは認証とTLSを設ける。
- data directoryを静的配信rootとして丸ごと公開しない。
- write endpointやjob controlを閲覧APIへ追加しない。
- reverse proxy使用時はtrusted proxy、base path、websocket、cache headerを確認する。

## Verification

healthのHTTP 200だけでは完了ではない。

1. local originで実データを描画する。
2. 選択、filter、URL再読込、mobile操作を確認する。
3. remote scopeがある場合はremote URLでも同じ内容を確認する。
4. browser console、failed request、base-path崩れ、横overflowを確認する。
5. response、HTML、JavaScript、errorへhost filesystem pathが出ていないことを確認する。
6. service再起動後にも同じ経路で復旧することを確認する。
