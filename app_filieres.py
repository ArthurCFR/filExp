import streamlit as st
import json
import os
from datetime import datetime
import requests

# Try to import plotting libraries
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Configuration de la page
st.set_page_config(
    page_title="Suivi des Filières Support - La Poste",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

GIST_ID = "e5f2784739d9e2784a3f067217b25e01"
FILENAME = "filieres_data.json"
GITHUB_TOKEN = st.secrets["GITHUB_PAT"]

# Champs attendus pour une filière (doit correspondre à la structure du JSON)
FILIERE_FIELDS = {
    "nom": "Nom de la filière",
    "icon": "📁",
    "referent_metier": "",
    "nombre_referents_delegues": 0,
    "nombre_collaborateurs_sensibilises": 0,
    "nombre_collaborateurs_total": 0,
    "etat_avancement": "en_emergence",
    "niveau_autonomie": "",
    "fopp_count": 0,
    "description": "",
    "point_attention": "",
    "usages_phares": [],
    "acces": {"laposte_gpt": 0, "copilot_licences": 0},
    "evenements_recents": []
}

def migrate_filiere_fields(filiere):
    """Complète dynamiquement les champs manquants d'une filière avec les valeurs par défaut attendues."""
    for k, v in FILIERE_FIELDS.items():
        if k not in filiere:
            filiere[k] = v if not isinstance(v, dict) and not isinstance(v, list) else v.copy() if isinstance(v, list) else v.copy()
        elif isinstance(v, dict):
            # Pour les sous-dictionnaires (ex: acces)
            for subk, subv in v.items():
                if k not in filiere or not isinstance(filiere[k], dict):
                    filiere[k] = {}
                if subk not in filiere[k]:
                    filiere[k][subk] = subv
    return filiere

@st.cache_data(ttl=10)  # Cache for 10 seconds only
def load_data():
    url = f"https://api.github.com/gists/{GIST_ID}"
    
    # Use authentication for higher rate limit
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        files = r.json()["files"]
        content = files[FILENAME]["content"]
        data = json.loads(content)
        # Migration à la volée des filières (comme avant)
        if 'filieres' in data:
            for key, filiere in data['filieres'].items():
                data['filieres'][key] = migrate_filiere_fields(filiere)
        return data
    except requests.exceptions.HTTPError as e:
        st.error(f"Erreur HTTP lors du chargement du Gist: {e}")
        st.error(f"Status code: {r.status_code}")
        st.error(f"Response: {r.text}")
        if r.status_code == 403 and "rate limit" in r.text:
            st.error("💡 Limite d'API atteinte. L'administrateur doit configurer un token GitHub pour une meilleure performance.")
        return None
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return None

def save_data(data):
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {
        "files": {
            FILENAME: {
                "content": json.dumps(data, indent=2, ensure_ascii=False)
            }
        }
    }
    try:
        r = requests.patch(url, headers=headers, data=json.dumps(payload))
        r.raise_for_status()
        # Clear cache to reload fresh data
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"❌ Erreur lors de la sauvegarde: {e}")
        return False

def display_filiere_card(filiere_key, filiere_data, etats_config):
    """Affiche une carte pour une filière dans un container Streamlit natif"""
    etat = filiere_data.get('etat_avancement', 'initialisation')
    etat_info = etats_config.get(etat, {})
    
    # Mapping des états avec les nouveaux textes
    etats_labels_custom = {
        'prompts_deployes': 'AVANCÉ',
        'tests_realises': 'INTERMÉDIAIRE',
        'en_emergence': 'EN ÉMERGENCE',
        'a_initier': 'À INITIER'
    }
    
    etat_label = etats_labels_custom.get(etat, etat_info.get('label', 'État inconnu'))
    couleur_fond = etat_info.get('couleur', '#f8f9fa')
    couleur_bordure = etat_info.get('couleur_bordure', '#dee2e6')
    
    # Utiliser le container natif de Streamlit avec bordure
    with st.container(border=True):
        # Barre de couleur en haut pour indiquer l'état
        st.markdown(
            f"""<div style='background-color: {couleur_bordure}; 
            margin: -1rem -1rem 1rem -1rem; 
            padding: 0.5rem; 
            border-radius: 5px 5px 0 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);'></div>""", 
            unsafe_allow_html=True
        )
        
        # Titre avec icône et nombre total de collaborateurs
        nom_filiere = filiere_data.get('nom', 'Filière')
        nb_total_collab = filiere_data.get('nombre_collaborateurs_total', 0)
        st.markdown(f"""
        <h3>{filiere_data.get('icon', '📁')} {nom_filiere} <span style='font-weight: normal; font-style: italic; font-size: 0.8em;'>({nb_total_collab} collaborateurs)</span></h3>
        """, unsafe_allow_html=True)
        
        # Badge d'état coloré
        st.markdown(
            f"""<div style='display: inline-block; 
            background-color: {couleur_bordure}; 
            color: white; 
            padding: 8px 16px; 
            border-radius: 20px; 
            font-weight: bold; 
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
            🎯 {etat_label}
            </div>""", 
            unsafe_allow_html=True
        )
        # Niveau d'autonomie en haut, sous le badge d'état
        icone_autonomie = {
            "Besoin d'accompagnement faible": "🟢",
            "Besoin d'accompagnement modéré": "🟡",
            "Besoin d'accompagnement fort": "🟠",
            "Besoin d'accompagnement très fort": "🔴"
        }
        niveau_autonomie = filiere_data.get('niveau_autonomie', 'Non renseigné')
        icone = icone_autonomie.get(niveau_autonomie, "❔")
        st.markdown(
            f"""<div style='margin: 8px 0 0 0; font-size: 1.2em;'><span>{icone}</span> <span style='font-weight:bold;'>{niveau_autonomie}</span></div>""",
            unsafe_allow_html=True
        )
        
        # Ligne de séparation
        st.markdown("---")
        
        # Informations en colonnes avec fond légèrement coloré
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                f"""<div style='background-color: {couleur_fond}20; 
                padding: 10px; 
                border-radius: 5px; 
                border-left: 3px solid {couleur_bordure};
                margin-bottom: 10px;'>
                <strong>👤 Référent métier:</strong><br/>
                {filiere_data.get('referent_metier', 'Non défini')}
                </div>""", 
                unsafe_allow_html=True
            )
            st.markdown(
                f"""<div style='background-color: {couleur_fond}20; 
                padding: 10px; 
                border-radius: 5px; 
                border-left: 3px solid {couleur_bordure};
                margin-bottom: 10px;'>
                <strong>🧑‍💼 Nombre de référents métier délégués:</strong><br/>
                {filiere_data.get('nombre_referents_delegues', 0)}
                </div>""",
                unsafe_allow_html=True
            )
            st.markdown(
                f"""<div style='background-color: {couleur_fond}20; 
                padding: 10px; 
                border-radius: 5px; 
                border-left: 3px solid {couleur_bordure};
                margin-bottom: 10px;'>
                <strong>🎓 Nombre de collaborateurs sensibilisés à l'IAGen:</strong><br/>
                {filiere_data.get('nombre_collaborateurs_sensibilises', 0)}
                </div>""",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"""<div style='background-color: {couleur_fond}20; 
                padding: 10px; 
                border-radius: 5px; 
                border-left: 3px solid {couleur_bordure};
                margin-bottom: 10px;'>
                <strong>🔑 Accès LaPoste GPT:</strong><br/>
                {filiere_data.get('acces', {}).get('laposte_gpt', 0)}
                </div>""", 
                unsafe_allow_html=True
            )
            st.markdown(
                f"""<div style='background-color: {couleur_fond}20; 
                padding: 10px; 
                border-radius: 5px; 
                border-left: 3px solid {couleur_bordure};
                margin-bottom: 10px;'>
                <strong>📋 Licences Copilot:</strong><br/>
                {filiere_data.get('acces', {}).get('copilot_licences', 0)}
                </div>""", 
                unsafe_allow_html=True
            )
            st.markdown(
                f"""<div style='background-color: {couleur_fond}20; 
                padding: 10px; 
                border-radius: 5px; 
                border-left: 3px solid {couleur_bordure};
                margin-bottom: 10px;'>
                <strong>📄 Nombre de fiches d'opportunité:</strong><br/>
                {filiere_data.get('fopp_count', 0)}
                </div>""",
                unsafe_allow_html=True
            )
        
        # Point d'attention avec style coloré
        point_attention = filiere_data.get('point_attention', '')
        if point_attention and point_attention != 'Aucun point d\'attention spécifique':
            st.markdown("---")
            st.markdown(
                f"""<div style='background-color: #fff3cd; 
                border-left: 4px solid #ffc107; 
                padding: 15px; 
                border-radius: 5px;
                margin: 10px 0;'>
                <strong>⚠️ Point d'attention:</strong><br/>
                {point_attention}
                </div>""", 
                unsafe_allow_html=True
            )
        
        # Usage(s) phare(s)
        usages = filiere_data.get('usages_phares', [])
        if usages:
            st.markdown("---")
            st.markdown("**🌟 Usage(s) phare(s):**")
            for usage in usages:
                st.markdown(
                    f"""<div style='background-color: {couleur_fond}10; 
                    padding: 5px 10px; 
                    border-radius: 5px; 
                    margin: 5px 0;'>
                    • {usage}
                    </div>""", 
                    unsafe_allow_html=True
                )
        
        # Événements récents dans un expander
        st.markdown("---")
        with st.expander("📅 Événements récents", expanded=False):
            # Gestion ouverture/fermeture du formulaire via session_state
            form_key = f"show_event_form_{filiere_key}"
            if form_key not in st.session_state:
                st.session_state[form_key] = False
            if st.button("➕ Ajouter un événement", key=f"add_event_{filiere_key}", help="Ajouter un événement récent"):
                st.session_state[form_key] = True
            if st.session_state[form_key]:
                with st.form(key=f"form_add_event_{filiere_key}", clear_on_submit=True):
                    new_date = st.date_input("Date", value=datetime.now(), key=f"date_{filiere_key}")
                    new_title = st.text_input("Titre", key=f"title_{filiere_key}")
                    new_desc = st.text_area("Description", key=f"desc_{filiere_key}")
                    submitted = st.form_submit_button("Enregistrer")
                    if submitted and new_title and new_desc:
                        data = load_data()
                        filieres = data.get('filieres', {})
                        evenements = filieres.get(filiere_key, {}).get('evenements_recents', [])
                        evenements.insert(0, {
                            'date': new_date.strftime('%Y-%m-%d'),
                            'titre': new_title,
                            'description': new_desc
                        })
                        filieres[filiere_key]['evenements_recents'] = evenements
                        save_data(data)
                        st.session_state[form_key] = False
                        st.session_state[f"event_success_{filiere_key}"] = True
                        st.rerun()
            # Message de succès après ajout
            if st.session_state.get(f"event_success_{filiere_key}"):
                st.success("Événement ajouté avec succès !")
                st.session_state[f"event_success_{filiere_key}"] = False
            # Toujours récupérer la liste à jour depuis filiere_data
            evenements = filiere_data.get('evenements_recents', [])
            if evenements:
                for i, event in enumerate(evenements):
                    if i > 0:
                        st.markdown("---")
                    st.markdown(
                        f"""<div style='background-color: #f8f9fa; 
                        padding: 10px; 
                        border-radius: 5px;'>
                        <strong>{event.get('date', 'Date inconnue')}</strong> - {event.get('titre', 'Sans titre')}<br/>
                        <span style='color: #666;'>{event.get('description', 'Pas de description')}</span>
                        </div>""", 
                        unsafe_allow_html=True
                    )
            else:
                st.text("Aucun événement récent")

def main():
    # Chargement des données
    data = load_data()
    
    if not data:
        st.error("Impossible de charger les données. Vérifiez que le fichier filieres_data.json existe.")
        return
    
    filieres = data.get('filieres', {})
    etats_config = data.get('etats_avancement', {})
    
    # Titre principal
    st.title("📊 Suivi des Filières Support - La Poste")
    st.markdown("### Expérimentations sur les outils IA Génératifs")
    
    # Sidebar pour les filtres
    st.sidebar.header("🔍 Filtres")
    
    # Filtre par état d'avancement
    etats_labels_custom = {
        'prompts_deployes': 'AVANCÉ',
        'tests_realises': 'INTERMÉDIAIRE',
        'en_emergence': 'EN ÉMERGENCE',
        'a_initier': 'À INITIER'
    }
    
    etats_disponibles = ['Tous'] + list(etats_config.keys())
    filtre_etat = st.sidebar.selectbox(
        "État d'avancement",
        etats_disponibles,
        format_func=lambda x: "Tous" if x == "Tous" else etats_labels_custom.get(x, etats_config.get(x, {}).get('label', x))
    )
    
    # Filtre par référent métier
    referents = ['Tous'] + list(set([f.get('referent_metier', '') for f in filieres.values() if f.get('referent_metier', '')]))
    filtre_referent = st.sidebar.selectbox("Référent métier", referents)
    
    # Statistiques globales
    st.header("📈 Statistiques globales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total des filières", len(filieres))
    
    with col2:
        total_testeurs = sum([f.get('nombre_testeurs', 0) for f in filieres.values()])
        st.metric("Total des testeurs", total_testeurs)
    
    with col3:
        total_laposte_gpt = sum([f.get('acces', {}).get('laposte_gpt', 0) for f in filieres.values()])
        st.metric("Accès LaPoste GPT", total_laposte_gpt)
    
    with col4:
        total_copilot = sum([f.get('acces', {}).get('copilot_licences', 0) for f in filieres.values()])
        st.metric("Licences Copilot", total_copilot)
    
    # Répartition par état
    st.subheader("🎯 Répartition par état d'avancement")
    etat_counts = {}
    for filiere in filieres.values():
        etat = filiere.get('etat_avancement', 'initialisation')
        etat_counts[etat] = etat_counts.get(etat, 0) + 1
    
    # Mapping des états avec les nouveaux textes
    etats_labels_custom = {
        'prompts_deployes': 'AVANCÉ - Les COSUI sont réguliers et les expérimentations en cours',
        'tests_realises': 'INTERMÉDIAIRE - Échanges en cours avec les référents métiers - premiers COSUI et/ou quelques expérimentations en démarrage',
        'en_emergence': 'EN ÉMERGENCE - Des opportunités IAGen ont été identifiées - pas de COSUI ni d\'expérimentation en cours',
        'a_initier': 'À INITIER - Filière à engager (pas ou peu de FOPP, contact à initier avec un référent métier)'
    }
    
    cols = st.columns(len(etats_config))
    for i, (etat_key, etat_info) in enumerate(etats_config.items()):
        with cols[i]:
            count = etat_counts.get(etat_key, 0)
            # Utiliser le label personnalisé s'il existe
            label = etats_labels_custom.get(etat_key, etat_info.get('label', etat_key))
            # Pour l'affichage dans la métrique, on peut raccourcir
            short_label = label.split(' - ')[0] if ' - ' in label else label
            st.metric(
                short_label,
                count,
                help=label  # Le texte complet apparaît au survol
            )
    
    # Filtrage des filières
    filieres_filtrees = {}
    for key, filiere in filieres.items():
        # Filtre par état
        if filtre_etat != 'Tous' and filiere.get('etat_avancement') != filtre_etat:
            continue
        
        # Filtre par référent
        if filtre_referent != 'Tous' and filiere.get('referent_metier') != filtre_referent:
            continue
        
        filieres_filtrees[key] = filiere
    
    # Pie charts pour les accès aux outils
    st.markdown("### 📊 Répartition des accès aux outils")
    
    # Préparation des données pour les pie charts
    laposte_gpt_data = {}
    copilot_data = {}
    
    for key, filiere in filieres_filtrees.items():
        nom_filiere = filiere.get('nom', 'Filière inconnue')
        laposte_gpt_count = filiere.get('acces', {}).get('laposte_gpt', 0)
        copilot_count = filiere.get('acces', {}).get('copilot_licences', 0)
        
        if laposte_gpt_count > 0:
            laposte_gpt_data[nom_filiere] = laposte_gpt_count
        if copilot_count > 0:
            copilot_data[nom_filiere] = copilot_count
    
    # Palette de couleurs cohérente avec l'application - Version pastel (30% plus claire)
    def make_pastel(hex_color, lightness_factor=0.3):
        """Convertit une couleur hex en version pastel"""
        # Supprimer le # si présent
        hex_color = hex_color.lstrip('#')
        
        # Convertir en RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Éclaircir en mélangeant avec du blanc
        r = int(r + (255 - r) * lightness_factor)
        g = int(g + (255 - g) * lightness_factor)
        b = int(b + (255 - b) * lightness_factor)
        
        # Reconvertir en hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    # Palette étendue avec suffisamment de couleurs pour toutes les filières
    app_colors_original = [
        '#28a745',  # Vert (prompts_deployes)
        '#007bff',  # Bleu (tests_realises)
        '#ffc107',  # Jaune (en_emergence)
        '#dc3545',  # Rouge (a_initier)
        '#6c757d',  # Gris
        '#17a2b8',  # Cyan
        '#e83e8c',  # Rose
        '#fd7e14',  # Orange
        '#20c997',  # Teal
        '#6f42c1',  # Violet
        '#795548',  # Marron
        '#607d8b',  # Bleu gris
        '#ff9800',  # Orange profond
        '#4caf50',  # Vert clair
        '#2196f3',  # Bleu clair
        '#9c27b0',  # Violet profond
        '#f44336',  # Rouge profond
        '#00bcd4',  # Cyan clair
        '#8bc34a',  # Vert lime
        '#ff5722',  # Orange rouge
        '#3f51b5',  # Indigo
        '#9e9e9e',  # Gris moyen
        '#cddc39',  # Lime
        '#ffeb3b',  # Jaune clair
        '#ff9688',  # Rouge clair
        '#80cbc4',  # Teal clair
        '#ce93d8',  # Violet clair
        '#fff176',  # Jaune très clair
        '#a5d6a7',  # Vert très clair
        '#90caf9',  # Bleu très clair
        '#f8bbd9',  # Rose clair
        '#d7ccc8',  # Beige
        '#b39ddb',  # Lavande
        '#ffcc02',  # Or
        '#ff6f00',  # Orange foncé
        '#1de9b6',  # Turquoise
        '#7c4dff',  # Violet électrique
        '#ff1744',  # Rouge vif
        '#00e676',  # Vert vif
        '#2979ff'   # Bleu vif
    ]
    
    # Créer la version pastel de toutes les couleurs
    app_colors = [make_pastel(color) for color in app_colors_original]
    
    # Créer un mapping couleur fixe par département pour TOUS les départements
    tous_departements = set()
    for key, filiere in filieres_filtrees.items():
        nom_filiere = filiere.get('nom', 'Filière inconnue')
        tous_departements.add(nom_filiere)  # Tous les départements, pas seulement ceux avec accès
    
    # Trier les départements pour un ordre cohérent
    departements_ordonnes = sorted(tous_departements)
    
    # Vérifier qu'il y a assez de couleurs
    if len(departements_ordonnes) > len(app_colors):
        st.warning(f"⚠️ Il y a {len(departements_ordonnes)} filières mais seulement {len(app_colors)} couleurs disponibles. Certaines couleurs seront répétées.")
    
    # Créer un mapping département -> couleur FIXE pour tous les départements
    couleur_par_departement = {}
    for i, dept in enumerate(departements_ordonnes):
        couleur_par_departement[dept] = app_colors[i % len(app_colors)]
    
    # Debug : afficher le mapping (à supprimer après test)
    # st.write("DEBUG - Mapping couleurs:", couleur_par_departement)
    
    # Affichage des pie charts
    col1, col_divider, col2 = st.columns([5, 1, 5])
    
    with col1:
        if laposte_gpt_data:
            if PLOTLY_AVAILABLE:
                # Créer un mapping couleur direct pour Plotly
                couleurs_laposte = [couleur_par_departement[dept] for dept in laposte_gpt_data.keys()]
                
                fig1 = px.pie(
                    values=list(laposte_gpt_data.values()),
                    names=list(laposte_gpt_data.keys()),
                    title="🔑 Accès LaPoste GPT"
                )
                
                # Assigner les couleurs manuellement pour chaque segment
                fig1.update_traces(
                    marker=dict(colors=couleurs_laposte)
                )
                fig1.update_layout(
                    height=300,
                    margin=dict(t=50, b=20, l=20, r=20),
                    font=dict(size=10),
                    showlegend=True,
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
                )
                fig1.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig1, use_container_width=True)
            elif MATPLOTLIB_AVAILABLE:
                # Créer la séquence de couleurs pour matplotlib
                couleurs_laposte = [couleur_par_departement[dept] for dept in laposte_gpt_data.keys()]
                
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.pie(list(laposte_gpt_data.values()), labels=list(laposte_gpt_data.keys()), 
                       autopct='%1.1f%%', colors=couleurs_laposte)
                ax.set_title("🔑 Accès LaPoste GPT")
                st.pyplot(fig)
                plt.close(fig)
            else:
                # Fallback: simple text display
                total = sum(laposte_gpt_data.values())
                for filiere, count in laposte_gpt_data.items():
                    percentage = (count / total) * 100
                    st.write(f"• {filiere}: {count} accès ({percentage:.1f}%)")
        else:
            st.info("Aucun accès LaPoste GPT configuré")
    
    with col_divider:
        # Divider vertical léger
        st.markdown("""
        <div style='height: 300px; width: 1px; background-color: #dee2e6; margin: 0 auto;'></div>
        """, unsafe_allow_html=True)
    
    with col2:
        if copilot_data:
            if PLOTLY_AVAILABLE:
                # Créer un mapping couleur direct pour Plotly
                couleurs_copilot = [couleur_par_departement[dept] for dept in copilot_data.keys()]
                
                fig2 = px.pie(
                    values=list(copilot_data.values()),
                    names=list(copilot_data.keys()),
                    title="📋 Licences Copilot"
                )
                
                # Assigner les couleurs manuellement pour chaque segment
                fig2.update_traces(
                    marker=dict(colors=couleurs_copilot)
                )
                fig2.update_layout(
                    height=300,
                    margin=dict(t=50, b=20, l=20, r=20),
                    font=dict(size=10),
                    showlegend=True,
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
                )
                fig2.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig2, use_container_width=True)
            elif MATPLOTLIB_AVAILABLE:
                # Créer la séquence de couleurs pour matplotlib
                couleurs_copilot = [couleur_par_departement[dept] for dept in copilot_data.keys()]
                
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.pie(list(copilot_data.values()), labels=list(copilot_data.keys()), 
                       autopct='%1.1f%%', colors=couleurs_copilot)
                ax.set_title("📋 Licences Copilot")
                st.pyplot(fig)
                plt.close(fig)
            else:
                # Fallback: simple text display
                total = sum(copilot_data.values())
                for filiere, count in copilot_data.items():
                    percentage = (count / total) * 100
                    st.write(f"• {filiere}: {count} licences ({percentage:.1f}%)")
        else:
            st.info("Aucune licence Copilot configurée")
    
    # Affichage des fiches
    st.header("🗂️ Fiches d'avancement des filières")
    st.write(f"*{len(filieres_filtrees)} filière(s) affichée(s)*")
    
    # Mode d'affichage
    mode_affichage = st.radio(
        "Mode d'affichage",
        ["Cartes", "Tableau", "Édition"],
        horizontal=True
    )
    
    if mode_affichage == "Édition":
        st.info("📝 Mode édition activé - Vos modifications seront sauvegardées automatiquement")
    
    # Auto-refresh invisible - actualise automatiquement toutes les 15 secondes
    st.markdown("""
    <script>
    setTimeout(function(){
        window.location.reload();
    }, 15000);
    </script>
    """, unsafe_allow_html=True)
    
    if mode_affichage == "Cartes":
        # Recharge les données pour garantir la fraîcheur
        data = load_data()
        filieres = data.get('filieres', {})
        etats_config = data.get('etats_avancement', {})
        
        # Mapping des états avec les nouveaux textes
        etats_labels_custom = {
            'prompts_deployes': 'AVANCÉ',
            'tests_realises': 'INTERMÉDIAIRE', 
            'en_emergence': 'EN ÉMERGENCE',
            'a_initier': 'À INITIER'
        }
        
        etats_descriptions = {
            'prompts_deployes': 'Les COSUI sont réguliers et les expérimentations en cours',
            'tests_realises': 'Échanges en cours avec les référents métiers - premiers COSUI et/ou quelques expérimentations en démarrage',
            'en_emergence': 'Des opportunités IAGen ont été identifiées - pas de COSUI ni d\'expérimentation en cours',
            'a_initier': 'Filière à engager (pas ou peu de FOPP, contact à initier avec un référent métier)'
        }
        
        # Grouper les filières par état
        filieres_par_etat = {}
        for key, filiere in filieres_filtrees.items():
            etat = filiere.get('etat_avancement', 'initialisation')
            if etat not in filieres_par_etat:
                filieres_par_etat[etat] = []
            filieres_par_etat[etat].append((key, filiere))
        
        # Ordre des états (du plus avancé au moins avancé)
        ordre_etats = ['prompts_deployes', 'tests_realises', 'en_emergence', 'a_initier']
        
        # Afficher les filières groupées par état
        for etat in ordre_etats:
            if etat in filieres_par_etat and filieres_par_etat[etat]:
                # En-tête de la section avec couleur
                etat_info = etats_config.get(etat, {})
                couleur_bordure = etat_info.get('couleur_bordure', '#dee2e6')
                
                st.markdown(
                    f"""<div style='background-color: {couleur_bordure}; 
                    color: white; 
                    padding: 15px; 
                    border-radius: 10px; 
                    margin: 20px 0 10px 0;'>
                    <h3 style='margin: 0; color: white;'>📊 {etats_labels_custom.get(etat, 'État inconnu')}</h3>
                    <p style='margin: 5px 0 0 0; font-size: 0.9em; color: rgba(255,255,255,0.9);'>
                    {etats_descriptions.get(etat, '')}
                    </p>
                    </div>""", 
                    unsafe_allow_html=True
                )
                
                # Afficher les cartes de cet état en colonnes
                cols = st.columns(2, gap="medium")
                for i, (key, filiere) in enumerate(filieres_par_etat[etat]):
                    with cols[i % 2]:
                        display_filiere_card(key, filiere, etats_config)
    
    elif mode_affichage == "Tableau":
        import pandas as pd
        # Mapping des états pour le tableau
        etats_labels_custom = {
            'prompts_deployes': '🟢 AVANCÉ',
            'tests_realises': '🔵 INTERMÉDIAIRE',
            'en_emergence': '🟡 EN ÉMERGENCE',
            'a_initier': '🔴 À INITIER'
        }
        
        # Ordre de tri des états (du plus avancé au moins avancé)
        ordre_etats = ['prompts_deployes', 'tests_realises', 'en_emergence', 'a_initier']
        
        table_data = []
        for key, filiere in filieres_filtrees.items():
            etat = filiere.get('etat_avancement', 'initialisation')
            table_data.append({
                'État': etats_labels_custom.get(etat, etat),
                'Filière': f"{filiere.get('icon', '📁')} {filiere.get('nom', 'Filière')}",
                'Référent': filiere.get('referent_metier', 'Non défini'),
                'Référents délégués': filiere.get('nombre_referents_delegues', 0),
                'Collab. sensibilisés IAGen': filiere.get('nombre_collaborateurs_sensibilises', 0),
                'Collab. total': filiere.get('nombre_collaborateurs_total', 0),
                'Niveau autonomie': filiere.get('niveau_autonomie', ''),
                'Fiches opportunité': filiere.get('fopp_count', 0),
                'LaPoste GPT': filiere.get('acces', {}).get('laposte_gpt', 0),
                'Copilot': filiere.get('acces', {}).get('copilot_licences', 0),
                'ordre_tri': ordre_etats.index(etat) if etat in ordre_etats else 999
            })
        if table_data:
            df = pd.DataFrame(table_data)
            # Trier par ordre d'avancement (avancé en haut)
            df_sorted = df.sort_values(by=['ordre_tri', 'Filière']).drop('ordre_tri', axis=1)
            st.dataframe(
                df_sorted,
                use_container_width=True,
                hide_index=True
            )
            # Export CSV avec nettoyage des émojis et normalisation des accents
            def clean_text_for_csv(text):
                """Nettoie le texte en supprimant les émojis et normalisant les accents pour l'export CSV"""
                if not isinstance(text, str):
                    return str(text)
                
                # Mapping des émojis vers du texte
                emoji_mapping = {
                    '🟢': 'AVANCE',
                    '🔵': 'INTERMEDIAIRE', 
                    '🟡': 'EN_EMERGENCE',
                    '🔴': 'A_INITIER',
                    '📁': '',
                    '📊': '',
                    '📢': '',
                    '💰': '',
                    '⚖️': '',
                    '🏛️': '',
                    '🔧': '',
                    '🏢': '',
                    '📋': '',
                    '🎯': '',
                    '🛡️': '',
                    '🚀': '',
                    '🌐': '',
                    '📱': '',
                    '🔒': '',
                    '👥': '',
                    '🎨': '',
                    '📈': '',
                    '🔍': '',
                    '💡': '',
                    '🏆': '',
                    '⚡': '',
                    '📝': '',
                    '⚠️': 'ATTENTION',
                    '❌': 'NON',
                    '✅': 'OUI',
                    '❓': 'QUESTION',
                    '❗': 'IMPORTANT'
                }
                
                # Remplacer les émojis
                cleaned = text
                for emoji, replacement in emoji_mapping.items():
                    cleaned = cleaned.replace(emoji, replacement)
                
                # Normaliser les accents pour éviter les problèmes d'encodage
                import unicodedata
                # Décomposer les caractères Unicode puis les recomposer
                cleaned = unicodedata.normalize('NFD', cleaned)
                cleaned = unicodedata.normalize('NFC', cleaned)
                
                # Mapping manuel des caractères problématiques pour CSV
                accent_mapping = {
                    'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a',
                    'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
                    'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
                    'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
                    'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
                    'ý': 'y', 'ÿ': 'y',
                    'ç': 'c', 'ñ': 'n',
                    'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A',
                    'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
                    'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I',
                    'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O',
                    'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U',
                    'Ý': 'Y', 'Ÿ': 'Y',
                    'Ç': 'C', 'Ñ': 'N'
                }
                
                # Remplacer les caractères accentués
                for accented, plain in accent_mapping.items():
                    cleaned = cleaned.replace(accented, plain)
                
                # Supprimer les caractères spéciaux restants
                import re
                cleaned = re.sub(r'[^\w\s\-.,;:()]', '', cleaned)
                
                # Nettoyer les espaces multiples
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                
                return cleaned
            
            # Créer une copie du DataFrame pour l'export
            df_export = df_sorted.copy()
            
            # Nettoyer toutes les colonnes de type string
            for col in df_export.columns:
                if df_export[col].dtype == 'object':
                    df_export[col] = df_export[col].astype(str).apply(clean_text_for_csv)
            
            # Utiliser l'encodage latin-1 pour éviter les problèmes d'accents
            csv = df_export.to_csv(index=False, sep=';', encoding='latin-1', errors='replace')
            st.download_button(
                label="📥 Exporter en CSV",
                data=csv.encode('latin-1'),
                file_name='filieres_tableau.csv',
                mime='text/csv'
            )
    
    elif mode_affichage == "Édition":
        # Mode édition
        st.subheader("✏️ Édition des données")
        
        # Sélection de la filière à éditer avec navigation
        if filieres_filtrees:
            filieres_keys = list(filieres_filtrees.keys())
            
            # Initialiser la filière sélectionnée
            if "filiere_editee_index" not in st.session_state:
                st.session_state.filiere_editee_index = 0
            
            # S'assurer que l'index est dans les limites
            if st.session_state.filiere_editee_index >= len(filieres_keys):
                st.session_state.filiere_editee_index = 0
            
            # Fonction pour détecter les changements
            def detecter_changements(filiere_key, filiere_data):
                """Détecte si des changements ont été faits dans les champs"""
                if f"ref_{filiere_key}" in st.session_state:
                    return (
                        st.session_state.get(f"ref_{filiere_key}", "") != filiere_data.get('referent_metier', '') or
                        st.session_state.get(f"refdelegues_{filiere_key}", 0) != filiere_data.get('nombre_referents_delegues', 0) or
                        st.session_state.get(f"collabIAGen_{filiere_key}", 0) != filiere_data.get('nombre_collaborateurs_sensibilises', 0) or
                        st.session_state.get(f"collabTotal_{filiere_key}", 0) != filiere_data.get('nombre_collaborateurs_total', 0) or
                        st.session_state.get(f"autonomie_{filiere_key}", "") != filiere_data.get('niveau_autonomie', '') or
                        st.session_state.get(f"fopp_{filiere_key}", 0) != filiere_data.get('fopp_count', 0) or
                        st.session_state.get(f"etat_{filiere_key}", "") != filiere_data.get('etat_avancement', '') or
                        st.session_state.get(f"gpt_{filiere_key}", 0) != filiere_data.get('acces', {}).get('laposte_gpt', 0) or
                        st.session_state.get(f"copilot_{filiere_key}", 0) != filiere_data.get('acces', {}).get('copilot_licences', 0) or
                        st.session_state.get(f"attention_{filiere_key}", "") != filiere_data.get('point_attention', '')
                    )
                return False
            
            # Interface de navigation
            col1, col2, col3 = st.columns([1, 6, 1])
            
            with col1:
                if st.button("◀", key="nav_prev", help="Filière précédente"):
                    current_filiere = filieres_keys[st.session_state.filiere_editee_index]
                    if detecter_changements(current_filiere, filieres[current_filiere]):
                        st.session_state.navigation_pending = "prev"
                        st.session_state.show_save_dialog = True
                        st.session_state.filiere_nom_dialog = filieres[current_filiere].get('nom', 'Filière')
                    else:
                        st.session_state.filiere_editee_index = (st.session_state.filiere_editee_index - 1) % len(filieres_keys)
                        st.rerun()
            
            with col2:
                filiere_a_editer = st.selectbox(
                    "Sélectionnez une filière à éditer",
                    filieres_keys,
                    index=st.session_state.filiere_editee_index,
                    format_func=lambda x: f"{filieres[x].get('icon', '📁')} {filieres[x].get('nom', 'Filière')}",
                    key="filiere_selectbox"
                )
                
                # Mettre à jour l'index si changé via le selectbox
                if filiere_a_editer != filieres_keys[st.session_state.filiere_editee_index]:
                    st.session_state.filiere_editee_index = filieres_keys.index(filiere_a_editer)
            
            with col3:
                if st.button("▶", key="nav_next", help="Filière suivante"):
                    current_filiere = filieres_keys[st.session_state.filiere_editee_index]
                    if detecter_changements(current_filiere, filieres[current_filiere]):
                        st.session_state.navigation_pending = "next"
                        st.session_state.show_save_dialog = True
                        st.session_state.filiere_nom_dialog = filieres[current_filiere].get('nom', 'Filière')
                    else:
                        st.session_state.filiere_editee_index = (st.session_state.filiere_editee_index + 1) % len(filieres_keys)
                        st.rerun()
            
            # Dialog de confirmation pour sauvegarder
            if st.session_state.get("show_save_dialog", False):
                st.warning(f"⚠️ Vous avez des modifications non sauvegardées sur la filière '{st.session_state.filiere_nom_dialog}'")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("💾 Sauvegarder", key="save_and_nav"):
                        # Sauvegarder les modifications actuelles
                        current_filiere = filieres_keys[st.session_state.filiere_editee_index]
                        # Déclencher la sauvegarde (logique à ajouter)
                        st.session_state.force_save = True
                        st.session_state.show_save_dialog = False
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ Ignorer", key="ignore_and_nav"):
                        # Ignorer les modifications et naviguer
                        if st.session_state.navigation_pending == "prev":
                            st.session_state.filiere_editee_index = (st.session_state.filiere_editee_index - 1) % len(filieres_keys)
                        elif st.session_state.navigation_pending == "next":
                            st.session_state.filiere_editee_index = (st.session_state.filiere_editee_index + 1) % len(filieres_keys)
                        
                        st.session_state.show_save_dialog = False
                        st.session_state.navigation_pending = None
                        st.rerun()
                
                with col3:
                    if st.button("❌ Annuler", key="cancel_nav"):
                        st.session_state.show_save_dialog = False
                        st.session_state.navigation_pending = None
                        st.rerun()
            
            if filiere_a_editer:
                filiere_data = filieres[filiere_a_editer]
                
                # Container pour l'édition
                with st.container(border=True):
                    st.subheader(f"Édition : {filiere_data.get('icon', '📁')} {filiere_data.get('nom', 'Filière')}")
                    
                    # --- État d'avancement placé à part, en haut ---
                    etats_labels_custom = {
                        'prompts_deployes': 'AVANCÉ',
                        'tests_realises': 'INTERMÉDIAIRE',
                        'en_emergence': 'EN ÉMERGENCE',
                        'a_initier': 'À INITIER'
                    }
                    st.markdown("**🎯 État d'avancement**")
                    nouvel_etat = st.selectbox(
                        "État d'avancement",
                        list(etats_config.keys()),
                        index=list(etats_config.keys()).index(filiere_data.get('etat_avancement', 'initialisation')),
                        format_func=lambda x: etats_labels_custom.get(x, etats_config.get(x, {}).get('label', x)) or str(x),
                        key=f"etat_{filiere_a_editer}"
                    )
                                            # Niveau d'autonomie
                    options_autonomie = [
                        "Besoin d'accompagnement faible",
                        "Besoin d'accompagnement modéré",
                        "Besoin d'accompagnement fort",
                        "Besoin d'accompagnement très fort"
                    ]
                    valeur_actuelle = filiere_data.get('niveau_autonomie', options_autonomie[0])
                    if valeur_actuelle not in options_autonomie:
                        valeur_actuelle = options_autonomie[0]
                    nouveau_niveau_autonomie = st.selectbox(
                        "Niveau d'autonomie",
                        options_autonomie,
                        index=options_autonomie.index(valeur_actuelle),
                        key=f"autonomie_{filiere_a_editer}"
                    )
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**📝 Informations générales**")
                        
                        # Référent métier
                        nouveau_referent = st.text_input(
                            "Référent métier",
                            value=filiere_data.get('referent_metier', ''),
                            key=f"ref_{filiere_a_editer}"
                        )
                        
                        # Nombre de collaborateurs sensibilisés à l'IAGen
                        nouveau_nb_collab_sensibilises = st.number_input(
                            "Nombre de collaborateurs sensibilisés à l'IAGen",
                            min_value=0,
                            value=filiere_data.get('nombre_collaborateurs_sensibilises', 0),
                            key=f"collabIAGen_{filiere_a_editer}"
                        )
                        
                        # Nombre de référents métier délégués
                        nouveau_nb_referents_delegues = st.number_input(
                            "Nombre de référents métier délégués",
                            min_value=0,
                            value=filiere_data.get('nombre_referents_delegues', 0),
                            key=f"refdelegues_{filiere_a_editer}"
                        )
                        
                        # Nombre total de collaborateurs dans la filière
                        nouveau_nb_collab_total = st.number_input(
                            "Nombre total de collaborateurs dans la filière",
                            min_value=0,
                            value=filiere_data.get('nombre_collaborateurs_total', 0),
                            key=f"collabTotal_{filiere_a_editer}"
                        )
                        
                        # Nombre de fiches d'opportunité
                        nouveau_fopp_count = st.number_input(
                            "Nombre de fiches d'opportunité",
                            min_value=0,
                            value=filiere_data.get('fopp_count', 0),
                            key=f"fopp_{filiere_a_editer}"
                        )
                    
                    with col2:
                        st.markdown("**🔐 Accès et licences**")
                        
                        # Accès LaPoste GPT
                        nouveau_laposte_gpt = st.number_input(
                            "Accès LaPoste GPT",
                            min_value=0,
                            value=filiere_data.get('acces', {}).get('laposte_gpt', 0),
                            key=f"gpt_{filiere_a_editer}"
                        )
                        
                        # Licences Copilot
                        nouvelles_licences = st.number_input(
                            "Licences Copilot",
                            min_value=0,
                            value=filiere_data.get('acces', {}).get('copilot_licences', 0),
                            key=f"copilot_{filiere_a_editer}"
                        )
                    
                    # Point d'attention
                    st.markdown("**⚠️ Point d'attention**")
                    nouveau_point_attention = st.text_area(
                        "Point d'attention",
                        value=filiere_data.get('point_attention', ''),
                        height=80,
                        placeholder="Décrivez les points nécessitant une attention particulière...",
                        key=f"attention_{filiere_a_editer}"
                    )
                    
                    # Usages phares
                    st.markdown("**🌟 Usages phares**")
                    usages_actuels = filiere_data.get('usages_phares', [])
                    usages_text = '\n'.join(usages_actuels)
                    
                    nouveaux_usages_text = st.text_area(
                        "Usages phares (un par ligne)",
                        value=usages_text,
                        height=100,
                        help="Entrez un usage phare par ligne",
                        key=f"usages_{filiere_a_editer}"
                    )
                    
                    # Événements récents
                    st.markdown("**📅 Événements récents**")
                    evenements_actuels = filiere_data.get('evenements_recents', [])
                    
                    evenements_text = ""
                    for event in evenements_actuels:
                        evenements_text += f"{event.get('date', '')};{event.get('titre', '')};{event.get('description', '')}\n"
                    
                    nouveaux_evenements_text = st.text_area(
                        "Événements récents (format: date;titre;description)",
                        value=evenements_text,
                        height=120,
                        help="Format: YYYY-MM-DD;Titre de l'événement;Description détaillée",
                        key=f"events_{filiere_a_editer}"
                    )
                    
                    # Bouton de sauvegarde
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("💾 Sauvegarder les modifications", type="primary", use_container_width=True) or st.session_state.get("force_save", False):
                            # Convertir les données
                            nouveaux_usages = [usage.strip() for usage in nouveaux_usages_text.split('\n') if usage.strip()]
                            
                            nouveaux_evenements = []
                            for ligne in nouveaux_evenements_text.split('\n'):
                                if ligne.strip():
                                    parties = ligne.split(';')
                                    if len(parties) >= 3:
                                        nouveaux_evenements.append({
                                            'date': parties[0].strip(),
                                            'titre': parties[1].strip(),
                                            'description': parties[2].strip()
                                        })
                            
                            # Mise à jour explicite de tous les champs dans la filière
                            filiere = migrate_filiere_fields(filieres[filiere_a_editer])
                            filiere['referent_metier'] = nouveau_referent
                            filiere['nombre_referents_delegues'] = nouveau_nb_referents_delegues
                            filiere['nombre_collaborateurs_sensibilises'] = nouveau_nb_collab_sensibilises
                            filiere['nombre_collaborateurs_total'] = nouveau_nb_collab_total
                            filiere['niveau_autonomie'] = nouveau_niveau_autonomie
                            filiere['fopp_count'] = nouveau_fopp_count
                            filiere['etat_avancement'] = nouvel_etat
                            filiere['acces']['laposte_gpt'] = nouveau_laposte_gpt
                            filiere['acces']['copilot_licences'] = nouvelles_licences
                            filiere['point_attention'] = nouveau_point_attention
                            filiere['usages_phares'] = nouveaux_usages
                            filiere['evenements_recents'] = nouveaux_evenements
                            
                            # Sauvegarde
                            if save_data(data):
                                # Message de succès temporaire avec timestamp
                                st.session_state["success_message"] = True
                                st.session_state["success_timestamp"] = datetime.now().timestamp()
                                
                                # Si c'était une sauvegarde forcée, naviguer après
                                if st.session_state.get("force_save", False):
                                    st.session_state.force_save = False
                                    if st.session_state.get("navigation_pending") == "prev":
                                        st.session_state.filiere_editee_index = (st.session_state.filiere_editee_index - 1) % len(filieres_keys)
                                    elif st.session_state.get("navigation_pending") == "next":
                                        st.session_state.filiere_editee_index = (st.session_state.filiere_editee_index + 1) % len(filieres_keys)
                                    st.session_state.navigation_pending = None
                                
                                st.rerun()
                    
                    # Affichage du message de succès temporaire
                    if st.session_state.get("success_message", False):
                        current_time = datetime.now().timestamp()
                        if current_time - st.session_state.get("success_timestamp", 0) < 6:
                            st.success("✅ Modifications sauvegardées avec succès!")
                        else:
                            st.session_state["success_message"] = False
        else:
            st.info("Aucune filière ne correspond aux filtres sélectionnés.")
    
    # Footer
    st.markdown("---")
    st.markdown(f"*Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}*")


if __name__ == "__main__":
    main()
