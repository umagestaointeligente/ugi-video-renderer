import { chromium } from 'playwright';

const base = process.env.CAREER360_PREVIEW_URL;
if (!base) throw new Error('CAREER360_PREVIEW_URL_REQUIRED');
const assert=(ok,msg)=>{if(!ok)throw new Error(msg)};
const appIPin='90a795bf1a371be66fd8f907c8a76501f8a5421c';
const expectedPins=[
  appIPin,
  '6df7b4e63d7e52ce3c3f02247392b98f0393cbe8',
  '4283646143425e4a3156e44100aabb475df88d27',
  '719c15ebfe89d212a19473b70ea6e615174601d9'
];
const truthful='Você confirma o que importa. O Career 360 organiza sua busca.';

const browser=await chromium.launch({headless:true});
try {
  for (const width of [360,412,768,1180]) {
    const page=await browser.newPage({viewport:{width,height:900}});
    const pageErrors=[]; const consoleErrors=[]; const failed=[];
    page.on('pageerror',e=>pageErrors.push(String(e)));
    page.on('console',m=>{if(m.type()==='error') consoleErrors.push(m.text())});
    page.on('requestfailed',r=>failed.push(`${r.method()} ${r.url()} ${r.failure()?.errorText||''}`));
    const resp=await page.goto(base+'/',{waitUntil:'networkidle',timeout:45000});
    assert(resp && resp.status()===200,`root_http_${width}_${resp?.status()}`);
    await page.waitForTimeout(800);
    const state=await page.evaluate(()=>({
      title:document.title,
      lang:document.documentElement.lang,
      dataset:document.documentElement.dataset.careerUiClarity||'',
      scrollWidth:document.documentElement.scrollWidth,
      authVisible:getComputedStyle(document.getElementById('auth')).display!=='none',
      appHidden:document.getElementById('app').classList.contains('hide'),
      authCopy:document.querySelector('#auth > p.muted')?.textContent?.trim()||'',
      authTitle:document.getElementById('authTitle')?.textContent?.trim()||'',
      loginText:document.getElementById('loginMode')?.textContent?.trim()||'',
      signupText:document.getElementById('signupMode')?.textContent?.trim()||'',
      authGoHeight:document.getElementById('authGo')?.getBoundingClientRect().height||0,
      scripts:[...document.scripts].map(s=>s.src).filter(Boolean),
      styleInstalled:!!document.getElementById('careerV16Clarity')
    }));
    assert(state.title==='LSI Career 360',`title_${width}`);
    assert(state.lang==='pt-BR',`lang_${width}`);
    assert(state.authVisible,`auth_not_visible_${width}`);
    assert(state.appHidden,`app_should_be_hidden_prelogin_${width}`);
    assert(state.authCopy===truthful,`truthful_copy_${width}`);
    assert(state.authTitle==='Entrar na minha conta',`auth_title_${width}`);
    assert(state.loginText==='Entrar'&&state.signupText==='Criar minha conta',`auth_modes_${width}`);
    assert(state.authGoHeight>=44,`auth_touch_${width}_${state.authGoHeight}`);
    assert(state.scrollWidth<=width+1,`overflow_${width}_${state.scrollWidth}`);
    assert(state.dataset==='v16',`v16_dataset_${width}_${state.dataset}`);
    assert(state.styleInstalled,`v16_style_${width}`);
    for (const pin of expectedPins) assert(state.scripts.some(s=>s.includes('@'+pin+'/career360/frontend/')),`missing_pin_${pin}_${width}`);
    assert(pageErrors.length===0,`page_errors_${width}_${pageErrors.join('|')}`);
    assert(consoleErrors.length===0,`console_errors_${width}_${consoleErrors.join('|')}`);
    assert(failed.length===0,`request_failed_${width}_${failed.join('|')}`);

    await page.click('#signupMode');
    await page.waitForTimeout(100);
    const signup=await page.evaluate(()=>({
      title:document.getElementById('authTitle')?.textContent?.trim(),
      go:document.getElementById('authGo')?.textContent?.trim(),
      visible:!document.getElementById('signupBox').classList.contains('hide'),
      pwd2H:document.getElementById('password2')?.getBoundingClientRect().height||0
    }));
    assert(signup.title==='Criar minha conta'&&signup.go==='Criar minha conta'&&signup.visible,`signup_toggle_${width}`);
    assert(signup.pwd2H>=44,`signup_touch_${width}_${signup.pwd2H}`);
    await page.click('#loginMode');
    await page.waitForTimeout(80);
    const back=await page.evaluate(()=>({title:document.getElementById('authTitle')?.textContent?.trim(),hidden:document.getElementById('signupBox').classList.contains('hide')}));
    assert(back.title==='Entrar na minha conta'&&back.hidden,`login_toggle_${width}`);
    console.log(`CLOUDFLARE_BROWSER_${width}=PASS`);
    await page.close();
  }

  const ui=await browser.newPage({viewport:{width:412,height:900}});
  const uiErrors=[];
  ui.on('pageerror',e=>uiErrors.push(String(e)));
  await ui.setContent('<!doctype html><html><body><button data-v="agent">Meu Agente</button><div id="app"><div id="home"></div></div></body></html>');
  await ui.evaluate(()=>{
    let confirmed=false;
    window.__applicationConfirmationCalls=[];
    window.confirm=()=>true;
    const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const status=()=>({
      status:'PROACTIVE_AGENT_READY',
      preference:{cadence_hours:12},
      latest_digest:null,
      notifications:[],
      unread_count:0,
      application_counts:{draft_ready:confirmed?0:1,awaiting_user:confirmed?1:0},
      confirmable_applications:[{
        id:'11111111-1111-4111-8111-111111111111',
        status:confirmed?'awaiting_user':'draft_ready',
        submission_confirmed:confirmed,
        submission_dispatch_state:'idle',
        title:'Gerente Comercial',
        employer_name:'Empresa Teste',
        source_name:'Quickin',
        global_submit_permission:false,
        dispatch_eligible:false
      }],
      application_permissions:{allow_application_submit:false,require_confirmation_for_identity_disclosure:true},
      pending_mail_actions:[],critical_count:0,action_required_count:0
    });
    window.C={
      $:id=>document.getElementById(id),
      esc,
      sb:{
        auth:{
          getSession:async()=>({data:{session:{access_token:'synthetic'}}}),
          onAuthStateChange:()=>({data:{subscription:{unsubscribe(){}}}})
        },
        functions:{invoke:async(name,{body}={})=>{
          if(name==='career-proactive-status')return {data:status(),error:null};
          if(name==='career-application-confirm'){
            window.__applicationConfirmationCalls.push({name,body});
            confirmed=Boolean(body?.confirmed);
            return {data:{status:confirmed?'APPLICATION_CONFIRMED':'APPLICATION_CONFIRMATION_REVOKED',global_submit_permission:false,provider_side_effect:false},error:null};
          }
          return {data:{},error:null};
        }}
      }
    };
  });
  await ui.addScriptTag({type:'module',url:`https://cdn.jsdelivr.net/gh/umagestaointeligente/ugi-video-renderer@${appIPin}/career360/frontend/app-i.js`});
  await ui.waitForSelector('.app-confirm', {timeout:15000});
  const before=await ui.evaluate(()=>({
    title:document.querySelector('.app-confirm-title')?.textContent?.trim(),
    button:document.querySelector('.app-confirm')?.textContent?.trim(),
    state:document.querySelector('.app-confirm-state')?.textContent?.trim()
  }));
  assert(before.title==='Gerente Comercial',`confirm_ui_title_${before.title}`);
  assert(before.button==='Confirmar candidatura',`confirm_ui_button_${before.button}`);
  assert(before.state.includes('Nenhuma tentativa de envio'),`confirm_ui_truth_before_${before.state}`);
  await ui.click('.app-confirm');
  await ui.waitForSelector('.app-revoke',{timeout:10000});
  const afterConfirm=await ui.evaluate(()=>({
    button:document.querySelector('.app-revoke')?.textContent?.trim(),
    state:document.querySelector('.app-confirm-state')?.textContent?.trim(),
    message:document.querySelector('.app-confirm-message')?.textContent?.trim(),
    calls:window.__applicationConfirmationCalls
  }));
  assert(afterConfirm.button==='Revogar confirmação',`revoke_button_${afterConfirm.button}`);
  assert(afterConfirm.state.includes('nada foi enviado'),`confirm_ui_no_false_send_${afterConfirm.state}`);
  assert(afterConfirm.message.includes('nada foi enviado'),`confirm_ui_message_truth_${afterConfirm.message}`);
  assert(afterConfirm.calls.length===1&&afterConfirm.calls[0].body.confirmed===true,`confirm_call_contract_${JSON.stringify(afterConfirm.calls)}`);
  await ui.click('.app-revoke');
  await ui.waitForSelector('.app-confirm',{timeout:10000});
  const afterRevoke=await ui.evaluate(()=>({button:document.querySelector('.app-confirm')?.textContent?.trim(),calls:window.__applicationConfirmationCalls}));
  assert(afterRevoke.button==='Confirmar candidatura',`confirm_button_restored_${afterRevoke.button}`);
  assert(afterRevoke.calls.length===2&&afterRevoke.calls[1].body.confirmed===false,`revoke_call_contract_${JSON.stringify(afterRevoke.calls)}`);
  assert(uiErrors.length===0,`application_confirmation_ui_errors_${uiErrors.join('|')}`);
  await ui.close();
  console.log('CLOUDFLARE_APPLICATION_CONFIRMATION_UI=PASS');
  console.log('CLOUDFLARE_APPLICATION_CONFIRMATION_TRUTHFUL_NO_FALSE_SEND=PASS');
  console.log('CLOUDFLARE_V16_BROWSER_PRELOGIN=PASS');
  console.log('CLOUDFLARE_V16_RESPONSIVE=PASS');
  console.log('CLOUDFLARE_V16_RUNTIME_ERRORS=ZERO');
  console.log('CLOUDFLARE_V16_PRODUCTION_MUTATION=NONE');
} finally { await browser.close(); }
