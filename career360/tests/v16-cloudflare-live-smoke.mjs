import { chromium } from 'playwright';

const base = process.env.CAREER360_PREVIEW_URL;
if (!base) throw new Error('CAREER360_PREVIEW_URL_REQUIRED');
const assert=(ok,msg)=>{if(!ok)throw new Error(msg)};
const expectedPins=[
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
  console.log('CLOUDFLARE_V16_BROWSER_PRELOGIN=PASS');
  console.log('CLOUDFLARE_V16_RESPONSIVE=PASS');
  console.log('CLOUDFLARE_V16_RUNTIME_ERRORS=ZERO');
  console.log('CLOUDFLARE_V16_PRODUCTION_MUTATION=NONE');
} finally { await browser.close(); }
