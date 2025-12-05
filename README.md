# Suat's AI Assistant 🤖

This is an AI-powered portfolio assistant built with **Streamlit** and **n8n**. It allows users to chat with an AI avatar that answers questions about Suat's professional experience, skills, and projects.

## 🚀 Features
- **Interactive Chat Interface**: Built with Streamlit for a smooth user experience.
- **AI-Powered Responses**: Integrated with n8n workflows to process queries.
- **Secure Access**: Simple password-based authentication to protect the content.

## 🛠️ Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/) (Python)
- **Backend/Workflow**: [n8n](https://n8n.io/)
- **Vector Database**: Pinecone (via n8n workflow)

## 🏃‍♂️ How to Run Locally

1.  **Clone the repository**
    ```bash
    git clone https://github.com/stuncers/suatini.git
    cd suatini
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Secrets**
    Create a file named `.streamlit/secrets.toml` in the project root and add your configuration:
    ```toml
    N8N_WEBHOOK_URL = "your_n8n_webhook_url_here"
    RECRUITER_KEYS = ["your_access_code_1", "your_access_code_2"]
    ```

4.  **Run the App**
    ```bash
    streamlit run app.py
    ```

## ☁️ Deployment
This app is designed to be deployed on **Streamlit Community Cloud**.
Ensure you add the secrets in the Streamlit Cloud dashboard under **App Settings > Secrets**.
