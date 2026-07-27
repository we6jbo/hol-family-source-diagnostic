#!/usr/bin/env python3
from __future__ import annotations
import getpass, grp, json, os, pwd, re, shutil, signal, subprocess, tempfile, time, traceback, zipfile
from pathlib import Path

DOWNLOADS = Path.home() / 'Downloads'
TARGET = Path('/tmp/to-github/hol-family-source-diagnostic')
STATE_DIR = Path.home() / '.local/state/hol-family-source-diagnostic'
STATE_FILE = STATE_DIR / 'updater-state.json'
PID_FILE = STATE_DIR / 'bridge.pid'
LOG_FILE = STATE_DIR / 'updater.log'
PATTERN = re.compile(r'^hol-family-source-diagnostic-v(\d+)\.(\d+)\.(\d+)\.zip$')
APPROVAL_FILE = Path.home() / '.config/hol-family-source-diagnostic/confirm-updates'
CURRENT_STAGE = 'startup'

def log(msg: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    line = time.strftime('%Y-%m-%d %H:%M:%S ') + msg
    with LOG_FILE.open('a', encoding='utf-8') as f: f.write(line+'\n')
    print(line, flush=True)

def identity_summary() -> str:
    uid=os.geteuid(); gid=os.getegid()
    try: user=pwd.getpwuid(uid).pw_name
    except KeyError: user=getpass.getuser()
    try: group=grp.getgrgid(gid).gr_name
    except KeyError: group=str(gid)
    groups=[]
    for g in os.getgroups():
        try: groups.append(grp.getgrgid(g).gr_name)
        except KeyError: groups.append(str(g))
    return f'user={user} uid={uid} group={group} gid={gid} groups={",".join(groups)} home={Path.home()} cwd={Path.cwd()}'

def desktop_approval(version: str, zip_name: str) -> bool:
    if not APPROVAL_FILE.exists():
        return True
    zenity=shutil.which('zenity')
    if not zenity:
        log(f'Approval requested for {version}, but zenity is unavailable; update deferred.')
        return False
    env=os.environ.copy()
    cp=subprocess.run([zenity, '--question', '--title=HOL Update Permission',
                       '--text', f'Install HOL Family Source Diagnostic {version} from {zip_name}?',
                       '--ok-label=Install update', '--cancel-label=Not now'], env=env)
    return cp.returncode == 0

def run_sh(script: Path, *, cwd: Path) -> None:
    log(f'Running shell script through /bin/sh: {script}')
    subprocess.run(['/bin/sh', str(script)], cwd=cwd, check=True)

def version_of_zip(path: Path):
    m=PATTERN.match(path.name)
    return tuple(map(int,m.groups())) if m else None

def current_version():
    p=TARGET/'chrome-extension/manifest.json'
    try:
        v=json.loads(p.read_text())['version']
        return tuple(map(int,v.split('.')))
    except Exception: return (0,0,0)

def safe_extract(z: Path, dest: Path) -> Path:
    with zipfile.ZipFile(z) as f:
        for i in f.infolist():
            n=Path(i.filename)
            if n.is_absolute() or '..' in n.parts:
                raise RuntimeError('unsafe ZIP path: '+i.filename)
        f.extractall(dest)
    matches=list(dest.glob('**/hol-family-source-diagnostic/chrome-extension/manifest.json'))
    if len(matches)!=1: raise RuntimeError(f'expected one project, found {len(matches)}')
    root=matches[0].parents[1]
    required=['hol-reddit-ollama-bridge.py','run-reddit-ollama-bridge.sh','install-extension-to-home.sh']
    for n in required:
        if not (root/n).is_file(): raise RuntimeError('missing '+n)
    subprocess.run(['python3','-m','py_compile',str(root/'hol-reddit-ollama-bridge.py')],check=True)
    json.loads((root/'chrome-extension/manifest.json').read_text())
    return root

def git_warning() -> None:
    if not (TARGET/'.git').exists(): return
    dirty=subprocess.run(['git','-C',str(TARGET),'status','--porcelain'],capture_output=True,text=True).stdout.strip()
    ahead=''
    subprocess.run(['git','-C',str(TARGET),'fetch','origin'],capture_output=True,text=True,timeout=60)
    cp=subprocess.run(['git','-C',str(TARGET),'rev-list','--count','@{u}..HEAD'],capture_output=True,text=True)
    if cp.returncode==0: ahead=cp.stdout.strip()
    if dirty or (ahead.isdigit() and int(ahead)>0):
        log('WARNING: current version has uncommitted or unpushed GitHub changes before automatic replacement.')

def stop_bridge() -> None:
    if PID_FILE.exists():
        try:
            pid=int(PID_FILE.read_text().strip()); os.kill(pid, signal.SIGTERM)
            for _ in range(30):
                try: os.kill(pid,0); time.sleep(.1)
                except ProcessLookupError: break
        except Exception as e: log('Could not stop old bridge: '+repr(e))
        PID_FILE.unlink(missing_ok=True)

def start_bridge(expected_version: str | None = None) -> None:
    logf=(STATE_DIR/'bridge.log').open('a')
    command=['/bin/sh', str(TARGET/'run-reddit-ollama-bridge.sh')]
    log(f'Starting bridge as {identity_summary()} command={command!r}')
    p=subprocess.Popen(command,cwd=TARGET,stdout=logf,stderr=subprocess.STDOUT,start_new_session=True)
    PID_FILE.write_text(str(p.pid))
    log(f'Started bridge launcher PID {p.pid}')
    if expected_version:
        marker=Path('/tmp/thecurversionofthisis.json')
        deadline=time.time()+15
        while time.time()<deadline:
            try:
                data=json.loads(marker.read_text(encoding='utf-8'))
                if data.get('version') == expected_version:
                    log(f'Verified running bridge version {expected_version}, pid={data.get("pid")}, program={data.get("program")}')
                    return
            except Exception:
                pass
            if p.poll() is not None:
                raise RuntimeError(f'bridge launcher exited with return code {p.returncode}; see {STATE_DIR/"bridge.log"}')
            time.sleep(.5)
        raise RuntimeError(f'bridge did not publish expected version {expected_version} within 15 seconds; see {STATE_DIR/"bridge.log"}')

def install(z: Path) -> None:
    global CURRENT_STAGE
    v=version_of_zip(z)
    version_text='.'.join(map(str,v)) if v else 'unknown'
    CURRENT_STAGE='approval'
    if not desktop_approval(version_text, z.name):
        log(f'Update {version_text} was not approved; leaving current version running.')
        return
    with tempfile.TemporaryDirectory(prefix='hol-update-') as td:
        CURRENT_STAGE='validate ZIP'
        root=safe_extract(z,Path(td))
        manifest=json.loads((root/'chrome-extension/manifest.json').read_text())
        mv=tuple(map(int,manifest['version'].split('.')))
        if mv!=v: raise RuntimeError(f'filename version {v} differs from manifest {mv}')
        CURRENT_STAGE='GitHub warning check'
        git_warning()
        CURRENT_STAGE='stop old bridge'
        stop_bridge()
        CURRENT_STAGE='backup current project'
        if TARGET.exists():
            backup=TARGET.with_name(TARGET.name+'.backup-'+time.strftime('%Y%m%d-%H%M%S'))
            shutil.move(TARGET,backup); log('Backup: '+str(backup))
        CURRENT_STAGE='copy new project'
        shutil.copytree(root,TARGET,symlinks=True)
        CURRENT_STAGE='set permissions'
        for script in TARGET.glob('*.sh'):
            script.chmod(script.stat().st_mode | 0o111)
        CURRENT_STAGE='install Chrome extension'
        run_sh(TARGET/'install-extension-to-home.sh',cwd=TARGET)
        CURRENT_STAGE='start and verify bridge'
        start_bridge(manifest['version'])
        CURRENT_STAGE='complete'
        log(f'Installed and verified version {manifest["version"]} from {z.name}')

def restore_if_missing() -> None:
    if TARGET.exists():
        return
    log('Project missing after restart; restoring the last GitHub version.')
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    cp=subprocess.run(['git','clone','https://github.com/we6jbo/hol-family-source-diagnostic.git',str(TARGET)],capture_output=True,text=True)
    if cp.returncode != 0:
        raise RuntimeError('GitHub restore failed: '+cp.stderr.strip())
    subprocess.run(['python3','-m','py_compile',str(TARGET/'hol-reddit-ollama-bridge.py')],check=True)
    for script in TARGET.glob('*.sh'):
        script.chmod(script.stat().st_mode | 0o111)
    run_sh(TARGET/'install-extension-to-home.sh',cwd=TARGET)
    manifest=json.loads((TARGET/'chrome-extension/manifest.json').read_text())
    start_bridge(manifest.get('version'))


def main():
    STATE_DIR.mkdir(parents=True,exist_ok=True)
    try:
        restore_if_missing()
    except Exception as e:
        log('STARTUP RESTORE FAILED: '+repr(e))
    seen=set()
    log('Updater identity: '+identity_summary())
    log('Optional confirmation mode: '+('enabled' if APPROVAL_FILE.exists() else 'disabled')+f' ({APPROVAL_FILE})')
    log('Watching '+str(DOWNLOADS)+' for HOL version ZIP files.')
    while True:
        candidates=[]
        for p in DOWNLOADS.glob('hol-family-source-diagnostic-v*.zip'):
            v=version_of_zip(p)
            if v and p.stat().st_size>0: candidates.append((v,p))
        for v,p in sorted(candidates):
            key=(str(p),p.stat().st_mtime_ns,p.stat().st_size)
            if key in seen: continue
            seen.add(key)
            if v>current_version():
                try: install(p)
                except Exception as e:
                    log(f'UPDATE FAILED during stage={CURRENT_STAGE}: {type(e).__name__}: {e}')
                    log(traceback.format_exc().rstrip())
        time.sleep(5)
if __name__=='__main__': main()
