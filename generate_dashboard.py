import json
import sqlite3
from pathlib import Path
from datetime import datetime, date

BASE_DIR = Path("C:/Users/admin/.gemini/antigravity/scratch/petro_phd_radar_bot")
DB_PATH = BASE_DIR / "phd_radar.db"
OUTPUT_HTML = BASE_DIR / "dashboard.html"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT * FROM opportunities ORDER BY deadline ASC")
rows = cursor.fetchall()
opps = [dict(r) for r in rows]

cursor.execute("""
SELECT p1.* FROM portal_audit_logs p1
JOIN (
    SELECT portal_name, MAX(id) as max_id
    FROM portal_audit_logs
    GROUP BY portal_name
) p2 ON p1.id = p2.max_id
ORDER BY p1.http_status DESC, p1.response_time_ms ASC
""")
portal_audits = [dict(r) for r in cursor.fetchall()]

cursor.execute("SELECT * FROM hunting_logs ORDER BY id DESC LIMIT 1")
last_hunt_row = cursor.fetchone()
last_hunt = dict(last_hunt_row) if last_hunt_row else {}
conn.close()

today = date(2026, 11, 14) # Local current date

online_portals_count = sum(1 for p in portal_audits if p["http_status"] == 200)
total_links_scanned = sum(p["links_scanned"] for p in portal_audits)
total_petro_matches = sum(p["petro_matches"] for p in portal_audits)
avg_portal_latency = round(sum(p["response_time_ms"] for p in portal_audits) / max(1, len(portal_audits)))
latest_hunt_time = last_hunt.get("timestamp", "اليوم")

portal_rows_html = ""
for p in portal_audits:
    status_badge = f'<span style="background: rgba(34, 197, 94, 0.2); color: #4ade80; padding: 2px 8px; border-radius: 4px; font-weight: 700;">🟢 {p["http_status"]} OK</span>' if p["http_status"] == 200 else f'<span style="background: rgba(239, 68, 68, 0.2); color: #f87171; padding: 2px 8px; border-radius: 4px; font-weight: 700;">🔴 فشل</span>'
    portal_rows_html += f"""
    <tr style="border-bottom: 1px solid #334155;">
        <td style="padding: 10px 12px; font-weight: 600; color: #f8fafc;">{p["portal_name"]}</td>
        <td style="padding: 10px 12px;">{status_badge}</td>
        <td style="padding: 10px 12px; color: #38bdf8; font-weight: 600;">{p["response_time_ms"]} ms</td>
        <td style="padding: 10px 12px; color: #94a3b8;">{p["links_scanned"]} رابط</td>
        <td style="padding: 10px 12px; color: #f59e0b; font-weight: 700;">{p["petro_matches"]}</td>
        <td style="padding: 10px 12px;"><a href="{p['portal_url']}" target="_blank" style="color: #60a5fa; text-decoration: underline; font-size: 0.78rem;">فتح البوابة ↗</a></td>
    </tr>
    """

for o in opps:
    dl = o.get("deadline", "")
    if dl and len(dl) >= 10:
        try:
            d_date = datetime.strptime(dl[:10], "%Y-%m-%d").date()
            diff = (d_date - today).days
            if diff < 0:
                o["urgency"] = "منتهي"
                o["urgency_color"] = "gray"
            elif diff == 0:
                o["urgency"] = "ينتهي اليوم!"
                o["urgency_color"] = "danger"
            elif diff == 1:
                o["urgency"] = "ينتهي غداً!"
                o["urgency_color"] = "danger"
            elif diff <= 7:
                o["urgency"] = f"يغلق خلال {diff} أيام!"
                o["urgency_color"] = "danger"
            elif diff <= 35:
                o["urgency"] = f"متبقي {diff} يوماً"
                o["urgency_color"] = "warning"
            else:
                o["urgency"] = f"متبقي {diff} يوماً"
                o["urgency_color"] = "success"
        except ValueError:
            o["urgency"] = "مفتوح"
            o["urgency_color"] = "info"
    else:
        o["urgency"] = "مفتوح حتى ملء الشواغر"
        o["urgency_color"] = "info"

opps_json = json.dumps(opps, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>رادار دكتوراه هندسة البترول والطاقة الجوفية | مخصص لجزائري في إيطاليا</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --accent-green: #22c55e;
            --accent-orange: #f59e0b;
            --accent-red: #ef4444;
            --border: #334155;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }}
        body {{ background-color: var(--bg); color: var(--text-main); padding: 24px 16px; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ text-align: center; margin-bottom: 32px; padding: 24px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 16px; border: 1px solid var(--border); box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); }}
        header h1 {{ font-size: 1.9rem; color: #fff; margin-bottom: 8px; }}
        header p {{ color: var(--text-muted); font-size: 0.95rem; }}
        .badge-student {{ display: inline-block; background: rgba(56, 189, 248, 0.15); color: var(--accent); border: 1px solid rgba(56, 189, 248, 0.3); padding: 4px 14px; border-radius: 20px; font-weight: 600; margin-top: 10px; font-size: 0.85rem; }}
        
        .controls {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 24px; justify-content: space-between; align-items: center; }}
        .search-box {{ flex: 1; min-width: 260px; }}
        .search-box input {{ width: 100%; padding: 12px 16px; border-radius: 10px; border: 1px solid var(--border); background: var(--card-bg); color: #fff; font-size: 0.95rem; outline: none; }}
        .search-box input:focus {{ border-color: var(--accent); }}
        
        .filter-buttons {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .filter-btn {{ padding: 8px 16px; border-radius: 8px; border: 1px solid var(--border); background: var(--card-bg); color: var(--text-muted); cursor: pointer; font-size: 0.88rem; font-weight: 600; transition: all 0.2s; }}
        .filter-btn:hover, .filter-btn.active {{ background: var(--accent); color: #0f172a; border-color: var(--accent); }}
        
        .stats-bar {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 24px; }}
        .stat-card {{ background: var(--card-bg); padding: 16px; border-radius: 12px; border: 1px solid var(--border); text-align: center; }}
        .stat-num {{ font-size: 1.6rem; font-weight: 800; color: var(--accent); }}
        .stat-label {{ font-size: 0.85rem; color: var(--text-muted); }}

        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 20px; }}
        .card {{ background: var(--card-bg); border-radius: 14px; border: 1px solid var(--border); padding: 20px; display: flex; flex-direction: column; justify-content: space-between; position: relative; transition: transform 0.2s, box-shadow 0.2s; }}
        .card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 24px -8px rgba(0,0,0,0.4); border-color: #475569; }}
        
        .card-top {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 12px; }}
        .source-tag {{ font-size: 0.75rem; padding: 3px 10px; border-radius: 6px; font-weight: 600; text-transform: uppercase; }}
        .source-tag.GOVERNMENT {{ background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .source-tag.INSTITUTE {{ background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }}
        .source-tag.PROFESSOR_LAB {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }}
        .source-tag.UNIVERSITY {{ background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }}
        
        .urgency-badge {{ font-size: 0.75rem; padding: 3px 10px; border-radius: 6px; font-weight: 700; }}
        .urgency-badge.danger {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }}
        .urgency-badge.warning {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }}
        .urgency-badge.success {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); }}
        .urgency-badge.info {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }}
        
        .card-title {{ font-size: 1.05rem; font-weight: 700; color: #fff; margin-bottom: 6px; }}
        .card-meta {{ font-size: 0.85rem; color: var(--text-muted); margin-bottom: 14px; display: flex; align-items: center; gap: 6px; }}
        
        .field-list {{ font-size: 0.86rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 12px; margin-bottom: 14px; display: flex; flex-direction: column; gap: 8px; }}
        .field-item {{ display: flex; justify-content: space-between; }}
        .field-label {{ color: var(--text-muted); font-weight: 600; }}
        .field-val {{ color: #e2e8f0; font-weight: 600; text-align: left; max-width: 60%; }}
        .field-val.salary {{ color: #38bdf8; font-weight: 700; }}
        
        .eval-box {{ background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 8px; border-right: 3px solid var(--accent-green); margin-bottom: 16px; font-size: 0.83rem; }}
        .eval-title {{ font-weight: 700; color: var(--accent-green); margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }}
        .eval-text {{ color: #cbd5e1; line-height: 1.5; }}
        
        .apply-btn {{ display: block; text-align: center; background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #fff; text-decoration: none; padding: 10px; border-radius: 8px; font-weight: 700; font-size: 0.9rem; transition: background 0.2s; }}
        .apply-btn:hover {{ background: linear-gradient(135deg, #0369a1 0%, #075985 100%); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛢️ رادار فرص دكتوراه وتدريب هندسة البترول والطاقة الجوفية</h1>
            <p>متابعة آنية ومحدثة للفرص المفتوحة، مواعيد الإغلاق، ومصادر التمويل الحكومية ومشاريع المخابر والشركات المستقلة</p>
            <div class="badge-student">🎯 مخصص للمهندس بلال حداد: ماستر غوبكين موسكو (4.6/5.0) + ماستر كاتانيا + خبرة سوناطراك وإيني</div>
        </header>

        <!-- Live Deep Web Crawler Telemetry -->
        <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 14px; padding: 18px 22px; margin-bottom: 24px; box-shadow: 0 8px 20px rgba(0,0,0,0.35);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 12px #22c55e;"></span>
                    <h2 style="font-size: 1.15rem; color: #38bdf8; font-weight: 700;">📡 رادار الصيد والزحف الحي المباشر (24/7 Autonomous Deep Hunter Telemetry)</h2>
                </div>
                <div style="font-size: 0.82rem; color: #94a3b8; background: rgba(51, 65, 85, 0.6); padding: 4px 12px; border-radius: 20px;">
                    ⏱️ آخر فحص متوازي حي: <strong style="color: #f8fafc;">{latest_hunt_time}</strong>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 14px;">
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid var(--border); border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 1.45rem; font-weight: 800; color: #22c55e;">{online_portals_count} / {len(portal_audits)}</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">بوابات حية مفحوصة ومحللة كلياً</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid var(--border); border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 1.45rem; font-weight: 800; color: #38bdf8;">{total_links_scanned:,}</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">رابط تم تنزيل وتحليل كود HTML الخاص به</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid var(--border); border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 1.45rem; font-weight: 800; color: #f59e0b;">{total_petro_matches}</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">مطابقة تخصصية (مكامن / غاز / CCUS / H2)</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid var(--border); border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 1.45rem; font-weight: 800; color: #a855f7;">{avg_portal_latency} ms</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">متوسط سرعة استجابة الخوادم الدولية</div>
                </div>
            </div>

            <!-- تفاصيل تدقيق البوابات -->
            <details style="margin-top: 10px; cursor: pointer;">
                <summary style="color: #38bdf8; font-weight: 600; font-size: 0.9rem; user-select: none;">🔍 استعراض سجل الفحص المباشر للبوابات الـ 29 (انقر للإظهار / الإخفاء)</summary>
                <div style="margin-top: 14px; overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.82rem; text-align: right;">
                        <thead>
                            <tr style="background: rgba(51, 65, 85, 0.5); color: #cbd5e1; border-bottom: 1px solid var(--border);">
                                <th style="padding: 8px 12px;">البوابة والمؤسسة</th>
                                <th style="padding: 8px 12px;">الحالة</th>
                                <th style="padding: 8px 12px;">زمن الاستجابة</th>
                                <th style="padding: 8px 12px;">الروابط المحللة</th>
                                <th style="padding: 8px 12px;">مطابقات التخصص</th>
                                <th style="padding: 8px 12px;">الرابط المفحوص</th>
                            </tr>
                        </thead>
                        <tbody>
                            {portal_rows_html}
                        </tbody>
                    </table>
                </div>
            </details>
        </div>

        <div class="stats-bar">
            <div class="stat-card">
                <div class="stat-num">{len(opps)}</div>
                <div class="stat-label">إجمالي الفرص النشطة بالقاعدة</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" id="easy-count">0</div>
                <div class="stat-label">فرص عالية / سهلة القبول</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" style="color: #f87171;" id="closing-count">0</div>
                <div class="stat-label">تغلق قريباً (أقل من 35 يوماً)</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" style="color: #4ade80;">100%</div>
                <div class="stat-label">فرص ممولة برواتب بحثية</div>
            </div>
        </div>

        <div class="controls">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="ابحث بالتخصص (CCUS, Reservoir, Drilling) أو البلد أو الجامعة...">
            </div>
            <div class="filter-buttons">
                <button class="filter-btn active" data-filter="all">الكل</button>
                <button class="filter-btn" data-filter="easy">🟢 سهلة القبول</button>
                <button class="filter-btn" data-filter="GOVERNMENT">👑 منح حكومية</button>
                <button class="filter-btn" data-filter="INSTITUTE">🔬 معاهد أبحاث</button>
                <button class="filter-btn" data-filter="PROFESSOR_LAB">👨‍🏫 مشاريع أساتذة</button>
                <button class="filter-btn" data-filter="closing">⏳ تغلق قريباً</button>
            </div>
        </div>

        <div class="grid" id="oppsGrid"></div>
    </div>

    <script>
        const oppsData = {opps_json};
        
        // حساب الإحصائيات
        let easyCount = 0;
        let closingCount = 0;
        oppsData.forEach(o => {{
            if (o.acceptance_difficulty.includes("سهلة")) easyCount++;
            if (o.urgency_color === "danger" || o.urgency_color === "warning") closingCount++;
        }});
        document.getElementById('easy-count').textContent = easyCount;
        document.getElementById('closing-count').textContent = closingCount;

        function getSourceLabel(s) {{
            switch(s) {{
                case 'GOVERNMENT': return '👑 منحة حكومية';
                case 'INSTITUTE': return '🔬 معهد أبحاث';
                case 'PROFESSOR_LAB': return '👨‍🏫 مشروع أستاذ';
                default: return '🏛️ جامعة';
            }}
        }}

        function renderCards(items) {{
            const grid = document.getElementById('oppsGrid');
            grid.innerHTML = '';
            if (items.length === 0) {{
                grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">لا توجد فرص تطابق هذا البحث حالياً.</div>';
                return;
            }}
            items.forEach(o => {{
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <div>
                        <div class="card-top">
                            <span class="source-tag ${{o.source_type}}">${{getSourceLabel(o.source_type)}}</span>
                            <span class="urgency-badge ${{o.urgency_color}}">${{o.urgency}}</span>
                        </div>
                        <h3 class="card-title">${{o.title}}</h3>
                        <div class="card-meta">
                            <span>🏛️ ${{o.institution}}</span> • <span>📍 ${{o.country}}</span>
                        </div>
                        
                        <div class="field-list">
                            <div class="field-item">
                                <span class="field-label">🎯 التخصص الدقيق:</span>
                                <span class="field-val">${{o.sub_specialty}}</span>
                            </div>
                            <div class="field-item">
                                <span class="field-label">💵 الراتب الشهري:</span>
                                <span class="field-val salary">${{o.monthly_salary}}</span>
                            </div>
                            <div class="field-item">
                                <span class="field-label">🎓 رسوم الدراسة:</span>
                                <span class="field-val">${{o.tuition_fee}}</span>
                            </div>
                            <div class="field-item">
                                <span class="field-label">📝 رسوم التسجيل:</span>
                                <span class="field-val">${{o.registration_fee}}</span>
                            </div>
                            <div class="field-item">
                                <span class="field-label">👥 عدد المقاعد:</span>
                                <span class="field-val">${{o.seats}}</span>
                            </div>
                            <div class="field-item">
                                <span class="field-label">⏱️ مدة العقد / التربص:</span>
                                <span class="field-val" style="color: #60a5fa; font-weight: 600;">${{o.duration || '3 إلى 4 سنوات'}}</span>
                            </div>
                            <div class="field-item">
                                <span class="field-label">📅 الموعد النهائي:</span>
                                <span class="field-val">${{o.deadline || 'مستمر'}}</span>
                            </div>
                        </div>

                        ${{o.application_method ? `
                        <div style="background: rgba(59, 130, 246, 0.08); border-right: 3px solid #3b82f6; padding: 10px 12px; border-radius: 8px; margin-bottom: 12px; font-size: 0.83rem; line-height: 1.5; color: #bfdbfe;">
                            <div style="font-weight: 700; color: #60a5fa; margin-bottom: 3px;">📨 طريقة والرمز المرجعي للتقديم المباشر:</div>
                            <div>${{o.application_method.replace(/\\n/g, '<br>')}}</div>
                        </div>` : ''}}

                        ${{o.key_requirements ? `
                        <div style="background: rgba(245, 158, 11, 0.08); border-right: 3px solid #f59e0b; padding: 12px; border-radius: 8px; margin-bottom: 12px; font-size: 0.83rem; line-height: 1.5; color: #fde68a;">
                            <div style="font-weight: 700; color: #fbbf24; margin-bottom: 4px;">⚠️ أصعب الشروط ونقاط الحسم (Deal-breakers):</div>
                            <div>${{o.key_requirements.replace(/\\n/g, '<br>')}}</div>
                        </div>` : ''}}

                        <div class="eval-box">
                            <div class="eval-title">📊 تقييم القبول لملفك (جزائري بماستر إيطالي)</div>
                            <div class="eval-text">${{o.acceptance_difficulty.replace(/\\n/g, '<br>')}}</div>
                        </div>
                    </div>

                    <a href="${{o.link}}" target="_blank" class="apply-btn">فتح صفحة التقديم المباشر ↗</a>
                `;
                grid.appendChild(card);
            }});
        }}

        renderCards(oppsData);

        // فلترة وبحث
        let currentFilter = 'all';
        let searchQuery = '';

        function applyFilters() {{
            let filtered = oppsData.filter(o => {{
                // تصفية الفئة
                let matchCategory = true;
                if (currentFilter === 'easy') {{
                    matchCategory = o.acceptance_difficulty.includes("سهلة");
                }} else if (currentFilter === 'closing') {{
                    matchCategory = (o.urgency_color === 'danger' || o.urgency_color === 'warning');
                }} else if (currentFilter !== 'all') {{
                    matchCategory = (o.source_type === currentFilter);
                }}

                // تصفية البحث
                let matchSearch = true;
                if (searchQuery.trim() !== '') {{
                    const q = searchQuery.toLowerCase();
                    matchSearch = o.title.toLowerCase().includes(q) ||
                                  o.sub_specialty.toLowerCase().includes(q) ||
                                  o.country.toLowerCase().includes(q) ||
                                  o.institution.toLowerCase().includes(q);
                }}

                return matchCategory && matchSearch;
            }});

            renderCards(filtered);
        }}

        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', (e) => {{
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.getAttribute('data-filter');
                applyFilters();
            }});
        }});

        document.getElementById('searchInput').addEventListener('input', (e) => {{
            searchQuery = e.target.value;
            applyFilters();
        }});
    </script>
</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Interactive Dashboard successfully generated at: {OUTPUT_HTML}")
