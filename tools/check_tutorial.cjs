const fs=require('fs');const path=require('path');
const {chromium}=require('C:/Users/Celes/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const report=[];
 for(const width of [1440,390]){
  const page=await browser.newPage({viewport:{width,height:1000}});
  for(let ch=1;ch<=5;ch++){
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(`file:///E:/prj/random_/chapter${ch}/index.html`);await page.evaluate(()=>document.fonts.ready);
   const status=await page.evaluate(()=>tutorialStatus());
   const details=await page.evaluate(()=>({width:document.documentElement.scrollWidth,viewport:innerWidth,errors:[...document.querySelectorAll('.katex-error')].map(x=>x.title),raw:[...document.querySelectorAll('p')].filter(x=>!x.closest('.katex')&&/\\\[|\\\(/.test(x.textContent)).slice(0,2).map(x=>x.textContent),ids:[...document.querySelectorAll('[id]')].map(x=>x.id)}));
   if(new Set(details.ids).size!==details.ids.length)errors.push('duplicate ids');
   if(details.width>width+1)errors.push('page overflow');
   if(details.errors.length)errors.push(...details.errors);
   const keys=await page.evaluate(()=>tutorialStatus().correctAnswers);
   for(let i=0;i<keys.length;i++)await page.locator('.quiz-card').nth(i).locator(`button[data-answer="${keys[i]}"]`).evaluate(b=>b.click());
   const score=await page.locator('#quiz-score').innerText();
   if(!score.includes(`答对 ${keys.length} 题`))errors.push('correct answer scoring');
   await page.locator('#quiz-reset').evaluate(b=>b.click());
   await page.locator('.quiz-card').first().locator('button').nth((keys[0]+1)%3).evaluate(b=>b.click());
   const wrong=await page.locator('.quiz-explanation.wrong').count();
   await page.locator('#quiz-reset').evaluate(b=>b.click());
   await page.locator('#search').fill(ch===5?'平稳':'例');await page.locator('#search-button').evaluate(b=>b.click());
   const search=await page.locator('#search-status').innerText();
   const print=await page.evaluate(()=>{const d=[...document.querySelectorAll('details')];const orig=d.map(x=>x.open);dispatchEvent(new Event('beforeprint'));const opened=d.every(x=>x.open);dispatchEvent(new Event('afterprint'));return opened&&d.every((x,i)=>x.open===orig[i]);});
   if(!wrong||!print||!search.includes('/'))errors.push('interaction failure');
   if(ch===4){await page.locator('#spectral-a').fill('4');if(!(await page.locator('#spectral-result').innerText()).includes('8.00'))errors.push('spectrum demo');}
   if(ch===5){await page.locator('#chain-start').selectOption('2');await page.locator('#chain-n').fill('20');if(!(await page.locator('#chain-result').innerText()).includes('0.600000'))errors.push('chain demo');}
   report.push({ch,width,status,score,wrong,print,search,errors,raw:details.raw});
   if(ch>=3&&width===1440){await page.locator('h2').nth(1).scrollIntoViewIfNeeded();await page.screenshot({path:`tmp/ch${ch}-desktop.png`});}
   if(ch>=3&&width===390){await page.locator(ch===4?'#spectral-svg':ch===5?'#chain-svg':'#derivative').scrollIntoViewIfNeeded();await page.screenshot({path:`tmp/ch${ch}-mobile.png`});}
  }
  await page.close();
 }
 await browser.close();fs.writeFileSync('验证报告.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
 if(report.some(r=>r.errors.length))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
