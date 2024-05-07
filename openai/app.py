import streamlit as st
import json
import openai
import os

# API Key and Client Initialization
api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=api_key)

# Environment variables for username and password
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

    model_options = ["gpt-4-turbo", "gpt-3.5-turbo"]
    model_selection = st.sidebar.selectbox("Choose your model:", model_options)
    
    # Initialize the openai_model in session state
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = model_selection

    # API Key and Client Initialization
    api_key = st.secrets["OPENAI_API_KEY"]
    client = openai.OpenAI(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Load history
    uploaded_file = st.file_uploader("Upload a JSON history file")
    if uploaded_file is not None:
        st.session_state.messages = json.load(uploaded_file)

    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state.openai_model,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Download history
    if st.button("Download History"):
        json_history = json.dumps(st.session_state.messages, indent=4)
        st.download_button(
            label="Download History",
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
