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
    etat_label = etat_info.get('label', 'État inconnu')
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
        with st.expander("📅 Événements récents"):
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
    etats_disponibles = ['Tous'] + list(etats_config.keys())
    filtre_etat = st.sidebar.selectbox(
        "État d'avancement",
        etats_disponibles,
        format_func=lambda x: "Tous" if x == "Tous" else etats_config.get(x, {}).get('label', x)
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
    
    cols = st.columns(len(etats_config))
    for i, (etat_key, etat_info) in enumerate(etats_config.items()):
        with cols[i]:
            count = etat_counts.get(etat_key, 0)
            st.metric(
                etat_info.get('label', etat_key),
                count,
                help=etat_info.get('description', '')
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
        # Affichage en cartes (2 colonnes avec gap)
        cols = st.columns(2, gap="medium")
        for i, (key, filiere) in enumerate(filieres_filtrees.items()):
            with cols[i % 2]:
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
                        
                        # État d'avancement
                        nouvel_etat = st.selectbox(
                            "État d'avancement",
                            list(etats_config.keys()),
                            index=list(etats_config.keys()).index(filiere_data.get('etat_avancement', 'initialisation')),
                            format_func=lambda x: etats_config.get(x, {}).get('label', x),
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
                            filieres[filiere_a_editer]['etat_avancement'] = nouvel_etat
                            filieres[filiere_a_editer]['acces']['laposte_gpt'] = nouveau_laposte_gpt
                            filieres[filiere_a_editer]['acces']['copilot_licences'] = nouvelles_licences
                            filieres[filiere_a_editer]['point_attention'] = nouveau_point_attention
                            filieres[filiere_a_editer]['usages_phares'] = nouveaux_usages
                            filieres[filiere_a_editer]['evenements_recents'] = nouveaux_evenements
                            
                            # Sauvegarde
                            save_data(data)
                            
                            st.success("✅ Modifications sauvegardées avec succès!")
                            st.rerun()
        else:
            st.info("Aucune filière ne correspond aux filtres sélectionnés.")
    
    # Footer
    st.markdown("---")
    st.markdown(f"*Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}*")

if __name__ == "__main__":
    main()
