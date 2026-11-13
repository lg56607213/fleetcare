/* 에이스렌트 견적기 가격표 → site/truck-data.js 변환기
 *
 * 사용법 (이 저장소 폴더에서):
 *   node tools/acerent-to-data.js                 차량 전부
 *   node tools/acerent-to-data.js --trucks-only   세금구분이 '화물'인 차만
 *   node tools/acerent-to-data.js "C:\경로\quote-data.json"
 *
 * 원본: acerent 저장소의 src/data/quote-data.json
 *   T: [제조사, 구분, 차종, 라인업, 트림, 기본가, 배기량, 세금구분, 정액세, 잔가그룹, 옵션[[이름,가격]]]
 *   C: [차종, 외장|내장, 색상명, 추가금]
 *
 * 결과: site/truck-data.js
 *   TRUCK_DATA   제조사 > 구분 > 차종 > 라인업 > 트림 = { price, opts: [{n, p}] }
 *   TRUCK_COLORS 제조사 > 구분 > 차종 = { ext: [{n, p}], int: [{n, p}] }
 *
 * mytruck 의 같은 이름 도구와 형식이 같다. 다른 점은 두 가지다.
 *   - 차종 이름을 줄이지 않는다 ('포터II 카고' 그대로)
 *   - 기본값이 차량 전부다 (mytruck 은 화물만)
 */
const fs = require('fs');
const os = require('os');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'site', 'truck-data.js');

const args = process.argv.slice(2);
const TRUCKS_ONLY = args.includes('--trucks-only');
const given = args.find(a => !a.startsWith('--'));

// acerent 폴더는 이 저장소 옆이나 사용자 홈 폴더에서 찾는다
const candidates = given ? [given] : [
  path.join(ROOT, '..', 'acerent', 'src', 'data', 'quote-data.json'),
  path.join(os.homedir(), 'acerent', 'src', 'data', 'quote-data.json'),
];
const SRC = candidates.find(p => fs.existsSync(p));
if (!SRC) {
  console.error('원본 가격표를 찾지 못했습니다. 찾아본 곳:');
  candidates.forEach(p => console.error('  ' + p));
  console.error('acerent 저장소를 받아 두거나, quote-data.json 경로를 직접 적어 주세요.');
  process.exit(1);
}
const DATA = JSON.parse(fs.readFileSync(SRC, 'utf8'));

const isTruck = t => t[7] === '화물';
const rows = DATA.T.filter(t => !TRUCKS_ONLY || isTruck(t));

// 화물차가 들어 있는 구분을 앞에 둔다 (화물·특장이 이 사이트의 주력이다)
const truckCats = new Set(rows.filter(isTruck).map(t => t[0] + '|' + t[1]));
const order = new Map();
rows.forEach(t => {
  const k = t[0] + '|' + t[1];
  if (!order.has(k)) order.set(k, order.size);
});
const rank = t => (truckCats.has(t[0] + '|' + t[1]) ? 0 : 1000) + order.get(t[0] + '|' + t[1]);
const makers = [...new Set(rows.map(t => t[0]))];
const sorted = rows
  .map((t, i) => ({ t, i }))
  .sort((a, b) => makers.indexOf(a.t[0]) - makers.indexOf(b.t[0]) || rank(a.t) - rank(b.t) || a.i - b.i)
  .map(x => x.t);

const data = {}, models = new Set(), warn = [];
let count = 0;
for (const t of sorted) {
  const [mk, cat, model, line, trim, price] = t;
  const lines = ((data[mk] ||= {})[cat] ||= {})[model] ||= {};
  const trims = lines[line] ||= {};
  const where = [mk, cat, model, line, trim].join(' > ');
  if (trims[trim]) warn.push('중복 트림(뒤의 값 사용): ' + where);
  if (!price) warn.push('차량가 없음: ' + where);
  trims[trim] = { price, opts: (t[10] || []).map(([n, p]) => ({ n, p })) };
  models.add([mk, cat, model].join('|'));
  count++;
}

/* 색상: 차종 이름으로 찾는다. 특장차는 색상표가 없으면 같은 차의 카고 색상을 쓴다 (캡이 같다). */
const colorsOf = model => {
  const hit = DATA.C.filter(c => c[0] === model);
  if (hit.length || !/특장차$/.test(model)) return hit;
  return DATA.C.filter(c => c[0] === model.replace(/특장차$/, '카고'));
};
const colors = {};
for (const key of models) {
  const [mk, cat, model] = key.split('|');
  const hit = colorsOf(model);
  if (!hit.length) continue;
  const pick = side => hit.filter(c => c[1] === side).map(c => ({ n: c[2], p: c[3] || 0 }));
  ((colors[mk] ||= {})[cat] ||= {})[model] = { ext: pick('외장'), int: pick('내장') };
}

const head = `/* 견적 요청 - 차량 데이터 (직접 고치지 않는다)
 * 원본: 에이스렌트 견적기 가격표 (acerent/src/data/quote-data.json) 자동 변환 — tools/acerent-to-data.js
 * 구조: TRUCK_DATA   제조사 > 구분 > 차종 > 라인업 > 트림 = { price: 차량가(원), opts: [{n:옵션명, p:옵션가}] }
 *       TRUCK_COLORS 제조사 > 구분 > 차종 = { ext: 외장 [{n, p}], int: 내장 [{n, p}] }
 */
`;
fs.writeFileSync(OUT, head
  + 'const TRUCK_DATA = ' + JSON.stringify(data) + ';\n\n'
  + 'const TRUCK_COLORS = ' + JSON.stringify(colors) + ';\n');

warn.forEach(w => console.warn('[주의] ' + w));
console.log(`완료: 트림 ${count}개${TRUCKS_ONLY ? ' (화물만)' : ''} → ${path.relative(ROOT, OUT)}`);
console.log('원본: ' + SRC);
