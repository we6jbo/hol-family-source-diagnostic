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
RESTORE_RETRY_SECONDS = 60
GUI_RETRY_SECONDS = 15
PENDING_GUI_FILE = STATE_DIR / 'pending-gui-start.json'
PERSISTENT_CACHE = Path.home() / '.local/share/hol-family-source-diagnostic/recovery-project'

TMP_ROOT = Path('/tmp')
BACKUP_PARENT = Path('/tmp/to-github')
BACKUP_GLOB = 'hol-family-source-diagnostic.backup-*'
PUBLIC_RECOVERY = TARGET / 'PF2F5QTT.md'
MAX_PROJECT_BACKUPS = 10
KEEP_NEWEST_BACKUPS = 3
EMERGENCY_ENTRY_LIMIT = 500_000
EMERGENCY_FREE_BYTES = 1 * 1024**3
EMERGENCY_BACKUP_BYTES = 2 * 1024**3
SAFETY_INTERVAL_SECONDS = 300

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

def graphical_environment_ready() -> bool:
    display=os.environ.get('DISPLAY','').strip()
    wayland=os.environ.get('WAYLAND_DISPLAY','').strip()
    return bool(display or wayland)

def desktop_approval(version: str, zip_name: str) -> bool | None:
    """Return True/False, or None when approval must wait for a GUI session."""
    if not APPROVAL_FILE.exists():
        return True
    if not graphical_environment_ready():
        log(f'Approval for {version} deferred: no DISPLAY or WAYLAND_DISPLAY is available yet.')
        return None
    zenity=shutil.which('zenity')
    if not zenity:
        log(f'Approval requested for {version}, but zenity is unavailable; update deferred.')
        return None
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

def start_bridge(expected_version: str | None = None) -> bool:
    if not graphical_environment_ready():
        PENDING_GUI_FILE.parent.mkdir(parents=True,exist_ok=True)
        PENDING_GUI_FILE.write_text(json.dumps({'version':expected_version,'reason':'graphical environment unavailable'},indent=2)+'\n',encoding='utf-8')
        log(f'Bridge start deferred for version {expected_version or "unknown"}: no graphical display is available. The graphical-login helper will retry.')
        return False
    logf=(STATE_DIR/'bridge.log').open('a')
    command=['/bin/sh', str(TARGET/'run-reddit-ollama-bridge.sh')]
    log(f'Starting bridge as {identity_summary()} command={command!r}')
    p=subprocess.Popen(command,cwd=TARGET,stdout=logf,stderr=subprocess.STDOUT,start_new_session=True,env=os.environ.copy())
    PID_FILE.write_text(str(p.pid))
    log(f'Started bridge launcher PID {p.pid}')
    if expected_version:
        marker=Path('/tmp/thecurversionofthisis.json')
        deadline=time.time()+25
        while time.time()<deadline:
            try:
                data=json.loads(marker.read_text(encoding='utf-8'))
                if data.get('version') == expected_version:
                    PENDING_GUI_FILE.unlink(missing_ok=True)
                    log(f'Verified running bridge version {expected_version}, pid={data.get("pid")}, program={data.get("program")}')
                    return True
            except Exception:
                pass
            if p.poll() is not None:
                raise RuntimeError(f'bridge launcher exited with return code {p.returncode}; see {STATE_DIR/"bridge.log"}')
            time.sleep(.5)
        raise RuntimeError(f'bridge did not publish expected version {expected_version} within 25 seconds; see {STATE_DIR/"bridge.log"}')
    return True

def install(z: Path, *, recovery: bool = False) -> str:
    global CURRENT_STAGE
    v=version_of_zip(z)
    version_text='.'.join(map(str,v)) if v else 'unknown'
    CURRENT_STAGE='approval'
    approval=True if recovery else desktop_approval(version_text, z.name)
    if approval is None:
        return 'deferred'
    if approval is False:
        log(f'Update {version_text} was not approved; leaving current version running.')
        return 'declined'
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
        started=start_bridge(manifest['version'])
        CURRENT_STAGE='complete'
        if started:
            log(f'Installed and verified version {manifest["version"]} from {z.name}')
        else:
            log(f'Installed version {manifest["version"]} from {z.name}; GUI start is pending graphical login.')
        return 'installed'


def count_entries_capped(root: Path, cap: int) -> int:
    count=0; stack=[root]
    while stack:
        current=stack.pop()
        try:
            with os.scandir(current) as it:
                for entry in it:
                    count += 1
                    if count >= cap: return count
                    try:
                        if entry.is_dir(follow_symlinks=False): stack.append(Path(entry.path))
                    except OSError: pass
        except (PermissionError, FileNotFoundError, NotADirectoryError):
            continue
    return count

def tree_size(path: Path) -> int:
    total=0; stack=[path]
    while stack:
        current=stack.pop()
        try:
            with os.scandir(current) as it:
                for entry in it:
                    try:
                        if entry.is_dir(follow_symlinks=False): stack.append(Path(entry.path))
                        else: total += entry.stat(follow_symlinks=False).st_size
                    except OSError: pass
        except OSError: pass
    return total

def project_git_needs_upload() -> bool:
    if not (TARGET/'.git').exists(): return False
    dirty=subprocess.run(['git','-C',str(TARGET),'status','--porcelain'],capture_output=True,text=True).stdout.strip()
    ahead=subprocess.run(['git','-C',str(TARGET),'rev-list','--count','@{u}..HEAD'],capture_output=True,text=True)
    return bool(dirty) or (ahead.returncode==0 and ahead.stdout.strip().isdigit() and int(ahead.stdout.strip())>0)

def attempt_safe_upload() -> None:
    if not project_git_needs_upload():
        log('PF2F5QTT: active project has no detected uncommitted or ahead source changes.')
        return
    publisher=TARGET/'publish-to-github.sh'
    if not publisher.is_file():
        log('PF2F5QTT: source needs upload, but the allowlisted publisher is missing.')
        return
    try:
        cp=subprocess.run(['/bin/sh',str(publisher)],cwd=TARGET,capture_output=True,text=True,timeout=180)
        log(f'PF2F5QTT safe upload returncode={cp.returncode}: '+(cp.stdout+cp.stderr).strip()[-2000:])
    except Exception as exc:
        log('PF2F5QTT safe upload failed: '+repr(exc))

def write_recovery_status(metrics: dict, removed: list[str], reasons: list[str]) -> None:
    if not TARGET.exists(): return
    reason_text=', '.join(reasons) if reasons else 'preventive project-backup limit'
    lines=[
      '# PF2F5QTT: HOL `/tmp` Recovery and Capacity Guide','',
      '> Public, sanitized recovery document. No account names, passwords, tokens, email addresses, IP addresses, or hostnames are included.','',
      '## Latest automatic safety event','',
      f'- UTC event time: `{time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}`',
      f'- Trigger reasons: `{reason_text}`',
      f'- `/tmp` used: `{metrics["used_percent"]:.1f}%`',
      f'- `/tmp` inode use: `{metrics["inode_percent"]:.1f}%`',
      f'- `/tmp` free bytes: `{metrics["free_bytes"]}`',
      f'- Counted `/tmp` entries: `{metrics["entry_count"]}`',
      f'- HOL backup directories before cleanup: `{metrics["backup_count"]}`',
      f'- HOL backup bytes before cleanup: `{metrics["backup_bytes"]}`','',
      '## Automatic action','',
      '- The active project was not deleted.',
      '- Only directories matching `/tmp/to-github/hol-family-source-diagnostic.backup-*` were eligible.',
      f'- Removed backup count: `{len(removed)}`.'
    ]
    if removed:
        lines += ['', 'Removed backups, recorded by sanitized basename:', '']
        lines += [f'- `{Path(item).name}`' for item in removed]
    lines += ['', '## T14 recovery steps','',
      '1. Run `df -h /tmp` and `df -i /tmp`.',
      '2. Run `systemctl --user status hol-family-source-updater.service --no-pager -l`.',
      '3. Run `tail -n 120 "$HOME/.local/state/hol-family-source-diagnostic/updater.log"`.',
      '4. Confirm `/tmp/to-github/hol-family-source-diagnostic` exists.',
      '5. When missing, run `systemctl --user restart hol-family-source-updater.service`.',
      '6. Start HOL with `cd /tmp/to-github/hol-family-source-diagnostic && ./run-reddit-ollama-bridge.sh`.',
      '7. Do not use broad deletion commands against `/tmp`.','',
      '## Important','',
      'The recoverable version is the last version successfully committed and pushed to GitHub. Debian cleanup behavior varies, so do not rely on every `/tmp` item being deleted on every reboot.','']
    PUBLIC_RECOVERY.write_text('\n'.join(lines),encoding='utf-8')
    if (TARGET/'.git').exists():
        subprocess.run(['git','-C',str(TARGET),'add','--','PF2F5QTT.md'],capture_output=True,text=True)
        staged=subprocess.run(['git','-C',str(TARGET),'diff','--cached','--quiet'])
        if staged.returncode != 0:
            subprocess.run(['git','-C',str(TARGET),'commit','-m','Update PF2F5QTT tmp safety guide'],capture_output=True,text=True)
            push=subprocess.run(['git','-C',str(TARGET),'push','origin','main'],capture_output=True,text=True,timeout=120)
            log(f'PF2F5QTT guide push returncode={push.returncode}: '+(push.stdout+push.stderr).strip()[-1200:])

def tmp_safety_check() -> None:
    try:
        disk=shutil.disk_usage(TMP_ROOT)
        vfs=os.statvfs(TMP_ROOT)
        inode_total=vfs.f_files; inode_free=vfs.f_ffree
        inode_percent=(100.0*(inode_total-inode_free)/inode_total) if inode_total else 0.0
        used_percent=(100.0*disk.used/disk.total) if disk.total else 0.0
        backups=sorted([p for p in BACKUP_PARENT.glob(BACKUP_GLOB) if p.is_dir()],key=lambda p:p.stat().st_mtime,reverse=True)
        backup_bytes=sum(tree_size(p) for p in backups)
        need_count=used_percent>=90 or inode_percent>=90 or disk.free<2*EMERGENCY_FREE_BYTES or len(backups)>MAX_PROJECT_BACKUPS or backup_bytes>=1024**3
        entry_count=count_entries_capped(TMP_ROOT,EMERGENCY_ENTRY_LIMIT) if need_count else 0
        reasons=[]
        if used_percent>=95: reasons.append('tmp filesystem at least 95 percent used')
        if inode_percent>=95: reasons.append('tmp inode use at least 95 percent')
        if disk.free<EMERGENCY_FREE_BYTES: reasons.append('tmp filesystem below 1 GiB free')
        if entry_count>=EMERGENCY_ENTRY_LIMIT: reasons.append('tmp contains at least 500000 entries')
        if backup_bytes>=EMERGENCY_BACKUP_BYTES: reasons.append('HOL backups total at least 2 GiB')
        preventive=len(backups)>MAX_PROJECT_BACKUPS
        if not reasons and not preventive: return
        metrics={'used_percent':used_percent,'inode_percent':inode_percent,'free_bytes':disk.free,'entry_count':entry_count,'backup_count':len(backups),'backup_bytes':backup_bytes}
        log('PF2F5QTT safety trigger: '+(', '.join(reasons) if reasons else f'{len(backups)} HOL backups exceeds cap {MAX_PROJECT_BACKUPS}'))
        attempt_safe_upload()
        removed=[]
        for old in backups[KEEP_NEWEST_BACKUPS:]:
            try:
                shutil.rmtree(old); removed.append(str(old)); log('PF2F5QTT removed old HOL backup: '+old.name)
            except Exception as exc:
                log('PF2F5QTT could not remove '+old.name+': '+repr(exc))
        write_recovery_status(metrics,removed,reasons)
    except Exception as exc:
        log('PF2F5QTT safety check failed: '+repr(exc))

def newest_local_zip() -> tuple[tuple[int,int,int],Path] | None:
    candidates=[]
    for p in DOWNLOADS.glob('hol-family-source-diagnostic-v*.zip'):
        try:
            v=version_of_zip(p)
            if v and p.stat().st_size>0:
                candidates.append((v,p))
        except OSError:
            continue
    return max(candidates,key=lambda item:item[0]) if candidates else None

def restore_if_missing() -> bool:
    if TARGET.exists():
        return True
    if (PERSISTENT_CACHE/'chrome-extension/manifest.json').is_file() and (PERSISTENT_CACHE/'378876.txt').is_file():
        log(f'Project missing after restart; restoring from persistent cache {PERSISTENT_CACHE}.')
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(PERSISTENT_CACHE, TARGET, symlinks=True)
        for script in TARGET.glob('*.sh'):
            script.chmod(script.stat().st_mode | 0o111)
        subprocess.run(['python3','-m','py_compile',str(TARGET/'hol-reddit-ollama-bridge.py')],check=True)
        run_sh(TARGET/'install-extension-to-home.sh',cwd=TARGET)
        manifest=json.loads((TARGET/'chrome-extension/manifest.json').read_text())
        start_bridge(manifest.get('version'))
        return True
    local=newest_local_zip()
    if local:
        version,path=local
        log(f'Project missing after restart; restoring from local Downloads ZIP {path.name}.')
        try:
            result=install(path,recovery=True)
            return result == 'installed' and TARGET.exists()
        except Exception as exc:
            log('LOCAL ZIP RESTORE FAILED: '+repr(exc))
    log('Project missing after restart; trying the last GitHub version.')
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    cp=subprocess.run(['git','clone','https://github.com/we6jbo/hol-family-source-diagnostic.git',str(TARGET)],capture_output=True,text=True,timeout=120)
    if cp.returncode != 0:
        shutil.rmtree(TARGET,ignore_errors=True)
        raise RuntimeError('GitHub restore failed: '+cp.stderr.strip())
    subprocess.run(['python3','-m','py_compile',str(TARGET/'hol-reddit-ollama-bridge.py')],check=True)
    for script in TARGET.glob('*.sh'):
        script.chmod(script.stat().st_mode | 0o111)
    run_sh(TARGET/'install-extension-to-home.sh',cwd=TARGET)
    manifest=json.loads((TARGET/'chrome-extension/manifest.json').read_text())
    start_bridge(manifest.get('version'))
    return True

def start_pending_gui_if_possible() -> None:
    if not TARGET.exists() or not graphical_environment_ready():
        return
    marker=Path('/tmp/thecurversionofthisis.json')
    expected='.'.join(map(str,current_version()))
    try:
        data=json.loads(marker.read_text(encoding='utf-8'))
        pid=int(data.get('pid',0))
        if data.get('version') == expected and pid>0:
            os.kill(pid,0)
            PENDING_GUI_FILE.unlink(missing_ok=True)
            return
    except Exception:
        pass
    stop_bridge()
    start_bridge(expected)


def main():
    STATE_DIR.mkdir(parents=True,exist_ok=True)
    seen_success=set()
    declined_until={}
    last_restore_attempt=0.0
    last_gui_attempt=0.0
    tmp_safety_check()
    last_safety=time.monotonic()
    log('Updater identity: '+identity_summary())
    log('Graphical environment: DISPLAY='+repr(os.environ.get('DISPLAY'))+' WAYLAND_DISPLAY='+repr(os.environ.get('WAYLAND_DISPLAY')))
    log('Optional confirmation mode: '+('enabled' if APPROVAL_FILE.exists() else 'disabled')+f' ({APPROVAL_FILE})')
    log('Watching '+str(DOWNLOADS)+' for HOL version ZIP files.')
    while True:
        now=time.monotonic()
        if not TARGET.exists() and now-last_restore_attempt >= RESTORE_RETRY_SECONDS:
            last_restore_attempt=now
            try:
                restore_if_missing()
            except Exception as e:
                log('STARTUP RESTORE DEFERRED: '+repr(e))
        if TARGET.exists() and now-last_gui_attempt >= GUI_RETRY_SECONDS:
            last_gui_attempt=now
            try:
                start_pending_gui_if_possible()
            except Exception as e:
                log('GUI START RETRY FAILED: '+repr(e))
        if now-last_safety >= SAFETY_INTERVAL_SECONDS:
            tmp_safety_check(); last_safety=now
        candidates=[]
        for p in DOWNLOADS.glob('hol-family-source-diagnostic-v*.zip'):
            try:
                v=version_of_zip(p)
                if v and p.stat().st_size>0: candidates.append((v,p))
            except OSError:
                continue
        for v,p in sorted(candidates):
            key=(str(p),p.stat().st_mtime_ns,p.stat().st_size)
            if key in seen_success or time.time() < declined_until.get(key,0):
                continue
            if v>current_version():
                try:
                    result=install(p)
                    if result == 'installed':
                        seen_success.add(key)
                    elif result == 'declined':
                        declined_until[key]=time.time()+600
                    # deferred is intentionally not marked seen; retry after GUI import
                except Exception as e:
                    log(f'UPDATE FAILED during stage={CURRENT_STAGE}: {type(e).__name__}: {e}')
                    log(traceback.format_exc().rstrip())
            else:
                seen_success.add(key)
        time.sleep(5)
if __name__=='__main__': main()
