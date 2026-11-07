path = r"C:\Users\lenovo\.gemini\antigravity\scratch\FoxTrader-Pro\frontend\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update view-broker HTML
target_broker_html = '''    <!-- 2. Broker API Gateway -->
    <section class="view-container" id="view-broker">
      <div style="display:grid; grid-template-columns: 420px 1fr; gap:10px; padding:12px; width:100%; height:100%;">
        <div class="smc-card">
          <div class="smc-title">🔑 Broker API Configuration</div>
          <p style="color:var(--text-muted); font-size:11px;">Connect your live broker account to stream tick-by-tick market data across all 224 F&amp;O instruments.</p>

          <div class="form-group">
            <label>Select Active Broker:</label>
            <select class="fox-select" id="brokerSelect" onchange="toggleBrokerFields(this.value)">
              <option value="fyers">Fyers API v3 (Installed &amp; Recommended)</option>
              <option value="zerodha">Zerodha Kite Connect</option>
              <option value="angel">Angel One SmartAPI</option>
              <option value="dhan">Dhan Trading API</option>
              <option value="live_stream">FoxTrader Live Tick Streamer</option>
            </select>
          </div>

          <!-- Fyers Fields -->
          <div id="fyersFields">
            <div class="form-group" style="margin-top:6px;">
              <label>Fyers App ID (Client ID):</label>
              <input type="text" class="fox-input" id="fyersClientId" value="RMR62XB492-100">
            </div>
            <div class="form-group" style="margin-top:6px;">
              <label>Fyers Secret Key:</label>
              <input type="password" class="fox-input" id="fyersSecretKey" value="0WF68SFOJD">
            </div>
            <div class="form-group" style="margin-top:6px;">
              <label>Fyers Access Token (Valid for 24h):</label>
              <input type="password" class="fox-input" id="fyersAccessToken" placeholder="Paste access token here">
            </div>
            <div style="display:flex; gap:8px; margin-top:8px;">
              <button class="fox-btn fox-btn-secondary" onclick="openFyersLogin()">🌐 Generate Fyers Login URL</button>
            </div>
          </div>

          <!-- Zerodha Fields -->
          <div id="zerodhaFields" style="display:none;">
            <div class="form-group" style="margin-top:6px;">
              <label>Zerodha API Key:</label>
              <input type="text" class="fox-input" id="zerodhaApiKey" placeholder="API Key">
            </div>
            <div class="form-group" style="margin-top:6px;">
              <label>Zerodha Access Token:</label>
              <input type="password" class="fox-input" id="zerodhaAccessToken" placeholder="Access Token">
            </div>
          </div>

          <div style="display:flex; gap:8px; margin-top:14px;">
            <button class="fox-btn" onclick="saveBrokerConfig()">💾 Save Broker Settings</button>
            <button class="fox-btn fox-btn-secondary" onclick="checkBrokerLiveStatus()">⚡ Test Connection</button>
          </div>

          <div id="brokerDiagResult" style="background:#191c20; padding:10px; border-radius:4px; font-family:'JetBrains Mono'; font-size:11px; margin-top:10px; line-height:1.5;">
            Status: Initializing gateway...
          </div>
        </div>

        <!-- 224 Instruments Universe Breakdown -->
        <div class="fox-panel">
          <div class="panel-header">
            <span>224 F&amp;O Instruments Directory</span>
            <div class="panel-header-controls">
              <span>6 Indices + 218 Equities</span>
            </div>
          </div>
          <div class="panel-body">
            <table class="fox-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Symbol</th>
                  <th>Underlying Name</th>
                  <th>Sector</th>
                  <th>Fyers Symbol</th>
                  <th>Lot Size</th>
                </tr>
              </thead>
              <tbody id="universeDirectoryBody">
                <!-- Injected via JS -->
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>'''

replacement_broker_html = '''    <!-- 2. Broker API Gateway -->
    <section class="view-container" id="view-broker">
      <div style="display:grid; grid-template-columns: 460px 1fr; gap:10px; padding:12px; width:100%; height:100%;">
        <div class="smc-card">
          <div class="smc-title">🔑 Broker API Gateway &amp; Live Feeds</div>
          <p style="color:var(--text-muted); font-size:11px;">Connect your live broker account to stream tick-by-tick market data across all 224 F&amp;O instruments.</p>

          <div class="form-group">
            <label>Select Active Broker:</label>
            <select class="fox-select" id="brokerSelect" onchange="toggleBrokerFields(this.value)">
              <option value="upstox">🦊 Upstox API v2 (Official Live Quotes &amp; Candles)</option>
              <option value="fyers">Fyers API v3 (Direct Multi-Quotes)</option>
              <option value="zerodha">Zerodha Kite Connect</option>
              <option value="angel">Angel One SmartAPI</option>
              <option value="dhan">Dhan Trading API</option>
              <option value="live_stream">FoxTrader High-Speed Tick Streamer</option>
            </select>
          </div>

          <!-- Upstox API v2 Fields -->
          <div id="upstoxFields">
            <div style="background:rgba(255, 107, 53, 0.1); border:1px solid rgba(255, 107, 53, 0.35); padding:8px 10px; border-radius:4px; margin-top:6px; font-size:11px; color:#ff8a5c; line-height:1.4;">
              ⚡ <b>Upstox API v2 Live Feed:</b> Streams real-time tick-by-tick prices, LTP quotes, and historical candles for all 224 F&amp;O scrips &amp; indices.
            </div>
            <div class="form-group" style="margin-top:8px;">
              <label>Upstox API Key (Client ID):</label>
              <input type="text" class="fox-input" id="upstoxApiKey" placeholder="e.g. 789a45bc-1234-...">
            </div>
            <div class="form-group" style="margin-top:6px;">
              <label>Upstox API Secret:</label>
              <input type="password" class="fox-input" id="upstoxApiSecret" placeholder="e.g. abc987xyz...">
            </div>
            <div class="form-group" style="margin-top:6px;">
              <label>Upstox Access Token (Bearer Token):</label>
              <input type="password" class="fox-input" id="upstoxAccessToken" placeholder="Paste Upstox access token here">
            </div>
            <div class="form-group" style="margin-top:6px;">
              <label>Redirect URI (Callback):</label>
              <input type="text" class="fox-input" id="upstoxRedirectUri" value="http://127.0.0.1:8088/api/broker/upstox/callback" readonly style="color:var(--text-muted); font-size:11px;">
            </div>
            <div style="display:flex; gap:8px; margin-top:10px;">
              <button class="fox-btn fox-btn-secondary" onclick="openUpstoxLogin()">🌐 Upstox OAuth Login</button>
              <button class="fox-btn" style="background:#2ecc71; font-weight:700;" onclick="quickSaveUpstoxToken()">⚡ Activate Upstox Token</button>
            </div>
          </div>

          <!-- Fyers Fields -->
          <div id="fyersFields" style="display:none;">
            <div class="form-group" style="margin-top:6px;">
              <label>Fyers App ID (Client ID):</label>
              <input type="text" class="fox-input" id="fyersClientId" value="RMR62XB492-100">
            </div>
            <div class="form-group" style="margin-top:6px;">
              <label>Fyers Secret Key:</label>
              <input type="password" class="fox-input" id="fyersSecretKey" value="0WF68SFOJD">
            </div>
            <div class="form-group" style="margin-top:6px;">
              <label>Fyers Access Token (Valid for 24h):</label>
              <input type="password" class="fox-input" id="fyersAccessToken" placeholder="Paste access token here">
            </div>
            <div style="display:flex; gap:8px; margin-top:8px;">
              <button class="fox-btn fox-btn-secondary" onclick="openFyersLogin()">🌐 Generate Fyers Login URL</button>
            </div>
          </div>

          <!-- Zerodha Fields -->
          <div id="zerodhaFields" style="display:none;">
            <div class="form-group" style="margin-top:6px;">
              <label>Zerodha API Key:</label>
              <input type="text" class="fox-input" id="zerodhaApiKey" placeholder="API Key">
            </div>
            <div class="form-group" style="margin-top:6px;">
              <label>Zerodha Access Token:</label>
              <input type="password" class="fox-input" id="zerodhaAccessToken" placeholder="Access Token">
            </div>
          </div>

          <div style="display:flex; gap:8px; margin-top:14px;">
            <button class="fox-btn" onclick="saveBrokerConfig()">💾 Save All Broker Settings</button>
            <button class="fox-btn fox-btn-secondary" onclick="checkBrokerLiveStatus()">⚡ Test Connection</button>
          </div>

          <div id="brokerDiagResult" style="background:#191c20; padding:10px; border-radius:4px; font-family:'JetBrains Mono'; font-size:11px; margin-top:10px; line-height:1.5;">
            Status: Initializing gateway...
          </div>
        </div>

        <!-- 224 Instruments Universe Breakdown -->
        <div class="fox-panel">
          <div class="panel-header">
            <span>224 F&amp;O Instruments Directory</span>
            <div class="panel-header-controls">
              <span>6 Indices + 218 Equities • Upstox Instrument Keys</span>
            </div>
          </div>
          <div class="panel-body">
            <table class="fox-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Symbol</th>
                  <th>Underlying Name</th>
                  <th>Sector</th>
                  <th>Upstox Instrument Key</th>
                  <th>Lot Size</th>
                </tr>
              </thead>
              <tbody id="universeDirectoryBody">
                <!-- Injected via JS -->
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>'''

if target_broker_html in html:
    html = html.replace(target_broker_html, replacement_broker_html)
    print("Updated view-broker HTML")
else:
    print("Target broker HTML not found!")

# 2. Update JavaScript broker functions
target_js_block = '''    function checkBrokerLiveStatus() {
      const diag = document.getElementById('brokerDiagResult');
      diag.innerHTML = 'Testing connection to broker API...';
      try {
        const res = await fetch('/api/broker/status');
        const data = await res.json();
        if (data.connected) {
          diag.innerHTML = `<span class="text-green">✅ ${data.broker} Connected!</span><br>Status: ${data.status}`;
          document.getElementById('brokerStatusText').innerText = `Live: ${data.broker}`;
          document.getElementById('footerBrokerName').innerText = data.broker;
        } else {
          diag.innerHTML = `<span class="text-orange">⚠️ ${data.broker}: ${data.status}</span><br>Fallback Live Tick Streamer active across 224 instruments.`;
          document.getElementById('brokerStatusText').innerText = `Fallback: Live Streamer`;
        }
      } catch (e) {
        diag.innerHTML = `<span class="text-red">Error: ${e.message}</span>`;
      }
    }

    async function saveBrokerConfig() {
      const activeBroker = document.getElementById('brokerSelect').value;
      const payload = {
        active_broker: activeBroker,
        fyers: {
          client_id: document.getElementById('fyersClientId').value,
          secret_key: document.getElementById('fyersSecretKey').value,
          access_token: document.getElementById('fyersAccessToken').value
        }
      };
      try {
        const res = await fetch('/api/broker/config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        alert('Broker configuration updated!');
        checkBrokerLiveStatus();
      } catch (e) {
        alert('Failed saving config: ' + e);
      }
    }

    async function openFyersLogin() {
      try {
        const res = await fetch('/api/broker/fyers/login_url');
        const data = await res.json();
        if (data.url) {
          window.open(data.url, '_blank');
        }
      } catch (e) {
        alert(e);
      }
    }

    function toggleBrokerFields(b) {
      document.getElementById('fyersFields').style.display = (b === 'fyers') ? 'block' : 'none';
      document.getElementById('zerodhaFields').style.display = (b === 'zerodha') ? 'block' : 'none';
    }'''

replacement_js_block = '''    async function checkBrokerLiveStatus() {
      const diag = document.getElementById('brokerDiagResult');
      diag.innerHTML = 'Testing connection to broker API...';
      try {
        const res = await fetch('/api/broker/status');
        const data = await res.json();
        if (data.connected) {
          let userDetail = data.user_name ? `<br>User: <b>${data.user_name}</b> (${data.user_id || ''})` : '';
          diag.innerHTML = `<span class="text-green">✅ ${data.broker} Connected!</span>${userDetail}<br>Status: ${data.status}`;
          document.getElementById('brokerStatusText').innerText = `Live: ${data.broker}`;
          document.getElementById('footerBrokerName').innerText = data.broker;
        } else {
          diag.innerHTML = `<span class="text-orange">⚠️ ${data.broker}: ${data.status}</span><br>FoxTrader Live Tick Streamer active across 224 instruments.`;
          document.getElementById('brokerStatusText').innerText = `Fallback: Live Streamer`;
        }
      } catch (e) {
        diag.innerHTML = `<span class="text-red">Error: ${e.message}</span>`;
      }
    }

    async function saveBrokerConfig() {
      const activeBroker = document.getElementById('brokerSelect').value;
      const payload = {
        active_broker: activeBroker,
        upstox: {
          api_key: document.getElementById('upstoxApiKey')?.value.trim() || '',
          api_secret: document.getElementById('upstoxApiSecret')?.value.trim() || '',
          access_token: document.getElementById('upstoxAccessToken')?.value.trim() || '',
          redirect_uri: document.getElementById('upstoxRedirectUri')?.value.trim() || 'http://127.0.0.1:8088/api/broker/upstox/callback'
        },
        fyers: {
          client_id: document.getElementById('fyersClientId')?.value.trim() || '',
          secret_key: document.getElementById('fyersSecretKey')?.value.trim() || '',
          access_token: document.getElementById('fyersAccessToken')?.value.trim() || ''
        }
      };
      try {
        const res = await fetch('/api/broker/config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        showToast('✅ Broker configuration saved!');
        checkBrokerLiveStatus();
      } catch (e) {
        alert('Failed saving config: ' + e);
      }
    }

    async function openUpstoxLogin() {
      try {
        const res = await fetch('/api/broker/upstox/login_url');
        const data = await res.json();
        if (data.url) {
          window.open(data.url, '_blank');
        }
      } catch (e) {
        alert(e);
      }
    }

    async function quickSaveUpstoxToken() {
      const token = document.getElementById('upstoxAccessToken').value.trim();
      const apiKey = document.getElementById('upstoxApiKey').value.trim();
      const apiSecret = document.getElementById('upstoxApiSecret').value.trim();
      if (!token) {
        alert('Please paste an Upstox access token.');
        return;
      }
      try {
        const res = await fetch('/api/broker/upstox/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ access_token: token, api_key: apiKey, api_secret: apiSecret })
        });
        const data = await res.json();
        if (data.success) {
          showToast('✅ Upstox API v2 Token Activated!');
          document.getElementById('brokerSelect').value = 'upstox';
          toggleBrokerFields('upstox');
          checkBrokerLiveStatus();
        } else {
          alert('Failed activating Upstox token: ' + JSON.stringify(data));
        }
      } catch (e) {
        alert('Error: ' + e);
      }
    }

    async function openFyersLogin() {
      try {
        const res = await fetch('/api/broker/fyers/login_url');
        const data = await res.json();
        if (data.url) {
          window.open(data.url, '_blank');
        }
      } catch (e) {
        alert(e);
      }
    }

    function toggleBrokerFields(b) {
      document.getElementById('upstoxFields').style.display = (b === 'upstox') ? 'block' : 'none';
      document.getElementById('fyersFields').style.display = (b === 'fyers') ? 'block' : 'none';
      document.getElementById('zerodhaFields').style.display = (b === 'zerodha') ? 'block' : 'none';
    }

    async function loadBrokerConfig() {
      try {
        const res = await fetch('/api/broker/config');
        const cfg = await res.json();
        if (cfg.active_broker) {
          document.getElementById('brokerSelect').value = cfg.active_broker;
          toggleBrokerFields(cfg.active_broker);
        }
        if (cfg.upstox) {
          if (cfg.upstox.api_key) document.getElementById('upstoxApiKey').value = cfg.upstox.api_key;
          if (cfg.upstox.access_token) document.getElementById('upstoxAccessToken').value = cfg.upstox.access_token;
        }
        if (cfg.fyers) {
          if (cfg.fyers.client_id) document.getElementById('fyersClientId').value = cfg.fyers.client_id;
          if (cfg.fyers.access_token) document.getElementById('fyersAccessToken').value = cfg.fyers.access_token;
        }
      } catch (e) {
        console.error('Error loading broker config:', e);
      }
    }'''

if target_js_block in html:
    html = html.replace(target_js_block, replacement_js_block)
    print("Updated JS broker functions")
else:
    print("Target JS block not found!")

# 3. Update renderUniverseDirectory to display Upstox Instrument Key
target_render_univ = '''    function renderUniverseDirectory() {
      const tbody = document.getElementById('universeDirectoryBody');
      tbody.innerHTML = '';
      marketData.forEach(m => {
        const tr = document.createElement('tr');
        const typeBadge = m.is_index ? '<span class="text-orange" style="font-weight:700;">INDEX</span>' : 'EQUITY';
        tr.innerHTML = `
          <td>${typeBadge}</td>
          <td><strong>${m.symbol}</strong></td>
          <td>${m.name}</td>
          <td>${m.sector || 'F&O'}</td>
          <td style="color:var(--text-muted);"><code>${m.fyers_symbol || '-'}</code></td>
          <td>${m.lot_size || 500}</td>
        `;
        tbody.appendChild(tr);
      });
    }'''

replacement_render_univ = '''    function renderUniverseDirectory() {
      const tbody = document.getElementById('universeDirectoryBody');
      tbody.innerHTML = '';
      marketData.forEach(m => {
        const tr = document.createElement('tr');
        const typeBadge = m.is_index ? '<span class="text-orange" style="font-weight:700;">INDEX</span>' : 'EQUITY';
        const upstoxKey = m.upstox_instrument_key || (m.is_index ? `NSE_INDEX|${m.name}` : `NSE_EQ|${m.symbol}`);
        tr.innerHTML = `
          <td>${typeBadge}</td>
          <td><strong>${m.symbol}</strong></td>
          <td>${m.name}</td>
          <td>${m.sector || 'F&amp;O'}</td>
          <td><code style="color:#ff8a5c; background:#1c1713; padding:2px 6px; border-radius:3px; border:1px solid #4a2818;">${upstoxKey}</code></td>
          <td>${m.lot_size || 500}</td>
        `;
        tbody.appendChild(tr);
      });
    }'''

if target_render_univ in html:
    html = html.replace(target_render_univ, replacement_render_univ)
    print("Updated renderUniverseDirectory")
else:
    print("Target renderUniverseDirectory not found!")

# 4. In window.onload, add loadBrokerConfig()
target_onload = '''    window.onload = () => {
      fetchScannerSignals();

      fetchAISentinelStatus();
      fetchOrders();

      connectWebSocket();
      loadPresets();
      loadGitHubConfig();
      checkBrokerLiveStatus();
      runScanner();
    };'''

replacement_onload = '''    window.onload = () => {
      fetchScannerSignals();

      fetchAISentinelStatus();
      fetchOrders();

      connectWebSocket();
      loadPresets();
      loadGitHubConfig();
      loadBrokerConfig();
      checkBrokerLiveStatus();
      runScanner();
    };'''

if target_onload in html:
    html = html.replace(target_onload, replacement_onload)
    print("Updated window.onload with loadBrokerConfig")
else:
    print("Target window.onload not found!")

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("Finished updating index.html for Upstox API v2!")
