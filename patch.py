import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. CSS Adds (Animations, Skeleton, Shimmer, Dark mode)
css = """
        /* ── THEME SUPPORT ── */
        [data-theme="dark"] {
            --amz-bg: #0F1111;
            --amz-white: #131921;
            --amz-card: #131921;
            --amz-text: #FFFFFF;
            --amz-text2: #CCCCCC;
            --amz-line: #3a4553;
            --amz-shadow: 0 2px 5px rgba(0,0,0,0.5);
        }
        .amz-card { transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.2s; }
        .amz-card:hover { transform: translateY(-2px); box-shadow: var(--amz-shadow2); }
        .shimmer { animation: shimmer 2s infinite linear; background: linear-gradient(to right, #f6f7f8 4%, #edeef1 25%, #f6f7f8 36%); background-size: 1000px 100%; border-radius: 4px; pointer-events: none;}
        [data-theme="dark"] .shimmer { background: linear-gradient(to right, #2a333f 4%, #3a4553 25%, #2a333f 36%); background-size: 1000px 100%; }
        @keyframes shimmer { 0% { background-position: -1000px 0 } 100% { background-position: 1000px 0 } }
        .prog-fill { transition: width 0.8s cubic-bezier(0.34, 1.56, 0.64, 1); }
        @keyframes sweep { 0% { stroke-dashoffset: 276; } }
        svg circle.wri-circle { animation: sweep 1.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }
        [data-theme="dark"] .amz-botnav, [data-theme="dark"] .amz-subnav { background: #131921; }
        [data-theme="dark"] .amz-input, [data-theme="dark"] .amz-select { background: #0F1111; color: white; border-color: #3a4553; }
        @keyframes blink-critical { 0%, 100% { border-color: #B12704; box-shadow: 0 0 12px rgba(177,39,4,0.4); } 50% { border-color: #fff0f0; box-shadow: none; } }
        .risk-card-critical { animation: blink-critical 1.5s infinite; }
        
        .pull-refresh { display: flex; align-items: center; justify-content: center; height: 0; overflow: hidden; transition: height 0.3s; color: #888C8C; font-size: 12px; }
        .pull-refresh.active { height: 40px; }
        
        .cinematic-bg { background-image: url('https://images.unsplash.com/photo-1593955259160-f0e63c0aef48?auto=format&fit=crop&q=80&w=430'); background-size: cover; background-position: center; position: relative; }
        .cinematic-bg::before { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, #131921 20%, rgba(19,25,33,0.6)); }

        /* ── LAYOUT ── */
"""
text = text.replace('        /* ── LAYOUT ── */', css)

# 2. Confetti duration
text = text.replace('animation: confettiDrop 2.4s', 'animation: confettiDrop 5s')
text = text.replace('setGs(function (s) { return Object.assign({}, s, { confetti: false }); }); }, 3000);', 'setGs(function (s) { return Object.assign({}, s, { confetti: false }); }); }, 6000);')
text = text.replace('setGs(s => ({ ...s, confetti: false })), 3000);', 'setGs(s => ({ ...s, confetti: false })), 6000);')

# 3. WRI Gauge Class (Registration & Worker Policy)
text = text.replace(
    "strokeDashoffset: dash, strokeLinecap: 'round', transform: 'rotate(-90 50 50)'",
    "strokeDashoffset: dash, strokeLinecap: 'round', transform: 'rotate(-90 50 50)', className: 'wri-circle'"
)

# 4. Cinematic Landing + Explainer + Trust Footer
entry_old = """h('div', { style: { background: 'linear-gradient(135deg,#232F3E,#131921)', borderRadius: 8, padding: '20px 18px', marginBottom: 12, position: 'relative', overflow: 'hidden' } },"""
entry_new = """h('div', { className: 'cinematic-bg', style: { borderRadius: 8, padding: '100px 18px 20px', marginBottom: 16, overflow: 'hidden', boxShadow: '0 8px 24px rgba(0,0,0,0.3)' } },
                            h('div', { style: { position: 'relative', zIndex: 1 } },"""
text = text.replace(entry_old, entry_new, 1)

text = text.replace("""h('p', { style: { fontSize: 13, color: '#ccc', lineHeight: 1.6, marginBottom: 16 } }, t('hero_s', lang)),""", """h('p', { style: { fontSize: 13, color: '#ccc', lineHeight: 1.6, marginBottom: 16 } }, t('hero_s', lang)),
                                h('div', { style: { background: 'rgba(255,255,255,0.05)', borderRadius: 8, padding: 12, marginBottom: 16, border: '1px solid rgba(255,255,255,0.1)' } },
                                    h('div', { style: { color: 'white', fontWeight: 700, fontSize: 13, marginBottom: 10 } }, 'How it works:'),
                                    h('div', { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' } },
                                        h('div', { style: { textAlign: 'center', width: '30%' } }, h('div', { style: { fontSize: 20 } }, '📱'), h('div', { style: { fontSize: 10, color: '#ccc', marginTop: 4 } }, '1. Register')),
                                        h('div', { style: { color: '#007185', fontSize: 12 } }, '→'),
                                        h('div', { style: { textAlign: 'center', width: '30%' } }, h('div', { style: { fontSize: 20 } }, '🛡️'), h('div', { style: { fontSize: 10, color: '#ccc', marginTop: 4 } }, '2. Get Covered')),
                                        h('div', { style: { color: '#007185', fontSize: 12 } }, '→'),
                                        h('div', { style: { textAlign: 'center', width: '30%' } }, h('div', { style: { fontSize: 20 } }, '💸'), h('div', { style: { fontSize: 10, color: '#ccc', marginTop: 4 } }, '3. Auto-Pay'))
                                    )
                                ),""")

# Adding Trust Footer at bottom of Entry screen
text = text.replace("h('button', { className: 'btn-secondary', onClick: function () { setShowAdmin(true); }, style: { width: '100%' } }, t('signin_adm', lang))", """h('button', { className: 'btn-secondary', onClick: function () { setShowAdmin(true); }, style: { width: '100%' } }, t('signin_adm', lang)),
                            h('div', { style: { marginTop: 30, textAlign: 'center', fontSize: 10, color: '#888C8C' } },
                                h('div', { style: { marginBottom: 4 } }, '🔒 Verified by IRDAI Sandbox · ISO 27001 Certified'),
                                h('div', null, 'Your data is encrypted and securely stored.')
                            )""")

# 5. Pull to refresh for WorkerApp
worker_app_inject = """function WorkerApp({ navigate, gs, setGs }) {
            const [tab, setTab] = useState('home');
            const [payouts, setPayouts] = useState(PAYOUTS_BASE.map(p => ({ ...p })));
            const [toast, setToast] = useState(null);
            const [refreshing, setRefreshing] = useState(false);
            const worker = WORKERS[0];
            const covered = gs.covered || false;
            
            function onPull() {
                setRefreshing(true);
                setTimeout(() => setRefreshing(false), 1500);
            }
"""
text = text.replace("function WorkerApp({ navigate, gs, setGs }) {\n            const [tab, setTab] = useState('home');", worker_app_inject.replace("function WorkerApp({ navigate, gs, setGs }) {", ""))
text = text.replace("h(AmzTopNav, {}),", """h(AmzTopNav, {}),
                    h('div', { className: 'pull-refresh ' + (refreshing ? 'active' : '') }, h(Spinner), h('span', {style: {marginLeft: 8}}, 'Refreshing data...')),""")

# 6 & 7. Admin Dashboard clock & Admin Topbar export report
admin_app_top_old = """// Admin topbar
                    h('div', { style: { background: '#232F3E', padding: '12px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, zIndex: 50, borderBottom: '1px solid rgba(255,255,255,.08)' } },
                        h('div', { style: { color: 'white', fontSize: 15, fontWeight: 700 } }, (nav.find(n => n.id === tab) || { l: 'Dashboard' }).l),
                        h('div', { style: { display: 'flex', alignItems: 'center', gap: 12 } },
                            h('div', { style: { display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: '#067D62', background: 'rgba(6,125,98,.15)', padding: '4px 10px', borderRadius: 3 } },
                                h('span', { style: { width: 6, height: 6, background: '#067D62', borderRadius: '50%', display: 'inline-block' }, className: 'blink' }),
                                'Live'
                            ),
                            h('div', { style: { width: 30, height: 30, borderRadius: '50%', background: '#FF9900', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 12, color: '#232F3E' } }, 'AD')
                        )
                    ),"""
admin_app_top_new = """// Admin topbar
                    h('div', { style: { background: '#232F3E', padding: '12px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, zIndex: 50, borderBottom: '1px solid rgba(255,255,255,.08)' } },
                        h('div', { style: { color: 'white', fontSize: 15, fontWeight: 700 } }, (nav.find(n => n.id === tab) || { l: 'Dashboard' }).l),
                        h('div', { style: { display: 'flex', alignItems: 'center', gap: 14 } },
                            h('button', { style: { background: 'transparent', border: '1px solid rgba(255,255,255,.3)', color: 'white', borderRadius: 3, padding: '4px 10px', fontSize: 11, cursor: 'pointer' }, onClick: () => alert('Report exporting as CSV...') }, '📥 Export Report'),
                            h('div', { style: { color: '#ccc', fontFamily: 'monospace', fontSize: 12 } }, new Date().toLocaleTimeString('en-IN')),
                            h('div', { style: { display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: '#067D62', background: 'rgba(6,125,98,.15)', padding: '4px 10px', borderRadius: 3 } },
                                h('span', { style: { width: 6, height: 6, background: '#067D62', borderRadius: '50%', display: 'inline-block' }, className: 'blink' }),
                                'Live'
                            ),
                            h('div', { style: { width: 30, height: 30, borderRadius: '50%', background: '#FF9900', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 12, color: '#232F3E' } }, 'AD')
                        )
                    ),"""
text = text.replace(admin_app_top_old, admin_app_top_new)

# Force the clock to strictly update inside AdminApp
adminapp_old = "function AdminApp({ navigate, gs, setGs }) {\n            const [tab, setTab] = useState('dashboard');"
adminapp_new = """function AdminApp({ navigate, gs, setGs }) {\n            const [tab, setTab] = useState('dashboard');\n            const [, setTick] = useState(0);\n            useEffect(() => { const t = setInterval(()=>setTick(x=>x+1), 1000); return ()=>clearInterval(t); }, []);"""
text = text.replace(adminapp_old, adminapp_new)

# 8. Admin Live Event Feed setInterval scrolling ticker
ticker_old = """h('div', { style: { height: 180, overflow: 'hidden' } },
                            h('div', { className: 'scrollup' },
                                [...feed, ...feed].map((item, i) =>
                                    h('div', { key: i, style: { padding: '6px 0', borderBottom: '1px solid #f5f5f5', display: 'flex', gap: 8, alignItems: 'flex-start' } },"""
ticker_new = """h('div', { style: { height: 180, overflow: 'hidden', position: 'relative' } },
                            h('div', { className: 'scrollup' },
                                [...feed, ...feed].map((item, i) =>
                                    h('div', { key: i, style: { padding: '6px 0', borderBottom: '1px solid var(--amz-line)', display: 'flex', gap: 8, alignItems: 'flex-start' } },"""
text = text.replace(ticker_old, ticker_new)

# Wait, instead of just repeating, let's create a functional `feedStream` in ADash
adash_old = "const [simResult, setSimResult] = useState(null);"
adash_new = """const [simResult, setSimResult] = useState(null);
            const [liveFeed, setLiveFeed] = useState(feed);
            useEffect(() => {
                const timer = setInterval(() => {
                    setLiveFeed(prev => {
                        const next = [...prev];
                        const msgs = ['Fraud flag: New account spike (Powai)', 'Auto-payout ₹320 (Andheri West)', 'Trigger monitoring AQI 320 in Delhi'];
                        next.unshift({ t: new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}), msg: msgs[Math.floor(Math.random()*msgs.length)], c: '#007185' });
                        if(next.length > 15) next.pop();
                        return next;
                    });
                }, 4000);
                return () => clearInterval(timer);
            }, []);"""
text = text.replace(adash_old, adash_new)
text = text.replace("[...feed, ...feed].map", "liveFeed.map")
text = text.replace("className: 'scrollup'", "style: { transition: 'transform 0.5s ease' }")

# Risk map pulse critical
text = re.sub(r'className: \'amz-card\', style: \{ padding: 12, border: `2px solid \$\{(z.zone === worker.zone) \? \'#FF9900\' : \'#D5D9D9\'\}` \}',
              r"className: 'amz-card ' + (z.risk === 'critical' ? 'risk-card-critical' : ''), style: { padding: 12, border: `2px solid ${z.zone === worker.zone ? '#FF9900' : '#D5D9D9'}` }", text)

# Fraud Queue ML cards
ml_insights_old = """h('div', { style: { background: '#fffbf2', border: '1px solid #f0c14b', borderRadius: 6, padding: 16, marginTop: 8 } },
                    h('div', { style: { fontWeight: 700, color: '#8a6116', marginBottom: 6, fontSize: 13 } }, '🤖 ML Fraud Insights'),
                    h('div', { style: { fontSize: 13, color: '#6b4a08', lineHeight: 1.7 } }, 'Top pattern this week: GPS spoofing in Dharavi zone (4 attempts, 8.4km average gap). New account spike: 3 accounts under 15 days filed AQI claims. Isolation Forest confidence: 94%. Recommendation: Increase minimum account age for AQI claims to 30 days.')
                )"""

ml_insights_new = """h('div', { style: { background: '#fffbf2', border: '1px solid #f0c14b', borderRadius: 6, padding: 16, marginTop: 12 } },
                    h('div', { style: { fontWeight: 700, color: '#8a6116', marginBottom: 12, fontSize: 14 } }, '🤖 Auto-Generated ML Insights'),
                    h('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 } },
                        [{t: 'Pattern: GPS Spoofing', d: 'Dharavi zone (4 attempts, 8.4km avg gap)', c: 94}, {t: 'Anomaly: Account Age', d: 'Spike in claims from <15d accounts (AQI)', c: 88}, {t: 'Action Recommended', d: 'Increase min account age for AQI to 30d', c: 97, cColor: '#067D62'}].map(c => 
                            h('div', { key: c.t, style: { background: 'white', border: '1px solid #e7e9ea', borderRadius: 4, padding: 12 } },
                                h('div', { style: { fontSize: 12, fontWeight: 700, marginBottom: 4 } }, c.t),
                                h('div', { style: { fontSize: 11, color: '#565959', marginBottom: 8, height: 32 } }, c.d),
                                h('div', { style: { display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#888C8C', marginBottom: 4 } }, h('span', null, 'AI Confidence'), h('span', {style: {fontWeight:700, color: c.cColor || '#007185'}}, c.c+'%')),
                                h('div', { className: 'prog', style: { height: 4 } }, h('div', { className: 'prog-fill', style: { width: c.c+'%', background: c.cColor || '#007185' } }))
                            )
                        )
                    )
                )"""
text = text.replace(ml_insights_old, ml_insights_new)

# Analytics charts date range filter (add to AAnalytics)
aanalytics_old = """function AAnalytics() {
            const rechartsReady = useRechartsReady();"""
aanalytics_new = """function AAnalytics() {
            const rechartsReady = useRechartsReady();
            const [range, setRange] = useState('mtd');"""
text = text.replace(aanalytics_old, aanalytics_new)

filter_btns = """h('div', { style: { display: 'flex', justifyContent: 'flex-end', gap: 6, marginBottom: 16 } },
                    [['week', 'This Week'], ['mtd', 'Month to Date'], ['ytd', 'Year to Date']].map(r => 
                       h('button', { key: r[0], onClick: () => setRange(r[0]), style: { padding: '5px 12px', fontSize: 11, fontWeight: 600, borderRadius: 14, border: '1px solid #D5D9D9', background: range === r[0] ? '#232F3E' : 'white', color: range === r[0] ? 'white' : '#565959', cursor: 'pointer' } }, r[1])
                    )
                ),"""
text = text.replace("h('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 } },", filter_btns + "h('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 } },", 1)

# Dark mode functionality and Top Nav toggle
root_old = """function Root() {
            var [gs, setGsRaw] = useState(function () {"""
root_new = """function Root() {
            var [theme, setTheme] = useState("light");
            useEffect(() => { document.documentElement.setAttribute("data-theme", theme); }, [theme]);
            var [gs, setGsRaw] = useState(function () {
"""
text = text.replace(root_old, root_new)

# pass `theme, setTheme` implicitly through gs
text = text.replace("{ route: '/gigshield', lang: 'en', covered: false, confetti: false };", "{ route: '/gigshield', lang: 'en', covered: false, confetti: false, theme: 'light' };")

# Add Topnav night mode toggle
amztopnav_old = """rightEl || h('div', { style: { display: 'flex', gap: 12, alignItems: 'center' } },
                        h('div', { style: { position: 'relative' } },"""
amztopnav_new = """rightEl || h('div', { style: { display: 'flex', gap: 14, alignItems: 'center' } },
                        h('button', { onClick: () => document.documentElement.setAttribute("data-theme", document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark"), style: { background: 'none', border: 'none', color: '#FF9900', fontSize: 18, cursor: 'pointer' } }, '🌖'),
                        h('div', { style: { position: 'relative' } },"""
text = text.replace(amztopnav_old, amztopnav_new)

# Skeletons logic
w_home_load = """const [loading, setLoading] = useState(true);
            useEffect(() => { const t = setTimeout(()=>setLoading(false), 900); return ()=>clearTimeout(t); }, []);"""
whome_old = """function WHome({ worker, covered, activate, gs, setGs }) {
            const lang = gs.lang || 'en';"""
whome_new = """function WHome({ worker, covered, activate, gs, setGs }) {
            const lang = gs.lang || 'en';
            """ + w_home_load
text = text.replace(whome_old, whome_new)

# Apply shimmer class
text = text.replace(
    """h('div', { className: 'amz-card', style: { marginBottom: 10, overflow: 'hidden' } },""",
    """h('div', { className: 'amz-card ' + (loading ? 'shimmer' : ''), style: { marginBottom: 10, overflow: 'hidden' } },"""
)
text = text.replace(
    """h('div', { className: 'amz-card', style: { marginBottom: 10 } },""",
    """h('div', { className: 'amz-card ' + (loading ? 'shimmer' : ''), style: { marginBottom: 10 } },"""
)

# Chart Placeholder improvements (shimmer)
text = text.replace("loading chart...'", "loading chart...', className: 'shimmer'")

# Final rewrite
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Patching complete.")
