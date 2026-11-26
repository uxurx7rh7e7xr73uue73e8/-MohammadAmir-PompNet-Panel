from pathlib import Path

MAIN = Path("/app/main.py")

if not MAIN.exists():
    raise SystemExit("ERROR: /app/main.py not found")

source = MAIN.read_text(encoding="utf-8")

# جلوگیری از نصب دوباره
if "POMP NET MOHAMMAD — SUPER JINX" in source:
    print("POMP NET SUPER JINX LOGIN BRAND: ALREADY INSTALLED")
    raise SystemExit(0)

OLD = """      <button type="submit" id="loginBtn">ورود</button>
    </form>"""

NEW = """      <button type="submit" id="loginBtn">ورود</button>

      <div dir="rtl" style="
        margin-top:18px;
        padding-top:14px;
        border-top:1px solid rgba(139,53,255,.22);
        text-align:center;
        font-family:Vazirmatn,sans-serif;
      ">
        <div style="
          font-size:14px;
          font-weight:950;
          letter-spacing:.5px;
          color:#ffffff;
          text-shadow:0 0 9px rgba(139,53,255,.7),0 0 18px rgba(22,140,255,.45);
        ">
          ⚡ POMP NET MOHAMMAD
        </div>
        <div style="
          margin-top:7px;
          font-size:12px;
          font-weight:900;
          color:#b98cff;
          letter-spacing:2px;
          direction:ltr;
        ">
          SUPER JINX
        </div>
        <div style="
          margin-top:8px;
          font-size:11px;
          color:rgba(255,255,255,.72);
        ">
          قدرت ساخت، آزادی انتخاب، کنترل در دستان تو
        </div>
      </div>
    </form>"""

count = source.count(OLD)
if count != 1:
    raise SystemExit(
        f"ERROR: exact login location not found uniquely. Found: {count}"
    )

updated = source.replace(OLD, NEW, 1)
MAIN.write_text(updated, encoding="utf-8")

print("POMP NET MOHAMMAD — SUPER JINX LOGIN BRAND: OK")
print("AMIR BRANDING: NOT INSERTED")
