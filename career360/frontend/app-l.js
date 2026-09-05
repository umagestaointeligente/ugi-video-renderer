const {sb,$}=window.C;
const U={state:null,loading:false};

function css(){
  if($('careerV15Scale'))return;
  const s=document.createElement('style');
  s.id='careerV15Scale';
  s.textContent=`
:root{--career-max:1180px;--career-gap:clamp(10px,1.5vw,18px);--career-pad:clamp(12px,2vw,24px);--career-radius:clamp(15px,1.8vw,24px);--career-title:clamp(22px,2.3vw,32px);--career-body:clamp(13px,1.1vw,15px)}
*{box-sizing:border-box}html,body{max-width:100%;overflow-x:hidden}body{min-width:320px}.w{width:min(var(--career-max),100%);margin:0 auto;padding-inline:clamp(10px,2vw,22px)}
#app,#main,.v,.stack{min-width:0}.card{border-radius:var(--career-radius);padding:var(--career-pad)}
.btn,.tinybtn,button,input,select,textarea{font-size:max(16px,1em)}.btn,.tinybtn,.tabs button,.more-nav>summary{min-height:44px;touch-action:manipulation}
.top{gap:12px}.tabs{display:flex;gap:8px;align-items:center;max-width:100%;scrollbar-width:none}.tabs::-webkit-scrollbar{display:none}
.my-page,.showcase-page,.professional-v8,.radarbox,.proactive-card{min-width:0}.my-main,.showcase-body{min-width:0}
.my-name h1,.showcase-name h1{font-size:var(--career-title);overflow-wrap:anywhere}.my-headline,.showcase-headline{font-size:clamp(13px,1.3vw,16px)}
.my-about,.showcase-card p{font-size:var(--career-body)}
.my-avatar img,.showcase-avatar img,.photo-shell img{object-fit:cover;object-position:50% 28%;max-width:100%}
.showcase-shell{width:min(920px,100%);margin-inline:auto}.showcase-grid{grid-template-columns:minmax(0,1.5fr) minmax(240px,.75fr)}
.showcase-card,.my-highlight,.profile-v11-box,.proactive-summary,.radar-mini>div{min-width:0;overflow-wrap:anywhere}
.showcase-highlights{grid-template-columns:repeat(2,minmax(0,1fr))}.showcase-skills,.my-skills{max-width:100%}.showcase-skill,.my-skill{max-width:100%;white-space:normal;text-align:left}
.photo-studio-panel{width:min(820px,100%);padding:clamp(16px,2.4vw,24px)}.photo-compare{grid-template-columns:repeat(2,minmax(0,1fr))}.photo-frame{min-width:0}.photo-frame img,.photo-frame canvas{max-width:100%;height:auto;aspect-ratio:4/5;object-fit:cover}
.showcase-drawer-panel{width:min(760px,100%)}
.proactive-grid{grid-template-columns:repeat(4,minmax(0,1fr))}.radar-mini{grid-template-columns:repeat(3,minmax(0,1fr))}
.career-ui-ready .old-home-hidden{display:none!important}
@media(max-width:980px){.showcase-grid{grid-template-columns:1fr}.showcase-side-stack{grid-template-columns:repeat(2,minmax(0,1fr))}.showcase-leadership{grid-column:1/-1}.proactive-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:768px){
  :root{--career-pad:15px;--career-radius:18px}
  body{padding-bottom:calc(78px + env(safe-area-inset-bottom,0px))}.w{padding-inline:10px}
  .top{padding-top:max(8px,env(safe-area-inset-top,0px))}.top .brand{font-size:18px}.top #role{display:none}
  .tabs{position:fixed;left:0;right:0;bottom:0;z-index:70;background:rgba(255,255,255,.96);backdrop-filter:blur(16px);border-top:1px solid #e8e8ef;padding:7px max(7px,env(safe-area-inset-right,0px)) calc(7px + env(safe-area-inset-bottom,0px)) max(7px,env(safe-area-inset-left,0px));display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:4px;box-shadow:0 -10px 30px rgba(20,18,40,.08);overflow:visible}
  .tabs>.btn,.tabs>.more-nav>summary{min-width:0!important;width:100%;min-height:54px!important;padding:6px 3px!important;border-radius:13px!important;display:flex!important;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:10.5px!important;line-height:1.08;text-align:center;white-space:normal!important;background:transparent!important;box-shadow:none!important;color:#667085!important}
  .tabs>.btn.on{background:#f2efff!important;color:#5639df!important}.tabs>.btn[data-v="career"],.tabs>.btn[data-v="support"],.tabs>#masterTab{display:none!important}
  .more-nav{position:static}.more-nav>summary{list-style:none}.more-pop{position:fixed!important;left:10px!important;right:10px!important;bottom:calc(76px + env(safe-area-inset-bottom,0px))!important;top:auto!important;min-width:0!important;border-radius:18px!important;box-shadow:0 15px 55px rgba(20,18,40,.2)!important}
  .showcase-cover{height:112px}.showcase-body{padding:0 15px 17px}.showcase-identity{grid-template-columns:auto minmax(0,1fr);gap:12px;margin-top:-41px}.showcase-avatar{width:84px;height:84px;border-radius:22px}.showcase-privacy{grid-column:1/-1;max-width:100%;white-space:normal}
  .showcase-actions{grid-template-columns:1fr 1fr;gap:7px}.showcase-actions .btn{width:100%}.showcase-side-stack{grid-template-columns:1fr}.showcase-highlights{grid-template-columns:1fr}
  .my-identity{gap:12px}.my-avatar{width:76px;height:76px}.my-actions{display:grid!important;grid-template-columns:1fr 1fr;gap:7px}.my-actions .btn{width:100%}
  .photo-studio-modal{padding:0!important;align-items:flex-end}.photo-studio-panel{max-height:92dvh!important;border-radius:24px 24px 0 0!important;padding-bottom:calc(18px + env(safe-area-inset-bottom,0px))}.photo-style-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.photo-compare{grid-template-columns:1fr}.photo-studio-actions{display:grid;grid-template-columns:1fr 1fr}.photo-studio-actions .btn{width:100%}
  .proactive-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.radar-mini{gap:6px}.radar-mini>div{padding:10px}.radar-mini strong{font-size:19px}
  .showcase-drawer{padding:0}.showcase-drawer-panel{border-radius:24px 24px 0 0;max-height:92dvh;padding-bottom:calc(18px + env(safe-area-inset-bottom,0px))}
}
@media(max-width:430px){
  .w{padding-inline:8px}.card{padding:14px}.showcase-cover{height:104px}.showcase-avatar{width:80px;height:80px}.showcase-name h1{font-size:22px}.showcase-headline{font-size:13px}.showcase-actions{grid-template-columns:1fr}.showcase-actions .btn:first-child{grid-column:auto}.my-actions{grid-template-columns:1fr}.radar-actions,.proactive-actions{display:grid!important;grid-template-columns:1fr}.radar-actions .btn,.proactive-actions .btn{width:100%}.photo-studio-actions{grid-template-columns:1fr}.photo-style-grid{grid-template-columns:1fr 1fr}.proactive-grid{gap:6px}.proactive-metric{padding:9px}.showcase-card{padding:15px}.showcase-timeline{padding-left:18px}}
@media(max-width:370px){.tabs>.btn,.tabs>.more-nav>summary{font-size:9.5px!important}.showcase-avatar{width:74px;height:74px}.photo-style-grid{grid-template-columns:1fr}.radar-mini strong{font-size:17px}}
@media(min-width:1180px){.showcase-shell{width:min(980px,100%)}.showcase-cover{height:184px}.showcase-avatar{width:124px;height:124px}.showcase-grid{gap:20px}}
`;
  document.head.appendChild(s);
}

async function getState(){
  if(U.loading)return U.state;
  U.loading=true;
  try{
    const {data,error}=await sb.functions.invoke('career-ui-state',{body:{}});
    if(error)throw error;
    U.state=data||null;
    applyState();
    return U.state;
  }catch{return null}finally{U.loading=false}
}

function setNavLabel(el,key,html,title){
  if(!el||el.dataset.v15Nav===key)return;
  el.innerHTML=html;
  el.dataset.v15Nav=key;
  if(title)el.title=title;
}

function setNavLabels(){
  const home=document.querySelector('.tabs [data-v="home"]');
  const profile=$('showcaseTab');
  const opp=document.querySelector('.tabs [data-v="opps"]');
  const agent=document.querySelector('.tabs [data-v="agent"]');
  const more=$('moreNav')?.querySelector('summary');
  setNavLabel(home,'home','<span aria-hidden="true">⌂</span><span>Minha Página</span>','Minha Página');
  setNavLabel(profile,'profile','<span aria-hidden="true">◉</span><span>Meu Perfil</span>','Meu Perfil');
  setNavLabel(opp,'opps','<span aria-hidden="true">⌕</span><span>Oportunidades</span>','Oportunidades');
  if(agent&&agent.dataset.v15Nav!=='agent'){
    const badge=agent.querySelector('.agent-badge');
    agent.innerHTML='<span aria-hidden="true">✦</span><span>Meu Agente</span>';
    if(badge)agent.appendChild(badge);
    agent.dataset.v15Nav='agent';
    agent.title='Meu Agente';
  }
  setNavLabel(more,'more','<span aria-hidden="true">•••</span><span>Mais</span>');
}

function applyState(){
  document.documentElement.classList.add('career-ui-ready');
  document.documentElement.dataset.careerUi='v15';
  const caps=U.state?.capabilities||null;
  document.documentElement.dataset.photoAi=!caps?'unknown':caps.photo_studio_external_ai?'external':'local';
  document.documentElement.dataset.mailDelivery=!caps?'unknown':caps.mail_delivery?'on':'off';
  setNavLabels();
  const provider=document.querySelector('.photo-provider');
  const providerText='⚡ Ajuste profissional no aparelho';
  if(provider&&caps?.photo_studio_external_ai===false&&provider.textContent!==providerText)provider.textContent=providerText;
}

function watch(){
  const root=$('app')||document.body;
  let t;
  new MutationObserver(()=>{clearTimeout(t);t=setTimeout(applyState,120)}).observe(root,{childList:true,subtree:true});
  if('ResizeObserver'in window){
    new ResizeObserver(()=>{
      const value=`${window.innerWidth}px`;
      if(document.documentElement.style.getPropertyValue('--career-vw')!==value)document.documentElement.style.setProperty('--career-vw',value);
    }).observe(document.documentElement);
  }
}

css();watch();
sb.auth.onAuthStateChange((_,s)=>{if(s)setTimeout(getState,450)});
const se=(await sb.auth.getSession()).data.session;if(se)await getState();
setInterval(()=>{if(!$('app')?.classList.contains('hide'))getState()},120000);