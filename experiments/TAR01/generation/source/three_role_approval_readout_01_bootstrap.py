"""One-cell supervisor; setup helpers retained from the tested XM01 Colab runner."""
import base64

from hashlib import sha256

import importlib.util

import json

import os

from pathlib import Path

import platform

import re

import shutil

import signal

import subprocess

import sys

import time

import traceback

import uuid

import zipfile

import zlib

def colab_available():
    if platform.system() != "Linux" or not Path("/content").is_dir():
        return False
    try:
        return importlib.util.find_spec("google.colab") is not None
    except (ImportError, ModuleNotFoundError):
        return False

def require_colab():
    if not colab_available():
        raise RuntimeError("Colab専用です。このマシンではモデル取得・ロードを行いません。ColabのGPUランタイムへ貼ってください。")

def atomic_new(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError("上書き拒否: " + str(path))
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    with temporary.open("xb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    os.rename(temporary, path)
    if path.read_bytes() != raw:
        raise RuntimeError("保存後の読返しが不一致")

def jbytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()

def put_or_match(path, raw):
    if path.exists():
        if path.read_bytes() != raw:
            raise RuntimeError("保存済みのコード・材料・設定が異なります。旧実行へ混ぜません: " + path.name)
    else:
        atomic_new(path, raw)

def run_child(command, log_path, env, deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("今回の実行時間上限に達しました。")
    with log_path.open("ab", buffering=0) as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
        try:
            # Mirror the log without collecting unbounded output in notebook memory.
            with log_path.open("rb") as reader:
                while child.poll() is None:
                    chunk = reader.read(32768)
                    if chunk:
                        print(chunk.decode("utf-8", errors="replace"), end="", flush=True)
                    if time.monotonic() >= deadline:
                        raise TimeoutError("今回の実行時間上限。子プロセスを停止します。")
                    time.sleep(0.5)
                chunk = reader.read()
                if chunk:
                    print(chunk.decode("utf-8", errors="replace"), end="", flush=True)
            if child.returncode:
                raise RuntimeError(f"子プロセス終了コード {child.returncode}。ログ: {log_path.name}")
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=5)

def prepare_python_environment(venv, window_dir, env, deadline, torch_version):
    """Manage a pip-less venv from Colab's pip; do not invoke ensurepip."""
    setup_log = window_dir / "setup.log"
    # Reconfigure even when bin/python exists: it can survive a failed creation.
    run_child([sys.executable, "-m", "venv", "--without-pip", "--system-site-packages", str(venv)],
              setup_log, env, deadline)
    python = str(venv / "bin/python")
    check = '''import json,sys,sysconfig
from pathlib import Path
expected=Path(sys.argv[1]).resolve(); prefix=Path(sys.prefix).resolve()
assert prefix==expected and sys.prefix!=sys.base_prefix, 'Target is not the requested virtual environment'
assert Path(sysconfig.get_path('purelib')).resolve().is_relative_to(expected), 'Install target is outside venv'
x={'executable':sys.executable,'prefix':sys.prefix,'base_prefix':sys.base_prefix,'purelib':sysconfig.get_path('purelib')}
Path(sys.argv[2]).write_text(json.dumps(x,indent=2)); print(json.dumps(x),flush=True)
'''
    run_child([python, "-c", check, str(venv), str(window_dir / "venv-check.json")],
              setup_log, env, deadline)
    pip_check = '''import pip,re
v=tuple(map(int,re.match(r'(\\d+)\\.(\\d+)',pip.__version__).groups()))
print('Host pip:',pip.__version__,flush=True)
assert v>=(22,3), 'Colab host pip must be >=22.3 for --python; no automatic base-environment update'
'''
    run_child([sys.executable, "-c", pip_check], setup_log, env, deadline)
    constraint = window_dir / "torch-constraint.txt"
    atomic_new(constraint, ("torch==" + torch_version + "\n").encode())
    run_child([sys.executable, "-m", "pip", "--python", python, "install", "--disable-pip-version-check",
               "--index-url", "https://pypi.org/simple", "--constraint", str(constraint),
               "transformers==5.17.0", "accelerate==1.15.0"], setup_log, env, deadline)
    return python


def load_readout_support(packed, folder):
    names = ('cross_model_e1_01_offline_runtime', 'cross_model_e1_01_generation_runtime',
             'readout_split_01_scoring', 'update_readout_01_envelope',
             'three_role_boundary_01_design', 'three_role_boundary_01_scoring',
             'three_role_boundary_01_fixtures',
             'three_role_approval_readout_01_design', 'three_role_approval_readout_01_scoring',
             'three_role_approval_readout_01_fixtures', 'three_role_approval_readout_01_runtime')
    folder.mkdir(parents=True, exist_ok=True)
    for name, source in packed['code'].items():
        if not re.fullmatch(r'(cross_model_e1_01|readout_split_01|update_readout_01|three_role_boundary_01|three_role_approval_readout_01)_[a-z_]+\.py', name):
            raise ValueError('Unexpected embedded source')
        if sha256(source.encode()).hexdigest() != packed['contract']['source_hashes'][name]:
            raise ValueError('Embedded source hash mismatch')
        put_or_match(folder / name, source.encode())
    sys.path.insert(0, str(folder))
    try:
        for name in names:
            spec = importlib.util.spec_from_file_location(name, folder / (name + '.py'))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(folder))




def run_readout_colab(blob, expected_hash, download=True):
    require_colab()  # Before torch, pip, Hub, or model construction.
    started = time.monotonic()
    raw = zlib.decompress(base64.b64decode(blob, validate=True))
    if sha256(raw).hexdigest() != expected_hash:
        raise ValueError('埋込みデータが不一致です。全文を再コピーしてください。')
    packed = json.loads(raw)
    tag = time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    base = Path('/content/npp_tar01_runs')
    if base.resolve() != base:
        raise ValueError('保存先へのリンクは使いません。Colab一時領域へ保存してください。')
    base.mkdir(exist_ok=True)
    candidate = base / 'three-role-approval-readout-01-v01'
    diagnostic = base / ('bootstrap-' + tag)
    diagnostic.mkdir()
    root = diagnostic; support = None; own_lock = False
    try:
        print('THREE-ROLE-APPROVAL-READOUT-01：保存済み資料から三状態×3材料×3読出し役×2反復。最大54回答・準備込み30分。')
        print('TCV02完走版を継承。TB01のREAD指示と採点を保ち、全54入力をモデルロード前に検査します。')
        print('Drive接続なし。終了ZIPをダウンロードします。誤答・形式不備でも続行します。')
        support = load_readout_support(packed, diagnostic / 'code')
        support.validate_payload(packed)
        if candidate.is_symlink():
            raise ValueError('実行先へのリンクは使いません。')
        if candidate.exists():
            if (candidate / 'RUNNING.lock').exists():
                raise RuntimeError('実行ロックが残っています。重複生成しません。表示された記録を保管し、停止状態を確認してください。')
            support.verify_root(candidate, packed)
            root = candidate
            print('既存の実行記録を検出。追加生成せず、再照合してZIPを返します。')
            return
        candidate.mkdir()
        root = candidate
        atomic_new(root / 'RUNNING.lock', jbytes({'pid': os.getpid(), 'tag': tag}))
        own_lock = True
        support.initialize(root, packed)
        atomic_new(root / 'payload.json', raw)
        atomic_new(root / 'preflight.json', jbytes(support.preflight(packed)))
        atomic_new(root / 'run-start.json', jbytes({'started_at': support.live.now(), 'reserved_seconds': 1800, 'tag': tag}))
        deadline = started + 1800
        env = dict(os.environ)
        for key in ('HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN', 'HUGGINGFACEHUB_API_TOKEN', 'PIP_EXTRA_INDEX_URL',
                    'PYTHONPATH', 'PIP_TARGET', 'PIP_PREFIX', 'PIP_USER'):
            env.pop(key, None)
        env.update({'HF_HUB_DISABLE_IMPLICIT_TOKEN': '1', 'HF_HUB_DISABLE_TELEMETRY': '1',
                    'HF_HOME': '/content/npp_xm01_hf_cache', 'PYTHONUNBUFFERED': '1',
                    'TOKENIZERS_PARALLELISM': 'false', 'PIP_CONFIG_FILE': os.devnull,
                    'PIP_INDEX_URL': 'https://pypi.org/simple'})
        env.pop('HF_HUB_OFFLINE', None)
        window = root / 'setup'; window.mkdir()
        guard = '''import json,torch
from pathlib import Path
p=Path(__import__('sys').argv[1])
free,total=torch.cuda.mem_get_info(0) if torch.cuda.is_available() else (0,0)
x={'torch':torch.__version__,'cuda':torch.version.cuda,'cuda_available':torch.cuda.is_available(),'total_bytes':total,'free_bytes':free,'bf16_supported':torch.cuda.is_available() and torch.cuda.is_bf16_supported()}
(p/'preload-hardware.json').write_text(json.dumps(x,indent=2)); print(json.dumps(x),flush=True)
assert x['cuda_available'] and total>=75000000000 and free>=65000000000 and x['bf16_supported'], 'VRAM/BF16条件未達。モデルは取得・ロードしません。'
'''
        run_child([sys.executable, '-c', guard, str(window)], window / 'preload.log', env, deadline - 90)
        if shutil.disk_usage('/content').free < 70_000_000_000 and not Path(env['HF_HOME']).exists():
            raise RuntimeError('初回のモデル取得には70GB以上の空きディスクが必要です。')
        hardware = json.loads((window / 'preload-hardware.json').read_bytes())
        python = prepare_python_environment(Path('/content/npp_tb01_venv_tf517_v01'), window, env, deadline - 90, hardware['torch'])
        run_child([python, '-u', str(root / 'code/three_role_approval_readout_01_runtime.py'), str(root),
                   str(max(0, deadline - time.monotonic() - 90))], root / 'worker.log', env, deadline - 60)
    except BaseException as error:
        atomic_new(root / ('error-' + tag + '.json'), jbytes({'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}))
        print('停止:', type(error).__name__, str(error), flush=True)
        print('モデル設定・回答を変更せず、ログをZIPに残します。')
    finally:
        if support is not None and (root / 'payload.json').exists():
            try:
                run_child([sys.executable, '-u', str(root / 'code/three_role_approval_readout_01_runtime.py'), str(root), '0', 'AUDIT_ONLY'],
                          root / ('audit-' + tag + '.log'), dict(os.environ), time.monotonic() + 30)
            except BaseException as error:
                atomic_new(root / ('audit-error-' + tag + '.json'), jbytes({'type': type(error).__name__, 'message': str(error)}))
                print('最終照合を完了できませんでした。原記録をそのまま回収します:', str(error))
        if own_lock:
            atomic_new(root / 'run-end.json', jbytes({'elapsed_seconds': time.monotonic() - started, 'ended_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}))
            (root / 'RUNNING.lock').unlink()
        archive = Path('/content') / ('npp-tar01-result-' + tag + '.zip')
        try:
            if support is not None:
                support.export_zip(root, archive)
            else:
                with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
                    files = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                    for name, data in files.items(): z.writestr(name, data)
                    z.writestr('FEEDBACK_MANIFEST.json', jbytes({'protocol': 'THREE-ROLE-APPROVAL-READOUT-01-RUN-v0.1', 'kind': 'BOOTSTRAP_ERROR', 'files_sha256': {n: sha256(b).hexdigest() for n, b in files.items()}}))
            print('終了ZIP:', archive)
            print('このZIPを保管して返してください。ランタイム破棄で未回収の記録は失われます。')
            if download:
                try:
                    from google.colab import files
                    files.download(str(archive))
                except Exception as error:
                    print('自動DLを開始できませんでした。左のファイル欄からZIPをダウンロードしてください:', str(error))
        except Exception as error:
            print('ZIP出力失敗。保存先とエラーを返してください:', root, str(error))
