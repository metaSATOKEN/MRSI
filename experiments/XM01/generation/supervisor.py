"""Single-cell Colab supervisor. Called only after its explicit Colab-only guard."""
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


def reserved_seconds(root):
    total = 0.0
    for path in (root / "windows").glob("*-start.json"):
        start = json.loads(path.read_bytes())
        end_path = path.with_name(path.name.replace("-start.json", "-end.json"))
        total += json.loads(end_path.read_bytes())["elapsed_seconds"] if end_path.exists() else start["reserved_seconds"]
    return total


def live_pid(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def take_lock(root, recover=False):
    path = root / "RUNNING.lock"
    boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    if path.exists():
        old = json.loads(path.read_bytes())
        if not recover:
            raise RuntimeError("前の実行ロックが残っています。前のランタイムが停止済みと確認してからRECOVER_INTERRUPTED_RUN=Trueにしてください。")
        if old["boot_id"] == boot and live_pid(old["pid"]):
            raise RuntimeError("前のプロセスが同じランタイムで稼働中です。同時実行しません。")
        atomic_new(root / "lock-recovery" / (uuid.uuid4().hex + ".json"), jbytes(old))
        path.unlink()
    owner = {"boot_id": boot, "pid": os.getpid(), "token": uuid.uuid4().hex}
    with path.open("xb") as f:
        f.write(jbytes(owner))
        f.flush()
        os.fsync(f.fileno())
    return owner


def release_lock(root, owner):
    path = root / "RUNNING.lock"
    if path.exists() and json.loads(path.read_bytes())["token"] == owner["token"]:
        path.unlink()


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


def export_feedback(root, tag):
    # Export only this experiment's local folder; never the HF cache or other folders.
    files = [p for p in sorted(root.rglob("*")) if p.is_file() and not p.is_symlink() and p.name != "RUNNING.lock"]
    manifest = {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest() for p in files}
    destination = Path("/content") / ("npp-xm01-feedback-" + tag + ".zip")
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for p in files:
            archive.write(p, str(p.relative_to(root)))
        archive.writestr("FEEDBACK_MANIFEST.json", jbytes({"files_sha256": manifest, "scope": "MAIN_BOOTSTRAP_DIAGNOSTIC"}))
    return destination


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


def local_destination(save_root):
    base = Path("/content/npp_xm01_runs")
    if base.resolve() != base:
        raise ValueError("専用の一時保存先がリンクになっています。通常のColabローカル領域を使用してください。")
    destination = Path(save_root).expanduser().resolve()
    if destination != base and base not in destination.parents:
        raise ValueError("SAVE_ROOTはColabの /content/npp_xm01_runs 内にしてください。クラウドストレージは使用しません。")
    return destination



def load_main_support(code, folder):
    folder.mkdir(parents=True, exist_ok=True)
    for name, source in code.items():
        if not re.fullmatch(r'cross_model_e1_01_[a-z_]+\.py', name):
            raise ValueError('Unexpected embedded source name')
        put_or_match(folder / name, source.encode())
    # Only embedded, hash-bound source is imported; never code chosen by a ZIP.
    sys.path.insert(0, str(folder))
    try:
        for name in ('cross_model_e1_01_offline_runtime', 'cross_model_e1_01_generation_runtime', 'cross_model_e1_01_main_runtime'):
            spec = importlib.util.spec_from_file_location(name, folder / (name + '.py'))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(folder))


def run_main_colab(payload_bytes, expected_hash, *, part=1, run_main=False, resume_zip='', recover=False, download=True):
    if not run_main:
        print('本番コード準備済み。PART=1 または2を選び、実行時にRUN_MAIN=Trueへ変更してください。')
        print('各PART: 最大768生成・準備を含め累計8時間。Drive不要、終了ZIPを回収します。')
        return
    require_colab()  # Must precede all torch/Hub/pip imports, ZIP upload, and model downloads.
    if type(part) is not int or part not in (1, 2):
        raise ValueError('PARTは1または2です。')
    raw = payload_bytes
    if sha256(raw).hexdigest() != expected_hash:
        raise ValueError('埋込みpayloadが変わっています。全文を再コピーしてください。')
    packed = json.loads(raw)
    name = 'PART' + str(part)
    contract = packed['contracts'][name]
    expected = {'bundle': packed['bundle'], 'partition': packed['partition'], 'contract': contract,
                'allocation': packed['partition']['parts'][name]['allocation'], 'code': packed['code']}
    tag = time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    root = Path('/content') / ('npp-xm01-main-bootstrap-' + tag)
    root.mkdir()
    owner = started = window = support = None
    diagnostic_root = root
    try:
        print(f'{name}: 32材料、768予定応答、累計8時間。両方式・3反復を実行します。')
        print('回答不成立は記録して続行。Drive接続なし。終了後はZIPを回収してください。')
        support = load_main_support(packed['code'], diagnostic_root / 'code')
        candidate = local_destination('/content/npp_xm01_runs') / ('xm01-main-v01-part' + str(part))
        if candidate.is_symlink():
            raise ValueError('実行先へのリンクは使用しません。')
        if resume_zip:
            if candidate.exists():
                raise ValueError('このPARTのローカル保存が既にあります。RESUME_ZIPを空にして照合再開してください。')
            if resume_zip == 'UPLOAD':
                from google.colab import files
                uploaded = files.upload()
                if len(uploaded) != 1:
                    raise ValueError('同じPARTの最新終了ZIPを1個だけ選択してください。')
                archive_path = diagnostic_root / 'selected-resume.zip'
                atomic_new(archive_path, next(iter(uploaded.values())))
            else:
                archive_path = Path(resume_zip).expanduser().resolve()
                if not archive_path.is_relative_to(Path('/content')) or archive_path.is_relative_to(Path('/content/drive')):
                    raise ValueError('復帰ZIPはColabローカル/contentへ置いてください。Driveは読み込みません。')
            support.restore_zip(archive_path, candidate, expected)
            print('最新終了ZIPを照合して復元しました。処理済み回答は再生成しません。')
        candidate.mkdir(parents=True, exist_ok=True)
        owner = take_lock(candidate, recover)
        root = candidate
        for filename, value in [('bundle.json', packed['bundle']), ('partition.json', packed['partition']),
                                ('contract.json', contract), ('allocation.json', expected['allocation'])]:
            put_or_match(root / filename, jbytes(value))
        for filename, source in packed['code'].items():
            put_or_match(root / 'code' / filename, source.encode())
        support.verify_scope(root, packed['bundle'], packed['partition'], contract)
        audit_cmd = [sys.executable, '-u', str(root / 'code/cross_model_e1_01_main_runtime.py'), str(root), '0', 'AUDIT_ONLY']
        run_child(audit_cmd, root / ('audit-' + tag + '.log'), dict(os.environ), time.monotonic() + 180)
        closed = len(list((root / 'responses').glob('*/result.json')))
        if closed == 768:
            print('768予定応答は既に処理済みです。モデルをロードせずZIPを返します。')
            return
        remaining = contract['total_seconds'] - support.budget_used(root)
        if remaining <= 90:
            print('累計時間の残りが終了処理用の90秒以下です。新規生成を行わず記録を返します。')
            return
        started = time.monotonic()
        deadline = started + remaining
        window = root / 'windows' / tag
        atomic_new(window.with_name(window.name + '-start.json'), jbytes({'reserved_seconds': remaining, 'tag': tag,
                    'started_at': support.live.now(), 'part': name}))
        env = dict(os.environ)
        for key in ('HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN', 'HUGGINGFACEHUB_API_TOKEN', 'PIP_EXTRA_INDEX_URL', 'PYTHONPATH',
                    'PIP_TARGET', 'PIP_PREFIX', 'PIP_USER'):
            env.pop(key, None)
        env.update({'HF_HUB_DISABLE_IMPLICIT_TOKEN': '1', 'HF_HUB_DISABLE_TELEMETRY': '1',
                    'HF_HOME': '/content/npp_xm01_hf_cache', 'PYTHONUNBUFFERED': '1',
                    'TOKENIZERS_PARALLELISM': 'false', 'PIP_CONFIG_FILE': os.devnull, 'PIP_INDEX_URL': 'https://pypi.org/simple'})
        env.pop('HF_HUB_OFFLINE', None)
        guard = '''import json,torch
from pathlib import Path
p=Path(__import__('sys').argv[1]); p.mkdir(parents=True,exist_ok=True)
free,total=torch.cuda.mem_get_info(0) if torch.cuda.is_available() else (0,0)
x={'torch':torch.__version__,'cuda':torch.version.cuda,'cuda_available':torch.cuda.is_available(),'total_bytes':total,'free_bytes':free,'bf16_supported':torch.cuda.is_available() and torch.cuda.is_bf16_supported()}
(p/'preload-hardware.json').write_text(json.dumps(x,indent=2)); print(json.dumps(x),flush=True)
assert x['cuda_available'] and total>=75000000000 and free>=65000000000 and x['bf16_supported'], 'VRAM/BF16条件未達。モデルは取得・ロードしません。'
'''
        window.mkdir(parents=True, exist_ok=True)
        run_child([sys.executable, '-c', guard, str(window)], window / 'preload.log', env, deadline - 90)
        if shutil.disk_usage('/content').free < 70_000_000_000 and not Path(env['HF_HOME']).exists():
            raise RuntimeError('初回の重み取得には70GB以上の空きディスクが必要です。')
        hardware = json.loads((window / 'preload-hardware.json').read_bytes())
        python = prepare_python_environment(Path('/content/npp_xm01_venv_tf517_v03'), window, env, deadline - 90, hardware['torch'])
        run_child([python, '-u', str(root / 'code/cross_model_e1_01_main_runtime.py'), str(root),
                   str(max(0, deadline - time.monotonic() - 90))], window / 'worker.log', env, deadline - 60)
    except BaseException as error:
        details = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
        atomic_new(root / ('error-' + tag + '.json'), jbytes(details))
        print('\n停止:', details['type'], details['message'], flush=True)
        print('記録した回答を変更せず、回収用ZIPを作成します。', flush=True)
    finally:
        try:
            if owner is not None and support is not None:
                try:
                    report = support.audit_root(root, packed['bundle'], packed['partition'], contract)
                    atomic_new(root / ('report-final-' + tag + '.json'), jbytes(report))
                    print('処理済み:', report['closed_responses'], '/768 / 実生成開始:', report['attempted_generations'])
                except Exception as audit_error:
                    atomic_new(root / ('final-audit-error-' + tag + '.json'), jbytes({'error': str(audit_error)}))
                    print('最終照合エラー（証拠をそのまま保存）:', str(audit_error))
            if started is not None:
                atomic_new(window.with_name(window.name + '-end.json'), jbytes({'elapsed_seconds': time.monotonic() - started,
                           'ended_at': support.live.now()}))
        finally:
            try:
                if support is not None:
                    archive = Path('/content') / f'npp-xm01-main-{name.lower()}-{tag}.zip'
                    support.export_zip(root, archive, kind='FINAL')
                else:
                    archive = export_feedback(root, 'main-bootstrap-' + tag)
            finally:
                if owner is not None:
                    release_lock(root, owner)
            print('保存先:', root)
            print('終了ZIP:', archive)
            print('このZIPをダウンロードして保管してください。PART2はPART1のZIPなしで独立実行できます。')
            if download:
                try:
                    from google.colab import files
                    files.download(str(archive))
                except Exception as download_error:
                    print('自動DLを開始できませんでした。左のファイル欄から上記ZIPを取得してください:', str(download_error))
