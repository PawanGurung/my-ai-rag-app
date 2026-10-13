import streamlit as st
import requests

# 1. Configure the browser tab layout and page headers
st.set_page_config(page_title="Corporate HR AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 Corporate HR AI Assistant")
st.write("Ask me anything about company guidelines, working hours, or allowances.")
st.markdown("---")

# 2. Initialize a local session memory array to track the conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Visually render past message bubbles onto the screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Create an interactive chat input field at the bottom of the monitor
if user_prompt := st.chat_input("Type your question here..."):
    
    # Render the user's text message bubble immediately
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # 5. Connect directly to your live production Render server URL path!
    # Update this URL with your exact live Render endpoint string
    render_url = "https://onrender.com"
    payload = {"message": user_prompt}
    
    # Spawn an assistant bubble with a loading spinner while fetching the backend response
    with st.chat_message("assistant"):
        with st.spinner("Searching corporate database..."):
            try:
                response = requests.post(render_url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    ai_reply = data["response"]
                    source = data.get("source_used", "No source found.")
                    
                    # Display the AI's answer text bubble
                    st.markdown(ai_reply)
                    
                    # Render a clean expander drop-down to show the database verification source row
                    with st.expander("🔍 View Database Source Used"):
                        st.caption(f"{source}")
                        
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                else:
                    st.error(f"Backend Server Error: Received Code {response.status_code}")
            except Exception as e:
                st.error(f"Connection Failure: Could not reach Render server. Details: {str(e)}")
