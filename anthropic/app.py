import os
import streamlit as st
import json
import anthropic

# Configuration de l'API
api_key = os.environ.get("API_KEY")
client = anthropic.Anthropic(api_key=api_key)

# Variables d'environnement pour le nom d'utilisateur et le mot de passe
USER = os.environ.get("MY_APP_USER")
PASSWORD = os.environ.get("MY_APP_PASSWORD")

def check_credentials(username, password):
    return username == USER and password == PASSWORD

def login_form():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted and check_credentials(username, password):
            return True
        if submitted:
            st.error("Incorrect Username or Password")
    return False

def chatbot_interface():
    st.title("")

    # Choix du modèle
    model_options = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]
    model_selected = st.sidebar.selectbox("Choisissez un modèle de Claude :", model_options)
    if "ai_model" not in st.session_state or st.session_state["ai_model"] != model_selected:
        st.session_state["ai_model"] = model_selected

    # Initialisation de l'état de session
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Charger l'historique
    uploaded_file = st.file_uploader("Chargez un fichier historique JSON")
    if uploaded_file is not None:
        st.session_state.messages = json.load(uploaded_file)

    # Afficher les messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrée utilisateur
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Appel API pour obtenir la réponse de l'assistant
        with st.chat_message("assistant"):
            message_placeholder = st.empty()  # Placeholder pour les réponses progressives
            full_response = ""

            # Préparation de la requête à envoyer à Claude
            with client.messages.stream(
                max_tokens=1024,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                model=st.session_state["ai_model"]
            ) as stream:
                for text in stream.text_stream:
                    full_response += str(text) if text is not None else ""
                    message_placeholder.markdown(full_response + "▌")  # Afficher la réponse progressive avec un curseur

            message_placeholder.markdown(full_response)  # Afficher la réponse finale
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Télécharger l'historique
    if st.button("Télécharger l'historique"):
        json_history = json.dumps(st.session_state.messages, indent=4)
        st.download_button(
            label="Télécharger l'historique",
            data=json_history,
            file_name="chat_history.json",
            mime="application/json"
        )

def main():
    st.sidebar.title("Login")
    logo_path = "logo.png"  # Remplacez 'logo.png' par le chemin réel vers votre image
    st.sidebar.image(logo_path, width=150)  # Ajustez la largeur selon vos besoins

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        chatbot_interface()
    else:
        if login_form():
            st.session_state['logged_in'] = True

if __name__ == "__main__":
    main()
