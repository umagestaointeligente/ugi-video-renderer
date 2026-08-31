import crypto from 'node:crypto';

const STRIPE_API='https://api.stripe.com/v1';
export const PACKVALUE_STRIPE_PRICE_BRL=49.90;
export const PACKVALUE_STRIPE_UNIT_AMOUNT=4990;

export async function createPackValuePaymentLink({secretKey,fetchImpl=fetch}){
  if(!String(secretKey||'').startsWith('sk_'))throw new Error('stripe_secret_key_missing');
  const body=new URLSearchParams();
  body.set('line_items[0][price_data][currency]','brl');
  body.set('line_items[0][price_data][unit_amount]',String(PACKVALUE_STRIPE_UNIT_AMOUNT));
  body.set('line_items[0][price_data][product_data][name]','PackValue PRO');
  body.set('line_items[0][price_data][product_data][description]','Comparador em lote de SKUs, preço normalizado, frete e desconto');
  body.set('line_items[0][quantity]','1');
  body.set('after_completion[type]','hosted_confirmation');
  body.set('after_completion[hosted_confirmation][custom_message]','Pagamento recebido. A liberação digital depende da confirmação do webhook.');
  const r=await fetchImpl(`${STRIPE_API}/payment_links`,{method:'POST',headers:{authorization:`Bearer ${secretKey}`,'content-type':'application/x-www-form-urlencoded'},body});
  const j=await r.json().catch(()=>({}));
  if(!r.ok)throw new Error(`stripe_payment_link_${r.status}:${j?.error?.code||'unknown'}`);
  if(!j?.id||!/^https:\/\//.test(String(j.url||'')))throw new Error('stripe_payment_link_invalid_response');
  return {id:j.id,url:j.url,active:j.active!==false,livemode:Boolean(j.livemode),currency:j.currency||'brl',unitAmount:PACKVALUE_STRIPE_UNIT_AMOUNT};
}

function parseSignature(header){
  const parts=String(header||'').split(',').map(x=>x.trim()).filter(Boolean);let t=null;const v1=[];
  for(const part of parts){const i=part.indexOf('=');if(i<0)continue;const k=part.slice(0,i),v=part.slice(i+1);if(k==='t')t=Number(v);if(k==='v1')v1.push(v)}
  return {t,v1};
}
export function verifyStripeWebhook({rawBody,signatureHeader,endpointSecret,nowSeconds=Math.floor(Date.now()/1000),toleranceSeconds=300}){
  if(!String(endpointSecret||'').startsWith('whsec_'))throw new Error('stripe_webhook_secret_missing');
  const {t,v1}=parseSignature(signatureHeader);if(!Number.isFinite(t)||v1.length<1)throw new Error('stripe_signature_invalid');
  if(Math.abs(nowSeconds-t)>toleranceSeconds)throw new Error('stripe_signature_timestamp_outside_tolerance');
  const expected=crypto.createHmac('sha256',endpointSecret).update(`${t}.${rawBody}`).digest('hex');
  const a=Buffer.from(expected,'hex');
  const ok=v1.some(s=>{try{const b=Buffer.from(s,'hex');return a.length===b.length&&crypto.timingSafeEqual(a,b)}catch{return false}});
  if(!ok)throw new Error('stripe_signature_mismatch');
  return JSON.parse(rawBody);
}

export function normalizeStripeSettlement(event){
  const type=String(event?.type||'');const session=event?.data?.object||{};
  const paid = (type==='checkout.session.completed' && session.payment_status==='paid') || type==='checkout.session.async_payment_succeeded';
  const reversed = type==='charge.refunded' || type==='charge.dispute.created';
  if(!paid&&!reversed)return {action:'IGNORE',eventType:type};
  return {
    action:paid?'SETTLEMENT_PAID':'SETTLEMENT_REVERSED',
    eventType:type,
    provider:'stripe',
    sessionId:session.id||null,
    paymentStatus:session.payment_status||null,
    currency:session.currency||null,
    amountTotal:Number.isFinite(Number(session.amount_total))?Number(session.amount_total):null,
    livemode:Boolean(event?.livemode),
    customerPiiPersisted:false
  };
}
