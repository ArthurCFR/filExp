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

def display_filiere_card(filiere_key, filiere_data, etats_config):
    """Affiche une carte pour une filière dans un container Streamlit natif"""
    etat = filiere_data.get('etat_avancement', 'initialisation')
    etat_info = etats_config.get(etat, {})
    
    # Mapping des états avec les nouveaux textes
    etats_labels_custom = {
        'prompts_deployes': 'AVANCÉ',
        'tests_realises': 'INTERMÉDIAIRE',
        'ateliers_planifies': 'NAISSANT',
        'initialisation': 'À ENGAGER'
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
        
        # Titre avec icône
        st.subheader(f"{filiere_data.get('icon', '📁')} {filiere_data.get('nom', 'Filière')}")
        
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
                border-left: 3px solid {couleur_bordure};'>
                <strong>🧪 Nombre de testeurs:</strong><br/>
                {filiere_data.get('nombre_testeurs', 0)}
                </div>""", 
                unsafe_allow_html=True
            )
            
            st.markdown(
                f"""<div style='background-color: {couleur_fond}20; 
                padding: 10px; 
                border-radius: 5px; 
                border-left: 3px solid {couleur_bordure};'>
                <strong>📈 Niveau d'autonomie:</strong><br/>
                {filiere_data.get('niveau_autonomie', 'Non renseigné')}
                </div>""",
                unsafe_allow_html=True
            )
            st.markdown(
                f"""<div style='background-color: {couleur_fond}20; 
                padding: 10px; 
                border-radius: 5px; 
                border-left: 3px solid {couleur_bordure};'>
                <strong>📄 Nombre de fiches d'opportunité:</strong><br/>
                {filiere_data.get('fopp_count', 0)}
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
                border-left: 3px solid {couleur_bordure};'>
                <strong>📋 Licences Copilot:</strong><br/>
                {filiere_data.get('acces', {}).get('copilot_licences', 0)}
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
        'ateliers_planifies': 'NAISSANT',
        'initialisation': 'À ENGAGER'
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
        'ateliers_planifies': 'NAISSANT - Des opportunités IAGen ont été identifiées - pas de COSUI ni d\'expérimentation en cours',
        'initialisation': 'À ENGAGER - Filière à engager (pas ou peu de FOPP, contact à initier avec un référent métier)'
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
    
    # Affichage des fiches
    st.header("🗂️ Fiches d'avancement des filières")
    st.write(f"*{len(filieres_filtrees)} filière(s) affichée(s)*")
    
    # Mode d'affichage
    mode_affichage = st.radio(
        "Mode d'affichage",
        ["Cartes", "Tableau", "Édition"],
        horizontal=True
    )
    
    if mode_affichage == "Cartes":
        # Recharge les données pour garantir la fraîcheur
        data = load_data()
        filieres = data.get('filieres', {})
        etats_config = data.get('etats_avancement', {})
        
        # Mapping des états avec les nouveaux textes
        etats_labels_custom = {
            'prompts_deployes': 'AVANCÉ',
            'tests_realises': 'INTERMÉDIAIRE', 
            'ateliers_planifies': 'NAISSANT',
            'initialisation': 'À ENGAGER'
        }
        
        etats_descriptions = {
            'prompts_deployes': 'Les COSUI sont réguliers et les expérimentations en cours',
            'tests_realises': 'Échanges en cours avec les référents métiers - premiers COSUI et/ou quelques expérimentations en démarrage',
            'ateliers_planifies': 'Des opportunités IAGen ont été identifiées - pas de COSUI ni d\'expérimentation en cours',
            'initialisation': 'Filière à engager (pas ou peu de FOPP, contact à initier avec un référent métier)'
        }
        
        # Grouper les filières par état
        filieres_par_etat = {}
        for key, filiere in filieres_filtrees.items():
            etat = filiere.get('etat_avancement', 'initialisation')
            if etat not in filieres_par_etat:
                filieres_par_etat[etat] = []
            filieres_par_etat[etat].append((key, filiere))
        
        # Ordre des états (du plus avancé au moins avancé)
        ordre_etats = ['prompts_deployes', 'tests_realises', 'ateliers_planifies', 'initialisation']
        
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
        # Affichage en tableau
        import pandas as pd
        
        # Mapping des états pour le tableau
        etats_labels_custom = {
            'prompts_deployes': 'AVANCÉ',
            'tests_realises': 'INTERMÉDIAIRE',
            'ateliers_planifies': 'NAISSANT',
            'initialisation': 'À ENGAGER'
        }
        
        table_data = []
        for key, filiere in filieres_filtrees.items():
            etat = filiere.get('etat_avancement', 'initialisation')
            table_data.append({
                'Filière': f"{filiere.get('icon', '📁')} {filiere.get('nom', 'Filière')}",
                'État': etats_labels_custom.get(etat, etats_config.get(etat, {}).get('label', 'État inconnu')),
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
        st.subheader("✏️ Édition des données")
        
        # Sélection de la filière à éditer
        if filieres_filtrees:
            filiere_a_editer = st.selectbox(
                "Sélectionnez une filière à éditer",
                list(filieres_filtrees.keys()),
                format_func=lambda x: f"{filieres[x].get('icon', '📁')} {filieres[x].get('nom', 'Filière')}"
            )
            
            if filiere_a_editer:
                filiere_data = filieres[filiere_a_editer]
                
                # Container pour l'édition
                with st.container(border=True):
                    st.subheader(f"Édition : {filiere_data.get('icon', '📁')} {filiere_data.get('nom', 'Filière')}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📝 Informations générales**")
                        
                        # Référent métier
                        nouveau_referent = st.text_input(
                            "Référent métier",
                            value=filiere_data.get('referent_metier', ''),
                            key=f"ref_{filiere_a_editer}"
                        )
                        
                        # Nombre de testeurs
                        nouveau_nb_testeurs = st.number_input(
                            "Nombre de testeurs",
                            min_value=0,
                            value=filiere_data.get('nombre_testeurs', 0),
                            key=f"test_{filiere_a_editer}"
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
                        # Nombre de fiches d'opportunité
                        nouveau_fopp_count = st.number_input(
                            "Nombre de fiches d'opportunité",
                            min_value=0,
                            value=filiere_data.get('fopp_count', 0),
                            key=f"fopp_{filiere_a_editer}"
                        )
                        
                        # État d'avancement
                        etats_labels_custom = {
                            'prompts_deployes': 'AVANCÉ',
                            'tests_realises': 'INTERMÉDIAIRE',
                            'ateliers_planifies': 'NAISSANT',
                            'initialisation': 'À ENGAGER'
                        }
                        
                        nouvel_etat = st.selectbox(
                            "État d'avancement",
                            list(etats_config.keys()),
                            index=list(etats_config.keys()).index(filiere_data.get('etat_avancement', 'initialisation')),
                            format_func=lambda x: etats_labels_custom.get(x, etats_config.get(x, {}).get('label', x)),
                            key=f"etat_{filiere_a_editer}"
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
                        if st.button("💾 Sauvegarder les modifications", type="primary", use_container_width=True):
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
                            
                            # Mise à jour
                            filieres[filiere_a_editer]['referent_metier'] = nouveau_referent
                            filieres[filiere_a_editer]['nombre_testeurs'] = nouveau_nb_testeurs
                            filieres[filiere_a_editer]['niveau_autonomie'] = nouveau_niveau_autonomie
                            filieres[filiere_a_editer]['fopp_count'] = nouveau_fopp_count
                            filieres[filiere_a_editer]['etat_avancement'] = nouvel_etat
                            filieres[filiere_a_editer]['acces']['laposte_gpt'] = nouveau_laposte_gpt
                            filieres[filiere_a_editer]['acces']['copilot_licences'] = nouvelles_licences
                            filieres[filiere_a_editer]['point_attention'] = nouveau_point_attention
                            filieres[filiere_a_editer]['usages_phares'] = nouveaux_usages
                            filieres[filiere_a_editer]['evenements_recents'] = nouveaux_evenements
                            
                            # Sauvegarde
                            save_data(data)
                            
                            st.session_state["edition_success"] = True
                            st.rerun()
        else:
            st.info("Aucune filière ne correspond aux filtres sélectionnés.")
    
    # Footer
    st.markdown("---")
    st.markdown(f"*Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}*")

    # Affichage du toast de succès si paramètre dans l'URL
    query_params = st.query_params
    if query_params.get("success") == ["1"]:
        st.success("✅ Modifications sauvegardées avec succès!", icon="✅")
        del st.query_params["success"]

    # --- Correction message succès édition ---
    # Dans le mode édition, remplacer l'utilisation des query params par un st.session_state pour afficher le message de succès
    if st.session_state.get("edition_success"):
        st.success("Modifications sauvegardées avec succès!", icon="✅")
        st.session_state["edition_success"] = False

if __name__ == "__main__":
    main()
