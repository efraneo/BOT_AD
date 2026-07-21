# Forzar a que el navegador NUNCA guarde esta página en caché
ANTI_CACHE = '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0">'

ESTILOS_CSS = ANTI_CACHE + """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stSidebar"] { display: none !important; }
    
    /* ═══════════════════════════════════════════════════════════════
       TRUCO: CAMBIAR TEXTO POR PUNTITOS EN LAS CLAVES (INPUTS CLAVE)
       ═══════════════════════════════════════════════════════════════ */
    input.clave-oculta {
        -webkit-text-security: disc;
        -moz-text-security: disc;
        text-security: disc;
        font-family: 'Arial', sans-serif !important;
        letter-spacing: 2px;
    }
    /* ═══════════════════════════════════════════════════════════════ */

    /* Solución a textos superpuestos */
    .stTextInput, .stSelectbox, .stDateInput, .stFileUploader, .stCheckbox { margin-top: 15px !important; margin-bottom: 5px !important; }
    div.stButton > button, div.stForm > div > div > div > button { margin-top: 15px !important; margin-bottom: 10px !important; }
    .stAlert { margin-top: 10px !important; margin-bottom: 10px !important; }
    h1, h2, h3, h4 { margin-top: 15px !important; margin-bottom: 10px !important; }
    hr { margin-top: 25px !important; margin-bottom: 25px !important; }

    /* Estilos visuales */
    .metric-card { background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); border-radius: 16px; padding: 24px; box-shadow: 0 2px 16px rgba(0,0,0,0.06); border: 1px solid rgba(0,0,0,0.05); margin-bottom: 10px !important; }
    .metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
    .alerta-danger { background: #ffebee; border-left: 4px solid #c62828; padding: 12px 16px; border-radius: 6px; margin: 10px 0 !important; font-size: 13px; color: #b71c1c; }
    .alerta-warning { background: #fff8e1; border-left: 4px solid #f57f17; padding: 12px 16px; border-radius: 6px; margin: 10px 0 !important; font-size: 13px; color: #e65100; }
    .alerta-info { background: #e8eaf6; border-left: 4px solid #283593; padding: 12px 16px; border-radius: 6px; margin: 10px 0 !important; font-size: 13px; color: #1a237e; }
    .alerta-success { background: #e8f5e9; border-left: 4px solid #2e7d32; padding: 12px 16px; border-radius: 6px; margin: 10px 0 !important; font-size: 13px; color: #1b5e20; }
    div.stButton > button[kind="primary"] { background: linear-gradient(135deg, #1a237e, #283593) !important; border: none !important; border-radius: 10px !important; padding: 12px 32px !important; font-weight: 600 !important; font-size: 15px !important; box-shadow: 0 4px 16px rgba(26,35,126,0.3) !important; }
    div.stButton > button[kind="primary"]:hover { background: linear-gradient(135deg, #0d1557, #1a237e) !important; box-shadow: 0 6px 24px rgba(26,35,126,0.4) !important; }
    .stTextInput > div > div > input, .stSelectbox > div > div { border-radius: 8px !important; border: 1px solid #ddd !important; }
    .main-title { text-align: center; margin-bottom: 8px; }
    .main-title h1 { font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #1a237e, #283593, #3949ab); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }
    .main-title p { color: #666; font-size: 1rem; margin-top: 4px; }
    .divider { height: 2px; background: linear-gradient(90deg, transparent, #1a237e, transparent); margin: 24px 0; }
    .dataframe th { background-color: #1a237e !important; color: white !important; font-weight: 600 !important; text-align: left !important; }
    .dataframe td { padding: 10px 12px !important; font-size: 13px !important; }
    .dataframe tr:nth-child(even) { background-color: #f8f9ff !important; }
    .dataframe tr:hover { background-color: #e8eaf6 !important; }
    .step-indicator { display: flex; justify-content: center; gap: 8px; margin: 20px 0; }
    .step-dot { width: 12px; height: 12px; border-radius: 50%; background: #ddd; }
    .step-dot.active { background: #1a237e; box-shadow: 0 0 8px rgba(26,35,126,0.4); }
    .step-dot.completed { background: #2e7d32; }
</style>
"""

def cargar_estilos():
    import streamlit as st
    st.markdown(ESTILOS_CSS, unsafe_allow_html=True)
