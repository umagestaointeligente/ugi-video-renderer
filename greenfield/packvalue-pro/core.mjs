export function parseNumber(value) {
  const raw = String(value ?? '').trim();
  if (!raw) return NaN;
  let normalized = raw.replace(/\s/g, '').replace(/^R\$/i, '');
  if (normalized.includes(',') && normalized.includes('.')) {
    normalized = normalized.lastIndexOf(',') > normalized.lastIndexOf('.')
      ? normalized.replace(/\./g, '').replace(',', '.')
      : normalized.replace(/,/g, '');
  } else if (normalized.includes(',')) {
    normalized = normalized.replace(',', '.');
  }
  const number = Number(normalized);
  return Number.isFinite(number) ? number : NaN;
}

export function normalizeUnit(unit) {
  const value = String(unit || '').trim().toLowerCase();
  if (['g', 'grama', 'gramas'].includes(value)) return { dimension: 'kg', multiplier: 0.001, label: 'kg' };
  if (['kg', 'quilo', 'quilos'].includes(value)) return { dimension: 'kg', multiplier: 1, label: 'kg' };
  if (['ml', 'mililitro', 'mililitros'].includes(value)) return { dimension: 'l', multiplier: 0.001, label: 'L' };
  if (['l', 'lt', 'litro', 'litros'].includes(value)) return { dimension: 'l', multiplier: 1, label: 'L' };
  if (['un', 'und', 'unidade', 'unidades', 'unit'].includes(value)) return { dimension: 'un', multiplier: 1, label: 'un' };
  return null;
}

export function calculateRow(row, index = 0) {
  const sku = String(row.sku ?? row.SKU ?? '').trim() || `SKU-${index + 1}`;
  const descricao = String(row.descricao ?? row.descrição ?? row.description ?? '').trim();
  const qtdPack = parseNumber(row.qtd_pack ?? row.quantidade_pack ?? row.quantidade ?? row.qty ?? 1);
  const tamanho = parseNumber(row.tamanho ?? row.size ?? 1);
  const unit = normalizeUnit(row.unidade ?? row.unit ?? 'un');
  const preco = parseNumber(row.preco ?? row.preço ?? row.price);
  const frete = parseNumber(row.frete ?? row.shipping ?? 0);
  const desconto = parseNumber(row.desconto_pct ?? row.desconto ?? row.discount ?? 0);

  const issues = [];
  if (!(qtdPack > 0)) issues.push('qtd_pack deve ser maior que zero');
  if (!(tamanho > 0)) issues.push('tamanho deve ser maior que zero');
  if (!unit) issues.push('unidade deve ser g, kg, ml, L ou un');
  if (!(preco >= 0)) issues.push('preco inválido');
  if (!(frete >= 0)) issues.push('frete inválido');
  if (!(desconto >= 0 && desconto <= 100)) issues.push('desconto deve ficar entre 0 e 100');

  if (issues.length) return { ok: false, sku, descricao, issues, source: row };

  const quantidadeNormalizada = qtdPack * tamanho * unit.multiplier;
  const custoFinal = preco * (1 - desconto / 100) + frete;
  const precoNormalizado = custoFinal / quantidadeNormalizada;
  const economiaDesconto = preco * (desconto / 100);

  return {
    ok: true,
    sku,
    descricao,
    dimension: unit.dimension,
    unidade_normalizada: unit.label,
    quantidade_pack: qtdPack,
    tamanho,
    unidade_original: String(row.unidade ?? row.unit ?? 'un'),
    preco,
    frete,
    desconto_pct: desconto,
    quantidade_normalizada: quantidadeNormalizada,
    custo_final: custoFinal,
    preco_normalizado: precoNormalizado,
    economia_desconto: economiaDesconto
  };
}

export function rankRows(rows) {
  const calculated = rows.map((row, index) => calculateRow(row, index));
  const valid = calculated.filter(item => item.ok);
  for (const dimension of ['kg', 'l', 'un']) {
    const group = valid.filter(item => item.dimension === dimension).sort((a, b) => a.preco_normalizado - b.preco_normalizado);
    group.forEach((item, rank) => {
      item.rank = rank + 1;
      item.melhor_valor = rank === 0;
      const best = group[0]?.preco_normalizado || 0;
      item.premium_vs_melhor_pct = best > 0 ? ((item.preco_normalizado / best) - 1) * 100 : 0;
    });
  }
  return calculated;
}

export function detectDelimiter(text) {
  const first = String(text || '').split(/\r?\n/).find(line => line.trim()) || '';
  const candidates = [',', ';', '\t'];
  return candidates.sort((a, b) => first.split(b).length - first.split(a).length)[0] || ',';
}

export function parseDelimited(text) {
  const clean = String(text || '').replace(/^\uFEFF/, '').trim();
  if (!clean) return [];
  const delimiter = detectDelimiter(clean);
  const lines = clean.split(/\r?\n/).filter(Boolean);
  const parseLine = line => {
    const out = [];
    let current = '';
    let quoted = false;
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        if (quoted && line[i + 1] === '"') { current += '"'; i++; }
        else quoted = !quoted;
      } else if (char === delimiter && !quoted) {
        out.push(current.trim()); current = '';
      } else current += char;
    }
    out.push(current.trim());
    return out;
  };
  const headers = parseLine(lines.shift()).map(header => header.trim().toLowerCase());
  return lines.map(line => {
    const values = parseLine(line);
    return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? '']));
  });
}

function csvEscape(value) {
  const text = String(value ?? '');
  return /[;"\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

export function resultsToCsv(results) {
  const headers = ['sku','descricao','status','dimensao','rank','melhor_valor','custo_final','preco_normalizado','unidade_normalizada','premium_vs_melhor_pct','issues'];
  const rows = results.map(item => [
    item.sku,
    item.descricao,
    item.ok ? 'OK' : 'ERRO',
    item.dimension || '',
    item.rank || '',
    item.ok ? (item.melhor_valor ? 'SIM' : 'NÃO') : '',
    item.ok ? item.custo_final.toFixed(2) : '',
    item.ok ? item.preco_normalizado.toFixed(6) : '',
    item.unidade_normalizada || '',
    item.ok ? item.premium_vs_melhor_pct.toFixed(2) : '',
    item.ok ? '' : (item.issues || []).join(' | ')
  ]);
  return [headers, ...rows].map(row => row.map(csvEscape).join(';')).join('\n');
}
