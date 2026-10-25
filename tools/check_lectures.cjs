const fs=require('fs');const {chromium}=require('C:/Users/Celes/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 fs.mkdirSync('tmp/lecture-qa',{recursive:true});
 const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});const results=[];
 for(const width of [1440,390]){
  const page=await b.newPage({viewport:{width,height:1000}});
  for(let n=1;n<=4;n++){
   const errors=[],failed=[];const onerror=e=>errors.push(e.message);const onfailed=r=>failed.push(r.url());page.on('pageerror',onerror);page.on('requestfailed',onfailed);
   await page.goto(`file:///E:/prj/random_/lecture/lecture${n}/index.html`);await page.evaluate(()=>document.fonts.ready);
   const info=await page.evaluate(()=>({...tutorialStatus(),ids:[...document.querySelectorAll('[id]')].map(x=>x.id),width:document.documentElement.scrollWidth,mathErrorDetails:[...document.querySelectorAll('.katex-error')].map(x=>x.title),raw:[...document.querySelectorAll('p')].filter(x=>!x.closest('.katex')&&/\\\[|\\\(/.test(x.textContent)).map(x=>x.textContent)}));
   if(new Set(info.ids).size!==info.ids.length)errors.push('duplicate ids');
   if(info.width>width+1)errors.push('horizontal page overflow');if(info.mathErrors||info.raw.length)errors.push('math render');
   const answers=info.correctAnswers;
   for(let i=0;i<answers.length;i++)await page.locator('.quiz-card').nth(i).locator(`button[data-answer="${answers[i]}"]`).evaluate(x=>x.click());
   const score=await page.locator('#quiz-score').innerText();if(!score.includes(`答对 ${answers.length} 题`))errors.push('score');
   await page.locator('#quiz-reset').evaluate(x=>x.click());await page.locator('.quiz-card').first().locator(`button[data-answer="${(answers[0]+1)%3}"]`).evaluate(x=>x.click());
   if(await page.locator('.quiz-explanation.wrong').count()!==1)errors.push('wrong feedback');await page.locator('#quiz-reset').evaluate(x=>x.click());
   await page.locator('#search').fill(n===4?'5.3.4':'条件');await page.locator('#search-button').evaluate(x=>x.click());const search=await page.locator('#search-status').innerText();if(!search.includes('/'))errors.push('search');
   const print=await page.evaluate(()=>{let d=[...document.querySelectorAll('details')],old=d.map(x=>x.open);dispatchEvent(new Event('beforeprint'));const ok=d.every(x=>x.open);dispatchEvent(new Event('afterprint'));return ok&&d.every((x,i)=>x.open===old[i]);});if(!print)errors.push('print restoration');
   if(n===1){await page.goto(`file:///E:/prj/random_/lecture/lecture1/index.html#moments`);await page.evaluate(()=>document.fonts.ready);const detail=page.locator('details');await detail.evaluate(x=>x.open=false);const id=await detail.evaluate(x=>{x.id='linked-detail-check';return x.id});await page.evaluate(id=>location.hash=id,id);await page.waitForTimeout(100);if(!await detail.evaluate(x=>x.open))errors.push('linked details');}
   if(n===2){await page.locator('#amplitude').fill('1');await page.locator('#observe').fill('3.14');if(!(await page.locator('#path-result').innerText()).includes('-1.000'))errors.push('amplitude demo negative');await page.locator('#amplitude').fill('0');if(!(await page.locator('#path-result').innerText()).includes('0.000'))errors.push('amplitude zero');}
   if(n===3){await page.locator('#count-time').fill('0');if(!(await page.locator('#count-result').innerText()).includes('1.0000'))errors.push('count zero');await page.locator('#count-rate').fill('4');await page.locator('#count-time').fill('4');if(!(await page.locator('#count-result').innerText()).includes('16.00'))errors.push('count upper');}
   if(n===4){for(let k=0;k<3;k++){await page.locator('#period-choice').selectOption(String(k));if(!(await page.locator('#period-result').innerText()).includes(`周期${[1,3,2][k]}`))errors.push('period choice '+k);}}
   const shot=n===1?'#ex-1-2-3':n===2?'#path-svg':n===3?'#count-svg':'#ex-5-3-4';await page.locator(shot).scrollIntoViewIfNeeded();await page.screenshot({path:`tmp/lecture-qa/lecture${n}-${width}.png`});
   results.push({lecture:n,viewport:width,examples:info.examples,questions:info.questions,formulas:info.formulas,demos:info.demos,score,print,errors,failed,mathErrorDetails:info.mathErrorDetails});page.off('pageerror',onerror);page.off('requestfailed',onfailed);
  }
  await page.goto('file:///E:/prj/random_/lecture/index.html');if(await page.locator('.chapters article').count()!==4)throw Error('index cards');if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('index overflow');await page.screenshot({path:`tmp/lecture-qa/index-${width}.png`});await page.close();
 }
 await b.close();fs.writeFileSync('lecture/验证报告.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));if(results.some(r=>r.errors.length||r.failed.length))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
