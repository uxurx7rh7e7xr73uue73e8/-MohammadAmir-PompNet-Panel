from pathlib import Path

MAIN = Path("/app/main.py")

if not MAIN.exists():
    raise SystemExit("ERROR: /app/main.py not found")

text = MAIN.read_text(encoding="utf-8")

# جلوگیری از نصب دوباره
if "کدنویسی و توسعه توسط تیم POMP NET" in text:
    print("POMP NET LOGIN CREDIT: ALREADY INSTALLED")
    raise SystemExit(0)

# نقطه دقیق فرم Login واقعی در Core
OLD = """      <button type="submit" id="loginBtn">ورود</button>
    </form>"""

NEW = """      <button type="submit" id="loginBtn">ورود</button>

      <div dir="rtl" style="
        margin-top:18px;
        padding-top:14px;
        border-top:1px solid rgba(255,255,255,.08);
        text-align:center;
        font-family:Vazirmatn,sans-serif;
      ">
        <div style="
          font-size:13px;
          font-weight:800;
          color:#ffffff;
          text-shadow:
            0 0 8px rgba(22,140,255,.70),
            0 0 18px rgba(139,53,255,.55);
        ">
          ⚡ کدنویسی و توسعه توسط تیم POMP NET
        </div>

        <div style="
          margin-top:7px;
          font-size:12px;
          color:rgba(255,255,255,.78);
        ">
          با همکاری و همراهی آقا امیر
        </div>

        <div style="
          margin-top:8px;
          font-size:10px;
          font-weight:900;
          letter-spacing:3px;
          color:#b875ff;
          direction:ltr;
          text-shadow:0 0 10px rgba(139,53,255,.65);
        ">
          MOHAMMAD × AMIR
        </div>
      </div>
    </form>"""

# باید دقیقاً یک بار پیدا شود
count = text.count(OLD)

if count != 1:
    raise SystemExit(
        f"ERROR: exact login location not found uniquely. Found: {count}"
    )

text = text.replace(OLD, NEW, 1)

MAIN.write_text(text, encoding="utf-8")

print("POMP NET LOGIN CREDIT: OK")
print("LOCATION: EXACTLY UNDER LOGIN BUTTON")
