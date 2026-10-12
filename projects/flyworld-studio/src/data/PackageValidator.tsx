import { useState } from 'react';
import { MAX_PACKAGE_BYTES, parseCircuitPackage } from './schema';
import { parseDemoPackage } from './demoSchema';
import { parseRealPackageText, BROWSER_LIMITS } from '../realdata/schema';

export function PackageValidator() {
  const [result, setResult] = useState('Active: educational display package. 5 systems, 13 generic nodes, 8 illustrative relations. No biological records.');
  return <div className="package-validator"><p>Validate educational or future biological package structure. This dialog never replaces the bundled demo. A schema pass does not verify a scientific claim.</p>
    <label className="file-label">Validate a JSON package<input type="file" accept=".json,application/json" onChange={async e => {
      const file = e.target.files?.[0]; if (!file) return;
      try {
        if (file.size > BROWSER_LIMITS.maxPackageBytes) throw new Error('Package exceeds the 4 MiB limit');
        const text = await file.text();
        const input = JSON.parse(text);
        if (input?.format === 'FLYWORLD_CIRCUIT_PACKAGE') {
          const pkg = parseRealPackageText(text);
          setResult(`Schema valid: ${pkg.name}. ${pkg.neurons.length} bodies, ${pkg.edges.length} raw edges. Load it through MaleCNS data → Import small local package. Schema validity does not independently verify supplied scientific provenance.`);
        } else if (file.size > MAX_PACKAGE_BYTES) throw new Error('Legacy/demo package exceeds the 2 MiB limit');
        else if (input?.format === 'FLYWORLD_EDUCATIONAL_DEMO') {
          const pkg = parseDemoPackage(input);
          setResult(`Schema valid: ${pkg.name}. ${pkg.neurons.length} generic nodes and ${pkg.relations.length} illustrative relations. No biological records. Package has not been loaded or scientifically verified.`);
        } else {
          const pkg = parseCircuitPackage(input);
          setResult(`Schema valid: ${pkg.name}. ${pkg.neurons.length} neuron records, ${pkg.edges.length} edges. Package has not been loaded or scientifically verified.`);
        }
      } catch (error) { setResult(`Rejected: ${error instanceof Error ? error.message : 'Invalid package'}`); }
    }} /></label><pre role="status">{result}</pre>
    <a href={import.meta.env.BASE_URL + 'data/demo/educational-circuits.json'} download>Download the generic educational circuits ↗</a>
    <a href={import.meta.env.BASE_URL + 'data/demo/timeline.json'} download>Download the synthetic demo timeline ↗</a>
    <div className="demo-downloads"><strong>Individual educational circuit packages</strong>{['visual', 'taste', 'motor', 'mating', 'central'].map(name => <a key={name} href={`/data/demo/circuits/${name}.json`} download>{name} demo package ↗</a>)}</div>
  </div>;
}
