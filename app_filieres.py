import streamlit as st
import json
import os
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Suivi des Filières Support - La Poste",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chemin vers le fichier JSON
DATA_FILE = "filieres_data.json"

def load_data():
    """Charge les données depuis le fichier JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    """Sauvegarde les données dans le fichier JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_color_by_state(state, etats_config):
    """Retourne la couleur associée à un état d'avancement"""
    return etats_config.get(state, {}).get('couleur', '#gray')

def display_filiere_card(filiere_key, filiere_data, etats_config):
    """Affiche une carte pour une filière avec un fond coloré"""
    etat = filiere_data.get('etat_avancement', 'initialisation')
    etat_info = etats_config.get(etat, {})
    couleur_fond = etat_info.get('couleur', '#f8f9fa')
    couleur_bordure = etat_info.get('couleur_bordure', '#dee2e6')
    
    # Conversion des couleurs hex en RGB pour une transparence
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    rgb = hex_to_rgb(couleur_fond)
    rgba_light = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.2)"
    rgba_medium = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.4)"
    
    # CSS personnalisé pour cette carte spécifique
    card_css = f"""
    <style>
    .filiere-card-container-{filiere_key} {{
        background: linear-gradient(135deg, {rgba_light} 0%, {rgba_medium} 100%);
        border: 3px solid {couleur_bordure};
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }}
    .filiere-header-{filiere_key} {{
        background: linear-gradient(90deg, {couleur_fond} 0%, {couleur_bordure} 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        margin: -1rem -1rem 1rem -1rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }}
    .filiere-header-{filiere_key} h3 {{
        margin: 0;
        display: flex;
        align-items: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .etat-badge-{filiere_key} {{
        background: {couleur_bordure};
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    .info-box-{filiere_key} {{
        background: rgba(255,255,255,0.8);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 4px solid {couleur_bordure};
    }}
    </style>
    """
    
    st.markdown(card_css, unsafe_allow_html=True)
    
    # Container principal avec bordure et classe unique
    st.markdown(f'<div class="filiere-card-container-{filiere_key}">', unsafe_allow_html=True)
    
    # En-tête coloré avec icône et nom (avec gestion du dépassement)
    nom_filiere = filiere_data.get('nom', 'Filière')
    # Limiter la longueur du nom si nécessaire
    if len(nom_filiere) > 25:
        nom_filiere = nom_filiere[:25] + "..."
    
    header_html = f"""
    <div class="filiere-header-{filiere_key}">
        <h3>
            <span style="font-size: 1.5em; margin-right: 10px;">{filiere_data.get('icon', '📁')}</span>
            <span>{nom_filiere}</span>
        </h3>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
        
    # Badge d'état
    etat_label = etat_info.get('label', 'État inconnu')
    st.markdown(f'<div class="etat-badge-{filiere_key}">🎯 {etat_label}</div>', unsafe_allow_html=True)
    
    # Informations principales dans des boîtes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="info-box-{filiere_key}">
            <strong>👤 Référent métier:</strong><br/>
            {filiere_data.get('referent_metier', 'Non défini')}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-box-{filiere_key}">
            <strong>🧪 Nombre de testeurs:</strong><br/>
            {filiere_data.get('nombre_testeurs', 0)}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-box-{filiere_key}">
            <strong>🔑 Accès LaPoste GPT:</strong><br/>
            {filiere_data.get('acces', {}).get('laposte_gpt', 0)}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-box-{filiere_key}">
            <strong>📋 Licences Copilot:</strong><br/>
            {filiere_data.get('acces', {}).get('copilot_licences', 0)}
        </div>
        """, unsafe_allow_html=True)
    
    # Point d'attention avec style
    point_attention = filiere_data.get('point_attention', 'Aucun point d\'attention spécifique')
    if point_attention != 'Aucun point d\'attention spécifique':
        st.markdown(f"""
        <div style="background: rgba(255,193,7,0.2); border-left: 4px solid #ffc107; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <strong>⚠️ Point d'attention:</strong><br/>
            {point_attention}
        </div>
        """, unsafe_allow_html=True)
    
    # Usage(s) phare(s)
    usages = filiere_data.get('usages_phares', [])
    if usages:
        st.markdown(f"""
        <div class="info-box-{filiere_key}">
            <strong>🌟 Usage(s) phare(s):</strong>
            <ul style="margin: 5px 0 0 0; padding-left: 20px;">
        """, unsafe_allow_html=True)
        for usage in usages:
            st.markdown(f"<li>{usage}</li>", unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)
    
    # Événements récents (avec expander stylé)
    with st.expander("📅 Événements récents", expanded=False):
        evenements = filiere_data.get('evenements_recents', [])
        if evenements:
            for event in evenements:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.6); padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>{event.get('date', 'Date inconnue')}</strong> - {event.get('titre', 'Titre inconnu')}<br/>
                    <span style="color: #666;">{event.get('description', 'Aucune description')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("Aucun événement récent")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)  # Espace supplémentaire entre les cartes

def main():
    # Style global pour améliorer l'apparence
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        background-color: #0066cc;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #0052a3;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Chargement des données
    data = load_data()
    
    if not data:
        st.error("Impossible de charger les données. Vérifiez que le fichier filieres_data.json existe.")
        return
    
    filieres = data.get('filieres', {})
    etats_config = data.get('etats_avancement', {})
    
    # Titre principal avec style
    st.markdown("""
    <h1 style="color: #0066cc; text-align: center; padding: 20px 0;">
        📊 Suivi des Filières Support - La Poste
    </h1>
    <h3 style="color: #666; text-align: center; margin-top: -10px;">
        Expérimentations sur les outils IA Génératifs
    </h3>
    """, unsafe_allow_html=True)
    
    # Sidebar pour les filtres
    st.sidebar.header("🔍 Filtres")
    
    # Filtre par état d'avancement
    etats_disponibles = ['Tous'] + list(etats_config.keys())
    filtre_etat = st.sidebar.selectbox(
        "État d'avancement",
        etats_disponibles,
        format_func=lambda x: "Tous" if x == "Tous" else etats_config.get(x, {}).get('label', x)
    )
    
    # Filtre par référent métier
    referents = ['Tous'] + list(set([f.get('referent_metier', '') for f in filieres.values()]))
    filtre_referent = st.sidebar.selectbox("Référent métier", referents)
    
    # Statistiques globales avec style
    st.markdown("<h2 style='color: #0066cc;'>📈 Statistiques globales</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_filieres = len(filieres)
        st.metric("Total des filières", total_filieres)
    
    with col2:
        total_testeurs = sum([f.get('nombre_testeurs', 0) for f in filieres.values()])
        st.metric("Total des testeurs", total_testeurs)
    
    with col3:
        total_laposte_gpt = sum([f.get('acces', {}).get('laposte_gpt', 0) for f in filieres.values()])
        st.metric("Accès LaPoste GPT", total_laposte_gpt)
    
    with col4:
        total_copilot = sum([f.get('acces', {}).get('copilot_licences', 0) for f in filieres.values()])
        st.metric("Licences Copilot", total_copilot)
    
    # Répartition par état avec couleurs
    st.markdown("<h3 style='color: #0066cc;'>🎯 Répartition par état d'avancement</h3>", unsafe_allow_html=True)
    etat_counts = {}
    for filiere in filieres.values():
        etat = filiere.get('etat_avancement', 'initialisation')
        etat_counts[etat] = etat_counts.get(etat, 0) + 1
    
    cols = st.columns(len(etats_config))
    for i, (etat_key, etat_info) in enumerate(etats_config.items()):
        with cols[i]:
            count = etat_counts.get(etat_key, 0)
            couleur = etat_info.get('couleur_bordure', '#666')
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: {couleur}20; border-radius: 10px; border: 2px solid {couleur};">
                <h4 style="margin: 0; color: {couleur};">{etat_info.get('label', etat_key)}</h4>
                <h2 style="margin: 5px 0; color: {couleur};">{count}</h2>
            </div>
            """, unsafe_allow_html=True)
    
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
    
    # Affichage des fiches
    st.markdown("<h2 style='color: #0066cc;'>🗂️ Fiches d'avancement des filières</h2>", unsafe_allow_html=True)
    st.write(f"*{len(filieres_filtrees)} filière(s) affichée(s)*")
    
    # Mode d'affichage
    mode_affichage = st.radio(
        "Mode d'affichage",
        ["Cartes", "Tableau", "Édition"],
        horizontal=True
    )
    
    if mode_affichage == "Cartes":
        # Affichage en cartes (2 colonnes avec espacement)
        cols = st.columns([1, 0.05, 1])  # Ajout d'une colonne centrale pour l'espacement
        for i, (key, filiere) in enumerate(filieres_filtrees.items()):
            col_index = 0 if i % 2 == 0 else 2  # Colonnes 0 et 2, en sautant la colonne centrale
            with cols[col_index]:
                display_filiere_card(key, filiere, etats_config)
    
    elif mode_affichage == "Tableau":
        # Affichage en tableau
        import pandas as pd
        
        table_data = []
        for key, filiere in filieres_filtrees.items():
            etat = filiere.get('etat_avancement', 'initialisation')
            table_data.append({
                'Filière': f"{filiere.get('icon', '📁')} {filiere.get('nom', 'Filière')}",
                'État': etats_config.get(etat, {}).get('label', 'État inconnu'),
                'Référent': filiere.get('referent_metier', 'Non défini'),
                'Testeurs': filiere.get('nombre_testeurs', 0),
                'LaPoste GPT': filiere.get('acces', {}).get('laposte_gpt', 0),
                'Copilot': filiere.get('acces', {}).get('copilot_licences', 0)
            })
        
        if table_data:
            df = pd.DataFrame(table_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Filière": st.column_config.TextColumn("Filière", width="large"),
                    "État": st.column_config.TextColumn("État", width="medium"),
                    "Référent": st.column_config.TextColumn("Référent", width="medium"),
                    "Testeurs": st.column_config.NumberColumn("Testeurs", width="small"),
                    "LaPoste GPT": st.column_config.NumberColumn("LaPoste GPT", width="small"),
                    "Copilot": st.column_config.NumberColumn("Copilot", width="small")
                }
            )
    
    elif mode_affichage == "Édition":
        # Mode édition
        st.markdown("<h3 style='color: #0066cc;'>✏️ Édition des données</h3>", unsafe_allow_html=True)
        
        # Sélection de la filière à éditer
        filiere_a_editer = st.selectbox(
            "Sélectionnez une filière à éditer",
            list(filieres_filtrees.keys()),
            format_func=lambda x: f"{filieres[x].get('icon', '📁')} {filieres[x].get('nom', 'Filière')}"
        )
        
        if filiere_a_editer:
            filiere_data = filieres[filiere_a_editer]
            
            # Container avec bordure pour l'édition
            with st.container(border=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📝 Informations générales**")
                    
                    # Référent métier (éditable)
                    nouveau_referent = st.text_input(
                        "Référent métier",
                        value=filiere_data.get('referent_metier', '')
                    )
                    
                    # Nombre de testeurs (éditable)
                    nouveau_nb_testeurs = st.number_input(
                        "Nombre de testeurs",
                        min_value=0,
                        value=filiere_data.get('nombre_testeurs', 0)
                    )
                    
                    # État d'avancement (éditable)
                    nouvel_etat = st.selectbox(
                        "État d'avancement",
                        list(etats_config.keys()),
                        index=list(etats_config.keys()).index(filiere_data.get('etat_avancement', 'initialisation')),
                        format_func=lambda x: etats_config.get(x, {}).get('label', x)
                    )
                
                with col2:
                    st.markdown("**🔐 Accès et licences**")
                    
                    # Accès LaPoste GPT
                    nouveau_laposte_gpt = st.number_input(
                        "Accès LaPoste GPT",
                        min_value=0,
                        value=filiere_data.get('acces', {}).get('laposte_gpt', 0)
                    )
                    
                    # Licences Copilot
                    nouvelles_licences = st.number_input(
                        "Licences Copilot",
                        min_value=0,
                        value=filiere_data.get('acces', {}).get('copilot_licences', 0)
                    )
                
                # Point d'attention (éditable)
                st.markdown("**⚠️ Point d'attention**")
                nouveau_point_attention = st.text_area(
                    "Point d'attention",
                    value=filiere_data.get('point_attention', ''),
                    height=80,
                    placeholder="Décrivez les points nécessitant une attention particulière..."
                )
                
                # Section Usages phares (éditable)
                st.markdown("**🌟 Usages phares**")
                usages_actuels = filiere_data.get('usages_phares', [])
                
                # Convertir la liste en texte (un usage par ligne)
                usages_text = '\n'.join(usages_actuels)
                
                nouveaux_usages_text = st.text_area(
                    "Usages phares (un par ligne)",
                    value=usages_text,
                    height=100,
                    help="Entrez un usage phare par ligne"
                )
                
                # Section Événements récents (éditable)
                st.markdown("**📅 Événements récents**")
                evenements_actuels = filiere_data.get('evenements_recents', [])
                
                # Convertir les événements en texte pour édition
                evenements_text = ""
                for event in evenements_actuels:
                    evenements_text += f"{event.get('date', '')};{event.get('titre', '')};{event.get('description', '')}\n"
                
                nouveaux_evenements_text = st.text_area(
                    "Événements récents (format: date;titre;description)",
                    value=evenements_text,
                    height=120,
                    help="Format: YYYY-MM-DD;Titre de l'événement;Description détaillée"
                )
                
                # Bouton de sauvegarde centré
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("💾 Sauvegarder les modifications", type="primary", use_container_width=True):
                        # Convertir le texte des usages en liste
                        nouveaux_usages = [usage.strip() for usage in nouveaux_usages_text.split('\n') if usage.strip()]
                        
                        # Convertir le texte des événements en liste de dictionnaires
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
                        
                        # Mise à jour des données
                        filieres[filiere_a_editer]['referent_metier'] = nouveau_referent
                        filieres[filiere_a_editer]['nombre_testeurs'] = nouveau_nb_testeurs
                        filieres[filiere_a_editer]['etat_avancement'] = nouvel_etat
                        filieres[filiere_a_editer]['acces']['laposte_gpt'] = nouveau_laposte_gpt
                        filieres[filiere_a_editer]['acces']['copilot_licences'] = nouvelles_licences
                        filieres[filiere_a_editer]['point_attention'] = nouveau_point_attention
                        filieres[filiere_a_editer]['usages_phares'] = nouveaux_usages
                        filieres[filiere_a_editer]['evenements_recents'] = nouveaux_evenements
                        
                        # Sauvegarde dans le fichier JSON
                        save_data(data)
                        
                        st.success("✅ Modifications sauvegardées avec succès!")
                        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <p style="text-align: center; color: #666; font-style: italic;">
        Dernière mise à jour: {datetime.now().strftime("%d/%m/%Y %H:%M")}
    </p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
