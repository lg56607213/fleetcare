/* FleetCare
   1) 모바일 메뉴
   2) 자주 묻는 질문 — 인쇄 시 전부 펼치기
   3) 상담 요청 폼 — Cloudflare Worker 로 접수
*/

/* ==========================================================================
   1. 모바일 메뉴
   ========================================================================== */
(function () {
  "use strict";

  var btn = document.getElementById("menuBtn");
  var gnb = document.getElementById("gnb");
  if (!btn || !gnb) return;

  function close() {
    gnb.classList.remove("is-open");
    btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-label", "메뉴 열기");
  }

  btn.addEventListener("click", function () {
    var open = gnb.classList.toggle("is-open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    btn.setAttribute("aria-label", open ? "메뉴 닫기" : "메뉴 열기");
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && gnb.classList.contains("is-open")) {
      close();
      btn.focus();
    }
  });

  document.addEventListener("click", function (e) {
    if (!gnb.classList.contains("is-open")) return;
    if (gnb.contains(e.target) || btn.contains(e.target)) return;
    close();
  });

  // 창을 넓히면 메뉴 상태를 초기화한다
  window.addEventListener("resize", function () {
    if (window.innerWidth > 1000) close();
  });
})();

/* ==========================================================================
   2. 자주 묻는 질문 — 인쇄할 때는 접힌 답변도 나오게 한다
   ========================================================================== */
(function () {
  "use strict";

  var qas = document.querySelectorAll("details.qa");
  if (!qas.length) return;

  var reopened = [];

  function openAll() {
    reopened = [];
    for (var i = 0; i < qas.length; i++) {
      if (!qas[i].open) {
        qas[i].open = true;
        reopened.push(qas[i]);
      }
    }
  }

  function restore() {
    for (var i = 0; i < reopened.length; i++) reopened[i].open = false;
    reopened = [];
  }

  window.addEventListener("beforeprint", openAll);
  window.addEventListener("afterprint", restore);
})();

/* ==========================================================================
   3. 상담 요청 폼
   폼 내용을 /api/contact 로 보내면 Worker 가 메일로 전달한다.
   ========================================================================== */
(function () {
  "use strict";

  var TEL = "02-6925-0516";

  var form = document.getElementById("contactForm");
  var done = document.getElementById("formDone");
  var errBox = document.getElementById("formError");
  var btn = document.getElementById("submitBtn");
  if (!form || !done || !errBox || !btn) return;

  function showError(html) {
    errBox.innerHTML = html;
    errBox.hidden = false;
  }

  function clearError() {
    errBox.hidden = true;
    errBox.innerHTML = "";
    var marked = form.querySelectorAll(".field-invalid");
    for (var i = 0; i < marked.length; i++) marked[i].classList.remove("field-invalid");
  }

  function markInvalid(el) {
    var wrap = el.closest(".field");
    if (wrap) wrap.classList.add("field-invalid");
  }

  function failMessage() {
    return (
      '전송에 실패했습니다. <a href="tel:0269250516">' + TEL +
      "</a>으로 전화 주시면 바로 도와드리겠습니다."
    );
  }

  function setSending(sending) {
    btn.disabled = sending;
    btn.textContent = sending ? "보내는 중" : "상담 요청";
  }

  function val(id) {
    var el = form.querySelector("#" + id);
    return el ? el.value.trim() : "";
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    clearError();

    // 허니팟 — 채워져 있으면 봇으로 보고 조용히 중단
    var hp = form.querySelector('input[name="website"]');
    if (hp && hp.value.trim() !== "") return;

    var name = form.querySelector("#name");
    var phone = form.querySelector("#phone");
    var agree = form.querySelector("#agree");

    if (name.value.trim() === "") {
      markInvalid(name);
      showError("담당자명을 입력해 주세요.");
      name.focus();
      return;
    }

    if (phone.value.replace(/[^0-9]/g, "").length < 9) {
      markInvalid(phone);
      showError("연락처를 정확히 입력해 주세요.");
      phone.focus();
      return;
    }

    if (!agree.checked) {
      showError("개인정보 수집·이용에 동의해 주세요.");
      agree.focus();
      return;
    }

    setSending(true);

    fetch("/api/contact", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        company: val("company"),
        name: val("name"),
        phone: val("phone"),
        email: val("email"),
        vehicle: val("vehicle"),
        message: val("message"),
        website: val("website"),
        agree: true,
      }),
    })
      .then(function (r) {
        return r.json().catch(function () { return {}; });
      })
      .then(function (body) {
        if (body && body.ok) {
          form.hidden = true;
          done.hidden = false;
          done.setAttribute("tabindex", "-1");
          done.focus();
          return;
        }
        setSending(false);
        // 서버가 이유를 알려준 경우엔 그대로 보여주고, 아니면 전화 안내
        showError(body && body.error && !body.detail ? body.error : failMessage());
      })
      .catch(function () {
        setSending(false);
        showError(failMessage());
      });
  });

  // 입력을 고치기 시작하면 오류 표시를 지운다
  form.addEventListener("input", function (e) {
    if (errBox.hidden) return;
    if (e.target.matches("input, textarea, select")) clearError();
  });
})();
