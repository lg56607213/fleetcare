# FleetCare 홈페이지

`fleetcare.co.kr` — 순수 HTML/CSS/vanilla JS 정적 사이트. 빌드 과정 없음.
이 폴더의 파일을 그대로 Cloudflare Pages에 올리면 동작합니다.

```
index.html      홈                    -> fleetcare.co.kr/
about.html      회사소개               -> /about
needs.html      고객 Needs             -> /needs
service.html    제공 내용              -> /service
process.html    진행 절차              -> /process
partners.html   제휴사                 -> /partners
faq.html        자주 묻는 질문          -> /faq
contact.html    상담 요청              -> /contact

admin.html      문구 수정 관리자        -> /admin
admin/defaults.json   원래 문구 목록 (자동 생성, 직접 고치지 말 것)
_worker.js      관리자 저장분을 페이지에 끼워 넣는 코드

assets/  logo.svg  logo-white.svg  symbol.svg  favicon.svg  og-image.png
css/     style.css
js/      config.js  main.js
sitemap.xml
robots.txt
```

주소에 `.html` 이 붙지 않습니다. Cloudflare Pages 가 확장자를 떼고 서비스하므로
사이트 안의 링크와 canonical, sitemap 을 모두 `/about` 형태로 맞춰 두었습니다.

로고 SVG 4종은 `fleetcare-logo.pdf`의 벡터 경로를 그대로 추출한 것이라
원본과 좌표가 동일합니다. favicon은 심볼의 원형 부분만 잘랐습니다.

---

## 배포 전에 반드시 채울 것

### 1. EmailJS 키 — `js/config.js`

```js
window.EMAILJS_CONFIG = {
  publicKey:  "...",   // Account > General > Public Key
  serviceId:  "...",   // Email Services > Service ID
  templateId: "...",   // Email Templates > Template ID
};
```

템플릿에서 쓸 변수: `{{company}}` `{{name}}` `{{phone}}` `{{email}}` `{{message}}`

**Account > Security > Allowed Domains 를 `fleetcare.co.kr` 로 제한할 것.**
Public Key는 브라우저에 노출되는 값이라 도메인 제한이 유일한 방어선입니다.

키를 채우지 않은 상태에서 폼을 제출하면
"전송에 실패했습니다 — 02-6925-0516으로 전화 주세요" 안내가 뜹니다.
전화 유입은 끊기지 않으니 급하면 이 상태로도 배포할 수 있습니다.

### 2. 제휴사 — `partners.html`

- 금융사: `[금융사명]` 8칸
- 협력 네트워크: 정비 / 특장 제작사 / 보험 / GPS 관제 각 `[업체명]` 3칸

이것도 관리자 페이지의 "제휴사" 탭에서 칸마다 이름을 넣으시면 됩니다.
칸 수를 늘리거나 줄이는 건 HTML 수정이 필요하니 말씀해 주세요.

### 3. 확인이 필요한 서술 (사실 확인 후 확정)

사이트에 이미 문장으로 들어가 있는 내용입니다. 맞지 않으면 고쳐야 합니다.
해당 위치에 `<!-- 확인 필요 -->` 주석을 달아 두었습니다.

| 내용 | 위치 |
|---|---|
| "차량 계약이 성사되면 금융사로부터 중개 수수료를 받는다" — 수익 구조 설명 | `about.html`, `service.html`, `faq.html`, `index.html` |
| "GPS 관제 시스템을 직접 공급하지는 않는다" — 직접 공급/설치까지 하신다면 제공 내용에서 '직접 처리'로 옮겨야 함 | `service.html`, `needs.html`, `faq.html` |
| "대수 기준을 두지 않는다" | `faq.html` |
| "정비 수리비·보험료·특장 제작비 등은 고객사 부담, 중간 수수료 없음" | `about.html`, `service.html`, `faq.html` |
| 평일 09:00–18:00 상담 시간 | `contact.html`, 각 페이지 상담 영역 |

---

## 문구 수정 관리자 페이지

`fleetcare.co.kr/admin` 에서 비밀번호로 로그인하면 홈페이지 글씨를 직접 고칠 수 있습니다.
저장하면 곧바로 반영됩니다. 8개 페이지에서 총 **353곳**을 고칠 수 있습니다.

- 탭이 페이지별로 나뉘어 있고, 맨 앞 **공통** 탭에는 모든 페이지에 똑같이 들어가는
  푸터 회사 정보와 하단 상담 문구가 모여 있습니다. 여기서 한 번 고치면 8개 페이지에 다 반영됩니다.
  (사업자등록번호도 여기서 넣으시면 됩니다)
- 고친 항목은 초록 테두리가 생기고 아래에 원래 문구가 표시됩니다.
  **되돌리기**를 누르면 원래대로 돌아갑니다.
- 줄을 바꾸려면 그냥 엔터를 치면 됩니다.
- 글씨만 바뀝니다. 디자인, 사진, 메뉴 구성, 전화번호 링크는 이 화면에서 바뀌지 않습니다.
  (전화번호·이메일은 링크와 함께 바꿔야 해서 제외했습니다)

### 동작 방식

수정본은 Cloudflare KV 에 저장되고, `_worker.js` 가 **서버에서** 페이지에 끼워 넣습니다.
브라우저에서 바꾸는 게 아니라서 검색엔진에도 수정한 문구가 그대로 보입니다.

### 설정 (한 번만, 약 10분)

1. Cloudflare 대시보드 > **Storage & Databases > KV** > Create namespace
   - 이름: `fleetcare-content` (아무 이름이나 상관없음)
2. **Workers & Pages > (프로젝트) > Settings > Bindings > Add > KV namespace**
   - Variable name: **`CONTENT`** ← 이 이름이어야 합니다
   - KV namespace: 방금 만든 것
3. 같은 Settings 화면 > **Variables and Secrets > Add**
   - Type: **Secret**
   - Name: **`ADMIN_PASSWORD`**
   - Value: 쓰실 비밀번호 (길게. 이게 뚫리면 홈페이지 문구가 바뀝니다)
4. 저장하고 **재배포**

설정 전에는 `/admin` 에 들어가도 저장이 안 되고 안내 문구가 뜹니다.
KV나 비밀번호가 없어도 **홈페이지 자체는 원래 문구로 정상 동작**합니다.

### 비밀번호를 바꾸려면

Settings 에서 `ADMIN_PASSWORD` 값을 바꾸고 재배포하면 됩니다.
바꾸면 기존 로그인 세션은 전부 끊어집니다. (로그인은 8시간 유지됩니다)

### 문구를 제가 새로 만들면

페이지 내용을 새로 손보면 `admin/defaults.json` 이 다시 만들어집니다.
문구가 바뀐 항목은 관리자에서 고쳐둔 내용이 사라지고 새 문구가 들어갑니다.
안 건드린 항목의 수정본은 그대로 남습니다. (순서를 바꾸거나 섹션을 추가해도 안 깨집니다)

---

## Cloudflare Pages 배포

1. Pages > Create a project > **Direct Upload** — 이 폴더 전체를 업로드
   (빌드 명령·출력 디렉터리 설정 없음)
   - `_worker.js` 가 폴더 맨 위에 있어야 관리자 저장분이 반영됩니다. 빼먹지 마세요.
   - **`.wrangler` 폴더가 있으면 지우고 올리세요.** 로컬 테스트용 찌꺼기입니다.
2. Custom domains 에 `fleetcare.co.kr` 와 `www.fleetcare.co.kr` 둘 다 연결
3. **Rules > Redirect Rules** 로 하나를 정본으로 통일 (301)
   - 예: `www.fleetcare.co.kr/*` → `https://fleetcare.co.kr/$1` (301)
   - 각 페이지의 `canonical`·`sitemap.xml`·OG URL이 모두 **apex(`fleetcare.co.kr`)** 기준입니다.
     www를 정본으로 바꾸려면 8개 파일과 sitemap을 같이 고쳐야 합니다.
4. SSL/TLS > Edge Certificates > **Always Use HTTPS** 켜기
5. 배포 후 Google Search Console에 `https://fleetcare.co.kr/sitemap.xml` 제출

## 로컬에서 확인

```
python -m http.server 8000
```

절대 경로(`/css/style.css`)를 쓰므로 HTML 파일을 직접 열면 스타일이 깨집니다.
반드시 서버로 띄워서 확인하세요.

단, 이 방법으로는 `/admin` 이 동작하지 않습니다 (`_worker.js` 가 실행되지 않아서).
관리자 화면까지 로컬에서 보려면 Node 설치 후:

```
npx wrangler pages dev . --kv CONTENT --binding ADMIN_PASSWORD=원하는비밀번호
```

`http://127.0.0.1:8788` 로 열립니다. 여기서 저장한 내용은 `.wrangler` 폴더에만
쌓이는 로컬 데이터라 실제 사이트와 무관하며, 업로드 전에 지우면 됩니다.

---

## 구조에 대해

### 헤더와 푸터는 8개 파일에 복제돼 있습니다

빌드 도구를 쓰지 않기로 했기 때문에, 메뉴·전화번호·회사 정보를 바꾸려면
8개 HTML을 모두 고쳐야 합니다. 한 곳만 고치고 넘어가면 페이지마다 달라집니다.
바꿀 일이 생기면 편집기의 "전체 폴더에서 바꾸기"를 쓰세요.

현재 메뉴에 활성 표시(`aria-current="page"`)가 붙는 규칙:
각 파일의 헤더에서 자기 자신에 해당하는 `<a>`에만 이 속성이 있습니다.
페이지를 추가할 때 잊지 마세요.

### 자주 묻는 질문은 `<details>` 태그입니다

JS 없이 브라우저 기본 기능으로 열고 닫힙니다. 질문을 추가하려면
`faq.html`에서 아래 블록을 복사해 붙이면 됩니다.

```html
<details class="qa">
  <summary>질문</summary>
  <div class="qa-a"><p>답변</p></div>
</details>
```

인쇄할 때는 접힌 답변도 자동으로 펼쳐져서 나옵니다.

---

## 손댈 때 알아둘 것

- **초록(`--green`)은 면적을 넓히지 말 것.** 버튼, 밑줄, 체크 표시, 강조 요소에만 씁니다.
  넓게 깔면 친환경 업체로 읽힙니다.
- **ERP·법인대출은 이 사이트에 넣지 않습니다.** 링크도 언급도 금지.
  방문자에게 다른 사업이 보이면 전문성이 흐려지고, 대출이 노출되면 대부업으로 오인됩니다.
- 헤드라인에 "최저가·다이렉트·비교견적"을 쓰지 않습니다. 가격은 상담에서 꺼내는 카드입니다.
- **관리 대행 비용을 받지 않는다는 점**이 이 사이트의 가장 강한 무기입니다.
  홈 히어로, 홈 3번째 카드, 회사소개, 제공 내용, FAQ 첫 질문에 반복해서 배치돼 있습니다.
  줄이지 마세요. 대신 "그럼 어디서 돈을 버느냐"는 의심을 반드시 같이 풀어줘야 합니다.
- **못 하는 일을 적어둔 문장을 지우지 마세요.**
  운행기록부 대행 작성, 보험 처리 결과 보증, GPS 시스템 직접 공급 —
  이 세 가지는 "안 한다"고 명시돼 있습니다. 범위가 분명한 편이 계약 후 분쟁을 줄입니다.
- **개인 이력(근무 연차, 관리 대수)은 싣지 않습니다.** 한 사람이 몇 년 일했고 몇 대를
  관리했다는 식의 서술은 회사를 작아 보이게 만들어 오히려 신뢰를 깎습니다.
  신뢰는 복수 금융사 거래, 통합 장부, 범위를 먼저 밝히는 방식으로 보여줍니다.
- 상세 견적 폼을 붙이지 않습니다. 조건이 많은 폼은 견적 비교 사이트로 오인됩니다.
- 모바일 하단 고정 바의 전화 버튼은 항상 노출돼야 합니다.
- HTML 안의 `<span class="ed" data-edit="...">` 는 관리자 페이지가 고칠 자리를 표시한 것입니다.
  **지우지 마세요.** 지우면 그 문장은 관리자에서 못 고치게 됩니다.
