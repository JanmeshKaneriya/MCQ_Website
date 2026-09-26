
import streamlit as st
from select_api import generate_mcqs
import json
import re
import threading
import time


#📄 Page setup 📄

st.set_page_config(
    page_title="AI MCQ Generator",
    page_icon="📝",
    layout="wide"
)

st.title("📝 AI MCQ Generator", text_alignment="center")
st.markdown(
    "<p style='text-align:center'>Generate MCQs from your study material using Groq AI.</p>",
    unsafe_allow_html=True
)

st.markdown("""
<style>
/* Main background */
.stApp {
    background-color: black;
    color: black;
}

/* all text */
h1, h2, h3, p, label {
    color: white !important;
}

/* Input text background color */
textarea {
    background-color: gray !important;
    color: white !important;
    
    border-radius:18px !important;
    border: 2px solid #666 !important;
    padding: 15px !important;
}

textarea:focus{
    border:2px solid #FFC000 !important;
    box-shadow: 0 0 8px rgba (255, 192, 0, 0.4) !important;
}

/* Number input background color */
input {
    background-color: gray !important;
    color: white !important;
}
input:focus{
    border:2px solid #FFC000 !important;
    box-shadow: 0 0 8px rgba (255, 192, 0, 0.4) !important;
}
/* all Buttons */
button {
    background-color: #FFC000 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Input
# -----------------------------

# Create text area
text = st.text_area(
    "📚 Enter your study material",
    height=300,
    placeholder="Paste your study material here... \nUse longer text to generate more MCQs."
)

# Create number selector
question_count = st.number_input(
    "🔢 Number of MCQs",
    min_value=1,
    max_value=50,
    value=10
)


# -----------------------------
# Parse AI response
# -----------------------------

def parse_questions(response, expected_count):

    # Remove ```json ... ``` if the model adds it
    response = re.sub(
        r"```(?:json)?|```",
        "",
        response
    ).strip()

    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        raise ValueError("AI returned invalid JSON.")

    questions = data.get("questions", [])

    if len(questions) != expected_count:
        raise ValueError(
            f"Expected {expected_count} questions, but got {len(questions)}. Click on Generate MCQs again."
        )

    for q in questions:

        if (
            not q.get("question")
            or not isinstance(q.get("options"), list)
            or len(q["options"]) != 4
            or q.get("correct_answer") not in q["options"]
        ):
            raise ValueError("One or more questions have an invalid format. Click on Generate MCQs again.")

    return questions


# -----------------------------
# Generate MCQs
# -----------------------------

if st.button(
    "🚀 Generate MCQs",
    type="primary",
    use_container_width=True
):

    if not text.strip():
        st.warning("⚠️ Please enter some study material.")

    else:

        prompt = f"""
Create exactly {question_count} multiple-choice questions
from the text below.

Rules:
- Exactly 4 options per question.
- Exactly 1 correct answer.
- Use only information from the supplied text.
- No outside knowledge.
- correct_answer must exactly match one option.
- Include a short explanation.
- Do not create duplicate questions.
- Return ONLY valid JSON.

Format:

{{
    "questions": [
        {{
            "question": "Question?",
            "options": [
                "Option 1",
                "Option 2",
                "Option 3",
                "Option 4"
            ],
            "correct_answer": "Option 1",
            "explanation": "Short explanation."
        }}
    ]
}}

Text:
{text}
"""

        result = [None]
        error = [None]

        # Run Groq API in another thread
        def generate():

            try:
                result[0] = generate_mcqs(prompt)

            except Exception as e:
                error[0] = str(e)

        thread = threading.Thread(target=generate)
        thread.start()

        # Simple loading screen
        with st.spinner("🤖 Generating MCQs..."):
            while thread.is_alive():
                time.sleep(0.2)

        thread.join()

        if error[0]:
            st.error(f"❌ Error: {error[0]}")

        else:
            try:
                # Clear previous answers from session state
                for key in list(st.session_state.keys()):
                    if key.startswith("answer_"):
                        del st.session_state[key]

                st.session_state.questions = parse_questions(
                    result[0],
                    int(question_count)
                )

                st.session_state.quiz_submitted = False

                st.success(
                    f"✅ {question_count} MCQs generated successfully!"
                )

            except ValueError as e:
                st.error(f"❌ {e}")


# -----------------------------
# Quiz
# -----------------------------

if "questions" not in st.session_state:
    st.session_state.questions = None

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False


if st.session_state.questions:

    questions = st.session_state.questions

    st.subheader("📋 Generated MCQs")

    with st.form("quiz"):

        for i, question in enumerate(questions, 1):

            st.radio(
                f"{i}. {question['question']}",
                question["options"],
                key=f"answer_{i}",
                index=None
            )

        submitted = st.form_submit_button(
            "✅ Submit Quiz",
            type="primary",
            use_container_width=True
        )

    # -----------------------------
    # Submit quiz
    # -----------------------------

    if submitted:

        unanswered = [
            i for i in range(1, len(questions) + 1)
            if st.session_state.get(f"answer_{i}") is None
        ]

        if unanswered:
            st.warning(
                "Please answer question(s): "
                + ", ".join(map(str, unanswered))
            )

        else:
            st.session_state.quiz_submitted = True


    # -----------------------------
    # Show result
    # -----------------------------

    if st.session_state.quiz_submitted:

        score = sum(
            st.session_state[f"answer_{i}"]
            == question["correct_answer"]
            for i, question in enumerate(questions, 1)
        )

        percentage = score / len(questions) * 100

        st.success(
            f"🎉 Score: **{score}/{len(questions)} "
            f"({percentage:.0f}%)**"
        )

        for i, question in enumerate(questions, 1):

            selected = st.session_state[f"answer_{i}"]

            if selected == question["correct_answer"]:
                st.success(f"Question {i}: ✅ Correct")

            else:
                st.error(
                    f"Question {i}: ❌ Incorrect — "
                    f"Correct answer: **{question['correct_answer']}**"
                )

            if question.get("explanation"):
                st.caption(
                    f"💡 {question['explanation']}"
                )


  


    # -----------------------------
    # Reset / Clear
    # -----------------------------

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🔄 Reset Quiz (Try Again)",
            use_container_width=True
        ):
            for i in range(1, len(questions) + 1):
                st.session_state.pop(f"answer_{i}", None)

            st.session_state.quiz_submitted = False
            st.rerun()

    with col2:
        if st.button(
            "🗑️ Clear MCQs",
            use_container_width=True
        ):
            for i in range(1, len(questions) + 1):
                st.session_state.pop(f"answer_{i}", None)

            st.session_state.questions = None
            st.session_state.quiz_submitted = False
            st.rerun()