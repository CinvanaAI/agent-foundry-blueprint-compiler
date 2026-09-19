import json
import tempfile
from pathlib import Path
from agent_foundry_blueprint_compiler import compile_blueprint, compile_runtime_package, parse_blueprint

record = json.loads(Path(__file__).with_name('record.json').read_text())
blueprint = compile_blueprint(record)
runtime = compile_runtime_package(blueprint)
assert runtime['package']['logic']['logic_source'] == record['logic']
try:
    parse_blueprint(blueprint.replace('Normalize Text Returns', 'Other Returns'))
except ValueError:
    rejected = True
else:
    raise AssertionError('Mixed-package blueprint was accepted')
root = Path(tempfile.mkdtemp(prefix='blueprint-demo-'))
(root/'package.blueprint.txt').write_text(blueprint, encoding='utf-8')
(root/'runtime.json').write_text(json.dumps(runtime,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'name': runtime['package']['name'], 'round_trip': True, 'mixed_package_rejected': rejected, 'blueprint_sha256': runtime['blueprint_sha256'], 'evidence_root': str(root)},indent=2))
