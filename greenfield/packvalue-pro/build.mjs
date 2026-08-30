import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const corePath = path.join(here, 'core.mjs');
const templatePath = path.join(here, 'template.html');
const distDir = path.join(here, 'dist');
const outPath = path.join(distDir, 'packvalue-pro.html');

const core = fs.readFileSync(corePath, 'utf8').replace(/^export\s+/gm, '');
const template = fs.readFileSync(templatePath, 'utf8');
if (!template.includes('/*__PACKVALUE_CORE__*/')) throw new Error('core_placeholder_missing');
const output = template.replace('/*__PACKVALUE_CORE__*/', core);

const forbidden = [
  /\bfetch\s*\(/i,
  /XMLHttpRequest/i,
  /navigator\.sendBeacon/i,
  /new\s+WebSocket/i,
  /<script[^>]+src=/i,
  /<form[^>]+action=/i,
  /https?:\/\//i
];
for (const pattern of forbidden) {
  if (pattern.test(output)) throw new Error(`standalone_network_gate:${pattern}`);
}
if (/Uma Gestão Inteligente|UGI|Bom de Clique|Orbit/i.test(output)) throw new Error('greenfield_brand_leak');
if (!output.includes('Nenhuma economia ou margem é garantida')) throw new Error('commercial_disclaimer_missing');

fs.mkdirSync(distDir, { recursive: true });
fs.writeFileSync(outPath, output);
const sha256 = crypto.createHash('sha256').update(output).digest('hex');
fs.writeFileSync(path.join(distDir, 'manifest.json'), JSON.stringify({
  schema_version: '1.0',
  product_id: 'packvalue-pro-r1',
  file: 'packvalue-pro.html',
  mime_type: 'text/html; charset=utf-8',
  bytes: Buffer.byteLength(output),
  sha256,
  network_capability: false,
  pii_collection: false,
  server_required_after_delivery: false
}, null, 2));
console.log(`PACKVALUE_PRO_BUILD=PASS bytes=${Buffer.byteLength(output)} sha256=${sha256}`);
