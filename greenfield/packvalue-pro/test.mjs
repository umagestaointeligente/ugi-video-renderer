import assert from 'node:assert/strict';
import { calculateRow, parseDelimited, rankRows, resultsToCsv } from './core.mjs';

const a = calculateRow({sku:'A',qtd_pack:'3',tamanho:'200',unidade:'g',preco:'17,90',frete:'0',desconto_pct:'0'});
assert.equal(a.ok, true);
assert.equal(a.dimension, 'kg');
assert.ok(Math.abs(a.quantidade_normalizada - 0.6) < 1e-9);
assert.ok(Math.abs(a.preco_normalizado - (17.9 / 0.6)) < 1e-9);

const b = calculateRow({sku:'B',qtd_pack:'1',tamanho:'1',unidade:'kg',preco:'27,90',frete:'0',desconto_pct:'10'});
assert.equal(b.ok, true);
assert.ok(Math.abs(b.custo_final - 25.11) < 1e-9);
assert.ok(Math.abs(b.preco_normalizado - 25.11) < 1e-9);

const rows = parseDelimited('sku;descricao;qtd_pack;tamanho;unidade;preco;frete;desconto_pct\nA;Pack A;3;200;g;17,90;0;0\nB;Pack B;1;1;kg;27,90;0;10');
assert.equal(rows.length, 2);
const ranked = rankRows(rows);
assert.equal(ranked.filter(x => x.ok).length, 2);
assert.equal(ranked.find(x => x.sku === 'B').rank, 1);
assert.equal(ranked.find(x => x.sku === 'B').melhor_valor, true);
assert.equal(ranked.find(x => x.sku === 'A').rank, 2);

const volume = rankRows(parseDelimited('sku;descricao;qtd_pack;tamanho;unidade;preco;frete;desconto_pct\nV1;Pack;6;330;ml;19,90;0;0\nV2;Garrafa;1;2;L;8,99;0;0'));
assert.equal(volume.find(x => x.sku === 'V2').rank, 1);

const invalid = calculateRow({sku:'ERR',qtd_pack:0,tamanho:1,unidade:'x',preco:'-1',frete:0,desconto_pct:101});
assert.equal(invalid.ok, false);
assert.ok(invalid.issues.length >= 4);

const csv = resultsToCsv(ranked);
assert.match(csv, /preco_normalizado/);
assert.match(csv, /A;Pack A/);
assert.doesNotMatch(csv, /undefined|NaN/);

console.log('PACKVALUE_PRO_TESTS=PASS');
