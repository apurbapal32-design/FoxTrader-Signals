import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\lenovo\.gemini\antigravity\scratch\FoxTrader-Pro\frontend\index.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('id="view-scanner"')
idx2 = text.find('</section>', idx)
print("=== view-scanner length:", idx2 - idx)
print(text[idx-40:idx+1500])
