"""Pueue上で、上限付きの実験セッションと終了後要約を順に接続する。"""

from __future__ import annotations

import argparse
import fcntl
import json
from pathlib import Path
import shlex
import subprocess
import sys
import time

SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'properties': {
        'action': {'type': 'string', 'enum': ['queued', 'stop']},
        'summary_job': {'type': ['integer', 'null']},
        'reason': {'type': 'string'},
    },
    'required': ['action', 'summary_job', 'reason'],
}


def save(path: Path, state: dict) -> None:
    """中途半端なJSONを残さず保存する。"""
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def pueue(*args: str) -> str:
    return subprocess.check_output(['pueue', *args], text=True).strip()


def queue_state() -> dict:
    return json.loads(pueue('status', '--json'))


def stop_requested(path: Path) -> bool:
    return path.with_suffix('.stop').exists()


def wait_summary(path: Path, state: dict, job: int) -> bool:
    """要約の成功を待つ。失敗・欠落を成功へ読み替えない。"""
    while True:
        if stop_requested(path):
            return False
        task = queue_state()['tasks'].get(str(job))
        if task is None:
            raise RuntimeError(f'要約job {job}が見つかりません')
        if task['group'] == state['group']:
            raise RuntimeError('要約jobと制御jobが同じgroupです')
        status = task['status']
        if isinstance(status, dict) and 'Done' in status:
            done = status['Done']
            result = done.get('result') if isinstance(done, dict) else done
            if result != 'Success':
                raise RuntimeError(f'要約job {job}が失敗: {status}')
            return True
        time.sleep(5)


def session(path: Path, state: dict, iteration: dict) -> dict:
    """既存設定を使って新規セッションを起動し、引継ぎだけを取得する。"""
    schema_path = path.parent / 'handoff.schema.json'
    schema_path.write_text(json.dumps(SCHEMA))
    result_path = path.parent / f"round-{iteration['number']}.json"
    if result_path.exists():
        raise RuntimeError('今回の引継ぎファイルが既にあります。重複起動を確認してください')
    prompt = (
        f'$automating-experiments の「各セッションの仕事」を実行してください。'
        f'状態は{path}、今回は{iteration["number"]}/{state["rounds"]}回目です。'
        f'ユーザーが許可した範囲: {state["scope"]}\n'
        f'制御group {state["group"]}は待機用です。実験・評価・要約を入れないでください。'
        '追加検証は最大1件。通常の終了後要約jobを登録して、そのIDを返してください。'
        'このループのstart/workerは呼ばず、状態ファイルを変更しないでください。'
        '停止する場合はaction=stop、summary_job=nullと理由を返してください。'
    )
    command = ['codex', 'exec', '--approve-for-me', '-C', state['repo'], '--json',
               '--output-schema', str(schema_path), '-o', str(result_path), prompt]
    with subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, text=True) as process:
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end='', flush=True)
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get('type') == 'thread.started':
                iteration['thread_id'] = event.get('thread_id')
                save(path, state)
        if process.wait() != 0:
            raise RuntimeError('Codexセッションが失敗しました。投入済みjobを確認してください')
    result = json.loads(result_path.read_text())
    if result.get('action') not in ('queued', 'stop') or not isinstance(result.get('reason'), str):
        raise RuntimeError('引継ぎ形式が不正です')
    if result['action'] == 'queued' and (type(result.get('summary_job')) is not int or result['summary_job'] < 0):
        raise RuntimeError('要約job IDが不正です')
    return result


def worker(path: Path) -> None:
    """状態ごとに一つだけ制御を動かす。再起動で投入を繰り返さない。"""
    with path.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = json.loads(path.read_text())
        if state['phase'] != 'queued':
            raise RuntimeError('新規queued状態だけ実行できます。再起動は自動では行いません')
        try:
            for number in range(1, state['rounds'] + 1):
                if stop_requested(path):
                    break
                iteration = {'number': number}
                state['iterations'].append(iteration)
                state['phase'] = 'running'
                save(path, state)
                existing_jobs = set(queue_state()['tasks'])
                handoff = session(path, state, iteration)
                if handoff['action'] == 'queued' and str(handoff['summary_job']) in existing_jobs:
                    raise RuntimeError('過去のjobが引継がれました。今回の要約jobを確認してください')
                iteration.update(handoff)
                state['phase'] = 'waiting' if handoff['action'] == 'queued' else 'stopped'
                state['reason'] = handoff['reason']
                save(path, state)
                if handoff['action'] == 'stop':
                    return
                if not wait_summary(path, state, handoff['summary_job']):
                    break
                iteration['summary_succeeded'] = True
                save(path, state)
            state['phase'] = 'stopped' if stop_requested(path) else 'complete'
            state['reason'] = 'ユーザーの停止要求' if stop_requested(path) else '指定回数の検証と要約が終了'
        except Exception as error:
            state['phase'] = 'failed'
            state['reason'] = str(error)
            raise
        finally:
            save(path, state)


def start(args: argparse.Namespace) -> None:
    path = args.state.resolve()
    repo = args.repo.resolve()
    if not repo.is_dir() or not path.is_relative_to(repo):
        raise ValueError('状態ファイルは対象repository内に置いてください')
    if args.rounds < 1 or not args.scope.strip():
        raise ValueError('正の上限回数と許可範囲が必要です')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if path.exists() or stop_requested(path):
            raise ValueError('状態が既にあります。新しい識別名を使ってください')
        groups = queue_state()['groups']
        if args.group not in groups:
            pueue('group', 'add', args.group)
        elif groups[args.group]['parallel_tasks'] != 1:
            raise ValueError('制御専用の並列数1のgroupを使ってください')
        state = {'repo': str(repo), 'scope': args.scope, 'rounds': args.rounds,
                 'group': args.group, 'phase': 'starting', 'iterations': []}
        save(path, state)
        command = shlex.join([sys.executable, str(Path(__file__).resolve()), 'worker', '--state', str(path)])
        try:
            state['job_id'] = int(pueue('add', '--print-task-id', '--group', args.group,
                                        '--working-directory', str(repo), '--label', 'automatic-experiments', command))
            state['phase'] = 'queued'
        except Exception:
            state['phase'] = 'failed'
            state['reason'] = '制御job登録失敗。Pueueを確認してから再開してください'
            raise
        finally:
            save(path, state)
    print(json.dumps(state, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('start', 'worker', 'status', 'stop'):
        child = sub.add_parser(command)
        child.add_argument('--state', type=Path, required=True)
        if command == 'start':
            child.add_argument('--repo', type=Path, required=True)
            child.add_argument('--scope', required=True)
            child.add_argument('--rounds', type=int, default=3)
            child.add_argument('--group', default='experiment-automation')
    args = parser.parse_args()
    path = args.state.resolve()
    if args.command == 'start':
        start(args)
    elif args.command == 'worker':
        worker(path)
    else:
        state = json.loads(path.read_text())
        if args.command == 'stop':
            path.with_suffix('.stop').touch()
            print('次回以降のセッションを停止します。開始済みの処理は続きます。')
        else:
            if 'job_id' in state:
                task = queue_state()['tasks'].get(str(state['job_id']))
                state['controller_task'] = (
                    {key: task.get(key) for key in ('id', 'group', 'status')} if task else None
                )
            state['stop_requested'] = stop_requested(path)
            print(json.dumps(state, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
