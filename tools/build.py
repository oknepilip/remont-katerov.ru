# -*- coding: utf-8 -*-
"""Сборка сайта из tools/content.py.
  python3 tools/build.py            -> предпросмотр в /preview/ (noindex, с заметками TODO)
  python3 tools/build.py --live     -> сайт в корень репозитория (индексируется, sitemap.xml, Метрика)
"""
import sys, os, json, html, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content as C

LIVE = "--live" in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "" if LIVE else "/preview"
OUT = ROOT if LIVE else os.path.join(ROOT, "preview")
SITE = "https://remontkaterov.ru"
WORKER = "https://soft-cherry-0d1a.pilipenko470.workers.dev/"
METRIKA = "109135905"
VER = "1"
e = html.escape
PAGES = []  # (path, title) для sitemap

ORG = {"@type": "LocalBusiness", "@id": SITE + "/#org", "name": "Маньяна Менеджмент", "legalName": "ООО «Маньяна Менеджмент»",
       "url": SITE + "/", "telephone": "+7 921 772-71-77", "email": C.EMAIL, "foundingDate": C.YEAR,
       "address": {"@type": "PostalAddress", "streetAddress": "пр. Крузенштерна, 18", "addressLocality": "Санкт-Петербург", "addressCountry": "RU"},
       "areaServed": ["Санкт-Петербург", "Ленинградская область"]}

def url(p): return BASE + p
def absu(p): return SITE + BASE + p
def svc(slug): return next(s for s in C.SERVICES if s["slug"] == slug)
def case(slug): return next(c for c in C.CASES if c["slug"] == slug)

def ld(*objs):
    return "".join('<script type="application/ld+json">%s</script>\n' % json.dumps(dict({"@context": "https://schema.org"}, **o), ensure_ascii=False) for o in objs)

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": absu(p)} for i, (n, p) in enumerate(items)]}

def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

def layout(path, title, desc, body, jsonld="", cur="", home=False, ogimg=None):
    PAGES.append(path)
    nav = [("Услуги", "/uslugi/", "uslugi"), ("Работы", "/raboty/", "raboty"), ("Коммерческие суда", "/kommercheskie-suda/", "kom"), ("Вопросы", "/#faq", "")]
    navh = "".join('<a href="%s"%s>%s</a>' % (h if h.startswith("#") else url(h), ' aria-current="page"' if k and k == cur else "", n) for n, h, k in nav)
    robots = "" if LIVE else '<meta name="robots" content="noindex, nofollow">\n'
    metrika = ("""<script>(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};m[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})(window,document,'script','https://mc.yandex.ru/metrika/tag.js?id=%s','ym');ym(%s,'init',{webvisor:true,clickmap:true,accurateTrackBounce:true,trackLinks:true});</script>
<noscript><div><img src="https://mc.yandex.ru/watch/%s" style="position:absolute;left:-9999px" alt=""></div></noscript>\n""" % (METRIKA, METRIKA, METRIKA)) if LIVE else ""
    og = absu("/img/%s.webp" % (ogimg or "100"))
    splash = '<div class="splash" id="splash"><span class="logo" role="img" aria-label="Логотип"></span><p>Маньяна Менеджмент · судоремонт</p><button class="btn" id="skipSplash" type="button">Пропустить</button></div>\n' if home else ""
    servs = "".join('<li><a href="%s">%s</a></li>' % (url("/uslugi/%s/" % s["slug"]), s["name"]) for s in C.SERVICES)
    page = f"""<!DOCTYPE html>
<html lang="ru"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{robots}<link rel="canonical" href="{absu(path)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:url" content="{absu(path)}"><meta property="og:image" content="{og}"><meta property="og:site_name" content="Маньяна Менеджмент">
<link rel="icon" href="{url('/assets/logo.svg')}" type="image/svg+xml">
<link rel="preload" href="{url('/assets/golos-cyr.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{url('/assets/site.css')}?v={VER}">
{jsonld}</head><body>
<a class="skip" href="#main">К содержанию</a>
{splash}<header class="top"><div class="bar wrap">
<a class="brand" href="{url('/')}"><span class="logo" role="img" aria-label="Логотип: якорь и гаечные ключи"></span><span>Маньяна Менеджмент<small>судоремонт, Санкт-Петербург</small></span></a>
<nav id="nav" aria-label="Основное">{navh}<a class="btn cta-m" href="#request">Оставить заявку</a></nav>
<a class="btn o tel" href="{C.TEL_HREF}" aria-label="Позвонить: +7 921 772-71-77"><b aria-hidden="true">☎</b><span>{C.TEL}</span></a>
<a class="btn cta" href="#request">Оставить заявку</a>
<button class="btn o" id="menuBtn" type="button" aria-expanded="false" aria-controls="nav">Меню</button></div></header>
<main id="main">
{body}
</main>
<footer id="contacts"><div class="wrap fcols">
<div><b>Маньяна Менеджмент</b><br>ООО «Маньяна Менеджмент», работаем с {C.YEAR} года<br>Порт «Морской Фасад», пр. Крузенштерна, 18<br>п. Лисий Нос<br><a href="{C.TEL_HREF}">{C.TEL}</a><br><a href="mailto:{C.EMAIL}">{C.EMAIL}</a></div>
<div><b>Услуги</b><ul>{servs}</ul></div>
<div><b>Разделы</b><ul><li><a href="{url('/raboty/')}">Работы</a></li><li><a href="{url('/kommercheskie-suda/')}">Коммерческие суда</a></li><li><a href="{url('/politika/')}">Политика конфиденциальности</a></li></ul></div>
</div></footer>
<script>window.MM={{base:{json.dumps(BASE)},worker:{json.dumps(WORKER)}}}</script>
<script src="{url('/assets/site.js')}?v={VER}" defer></script>
{metrika}</body></html>
"""
    d = os.path.join(OUT, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page)

def chat(start="start"):
    return f"""<div class="chat" role="region" aria-label="Диалог со Стармехом" data-chat data-start="{start}">
 <div class="chead"><span class="av" role="img" aria-label="Стармех: якорь с глазами и гаечным ключом"></span><div><b>Стармех</b><small>виртуальный механик: задаст вопросы и передаст заявку мастеру</small></div></div>
 <div class="cbody"><div class="clog" aria-live="polite" aria-relevant="additions"></div><div class="cctl"></div>
 <noscript><p class="note">Диалог работает с включённым JavaScript. Позвоните: {C.TEL}</p></noscript></div></div>"""

def request(topic=""):
    return f"""<section class="s wrap" id="request" aria-labelledby="h-req"><div class="req"><div><h2 id="h-req">Заявка без диалога</h2><p>Опишите задачу, мастер перезвонит. Или звоните: <a href="{C.TEL_HREF}">{C.TEL}</a></p></div><div data-reqform="{e(topic)}"></div></div></section>"""

def todo(notes):
    if LIVE or not notes: return ""
    return "".join('<p class="todo"><b>заметка для владельца, на сайте не появится</b>%s</p>' % e(n) for n in notes)

def works(groups):
    out = []
    for g, items in groups:
        lis = ""
        for it in items:
            if isinstance(it, tuple): lis += '<li><span class="pr">%s</span>%s</li>' % (e(it[1]), e(it[0]))
            else: lis += "<li>%s</li>" % e(it)
        out.append('<div class="wk"><h3>%s</h3><ul>%s</ul></div>' % (e(g), lis))
    return '<div class="works">%s</div>' % "".join(out)

def steps(st):
    return '<ol class="steps">%s</ol>' % "".join('<li class="step"><b>%s</b>%s</li>' % (e(a), e(b)) for a, b in st)

def faq(items):
    return '<div class="faq">%s</div>' % "".join("<details><summary>%s</summary><p>%s</p></details>" % (e(q), e(a)) for q, a in items)

def case_card(c):
    cov = c.get("cover") or c["imgs"][0]
    return '<a class="case" href="%s"><img src="%s" alt="%s" loading="lazy" width="640" height="480"><p><small>%s</small>%s</p></a>' % (url("/raboty/%s/" % c["slug"]), url("/img/%s-s.webp" % cov), e(c["alt"]), e(c["tag"]), e(c["title"]))

def head(crumbs, h1, lead, acts=True):
    cr = "".join('<li><a href="%s">%s</a></li>' % (url(p), e(n)) for n, p in crumbs[:-1]) + '<li aria-current="page">%s</li>' % e(crumbs[-1][0])
    a = f'<div class="acts"><a class="btn" href="#request">Оставить заявку</a><a class="btn o" href="{C.TEL_HREF}">{C.TEL}</a></div>' if acts else ""
    return f'<div class="first"><div class="ph-head wrap"><nav aria-label="Хлебные крошки"><ol class="crumbs">{cr}</ol></nav><h1>{e(h1)}</h1><p class="lead">{e(lead)}</p>{a}</div></div>'

def bento():
    out = ""
    for s in C.SERVICES:
        cls = " ".join(x for x in ("w" if s.get("wide") else "", "p" if s.get("plate") else "") if x)
        out += '<a%s href="%s"><svg viewBox="0 0 48 48" aria-hidden="true">%s</svg>%s<span>%s</span></a>' % (' class="%s"' % cls if cls else "", url("/uslugi/%s/" % s["slug"]), C.ICONS[s["slug"]], e(s["name"]), e(s["short"]))
    return '<div class="bento">%s</div>' % out

# ---------- страницы ----------
def home():
    cases = "".join(case_card(c) for c in C.CASES[:6])
    body = f"""<div class="first" id="top"><div class="fw wrap">
<div class="head"><span class="stamp">отвечает мастер, Стармех помогает</span><h1>Ремонт катеров и яхт в <em>Санкт-Петербурге</em></h1></div>
<div class="chatw">{chat()}
 <a class="show" href="#services">Показать сайт без диалога ↓</a></div>
<div class="info"><p class="lead">Двигатели, редукторы, электрика, корпус, интерьер, зимнее хранение. Суда от 5 до 30 метров. База в порту «Морской Фасад» и на Лисьем Носу.</p>
<ul class="trust"><li>Работаем с {C.YEAR} года, ремонтируем в своих помещениях</li><li>Ремонтируем и обслуживаем катера государственных служб</li><li>В команде сварщики, механики и электрики, которые работали на сухогрузах и других коммерческих судах</li></ul></div>
<div class="pics"><div class="ph" role="img" aria-label="Заглушка для фото цеха"><span>Фото: цех на «Морском Фасаде»<small>заглушка, нужно своё фото</small></span></div><div class="ph" role="img" aria-label="Заглушка для фото мастера за работой"><span>Фото: мастер за работой<small>заглушка</small></span></div><div class="ph" role="img" aria-label="Заглушка для фото катера на базе"><span>Фото: катер на базе<small>заглушка</small></span></div></div>
</div></div>
<section class="s wrap" id="services" aria-labelledby="h-serv"><h2 id="h-serv">Услуги</h2>{bento()}</section>
<section class="s wrap" id="process" aria-labelledby="h-proc"><h2 id="h-proc">Как мы работаем</h2>{steps(C.STEPS_DEFAULT)}</section>
<section class="s wrap" id="cases" aria-labelledby="h-cases"><h2 id="h-cases">Работы</h2><p class="sub">Настоящие фото из нашего цеха. <a href="{url('/raboty/')}">Все {len(C.CASES)} работ</a></p><div class="cases">{cases}</div></section>
<section class="s wrap" id="team" aria-labelledby="h-team"><h2 id="h-team">Команда</h2><p class="sub">Сварщики, механики и электрики, которые работали на сухогрузах, танкерах, буксирах и катерах.</p><div class="team">
<div class="tm"><div class="ph" role="img" aria-label="Заглушка для фото сотрудника"><span>Фото сварщика<small>заглушка</small></span></div><b>Имя Фамилия</b><br>Сварщик · стаж __ лет<br><span>Работал на: __. Аттестация: __</span></div>
<div class="tm"><div class="ph" role="img" aria-label="Заглушка для фото сотрудника"><span>Фото механика<small>заглушка</small></span></div><b>Имя Фамилия</b><br>Механик · стаж __ лет<br><span>Работал на: __</span></div>
<div class="tm"><div class="ph" role="img" aria-label="Заглушка для фото сотрудника"><span>Фото электрика<small>заглушка</small></span></div><b>Имя Фамилия</b><br>Электрик · стаж __ лет<br><span>Работал на: __</span></div></div></section>
<section class="s wrap" id="about" aria-labelledby="h-about"><h2 id="h-about">Коротко о компании</h2><div class="two">
<dl class="facts"><dt>Компания</dt><dd>ООО «Маньяна Менеджмент», работаем с {C.YEAR} года</dd><dt>Где</dt><dd>Санкт-Петербург, порт «Морской Фасад» (пр. Крузенштерна, 18) и п. Лисий Нос</dd><dt>Суда</dt><dd>Яхты и катера от 5 до 30 м. В <a href="{url('/kommercheskie-suda/')}">большой судоремонт</a> мы только заходим</dd><dt>Двигатели</dt><dd>Volvo Penta, Mercury, Yamaha, Suzuki</dd><dt>Заказчики</dt><dd>Владельцы яхт и катеров, государственные службы</dd></dl>
<div class="gov"><h3>Как работает Стармех</h3><ul><li>Кнопки и ветки диалога написаны заранее и работают всегда.</li><li>На вопрос по технике Стармех ищет документ в базе мануалов.</li><li>Если ответа нет, вопрос уходит мастеру как заявка.</li><li>Цены, сроки и гарантии называет мастер, а не Стармех.</li></ul></div></div></section>
<section class="s wrap" id="faq" aria-labelledby="h-faq"><h2 id="h-faq">Частые вопросы</h2>{faq(C.FAQ_HOME)}</section>
<section class="s wrap" aria-labelledby="h-part"><h2 id="h-part">Партнёры</h2><ul class="chips"><li>Яхт-клуб Санкт-Петербурга</li><li>Пассажирский порт</li><li>Смоленка</li></ul></section>
{request()}"""
    org = dict(ORG, description="Ремонт и обслуживание яхт и катеров от 5 до 30 м в Санкт-Петербурге: двигатели, редукторы, электрика, корпус, интерьер, зимнее хранение и консервация.")
    layout("/", "Ремонт катеров и яхт в Санкт-Петербурге — Маньяна Менеджмент",
           "Ремонт и обслуживание яхт и катеров 5–30 м в Санкт-Петербурге: двигатели Volvo Penta, Mercury, Yamaha, Suzuki, редукторы, электрика, корпус, интерьер, зимнее хранение.",
           body, ld(org, faq_ld(C.FAQ_HOME)), home=True)

def services_index():
    cr = [("Главная", "/"), ("Услуги", "/uslugi/")]
    body = head(cr, "Услуги по ремонту катеров и яхт", "Ремонтируем и обслуживаем яхты и катера от 5 до 30 метров в Санкт-Петербурге и Ленинградской области. Выберите направление или опишите задачу Стармеху.") + \
        f'<section class="s wrap" aria-labelledby="h-serv"><h2 id="h-serv">Направления</h2>{bento()}</section>' + \
        f'<section class="s wrap" aria-labelledby="h-proc"><h2 id="h-proc">Как мы работаем</h2>{steps(C.STEPS_DEFAULT)}</section>' + \
        f'<section class="s wrap" aria-labelledby="h-ask"><div class="ask"><div><h2 id="h-ask">Не знаете, что выбрать?</h2><p>Стармех задаст несколько вопросов и передаст заявку мастеру.</p></div>{chat()}</div></section>' + request()
    layout("/uslugi/", "Услуги: ремонт и обслуживание катеров и яхт в Санкт-Петербурге",
           "Ремонт двигателей и редукторов, диагностика, электрика, корпус, интерьер, запчасти, проектирование, зимнее хранение катеров и яхт в Санкт-Петербурге.",
           body, ld(crumbs_ld(cr)), cur="uslugi")

def service_page(s):
    p = "/uslugi/%s/" % s["slug"]
    cr = [("Главная", "/"), ("Услуги", "/uslugi/"), (s["name"], p)]
    cs = [case(x) for x in s.get("cases", [])]
    cases = f'<section class="s wrap" aria-labelledby="h-cases"><h2 id="h-cases">Наши работы по теме</h2><div class="cases">{"".join(case_card(c) for c in cs)}</div></section>' if cs else ""
    others = "".join('<li><a href="%s">%s</a></li>' % (url("/uslugi/%s/" % o["slug"]), e(o["name"])) for o in C.SERVICES if o is not s)
    body = head(cr, s["h1"], s["lead"]) + f"""
<section class="s wrap" aria-labelledby="h-works"><h2 id="h-works">Что делаем</h2>{todo(s.get("todo"))}{works(s["works"])}<p class="note" style="max-width:46rem;font-size:1rem">Стоимость называем после осмотра: она зависит от модели, состояния узла и цены запчастей. Работу начинаем после вашего согласия.</p></section>
<section class="s wrap" aria-labelledby="h-proc"><h2 id="h-proc">Как проходит работа</h2>{steps(s.get("steps") or C.STEPS_DEFAULT)}</section>
{cases}
<section class="s wrap" aria-labelledby="h-faq"><h2 id="h-faq">Вопросы и ответы</h2>{faq(s["faq"])}</section>
<section class="s wrap" aria-labelledby="h-ask"><div class="ask"><div><h2 id="h-ask">Расскажите о задаче</h2><p>Стармех задаст несколько вопросов и передаст заявку мастеру. Цену и срок назовёт мастер.</p></div>{chat(s["start"])}</div></section>
<section class="s wrap" aria-labelledby="h-oth"><h2 id="h-oth">Другие услуги</h2><ul class="chips">{others}</ul></section>
{request(s["name"])}"""
    service = {"@type": "Service", "name": s["h1"], "description": s["desc"], "serviceType": s["name"], "url": absu(p),
               "areaServed": ["Санкт-Петербург", "Ленинградская область"], "provider": ORG}
    layout(p, s["title"] + " — Маньяна Менеджмент", s["desc"], body, ld(service, crumbs_ld(cr), faq_ld(s["faq"])), cur="uslugi",
           ogimg=(cs[0].get("cover") or cs[0]["imgs"][0]) if cs else None)

def commercial():
    k = C.COMMERCIAL; p = "/kommercheskie-suda/"
    cr = [("Главная", "/"), ("Коммерческие суда", p)]
    honest = "".join("<li>%s</li>" % e(x) for x in k["honest"])
    body = head(cr, k["h1"], k["lead"]) + f"""
<section class="s wrap" aria-labelledby="h-works"><h2 id="h-works">С чем можно обратиться</h2>{todo(k["todo"])}{works(k["works"])}</section>
<section class="s wrap" aria-labelledby="h-hon"><h2 id="h-hon">Что важно знать заранее</h2><div class="gov" style="max-width:52rem"><ul>{honest}</ul></div></section>
<section class="s wrap" aria-labelledby="h-cases"><h2 id="h-cases">Работа с дизелем</h2><div class="cases">{case_card(case("yamz-238-toplivnaya-apparatura"))}</div></section>
<section class="s wrap" aria-labelledby="h-faq"><h2 id="h-faq">Вопросы и ответы</h2>{faq(k["faq"])}</section>
<section class="s wrap" aria-labelledby="h-ask"><div class="ask"><div><h2 id="h-ask">Опишите задачу</h2><p>Укажите тип судна, объём работ и сроки. Ответим, что берём и что нет.</p></div>{chat("c")}</div></section>
{request("Коммерческие суда")}"""
    service = {"@type": "Service", "name": k["h1"], "description": k["desc"], "url": absu(p), "areaServed": ["Санкт-Петербург", "Ленинградская область"], "provider": ORG}
    layout(p, k["title"] + " — Маньяна Менеджмент", k["desc"], body, ld(service, crumbs_ld(cr), faq_ld(k["faq"])), cur="kom", ogimg="photo_18")

def cases_index():
    cr = [("Главная", "/"), ("Работы", "/raboty/")]
    body = head(cr, "Наши работы", "Настоящие фото из нашего цеха: двигатели, колонки, корпуса, покраска. Без стоковых картинок.", acts=False) + \
        f'<section class="s wrap" aria-labelledby="h-all"><h2 id="h-all">Все работы</h2><div class="cases">{"".join(case_card(c) for c in C.CASES)}</div></section>' + request()
    layout("/raboty/", "Работы: ремонт катеров и яхт, фото — Маньяна Менеджмент",
           "Фото выполненных работ: ремонт алюминиевого корпуса, ТО Volvo Penta D6, колонки DPH C, Mercury, Nanni, ЯМЗ-238, покраска катеров. Санкт-Петербург.",
           body, ld(crumbs_ld(cr)), cur="raboty")

def case_page(c):
    p = "/raboty/%s/" % c["slug"]; s = svc(c["service"])
    cr = [("Главная", "/"), ("Работы", "/raboty/"), (c["title"], p)]
    gal = ""
    if c.get("video"):
        gal += f'<figure><video controls preload="none" playsinline poster="{url("/img/%s.webp" % c["video"])}" aria-label="{e(c["alt"])}"><source src="{url("/img/%s.mp4" % c["video"])}" type="video/mp4"></video></figure>'
    for i, im in enumerate(c["imgs"]):
        gal += '<figure><a href="%s"><img src="%s" alt="%s" loading="%s" width="640" height="480"></a></figure>' % (url("/img/%s.webp" % im), url("/img/%s-s.webp" % im), e("%s, фото %d" % (c["alt"], i + 1)), "eager" if i == 0 else "lazy")
    same = [x for x in C.CASES if x["service"] == c["service"] and x is not c][:3]
    more = f'<section class="s wrap" aria-labelledby="h-more"><h2 id="h-more">Похожие работы</h2><div class="cases">{"".join(case_card(x) for x in same)}</div></section>' if same else ""
    body = head(cr, c["title"], c["text"], acts=False) + f"""
<section class="s wrap" aria-labelledby="h-gal"><h2 id="h-gal">Фото работы</h2>{todo(["Добавьте к этой работе: какое судно, что было не так, что сделали по шагам, сколько заняло. Сейчас здесь только одна фраза с текущего сайта."])}<div class="gal">{gal}</div>
<p style="margin-top:1.25rem">Услуга: <a href="{url('/uslugi/%s/' % s['slug'])}">{e(s['name'])}</a></p></section>
{more}
{request(c["title"])}"""
    cov = c.get("cover") or c["imgs"][0]
    art = {"@type": "Article", "headline": c["title"], "description": c["text"], "image": [absu("/img/%s.webp" % (i)) for i in (c["imgs"] or [cov])], "author": {"@id": SITE + "/#org"}, "publisher": ORG, "mainEntityOfPage": absu(p)}
    layout(p, c["title"] + " — работы Маньяна Менеджмент", c["text"], body, ld(art, crumbs_ld(cr)), cur="raboty", ogimg=cov)

def policy():
    p = "/politika/"; cr = [("Главная", "/"), ("Политика конфиденциальности", p)]
    body = head(cr, "Политика конфиденциальности", "Коротко о том, какие данные мы получаем через сайт и что с ними делаем.", acts=False) + f"""
<section class="s wrap"><div class="prose">{todo(["Это черновик. Перед запуском текст должен проверить юрист: требования 152-ФЗ к политике оператора шире."])}
<h2>Кто обрабатывает данные</h2><p>ООО «Маньяна Менеджмент», ИНН 7814833438, ОГРН 1247800002890. Адрес: г. Санкт-Петербург, пр. Крузенштерна, 18. Почта: <a href="mailto:{C.EMAIL}">{C.EMAIL}</a>.</p>
<h2>Какие данные мы получаем</h2><ul><li>Номер телефона, который вы указали в заявке.</li><li>Текст заявки: описание судна и задачи.</li><li>Ответы, выбранные в диалоге со Стармехом.</li></ul>
<h2>Зачем</h2><p>Чтобы мастер перезвонил вам и ответил на заявку. Для рассылок и рекламы эти данные не используем и третьим лицам не продаём.</p>
<h2>Как передаётся заявка</h2><p>Заявка с сайта уходит сотрудникам компании в мессенджер Telegram через сервис Cloudflare Workers.</p>
<h2>Как отозвать согласие</h2><p>Напишите на <a href="mailto:{C.EMAIL}">{C.EMAIL}</a> или позвоните: <a href="{C.TEL_HREF}">{C.TEL}</a>. Удалим ваши данные из переписки по заявке.</p></div></section>"""
    layout(p, "Политика конфиденциальности — Маньяна Менеджмент", "Какие данные получает сайт remontkaterov.ru, зачем и как отозвать согласие на обработку.", body, ld(crumbs_ld(cr)))

def main():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    for f in ("site.css", "site.js"):
        shutil.copy(os.path.join(ROOT, "tools", "src", f), os.path.join(OUT, "assets", f))
    home(); services_index()
    for s in C.SERVICES: service_page(s)
    commercial(); cases_index()
    for c in C.CASES: case_page(c)
    policy()
    if LIVE:
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join("<url><loc>%s</loc></url>\n" % absu(p) for p in PAGES) + "</urlset>\n"
        open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(sm)
    print("built", len(PAGES), "pages ->", OUT)

main()
