import assert from 'node:assert/strict';
import {stripPii,listProducts,listSalesSanitized,createReconciliationWebhook} from './client.mjs';

const env={KIWIFY_CLIENT_ID:'cid',KIWIFY_CLIENT_SECRET:'secret',KIWIFY_ACCOUNT_ID:'acct'};
const calls=[];
async function fakeFetch(url,opts={}){
  calls.push({url,opts});
  if(url.endsWith('/oauth/token'))return new Response(JSON.stringify({access_token:'tok'}),{status:200,headers:{'content-type':'application/json'}});
  if(url.includes('/products?'))return new Response(JSON.stringify({data:[{id:'p1',name:'Produto',status:'active'}]}),{status:200,headers:{'content-type':'application/json'}});
  if(url.includes('/sales?'))return new Response(JSON.stringify({data:[{id:'s1',status:'paid',customer:{name:'Pessoa',email:'x@y.test',cpf:'123',address:{city:'X'}},product:{id:'p1',name:'Produto'},amount:49.9}]}),{status:200,headers:{'content-type':'application/json'}});
  if(url.endsWith('/webhooks'))return new Response(JSON.stringify({id:'w1'}),{status:200,headers:{'content-type':'application/json'}});
  return new Response('{}',{status:404});
}
let x=stripPii({id:'1',customer:{email:'x',cpf:'1'},email:'y',amount:1});assert.deepEqual(x,{id:'1',amount:1});
let p=await listProducts(env,{fetchImpl:fakeFetch});assert.equal(p.data[0].id,'p1');
let s=await listSalesSanitized(env,{fetchImpl:fakeFetch});assert.equal(s.data[0].id,'s1');assert.equal('customer' in s.data[0],false);assert.equal(JSON.stringify(s).includes('x@y.test'),false);assert.equal(JSON.stringify(s).includes('123'),false);
let w=await createReconciliationWebhook(env,{url:'https://example.test/webhook',token:'1234567890abcdef',fetchImpl:fakeFetch});assert.equal(w.id,'w1');
const webhookCall=calls.find(c=>c.url.endsWith('/webhooks'));const body=JSON.parse(webhookCall.opts.body);assert.deepEqual(body.triggers,['compra_aprovada','compra_reembolsada','chargeback']);
await assert.rejects(()=>createReconciliationWebhook(env,{url:'http://bad.test',token:'1234567890abcdef',fetchImpl:fakeFetch}),/invalid_webhook_url/);
console.log('KIWIFY_RECONCILIATION_MOCK_QA=PASS');
