/* POMP NET LOGIN BRAND
   فقط ظاهر صفحه ورود
   منطق Login واقعی تغییر نمی‌کند
*/

(function () {

    function addPompNetLoginBrand() {

        if (
            document.getElementById(
                "pompnet-login-brand"
            )
        ) {
            return;
        }

        const loginBox =
            document.getElementById(
                "loginBox"
            );

        if (
            !loginBox ||
            !loginBox.parentNode
        ) {
            return;
        }

        const brand =
            document.createElement(
                "div"
            );

        brand.id =
            "pompnet-login-brand";

        brand.innerHTML = `
            <div
                class="pompnet-logo-circle"
                aria-label="PompNet"
            >
                <span class="pompnet-logo-text">
                    PN
                </span>
            </div>

            <div class="pompnet-login-title">

                <span class="pompnet-title-main">
                    MR. MOHAMMAD
                </span>

                <span class="pompnet-title-divider">
                    |
                </span>

                <span class="pompnet-title-brand">
                    POMPNET
                </span>

            </div>

            <div class="pompnet-login-credit">
                ✦ کدنویسی و توسعه اختصاصی توسط تیم پمپ‌نت • آقا امیر ✦
            </div>
        `;

        loginBox.parentNode.insertBefore(
            brand,
            loginBox
        );
    }

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            addPompNetLoginBrand
        );

    } else {

        addPompNetLoginBrand();

    }

})();
