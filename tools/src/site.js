/* Маньяна Менеджмент — меню, формы и сценарии Стармеха.
   Сценарии работают без модели. Свободный вопрос: поиск по списку мануалов, иначе «ИИ офлайн» и заявка мастеру.
   Настройки приходят из window.MM: {base, worker, pdfs}. Адрес с ?test=1 ничего не отправляет. */
(function(){
'use strict';
var MM=window.MM||{},TEL='+7 (921) 772-71-77',TELH='tel:+79217727177';
var TEST=/[?&]test=1/.test(location.search);
var $=function(s,r){return (r||document).querySelector(s)};
var el=function(tag,cls,txt){var e=document.createElement(tag);if(cls)e.className=cls;if(txt!=null)e.textContent=txt;return e};
var uid=0;

/* ---------- отправка заявки ---------- */
function clean(s){return String(s||'').replace(/[*_`\[\]]/g,' ').replace(/\s+/g,' ').trim().slice(0,1500)}
function send(lines){
  var text=lines.filter(Boolean).join('\n')+'\n\nСтраница: '+location.href.split('?')[0];
  if(TEST||!MM.worker){console.log('[MM test] заявка не отправлена:\n'+text);return Promise.resolve({ok:true,test:true})}
  return fetch(MM.worker,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:text})})
    .then(function(r){return r.json()}).then(function(d){if(!d||!d.ok)throw new Error('worker');return d});
}

/* ---------- форма с проверкой ---------- */
/* fields: [id,label,type('text'|'ta'|'tel'),required,hint] ; onSend(values) -> Promise */
function buildForm(box,fields,opt){
  var p='f'+(++uid)+'_';opt=opt||{};
  var f=el('form','f');f.noValidate=true;
  fields=fields.concat([['ph','Телефон','tel',1]]);
  fields.forEach(function(d){
    var w=el('div'),l=el('label',null,d[1]+(d[3]?' (обязательно)':''));l.htmlFor=p+d[0];
    var i=d[2]=='ta'?el('textarea'):el('input');i.id=p+d[0];
    if(d[2]=='ta')i.rows=3;else i.type=d[2];
    if(d[2]=='tel'){i.inputMode='tel';i.autocomplete='tel'}
    if(opt.values&&opt.values[d[0]])i.value=opt.values[d[0]];
    w.append(l,i);
    if(d[4]){var h=el('p','note',d[4]);h.style.margin='.2rem 0 0';w.append(h)}
    var e=el('div');e.id=p+d[0]+'e';w.append(e);f.append(w);
  });
  var cw=el('div'),cl=el('label','ck'),cb=el('input');cb.type='checkbox';cb.id=p+'ok';cl.htmlFor=cb.id;
  var sp=el('span');sp.append('Согласен на обработку персональных данных. ');
  var pa=el('a',null,'Политика конфиденциальности');pa.href=(MM.base||'')+'/politika/';sp.append(pa);
  cl.append(cb,sp);var ce=el('div');ce.id=p+'oke';cw.append(cl,ce);f.append(cw);
  var b=el('button','btn',opt.submit||'Отправить заявку');b.type='submit';f.append(b);
  var st=el('div');st.setAttribute('role','status');f.append(st);
  box.append(f);
  function err(i,e,m){i.setAttribute('aria-invalid','true');i.setAttribute('aria-describedby',e.id);e.innerHTML='';e.append(el('p','er',m))}
  f.onsubmit=function(ev){
    ev.preventDefault();var bad=null,v={};st.innerHTML='';
    fields.forEach(function(d){
      var i=$('#'+p+d[0],f),e=$('#'+p+d[0]+'e',f);e.innerHTML='';i.removeAttribute('aria-invalid');i.removeAttribute('aria-describedby');
      var x=i.value.trim(),m='';v[d[0]]=x;
      if(d[3]&&!x)m='Заполните поле.';
      else if(d[2]=='tel'&&x&&!/^[+\d][\d\s()\-]{9,}$/.test(x))m='Введите номер, например +7 921 772-71-77.';
      if(m){err(i,e,m);bad=bad||i}
    });
    ce.innerHTML='';cb.removeAttribute('aria-invalid');
    if(!cb.checked){err(cb,ce,'Отметьте согласие, без него мы не можем принять заявку.');bad=bad||cb}
    if(bad){bad.focus();return}
    b.disabled=true;var old=b.textContent;b.textContent='Отправляем…';
    opt.onSend(v).then(function(r){opt.onDone(r)},function(){
      b.disabled=false;b.textContent=old;
      var m=el('p','er');m.append('Заявка не отправилась. Позвоните: ');var a=el('a',null,TEL);a.href=TELH;m.append(a);st.append(m);
    });
  };
  return f;
}

/* ---------- сценарий Стармеха ---------- */
var WHERE=[['На воде','form'],['На берегу или на трейлере','form'],['В эллинге или на стоянке','form']];
var ENG=function(to){return ['Volvo Penta','Mercury','Yamaha','Suzuki','Другой или не знаю'].map(function(t){return [t,to]})};
var N={
 start:{say:'Какое у вас судно?',stack:1,opts:[['Яхта или катер, 5–30 м','y'],['Коммерческое судно','c'],['Срочная поломка','sos'],['Вопрос по технике','k']]},

 /* яхты и катера */
 y:{say:'Что нужно сделать?',opts:[['Мотор или редуктор','m1'],['Корпус, покраска','h1'],['Электрика','e1'],['Интерьер','i1'],['Плановое ТО','t1'],['Зимнее хранение','w1'],['Запчасти','p1'],['Другое','form']]},
 m1:{say:'Какой у вас двигатель?',opts:ENG('m2')},
 m2:{say:'Что происходит?',stack:1,opts:[['Не заводится','m_start'],['Перегревается','m_hot'],['Дымит или потерял мощность','m_smoke'],['Стук или вибрация','m_knock'],['Вода или эмульсия в масле','m_emul'],['Течёт масло или топливо','m_leak'],['Не включается передача','m_gear'],['Другое','where']]},
 m_start:{say:'Понял. Частые причины: аккумулятор, топливо, стартер или датчики. Точную причину назовёт мастер после диагностики. Где сейчас судно?',opts:WHERE},
 m_hot:{say:'Не запускайте двигатель до осмотра: при перегреве можно повредить головку блока. Часто дело в импеллере помпы или забитом теплообменнике, но причину назовёт мастер. Где сейчас судно?',opts:WHERE},
 m_smoke:{say:'Запомните цвет дыма (чёрный, белый, сизый) и когда он появляется: на холодную, под нагрузкой, постоянно. Это ускорит диагностику. Где сейчас судно?',opts:WHERE},
 m_knock:{say:'Со стуком и сильной вибрацией лучше не ходить: можно повредить вал, муфту или редуктор. Мастер осмотрит двигатель и линию вала. Где сейчас судно?',opts:WHERE},
 m_emul:{say:'Эмульсия значит, что в масло попала вода. Двигатель или колонку лучше не эксплуатировать до осмотра. Похожую работу мы делали на колонке Volvo Penta DPH C. Где сейчас судно?',link:['Посмотреть эту работу','/raboty/volvo-penta-dph-c-emulsiya/'],opts:WHERE},
 m_leak:{say:'Заметьте, где именно течёт и сколько уходит за выход. Мастер найдёт место течи и скажет, что менять. Где сейчас судно?',opts:WHERE},
 m_gear:{say:'Причина может быть в тросах управления, муфте или в самом редукторе. Мастер проверит по порядку, от простого к сложному. Где сейчас судно?',opts:WHERE},
 where:{say:'Где сейчас судно?',opts:WHERE},
 h1:{say:'Из чего корпус?',opts:[['Алюминий','h2'],['Стеклопластик','h2'],['Сталь','h2'],['Не знаю','h2']]},
 h2:{say:'Что нужно сделать с корпусом?',stack:1,opts:[['Пробоина, трещина, вмятина','where'],['Покраска, необрастающее покрытие','where'],['Днище, реданы, замена листа','h_al'],['Коррозия','where'],['Другое','where']]},
 h_al:{say:'Такие работы делаем: меняли лист обшивки и реданы на алюминиевом катере. Где сейчас судно?',link:['Посмотреть эту работу','/raboty/alyuminievyj-korpus-i-redany/'],opts:WHERE},
 e1:{say:'Что с электрикой?',stack:1,opts:[['Не заряжаются аккумуляторы','form'],['Не работает прибор или навигация','form'],['Проводка, щит, предохранители','form'],['Береговое питание, зарядное, инвертор','form'],['Установить новое оборудование','form'],['Другое','form']]},
 i1:{say:'Что нужно в интерьере?',stack:1,opts:[['Обивка, диваны, матрасы','form'],['Палуба, тик','form'],['Мебель','form'],['Тенты и чехлы','form'],['Иллюминаторы, люки','form'],['Другое','form']]},
 t1:{say:'Для какого двигателя нужно ТО?',opts:ENG('t2')},
 t2:{say:'Запишите в заявке модель двигателя и наработку в моточасах, если знаете. Мастер назовёт перечень работ и стоимость.',form:[['msg','Модель и моточасы','ta',0]]},
 w1:{say:'Какой длины судно?',opts:[['До 8 м','w2'],['8–12 м','w2'],['12–20 м','w2'],['20–30 м','w2']]},
 w2:{say:'Что нужно?',stack:1,opts:[['Консервация на зиму','w3'],['Хранение','w3'],['Консервация и хранение','w3'],['Расконсервация весной','w3']]},
 w3:{say:'Условия, свободные места и стоимость назовёт мастер. Оставьте телефон, он перезвонит.',link:['Что входит в консервацию','/uslugi/zimnee-hranenie/'],form:[['msg','Марка и модель судна, двигатель','ta',0]]},
 p1:{say:'Напишите марку и модель двигателя, серийный номер (если есть) и какая деталь нужна. Подберём оригинал или аналог и назовём срок.',form:[['msg','Двигатель и деталь','ta',1]]},

 /* коммерческие суда */
 c:{say:'Как компания мы только заходим в большой судоремонт. А наши сварщики, механики и электрики уже работали на сухогрузах и других коммерческих судах. Расскажите о задаче, честно скажем, возьмёмся или нет.',stack:1,opts:[['Описать задачу','c2',1],['Что мы можем взять','@/kommercheskie-suda/'],['Посмотреть команду','@/#team']]},
 c2:{say:'Укажите тип и проект судна, объём работ и сроки. ТЗ и документы можно прислать позже.',form:[['ship','Тип и проект судна','text',1],['msg','Объём работ и сроки','ta',1]]},

 /* срочно */
 sos:{say:'Если есть угроза людям или судну, сначала звоните в службу спасения: 112. По ремонту быстрее всего позвонить мастеру.',stack:1,opts:[['Позвонить: '+TEL,'@'+TELH,1],['Оставить телефон, мне перезвонят','sos2']]},
 sos2:{say:'Коротко опишите, что случилось и где стоит судно.',form:[['msg','Что случилось и где судно','ta',1]],urgent:1},

 /* вопрос по технике */
 k:{say:'Спросите про свой мотор или редуктор. Поищу в статьях и мануалах, а если не найду, передам вопрос мастеру.',ask:1},
 koff:{tag:'ИИ офлайн',say:'В базе знаний ответа не нашёл, а ИИ сейчас не на связи. Сохраню вопрос как заявку, мастер ответит. Оставьте телефон.',form:[['msg','Ваш вопрос','ta',1]]},

 form:{say:'Опишите, что происходит и когда. Оставьте телефон, мастер перезвонит.',form:[['msg','Что случилось','ta',0]]}
};
/* мануалы, которые лежат на сайте: [регулярное выражение, название, файлы] */
var KB=[
 [/df ?(300|250) ?ap|df300|df250/i,'Suzuki DF300AP / DF250AP',[['Технический паспорт','df300ap-df250ap-tehpasport.pdf'],['Каталог запчастей','df300ap-df250ap-katalog.pdf']]],
 [/df ?200/i,'Suzuki DF200AP',[['Технический паспорт','df200ap-tehpasport.pdf'],['Каталог запчастей','df200ap-katalog.pdf']]],
 [/df ?(325|350)/i,'Suzuki DF325A / DF350A',[['Технический паспорт','df325a-df350a-tehpasport.pdf']]],
 [/df ?(40|50|60)(?!\d)/i,'Suzuki DF40A / DF50A / DF60A',[['Технический паспорт','df40a-df60a-tehpasport.pdf'],['Каталог запчастей','df40a-df60a-katalog.pdf']]],
 [/df ?(70|80|90|100)(?!\d)/i,'Suzuki DF70A / DF80A / DF90A / DF100B',[['Технический паспорт','df70a-df100b-tehpasport.pdf']]],
 [/dt ?(9[.,]?9|15)/i,'Suzuki DT9.9A / DT15A',[['Технический паспорт','dt9.9a-dt15a-tehpasport.pdf']]],
 [/якорн|цеп[ьи]|швартов/i,'Якоря и якорные цепи',[['ГОСТ 228-79. Цепи якорные','gost-228-79-yakornye-cepi.pdf'],['ГОСТ Р 51722-2001. Нормы снабжения','gost-r-51722-2001-snabzhenie.pdf']]]
];

/* статьи базы знаний: [выражение, название, адрес] */
var ART=[
 [/импеллер|крыльчатк|помп[аыу]|перегре|tell-?tale|контрольн\S* отверсти/i,'Замена импеллера помпы охлаждения','zamena-impellera'],
 [/анализ\S* масл|масло\S* (анализ|проб)|металл\S* в масл|щелочн|tbn/i,'Анализ масла двигателя','analiz-masla'],
 [/vodia|код\S* (ошиб|неисправ)|ошибк\S* volvo|spn|fmi|dtc|event log/i,'Как читать коды ошибок Volvo Penta VODIA','kody-oshibok-volvo-penta-vodia'],
 [/тепловиз|греет\S* (провод|клемм|автомат)|нагрев\S* (провод|клемм|щит)/i,'Тепловизионный контроль судовой электрики','teplovizor-elektrika'],
 [/параллел|синхрониз|два генератор|обратн\S* мощност/i,'Параллельная работа генераторов','parallelnaya-rabota-generatorov'],
 [/центровк|расцентр|вибрац|гребн\S* вал|дейдвуд|муфт/i,'Центровка валовой линии','centrovka-valovoj-linii'],
 [/узк|толщин\S* (обшив|лист|металл)|толщиномер|ультразвук/i,'УЗК-обмер обшивки','uzk-obmer-obshivki'],
 [/пескостру|абразив|дробеструй/i,'Пескоструйная очистка алюминия','peskostrujnaya-ochistka-alyuminiya'],
 [/консерв|зим[уаео]|зимн|морозы?|хранени/i,'Консервация катера на зиму: чек-лист','konservaciya-na-zimu']
];
function Chat(root){
  var log=$('.clog',root),ctl=$('.cctl',root),hist=[],path=[],first=true,question='';
  function say(t,who,tag,link){
    var d;
    if(who){d=el('div','u',t)}
    else{d=el('div','row');var a=el('span','av');a.setAttribute('aria-hidden','true');var m=el('div','m');m.append(el('b',null,'Стармех · '+(tag||'сценарий')),document.createTextNode(t));
      if(link){m.append(' ');var l=el('a',null,link[0]);l.href=link[1];m.append(l)}
      d.append(a,m)}
    log.append(d);log.scrollTop=log.scrollHeight;
  }
  function tail(w){
    if(hist.length>1){var b=el('button','btn back','← Назад');b.type='button';b.onclick=function(){hist.pop();var h=hist.pop();path.length=h.p;go(h.id)};w.append(b)}
    if(hist.length>1){var r=el('button','btn back','Начать заново');r.type='button';r.onclick=restart;w.append(r)}
  }
  function restart(init){hist=[];path=[];question='';go(init===true&&N[root.dataset.start]?root.dataset.start:'start')}
  function focusFirst(){if(!first){var x=ctl.querySelector('button,input,textarea,a');if(x)x.focus({preventScroll:true})}first=false}
  function go(id){
    var n=N[id];hist.push({id:id,p:path.length});
    var link=n.link?[n.link[0],(MM.base||'')+n.link[1]]:null;
    say(n.say,0,n.tag,link);ctl.innerHTML='';
    if(n.opts){
      var w=el('div','opts'+(n.stack?' stack':''));
      n.opts.forEach(function(o){
        var b;
        if(o[1].charAt(0)=='@'){b=el('a','btn'+(o[2]?' main':''),o[0]);var h=o[1].slice(1);b.href=/^tel:/.test(h)?h:(MM.base||'')+h}
        else{b=el('button','btn'+(o[2]?' main':''),o[0]);b.type='button';b.onclick=function(){say(o[0],1);path.push(o[0]);go(o[1])}}
        w.append(b)});
      tail(w);ctl.append(w);
    }
    if(n.ask){
      var f=el('form','f');f.noValidate=true;var q='q'+(++uid);
      var l=el('label',null,'Ваш вопрос');l.htmlFor=q;var i=el('input');i.type='text';i.id=q;
      var h=el('p','note','Например: Suzuki DF300AP, свечи');h.style.margin='.2rem 0 0';
      var w0=el('div');w0.append(l,i,h);var b0=el('button','btn','Спросить');b0.type='submit';f.append(w0,b0);
      f.onsubmit=function(e){e.preventDefault();var v=i.value.trim();if(!v){i.focus();return}say(v,1);question=v;answer(v)};
      ctl.append(f);var w2=el('div','opts');tail(w2);ctl.append(w2);
    }
    if(n.form){
      buildForm(ctl,n.form,{values:question?{msg:question}:null,
        onSend:function(v){return send([(n.urgent?'СРОЧНО. ':'')+'Заявка с сайта (Стармех)',path.length?'Ветка: '+path.join(' → '):'',v.ship?'Судно: '+clean(v.ship):'',v.msg?'Сообщение: '+clean(v.msg):'','Телефон: '+clean(v.ph)])},
        onDone:function(r){
          say('Заявка принята. Мастер перезвонит и уточнит детали.');ctl.innerHTML='';
          var ok=el('p','okm',r&&r.test?'✔ Тестовый режим: заявка не отправлена.':'✔ Готово, заявка отправлена.');ok.setAttribute('role','status');ctl.append(ok);
          var w=el('div','opts');var r2=el('button','btn','Начать заново');r2.type='button';r2.onclick=restart;w.append(r2);ctl.append(w);
        }});
      var w3=el('div','opts');tail(w3);ctl.append(w3);
    }
    focusFirst();
  }
  function answer(q){
    var hit=null,arts=[];KB.forEach(function(k){if(!hit&&k[0].test(q))hit=k});
    ART.forEach(function(k){if(arts.length<2&&k[0].test(q))arts.push(k)});
    if(!hit&&!arts.length){path.push('Вопрос по технике');go('koff');return}
    var d=el('div','row'),a=el('span','av');a.setAttribute('aria-hidden','true');var m=el('div','m');
    m.append(el('b',null,'Стармех · база знаний'));
    if(arts.length){m.append(arts.length>1?'Об этом есть статьи: ':'Об этом есть статья: ');
      arts.forEach(function(k,i){if(i)m.append(', ');var l=el('a',null,k[1]);l.href=(MM.base||'')+'/baza-znanij/'+k[2]+'/';m.append(l)});m.append('. ')}
    if(hit){m.append('Документы по '+hit[1]+': ');
      hit[2].forEach(function(f,i){if(i)m.append(', ');var l=el('a',null,f[0]+' (PDF)');l.href=(MM.base||'')+'/manuals/'+f[1];l.target='_blank';l.rel='noopener';m.append(l)});m.append('. ')}
    m.append('Если ответа там нет, передам вопрос мастеру.');d.append(a,m);log.append(d);log.scrollTop=log.scrollHeight;
    ctl.innerHTML='';var w=el('div','opts');
    var b1=el('button','btn main','Передать вопрос мастеру');b1.type='button';b1.onclick=function(){say('Передать вопрос мастеру',1);path.push('Вопрос по технике');go('koff')};
    var b2=el('button','btn','Задать другой вопрос');b2.type='button';b2.onclick=function(){hist.pop();question='';go('k')};
    w.append(b1,b2);tail(w);ctl.append(w);focusFirst();
  }
  restart(true);
}
document.querySelectorAll('[data-chat]').forEach(function(r){new Chat(r)});

/* ---------- заявка без диалога ---------- */
document.querySelectorAll('[data-reqform]').forEach(function(box){
  var topic=box.dataset.reqform;
  buildForm(box,[['msg','Что нужно сделать','ta',1]],{
    onSend:function(v){return send(['Заявка с сайта (форма)',topic?'Тема: '+topic:'','Сообщение: '+clean(v.msg),'Телефон: '+clean(v.ph)])},
    onDone:function(r){box.innerHTML='';var p=el('p','okm',r&&r.test?'✔ Тестовый режим: заявка не отправлена.':'✔ Заявка отправлена. Мастер перезвонит.');p.setAttribute('role','status');p.tabIndex=-1;box.append(p);p.focus()}});
});

/* ---------- меню и заставка ---------- */
var mb=$('#menuBtn'),nav=$('#nav');
if(mb&&nav){
  var menu=function(o){nav.classList.toggle('open',o);mb.setAttribute('aria-expanded',o);mb.textContent=o?'Закрыть':'Меню'};
  mb.onclick=function(){menu(!nav.classList.contains('open'))};
  nav.onclick=function(e){if(e.target.closest('a'))menu(false)};
  addEventListener('keydown',function(e){if(e.key=='Escape'&&nav.classList.contains('open')){menu(false);mb.focus()}});
}
var sp=$('#splash');
if(sp){
  var seen=false;try{seen=sessionStorage.getItem('mmSplash')=='1';sessionStorage.setItem('mmSplash','1')}catch(e){}
  if(seen)sp.classList.add('gone');
  var sk=$('#skipSplash');if(sk)sk.onclick=function(){sp.classList.add('gone')};
}
})();
