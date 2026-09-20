import streamlit as st
from ollama import chat
import threading
import time

# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI MCQ Generator",
    page_icon="📝",
    layout="wide"
)

st.title("📝 AI MCQ Generator",text_alignment="center")
st.markdown(
    "<div style='text-align: center; font-size = 100px;'>Generate MCQs from your study material using Qwen3 1.7B.</div>",
    unsafe_allow_html=True
)
st.file_uploader("upload the pdf",accept_multiple_files=True)
# --------------------------------------------------
# Processing messages
# --------------------------------------------------

messages = [
    "Reading document",
    "Loading document content",
    "Extracting text",
    "Processing text",
    "Cleaning text",
    "Analyzing document structure",
    "Understanding the content",
    "Analyzing the subject",
    "Identifying key topics",
    "Finding important concepts",
    "Identifying important information",
    "Extracting key facts",
    "Analyzing relevant details",
    "Determining question topics",
    "Selecting important concepts",
    "Planning questions",
    "Determining question difficulty",
    "Creating questions",
    "Generating MCQs",
    "Writing question statements",
    "Creating answer options",
    "Generating distractors",
    "Selecting possible answers",
    "Checking answer choices",
    "Verifying correct answers",
    "Checking question relevance",
    "Checking for duplicate questions",
    "Reviewing generated questions",
    "Improving question quality",
    "Analyzing question difficulty",
    "Validating answers",
    "Checking explanations",
    "Generating explanations",
    "Reviewing explanations",
    "Finalizing questions",
    "Organizing the quiz",
    "Preparing final output",
    "Formatting questions",
    "Almost finished",
    "Finalizing quiz"
]

# --------------------------------------------------
# Text input
# --------------------------------------------------

text = st.text_area(
    "📚 Enter your study material",
    height=400,
    placeholder="Paste your study material here..."
)

# --------------------------------------------------
# Generate button
# --------------------------------------------------

if st.button(
    "🚀 Generate MCQs",
    type="primary",
    use_container_width=True
):

    if not text.strip():

        st.warning("⚠️ Please enter some text first.")

    else:

        # --------------------------------------------------
        # Prompt
        # --------------------------------------------------

        prompt = f"""
        Create 20 multiple-choice questions from the following text.

        Rules:
        - Each question must have exactly 4 options.
        - There must be exactly one correct answer.
        - Questions must be based only on the supplied text.
        - Do not use outside knowledge.
        - Include the correct answer.
        - Include a short explanation.
        - NO duplicate questions.
        - Make the questions clear and meaningful.
        - use emojis if possible.
        
        Format:

        Q1: **Question here?**

        A. Option
        B. Option
        C. Option
        D. Option

        Correct Answer with Short explanation.

        Text:
        {text}
        """

        # --------------------------------------------------
        # Variables shared with worker thread
        # --------------------------------------------------

        result = [None]
        error = [None]
        finished = [False]

        # --------------------------------------------------
        # Ollama worker
        # --------------------------------------------------

        def generate_mcqs():

            try:

                response = chat(
                    model="qwen3:1.7b",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                result[0] = response.message.content

            except Exception as e:

                error[0] = str(e)

            finally:

                finished[0] = True

        # --------------------------------------------------
        # Start Ollama in background
        # --------------------------------------------------

        thread = threading.Thread(
            target=generate_mcqs,
            daemon=True
        )

        thread.start()

        # --------------------------------------------------
        # Streamlit UI
        # --------------------------------------------------

        status = st.empty()

        progress = st.progress(0)

        message_index = 0

        while not finished[0]:

            # Current message
            message = messages[message_index]

            status.info(
                f"⏳ **{message}...**"
            )

            # Progress animation
            progress_value = int(
                (message_index / len(messages)) * 100
            )

            progress.progress(progress_value)

            # Move to next message
            message_index = (
                message_index + 1
            ) % len(messages)

            # Update every 1 second
            time.sleep(1)

        # --------------------------------------------------
        # Finished
        # --------------------------------------------------

        thread.join()

        progress.progress(100)

        # --------------------------------------------------
        # Error handling
        # --------------------------------------------------

        if error[0]:

            status.error(
                f"❌ Error: {error[0]}"
            )

        else:

            status.success(
                "✅📄 MCQs generated successfully📄✅!"
            )

            # --------------------------------------------------
            # Display MCQs
            # --------------------------------------------------

            st.subheader("📋 Generated MCQs")

            st.markdown(result[0])

            # --------------------------------------------------
            # Download
            # --------------------------------------------------

            st.download_button(
                "⬇️ Download MCQs",
                data=result[0],
                file_name="generated_mcqs.txt",
                mime="text/plain",
                use_container_width=True
            )