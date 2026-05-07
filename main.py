import pandas as pd
import streamlit as st
from openai import OpenAI
import os
import tempfile

st.set_page_config(page_title="CLEAR UTILITIES")

api_key = "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"

if not api_key:
    st.error("Missing API key. Add OPENAI_API_KEY to your environment.")
    st.stop()

client = OpenAI(api_key=api_key)

with st.sidebar:
    st.title("MENU")
    pages = st.radio("", ["CH TRACKER", "PERFORMANCE", "TRAINING", "INVENTORY"])

if pages == "CH TRACKER":
    st.title("CH TRACKER MAKER")
    uploaded_file = st.file_uploader(
        "Select the file you wish to upload:",
        type="csv"
    )

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)


elif pages == "PERFORMANCE":
    st.title("AI PERFORMANCE ASSISTANT")

    uploaded_performance_file = st.file_uploader(
        "Select the file you wish to upload:",
        type="csv"
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "doc_ref" not in st.session_state:
        st.session_state.doc_ref = None

    if uploaded_performance_file and st.session_state.doc_ref is None:
        with st.spinner("Uploading your document..."):
            file_extension = os.path.splitext(uploaded_performance_file.name)[1]

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(uploaded_performance_file.getbuffer())
                temp_filename = temp_file.name

            try:
                with open(temp_filename, "rb") as f:
                    doc_ref = client.files.create(
                        file=f,
                        purpose="user_data"
                    )

                st.session_state.doc_ref = doc_ref
                st.success("Document uploaded successfully!")

            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask a question about the document")

    if prompt:
        if st.session_state.doc_ref is None:
            st.error("Please upload a document first!")

        else:
            st.session_state.messages.append(
                {"role": "user", "content": prompt}
            )

            with st.chat_message("user", avatar="👨"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = client.responses.create(
                    model="gpt-4.1",
                    instructions=(
                        "You are a document expert. "
                        "Answer questions ONLY about the uploaded document. "
                        "If the answer is not in the document, say you don't know."
                    ),
                    input=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_file",
                                    "file_id": st.session_state.doc_ref.id,
                                },
                                {
                                    "type": "input_text",
                                    "text": prompt,
                                },
                            ],
                        }
                    ],
                )

                answer = response.output_text
                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )


elif pages == "TRAINING":
    st.title("TRAINING TRACKER")


elif pages == "INVENTORY":
    st.title("INVENTORY")