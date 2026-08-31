const BASE='https://public-api.kiwify.com/v1';
const PII_KEYS=new Set(['customer','buyer','client','name','email','cpf','cnpj','mobile','phone','telephone','instagram','address','street','number','complement','neighborhood','city','state','zipcode','zip_code']);

function required(env,key){const v=String(env?.[key]||'').trim();if(!v)throw new Error(`missing_${key.toLowerCase()}`);return v}
export function stripPii(value){
  if(Array.isArray(value))return value.map(stripPii);
  if(!value||typeof value!=='object')return value;
  const out={};
  for(const [k,v] of Object.entries(value)){
    if(PII_KEYS.has(k.toLowerCase()))continue;
    out[k]=stripPii(v);
  }
  return out;
}
export async function getToken(env,fetchImpl=fetch){
  const clientId=required(env,'KIWIFY_CLIENT_ID'),clientSecret=required(env,'KIWIFY_CLIENT_SECRET');
  const body=new URLSearchParams({client_id:clientId,client_secret:clientSecret});
  const r=await fetchImpl(`${BASE}/oauth/token`,{method:'POST',headers:{'content-type':'application/x-www-form-urlencoded'},body});
  if(!r.ok)throw new Error(`kiwify_oauth_${r.status}`);
  const j=await r.json();if(!j?.access_token)throw new Error('kiwify_oauth_token_missing');return j.access_token;
}
async function request(env,path,{method='GET',body,fetchImpl=fetch}={}){
  const token=await getToken(env,fetchImpl), account=required(env,'KIWIFY_ACCOUNT_ID');
  const headers={authorization:`Bearer ${token}`,'x-kiwify-account-id':account};
  if(body!==undefined)headers['content-type']='application/json';
  const r=await fetchImpl(`${BASE}${path}`,{method,headers,body:body===undefined?undefined:JSON.stringify(body)});
  if(!r.ok)throw new Error(`kiwify_api_${r.status}`);return r.json();
}
export async function listProducts(env,{pageSize=50,pageNumber=1,fetchImpl=fetch}={}){
  const qs=new URLSearchParams({page_size:String(Math.min(100,Math.max(1,pageSize))),page_number:String(Math.max(1,pageNumber))});
  return request(env,`/products?${qs}`,{fetchImpl});
}
export async function listSalesSanitized(env,{startDate,endDate,pageSize=50,pageNumber=1,fetchImpl=fetch}={}){
  const qs=new URLSearchParams({page_size:String(Math.min(100,Math.max(1,pageSize))),page_number:String(Math.max(1,pageNumber))});
  if(startDate)qs.set('start_date',startDate);if(endDate)qs.set('end_date',endDate);
  return stripPii(await request(env,`/sales?${qs}`,{fetchImpl}));
}
export async function createReconciliationWebhook(env,{url,token,products='all',fetchImpl=fetch}){
  if(!/^https:\/\//i.test(String(url||'')))throw new Error('invalid_webhook_url');
  if(String(token||'').length<16)throw new Error('webhook_token_too_short');
  return request(env,'/webhooks',{method:'POST',body:{name:'LSI Payment Hub Reconciliation',url,products,triggers:['compra_aprovada','compra_reembolsada','chargeback'],token},fetchImpl});
}
