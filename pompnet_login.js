/* POMP NET MOHAMMAD — SUPER JINX
   Premium login artwork. Authentication and setup requests remain untouched.
*/
(function () {
  const logoSvg = `
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 520">
    <defs>
      <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#050713"/><stop offset=".52" stop-color="#100829"/><stop offset="1" stop-color="#020b19"/></linearGradient>
      <linearGradient id="violet" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#b64dff"/><stop offset=".48" stop-color="#6935ff"/><stop offset="1" stop-color="#168cff"/></linearGradient>
      <linearGradient id="silver" x1="0" y1="0" x2="0.8" y2="1"><stop stop-color="#fff"/><stop offset=".38" stop-color="#c7c8f8"/><stop offset=".7" stop-color="#7654d9"/><stop offset="1" stop-color="#f3eaff"/></linearGradient>
      <radialGradient id="halo"><stop stop-color="#5631ff" stop-opacity=".5"/><stop offset="1" stop-color="#09051b" stop-opacity="0"/></radialGradient>
      <filter id="glow"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      <filter id="soft"><feGaussianBlur stdDeviation="24"/></filter>
    </defs>
    <rect width="1200" height="520" rx="34" fill="url(#bg)"/>
    <circle cx="520" cy="235" r="360" fill="url(#halo)"/>
    <circle cx="1000" cy="40" r="190" fill="#147bff" opacity=".10" filter="url(#soft)"/>
    <g fill="#b8baff" opacity=".8">
      <circle cx="70" cy="70" r="2"/><circle cx="170" cy="160" r="2"/><circle cx="285" cy="42" r="2"/><circle cx="420" cy="80" r="2"/><circle cx="620" cy="42" r="2"/><circle cx="760" cy="110" r="2"/><circle cx="1090" cy="125" r="2"/><circle cx="1140" cy="340" r="2"/><circle cx="90" cy="390" r="2"/><circle cx="310" cy="450" r="2"/>
    </g>
    <path d="M0 430 Q180 330 330 440 T650 420 T1200 400 V520 H0Z" fill="#130b36" opacity=".75"/>
    <path d="M0 330 L105 245 80 365 190 280 150 395 285 310 240 430 390 360" fill="none" stroke="#712cff" stroke-width="5" opacity=".65" filter="url(#glow)"/>
    <path d="M1200 270 L1090 180 1125 310 1000 225 1045 360 900 280 950 420" fill="none" stroke="#168cff" stroke-width="5" opacity=".7" filter="url(#glow)"/>
    <!-- left wing feathers -->
    <g fill="url(#violet)" stroke="#a58cff" stroke-width="2" filter="url(#glow)">
      <path d="M470 250 Q260 12 65 95 Q210 110 330 235 Q190 145 45 180 Q220 210 355 300 Q230 260 100 300 Q275 330 440 355Z"/>
      <path d="M460 270 Q300 115 125 130 Q270 185 390 285Z" opacity=".8"/>
      <path d="M445 300 Q285 225 155 250 Q300 275 425 340Z" opacity=".9"/>
    </g>
    <!-- right phoenix wings -->
    <g fill="url(#violet)" stroke="#63aaff" stroke-width="2" filter="url(#glow)">
      <path d="M720 260 Q900 8 1135 60 Q1000 130 860 245 Q1010 170 1170 185 Q1010 240 870 310 Q1010 285 1150 335 Q970 350 760 380Z"/>
      <path d="M745 280 Q925 120 1080 115 Q950 190 810 295Z" opacity=".82"/>
      <path d="M760 315 Q960 230 1110 260 Q960 295 790 355Z" opacity=".9"/>
    </g>
    <!-- crest -->
    <g filter="url(#glow)">
      <circle cx="600" cy="245" r="178" fill="#08091a" stroke="url(#violet)" stroke-width="8"/>
      <circle cx="600" cy="245" r="158" fill="none" stroke="#b77bff" stroke-opacity=".65" stroke-width="3"/>
      <path d="M490 110 L515 48 550 98 600 20 650 98 685 48 710 110" fill="none" stroke="url(#silver)" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M485 112 Q600 150 715 112 L700 145 Q600 175 500 145Z" fill="url(#violet)" stroke="#e6d7ff" stroke-width="3"/>
      <text x="600" y="310" text-anchor="middle" font-family="Arial,sans-serif" font-size="205" font-weight="900" font-style="italic" letter-spacing="-20" fill="url(#silver)" stroke="#24134d" stroke-width="5" paint-order="stroke">PJ</text>
      <path d="M510 355 Q600 400 690 355" fill="none" stroke="#a77aff" stroke-width="7" stroke-linecap="round"/>
      <path d="M600 365 l18 24 -18 24 -18 -24Z" fill="#168cff" stroke="#fff" stroke-width="2"/>
    </g>
    <!-- energy arcs -->
    <path d="M90 470 Q600 510 1110 460" fill="none" stroke="url(#violet)" stroke-width="4" opacity=".9" filter="url(#glow)"/>
    <path d="M130 35 Q600 -15 1070 35" fill="none" stroke="#168cff" stroke-width="2" opacity=".65"/>
  </svg>`;
  const logoImage = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(logoSvg);
  function addPompNetLoginBrand() {
    if (document.getElementById("pompnet-login-brand")) return;
    const loginBox = document.getElementById("loginBox");
    const setupBox = document.getElementById("setupBox");
    const anchor = setupBox || loginBox;
    if (!anchor || !anchor.parentNode) return;
    const brand = document.createElement("section");
    brand.id = "pompnet-login-brand";
    brand.setAttribute("aria-label", "POMP NET MOHAMMAD SUPER JINX");
    brand.innerHTML = `
      <div class="pompnet-logo-circle">
        <img src="${logoImage}" alt="نشان تصویری اختصاصی POMP NET SUPER JINX">
      </div>
      <div class="pompnet-login-title">
        <span class="pompnet-title-main">POMP NET MOHAMMAD</span>
        <span class="pompnet-title-brand">SUPER JINX</span>
      </div>
      <div class="pompnet-login-credit">قدرت ساخت، آزادی انتخاب، کنترل در دستان تو</div>
      <div class="pompnet-login-caption">درگاه امن مدیریت کاربران، کانفیگ‌ها و اشتراک‌ها</div>
      <div class="pompnet-login-divider"><i></i><b>✦</b><i></i></div>
    `;
    anchor.parentNode.insertBefore(brand, anchor);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", addPompNetLoginBrand, {once:true});
  } else {
    addPompNetLoginBrand();
  }
})();
