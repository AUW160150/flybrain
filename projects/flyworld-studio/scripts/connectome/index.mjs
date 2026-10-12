import { existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const project=fileURLToPath(new URL('../../',import.meta.url));
const workspacePython=fileURLToPath(new URL('../../../../.venv/bin/python',import.meta.url));
const python=process.env.FLYWORLD_PYTHON || (existsSync(workspacePython)?workspacePython:'python3');
const result=spawnSync(python,['scripts/connectome/build_index.py',...process.argv.slice(2)],{cwd:project,stdio:'inherit'});
if(result.error)console.error(result.error.message);
process.exit(result.status??1);
