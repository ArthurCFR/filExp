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
    """Affiche une carte pour une filière"""
    etat = filiere_data.get('etat_avancement', 'initialisation')
    couleur = get_color_by_state(etat, etats_config)
    
    # Utilisation de st.container pour créer une carte stylisée avec les composants natifs
    with st.container(border=True):
        # En-tête avec icône et nom
        col1, col2 = st.columns([1, 6])
        with col1:
            st.markdown(f"## {filiere_data.get('icon', '📁')}")
        with col2:
            st.markdown(f"### {filiere_data.get('nom', 'Filière')}")
        
        # Badge d'état
        etat_label = etats_config.get(etat, {}).get('label', 'État inconnu')
        st.markdown(f"**État:** :blue[{etat_label}]")
        
        # Informations principales
        st.markdown(f"**👤 Référent métier:** {filiere_data.get('referent_metier', 'Non défini')}")
        st.markdown(f"**🧪 Nombre de testeurs:** {filiere_data.get('nombre_testeurs', 0)}")
        st.markdown(f"**🔑 Accès LaPoste GPT:** {filiere_data.get('acces', {}).get('laposte_gpt', 0)}")
        st.markdown(f"**📋 Licences Copilot:** {filiere_data.get('acces', {}).get('copilot_licences', 0)}")
        
        # Description
        st.markdown("**Description:**")
        st.write(filiere_data.get('description', 'Aucune description disponible'))

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
    referents = ['Tous'] + list(set([f.get('referent_metier', '') for f in filieres.values()]))
    filtre_referent = st.sidebar.selectbox("Référent métier", referents)
    
    # Statistiques globales
    st.header("📈 Statistiques globales")
    
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
                delta=None,
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
        # Affichage en cartes (2 colonnes)
        cols = st.columns(2)
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
                'Copilot': filiere.get('acces', {}).get('copilot_licences', 0),
                'FOPP': filiere.get('fopp_count', 0)
            })
        
        if table_data:
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True)
    
    elif mode_affichage == "Édition":
        # Mode édition
        st.subheader("✏️ Édition des données")
        
        # Sélection de la filière à éditer
        filiere_a_editer = st.selectbox(
            "Sélectionnez une filière à éditer",
            list(filieres_filtrees.keys()),
            format_func=lambda x: f"{filieres[x].get('icon', '📁')} {filieres[x].get('nom', 'Filière')}"
        )
        
        if filiere_a_editer:
            filiere_data = filieres[filiere_a_editer]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Informations générales**")
                
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
                st.write("**Accès et licences**")
                
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
            
            # Bouton de sauvegarde
            if st.button("💾 Sauvegarder les modifications", type="primary"):
                # Mise à jour des données
                filieres[filiere_a_editer]['referent_metier'] = nouveau_referent
                filieres[filiere_a_editer]['nombre_testeurs'] = nouveau_nb_testeurs
                filieres[filiere_a_editer]['etat_avancement'] = nouvel_etat
                filieres[filiere_a_editer]['acces']['laposte_gpt'] = nouveau_laposte_gpt
                filieres[filiere_a_editer]['acces']['copilot_licences'] = nouvelles_licences
                
                # Sauvegarde dans le fichier JSON
                save_data(data)
                
                st.success("✅ Modifications sauvegardées avec succès!")
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("*Dernière mise à jour: {}*".format(datetime.now().strftime("%d/%m/%Y %H:%M")))

if __name__ == "__main__":
    main()