APP_CSS = """
<style>
:root {
    --bg: #f8fafc;
    --panel: #ffffff;
    --panel2: #f1f5f9;
    --text: #0f172a;
    --muted: #475569;
    --line: #e2e8f0;
    --soft: #f8fafc;
    --white: #ffffff;
    --black: #0f172a;
    --primary: #2563eb;
    --secondary: #ea580c;
}

.stApp {
    background: radial-gradient(at 0% 0%, rgba(37, 99, 235, 0.04) 0px, transparent 50%), 
                radial-gradient(at 100% 0%, rgba(234, 88, 12, 0.04) 0px, transparent 50%), 
                #f8fafc;
    color: var(--text);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1320px;
}

section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: var(--text);
}

[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {
    color: #334155;
}

.small-muted, .stCaptionContainer, .stCaptionContainer p {
    color: var(--muted) !important;
    font-size: 0.88rem;
}

.hero {
    border: 1px solid #e2e8f0;
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.03), rgba(234, 88, 12, 0.01));
    border-radius: 24px;
    padding: 28px 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.02);
    margin-bottom: 22px;
}

.hero h1 {
    margin: 0;
    font-size: 2.45rem;
    letter-spacing: -0.04em;
    color: #0f172a;
}

.hero p {
    margin-top: 10px;
    max-width: 920px;
    color: #475569;
    font-size: 1.05rem;
}

/* Metric Cards & Panels */
.metric-card, .panel, .evidence-card, .risk-card {
    border: 1px solid #e2e8f0 !important;
    background: #ffffff !important;
    border-radius: 18px !important;
    padding: 18px !important;
    box-shadow: 0 8px 20px rgba(0,0,0,0.02) !important;
    color: #1e293b !important;
    margin-bottom: 12px;
}

.metric-card .label {
    color: #64748b !important;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}

.metric-card .value {
    color: #0f172a !important;
    font-size: 2.2rem;
    font-weight: 800;
    margin-top: 6px;
}

/* Status Badging */
.status-pill {
    display: inline-flex;
    align-items: center;
    padding: 5px 12px;
    border-radius: 999px;
    border: 1px solid #e2e8f0;
    color: #475569;
    background: #f8fafc;
    margin: 4px 6px 4px 0;
    font-size: 0.82rem;
    font-weight: 600;
}

.good {
    border-color: #bbf7d0 !important;
    background: #f0fdf4 !important;
    color: #166534 !important;
}

.warn {
    border-color: #fed7aa !important;
    background: #fff7ed !important;
    color: #9a3412 !important;
}

.bad {
    border-color: #fca5a5 !important;
    background: #fef2f2 !important;
    color: #991b1b !important;
}

/* Input Fields & Textareas */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div, .stMultiSelect div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border-color: #cbd5e1 !important;
    border-radius: 10px !important;
}

.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #94a3b8 !important;
}

/* Styled Card-based Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    padding: 8px;
    background: #f1f5f9;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
    background: #ffffff !important;
    color: #475569 !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.01) !important;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background: #2563eb !important;
    color: #ffffff !important;
    border-color: #2563eb !important;
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.15) !important;
}

.stTabs [aria-selected="true"] p {
    color: #ffffff !important;
}

/* Sidebar Radio button styling */
div[data-testid="stSidebar"] [role="radiogroup"] > label {
    background: #ffffff !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    margin-bottom: 8px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.01) !important;
    transition: all 0.2s ease-in-out !important;
}

div[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
    background: #f8fafc !important;
    border-color: #cbd5e1 !important;
    transform: translateX(3px) !important;
}

div[data-testid="stSidebar"] [role="radiogroup"] [aria-checked="true"] {
    background: #2563eb !important;
    color: #ffffff !important;
    border-color: #2563eb !important;
    font-weight: 700 !important;
}

div[data-testid="stSidebar"] [role="radiogroup"] [aria-checked="true"] p {
    color: #ffffff !important;
}

/* Default Buttons (Blue Gradients) */
div.stButton > button, div.stDownloadButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: #ffffff !important;
    border: 1px solid #2563eb !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
    transition: all 0.2s ease !important;
    min-height: 42px;
}

div.stButton > button:hover, div.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
    border-color: #1d4ed8 !important;
    box-shadow: 0 6px 12px -1px rgba(37, 99, 235, 0.25) !important;
    transform: translateY(-1px) !important;
}

div.stButton > button p, div.stDownloadButton > button p {
    color: #ffffff !important;
}

/* Primary Action Buttons (Orange Gradients) */
button[kind="primary"] {
    background: linear-gradient(135deg, #ea580c, #c2410c) !important;
    border-color: #ea580c !important;
    color: #ffffff !important;
    box-shadow: 0 4px 6px -1px rgba(234, 88, 12, 0.2) !important;
}

button[kind="primary"]:hover {
    background: linear-gradient(135deg, #c2410c, #9a3412) !important;
    border-color: #c2410c !important;
    box-shadow: 0 6px 12px -1px rgba(234, 88, 12, 0.25) !important;
}

button[kind="primary"] p {
    color: #ffffff !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    overflow: hidden;
}

.stAlert {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.01) !important;
}

.stProgress > div > div > div > div {
    background-color: #2563eb !important;
}
</style>
"""
