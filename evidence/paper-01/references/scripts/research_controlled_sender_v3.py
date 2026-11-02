"""Single planned call via a scoped Codex authentication bootstrap.

CLI-generated context is diagnostic input only. Only frozen request bytes reach
the fixed Codex backend. Never read auth files or store incoming header values.
"""
from dataclasses import asdict
from datetime import datetime, timezone
from http.client import HTTPSConnection
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import hashlib
import json
import os
import secrets
import signal
import ssl
import subprocess
import sys
import threading
import time

import research_dual_gate_v1 as core
import research_responses_gate_v3 as wire
import research_response_capacity_v1 as capacity

HOST = 'chatgpt.com'
PATH = '/backend-api/codex/responses'


def now():
    return datetime.now(timezone.utc).isoformat()


def acceptable_sse_header(status, content_type):
    return status == 200 and (content_type is None or
        (type(content_type) is str and content_type.split(';', 1)[0].strip().lower() == 'text/event-stream'))


def save(path, obj):
    write(path, core.encode(obj) + b'\n')


def write(path, raw):
    with path.open('xb') as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())


def make_request(model, developer, user):
    return core.encode({'model': model, 'input': [
        {'type': 'message', 'role': 'developer', 'content': [{'type': 'input_text', 'text': developer}]},
        {'type': 'message', 'role': 'user', 'content': [{'type': 'input_text', 'text': user}]}],
        'tools': [], 'tool_choice': 'none', 'parallel_tool_calls': False,
        'reasoning': {'effort': 'medium'}, 'store': False, 'stream': True})


def bootstrap_valid(raw, prompt, model):
    obj = core.strict(raw)
    if obj.get('model') != model or type(obj.get('input')) is not list:
        return False
    # The nonce binds the launch, not research content. Nothing here is forwarded.
    parts = [p.get('text') for m in obj['input'] if type(m) is dict and m.get('role') == 'user'
             for p in m.get('content', []) if type(p) is dict]
    return parts.count(prompt) == 1


def cli_text_stream(text):
    message = {'id': 'npp_checked_message', 'type': 'message', 'role': 'assistant', 'status': 'completed',
               'content': [{'type': 'output_text', 'text': text, 'annotations': []}]}
    response = {'id': 'npp_checked_response', 'object': 'response', 'status': 'completed', 'output': [message]}
    # These are a delivery envelope, not source-model usage or response identity.
    events = [{'type': 'response.created', 'response': {'id': response['id'], 'status': 'in_progress'}},
              {'type': 'response.output_item.done', 'output_index': 0, 'item': message},
              {'type': 'response.completed', 'response': response}]
    return b''.join(b'data: ' + core.encode(e) + b'\n\n' for e in events)


def run(directory, trial):
    os.umask(0o077)
    root = Path(directory).resolve()
    c = json.loads((root / 'configuration.json').read_text())
    assert trial in c['order']
    for path, expected in c['frozen_sha256'].items():
        assert core.sha((root / path).read_bytes()) == expected, path
    assert core.sha(Path(c['cli']).read_bytes()) == c['cli_sha256']
    login = subprocess.run([c['cli'], 'login', 'status'], capture_output=True, text=True, check=True)
    assert 'Logged in using ChatGPT' in login.stdout + login.stderr, 'ChatGPT login required'
    out = root / 'results'
    assert not (out / (trial + '-launch.json')).exists(), 'trial already launched'
    if trial != 'P0':
        proof = root / c['auth_bootstrap_proof']
        assert core.sha(proof.read_bytes()) == c['auth_bootstrap_proof_sha256']
        assert json.loads(proof.read_text())['status'] == 'AUTH_BOOTSTRAP_PASS'
    prompt = 'NPP_AUTH_BOOTSTRAP_' + secrets.token_hex(24)
    seen = []
    outcome = []
    trial_spec = c['trials'].get(trial)
    planned = (root / trial_spec['request']).read_bytes() if trial_spec else None
    if planned is not None:
        assert core.sha(planned) == trial_spec['request_sha256']
    journal = None

    class Backend:
        def __init__(self, headers):
            # Only needed routing/authentication headers; never persisted.
            self.headers = {'Content-Type': 'application/json', 'Accept': 'text/event-stream'}
            for name in ['Authorization', 'ChatGPT-Account-Id', 'Originator', 'User-Agent']:
                if headers.get(name):
                    self.headers[name] = headers[name]

        def send(self, raw):
            if raw != planned or core.sha(raw) != trial_spec['request_sha256']:
                raise ValueError('unplanned outbound bytes')
            write(out / (trial + '-sent.json'), raw)
            save(out / (trial + '-send-boundary.json'), {'at': now(), 'host': HOST, 'path': PATH,
                 'bytes': len(raw), 'sha256': core.sha(raw), 'retry': False, 'redirect': False})
            conn = HTTPSConnection(HOST, timeout=75, context=ssl.create_default_context())
            start = time.monotonic()
            body = bytearray()
            try:
                conn.request('POST', PATH, body=raw, headers=self.headers)
                response = conn.getresponse()
                save(out / (trial + '-http-start.json'), {'at': now(), 'status': response.status,
                     'content_type': response.getheader('Content-Type'),
                     'header_names': [name for name, _ in response.getheaders()]})
                capacity.read_response(response, body, started_at=start)
                sensitive = [self.headers['Authorization'].removeprefix('Bearer ')]
                if self.headers.get('ChatGPT-Account-Id'):
                    sensitive.append(self.headers['ChatGPT-Account-Id'])
                capacity.check_reflection(body, sensitive)
                write(out / (trial + '-upstream.raw'), bytes(body))
                save(out / (trial + '-http.json'), {'at': now(), 'status': response.status,
                     'content_type': response.getheader('Content-Type'), 'header_names': [name for name, _ in response.getheaders()], 'body_bytes': len(body),
                     'body_sha256': core.sha(bytes(body)), 'seconds': time.monotonic() - start})
                if not acceptable_sse_header(response.status, response.getheader('Content-Type')):
                    raise capacity.ReadFailure('UPSTREAM_STATUS_OR_CONTENT_TYPE')
                return bytes(body)
            except Exception as exc:
                try:
                    capacity.check_reflection(body, [self.headers.get(name, '').removeprefix('Bearer ')
                        for name in ['Authorization', 'ChatGPT-Account-Id']])
                except capacity.ReadFailure:
                    exc = capacity.ReadFailure('CREDENTIAL_REFLECTION')
                if not (out / (trial + '-upstream.raw')).exists():
                    write(out / (trial + '-upstream.raw'), bytes(body))
                # Persist only the exception class and fixed diagnostic code.
                save(out / (trial + '-transport-error.json'), {'at': now(), 'class': type(exc).__name__, 'reason': exc.code if isinstance(exc, capacity.ReadFailure) else 'TRANSPORT_IO_OR_STORAGE', 'partial_bytes': len(body)})
                raise RuntimeError('upstream transport failed') from None
            finally:
                self.headers.clear()
                conn.close()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            nonlocal journal
            try:
                seen.append(now())
                save(out / (trial + '-ingress-' + str(len(seen)).zfill(2) + '.json'),
                     {'at': seen[-1], 'ordinal': len(seen), 'authorization_present': 'Authorization' in self.headers})
                size = self.headers.get('Content-Length', '')
                if len(seen) != 1 or self.path != '/v1/responses' or not size.isdigit() or not 0 < int(size) <= core.MAX_BYTES or self.headers.get('Content-Encoding'):
                    self.send_error(400)
                    return
                auth = self.headers.get('Authorization', '')
                if not auth.startswith('Bearer ') or not auth[7:] or auth[7:].startswith('sk-'):
                    self.send_error(403)
                    return
                auth = None
                raw = self.rfile.read(int(size))
                write(out / (trial + '-bootstrap.json'), raw)
                save(out / (trial + '-bootstrap-metadata.json'), {'at': now(), 'authorization_present': True,
                     'account_header_present': self.headers.get('ChatGPT-Account-Id') is not None,
                     'body_bytes': len(raw), 'body_sha256': core.sha(raw), 'headers_persisted': False})
                if not bootstrap_valid(raw, prompt, c['model']):
                    self.send_error(403)
                    return
                if trial == 'P0':
                    result = {'status': 'AUTH_BOOTSTRAP_PASS', 'send_invoked': False, 'text': 'AUTH_BOOTSTRAP_FIXTURE_ONLY'}
                else:
                    tickets = {t: core.Ticket(v['stage'], c['model'], v['request_sha256']) for t, v in c['trials'].items()}
                    runner = wire.ResponsesRunner(c['protocol'], tickets, root / 'journal.sqlite', Backend(self.headers),
                        gate=core.GateProcess(script=root / 'frozen/research_responses_gate_v3.py'))
                    journal = runner.journal
                    result = asdict(runner.run(trial, planned))
                save(out / (trial + '-result.json'), result)
                outcome.append(result)
                if result['status'] in ('AUTH_BOOTSTRAP_PASS', 'ACCEPTED'):
                    payload = cli_text_stream(result['text'])
                    status, content_type = 200, 'text/event-stream'
                else:
                    payload = core.encode({'error': {'type': 'research_gate', 'code': result['status']}})
                    status, content_type = 403, 'application/json'
                write(out / (trial + '-released.raw'), payload)
                self.send_response(status)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                self.wfile.flush()
                self.close_connection = True
            except Exception as exc:
                save(out / (trial + '-handler-error.json'), {'at': now(), 'class': type(exc).__name__})
                self.close_connection = True

    server = HTTPServer(('127.0.0.1', 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    cwd = Path('/private/tmp/npp-controlled-sender-20260913')
    cwd.mkdir(mode=0o700, exist_ok=True)
    argv = [c['cli'], 'exec', '--ignore-user-config', '--strict-config', '--ephemeral', '--skip-git-repo-check',
            '--json', '--color', 'never', '--sandbox', 'read-only', '-C', str(cwd), '-m', c['model']]
    configs = c['configs'] + ['features.enable_request_compression=false', 'model_provider="npp_controlled_sender"',
        'model_providers.npp_controlled_sender.name="NPP controlled sender"',
        'model_providers.npp_controlled_sender.base_url="http://127.0.0.1:' + str(server.server_address[1]) + '/v1"',
        'model_providers.npp_controlled_sender.requires_openai_auth=true',
        'model_providers.npp_controlled_sender.supports_websockets=false',
        'model_providers.npp_controlled_sender.request_max_retries=0',
        'model_providers.npp_controlled_sender.stream_max_retries=0',
        'model_providers.npp_controlled_sender.stream_idle_timeout_ms=150000',
        'model_providers.npp_controlled_sender.wire_api="responses"']
    for setting in configs:
        argv += ['-c', setting]
    argv += ['-']
    save(out / (trial + '-launch.json'), {'at': now(), 'argv': argv, 'bootstrap_prompt': prompt,
        'planned_request_sha256': core.sha(planned) if planned else None,
        'configuration_sha256': core.sha((root / 'configuration.json').read_bytes()), 'model_request_planned': trial != 'P0'})
    env = os.environ.copy()
    for name in ['OPENAI_API_KEY', 'CODEX_API_KEY']:
        env.pop(name, None)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    start = time.monotonic()
    timed_out = False
    with (out / (trial + '-cli-events.jsonl')).open('xb') as output, (out / (trial + '-cli-stderr.txt')).open('xb') as error:
        proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=output, stderr=error, env=env, start_new_session=True)
        try:
            proc.communicate(prompt.encode(), timeout=180)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=5)
    server.shutdown()
    server.server_close()
    save(out / (trial + '-process.json'), {'at': now(), 'exit_code': proc.returncode, 'timeout': timed_out,
        'seconds': time.monotonic() - start, 'bootstrap_requests': len(seen), 'results': len(outcome)})
    print(json.dumps({'trial': trial, 'status': outcome[0]['status'] if outcome else 'NO_RESULT',
                      'cli_exit': proc.returncode, 'seconds': time.monotonic() - start}), flush=True)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: research_controlled_sender_v2.py FROZEN_RUN_DIR TRIAL')
    run(sys.argv[1], sys.argv[2])
