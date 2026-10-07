/* =========================================================
   POMP NET LOGIN BRAND
   ========================================================= */

(function () {

    function addPompNetLoginBrand() {

        if (document.getElementById("pompnet-login-brand")) {
            return;
        }

        const loginBox =
            document.getElementById("loginBox");

        if (!loginBox) {
            return;
        }

        const brand =
            document.createElement("div");

        brand.id =
            "pompnet-login-brand";

        brand.innerHTML = `
            <div class="pompnet-logo-circle">

                <img
                    src="/pompnet_logo.png"
                    alt="POMP NET"
                >

            </div>

            <div class="pompnet-login-title">
                POMP NET PANEL
            </div>

            <div class="pompnet-login-credit">
                کدنویسی شده توسط تیم پمپ نت
            </div>
        `;

        loginBox.parentNode.insertBefore(
            brand,
            loginBox
        );
    }

    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            addPompNetLoginBrand
        );

    } else {

        addPompNetLoginBrand();

    }

})();
