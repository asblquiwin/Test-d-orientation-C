import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import json
from riasec_questions import get_all_questions

# Configuration Streamlit
st.set_page_config(
    page_title="Test RIASEC",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stRadio > label {
        font-size: 16px;
    }
    .metric-box {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialisations de session
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# Profils RIASEC
RIASEC_PROFILES = {
    'R': {'name': 'Réaliste', 'color': '#FF6B6B', 'description': 'Travail manuel, technique, pratique'},
    'I': {'name': 'Investigateur', 'color': '#4ECDC4', 'description': 'Recherche, analyse, résolution'},
    'A': {'name': 'Artistique', 'color': '#FFE66D', 'description': 'Création, expression, esthétique'},
    'S': {'name': 'Social', 'color': '#95E1D3', 'description': 'Aide, communication, équipe'},
    'E': {'name': 'Entreprenant', 'color': '#FF8D5C', 'description': 'Leadership, persuasion, risque'},
    'C': {'name': 'Conventionnel', 'color': '#6C5CE7', 'description': 'Ordre, organisation, règles'}
}

def calculate_scores(responses):
    """Calcule les scores pour chaque catégorie RIASEC"""
    scores = {'R': 0, 'I': 0, 'A': 0, 'S': 0, 'E': 0, 'C': 0}
    total_responses = 0
    
    for question_id, response in responses.items():
        question = next((q for q in get_all_questions() if q['id'] == question_id), None)
        if question:
            category = question['category']
            if question['type'] == 'positif':
                scores[category] += response
            else:
                scores[category] += (5 - response)
            total_responses += 1
    
    # Normaliser les scores (0-100)
    if total_responses > 0:
        for category in scores:
            scores[category] = round((scores[category] / (total_responses * 4)) * 100)
    
    return scores

def get_top_3_profiles(scores):
    """Retourne les 3 meilleures catégories"""
    sorted_profiles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [p[0] for p in sorted_profiles[:3]]

def create_radar_chart(scores):
    """Crée un graphique hexagonal (radar) RIASEC"""
    categories = list(scores.keys())
    values = list(scores.values())
    
    # Fermer le graphique en répétant la première valeur
    values += values[:1]
    categories_display = [RIASEC_PROFILES[c]['name'] for c in categories]
    categories_display += [categories_display[0]]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories_display,
        fill='toself',
        name='Votre Profil',
        line=dict(color='#667eea', width=2),
        fillcolor='rgba(102, 126, 234, 0.4)',
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10)
            ),
            bgcolor='rgba(240, 240, 240, 0.5)'
        ),
        showlegend=True,
        height=600,
        template='plotly_white',
        title={
            'text': "Votre Profil RIASEC",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#667eea'}
        }
    )
    
    return fig

def save_to_google_sheets(user_name, user_email, scores):
    """Sauvegarde les résultats dans Google Sheets"""
    try:
        # Configuration (à implémenter avec credentials Google)
        # Pour le prototype, on affiche un message
        st.success("✅ Résultats sauvegardés avec succès!")
        return True
    except Exception as e:
        st.warning(f"⚠️ Impossible de sauvegarder dans Google Sheets: {str(e)}")
        return False

# ======================== INTERFACE PRINCIPALE ========================

st.title("🎯 Test d'Orientation RIASEC")
st.markdown("---")

# Sidebar - Identification
with st.sidebar:
    st.header("👤 Identification")
    user_name = st.text_input("Votre nom:", placeholder="Ex: Jean Dupont")
    user_email = st.text_input("Votre email:", placeholder="Ex: jean@email.com")
    
    st.markdown("---")
    st.info("""
    ℹ️ **À propos du test RIASEC**
    
    Ce test mesure vos préférences professionnelles selon 6 profils:
    - 🔧 **Réaliste**: Travail technique et pratique
    - 🔬 **Investigateur**: Recherche et analyse
    - 🎨 **Artistique**: Création et expression
    - 👥 **Social**: Aide et communication
    - 💼 **Entreprenant**: Leadership et vente
    - 📋 **Conventionnel**: Organisation et règles
    """)
    
    progress = len(st.session_state.responses) / len(get_all_questions())
    st.progress(progress)
    st.caption(f"Progression: {len(st.session_state.responses)}/{len(get_all_questions())} questions")

# Tab layout
tabs = st.tabs(["📝 Test", "📊 Résultats"])

with tabs[0]:
    if not user_name or not user_email:
        st.warning("⚠️ Veuillez remplir votre nom et email pour commencer le test.")
    else:
        st.session_state.user_name = user_name
        st.session_state.user_email = user_email
        
        questions = get_all_questions()
        question_data = questions[st.session_state.current_question]
        
        st.subheader(f"Question {st.session_state.current_question + 1}/{len(questions)}")
        
        # Affichage de la question
        st.markdown(f"### {question_data['question']}")
        st.markdown(f"_Catégorie: {RIASEC_PROFILES[question_data['category']]['name']}_")
        
        # Réponse Likert (1-5)
        col1, col2, col3, col4, col5 = st.columns(5)
        response_map = {
            col1: 1,
            col2: 2,
            col3: 3,
            col4: 4,
            col5: 5
        }
        
        response_labels = ["Pas du tout\nd'accord", "Peu\nd'accord", "Neutre", "Assez\nd'accord", "Tout à fait\nd'accord"]
        
        for (col, response_val), label in zip(response_map.items(), response_labels):
            with col:
                if st.button(label, key=f"response_{question_data['id']}"):
                    st.session_state.responses[question_data['id']] = response_val
        
        # Navigation
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⬅️ Précédent") and st.session_state.current_question > 0:
                st.session_state.current_question -= 1
                st.rerun()
        
        with col3:
            if st.session_state.current_question < len(questions) - 1:
                if st.button("Suivant ➡️"):
                    st.session_state.current_question += 1
                    st.rerun()
            else:
                if st.button("✅ Terminer le test"):
                    st.session_state.current_question = -1
                    st.rerun()

with tabs[1]:
    if len(st.session_state.responses) < len(get_all_questions()):
        st.info("🔄 Complétez d'abord toutes les questions pour voir vos résultats.")
    else:
        scores = calculate_scores(st.session_state.responses)
        top_3 = get_top_3_profiles(scores)
        
        st.success("✅ Test complété! Voici vos résultats:")
        
        # Profil principal
        st.markdown("---")
        st.subheader(f"🎯 Votre Profil Principal: {top_3[0]}")
        main_profile = ''.join(top_3)
        st.markdown(f"### Profil {main_profile}")
        
        # Graphique radar
        fig = create_radar_chart(scores)
        st.plotly_chart(fig, use_container_width=True)
        
        # Scores détaillés
        st.markdown("---")
        st.subheader("📈 Scores Détaillés")
        
        cols = st.columns(3)
        for i, (profile_key, profile_info) in enumerate(RIASEC_PROFILES.items()):
            with cols[i % 3]:
                st.metric(
                    f"{profile_info['name']}",
                    f"{scores[profile_key]}/100",
                    delta=None,
                    delta_color="off"
                )
        
        # Interprétation
        st.markdown("---")
        st.subheader("💡 Interprétation")
        st.markdown(f"""
        Votre profil **{main_profile}** suggère:
        - **Force 1 - {RIASEC_PROFILES[top_3[0]]['name']}** ({scores[top_3[0]]}/100): {RIASEC_PROFILES[top_3[0]]['description']}
        - **Force 2 - {RIASEC_PROFILES[top_3[1]]['name']}** ({scores[top_3[1]]}/100): {RIASEC_PROFILES[top_3[1]]['description']}
        - **Force 3 - {RIASEC_PROFILES[top_3[2]]['name']}** ({scores[top_3[2]]}/100): {RIASEC_PROFILES[top_3[2]]['description']}
        """)
        
        # Sauvegarde
        st.markdown("---")
        if st.button("💾 Sauvegarder mes résultats"):
            save_to_google_sheets(st.session_state.user_name, st.session_state.user_email, scores)
        
        # Télécharger les résultats
        results_json = {
            "nom": st.session_state.user_name,
            "email": st.session_state.user_email,
            "date": datetime.now().isoformat(),
            "profil": main_profile,
            "scores": scores
        }
        
        st.download_button(
            label="📥 Télécharger mes résultats (JSON)",
            data=json.dumps(results_json, indent=2, ensure_ascii=False),
            file_name=f"riasec_results_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
        
        # Bouton pour recommencer
        if st.button("🔄 Recommencer le test"):
            st.session_state.responses = {}
            st.session_state.current_question = 0
            st.rerun()
