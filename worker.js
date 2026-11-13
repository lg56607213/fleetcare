/* ==========================================================================
   FleetCare — Cloudflare Pages 앞단 (Advanced mode)

   1) 관리자 페이지에서 저장한 문구를 KV에서 읽어 HTML에 끼워 넣는다
      (브라우저가 아니라 서버에서 바꿔치기하므로 검색엔진에도 수정본이 보인다)
   2) /api/* 로 로그인·저장을 처리한다

   Cloudflare Pages 설정에서 아래 두 가지를 연결해야 동작한다.
     - KV 네임스페이스 바인딩:  CONTENT
     - 환경 변수(시크릿):       ADMIN_PASSWORD
   둘 중 하나라도 없으면 사이트는 원래 문구 그대로 정상 동작한다.
   ========================================================================== */

import { EmailMessage } from "cloudflare:email";

const KV_KEY = "overrides";

// 상담 폼 — 받는 주소와 보내는 주소
const MAIL_TO = "jdgp@jdgp.co.kr";
const MAIL_FROM = "noreply@fleetcare.co.kr";
const MAIL_FROM_NAME = "플릿케어 홈페이지";
const TEL = "02-6925-0516";
const FORM_DAILY_CAP = 100;   // 하루 최대 접수 건수 (스팸 방어)

// 2026-09 구조 개편으로 옮겨간 주소
const MOVED = {
  "/needs": "/",
  "/process": "/service",
  "/partners": "/about",
};
const SESSION_HOURS = 8;
const MAX_LEN = 4000;      // 항목 하나의 최대 길이
const MAX_KEYS = 2000;     // 저장 가능한 항목 수

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname.startsWith("/api/")) {
      return handleApi(request, env, url);
    }

    // 구조 개편으로 없어진 페이지 -> 새 위치로 (검색엔진에 이미 올라간 주소)
    const moved = MOVED[url.pathname.replace(/\.html$/, "")];
    if (moved) {
      return Response.redirect(new URL(moved, url).toString(), 301);
    }

    const res = await env.ASSETS.fetch(request);
    const type = res.headers.get("content-type") || "";
    if (!type.includes("text/html")) return res;

    // 관리자 페이지는 손대지 않고, 캐시도 남기지 않는다
    if (url.pathname === "/admin" || url.pathname.startsWith("/admin/") ||
        url.pathname === "/admin.html") {
      return noStore(res);
    }

    const overrides = await readOverrides(env);
    if (!overrides || !Object.keys(overrides).length) return res;

    const out = new HTMLRewriter()
      .on("span[data-edit]", {
        element(el) {
          const key = el.getAttribute("data-edit");
          const val = overrides[key];
          if (typeof val === "string" && val.length) {
            el.setInnerContent(val, { html: true });
          }
        },
      })
      .transform(res);

    const headers = new Headers(out.headers);
    headers.set("cache-control", "public, max-age=0, must-revalidate");
    return new Response(out.body, { status: out.status, headers });
  },
};

/* ---------- 저장된 문구 ---------- */

async function readOverrides(env) {
  if (!env.CONTENT) return null;
  try {
    const raw = await env.CONTENT.get(KV_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    return null;
  }
}

/* ---------- 로그인 ---------- */

function enc(s) {
  return new TextEncoder().encode(s);
}

function b64url(bytes) {
  let s = "";
  const arr = new Uint8Array(bytes);
  for (let i = 0; i < arr.length; i++) s += String.fromCharCode(arr[i]);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function sign(value, secret) {
  const key = await crypto.subtle.importKey(
    "raw", enc(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return b64url(await crypto.subtle.sign("HMAC", key, enc(value)));
}

async function makeToken(secret) {
  const exp = String(Date.now() + SESSION_HOURS * 3600 * 1000);
  return exp + "." + (await sign(exp, secret));
}

async function validToken(token, secret) {
  if (!token || token.indexOf(".") < 0) return false;
  const [exp, mac] = token.split(".");
  if (!/^\d+$/.test(exp) || Number(exp) < Date.now()) return false;
  const want = await sign(exp, secret);
  if (want.length !== mac.length) return false;
  let diff = 0;
  for (let i = 0; i < want.length; i++) diff |= want.charCodeAt(i) ^ mac.charCodeAt(i);
  return diff === 0;
}

function cookieValue(request, name) {
  const raw = request.headers.get("cookie") || "";
  const hit = raw.split(";").map(function (c) { return c.trim(); })
    .find(function (c) { return c.indexOf(name + "=") === 0; });
  return hit ? decodeURIComponent(hit.slice(name.length + 1)) : "";
}

async function isLoggedIn(request, env) {
  if (!env.ADMIN_PASSWORD) return false;
  return validToken(cookieValue(request, "fc_admin"), env.ADMIN_PASSWORD);
}

/* ---------- 저장 전 정리 ----------
   관리자 본인만 쓰는 화면이지만, 실수로 붙여넣은 태그가 페이지를 망가뜨리지
   않도록 허용한 태그(<br> <strong> <b> <em> <span class="honest">)만 남긴다. */

function sanitize(input) {
  let s = String(input).slice(0, MAX_LEN);
  s = s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  s = s
    .replace(/&lt;br\s*\/?&gt;/gi, "<br>")
    .replace(/&lt;(\/?)(strong|b|em)&gt;/gi, "<$1$2>")
    .replace(/&lt;span class=&quot;honest&quot;&gt;/gi, '<span class="honest">')
    .replace(/&lt;span class="honest"&gt;/gi, '<span class="honest">')
    .replace(/&lt;\/span&gt;/gi, "</span>");
  return s.trim();
}

/* ---------- API ---------- */

function json(body, status, extraHeaders) {
  const headers = new Headers(extraHeaders || {});
  headers.set("content-type", "application/json; charset=utf-8");
  headers.set("cache-control", "no-store");
  return new Response(JSON.stringify(body), { status: status || 200, headers });
}

function noStore(res) {
  const headers = new Headers(res.headers);
  headers.set("cache-control", "no-store");
  headers.set("x-robots-tag", "noindex, nofollow");
  return new Response(res.body, { status: res.status, headers });
}

/* ---------- 상담 폼 접수 ---------- */

function b64(str) {
  const bytes = new TextEncoder().encode(str);
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin);
}

// 제목에 한글이 들어가므로 RFC 2047 로 인코딩한다
function encHeader(str) {
  return "=?UTF-8?B?" + b64(str) + "?=";
}

function wrap76(str) {
  return (str.match(/.{1,76}/g) || []).join("\r\n");
}

function plain(v, max) {
  return String(v == null ? "" : v)
    .replace(/[\r\n]+/g, " ")
    .trim()
    .slice(0, max || 200);
}

function buildMime(f) {
  const subject = "[플릿케어 상담] " +
    (f.company ? f.company + " " : "") + f.name +
    (f.vehicle ? " / " + f.vehicle : "");

  const body = [
    "홈페이지에서 상담 요청이 접수되었습니다.",
    "",
    "■ 법인명      " + (f.company || "-"),
    "■ 담당자명    " + f.name,
    "■ 연락처      " + f.phone,
    "■ 이메일      " + (f.email || "-"),
    "■ 차량 종류   " + (f.vehicle || "-"),
    "",
    "■ 문의 내용",
    f.message || "(없음)",
    "",
    "─────────────────────",
    "접수 시각  " + new Date().toLocaleString("ko-KR", { timeZone: "Asia/Seoul" }),
    "fleetcare.co.kr 상담 폼",
  ].join("\r\n");

  const headers = [
    "From: " + encHeader(MAIL_FROM_NAME) + " <" + MAIL_FROM + ">",
    "To: <" + MAIL_TO + ">",
    // 받은 메일에서 답장을 누르면 신청자에게 바로 가도록
    f.email ? "Reply-To: <" + f.email + ">" : null,
    "Subject: " + encHeader(subject),
    "Message-ID: <" + crypto.randomUUID() + "@fleetcare.co.kr>",
    "Date: " + new Date().toUTCString(),
    "MIME-Version: 1.0",
    'Content-Type: text/plain; charset="UTF-8"',
    "Content-Transfer-Encoding: base64",
  ].filter(Boolean).join("\r\n");

  return headers + "\r\n\r\n" + wrap76(b64(body)) + "\r\n";
}

async function overCap(env) {
  if (!env.CONTENT) return false;
  const key = "formcount:" + new Date().toISOString().slice(0, 10);
  const cur = Number((await env.CONTENT.get(key)) || 0);
  if (cur >= FORM_DAILY_CAP) return true;
  await env.CONTENT.put(key, String(cur + 1), { expirationTtl: 172800 });
  return false;
}

async function handleContact(request, env) {
  let body = {};
  try {
    body = await request.json();
  } catch (e) {
    return json({ ok: false, error: "요청을 읽지 못했습니다." }, 400);
  }

  // 허니팟 — 봇이 채웠으면 성공한 척하고 버린다
  if (plain(body.website)) return json({ ok: true });

  const f = {
    company: plain(body.company, 100),
    name: plain(body.name, 50),
    phone: plain(body.phone, 40),
    email: plain(body.email, 120),
    vehicle: plain(body.vehicle, 60),
    message: String(body.message == null ? "" : body.message).trim().slice(0, 3000),
  };

  if (!f.name) return json({ ok: false, error: "담당자명을 입력해 주세요." }, 400);
  if (f.phone.replace(/[^0-9]/g, "").length < 9) {
    return json({ ok: false, error: "연락처를 정확히 입력해 주세요." }, 400);
  }
  if (body.agree !== true) {
    return json({ ok: false, error: "개인정보 수집·이용에 동의해 주세요." }, 400);
  }
  if (f.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.email)) f.email = "";

  if (await overCap(env)) {
    return json({ ok: false, error: "오늘 접수가 많습니다. " + TEL + "로 전화 주세요." }, 429);
  }

  if (!env.SEND_EMAIL) {
    return json({ ok: false, error: "메일 발송이 아직 설정되지 않았습니다." }, 500);
  }

  try {
    await env.SEND_EMAIL.send(
      new EmailMessage(MAIL_FROM, MAIL_TO, buildMime(f))
    );
  } catch (e) {
    return json({ ok: false, error: "전송에 실패했습니다.", detail: String(e && e.message) }, 502);
  }

  return json({ ok: true });
}

/* ---------- 견적 요청 접수 ----------
   /quote 화면(js/quote.js)이 고른 차량·조건을 [항목, 값] 줄로 보내 준다.
   금액은 화면에서 계산한 참고값이다. 실제 견적은 사람이 다시 낸다. */

const QUOTE_MAX_ROWS = 30;

function sendMail(env, subject, lines, replyTo) {
  const headers = [
    "From: " + encHeader(MAIL_FROM_NAME) + " <" + MAIL_FROM + ">",
    "To: <" + MAIL_TO + ">",
    replyTo ? "Reply-To: <" + replyTo + ">" : null,
    "Subject: " + encHeader(subject),
    "Message-ID: <" + crypto.randomUUID() + "@fleetcare.co.kr>",
    "Date: " + new Date().toUTCString(),
    "MIME-Version: 1.0",
    'Content-Type: text/plain; charset="UTF-8"',
    "Content-Transfer-Encoding: base64",
  ].filter(Boolean).join("\r\n");
  const raw = headers + "\r\n\r\n" + wrap76(b64(lines.join("\r\n"))) + "\r\n";
  return env.SEND_EMAIL.send(new EmailMessage(MAIL_FROM, MAIL_TO, raw));
}

async function handleQuote(request, env) {
  let body = {};
  try {
    body = await request.json();
  } catch (e) {
    return json({ ok: false, error: "요청을 읽지 못했습니다." }, 400);
  }

  if (plain(body.website)) return json({ ok: true });   // 허니팟

  const f = {
    company: plain(body.company, 100),
    name: plain(body.name, 50),
    phone: plain(body.phone, 40),
    email: plain(body.email, 120),
    car: plain(body.car, 160),
    message: String(body.message == null ? "" : body.message).trim().slice(0, 3000),
  };
  const rows = (Array.isArray(body.rows) ? body.rows : [])
    .slice(0, QUOTE_MAX_ROWS)
    .filter(function (r) { return Array.isArray(r) && r.length === 2; })
    .map(function (r) { return [plain(r[0], 30), plain(r[1], 600)]; })
    .filter(function (r) { return r[0] && r[1]; });

  if (!f.car || !rows.length) {
    return json({ ok: false, error: "차량을 선택해 주세요." }, 400);
  }
  if (!f.name) return json({ ok: false, error: "담당자명을 입력해 주세요." }, 400);
  if (f.phone.replace(/[^0-9]/g, "").length < 9) {
    return json({ ok: false, error: "연락처를 정확히 입력해 주세요." }, 400);
  }
  if (body.agree !== true) {
    return json({ ok: false, error: "개인정보 수집·이용에 동의해 주세요." }, 400);
  }
  if (f.email && !/^[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+$/.test(f.email)) f.email = "";

  if (await overCap(env)) {
    return json({ ok: false, error: "오늘 접수가 많습니다. " + TEL + "로 전화 주세요." }, 429);
  }
  if (!env.SEND_EMAIL) {
    return json({ ok: false, error: "메일 발송이 아직 설정되지 않았습니다." }, 500);
  }

  const subject = "[플릿케어 견적] " + (f.company ? f.company + " " : "") + f.name + " / " + f.car;
  const lines = [
    "홈페이지에서 견적 요청이 접수되었습니다.",
    "",
    "■ 법인명      " + (f.company || "-"),
    "■ 담당자명    " + f.name,
    "■ 연락처      " + f.phone,
    "■ 이메일      " + (f.email || "-"),
    "",
    "── 요청 차량·조건",
  ].concat(
    rows.map(function (r) { return "· " + r[0] + " : " + r[1]; }),
    [
      "",
      "■ 요청 사항",
      f.message || "(없음)",
      "",
      "─────────────────────",
      "접수 시각  " + new Date().toLocaleString("ko-KR", { timeZone: "Asia/Seoul" }),
      "fleetcare.co.kr 견적 요청 폼",
    ]
  );

  try {
    await sendMail(env, subject, lines, f.email);
  } catch (e) {
    return json({ ok: false, error: "전송에 실패했습니다.", detail: String(e && e.message) }, 502);
  }
  return json({ ok: true });
}

async function handleApi(request, env, url) {
  const path = url.pathname;

  if (path === "/api/quote" && request.method === "POST") {
    return handleQuote(request, env);
  }

  if (path === "/api/contact" && request.method === "POST") {
    return handleContact(request, env);
  }

  if (path === "/api/status") {
    return json({
      kv: !!env.CONTENT,
      password: !!env.ADMIN_PASSWORD,
      loggedIn: await isLoggedIn(request, env),
    });
  }

  if (path === "/api/login" && request.method === "POST") {
    if (!env.ADMIN_PASSWORD) {
      return json({ ok: false, error: "ADMIN_PASSWORD가 설정되지 않았습니다." }, 500);
    }
    let body = {};
    try { body = await request.json(); } catch (e) {}
    const given = String(body.password || "");
    const want = String(env.ADMIN_PASSWORD);
    let diff = given.length === want.length ? 0 : 1;
    for (let i = 0; i < Math.max(given.length, want.length); i++) {
      diff |= (given.charCodeAt(i) || 0) ^ (want.charCodeAt(i) || 0);
    }
    if (diff !== 0) {
      // 무차별 대입을 조금이라도 느리게
      await new Promise(function (r) { setTimeout(r, 600); });
      return json({ ok: false, error: "비밀번호가 맞지 않습니다." }, 401);
    }
    const token = await makeToken(want);
    return json({ ok: true }, 200, {
      "set-cookie":
        "fc_admin=" + token + "; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=" +
        SESSION_HOURS * 3600,
    });
  }

  if (path === "/api/logout" && request.method === "POST") {
    return json({ ok: true }, 200, {
      "set-cookie": "fc_admin=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0",
    });
  }

  if (path === "/api/content") {
    if (!(await isLoggedIn(request, env))) {
      return json({ ok: false, error: "로그인이 필요합니다." }, 401);
    }
    if (!env.CONTENT) {
      return json({ ok: false, error: "KV 네임스페이스(CONTENT)가 연결되지 않았습니다." }, 500);
    }

    if (request.method === "GET") {
      return json({ ok: true, overrides: (await readOverrides(env)) || {} });
    }

    if (request.method === "POST") {
      let body = {};
      try { body = await request.json(); } catch (e) {
        return json({ ok: false, error: "요청을 읽지 못했습니다." }, 400);
      }
      const incoming = body.overrides;
      if (!incoming || typeof incoming !== "object") {
        return json({ ok: false, error: "저장할 내용이 없습니다." }, 400);
      }
      const keys = Object.keys(incoming);
      if (keys.length > MAX_KEYS) {
        return json({ ok: false, error: "항목이 너무 많습니다." }, 400);
      }
      const clean = {};
      for (const k of keys) {
        if (!/^[a-z0-9_:.-]{3,80}$/i.test(k)) continue;
        const v = sanitize(incoming[k]);
        if (v) clean[k] = v;          // 빈 값은 저장하지 않는다 = 원래 문구로 복귀
      }
      await env.CONTENT.put(KV_KEY, JSON.stringify(clean));
      return json({ ok: true, saved: Object.keys(clean).length });
    }
  }

  return json({ ok: false, error: "not found" }, 404);
}
