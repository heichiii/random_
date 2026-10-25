"""Build the four offline exam tutorials from authored, slide-checked content."""
from pathlib import Path
import json, html, re
from build_tutorial import prose, table
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'lecture'
def block(key,title,pages,text):return (key,title,pages,text)
def problem(key,label,pages,title,question,entry,solution,check):
    return (key,label,pages,title,question,entry,solution,check)
def sec(x):
    key,title,pages,text=x
    return f'<section class="lesson" id="{key}"><div class="section-num">PPT 第{pages}页</div><h2>{title}</h2>{prose(text)}</section>'
def ex(x):
    key,label,pages,title,q,entry,solution,check=x
    return f'<article class="example" id="{key}"><div class="example-kicker">{label} · PPT 第{pages}页</div><h3>{title}</h3><div class="problem">{prose(q)}</div><p class="entry"><b>从这里入手：</b>{entry}</p>{prose(solution)}<p class="check"><b>检查与迁移：</b>{check}</p></article>'
def build(n,title,lead,route,sections,examples,questions,quick,coverage,corrections):
    dest=OUT/f'lecture{n}';dest.mkdir(parents=True,exist_ok=True)
    nav=''.join(f'<a href="#{key}">{title}</a>' for key,title,_,_ in sections)
    links=(f'<a href="../lecture{n-1}/index.html">← Lecture {n-1}</a>' if n>1 else '<a href="../index.html">← 复习总目录</a>')+' · '+(f'<a href="../lecture{n+1}/index.html">Lecture {n+1} →</a>' if n<4 else '<a href="../index.html">复习总目录 →</a>')
    out=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="按课件范围编写的随机过程考试重点教程，讲解概念联系、原题推导与做题方法，可离线阅读。"><title>Lecture {n} · {title}</title><link rel="stylesheet" href="../../chapter2/assets/katex/katex.min.css"><link rel="stylesheet" href="../../chapter2/style.css"><link rel="stylesheet" href="../../shared.css"><link rel="stylesheet" href="../lecture.css"><script defer src="../../chapter2/assets/katex/katex.min.js"></script><script defer src="../../chapter2/assets/katex/contrib/auto-render.min.js"></script><script defer src="app.js"></script></head><body><div id="reading-progress" aria-hidden="true"></div><aside class="sidebar"><a class="brand" href="../index.html">∿ 随机过程 · 课件重点</a><p class="side-label">LECTURE 0{n} / {title}</p><nav aria-label="讲义目录"><a href="#start">复习路线</a>{nav}<a href="#examples">PPT 原题讲解</a><a href="#review">检验理解</a><a href="#quick">考前速查</a><a href="#coverage">课件覆盖与校正</a></nav><div class="side-bottom"><label for="search">查知识点或原PPT题号</label><input id="search" type="search" placeholder="例如：条件 / 5.3.4"><button id="search-button">查找</button><p id="search-status" role="status"></p><button id="print">打印 / 保存为 PDF</button><p>{links}</p></div></aside><main><header class="hero" id="start"><div class="eyebrow">PPT 考试重点 · LECTURE 0{n}</div><h1>{title}</h1><p class="lead">{lead}</p><div class="hero-meta"><span>按课件范围</span><span>原题保留题号</span><span>离线可用</span></div><a class="primary" href="#{sections[0][0]}">开始复习 →</a></header><section class="intro"><h2>这份课件怎样学才连贯</h2>{prose(route)}<div class="note">先理解正文的小例子，再自己试做原题。关键定义、条件与推导默认可见，速查放在最后。页码用于定位课件，学习本页不需要同时打开PPT。这里的“重点”指课件已纳入的范围，不预测具体试题或分值。</div></section>'''
    out+=''.join(sec(x) for x in sections)
    out+='<section class="examples" id="examples"><h2>按原题号跟做</h2><div class="example-index">'+''.join(f'<a href="#{x[0]}">{x[1]} · {x[3]}</a>' for x in examples)+'</div>'+''.join(ex(x) for x in examples)+'</section>'
    out+='<section class="lesson" id="review"><h2>合上公式，检查自己会不会用</h2><div id="quiz"></div><p id="quiz-score" role="status"></p><button id="quiz-reset">清空答案，重新自测</button></section>'
    out+='<section class="lesson formula-sheet" id="quick"><h2>考前速查：看到条件，选对入口</h2>'+prose(quick)+'</section>'
    out+='<section class="lesson sources" id="coverage"><h2>覆盖到哪些PPT页面</h2>'+table(['课件页面','内容','教程入口'],[[pages,topic,f'<a href="#{anchor}">定位讲解</a>'] for pages,topic,anchor in coverage])+prose(corrections)+'</section>'
    out+=f'<footer><p class="footer-line">{links}</p><p><a href="../index.html">四份PPT复习目录</a> · <a href="../../index.html">教材版完整教程</a></p></footer></main></body></html>'
    (dest/'index.html').write_text(out,encoding='utf-8')
    common=(ROOT/'chapter2/app.js').read_text(encoding='utf-8');common=common[common.index('let answers={};'):]
    prefix="'use strict';\nconst $=s=>document.querySelector(s);const $$=s=>Array.from(document.querySelectorAll(s));\nrenderMathInElement(document.body,{delimiters:[{left:'\\\\[',right:'\\\\]',display:true},{left:'\\\\(',right:'\\\\)',display:false}],throwOnError:false,strict:false});\n"
    qs=[dict(q=f'{i+1}. '+q,a=a,c=c,e=e,link=link) for i,(q,a,c,e,link) in enumerate(questions)]
    (dest/'app.js').write_text(prefix+'const questions='+json.dumps(qs,ensure_ascii=False)+';\n'+common,encoding='utf-8')
    meta={'lecture':n,'title':title,'sections':[{'id':k,'title':t,'slides':p} for k,t,p,_ in sections],'examples':[{'id':x[0],'label':x[1],'slides':x[2]} for x in examples],'questions':len(qs),'coverage':[{'slides':p,'topic':t,'anchor':a} for p,t,a in coverage]}
    (dest/'coverage.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    (dest/'阅读说明.md').write_text(f'# Lecture {n}：{title}\n\n用浏览器打开本目录的[index.html](index.html)，或从[四讲目录](../index.html)进入。内容以第{n}份PPT为准，原题号与页码保留，全部条件和关键推导写在正文。\n\n{len(sections)}个学习环节，{len(examples)}组原题讲解，{len(qs)}道带理由自测。课件中的场景举例也在正文或分类表中解释。页码和分布表不代替讲解。最后提供速查与逐段覆盖表。\n\n请保留整套项目目录，本页共用根目录chapter2的本地KaTeX资源与样式。阅读无需联网、服务器或Python。正文源在tools/lecture{n}_content.py，由build_lectures.py生成。\n',encoding='utf-8')
    return meta

def index(metas):
    OUT.mkdir(exist_ok=True)
    css=(ROOT/'index.html').read_text(encoding='utf-8');style=re.search(r'<style>(.*?)</style>',css,re.S).group(1)
    descriptions=['先会描述事件和随机变量，再用分布、均值方差、特征函数与条件期望完成计算。','从一条样本路径走到多时刻联合分布、数字特征、复过程、Gaussian、Wiener和平稳。','把计数、间隔、到达时刻和给定总数后的均匀点串起来，再处理随机总量。','从一步矩阵与路径开始，经过状态分类，最终求平稳分布和长期概率。']
    cards=''.join(f'<article><small>LECTURE 0{m["lecture"]}</small><h2>{m["title"]}</h2><p>{descriptions[i]}</p><div class="meta">{len(m["sections"])}个学习环节 · {len(m["examples"])}组原题 · {m["questions"]}道自测</div><a class="button" href="lecture{m["lecture"]}/index.html">进入 Lecture {m["lecture"]} →</a></article>' for i,m in enumerate(metas))
    out=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>随机过程 · 四份PPT考试重点</title><style>{style}</style></head><body><main><div class="brand">∿ 随机过程 · 课件重点</div><div class="eyebrow">按四份PPT复习</div><h1>把考试范围，<br><em>学成一条清楚的线。</em></h1><p class="lead">先讲为什么要用这个知识，再把公式和原题算明白。保留必要解释，减少教材中课件未展开的旁枝。</p><div class="promise">这是一套单独组织的PPT教程。Lecture 1—4依次对应四份原文件，保留原题号和页码。核心讲解与题意都在页面内，不要求再看教材。原PPT不改动。</div><div class="chapters">{cards}</div><section class="how"><h2>时间有限时的读法</h2><p>按1→2→3→4学习，每讲先读开头路线与小例子，再跟做原题，最后用自测找出薄弱处。复习第二遍可从“考前速查”找方法，再回到对应推导。页码覆盖表帮助你与老师课件核对。</p><p>本套按用户指定的课件范围制作。课件中的标注和例题完整保留；没有依据的“必考题”或分值预测不加入。未进入课件主体的均方随机分析、Itô、谱分析、连续时间链不扩写到这里。</p><p><a href="../index.html">教材版完整教程 →</a> · <a href="阅读说明.md">范围与文件说明</a></p></section><footer>本地离线学习 · 公式与字体使用项目已打包的KaTeX资源</footer></main></body></html>'''
    (OUT/'index.html').write_text(out,encoding='utf-8')
    (OUT/'manifest.json').write_text(json.dumps(metas,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    from lecture1_content import write as l1
    from lecture2_content import write as l2
    from lecture3_content import write as l3
    from lecture4_content import write as l4
    index([l1(),l2(),l3(),l4()])
