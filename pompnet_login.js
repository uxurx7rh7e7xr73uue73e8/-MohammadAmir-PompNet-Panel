/* POMP NET MOHAMMAD — SUPER JINX
   تصویر برند بالای فرم ورود؛ منطق احراز هویت دست‌نخورده است.
*/
(function () {
  const logoImage = "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20256%20256%22%3E%3Cdefs%3E%3ClinearGradient%20id%3D%22g%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%3Cstop%20stop-color%3D%22%23168cff%22%2F%3E%3Cstop%20offset%3D%22.52%22%20stop-color%3D%22%236338ff%22%2F%3E%3Cstop%20offset%3D%221%22%20stop-color%3D%22%23a12dff%22%2F%3E%3C%2FlinearGradient%3E%3ClinearGradient%20id%3D%22s%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%3Cstop%20stop-color%3D%22%23fff%22%2F%3E%3Cstop%20offset%3D%221%22%20stop-color%3D%22%23c8b4ff%22%2F%3E%3C%2FlinearGradient%3E%3Cfilter%20id%3D%22glow%22%3E%3CfeGaussianBlur%20stdDeviation%3D%228%22%20result%3D%22b%22%2F%3E%3CfeMerge%3E%3CfeMergeNode%20in%3D%22b%22%2F%3E%3CfeMergeNode%20in%3D%22SourceGraphic%22%2F%3E%3C%2FfeMerge%3E%3C%2Ffilter%3E%3C%2Fdefs%3E%3Crect%20x%3D%228%22%20y%3D%228%22%20width%3D%22240%22%20height%3D%22240%22%20rx%3D%2258%22%20fill%3D%22%23090713%22%20stroke%3D%22url(%23g)%22%20stroke-width%3D%228%22%2F%3E%3Crect%20x%3D%2222%22%20y%3D%2222%22%20width%3D%22212%22%20height%3D%22212%22%20rx%3D%2246%22%20fill%3D%22url(%23g)%22%20opacity%3D%22.18%22%2F%3E%3Cpath%20d%3D%22M56%2074h75c34%200%2055%2019%2055%2048s-21%2048-55%2048H99v31H56V74zm43%2036v25h31c9%200%2014-5%2014-13s-5-12-14-12H99z%22%20fill%3D%22url(%23s)%22%20filter%3D%22url(%23glow)%22%2F%3E%3Cpath%20d%3D%22M155%2074h45v127h-45z%22%20rx%3D%228%22%20fill%3D%22%23fff%22%20opacity%3D%22.92%22%2F%3E%3Cpath%20d%3D%22M168%2055l8-18%208%2018%2018%208-18%208-8%2018-8-18-18-8z%22%20fill%3D%22%23fff%22%20opacity%3D%22.9%22%2F%3E%3C%2Fsvg%3E";
  function addPompNetLoginBrand() {
    if (document.getElementById("pompnet-login-brand")) return;
    const loginBox = document.getElementById("loginBox");
    if (!loginBox || !loginBox.parentNode) return;
    const brand = document.createElement("section");
    brand.id = "pompnet-login-brand";
    brand.setAttribute("aria-label", "POMP NET MOHAMMAD SUPER JINX");
    brand.innerHTML = `
      <div class="pompnet-logo-circle">
        <img src="${logoImage}" alt="نشان تصویری POMP NET SUPER JINX">
      </div>
      <div class="pompnet-login-title">
        <span class="pompnet-title-main">POMP NET MOHAMMAD</span>
        <span class="pompnet-title-brand">SUPER JINX</span>
      </div>
      <div class="pompnet-login-credit">قدرت ساخت، آزادی انتخاب، کنترل در دستان تو</div>
      <div class="pompnet-login-caption">مرکز مدیریت هوشمند کاربران، کانفیگ‌ها و اشتراک‌ها</div>
    `;
    loginBox.parentNode.insertBefore(brand, loginBox);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", addPompNetLoginBrand, {once:true});
  } else {
    addPompNetLoginBrand();
  }
})();
