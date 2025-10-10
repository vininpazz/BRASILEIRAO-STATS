import streamlit as st
import requests
from datetime import date

HEADERS = {"X-Auth-Token": st.secrets["API_KEY"]}

st.set_page_config(page_title="Brasileirão Série A", page_icon="⚽", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0f1720;
        color: #e6edf3;
    }
    .hover-card:hover {
        transform: scale(1.01);
        transition: 0.2s;
        box-shadow: 0 0 10px rgba(255,255,255,0.1);
    }
    .hover-light:hover {
        transform: scale(1.01);
        transition: 0.2s;
        box-shadow: 0 0 10px rgba(255,255,255,0.15);
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data(ttl=300)
def buscar_dados(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

def verificar_jogos_ao_vivo():
    dados = buscar_dados("https://api.football-data.org/v4/competitions/BSA/matches")
    if not dados or "matches" not in dados:
        return False
    return any(m["status"] == "LIVE" for m in dados["matches"])

def painel_inicial():
    dados_comp = buscar_dados("https://api.football-data.org/v4/competitions/BSA")
    dados_class = buscar_dados("https://api.football-data.org/v4/competitions/BSA/standings")
    dados_art = buscar_dados("https://api.football-data.org/v4/competitions/BSA/scorers")

    rodada_atual = dados_comp.get("currentSeason", {}).get("currentMatchday", "-") if dados_comp else "-"
    total_rodadas = 38

    lider_nome, lider_pts, lider_escudo = "-", "-", ""
    if dados_class and "standings" in dados_class:
        top = dados_class["standings"][0]["table"][0]
        lider_nome = top["team"]["name"]
        lider_pts = top["points"]
        lider_escudo = top["team"].get("crest", "")

    art_nome, art_time, art_gols = "-", "-", "-"
    if dados_art and "scorers" in dados_art and len(dados_art["scorers"]) > 0:
        top = dados_art["scorers"][0]
        art_nome = top["player"]["name"]
        art_time = top["team"]["name"]
        art_gols = top["goals"]

    st.markdown("<div style='background:#111827; border-radius:10px; padding:10px;'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style='background:#0b1220; padding:14px; border-radius:10px; text-align:center;'>
                <div style='font-size:14px; color:#9aa5b1;'>🏁 Rodada Atual</div>
                <div style='font-size:28px; font-weight:700; margin-top:6px;'>{rodada_atual} / {total_rodadas}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        escudo_html = f"<img src='{lider_escudo}' width='45'>" if lider_escudo else ""
        st.markdown(
            f"""
            <div style='background:#07121a; padding:14px; border-radius:10px; text-align:center;'>
                <div style='font-size:14px; color:#9aa5b1;'>🥇 Líder</div>
                {escudo_html}
                <div style='font-size:18px; font-weight:700; margin-top:4px;'>{lider_nome}</div>
                <div style='font-size:13px; color:#9aa5b1;'>Pontos: <b>{lider_pts}</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style='background:#07121a; padding:14px; border-radius:10px; text-align:center;'>
                <div style='font-size:14px; color:#9aa5b1;'>⚽ Artilheiro</div>
                <div style='font-size:16px; font-weight:700; margin-top:6px;'>{art_nome}</div>
                <div style='font-size:13px; color:#9aa5b1;'>{art_time} — <b>{art_gols} gols</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

def ver_jogos():
    st.subheader("📅 Jogos do Dia")
    data = st.date_input("Selecione a data", value=date.today())
    url = f"https://api.football-data.org/v4/competitions/BSA/matches?dateFrom={data}&dateTo={data}"
    dados = buscar_dados(url)

    if not dados or "matches" not in dados or len(dados["matches"]) == 0:
        st.warning("⚠️ Nenhum jogo encontrado para esta data.")
        return

    for jogo in dados["matches"]:
        casa = jogo["homeTeam"]["name"]
        fora = jogo["awayTeam"]["name"]
        placar = jogo["score"]["fullTime"]
        esc_casa = jogo["homeTeam"].get("crest", "")
        esc_fora = jogo["awayTeam"].get("crest", "")
        status = jogo["status"]

        if status == "FINISHED":
            cor = "#a3b1b8"; txt = "Finalizado"
            placar_casa = placar.get("home", "-")
            placar_fora = placar.get("away", "-")
        elif status == "LIVE":
            cor = "#ff6b6b"; txt = "🔴 Ao vivo"
            placar_casa = placar.get("home", "-")
            placar_fora = placar.get("away", "-")
        else:
            cor = "#74c0fc"; txt = "Agendado"
            placar_casa = "NÃO"
            placar_fora = "INICIADO"

        st.markdown(
            f"""
            <div class='hover-card' style='background:#07121a; padding:12px; border-radius:10px; margin-bottom:10px;
                        display:flex; justify-content:space-between; color:#e6edf3; align-items:center;'>
                <div style='flex:1; text-align:right;'>
                    <img src='{esc_casa}' width='40'><br><b>{casa}</b>
                </div>
                <div style='flex:0.6; text-align:center;'>
                    <div style='font-size:20px; font-weight:700;'>{placar_casa} - {placar_fora}</div>
                    <div style='font-size:12px; color:{cor};'>{txt}</div>
                </div>
                <div style='flex:1; text-align:left;'>
                    <img src='{esc_fora}' width='40'><br><b>{fora}</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def ver_classificacao():
    st.subheader("📊 Classificação do Brasileirão")
    dados = buscar_dados("https://api.football-data.org/v4/competitions/BSA/standings")
    if not dados or "standings" not in dados:
        st.error("⚠️ Nenhuma classificação encontrada.")
        return

    tabela = dados["standings"][0]["table"]

    st.markdown(
        """
        <div style='background:#0b1220; color:#cbd5e1; padding:10px; border-radius:8px;
                    display:flex; align-items:center; text-align:center;'>
            <div style='width:35px;'>#</div>
            <div style='width:40px;'></div>
            <div style='flex:1; text-align:left;'>Clube</div>
            <div style='width:70px;'>PTS</div>
            <div style='width:60px;'>J</div>
            <div style='width:60px;'>V</div>
            <div style='width:60px;'>E</div>
            <div style='width:60px;'>D</div>
            <div style='width:80px;'>SG</div>
        </div>
        """, unsafe_allow_html=True)

    for time in tabela:
        pos = time["position"]
        nome = time["team"]["name"]
        escudo = time["team"].get("crest", "")
        pts, j, v, e, d, sg = (
            time["points"], time["playedGames"], time["won"],
            time["draw"], time["lost"], time["goalDifference"]
        )

        if pos <= 4:
            borda = "#00b894"
        elif 5 <= pos <= 6:
            borda = "#0984e3"
        elif 7 <= pos <= 12:
            borda = "#feca57"
        elif pos >= 17:
            borda = "#d63031"
        else:
            borda = "#636e72"

        st.markdown(
            f"""
            <div class='hover-card' style='border-left:6px solid {borda}; background:#07121a; padding:10px;
                        border-radius:8px; margin-bottom:8px; display:flex; align-items:center;'>
                <div style='width:35px; text-align:center; font-weight:700;'>{pos}</div>
                <div style='width:40px; text-align:center;'><img src='{escudo}' width='28'></div>
                <div style='flex:1; text-align:left;'>{nome}</div>
                <div style='width:70px; text-align:center; font-weight:700;'>{pts}</div>
                <div style='width:60px; text-align:center;'>{j}</div>
                <div style='width:60px; text-align:center;'>{v}</div>
                <div style='width:60px; text-align:center;'>{e}</div>
                <div style='width:60px; text-align:center;'>{d}</div>
                <div style='width:80px; text-align:center;'>{sg}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(
        """
        <div style='margin-top:20px; padding:10px; border-radius:8px; background:#0b1220; color:#cbd5e1;'>
            <b>Legenda das cores:</b><br>
            🟩 <b>Libertadores</b> (1º–4º) &nbsp;&nbsp;
            🟦 <b>Pré-Libertadores</b> (5º–6º) &nbsp;&nbsp;
            🟨 <b>Sul-Americana</b> (7º–12º) &nbsp;&nbsp;
            🟥 <b>Rebaixamento</b> (17º–20º)
        </div>
        """, unsafe_allow_html=True)

def ver_artilheiros():
    st.subheader("🏅 Artilheiros do Brasileirão")
    dados = buscar_dados("https://api.football-data.org/v4/competitions/BSA/scorers")
    if not dados or "scorers" not in dados or len(dados["scorers"]) == 0:
        st.warning("⚠️ Nenhum dado de artilheiro disponível.")
        return

    for i, s in enumerate(dados["scorers"][:20], start=1):
        jogador = s["player"]["name"]
        time = s["team"]["name"]
        gols = s["goals"]
        escudo = s["team"].get("crest", "")
        if i == 1:
            cor = "#ffd43b"; medalha = "🥇"; texto = "#08121a"
        elif i == 2:
            cor = "#adb5bd"; medalha = "🥈"; texto = "#08121a"
        elif i == 3:
            cor = "#ff9f1c"; medalha = "🥉"; texto = "#08121a"
        else:
            cor = "#07121a"; medalha = "⚽"; texto = "#e6edf3"
        st.markdown(
            f"""
            <div class='hover-light' style='background:{cor}; color:{texto}; padding:10px; border-radius:8px;
                        margin-bottom:8px; display:flex; align-items:center;'>
                <div style='width:40px; text-align:center; font-size:20px;'>{medalha}</div>
                <div style='width:50px; text-align:center;'><img src='{escudo}' width='35'></div>
                <div style='flex:1;'><b>{jogador}</b><br><span style='font-size:13px;'>{time}</span></div>
                <div style='font-size:16px; font-weight:700;'>⚽ {gols}</div>
            </div>
            """, unsafe_allow_html=True)

st.title("⚽ Brasileirão Série A")

painel_inicial()

tem_ao_vivo = verificar_jogos_ao_vivo()
aba_label = "📅 Jogos do Dia 🔴" if tem_ao_vivo else "📅 Jogos do Dia"

aba_jogos, aba_class, aba_art = st.tabs([aba_label, "📊 Classificação", "🏅 Artilheiros"])

with aba_jogos:
    ver_jogos()
with aba_class:
    ver_classificacao()
with aba_art:
    ver_artilheiros()

st.markdown(
    "<p style='text-align:center; color:#9aa5b1;'>🏁 Dados fornecidos por <b>Football-Data.org</b></p>",
    unsafe_allow_html=True
)
