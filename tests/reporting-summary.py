#!/usr/bin/env python3
"""Isolated shell tests: no systemd operations, network access or installation."""
from pathlib import Path
import subprocess, tempfile, shlex
root = Path(__file__).resolve().parents[1]
def block(name):
    s=(root/name).read_text()
    return s[s.index('# BEGIN reliable reporting summary'):s.index('# END reliable reporting summary')]
code=block('V2bX.sh')
assert code==block('install.sh'), 'summary implementations drifted'
def row(key='a', nid=102, state='enabled', mode='auto'):
    return f'V2BX_REPORTING_STATUS_V1 binding={key*64} node_id={nid} node_type=anytls state={state} mode={mode}'
reset='V2BX_REPORTING_RESET_V1\n'
for fixture, expected, missing in [
 (reset+row()+'\n'+row('b',103,'disabled','off'), ['节点 102','已启用','节点 103','未启用'], []),
 (reset+row()+'\n'+row(state='unknown'), ['状态未确认'], ['已启用']),
 (reset+row()+'\n'+reset+row('b',103,'disabled'), ['节点 103','未启用'], ['节点 102']),
 (row(), [], ['节点 102']),
 (reset+row()+' bad=extra', [], ['已启用']),
]:
    p=subprocess.run(['bash','-c',code+'\nparse_reporting_status'],input=fixture,text=True,capture_output=True)
    assert all(x in p.stdout for x in expected),(fixture,p.stdout)
    assert all(x not in p.stdout for x in missing),(fixture,p.stdout)

with tempfile.TemporaryDirectory() as tmp:
    counter=Path(tmp)/'counter'
    for case in ['ok','partial','stale','inactive','unreadable','old-binary','alpine','changed-invocation']:
        counter.write_text('0')
        fixture=reset+row()+'\n'+row('b',103,'disabled','off')
        if case=='partial':fixture=reset+row()+'\n'+row('b',103,'unknown')
        if case=='old-binary':fixture='level=info msg="Reliable traffic reporting enabled" reliable_reporting=true tag=test'
        pre='release='+('alpine' if case=='alpine' else 'debian')+'\n'+code+'\n'
        pre+='fixture='+shlex.quote(fixture)+'\nsleep() { :; }\n'
        pre+='systemctl() { echo '+('inactive' if case=='inactive' else 'active')+'; }\n'
        pre+='journalctl() { '+('return 1;' if case=='unreadable' else 'printf "%s\\n" "$fixture";')+' }\n'
        if case=='changed-invocation':
            q=shlex.quote(str(counter))
            pre+='reporting_invocation() { n=$(cat '+q+'); n=$((n+1)); echo "$n" > '+q+'; if (( n % 2 )); then echo '+('a'*32)+'; else echo '+('b'*32)+'; fi; }\n'
        else: pre+='reporting_invocation() { echo '+('a'*32)+'; }\n'
        previous='a'*32 if case=='stale' else 'b'*32
        p=subprocess.run(['bash','-c',pre+'show_reporting_status '+previous],capture_output=True,text=True,timeout=5)
        assert p.returncode==0,(case,p.stderr)
        if case=='ok':assert '节点 102' in p.stdout and '已启用' in p.stdout and '节点 103' in p.stdout and '未启用' in p.stdout
        elif case=='partial':assert '节点 102' in p.stdout and '节点 103' in p.stdout and '状态未确认' in p.stdout
        else:assert '状态未确认' in p.stdout and '已启用' not in p.stdout,(case,p.stdout)
print('PASS: 5 parser scenarios + 8 service scenarios; shared helper identical; no services touched')

# Exercise the actual restart wrapper as well as the shared helper.
script=(root/'V2bX.sh').read_text()
restart=script[script.index('\nrestart() {'):script.index('\nstatus() {')]
pre='release=debian\nreporting_invocation() { echo previous-invocation; }\nsystemctl() { :; }\nsleep() { :; }\ncheck_status() { return 0; }\nshow_reporting_status() { printf "SUMMARY_PREVIOUS=%s\\n" "$1"; }\n'
p=subprocess.run(['bash','-c',pre+restart+'\nrestart 0'],capture_output=True,text=True,timeout=5)
assert 'SUMMARY_PREVIOUS=previous-invocation' in p.stdout, p.stdout
print('PASS: actual restart wrapper passes its pre-restart invocation to summary')
