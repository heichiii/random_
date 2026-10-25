from pathlib import Path
import json, re, html

ROOT = Path(__file__).resolve().parents[1]
def prose(s):
    return '\n'.join(x.replace('<','&lt;') if x.startswith('\\[') else x if x.startswith('<') else '<p>'+x+'</p>' for x in s.strip().splitlines() if x.strip())
def section(key,title,s):
    return f'<section id="{key}" class="lesson"><h2>{title}</h2>{prose(s)}</section>'
def example(ch,n,label,title,problem,entry,body,check,method):
    return f'<article id="ex{n}" class="example"><div class="example-kicker">例 {ch}.{n}</div><h3>{title}</h3><div class="problem">{prose(problem)}</div><p class="entry"><b>入口：</b>{entry}</p>{prose(body)}<p class="check"><b>检查：</b>{check}</p><p class="method"><b>带走的方法：</b>{method}</p></article>'
def table(head,rows):
    return '<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+x+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def build(ch,title,lead,route,sections,examples,questions,coverage):
    dest=ROOT/f'chapter{ch}'; dest.mkdir(exist_ok=True)
    nav=''.join(f'<a href="#{k}">{t}</a>' for k,t,_ in sections)
    prev=f'<a href="../chapter{ch-1}/index.html">← 第{ch-1}章</a>'
    nxt=f'<a href="../chapter{ch+1}/index.html">第{ch+1}章 →</a>' if ch<5 else '<a href="../index.html">回到总目录 →</a>'
    out=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第{ch}章 · {title}</title><link rel="stylesheet" href="../chapter2/assets/katex/katex.min.css"><link rel="stylesheet" href="../chapter2/style.css"><link rel="stylesheet" href="../shared.css"><script defer src="../chapter2/assets/katex/katex.min.js"></script><script defer src="../chapter2/assets/katex/contrib/auto-render.min.js"></script><script defer src="app.js"></script></head><body><div id="reading-progress" aria-hidden="true"></div><aside class="sidebar"><a class="brand" href="../index.html">∿ 随机过程 · 理解笔记</a><p class="side-label">CHAPTER 0{ch} / {title}</p><nav aria-label="章节目录"><a href="#start">学习路线</a>{nav}<a href="#examples">全部编号例题</a><a href="#review">理解自测</a><a href="#coverage">覆盖与速查</a></nav><div class="side-bottom"><label for="search">查找知识点或例题</label><input id="search" type="search" placeholder="概念或例题编号"><button id="search-button">查找</button><p id="search-status" role="status"></p><button id="print">打印 / 保存为 PDF</button><p>{prev} · {nxt}</p></div></aside><main><header id="start" class="hero"><div class="eyebrow">随机过程 · 第{ch}站</div><h1>{title}</h1><p class="lead">{lead}</p><div class="hero-meta"><span>{len(sections)} 个相连的学习环节</span><span>{len(examples)} 道完整例题</span><span>离线学习 · 可打印</span></div><a class="primary" href="#{sections[0][0]}">开始理解 →</a></header><section class="intro"><h2>先知道这章为什么这样学</h2>{prose(route)}<div class="note">先读每节的问题、最小例子和结论，再跟做相应例题。核心定义和推导默认展开，补充细节可以稍后读。前置解释均在本套教程内；不需要打开教材。</div></section>'''
    out+=''.join(section(*x) for x in sections)
    out+='<section id="examples" class="examples"><h2>把知识接到题目上</h2><div class="example-index">'+''.join(f'<a href="#ex{i+1}">例 {ch}.{i+1} · {x[0]}</a>' for i,x in enumerate(examples))+'</div>'
    out+=''.join(example(ch,i+1,*x) for i,x in enumerate(examples))+'</section>'
    out+='<section id="review" class="lesson"><h2>能解释理由，才算学会</h2><div id="quiz"></div><p id="quiz-score" role="status"></p><button id="quiz-reset">清空答案，重新自测</button></section>'
    out+=section('coverage','复习速查与覆盖记录',coverage)
    out+=f'<footer><p class="footer-line">{prev}　{nxt}</p><p>知识范围：学习指导本章内容提要与全部编号例题。课后习题全解未逐题改写。编写依据记录见本章阅读说明。</p></footer></main></body></html>'
    (dest/'index.html').write_text(out,encoding='utf-8')
    common=(ROOT/'chapter2/app.js').read_text(encoding='utf-8')
    common=common[common.index('let answers={};'):]
    prefix="'use strict';\nconst $=s=>document.querySelector(s);const $$=s=>Array.from(document.querySelectorAll(s));\nrenderMathInElement(document.body,{delimiters:[{left:'\\\\[',right:'\\\\]',display:true},{left:'\\\\(',right:'\\\\)',display:false}],throwOnError:false,strict:false});\n"
    qs=[dict(q=f'{i+1}. '+q,a=a,c=c,e=e,link=link) for i,(q,a,c,e,link) in enumerate(questions)]
    (dest/'app.js').write_text(prefix+'const questions='+json.dumps(qs,ensure_ascii=False)+';\n'+common,encoding='utf-8')

def bridge_old():
    bridges={1:{
      '概率空间：有哪些结果，哪些问题能问，各有多大概率':'从“抛两次硬币，至少一次正面的概率是多少”出发：要算这个数，先得说清哪些完整结果算成功，再给它们分配概率。概率空间就是把这两步写成一套一致的规则。下面的事件域与公理，都是为避免漏算、重算或问出模型不能回答的问题。',
      '随机变量与分布：给结果打分，再描述分数':'列出完整结果后，我们往往不关心记录本身，而关心人数、等待时间、收入这些数。于是先用随机变量把记录变成数，再用分布汇总每个数出现的概率。两者各做一步：X 规定怎样读数，F 规定这些读数怎样分配概率。',
      '数字特征：用少量数字概括一个分布':'分布能回答所有取值问题，但比较两个方案时，我们常先问“平均多少、波动多大”。这就需要期望和方差。多个随机量一起出现时，还要问它们是否一起偏高或偏低，于是从单个量自然走到协方差。',
      '每一种分布，都从一个明确的问题开始':'已经会算平均与波动，下面才来认识常用的概率模型。它们分别回答“固定次数成功几次”“等到成功要多久”“一段时间发生几次”等不同问题。先根据场景和假设选模型，再推概率与均值方差；不必先背整张公式表。',
      '特征函数：给一个分布换一种编码':'刚才用卷积求独立和，每增加一个变量，求和或积分就更复杂。有没有一种表示，能把“随机量相加”变成“普通函数相乘”？特征函数就是为此引入的。先跟两点分布算一次编码，再看它为什么能还原概率和读取矩。',
      '多维正态：多个量一起服从“钟形规律”':'现在把“独立正态相加仍正态”和“联合分布要描述依赖”接起来：多个正态量一起变化时，只看每个量的钟形还不够。联合正态是一种更强的结构，使均值和协方差就能决定全部分布，第二章的 Gaussian 过程会逐次使用它。',
      '条件期望：知道一条线索后，重新估计平均值':'前面算的是没有额外信息时的平均。若先知道今天是工作日，或已知顾客总数，样本的权重就变了，估计也该跟着变。先按已知线索分组求平均，再把各组拼回去，这条线贯穿条件期望、全期望和全方差。',
      '收敛：你说“越来越接近”，到底是哪一种？':'一次观测不稳定，很多次平均是否可靠？要回答它，先得规定随机量“接近”的意思：是误差平方平均变小，还是大误差越来越少，或是一条完整记录最终稳定？下面先用定义区分这些问题，再用大数定律判断平均值。'
    },2:{
      '随机过程：随机抽到一整条时间曲线':'第一章的一次结果只读出一个数。现在把顾客的整天到达记录当作一次结果，就能在任意时刻读出累计人数。先分清“换一天记录”与“同一天往后看”，才能理解下面的两个输入与样本路径。',
      '别只看每一帧，还要知道帧与帧怎样联系':'知道每天 12 点的人数分布，还不能回答“12 点已经很多，13 点还会很多吗”。这要同时观察两个时刻。先从一维走到二维，再推广到任意有限次观测；有限维分布正是保留时间依赖的完整描述。',
      '均值看中心，协方差看时刻之间的联动':'有限维分布虽完整，实际往往太复杂。沿用第一章“用少量数字摘要”的办法：每一时刻算平均，每一对时刻算联动。于是均值从一个数变成时间函数，协方差从一个数变成二元函数；这些摘要有用，但通常不能替代全部分布。',
      '两段随机故事，怎样算“没有关系”？':'刚才比较的是同一过程的两个时刻。现在同时记录温度 X 和用电量 Y，问题变成：X 的记录能否帮助预测 Y？把两类观测放进同一个联合分布，就得到过程之间的独立；只比较偏差乘积，则得到较弱的不相关。',
      '复过程：把两个实信号装进一个数':'工程里常同时记录两路信号。用 X+iY 把它们写在一起，旋转和振荡会更容易计算。这里先解释这种记法怎样保留两路数据，再说明为何方差和相关要使用共轭。如果你先想掌握到达模型，可完成本节最小例子后进入下一节，遇到复数题再回查展开式。',
      '用特殊结构，让整条过程变得可计算':'前面建立了描述任何过程的语言，还没有指定“时间之间究竟怎样联系”。现在加入可计算的结构：二阶矩保证相关存在，Gaussian 限制联合分布，增量性质限制新增部分的关系。最后把这些条件组合成 Wiener 和 Poisson 两个模型；各条件并不是一层比一层强的同一条分类。',
      'Poisson 过程：随机事件到达，计数器向上跳':'Wiener 适合连续起伏的扰动；若每次事件发生让计数加 1，就需要另一种路径。把“互不重叠区间的新增计数独立”和“同长度区间有同样规律”放在一起，再指定计数服从 Poisson 分布，就得到这里的到达模型。',
      '四种“更复杂”，分别改了哪一层？':'普通 Poisson 模型已会处理固定速率、每次贡献 1 的到达。现实偏离它时，先辨认改了什么：速率随时钟变、速率随这一天变、一次到达留下持续响应，还是每次贡献量不同。下面分别只改一层，沿用已经会的条件化与求和方法。'
    }}
    for ch,mapping in bridges.items():
        p=ROOT/f'chapter{ch}/index.html'; s=p.read_text(encoding='utf-8')
        for title,text in mapping.items():
            marker='<h2>'+title+'</h2>'
            assert marker in s,title
            if marker+'<p class="bridge">' not in s:s=s.replace(marker,marker+'<p class="bridge">'+text+'</p>',1)
        inserts={1:{
          '<h3 id="joint-distribution">':'<p class="bridge">只看一个数的分布，无法回答“两次数值同时满足条件”的问题。先把可能取值排成二维表，表格内部是联合分布，沿行列加总是边缘，固定一列并重新归一化是条件分布。</p>',
          '<h3 id="covariance-matrix">':'<p class="bridge">两个量有一项协方差，三个量就有三对。为避免漏掉配对，把它们按行列整理成矩阵；先把它当表格读，后面的矩阵公式只是把加权求和压缩成一行。</p>',
          '<h3>Laplace 变换的定义':'<p class="bridge">特征函数适用于所有实随机变量，但等待时间非负，可以改用始终衰减的权重；整数计数又能用幂次保存每个概率。接下来的两种变换是按取值特点选择的工具，不是额外两种随机变量。</p>',
          '<h3>4 个弱大数定律':'<p class="bridge">这些定理都在回答同一个问题：样本平均能否在概率意义下接近期望平均。先看最容易验证的“独立且方差有界”，不满足时再检查弱一些的条件。它们是不同适用范围的工具，不要求每题四种都试。</p>'
        },2:{
          '<h3>两条必须满足的一致性要求':'<p class="bridge">如果这些联合分布真来自同一段记录，就不能因我们重排观测顺序、或少看一个时刻而自相矛盾。这正是下面对称性与相容性的来源。</p>',
          '<h3 id="orthogonal">':'<p class="bridge">下一步不是比较累计状态，而是比较两段新增量。可以要求乘积平均为零（正交），也可以要求全部概率可分解（独立）；先分开这两个要求，才不会把它们误当同义词。</p>',
          '<h3 id="arrivals">':'<p class="bridge">“三分钟内来了几人”已经会算；现在把问题倒过来：“等到第三个人要多久？”计数与到达时刻描述的是同一条阶梯，连接两者的事件是：第 k 次到达已发生，当且仅当累计计数至少为 k。</p>',
          '<h3 id="uniform-arrivals">':'<p class="bridge">下一类题先告诉你总共来了 n 人，再问他们在区间里怎样分布。总数已经固定，不能继续把子区间计数当作无条件独立的 Poisson；要改用给定总数后的到达位置规律。</p>'
        }}[ch]
        for marker,text in inserts.items():
            assert marker in s,marker
            if text not in s:s=s.replace(marker,text+marker,1)
        s=s.replace('</head>','<link rel="stylesheet" href="../shared.css">\n</head>',1) if '../shared.css' not in s else s
        if ch==2 and '../chapter3/index.html' not in s:s=s.replace('<p class="muted">整套 HTML', '<p><a href="../chapter3/index.html">第三章：随机分析 →</a></p><p class="muted">整套 HTML',1)
        p.write_text(s,encoding='utf-8')

if __name__=='__main__':
    from chapter3_content import write as c3
    from chapter4_content import write as c4
    from chapter5_content import write as c5
    bridge_old(); c3(); c4(); c5()
