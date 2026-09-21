# -*- coding: utf-8 -*-
"""FleetCare 기업형 홈페이지 생성기 (v2 — 기획안 Fleet Agent Concept 반영)"""
import io, os, re, json, hashlib

# 출력 폴더는 이 스크립트가 있는 곳의 site/ 다.
# 경로를 박아두지 않으므로 다른 PC 에서 받아도 그대로 돌아간다.
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site") + os.sep
SITE = "https://fleetcare.co.kr"
TEL_D = "02-6925-0516"
TEL_L = "tel:0269250516"
MAIL = "jdgp@jdgp.co.kr"

NAV = [
    ("about.html",   "회사소개"),
    ("service.html", "서비스 안내"),
    ("truck.html",   "화물·특장 솔루션"),
    ("care.html",    "보험·만기 케어"),
    ("contact.html", "상담·견적 문의"),
]


def slug(path):
    return "" if path == "index.html" else path[:-5]


def head(title, desc, path, page_class=""):
    canon = SITE + "/" + slug(path)
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">

<!-- 네이버 서치어드바이저 소유확인 (www / 루트 도메인 각각 등록) -->
<meta name="naver-site-verification" content="53c28ed440f686cbabbb48f0951c99045587370b" />
<meta name="naver-site-verification" content="0e321ec8d27f75ccc712e8a74899867167935637" />
<link rel="canonical" href="{canon}">
<meta name="robots" content="index, follow">

<meta property="og:type" content="website">
<meta property="og:site_name" content="플릿케어">
<meta property="og:locale" content="ko_KR">
<meta property="og:url" content="{canon}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/favicon.svg">
<meta name="theme-color" content="#14293D">

<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
<link rel="stylesheet" href="/css/style.css">

<script src="/js/main.js" defer></script>
</head>
<body{(' class="' + page_class + '"') if page_class else ''}>

<a class="skip" href="#main">본문 바로가기</a>
"""


def header(active):
    links = ""
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ""
        links += f'        <li><a href="/{href}"{cur}>{label}</a></li>\n'
    return f"""
<header class="hdr">
  <div class="wrap hdr-in">
    <a class="hdr-logo" href="/" aria-label="플릿케어 홈">
      <img src="/assets/logo.svg" alt="플릿케어 — 법인 차량관리" width="222" height="45">
    </a>

    <nav class="gnb" id="gnb" aria-label="주요 메뉴">
      <ul>
{links}      </ul>
    </nav>

    <div class="hdr-cta">
      <a class="hdr-tel" href="{TEL_L}">{TEL_D}</a>
      <a class="btn btn-ink" href="/contact.html">상담 요청</a>
    </div>

    <button class="hdr-menu" type="button" id="menuBtn" aria-expanded="false" aria-controls="gnb" aria-label="메뉴 열기">
      <span></span><span></span><span></span>
    </button>
  </div>
</header>
"""


def page_head(title, lead, eyebrow=None):
    eb = f'<p class="ph-eyebrow">{eyebrow}</p>' if eyebrow else ""
    return f"""
  <section class="ph">
    <div class="wrap">
      {eb}
      <h1>{title}</h1>
      <p class="ph-lead">{lead}</p>
    </div>
  </section>
"""


CTA_BAND = f"""
  <section class="cta">
    <div class="wrap cta-in">
      <div>
        <h2>차량 대수와 만기일만 알려주시면, 나머지는 저희가 정리합니다.</h2>
        <p>관리 대행 비용은 받지 않습니다. 기존에 받으신 견적서가 있으면 그대로 보내 주세요.</p>
      </div>
      <div class="cta-btns">
        <a class="btn btn-green btn-lg" href="{TEL_L}">{TEL_D}</a>
        <a class="btn btn-ghost btn-lg" href="/contact.html">상담·견적 문의</a>
      </div>
    </div>
  </section>
"""


def footer():
    links = "".join(f'<li><a href="/{h}">{l}</a></li>' for h, l in NAV)
    return f"""
<footer class="ftr">
  <div class="wrap ftr-in">
    <div class="ftr-brand">
      <img src="/assets/logo-white.svg" alt="플릿케어" width="200" height="41">
      <p class="ftr-tag">법인 전용 플릿 에이전트 — 도입·특장·보험·만기 통합 케어</p>
    </div>

    <nav class="ftr-nav" aria-label="사이트 메뉴">
      <p class="ftr-h">메뉴</p>
      <ul>{links}<li><a href="/faq.html">자주 묻는 질문</a></li></ul>
    </nav>

    <div class="ftr-info">
      <p class="ftr-h">회사 정보</p>
      <dl>
        <div><dt>상호</dt><dd>주식회사 제이디엔드</dd></div>
        <div><dt>대표이사</dt><dd>박동천</dd></div>
        <div><dt>사업자등록번호</dt><dd>766-86-02631</dd></div>
        <div><dt>주소</dt><dd>서울특별시 영등포구 여의대방로 379, 605호</dd></div>
        <div><dt>대표전화</dt><dd><a href="{TEL_L}">{TEL_D}</a></dd></div>
        <div><dt>이메일</dt><dd><a href="mailto:{MAIL}">{MAIL}</a></dd></div>
      </dl>
    </div>
  </div>
  <div class="wrap ftr-copy">
    <p>© 2026 주식회사 제이디엔드. All rights reserved.</p>
  </div>
</footer>

<div class="mbar">
  <a class="mbar-tel" href="{TEL_L}">전화 상담 {TEL_D}</a>
  <a class="mbar-form" href="/contact.html">상담 요청</a>
</div>

</body>
</html>
"""


# ==========================================================================
# 홈
# ==========================================================================
INDEX = f"""
  <section class="hero">
    <div class="wrap hero-in">
      <div class="hero-copy">
        <h1>법인차량 도입부터<br>화물 특장, 보험, 만기 관리까지<br>단 하나의 전담 창구</h1>
        <p class="hero-sub">리스사가 모르는 특장 프로세스 해결 · 운용리스 보험 다이렉트 케어 ·
          만기 손익 최적화 분석 리포트</p>
        <p class="hero-free">차량관리 대행 비용은 받지 않습니다.</p>
        <div class="hero-btns">
          <a class="btn btn-ink btn-lg" href="/contact.html">상담·견적 문의</a>
          <a class="btn btn-line btn-lg" href="{TEL_L}">{TEL_D}</a>
        </div>
      </div>
      <div class="hero-mark" aria-hidden="true">
        <img src="/assets/symbol.svg" alt="" width="360" height="231">
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="wrap">
      <h2 class="h2">전담자 한 명이 이어서 맡는 여섯 가지</h2>
      <p class="sec-lead measure">차량 한 대를 들이는 일은 계약으로 끝나지 않습니다.
        특장 승인, 보험 갱신, 만기 정산, 그리고 현장에서 쓰는 사람의 불편이 계속 따라옵니다.
        그 전부를 한 창구에서 받습니다.</p>

      <div class="val6">
        <article>
          <p class="val-n">01</p>
          <h3>법인차량 현장관리시스템</h3>
          <p>분기마다 현장을 직접 방문해 차량 상태와 문제점을 정리하고,
            본사 총무팀과 협의해 개선점을 도출·관리하는 핵심 서비스입니다.</p>
        </article>
        <article>
          <p class="val-n">02</p>
          <h3>화물 특장 리스 전문</h3>
          <p>특장 비용을 리스료에 포함하고 원상복구 제외 반납 조건으로 설계합니다.
            외주장착이 포함된 건의 금융 승인을 금융사와 직접 소통해 풀어냅니다.</p>
        </article>
        <article>
          <p class="val-n">03</p>
          <h3>금융 비교·심사 대행</h3>
          <p>여러 금융사에 같은 조건으로 견적을 넣어 비교표로 정리합니다.
            리스·렌탈이 중심이지만 할부까지 같은 기준으로 놓고 비교합니다.
            기존 견적 재설계, 심사 대행, 정비 포함 상품 연결까지 진행합니다.</p>
        </article>
        <article>
          <p class="val-n">04</p>
          <h3>운용리스 통합 보험 관리</h3>
          <p>제휴 보험대리점과 연계해 비교 가입부터 매년 갱신까지.
            차량별 갱신일을 대장으로 붙여 관리합니다.</p>
        </article>
        <article>
          <p class="val-n">05</p>
          <h3>만기 손익 최적화 분석</h3>
          <p>중고차 실거래 시세 대비 잔존가치를 따져 반납과 인수 후 매각을 숫자로 비교합니다.
            만기일 역산 발주로 차량 공백을 막습니다.</p>
        </article>
        <article>
          <p class="val-n">06</p>
          <h3>차량 비용절감 컨설팅</h3>
          <p>도입 시점 조건 조정, 운영 중 보험 요율 재비교, 만기 시점 손익 비교.
            계약 기간 전체 비용을 세 시점에서 점검합니다.</p>
        </article>
      </div>
    </div>
  </section>

  <section class="sec sec-paper">
    <div class="wrap">
      <h2 class="h2">무엇이 다른가</h2>
      <p class="sec-lead measure">가격표를 비교해 드리는 곳은 많습니다.
        계약한 뒤에 무엇을 해주는가에서 갈립니다.</p>

      <div class="cmp-wrap">
        <table class="cmp">
          <caption class="sr-only">기존 캐피탈·일반 중개사와 플릿케어 비교</caption>
          <thead>
            <tr>
              <th scope="col">구분</th>
              <th scope="col">기존 캐피탈 / 일반 중개사</th>
              <th scope="col" class="cmp-us">플릿케어</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">금융 비교</th>
              <td>자사 상품만 제안합니다.</td>
              <td class="cmp-us">국내 27개 렌트·리스사와 연계해 조건을 비교하고 최적 조건을 제안합니다.</td>
            </tr>
            <tr>
              <th scope="row">심사 요청·진행</th>
              <td>특장·용품 구조를 몰라 승인이 지연되고 소통이 막힙니다.</td>
              <td class="cmp-us">리스사 출신 노하우로 금융사와 직접 소통해 원스톱으로 승인을 받습니다.</td>
            </tr>
            <tr>
              <th scope="row">외주장착 비용·반납조건</th>
              <td>리프트·도색·래핑 등 외주장착 비용은 리스에서 제외되고, 반납 시 원상복구를 요구합니다.</td>
              <td class="cmp-us">계약 전에 외주장착 비용 포함과 원상복구 제외 조건을 협의하고, 가능한 금융사를 골라 진행합니다.</td>
            </tr>
            <tr>
              <th scope="row">운용리스 보험</th>
              <td>법인 담당자가 직접 보험사를 비교하고 가입해야 합니다.</td>
              <td class="cmp-us">보험대리점과 연계해 비교 가입과 매년 갱신을 관리하고, 차량별 갱신일을 대장으로 붙입니다.</td>
            </tr>
            <tr>
              <th scope="row">계약 후 현장 관리</th>
              <td>없습니다. 계약이 끝나면 현장에 오지 않습니다.</td>
              <td class="cmp-us">분기별 현장 방문 → 리포트 → 본사 협의 → 개선 관리로 이어집니다.</td>
            </tr>
            <tr>
              <th scope="row">만기 처리</th>
              <td>캐피탈사가 통보하는 반납·인수 안내에 의존합니다.</td>
              <td class="cmp-us">중고차 시세를 연동한 정량 손익 리포트를 드리고 매각안까지 제안합니다.</td>
            </tr>
            <tr>
              <th scope="row">계약 후 창구</th>
              <td>금융사·보험사·장착업체별로 각각 연락해야 합니다.</td>
              <td class="cmp-us">전담자 한 명이 계약 기간 내내 같은 번호로 받습니다.</td>
            </tr>
            <tr>
              <th scope="row">비용</th>
              <td>컨설팅·관리 수수료를 부과하거나 계약 조건에 반영합니다.</td>
              <td class="cmp-us">관리 대행 비용이 없고, 외부 실비에 수수료를 얹지 않습니다.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="sec killer">
    <div class="wrap">
      <p class="killer-tag">핵심 서비스</p>
      <h2 class="h2 h2-inv">리스사가 모르는 화물차 특장·외주장착,<br>플릿케어는 잘 압니다.</h2>
      <div class="killer-grid">
        <div>
          <p class="killer-lead">윙바디, 탑차, 파워게이트, 리프트 같은 외주장착 작업.
            일반 리스사 심사팀은 구조를 몰라 승인이 지체되는 경우가 많습니다.</p>
          <p class="killer-lead">플릿케어는 리스사 출신 전문가가 금융사와 장착업체 사이의
            기술적·행정적 간극을 직접 메워 빠른 승인을 이끌어냅니다.</p>
          <p class="killer-lead">승인만이 아닙니다.
            <strong>특장 비용을 리스료에 포함시키고, 만기에 원상복구 없이 반납할 수 있는 조건</strong>으로
            계약합니다. 둘 다 계약할 때 정해지는 조건이라 처음부터 챙겨야 합니다.</p>
          <a class="btn btn-green btn-lg" href="/truck.html">화물·특장 솔루션 보기</a>
        </div>
        <div class="killer-specs">
          <h3 class="killer-specs-h">취급 사양</h3>
          <ul>
            <li>윙바디·탑차</li><li>탑 사이즈 제작</li>
            <li>내장탑·냉동탑</li><li>파워게이트 리프트</li>
            <li>크레인</li><li>차량 하부보강·차바닥</li>
            <li>도색·래핑</li><li>구조변경 및 등록</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="wrap">
      <p class="killer-tag killer-tag-ink">핵심 서비스</p>
      <h2 class="h2">보험 가입도, 만기 정산도 대신 받습니다.</h2>
      <div class="two">
        <div>
          <p class="lead">운용리스는 렌트와 달리 법인이 직접 보험에 가입해야 합니다.
            차량 수가 늘수록 갱신일이 제각각이 되고 누락 위험이 커집니다.</p>
          <p class="lead">플릿케어는 보험의 시작과 끝을 전담합니다.
            만기가 오면 반납과 인수 후 매각 중 어느 쪽이 유리한지 숫자로 정리해 드립니다.</p>
          <p class="lead">새 차로 바꾸시는 경우에는 생산·출고 기간을 역산해
            <strong>만기일에 맞춰 차량이 도착하도록</strong> 발주 시점을 잡아 드립니다.
            차량 공백이 생기지 않게 미리 소통하는 것이 핵심입니다.</p>
          <p><a class="tlink" href="/care.html">보험·만기 케어 자세히 보기</a></p>
        </div>
        <div class="note-card">
          <h3>만기 손익 리포트에 담기는 것</h3>
          <ul class="ck">
            <li>계약상 잔존가치와 중고차 실거래 시세 비교</li>
            <li>반납 시 예상 정산 항목과 감가 비용</li>
            <li>인수 후 매각 시 예상 차익</li>
            <li>어느 쪽이 얼마나 유리한지 결론</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="wrap">
      <h2 class="h2">분기마다 현장을 찾아갑니다</h2>
      <div class="two">
        <div>
          <p class="lead">차량을 쓰는 사람과 관리하는 사람이 다릅니다.
            현장의 불편은 본사에 잘 닿지 않고, 닿아도 개별 민원으로 흩어집니다.</p>
          <p class="lead">플릿케어는 3개월마다 사업장을 직접 방문해
            차량과 사람을 확인하고, 그 내용을 분기 현장 리포트로 정리해
            본사 총무·재무팀과 협의합니다.
            도출된 개선점은 실행하고 다음 분기 방문에서 결과를 확인합니다.</p>
          <p class="lead"><strong>계약 후 현장에 오는 에이전트는 플릿케어뿐입니다.</strong></p>
          <p><a class="tlink" href="/service.html#field">현장관리 서비스 자세히 보기</a></p>
        </div>
        <div class="note-card">
          <h3>분기 현장 리포트에 담기는 것</h3>
          <ul class="ck">
            <li>차량별 상태와 주행거리</li>
            <li>사고·정비 이력</li>
            <li>보험 갱신·만기 캘린더</li>
            <li>현장 요청사항</li>
            <li>개선 권고 및 전 분기 조치 결과</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="wrap">
      <h2 class="h2">맡기시면 달라지는 것</h2>
      <div class="effect">
        <article>
          <p class="effect-k">비용</p>
          <ul class="ck">
            <li>금융 조건 재설계로 계약 기간 전체 납입 총액을 줄입니다</li>
            <li>만기 반납·매각 판단으로 대당 추가 수익이 생깁니다</li>
          </ul>
        </article>
        <article>
          <p class="effect-k">시간</p>
          <ul class="ck">
            <li>현장 방문 결과지를 총무팀에 전달해 현장 파악 시간을 줄입니다</li>
            <li>정비·이슈가 생기면 플릿케어 담당자에게 알리는 것으로 끝납니다</li>
          </ul>
        </article>
        <article>
          <p class="effect-k">리스크</p>
          <ul class="ck">
            <li>운용리스 보험을 캐피탈사와 플릿케어가 이중으로 확인합니다</li>
            <li>만기일 역산 발주로 차량 공백 없이 교체합니다</li>
          </ul>
        </article>
        <article>
          <p class="effect-k">가시성</p>
          <ul class="ck">
            <li>분기 현장 리포트를 정기적으로 보고받습니다</li>
            <li>연도별 보험 사고 내역을 정리해 드립니다 (사고일자, 대물·자차 지급액)</li>
          </ul>
        </article>
      </div>
    </div>
  </section>

  <section class="sec sec-paper">
    <div class="wrap">
      <h2 class="h2">이런 기업에서 찾으십니다</h2>
      <div class="target">
        <article>
          <h3>법인차량 도입·교체를 검토 중인 재무·총무 담당자</h3>
          <p>어느 금융사가 유리한지, 지금 받은 견적이 좋은 조건인지 판단하기 어려운 경우입니다.
            여러 금융사 조건을 동시에 받아 비교표로 정리해 드립니다.</p>
        </article>
        <article>
          <h3>특장·외주장착으로 출고가 지연되는 물류·제조 기업</h3>
          <p>장착업체와 금융사 사이에서 서류와 사양 확인이 오가며 시간이 흘러가는 경우입니다.
            그 사이를 저희가 직접 메웁니다.</p>
        </article>
        <article>
          <h3>운용리스 보험 관리가 버거운 기업</h3>
          <p>차량마다 갱신일이 달라 매번 챙기기 어려운 경우입니다.
            전체 갱신 일정을 대장으로 관리하고 시점마다 먼저 알려드립니다.</p>
        </article>
      </div>
    </div>
  </section>
{CTA_BAND}
"""

# ==========================================================================
# 회사소개
# ==========================================================================
ABOUT = page_head(
    "회사소개",
    "공급자 중심의 리스·렌트 시장에서, 고객 중심의 플릿 에이전트로."
) + """
  <section class="sec">
    <div class="wrap two">
      <div>
        <h2 class="h2">플릿케어가 서 있는 자리</h2>
        <p class="lead"><strong>각자 자기 몫만 봅니다.</strong>
          금융사는 자사 상품밖에 계약할 수 없고, 정비 업체는 입고된 차만 보고,
          보험사는 증권을 발행할 뿐 계약이 잘 관리되는지까지는 보지 않습니다.
          고객사의 차량 전체를 한 번에 보는 자리가 비어 있습니다.</p>
        <p class="lead">플릿케어는 그 자리에 있는 <strong>고객 측 대리인</strong>입니다.
          한 곳의 금융사, 한 곳의 보험사만 쓰지 않습니다.
          여러 금융사를 비교 견적해 최적 조건을 찾고,
          도입부터 특장·보험·만기까지 한 사람이 이어서 맡습니다.
          이것이 저희가 말하는 <strong>법인 전용 플릿 에이전트</strong>입니다.</p>
      </div>
      <div class="factbox">
        <h3>한눈에</h3>
        <dl>
          <div><dt>운영 법인</dt><dd>주식회사 제이디엔드</dd></div>
          <div><dt>대표이사</dt><dd>박동천</dd></div>
          <div><dt>서비스명</dt><dd>플릿케어 (FleetCare)</dd></div>
          <div><dt>사업 영역</dt><dd>법인 차량 리스·렌탈·할부 중개, 특장 승인 대행, 보험·만기 통합 관리</dd></div>
          <div><dt>대상</dt><dd>법인 고객사</dd></div>
          <div><dt>관리 대행 비용</dt><dd class="hl">없음</dd></div>
        </dl>
      </div>
    </div>
  </section>

  <section class="sec sec-paper">
    <div class="wrap">
      <h2 class="h2">세 가지 전문성</h2>
      <div class="svc svc-alt">
        <article>
          <h3>리스사 출신 노하우</h3>
          <p>금융사 심사가 어떤 기준으로 돌아가는지 안쪽에서 겪었습니다.
            어떤 차량이 왜 거절되는지, 어떤 서류에서 막히는지 알고 준비합니다.
            거절 이력을 쌓지 않는 편이 다음 심사에도 유리합니다.</p>
        </article>
        <article>
          <h3>보험대리점 연계 관리</h3>
          <p>제휴 보험대리점과 연계해 비교 견적부터 가입, 갱신까지 함께 진행합니다.
            보험 계약 자체는 대리점을 통해 체결되고, 플릿케어는 차량대장과 갱신 일정을 붙여
            빠지는 것이 없도록 관리합니다. 담당자가 보험사마다 따로 연락할 일이 없습니다.</p>
        </article>
        <article>
          <h3>중고차 시세 기반 만기 분석</h3>
          <p>만기가 오면 캐피탈사 안내만 보고 결정하게 됩니다.
            저희는 실거래 시세를 붙여 반납과 인수 후 매각을 숫자로 비교해 드립니다.</p>
        </article>
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="wrap">
      <h2 class="h2">고객 맞춤 프로세스</h2>
      <p class="sec-lead measure">회사마다 차량 구성도 고민도 다릅니다.
        정해진 상품을 권하는 대신, 지금 상태를 먼저 정리하는 것부터 시작합니다.</p>
      <ol class="steps">
        <li>
          <span class="step-n">1</span>
          <div><h3>현황 파악</h3>
            <p>운용 중인 차량, 계약 중인 금융사, 만기 분포, 보험 갱신일을 한 장부로 정리합니다.
              아직 차량이 없으셔도 용도만 들으면 후보를 좁힐 수 있습니다.</p></div>
        </li>
        <li>
          <span class="step-n">2</span>
          <div><h3>조건 설계</h3>
            <p>여러 금융사 조건을 동시에 받아 비교합니다.
              기존에 받으신 견적서가 있으면 그것을 기준으로 더 나은 안을 다시 짭니다.</p>
            <p>정비를 포함해서 갈지, 보험을 어떻게 가져갈지, 특장비를 리스료에 넣을지도 이때 정합니다.
              계약 이후에는 바꾸기 어려운 조건들이라 처음에 맞춰 두는 편이 낫습니다.</p></div>
        </li>
        <li>
          <span class="step-n">3</span>
          <div><h3>실행 대행</h3>
            <p>서류 준비, 심사 진행, 특장 발주와 구조변경, 등록까지 대신 진행합니다.
              차량 생산·출고 기간을 감안해 일정을 잡고, 진행 상황을 그때그때 알려드립니다.</p></div>
        </li>
        <li class="step-key">
          <span class="step-n">4</span>
          <div><h3>운영 케어</h3>
            <p>보험 갱신, 과태료 확인, 만기 대응까지
              계약 기간 내내 같은 번호로 연락하시면 됩니다.</p>
            <p>분기마다 사업장을 방문해 현장 리포트를 만들고 총무·재무팀과 협의합니다.
              가만히 계셔도 차량이 실제로 어떻게 쓰이고 있는지 정기적으로 보고받으실 수 있습니다.</p>
            <p class="step-tag">여기까지가 플릿케어입니다</p></div>
        </li>
      </ol>
    </div>
  </section>

  <section class="sec sec-paper">
    <div class="wrap">
      <h2 class="h2">협력 네트워크</h2>
      <p class="sec-lead measure">한 곳에 묶이지 않고 여러 금융사·업체와 거래합니다.
        조건은 건별로 비교해 정리합니다.</p>
      <div class="netgrid">
        <article class="net-key">
          <h3>금융사</h3>
          <p class="net-n">국내 27개 렌트 및 리스사</p>
          <p>차량 조건과 회사 상황에 따라 유리한 곳이 매번 다릅니다.
            한 곳에 묶여 있지 않아 건마다 새로 비교할 수 있습니다.</p>
        </article>
        <article>
          <h3>특장·장착 업체</h3>
          <p>윙바디, 탑차, 파워게이트, 리프트 장착과 구조변경을 진행합니다.
            사양에 맞는 제작사를 연결하고 출고 일정까지 맞춥니다.</p>
        </article>
        <article>
          <h3>손해보험사</h3>
          <p>제휴 보험대리점을 통해 주요 손해보험사 요율을 비교하고 가입합니다.
            차량별 갱신일은 저희가 대장으로 붙여 관리합니다.</p>
        </article>
        <article>
          <h3>FMS·관제</h3>
          <p>도입 검토 시 비교 대상이 되는 업체입니다.
            업체마다 구성 항목이 달라 요건에 맞춰 제안합니다.</p>
        </article>
      </div>
    </div>
  </section>
""" + CTA_BAND

# ==========================================================================
# 서비스 안내
# ==========================================================================
SERVICE = page_head(
    "서비스 안내",
    "여러 캐피탈사 조건을 종합 비교해 법인 상황에 가장 맞는 금융 솔루션을 찾아 드립니다."
) + """
  <section class="sec">
    <div class="wrap">
      <h2 class="h2">법인 승용·SUV 렌트·리스·할부</h2>
      <p class="sec-lead measure">같은 차종이라도 금융사마다 월 납입액, 잔가 설정, 중도 해지 조건이 다릅니다.
        한 곳에 묶여 있지 않아 매번 새로 비교할 수 있습니다.
        리스와 렌탈이 중심이지만, 할부가 맞는 경우라면 할부로 진행하도록 도와드립니다.</p>

      <div class="svc">
        <article><h3>다중 금융사 동시 비교</h3>
          <p>여러 금융사에 같은 조건으로 견적을 넣고 비교표로 정리합니다.
            월 납입액만이 아니라 잔가, 중도 해지 위약, 정비 포함 여부까지 같이 봅니다.</p></article>
        <article><h3>리스·렌트·할부 방식 검토</h3>
          <p>회사의 재무 상황과 차량 용도에 따라 유리한 방식이 다릅니다.
            리스·렌탈은 매달 내는 돈을 비용으로 처리하고,
            할부는 출고 시점부터 차량이 법인 명의가 되어 자산으로 잡힙니다.</p>
          <p>세 방식을 같은 차·같은 기간으로 계산해 비교표로 드립니다.
            비용 처리와 보험 부담까지 함께 놓고 판단해 드립니다.</p></article>
        <article><h3>기존 견적 재설계</h3>
          <p>이미 받으신 견적서를 보내 주시면 그 조건을 기준으로 더 나은 안이 있는지 확인합니다.
            같은 차, 같은 기간으로 비교해야 의미가 있습니다.</p></article>
        <article><h3>심사 대행</h3>
          <p>서류 준비부터 심사 진행까지 대신합니다.
            심사에서 막히면 다른 금융사로 돌려 다시 진행합니다.</p></article>
        <article><h3>정비 포함 상품 연결</h3>
          <p>차량이 늘면 정비를 누가 챙기느냐가 문제가 됩니다.
            렌트·리스 상품 중에는 정기 점검과 소모품 교체가 포함된 구성이 있습니다.
            정비까지 맡기고 싶으시면 포함형 상품으로 계약하도록 도와드립니다.</p>
          <p>회사 상황에 따라 포함형이 유리할 수도, 그때그때 실비로 처리하는 편이 나을 수도 있습니다.
            차량 용도와 주행거리를 보고 계약 시점에 같이 판단합니다.</p>
          <p class="honest">계약 이후 개별 정비 접수를 저희가 대신 받지는 않습니다.
            포함형으로 계약하시면 해당 상품의 정비 네트워크에서 처리됩니다.</p></article>
        <article><h3>만기일 맞춤 출고 일정</h3>
          <p>차량은 생산과 출고에 기간이 걸립니다. 기존 차량의 만기일에서 역산해
            발주 시점을 잡고, 고객사와 소통하며 만기일에 맞춰 새 차를 대드립니다.
            차량 공백이 생기지 않게 하는 것이 목적입니다.</p></article>
      </div>
    </div>
  </section>

  <section class="sec sec-paper" id="field">
    <div class="wrap">
      <h2 class="h2">법인차량 현장관리 서비스</h2>
      <p class="sec-lead measure">차량 문제는 본사 사무실에서 보이지 않습니다.
        플릿케어는 3개월마다 현장을 직접 방문해 차량과 사람을 확인하고,
        그 내용을 정리해 본사 총무팀과 협의합니다.
        <strong>계약 후 현장에 오는 에이전트는 플릿케어뿐입니다.</strong></p>

      <ol class="steps">
        <li>
          <span class="step-n">1</span>
          <div><h3>현장 방문</h3>
            <p>분기 1회 사업장을 방문합니다.
              차량 상태, 운행 실태, 현장 담당자의 불편사항을 확인합니다.
              전화나 설문으로는 나오지 않는 이야기가 현장에서 나옵니다.</p></div>
        </li>
        <li>
          <span class="step-n">2</span>
          <div><h3>현장 리포트 작성</h3>
            <p>문제점과 개선점, 차량별 상태를 정리한 분기 현장 리포트를 만듭니다.
              개별 민원을 그대로 옮기는 것이 아니라 반복되는 문제로 묶습니다.</p></div>
        </li>
        <li>
          <span class="step-n">3</span>
          <div><h3>본사 협의</h3>
            <p>총무·재무팀에 자료를 제출하고 예산, 교체, 운영 정책을 협의합니다.</p></div>
        </li>
        <li class="step-key">
          <span class="step-n">4</span>
          <div><h3>개선 실행·관리</h3>
            <p>도출된 개선점을 실행하고, 다음 분기 방문에서 결과를 추적합니다.</p>
            <p class="step-tag">3개월 주기로 반복 · 개선 결과는 다음 방문에서 확인</p></div>
        </li>
      </ol>

      <div class="note-card reportbox">
        <h3>분기 현장 리포트에 담기는 것</h3>
        <ul class="ck">
          <li>차량별 상태와 주행거리</li>
          <li>사고·정비 이력</li>
          <li>보험 갱신·만기 캘린더</li>
          <li>현장 요청사항</li>
          <li>개선 권고 및 전 분기 조치 결과</li>
        </ul>
      </div>

      <div class="target">
        <article>
          <h3>현장 만족도가 올라갑니다</h3>
          <p>말한 것이 실제로 바뀌면 차량에 대한 불만이 줄어듭니다.
            현장에서 가장 큰 불만은 불편 그 자체보다 말해도 안 바뀐다는 데서 옵니다.</p>
        </article>
        <article>
          <h3>차량 품질이 유지됩니다</h3>
          <p>작은 이상을 일찍 발견해 큰 수리로 번지기 전에 잡습니다.
            현장은 웬만하면 참고 쓰다가 멈춘 뒤에야 알립니다.</p>
        </article>
        <article>
          <h3>다음 계약이 정확해집니다</h3>
          <p>현장에서 나온 이야기가 차종과 사양을 고르는 근거가 됩니다.
            책상에서 정한 사양과 실제로 필요한 사양은 자주 다릅니다.</p>
        </article>
      </div>

      <p class="sec-note">방문 주기는 분기별이 기본입니다.
        차량 대수와 사업장 위치에 따라 조정할 수 있습니다.
        이 서비스도 별도 비용을 받지 않습니다.</p>
    </div>
  </section>

  <section class="sec">
    <div class="wrap">
      <h2 class="h2">FMS 업체 비교·제안</h2>
      <div class="two">
        <div>
          <p class="lead">차량이 늘면 누가 어디를 얼마나 운행했는지가 보이지 않습니다.
            운행기록부 작성, 유류비 정산, 사적 사용 관리가 모두 여기서 막힙니다.</p>
          <p class="lead">플릿케어는 FMS(차량 운행 관리 시스템) 업체를 비교해
            회사 상황에 맞는 곳을 제안해 드립니다.
            <strong>업체마다 서비스 구성 항목이 조금씩 다릅니다.</strong>
            어떤 곳은 운행기록에 강하고 어떤 곳은 관제나 사고 감지에 강합니다.
            필요한 기능이 무엇인지부터 정리한 뒤에 비교해야 맞는 곳을 고를 수 있습니다.</p>
          <p class="lead honest">시스템을 저희가 직접 공급하지는 않습니다.
            업체 비교와 제안까지가 저희 역할입니다.</p>
        </div>
        <div class="note-card">
          <h3>이럴 때 검토하시면 됩니다</h3>
          <ul class="ck">
            <li>운행기록부를 매번 손으로 받고 계신 경우</li>
            <li>차량 사적 사용 관리가 필요한 경우</li>
            <li>화물 차량의 운행 경로와 가동률을 보셔야 하는 경우</li>
            <li>차량이 늘어 유류비 정산이 복잡해진 경우</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section class="sec sec-paper">
    <div class="wrap">
      <h2 class="h2">법인 비용절감 컨설팅</h2>
      <p class="sec-lead measure">차량비는 한 번 정해지면 계약 기간 내내 나갑니다.
        들이는 시점에 한 번, 만기 시점에 한 번 점검하면 차이가 큽니다.</p>

      <div class="svc svc-alt">
        <article><h3>도입 시점</h3>
          <p>차종, 기간, 주행거리 설정에 따라 총 비용이 달라집니다.
            실제 운행 패턴에 맞춰 과한 조건을 덜어냅니다.</p></article>
        <article><h3>운영 중</h3>
          <p>보험 갱신 때마다 요율을 다시 비교합니다.
            정비가 잦은 차량은 다음 계약에서 정비 포함형으로 돌리는 편이 나은지 같이 따져 봅니다.</p></article>
        <article><h3>만기 시점</h3>
          <p>반납과 인수 후 매각을 숫자로 비교합니다.
            잘못 판단하면 차량 한 대에서 수백만 원이 갈립니다.</p></article>
      </div>

      <p class="sec-note">관리 대행 비용은 받지 않습니다.
        정비 수리비·보험료·특장 제작비처럼 실제로 외부에 지급되는 금액만 고객사 부담이며,
        플릿케어가 중간에서 수수료를 얹지 않습니다.</p>
    </div>
  </section>
""" + CTA_BAND

# ==========================================================================
# 화물·특장 솔루션 (KILLER)
# ==========================================================================
TRUCK = page_head(
    "화물·특장 솔루션",
    "리스사가 모르는 화물차 특장·외주장착, 플릿케어는 잘 압니다.",
    "핵심 서비스"
) + """
  <section class="sec">
    <div class="wrap two">
      <div>
        <h2 class="h2">왜 특장 건은 승인이 늦어지는가</h2>
        <p class="lead">윙바디, 탑차, 파워게이트, 리프트 같은 외주장착 작업.
          일반 리스사 심사팀은 구조를 몰라 금융 승인이 지체되거나 거절되기 일쑤입니다.</p>
        <p class="lead">특장이 붙으면 차량 가액이 올라가는데, 심사팀 입장에서는
          그 장착물의 잔존가치를 어떻게 잡아야 할지 판단이 서지 않습니다.
          장착업체는 금융 서류를 모르고, 금융사는 특장 구조를 모릅니다.
          그 사이에서 시간이 흘러갑니다.</p>
        <p class="lead">플릿케어는 리스사 출신 전문가가 양쪽의 기술적·행정적 간극을 직접 메워
          빠른 승인을 이끌어냅니다.</p>
      </div>
      <div class="note-card">
        <h3>이런 경우 연락 주세요</h3>
        <ul class="ck">
          <li>특장비는 리스에 안 들어간다며 따로 부담하라는 안내를 받은 경우</li>
          <li>만기 반납 때 원상복구 조건이 붙어 있는 경우</li>
          <li>특장 때문에 캐피탈사에서 거절당한 건이 있는 경우</li>
          <li>장착 사양을 어떻게 잡아야 할지 모르겠는 경우</li>
          <li>출고 일정이 급한데 승인이 늦어지는 경우</li>
          <li>구조변경과 등록 절차가 처음인 경우</li>
        </ul>
        <p class="note-more">한 곳에서 막혔다고 끝이 아닙니다. 진행 경험이 있는 금융사는 다릅니다.</p>
      </div>
    </div>
  </section>

  <section class="sec sec-paper">
    <div class="wrap">
      <h2 class="h2">특장 비용과 반납 조건, 여기서 갈립니다</h2>
      <p class="sec-lead measure">특장 차량은 승인만 받으면 끝이 아닙니다.
        특장비를 어떻게 처리하느냐, 만기에 어떤 상태로 반납하느냐에서 실제로 나가는 돈이 크게 달라집니다.
        그런데 이 두 가지는 대부분 고객사에 불리하게 잡혀 있습니다.</p>

      <div class="svc">
        <article>
          <h3>특장 비용을 리스료에 포함시킵니다</h3>
          <p>대부분의 리스사는 특장에 들어간 비용을 리스료에 넣어주지 않습니다.
            차량값만 리스로 잡고 특장비는 따로 현금으로 부담하라는 식입니다.
            윙바디나 냉동탑처럼 특장비가 큰 차량은 초기 자금 부담이 그대로 회사에 남습니다.</p>
          <p>플릿케어는 금융사 담당자와 직접 협의해
            <strong>특장 비용까지 리스료에 포함시킵니다.</strong>
            목돈이 한 번에 나가지 않고 월 비용으로 평탄하게 처리됩니다.</p>
        </article>
        <article>
          <h3>원상복구 없이 반납되는 조건을 찾습니다</h3>
          <p>특장 차량은 만기에 원상복구를 요구하는 금융사가 많습니다.
            붙여둔 윙바디나 리프트를 떼어내고 원래 상태로 되돌려 반납하라는 조건입니다.
            탈거 비용이 또 들고, 떼어낸 특장물은 쓸 데가 없습니다.</p>
          <p>플릿케어는 계약 전에 반납 조건을 확인하고,
            <strong>원상복구 요구 없이 반납할 수 있는 금융사로 진행합니다.</strong></p>
        </article>
      </div>

      <p class="sec-note">두 가지 모두 <strong>계약할 때 정해지는 조건</strong>입니다.
        출고하고 나서는 바꾸기 어렵습니다. 특장 차량을 검토 중이시라면 계약 전에 확인하셔야 합니다.</p>
    </div>
  </section>

  <section class="sec killer">
    <div class="wrap">
      <h2 class="h2 h2-inv">취급 사양</h2>
      <p class="killer-lead">아래 사양 외에도 진행 가능한 건이 많습니다. 사양서를 보내 주시면 확인해 드립니다.</p>
      <div class="spec-grid">
        <article><h3>적재함</h3><ul><li>윙바디·탑차</li><li>탑 사이즈 제작</li><li>내장탑·냉동탑</li><li>카고·일반 화물</li></ul></article>
        <article><h3>상하차 장비</h3><ul><li>파워게이트</li><li>리프트</li><li>크레인</li><li>기타 외주장착 품목</li></ul></article>
        <article><h3>차체·외장</h3><ul><li>차량 하부보강</li><li>차바닥</li><li>도색</li><li>래핑</li></ul></article>
        <article><h3>행정</h3><ul><li>구조변경 및 등록</li><li>상용차 2.5톤 이상 협의</li><li>특장 제작사 섭외</li><li>사양 결정 자문</li></ul></article>
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="wrap">
      <h2 class="h2">원스톱 승인 프로세스</h2>
      <p class="sec-lead measure">장착업체와 금융사 사이에서 시간이 흘러가는 구간을 저희가 맡습니다.</p>
      <ol class="steps">
        <li>
          <span class="step-n">1</span>
          <div><h3>장착업체 사양 확인</h3>
            <p>어떤 작업에 쓸 차인지 듣고 필요한 장착물을 정리합니다.
              이미 받으신 사양서나 견적서가 있으면 그것부터 봅니다.</p></div>
        </li>
        <li>
          <span class="step-n">2</span>
          <div><h3>금융사 심사 소통</h3>
            <p>특장 진행 경험이 있는 금융사에 사양과 가액 구성을 미리 설명합니다.
              외주장착 비용 포함과 원상복구 제외 조건도 이 단계에서 협의합니다.</p></div>
        </li>
        <li>
          <span class="step-n">3</span>
          <div><h3>특장 발주·구조변경</h3>
            <p>사양에 맞는 제작사를 연결하고 일정을 잡습니다.
              차량 출고와 장착 일정이 맞물리도록 조정하고 구조변경을 진행합니다.</p></div>
        </li>
        <li class="step-key">
          <span class="step-n">4</span>
          <div><h3>등록·출고 일정 관리</h3>
            <p>장착 완료 후 등록까지 확인하고 차량을 인도합니다.
              상용차 2.5톤 이상은 별도 협의로 진행합니다.</p>
            <p class="step-tag">출고 후 운영 케어로 이어집니다</p></div>
        </li>
      </ol>
    </div>
  </section>
""" + CTA_BAND

# ==========================================================================
# 보험·만기 케어 (KILLER)
# ==========================================================================
CARE = page_head(
    "보험·만기 케어",
    "운용리스 차량의 복잡한 보험 관리, 플릿케어가 알아서 처리해 드립니다.",
    "핵심 서비스"
) + """
  <section class="sec">
    <div class="wrap">
      <h2 class="h2">운용리스 보험 통합 관리</h2>
      <p class="sec-lead measure">운용리스는 렌트와 달리 법인이 직접 보험에 가입해야 합니다.
        차량 수가 늘어날수록 갱신일이 제각각이 되고, 개별 가입의 번거로움과 누락 위험이 커집니다.</p>
      <p class="sec-lead measure">플릿케어는 제휴 보험대리점과 연계해
        법인차량 보험의 시작과 끝을 함께 맡습니다.
        보험 계약은 대리점을 통해 체결되고, 차량별 갱신 일정은 저희가 붙어서 관리합니다.</p>

      <div class="svc svc-alt">
        <article><h3>최저 요율 보험사 선정</h3>
          <p>주요 손해보험사를 비교해 가장 나은 조건의 보험사를 골라 가입합니다.
            차량마다 따로 알아보실 필요가 없습니다.</p></article>
        <article><h3>자동 갱신 및 행정 대행</h3>
          <p>갱신 시점이 오기 전에 미리 알려드리고 서류 작업을 무상으로 대행합니다.
            갱신 누락으로 무보험 기간이 생기는 일을 막습니다.</p></article>
        <article><h3>조건 변경 요청 창구</h3>
          <p>연령 변경, 대물 한도, 자차 조건처럼 계약 중에 바꿔야 할 일이 생기면
            플릿케어로 요청하시면 됩니다. 보험사마다 따로 연락하실 필요가 없습니다.</p></article>
        <article><h3>증권·갱신일 대장 관리</h3>
          <p>차량별로 어느 보험사에 어떤 조건으로 가입돼 있는지 대장에 정리합니다.
            차량이 늘어도 갱신일이 한눈에 보이고, 담당자가 바뀌어도 이력이 남습니다.</p>
          <p class="honest">사고 접수와 보상 협의는 가입하신 보험사와 직접 진행하셔야 합니다. 저희가 대신 처리하지 않습니다.</p></article>
      </div>
    </div>
  </section>

  <section class="sec sec-paper">
    <div class="wrap">
      <h2 class="h2">만기 손익 분석 리포트</h2>
      <p class="sec-lead measure">만기가 오면 캐피탈사에서 반납할지 인수할지 통보가 옵니다.
        그런데 어느 쪽이 회사에 유리한지는 알려주지 않습니다.
        차량 한 대에서 수백만 원이 갈리는 판단입니다.</p>

      <div class="two">
        <div class="report">
          <p class="report-h">리포트에 담기는 것</p>
          <ol class="report-list">
            <li><strong>계약상 잔존가치</strong><span>인수하려면 얼마를 내야 하는지</span></li>
            <li><strong>중고차 실거래 시세</strong><span>같은 연식·주행거리 차량이 실제로 얼마에 팔리는지</span></li>
            <li><strong>반납 시 예상 정산</strong><span>초과 주행, 손상 감가 등 추가로 나갈 금액</span></li>
            <li><strong>인수 후 매각 시 예상 차익</strong><span>인수가와 시세의 차이, 처분까지의 비용</span></li>
            <li><strong>매각업체 매칭</strong><span>인수 후 매각을 택하시면 매각업체를 연결하거나 매각 방안을 추천</span></li>
            <li><strong>결론</strong><span>어느 쪽이 얼마나 유리한지</span></li>
          </ol>
        </div>
        <div>
          <p class="lead">시세가 잔존가치보다 높으면 인수 후 매각이 유리합니다.
            반대면 반납이 낫습니다. 차종과 시기에 따라 매번 다르기 때문에
            그때그때 숫자를 봐야 합니다.</p>
          <p class="lead">만기 도래 전에 먼저 연락드려 이 리포트를 드립니다.
            판단은 회사에서 하시고, 결정된 방향으로 저희가 처리합니다.
            인수 후 매각을 택하시면 인수업체를 확인하고 매각처까지 연결해 드립니다.</p>
          <p class="lead">차량을 많이 쓰신 경우일수록 인수 후 매각이 유리해지는 폭이 큽니다.
            주행거리가 길어 반납 정산이 불리하게 나오는 차량일수록 특히 그렇습니다.</p>
          <p class="lead"><strong>이 리포트도 별도 비용을 받지 않습니다.</strong></p>
        </div>
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="wrap">
      <h2 class="h2">만기일에 맞춘 차량 제공</h2>
      <p class="sec-lead measure">차량은 계약한다고 바로 나오지 않습니다.
        차종과 사양에 따라 생산과 출고에 기간이 걸리고, 특장 작업이 붙으면 제작 기간이 더해집니다.
        만기일은 정해져 있는데 새 차가 늦게 나오면 그사이 차량 공백이 생깁니다.</p>
      <p class="sec-lead measure">플릿케어는 만기일에서 거꾸로 계산해 움직입니다.
        차종별 생산·출고 기간을 확인하고 고객사와 미리 소통해 발주 시점을 정합니다.
        <strong>만기일에 맞춰 새 차가 도착하도록 일정을 맞추는 것</strong>까지가 저희 일입니다.</p>

      <ol class="rev">
        <li><p class="rev-t">만기일 확인</p>
          <p class="rev-d">대장에서 만기가 다가오는 차량을 먼저 뽑아 알려드립니다.</p></li>
        <li><p class="rev-t">차종·사양 협의</p>
          <p class="rev-d">같은 차로 갈지, 용도가 바뀌었는지 고객사와 미리 정합니다.</p></li>
        <li><p class="rev-t">생산·출고 기간 확인</p>
          <p class="rev-d">차종과 시기에 따라 납기가 크게 다릅니다. 특장이 붙으면 제작 기간이 더해집니다.</p></li>
        <li><p class="rev-t">발주 시점 역산</p>
          <p class="rev-d">납기에 계약·심사 기간을 더해 언제 발주해야 하는지 정합니다.</p></li>
        <li><p class="rev-t">인수·반납 맞물리기</p>
          <p class="rev-d">새 차 출고와 기존 차 반납 사이에 공백이 생기지 않게 맞춥니다.</p></li>
      </ol>

      <p class="sec-note">납기가 밀릴 수도 있습니다. 그럴 때는 기존 계약 연장 등으로
        공백을 메우는 방법을 같이 정합니다. 미리 알고 움직이면 대부분 해결됩니다.</p>
    </div>
  </section>
""" + CTA_BAND

# ==========================================================================
# 상담·견적 문의
# ==========================================================================
CONTACT = page_head(
    "상담·견적 문의",
    "법인명과 연락처만 남겨 주시면 됩니다. 기존에 받으신 견적서가 있으면 더 빠릅니다."
) + f"""
  <section class="sec">
    <div class="wrap">
      <div class="contact">
        <div class="contact-call">
          <p class="call-label">전화 상담</p>
          <a class="call-num" href="{TEL_L}">{TEL_D}</a>
          <p class="call-time">평일 09:00 – 18:00</p>
          <p class="call-hint">차종과 대수만 알려주셔도 상담이 시작됩니다.
            아직 정하지 않으셨어도 괜찮습니다.</p>
          <hr class="call-rule">
          <p class="call-mail">견적서·사양서 보내실 곳<br>
            <a href="mailto:{MAIL}">{MAIL}</a></p>
        </div>

        <div class="contact-form">
          <form id="contactForm" novalidate>
            <p class="form-lead">담당자명과 연락처만 필수입니다. 확인하는 대로 연락드립니다.</p>

            <div class="row2">
              <div class="field">
                <label for="company">법인명 <span class="opt">선택</span></label>
                <input type="text" id="company" name="company" autocomplete="organization">
              </div>
              <div class="field">
                <label for="name">담당자명 <span class="req">필수</span></label>
                <input type="text" id="name" name="name" autocomplete="name" required aria-required="true">
              </div>
            </div>

            <div class="row2">
              <div class="field">
                <label for="phone">연락처 <span class="req">필수</span></label>
                <input type="tel" id="phone" name="phone" autocomplete="tel" inputmode="tel" required aria-required="true" placeholder="010-0000-0000">
              </div>
              <div class="field">
                <label for="email">이메일 <span class="opt">선택</span></label>
                <input type="email" id="email" name="email" autocomplete="email">
              </div>
            </div>

            <div class="field">
              <label for="vehicle">차량 종류 <span class="opt">선택</span></label>
              <select id="vehicle" name="vehicle">
                <option value="">선택해 주세요</option>
                <option value="승용·SUV">승용·SUV</option>
                <option value="화물·특장">화물·특장</option>
                <option value="승용과 화물 모두">승용과 화물 모두</option>
                <option value="보험·만기 관리만">보험·만기 관리만</option>
                <option value="아직 미정">아직 미정</option>
              </select>
            </div>

            <div class="field">
              <label for="message">문의 내용 <span class="opt">선택</span></label>
              <textarea id="message" name="message" rows="4" placeholder="대수, 사용 목적, 현재 계약 중인 금융사, 만기 시점 등 아시는 만큼만 적어 주세요."></textarea>
            </div>

            <div class="hp" aria-hidden="true">
              <label for="website">웹사이트</label>
              <input type="text" id="website" name="website" tabindex="-1" autocomplete="off">
            </div>

            <div class="consent">
              <input type="checkbox" id="agree" name="agree" required aria-required="true">
              <label for="agree">상담 진행을 위한 개인정보 수집·이용에 동의합니다.
                <span class="consent-d">수집 항목: 법인명, 담당자명, 연락처, 이메일, 차량 종류, 문의 내용 ·
                  이용 목적: 상담 회신 · 보유 기간: 상담 종료 후 1년.
                  동의를 거부하실 수 있으며, 이 경우 전화로 상담해 주세요.</span>
              </label>
            </div>

            <p class="form-err" id="formError" role="alert" hidden></p>

            <button type="submit" class="btn btn-ink btn-lg btn-full" id="submitBtn">상담 요청</button>
          </form>

          <div class="form-done" id="formDone" hidden role="status">
            <p class="done-t">접수됐습니다. 확인하는 대로 연락드리겠습니다.</p>
            <p class="done-d">급하시면 <a href="{TEL_L}">{TEL_D}</a>으로 전화 주세요.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="sec sec-paper">
    <div class="wrap">
      <h2 class="h2">견적서·사양서를 보내시면 더 빠릅니다</h2>
      <div class="two">
        <div>
          <p class="lead">이미 다른 곳에서 받으신 리스·렌트·할부 견적서나
            화물차 특장 사양서가 있으면 <a class="tlink" href="mailto:{MAIL}">{MAIL}</a>로 보내 주세요.
            PDF, 사진, 엑셀 어떤 형식이든 됩니다.</p>
          <p class="lead">같은 차종·같은 기간으로 조건을 맞춰 비교해야 의미가 있기 때문에,
            기준이 되는 견적이 있으면 훨씬 정확한 답을 드릴 수 있습니다.</p>
          <p class="lead">메일 제목에 <strong>법인명과 연락처</strong>만 함께 적어 주세요.</p>
        </div>
        <div class="note-card">
          <h3>착수 시 준비해 주실 것</h3>
          <ul class="ck">
            <li>운용 차량 목록 — 차종, 대수, 금융사, 계약 형태</li>
            <li>차량별 만기일과 보험 갱신일 — 아시는 범위 내에서</li>
            <li>기존 견적서 — 있는 경우</li>
            <li>신규 도입·교체 계획</li>
          </ul>
          <p class="note-more">모르셔도 됩니다. 저희가 확인해 드리는 것부터 시작해도 늦지 않습니다.</p>
        </div>
      </div>
    </div>
  </section>
"""

# ==========================================================================
# 자주 묻는 질문
# ==========================================================================
FAQ_GROUPS = [
    ("비용", [
        ("차량관리 대행 비용이 얼마인가요?",
         "받지 않습니다. 플릿케어의 수익은 제조사와 캐피탈사 등 공급자 측에서 발생합니다. "
         "그래서 고객사는 비용 부담 없이 고객 측 대리인을 두는 구조가 됩니다."),
        ("운용리스 차량 보험을 플릿케어에 위탁하면 비용이 드나요?",
         "무상입니다. 보험 비교와 가입, 갱신 서류 대행까지 별도 수수료를 받지 않습니다. "
         "보험료 자체는 보험사에 납부하시는 금액이고, 저희가 중간에서 얹는 금액은 없습니다. "
         "보험 계약은 제휴 보험대리점을 통해 체결되며, 플릿케어는 차량대장과 갱신 일정을 붙여 관리하는 역할입니다."),
        ("그러면 어디서 수익이 나나요?",
         "제조사와 캐피탈사 등 공급자 측에서 나옵니다. 고객사에서 받지 않습니다. "
         "관리를 잘해서 다음 차량도 저희를 통해 진행하시는 것이 저희에게도 이득인 구조라, "
         "계약만 성사시키고 연락이 끊기지 않습니다."),
        ("만기 손익 분석 리포트도 비용이 드나요?",
         "받지 않습니다. 만기 도래 전에 먼저 연락드려 리포트를 드립니다."),
        ("숨은 비용이 있나요?",
         "정비 수리비, 보험료, 특장 제작비, 과태료처럼 실제로 외부에 지급되는 금액은 고객사 부담입니다. "
         "다만 플릿케어가 그 위에 수수료를 얹지 않습니다."),
    ]),
    ("화물·특장", [
        ("화물차 외주장착 비용도 리스 이용금액에 합산 가능한가요?",
         "가능합니다. 다만 대부분의 리스사는 특장비를 리스료에 넣어주지 않고 따로 현금으로 부담하라고 합니다. "
         "특장물의 잔존가치를 잡기 어렵다는 이유입니다. "
         "플릿케어는 금융사 담당자와 직접 협의해 특장 비용까지 리스료에 포함시킵니다. "
         "목돈이 한 번에 나가지 않아 초기 자금 부담이 줄어듭니다. "
         "사양과 견적을 보내 주시면 어느 금융사에서 어떤 조건으로 가능한지 확인해 드립니다."),
        ("만기에 반납할 때 특장물을 원상복구해야 하나요?",
         "금융사에 따라 다릅니다. 원상복구를 요구하는 곳이 많은데, 붙여둔 윙바디나 리프트를 떼어내고 "
         "원래 상태로 되돌려 반납하라는 조건입니다. 탈거 비용이 또 들고 떼어낸 특장물은 쓸 데가 없습니다. "
         "플릿케어는 계약 전에 반납 조건을 확인하고 원상복구 요구가 없는 금융사로 진행합니다. "
         "계약할 때 정해지는 조건이라 출고 후에는 바꾸기 어렵습니다. 시작할 때 잡아야 합니다."),
        ("캐피탈사에서 특장 때문에 거절당했는데 가능할까요?",
         "조건을 알려주세요. 특장 차량은 잔가 산정이 어려워 승인을 꺼리는 금융사가 많지만, "
         "진행 경험이 있는 곳은 다릅니다. 한 곳에서 막혔다고 끝이 아닙니다."),
        ("어떤 장착물까지 진행되나요?",
         "윙바디와 탑차, 탑 사이즈 제작, 내장탑·냉동탑, 파워게이트 리프트, 크레인, "
         "차량 하부보강과 차바닥, 도색·래핑 등을 진행합니다. "
         "상용차 2.5톤 이상은 별도 협의로 진행합니다. "
         "목록에 없는 사양도 사양서를 보내 주시면 확인해 드립니다."),
        ("구조변경과 등록도 대신 해주시나요?",
         "제작사 섭외부터 사양 결정, 구조변경 승인, 등록 절차까지 함께 진행합니다."),
    ]),
    ("보험", [
        ("보험 갱신 시기를 놓칠까 걱정됩니다.",
         "갱신 시점이 오기 전에 저희가 먼저 알려드립니다. 차량별 갱신일을 대장으로 관리하기 때문에 "
         "차량 수가 늘어도 누락되지 않습니다. 서류 작업도 대행합니다."),
        ("사고 처리도 대신 해주시나요?",
         "아닙니다. 사고 접수와 대차 수배, 보상 협의는 가입하신 보험사와 직접 진행하셔야 합니다. "
         "플릿케어가 맡는 것은 보험 가입과 갱신 관리까지입니다. "
         "다만 차량별로 어느 보험사에 어떤 조건으로 가입돼 있는지 대장에 정리돼 있어, "
         "사고가 났을 때 어디로 연락해야 하는지는 바로 확인해 드릴 수 있습니다."),
        ("계약 중에 보험 조건을 바꾸려면 어떻게 하나요?",
         "플릿케어로 요청하시면 됩니다. 운전자 연령 변경, 대물 한도 조정, 자차 조건 변경처럼 "
         "계약 중에 손봐야 할 일이 생기면 저희가 대리점을 통해 처리합니다. "
         "보험사에 직접 연락하실 필요가 없습니다."),
        ("지금 다른 곳에서 가입한 보험도 맡길 수 있나요?",
         "가능합니다. 현재 증권 정보를 주시면 갱신일을 대장에 올려 관리하고, "
         "갱신 시점에 조건을 비교해 드립니다."),
    ]),
    ("만기·교체", [
        ("만기 시 반납과 인수 후 매각 중 무엇이 유리한지 어떻게 판가름하나요?",
         "계약상 잔존가치와 중고차 실거래 시세를 비교합니다. 시세가 잔존가치보다 높으면 "
         "인수 후 매각이 유리하고, 반대면 반납이 낫습니다. 여기에 반납 시 초과 주행·손상 감가와 "
         "매각까지의 비용을 더해 최종 숫자를 냅니다. 차종과 시기에 따라 매번 다르기 때문에 "
         "그때그때 계산해 리포트로 드립니다."),
        ("신차는 언제 발주해야 하나요?",
         "차량은 계약한다고 바로 나오지 않고 생산과 출고에 기간이 걸립니다. 특장 작업이 붙으면 제작 기간이 더해집니다. "
         "그래서 만기일에서 거꾸로 계산해 발주 시점을 정합니다. 차종별 납기를 확인하고 계약·심사 기간을 더해 "
         "언제 움직여야 하는지 저희가 계산해 미리 알려드리고, 고객사와 소통하며 만기일에 맞춰 차량을 대드립니다."),
        ("납기가 밀리면 어떻게 되나요?",
         "기존 계약 연장 등으로 공백을 메우는 방법을 같이 정합니다. 미리 알고 대응하면 대부분 해결됩니다."),
    ]),
    ("관리 범위", [
        ("리스나 렌탈 말고 할부로도 진행할 수 있나요?",
         "가능합니다. 다만 저희가 주로 다루는 것은 리스와 렌탈입니다. "
         "할부는 출고 시점부터 차량이 법인 명의가 되고 자산으로 잡히기 때문에, "
         "비용 처리 방식과 부채비율에 미치는 영향이 리스·렌탈과 다릅니다. "
         "어느 쪽이 유리한지는 회사의 재무 상황과 차량 용도에 따라 갈리므로, "
         "같은 차·같은 기간 기준으로 세 방식을 나란히 계산해 비교표로 드립니다. "
         "금융사 선택과 심사 진행은 리스·렌탈과 똑같이 대행합니다."),
        ("지금 다른 캐피탈사와 계약 중인 차량도 맡길 수 있나요?",
         "가능합니다. 금융사가 어디든 대장에 올려 함께 관리합니다. "
         "차량번호와 계약사, 만기일만 알려주시면 정리해 드립니다. "
         "여러 금융사에 흩어진 차량을 한 곳에서 보는 것이 저희의 주된 역할입니다."),
        ("몇 대부터 맡길 수 있나요?",
         "대수 기준을 두지 않습니다. 대수가 적어도 만기·보험·정비는 똑같이 발생합니다."),
        ("차를 새로 뽑을 계획이 없어도 관리만 맡길 수 있나요?",
         "상담해 주세요. 현재 차량 구성과 만기 분포를 먼저 정리해 드리는 것부터 시작합니다."),
        ("현장관리 서비스는 무엇인가요?",
         "3개월마다 사업장을 직접 방문하는 서비스입니다. "
         "현장 방문 → 현장 리포트 작성 → 본사 협의 → 개선 실행·관리 네 단계로 돌아가고, "
         "개선 결과는 다음 분기 방문에서 확인합니다. "
         "리포트에는 차량별 상태와 주행거리, 사고·정비 이력, 보험 갱신·만기 캘린더, "
         "현장 요청사항, 개선 권고와 전 분기 조치 결과가 담깁니다. "
         "계약 후 현장에 오는 에이전트는 저희뿐입니다. 이 서비스도 별도 비용을 받지 않습니다."),
        ("정비도 관리해 주시나요?",
         "정비 접수를 저희가 대신 받지는 않습니다. 대신 계약할 때 정비가 포함된 상품으로 갈지 정해 드립니다. "
         "렌트·리스 상품 중에는 정기 점검과 소모품 교체가 포함된 구성이 있어서, "
         "정비까지 신경 쓰기 어려우시면 포함형으로 계약하시는 편이 낫습니다. "
         "반대로 운행이 적은 차량은 그때그때 실비로 처리하는 게 쌉니다. "
         "차량 용도와 주행거리를 보고 어느 쪽이 유리한지 같이 판단해 드립니다."),
        ("운행기록부도 대신 써주나요?",
         "쓰지 않습니다. 양식을 드리고, 작성 대상 차량을 안내하고, 결산 시즌에 맞춰 알려드리는 데까지입니다. "
         "운행 사실은 실제 운전자만 알 수 있어 대행 작성은 하지 않습니다. "
         "운행 기록 자체를 자동화하고 싶으시면 FMS 업체를 비교해 제안해 드립니다. 업체마다 구성 항목이 달라서 필요한 기능을 먼저 정리하는 편이 좋습니다."),
        ("차량 정보를 넘겨도 안전한가요?",
         "차량관리 목적 외에는 사용하지 않습니다. 상담 과정에서 받은 개인정보는 "
         "상담 종료 후 1년까지만 보관하고 파기합니다."),
    ]),
]


def faq_body():
    out = ""
    for gi, (group, qs) in enumerate(FAQ_GROUPS):
        items = ""
        for qi, (q, a) in enumerate(qs):
            op = " open" if (gi == 0 and qi == 0) else ""
            items += f"""
        <details class="qa"{op}>
          <summary>{q}</summary>
          <div class="qa-a"><p>{a}</p></div>
        </details>
"""
        cls = "sec sec-paper" if gi % 2 else "sec"
        out += f"""
  <section class="{cls}">
    <div class="wrap">
      <h2 class="h2">{group}</h2>
      <div class="qalist">{items}      </div>
    </div>
  </section>
"""
    return page_head(
        "자주 묻는 질문",
        "비용, 화물·특장 승인, 보험 관리 범위, 만기 교체에 대해 가장 많이 받는 질문입니다."
    ) + out + f"""
  <section class="sec">
    <div class="wrap">
      <div class="askbox">
        <h2>여기 없는 질문이라면</h2>
        <p>차량 상황은 회사마다 달라서 답이 하나로 정해지지 않는 경우가 많습니다.
          전화 주시면 그 자리에서 확인해 드립니다.</p>
        <div class="askbox-btns">
          <a class="btn btn-ink btn-lg" href="{TEL_L}">{TEL_D}</a>
          <a class="btn btn-line btn-lg" href="/contact.html">상담·견적 문의</a>
        </div>
      </div>
    </div>
  </section>
"""


# ==========================================================================
# 관리자 편집 표시
# ==========================================================================
EDIT_TAGS = ("h1", "h2", "h3", "p", "li", "dt", "dd", "summary", "td", "th", "caption")

BLOCK_INSIDE = re.compile(
    r"<\s*(p|h1|h2|h3|ul|ol|dl|div|article|section|details|form|img|button|"
    r"hr|input|label|textarea|svg|a|select|table|thead|tbody|tr)\b", re.I)

TAG_LABEL = {
    "h1": "제목", "h2": "제목", "h3": "소제목", "p": "본문",
    "li": "목록", "dt": "항목명", "dd": "항목 내용", "summary": "질문",
    "td": "표 내용", "th": "표 머리", "caption": "표 설명",
}


def common_ranges(html):
    out = []
    for pat in (r"<footer\b.*?</footer>",
                r'<section class="cta">.*?</section>',
                r'<div class="mbar">.*?</div>'):
        for m in re.finditer(pat, html, re.S | re.I):
            out.append((m.start(), m.end()))
    return out


def mark_editable(html, page_id, seen):
    commons = common_ranges(html)
    entries = []
    counts = {}

    def in_common(pos):
        return any(a <= pos < b for a, b in commons)

    pattern = re.compile(
        r"<(" + "|".join(EDIT_TAGS) + r")(\s[^>]*)?>(.*?)</\1>", re.S | re.I)

    def repl(m):
        tag, attrs, inner = m.group(1).lower(), m.group(2) or "", m.group(3)
        text = re.sub(r"\s+", " ", inner).strip()
        if not text or "data-edit" in inner:
            return m.group(0)
        if BLOCK_INSIDE.search(inner):
            return "<%s%s>%s</%s>" % (tag, attrs, pattern.sub(repl, inner), tag)

        owner = "common" if in_common(m.start()) else page_id
        h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
        base = owner + ":" + h
        n = counts.get(base, 0)
        counts[base] = n + 1
        key = base if n == 0 else "%s-%d" % (base, n)

        if key not in seen:
            seen[key] = True
            entries.append({"key": key, "owner": owner, "tag": tag,
                            "label": TAG_LABEL.get(tag, "본문"), "text": text})
        return '<%s%s><span class="ed" data-edit="%s">%s</span></%s>' % (
            tag, attrs, key, text, tag)

    return pattern.sub(repl, html), entries


# ==========================================================================
PAGES = [
    ("index.html", "플릿케어 — 법인 전용 플릿 에이전트 | 도입·특장·보험·만기 통합 케어",
     "분기별 현장관리, 화물 특장 리스, 금융 비교·심사 대행, 운용리스 보험, 만기 손익 분석, 비용절감까지 "
     "전담자 한 명이 맡습니다. "
     "관리 대행 비용 없음. 02-6925-0516", None, None, "home"),

    ("about.html", "회사소개 — 플릿케어",
     "법인 차량 리스·렌탈·할부 중개. 공급자 중심의 시장에서 고객 중심의 플릿 에이전트로. "
     "리스사 출신 노하우, 보험대리점 연계 관리, 중고차 시세 기반 만기 분석.", "about.html", None, ""),

    ("service.html", "서비스 안내 — 법인 렌트·리스·할부, 현장관리, FMS 비교 | 플릿케어",
     "여러 캐피탈사의 리스·렌탈·할부 조건을 종합 비교해 법인에 맞는 방식을 찾아 드립니다. "
     "분기별 현장관리 서비스, 정비 포함 상품 연결, FMS 업체 비교·제안, 법인 비용절감 컨설팅.", "service.html", None, ""),

    ("truck.html", "화물·특장 솔루션 — 외주장착 승인 대행 | 플릿케어",
     "윙바디, 탑차, 파워게이트, 리프트 등 화물차 외주장착 승인 대행. "
     "특장 비용을 리스료에 포함시키고, 원상복구 없이 반납할 수 있는 조건으로 계약합니다.", "truck.html", None, ""),

    ("care.html", "보험·만기 케어 — 운용리스 보험 통합 관리 | 플릿케어",
     "운용리스 보험 비교·가입·갱신 관리와 만기 손익 분석 리포트. "
     "반납과 인수 후 매각을 숫자로 비교하고 매각처까지 연결해 드립니다.", "care.html", None, ""),

    ("contact.html", "상담·견적 문의 — 플릿케어",
     "법인명과 연락처만 남겨 주시면 됩니다. 기존에 받으신 견적서·사양서를 보내시면 더 빠릅니다. "
     "전화 02-6925-0516, 평일 09:00–18:00.", "contact.html", None, ""),

    ("faq.html", "자주 묻는 질문 — 플릿케어",
     "특장비 리스료 포함, 원상복구 없는 반납, 관리 대행 비용, 운용리스 보험 관리 범위, "
     "만기 반납과 인수 후 매각 판단 기준에 대한 답변.", None, None, ""),
]

BODIES = {
    "index.html": INDEX,
    "about.html": ABOUT,
    "service.html": SERVICE,
    "truck.html": TRUCK,
    "care.html": CARE,
    "contact.html": CONTACT,
}

PAGE_TITLES = {
    "index.html": "홈",
    "about.html": "회사소개",
    "service.html": "서비스 안내",
    "truck.html": "화물·특장 솔루션",
    "care.html": "보험·만기 케어",
    "contact.html": "상담·견적 문의",
    "faq.html": "자주 묻는 질문",
}

os.makedirs(OUT, exist_ok=True)
os.makedirs(OUT + "admin", exist_ok=True)

# 구조 개편으로 없어진 페이지 정리
for old in ("needs.html", "process.html", "partners.html"):
    p = OUT + old
    if os.path.exists(p):
        os.remove(p)
        print("removed", old, "(worker.js 에서 301 리다이렉트 처리)")

seen_keys = {}
common_items = []
page_blocks = []

for fname, title, desc, active, _body, cls in PAGES:
    body = faq_body() if fname == "faq.html" else BODIES[fname]

    html = head(title, desc, fname, cls) + header(active) + \
        '\n<main id="main">\n' + body + '\n</main>\n' + footer()

    html = re.sub(r'href="/([a-z]+)\.html(#[^"]*)?"',
                  lambda m: 'href="/%s%s"' % (m.group(1), m.group(2) or ""), html)

    page_id = fname.replace(".html", "")
    html, entries = mark_editable(html, page_id, seen_keys)

    io.open(OUT + fname, "w", encoding="utf-8", newline="\n").write(html)

    mine = [e for e in entries if e["owner"] == page_id]
    common_items += [e for e in entries if e["owner"] == "common"]
    page_blocks.append({"id": page_id, "title": PAGE_TITLES[fname],
                        "file": fname, "items": mine})
    print("wrote %-14s %6d bytes  편집 가능 %d곳" % (fname, len(html), len(mine)))

blocks = [{"id": "common", "title": "공통 (모든 페이지)", "file": "",
           "items": common_items}] + page_blocks

io.open(OUT + "admin/defaults.json", "w", encoding="utf-8", newline="\n").write(
    json.dumps({"pages": blocks}, ensure_ascii=False, indent=1))
print("wrote admin/defaults.json  공통 %d곳 / 전체 %d곳"
      % (len(common_items), sum(len(b["items"]) for b in blocks)))

urls = ""
for fname, *_ in PAGES:
    loc = SITE + "/" + slug(fname)
    pri = "1.0" if fname == "index.html" else "0.8"
    urls += f"""  <url>
    <loc>{loc}</loc>
    <lastmod>2026-09-11</lastmod>
    <changefreq>monthly</changefreq>
    <priority>{pri}</priority>
  </url>
"""
io.open(OUT + "sitemap.xml", "w", encoding="utf-8", newline="\n").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
print("wrote sitemap.xml")

io.open(OUT + "robots.txt", "w", encoding="utf-8", newline="\n").write(
    "User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /api/\n\n"
    "Sitemap: https://fleetcare.co.kr/sitemap.xml\n")
print("wrote robots.txt")
