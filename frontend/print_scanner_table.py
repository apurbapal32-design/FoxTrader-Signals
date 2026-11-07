import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\lenovo\.gemini\antigravity\scratch\FoxTrader-Pro\frontend\index.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('id="view-scanner"')
idx_table = text.find('<table', idx)
print(text[idx_table:idx_table+1600])
