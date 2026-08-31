import assert from 'node:assert/strict';
import worker from './worker.mjs';

const secret='test-proxy-secret-not-production';
const env={RAPIDAPI_PROXY_SECRET:secret};
const req=(path,body,headers={})=>new Request(`https://example.test${path}`,{method:body===undefined?'GET':'POST',headers:{'content-type':'application/json',...headers},body:body===undefined?undefined:JSON.stringify(body)});

let r=await worker.fetch(req('/health'),env);assert.equal(r.status,200);let j=await r.json();assert.equal(j.ok,true);assert.equal(j.proxySecretConfigured,true);
r=await worker.fetch(req('/v1/normalize',{items:[{price:10,packageSize:500,unit:'g'}]}),env);assert.equal(r.status,401);
r=await worker.fetch(req('/v1/normalize',{items:[{name:'A',price:10,packageSize:500,unit:'g'},{name:'B',price:18,packageSize:1,unit:'kg'}]},{'x-rapidapi-proxy-secret':secret}),env);assert.equal(r.status,200);j=await r.json();assert.equal(j.results[0].normalizedPrice,20);assert.equal(j.results[1].normalizedPrice,18);assert.equal(j.results[1].bestWithinUnit,true);assert.equal(j.financialOutcomeGuaranteed,false);
r=await worker.fetch(req('/v1/normalize',{items:[]},{'x-rapidapi-proxy-secret':secret}),env);assert.equal(r.status,400);
r=await worker.fetch(req('/v1/normalize',{items:[{price:1,packageSize:1,unit:'kg'}]},{'x-rapidapi-proxy-secret':secret}),{});assert.equal(r.status,503);
console.log('RAPIDAPI_PACKVALUE_BACKEND_TESTS=PASS');
