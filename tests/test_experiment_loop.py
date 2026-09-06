"""GPUを使わず、引継ぎの上限と停止条件を検証する。"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/automating-experiments/scripts/experiment_loop.py'
spec = importlib.util.spec_from_file_location('experiment_loop', SCRIPT)
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)


class ExperimentLoopTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'state.json'
        loop.save(self.path, {'repo': self.temp.name, 'group': 'controller',
                             'scope': 'CPU接続テスト', 'rounds': 3, 'phase': 'queued', 'iterations': []})
        self.jobs = {}
        self.calls = 0

    def state(self):
        return json.loads(self.path.read_text())

    def session(self, path, state, iteration):
        self.calls += 1
        self.jobs[str(self.calls)] = {
            'group': 'summaries',
            'status': {'Done': {'result': 'Success'}},
        }
        return {'action': 'queued', 'summary_job': self.calls, 'reason': '今回の要約'}

    def run_worker(self, session=None):
        with patch.object(loop, 'session', side_effect=session or self.session), patch.object(
            loop, 'queue_state', side_effect=lambda: {'tasks': self.jobs}
        ):
            loop.worker(self.path)

    def test_session_does_not_wait_for_open_parent_stdin(self):
        executable = Path(self.temp.name) / 'codex'
        executable.write_text("#!/usr/bin/env python3\n"
                              "import sys,json,pathlib\n"
                              "assert sys.stdin.read() == ''\n"
                              "p=pathlib.Path(sys.argv[sys.argv.index('-o')+1])\n"
                              "p.write_text(json.dumps({'action':'stop','summary_job':None,'reason':'接続確認'}))\n"
                              "print(json.dumps({'type':'thread.started','thread_id':'test-session'}))\n")
        executable.chmod(0o755)
        command = (
            'import importlib.util,json,pathlib; '
            f's=importlib.util.spec_from_file_location("loop",{str(SCRIPT)!r}); '
            'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); '
            f'p=pathlib.Path({str(self.path)!r}); state=json.loads(p.read_text()); '
            'i={"number":1}; state["iterations"].append(i); '
            'assert m.session(p,state,i)["action"]=="stop"'
        )
        env = dict(os.environ, PATH=self.temp.name + os.pathsep + os.environ['PATH'])
        # 親のstdinを開いたままにしても、子CodexはEOFを受けて終了する。
        with subprocess.Popen([sys.executable, '-c', command], env=env,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as process:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                self.fail('Codexが親stdinの入力待ちになりました')
            finally:
                process.stdin.close()
            self.assertEqual(process.returncode, 0, process.stderr.read().decode())
        self.assertEqual(self.state()['iterations'][0]['thread_id'], 'test-session')

    def test_round_limit_and_duplicate_execution(self):
        self.run_worker()
        self.assertEqual(self.calls, 3)
        self.assertEqual(self.state()['phase'], 'complete')
        self.assertTrue(all(i['summary_succeeded'] for i in self.state()['iterations']))
        with self.assertRaises(RuntimeError):
            self.run_worker()
        self.assertEqual(self.calls, 3)

    def test_failed_summary_prevents_next_session(self):
        def failing(*args):
            result = self.session(*args)
            self.jobs['1']['status']['Done']['result'] = {'Failed': 1}
            return result
        with self.assertRaises(RuntimeError):
            self.run_worker(failing)
        self.assertEqual(self.calls, 1)
        self.assertEqual(self.state()['phase'], 'failed')

    def test_stop_before_first_session(self):
        self.path.with_suffix('.stop').touch()
        self.run_worker()
        self.assertEqual(self.calls, 0)
        self.assertEqual(self.state()['phase'], 'stopped')

    def test_stop_after_current_session(self):
        def stopping(*args):
            result = self.session(*args)
            self.path.with_suffix('.stop').touch()
            return result
        self.run_worker(stopping)
        self.assertEqual(self.calls, 1)
        self.assertEqual(self.state()['phase'], 'stopped')

    def test_agent_stop_does_not_queue_another_session(self):
        self.run_worker(lambda *args: {'action': 'stop', 'summary_job': None, 'reason': '追加分析で十分'})
        self.assertEqual(len(self.state()['iterations']), 1)
        self.assertEqual(self.state()['reason'], '追加分析で十分')

    def test_missing_or_deadlocking_summary_fails(self):
        for group in (None, 'controller'):
            with self.subTest(group=group):
                state = self.state()
                state.update(phase='queued', iterations=[])
                loop.save(self.path, state)
                self.jobs.clear()
                def broken(*args):
                    if group:
                        self.jobs['42'] = {'group': group, 'status': 'Queued'}
                    return {'action': 'queued', 'summary_job': 42, 'reason': '不正な依存先'}
                with self.assertRaises(RuntimeError):
                    self.run_worker(broken)
                self.assertEqual(self.state()['phase'], 'failed')

    def test_old_summary_cannot_authorize_next_session(self):
        self.jobs['42'] = {'group': 'summaries', 'status': {'Done': {'result': 'Success'}}}
        with self.assertRaises(RuntimeError):
            self.run_worker(lambda *args: {'action': 'queued', 'summary_job': 42, 'reason': '古い要約'})
        self.assertEqual(self.state()['phase'], 'failed')


if __name__ == '__main__':
    unittest.main()
