from pathlib import Path
import tempfile,subprocess,json
source=(Path(__file__).resolve().parents[1] / 'initconfig.sh').read_text()
for name,answers,core,expected in [
 ('anytls',['y','https://example.invalid','synthetic-test-key','y','2','42','8','3','node.example.invalid','n'],'sing','info'),
 ('sing-ss',['y','https://example.invalid','synthetic-test-key','y','2','42','1','n','n'],'sing','error'),
 ('xray-vmess',['y','https://example.invalid','synthetic-test-key','y','1','42','3','n','n'],'xray','error'),
]:
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);(p/'config.json').write_text('{}')
  script=source.replace('/etc/V2bX',d)+'\nfunction v2bx(){ :; }\nfunction check_ipv6_support(){ echo 0; }\ngenerate_config_file\n'
  r=subprocess.run(['bash','-c',script],input='\n'.join(answers)+'\n',text=True,capture_output=True,timeout=10)
  assert r.returncode==0,(name,r.stderr)
  c=json.loads((p/'config.json').read_text());level=next(x['Log']['Level'] for x in c['Cores'] if x['Type']==core)
  assert level==expected,(name,level)
  assert c['Nodes'][0]['NodeID']==42 and c['Nodes'][0]['ApiHost']=='https://example.invalid'
  assert c['Nodes'][0].get('AnyTLSAuditAccess') is (True if name=='anytls' else None)
  print(name,'PASS',level)
