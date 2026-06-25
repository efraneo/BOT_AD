import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import requests
from openai import OpenAI
import json

# Configuración de la página
st.set_page_config(page_title="AI Bet Generator", page_icon="🤖", layout="wide")

# Diccionario de iconos de deportes
SPORT_ICONS = {
    "soccer": "⚽", "basketball": "🏀", "tennis": "🎾", "baseball": "⚾",
    "american_football": "🏈", "ice_hockey": "🏒", "mma": "🥊", "boxing": "🥊", "esports": "🎮"
}

POPULAR_SPORTS = [
    'soccer', 'basketball', 'tennis', 'baseball', 'mma_mixed_martial_arts', 
    'ice_hockey', 'american_football_nfl'
]

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# --- FUNCIONES DE API ---

@st.cache_data(ttl=3600)
def get_sports_matches(api_key):
    col_tz = pytz.timezone('America/Bogota')
    today_col = datetime.now(col_tz).date()
    start_of_week = today_col - timedelta(days=today_col.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    matches_this_week = []

    for sport_key in POPULAR_SPORTS:
        odds_url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions=us&oddsFormat=decimal"
        try:
            odds_response = requests.get(odds_url)
            if odds_response.status_code == 200:
                matches = odds_response.json()
                for match in matches:
                    match_time = datetime.fromisoformat(match['commence_time'][:-1]).astimezone(col_tz)
                    if start_of_week <= match_time.date() <= end_of_week:
                        icon = SPORT_ICONS.get(sport_key, "🏆")
                        sport_title = sport_key.replace('_', ' ').title()
                        matches_this_week.append({
                            "sport_key": sport_key, "sport_title": sport_title, "icon": icon,
                            "match_time": match_time, "home_team": match['home_team'],
                            "away_team": match['away_team'], "bookmakers": match['bookmakers']
                        })
        except:
            pass
            
    matches_this_week.sort(key=lambda x: x['match_time'])
    return matches_this_week

def generate_ai_analysis(api_key, match_info):
    """Genera el análisis con OpenAI GPT-4o-mini con Picks por nivel de riesgo"""
    client = OpenAI(api_key=api_key)
    
    odds_str = ""
    if match_info['bookmakers']:
        for bm in match_info['bookmakers'][:3]:
            odds_str += f"{bm['title']}: "
            for market in bm['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        odds_str += f"{outcome['name']} @ {outcome['price']} | "
            odds_str += "\n"

    prompt = f"""
    Actúa como un tipster deportivo experto y analítico (estilo Oddsium). Analiza el partido de {match_info['sport_title']} entre {match_info['home_team']} y {match_info['away_team']}.
    Cuotas actuales: {odds_str}
    
    Devuelve ÚNICAMENTE un JSON válido con esta estructura exacta. Para cada nivel de riesgo, incluye una descripción y el Pick específico:
    {{
        "conclusiones": ["Conclusión clave 1", "Conclusión clave 2", "Conclusión clave 3", "Conclusión clave 4"],
        "bajo_riesgo": {{
            "descripcion": "Descripción detallada de la apuesta de bajo riesgo",
            "pick": "El Pick: [Apuesta] @ [Cuota] en [Casa]"
        }},
        "riesgo_medio": {{
            "descripcion": "Descripción detallada de la apuesta de riesgo medio",
            "pick": "El Pick: [Apuesta] @ [Cuota] en [Casa]"
        }},
        "alto_riesgo": {{
            "descripcion": "Descripción detallada de la apuesta de alto riesgo",
            "pick": "El Pick: [Apuesta] @ [Cuota] en [Casa]"
        }},
        "analisis_ia": "Un análisis profundo de 2 párrafos sobre el contexto del partido, motivaciones, tácticas y por qué se recomienda el pick.",
        "consenso": ["Resumen del consenso 1", "Resumen del consenso 2"]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error al conectar con OpenAI: {e}")
        return None

# --- INTERFAZ DE USUARIO ---

def main():
    st.markdown("<h1 style='text-align: center;'>🤖 AI Sports Bet Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Pronósticos IA en tiempo real | Hora Colombia ⏰</p>", unsafe_allow_html=True)
    st.divider()

    # Leer claves desde Streamlit Secrets
    try:
        odds_api_key = st.secrets["odds_api"]
        openai_api_key = st.secrets["openai"]
    except KeyError:
        st.error("⚠️ ERROR: No se encontraron las claves en los Secrets de Streamlit.")
        st.info("""
            **Instrucciones:**
            1. Ve a Settings -> Secrets en tu panel de Streamlit Cloud.
            2. Pega esto (con tus claves reales):
            ```
            odds_api = "TU_ODDS_API_KEY"
            openai = "TU_OPENAI_API_KEY"
            ```
            3. Guarda los cambios y la app se reiniciará sola.
        """)
        return

    # Botón para limpiar caché
    if st.sidebar.button("🧹 Limpiar Memoria del Sistema"):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.title("⚙️ Panel de Control")
    timeframe = st.sidebar.radio("📅 Selecciona Periodo", ["Hoy", "Esta Semana"], horizontal=True)
    st.sidebar.markdown("📊 **Filtros**")

    with st.spinner("Obteniendo partidos..."):
        all_matches = get_sports_matches(odds_api_key)

    if not all_matches:
        st.error("No se encontraron partidos o se agotó tu cuota de The Odds API.")
        return

    sports_available = list(set([f"{m['icon']} {m['sport_title']}" for m in all_matches]))
    selected_sport = st.sidebar.selectbox("Deporte", ["Todos"] + sorted(sports_available))

    col_tz = pytz.timezone('America/Bogota')
    today_col = datetime.now(col_tz).date()
    
    filtered_matches = []
    for m in all_matches:
        if selected_sport != "Todos" and f"{m['icon']} {m['sport_title']}" != selected_sport:
            continue
        if timeframe == "Hoy" and m['match_time'].date() == today_col:
            filtered_matches.append(m)
        elif timeframe == "Esta Semana":
            filtered_matches.append(m)

    if filtered_matches:
        if st.button(f"🚀 Generar Análisis IA para {len(filtered_matches)} partidos visibles", use_container_width=True):
            st.session_state['generate'] = True

    current_day = None
    for match in filtered_matches:
        match_date = match['match_time'].date()
        if timeframe == "Esta Semana":
            dia_semana = DIAS_SEMANA[match_date.weekday()]
            fecha_str = f"{dia_semana} {match_date.day:02d}/{match_date.month:02d}"
            if current_day != fecha_str:
                if current_day is not None:
                    st.divider()
                st.markdown(f"### 📅 {fecha_str}")
                current_day = fecha_str

        hora_col = match['match_time'].strftime("%H:%M")
        st.markdown(f"#### {match['icon']} {match['home_team']} vs {match['away_team']}")
        st.markdown(f"**{match['sport_title']} | 🕒 {hora_col} Hora Colombia**")
        
        with st.expander("💰 Ver Cuotas y Análisis IA"):
            cuotas_data = {}
            for bm in match['bookmakers'][:5]:
                for market in bm['markets']:
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            if bm['title'] not in cuotas_data:
                                cuotas_data[bm['title']] = {}
                            cuotas_data[bm['title']][outcome['name']] = outcome['price']
            
            if cuotas_data:
                st.markdown("##### 💰 Cuotas Actuales")
                df_cuotas = pd.DataFrame.from_dict(cuotas_data, orient='index')
                st.table(df_cuotas)
                st.caption("Las cuotas mostradas son contenido publicitario. 18+. Juega responsablemente.")

            if st.session_state.get('generate'):
                with st.spinner("IA de OpenAI analizando datos..."):
                    ai_data = generate_ai_analysis(openai_api_key, match)
                
                if ai_data:
                    st.markdown("##### 🔑 Conclusiones clave")
                    for conc in ai_data.get("conclusiones", []):
                        st.markdown(f"- {conc}")
                    st.divider()

                    st.markdown("##### 🎯 Mejores apuestas para este partido")
                    c1, c2, c3 = st.columns(3)
                    
                    with c1:
                        st.markdown("**🟢 Bajo Riesgo**")
                        br = ai_data.get("bajo_riesgo", {})
                        st.write(br.get("descripcion", "N/A"))
                        st.success(f"**{br.get('pick', 'N/A')}**")
                        
                    with c2:
                        st.markdown("**🟡 Riesgo Medio**")
                        mr = ai_data.get("riesgo_medio", {})
                        st.write(mr.get("descripcion", "N/A"))
                        st.success(f"**{mr.get('pick', 'N/A')}**")
                        
                    with c3:
                        st.markdown("**🔴 Alto Riesgo**")
                        ar = ai_data.get("alto_riesgo", {})
                        st.write(ar.get("descripcion", "N/A"))
                        st.success(f"**{ar.get('pick', 'N/A')}**")

                    st.caption("*Legal disclaimer: 18+. Solo jugadores nuevos. Se aplican términos y condiciones.*")
                    
                    st.markdown("##### 📊 Análisis del pronóstico de apuesta (IA)")
                    st.write(ai_data.get("analisis_ia", "Análisis no disponible."))
                    
                    st.markdown("##### 🌐 Consenso y Resumen")
                    for cons in ai_data.get("consenso", []):
                        st.info(cons)
            else:
                st.warning("Presiona el botón superior 'Generar Análisis IA' para analizar este partido.")
        st.markdown("---")

if __name__ == "__main__":
    main()
