

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/03527b67-cebe-4282-8bbb-5ac6f991ee96" />






# Retail Analytics Dashboard — Built with Claude Code

A production-ready interactive analytics dashboard built in **one session** using Claude Code (Anthropic's terminal-based AI coding tool). Processes 541,909 e-commerce transactions and delivers live KPIs, product analysis, customer insights, and multi-country breakdowns.

**Live demo:** [https://data-analysis-by-using-ai-claude-code-xxwaqrtgw8nxmxpw2u5mpe.streamlit.app](https://data-analysis-by-using-ai-claude-code-xxwaqrtgw8nxmxpw2u5mpe.streamlit.app)

---

## 🚀 Quick Start

### 1. Install Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Get your API key
Visit [anthropic.com](https://anthropic.com) and create an API key.

### 3. Setup Python environment
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install dependencies (one-time)
uv pip install pandas openpyxl seaborn matplotlib jupyter streamlit plotly
```

### 4. Run the dashboard
```bash
uv run streamlit run retail_dashboard.py
```

Opens at: `http://localhost:8501`

---

## 📊 What You Get

### 6 Dashboard Tabs

| Tab | What It Shows | Controls |
|---|---|---|
| **KPIs** | Revenue, orders, customers, AOV. 7 metric cards + monthly trend. | Date range |
| **Top Products** | Revenue & units by product. Horizontal bars. | Top N slider (5-50) |
| **Top Customers** | Revenue & order count by customer. | Top N slider |
| **Sales Trend** | Revenue & orders over time. Line + bar charts. | Frequency (daily/weekly/monthly) |
| **By Country** | Choropleth map + top N country bars + pie chart. | Top N slider |
| **QA Checks** | Data quality metrics. Cancellations trend. Anomaly rows. | Date range |

### Sidebar Controls
- **Date range picker** — filter all tabs instantly
- **Top N slider** (5–50) — products, customers, countries
- **Frequency selector** — D/W/M for sales trends
- **Exclude cancellations** — toggle returns/cancelled orders on/off

---

## 📈 Data & Numbers

**Dataset:** UK Online Retail (e-commerce transactions)
- **541,909 rows** | **8 columns** | **13 months** (Dec 2010 – Dec 2011)

**Key Metrics:**
- Gross revenue (sales): **£10.7M**
- Total returns: **−£919K**
- Net revenue: **£9.7M**
- Unique customers: **4,372**
- Unique products: **4,070**
- Unique countries: **37**

**Data quality:**
- Cancellations flagged (not deleted): 10,624 (1.96%)
- Missing customer ID: 135,080 (24.93%)
- Anomalous prices: 2,517 (0.46%)

---

## 📂 Project Structure

```
tech-talk-demo-project/
├── README.md                      # This file
├── PROJECT_CONTEXT.md             # Detailed project documentation
├── CLAUDE.md                       # Claude Code project rules
│
├── Online Retail.xlsx             # Raw data (541,909 rows)
│
├── explore.py                     # Step 1: Data exploration
├── data_prep.py                   # Step 2: Clean, transform, flag
├── retail_dashboard.py            # Step 3: Live Streamlit app
│
├── .venv/                         # Python virtual environment
└── output/
    ├── Claude_Code_Tech_Talk_v4.pptx   # 13-slide presentation (+ speaker notes)
    └── gamma_prompt.txt                # Gamma.app template
```

---

## 🔧 How to Use

### Explore the data
```bash
uv run --python .venv/Scripts/python.exe explore.py
```
Output: columns, data types, nulls, date range verification.

### Prepare the data
```bash
uv run --python .venv/Scripts/python.exe data_prep.py
```
Output: adds calculated columns, flags cancellations, prints data quality summary.

### Launch the dashboard
```bash
uv run streamlit run retail_dashboard.py
```
Opens interactive web app — sidebar controls update all tabs live.

---

## 🎯 Built with Claude Code

**What Claude Code did autonomously:**
- ✅ Read the project structure and requirements
- ✅ Wrote 3 production-ready Python scripts
- ✅ Ran each script to verify output
- ✅ Fixed errors (Unicode codec, Plotly layout)
- ✅ Created reusable, no-boilerplate code

**What I did:**
- Gave plain English instructions
- Verified the financial calculations
- Checked data quality flags

**Result:** Full working dashboard in one session. Zero manual coding.

---

## 🔑 Key Design Decisions

### No Rows Deleted
Cancellations and returns are flagged, not removed. Preserves audit trail and business context.

### 6-Tab Architecture
- **KPIs & Trend** — executive summary
- **Products & Customers** — business drill-down
- **By Country** — geographic insights
- **QA Checks** — data quality transparency

### Plotly Over Matplotlib
Interactive hover, choropleth maps, responsive design — users can explore data themselves.

### Context-First Approach
3 scripts (explore → prep → dashboard) instead of one monolith. Each can run independently.

---

## 📋 For the Tech Talk

This project demonstrates **6 Levels of Claude Code Mastery:**
1. **Level 1: Commander** — give instructions with context
2. **Level 2: Planner** — use `/plan` before building
3. **Level 3: Context Engineer** — use CLAUDE.md for project rules
4. **Level 4: Tool Master** — connect external tools via MCP
5. **Level 5: Skilled Craftsman** — build custom skills
6. **Level 6: Orchestrator** — run agent teams in parallel

This project hits **Levels 1–3**. Fully reusable.

---

## 🔐 Environment Variables

No secrets needed for the demo. In production:
- Set `ANTHROPIC_API_KEY` in `.env` or environment
- Never commit credentials

---

## 📚 Learn More

- **Deep dive into Claude Code architecture:** [YouTube video](https://youtube.com/watch?v=s2KVJirRoRs)
- **PROJECT_CONTEXT.md** — detailed breakdown of data transformations, KPIs, and design
- **CLAUDE.md** — project rules and standards that Claude Code follows

---

## 🛠 Extending This Project

### Add cohort analysis
Track customer acquisition → retention over time.

### Add forecasting
Use historical trends to forecast next month's revenue.

### Add export
Let users download filtered data as CSV or Excel.

### Add authentication
Restrict access by country or product segment.

### Swap the dataset
The pattern is reusable. Replace `Online Retail.xlsx` with your own dataset — adapt `data_prep.py` transforms to your schema, and you have a new dashboard.

---

## 💡 Command Reference

```bash
# Setup (Windows)
.venv\Scripts\activate
uv pip install pandas openpyxl seaborn matplotlib jupyter streamlit plotly

# Explore
uv run --python .venv/Scripts/python.exe explore.py

# Prepare
uv run --python .venv/Scripts/python.exe data_prep.py

# Dashboard
uv run streamlit run retail_dashboard.py

# View Streamlit logs
streamlit run retail_dashboard.py --logger.level=debug
```

---

## 📞 Support

This project was built as a tech talk demo. For questions about:
- **Claude Code:** Visit [code.claude.com](https://code.claude.com)
- **Streamlit:** Visit [streamlit.io](https://streamlit.io)
- **Plotly:** Visit [plotly.com](https://plotly.com)
- **This project:** See PROJECT_CONTEXT.md for full documentation

---

## 📄 License

Demo project for educational purposes. Data sourced from public e-commerce datasets.

**Created:** March 31, 2026
**Status:** Ready for live demonstration
**Built with:** Claude Code (1 session)
