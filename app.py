"""Streamlit interface for generating multiple-choice quizzes with Ollama."""

from __future__ import annotations

import os
from typing import Any

import streamlit as st
from ollama import ResponseError, chat


DEFAULT_TEXT = """Artificial Intelligence (AI) is the ability of computers and machines
to perform tasks that normally require human intelligence. These tasks include learning
from information, understanding language, recognizing images, solving problems, making
decisions, and identifying patterns. AI is used in healthcare, education, transportation,
and business. It can process large amounts of information quickly and automate repetitive
tasks, but it can also create challenges involving privacy, accuracy, bias, and changes
to the nature of some jobs."""


def build_prompt(source_text: str, question_count: int) -> str:
    return f"""Create {question_count} multiple-choice questions from the text below.

Follow these rules exactly:
- Number each question.
- Give each question exactly four options labeled A, B, C, and D.
- There must be exactly one correct answer per question.
- Use only information from the supplied text.
- After the options, write `**Answer:** <letter>. <answer text>`.
- Add a one-sentence `**Explanation:**` for every answer.
- Do not include an introduction or any content outside the questions.

Text:
{source_text}
"""


def generate_mcqs(source_text: str, question_count: int, model: str) -> str:
    response: Any = chat(
        model=model,
        messages=[{"role": "user", "content": build_prompt(source_text, question_count)}],
    )
    content = response.message.content
    if not content or not content.strip():
        raise ValueError("Ollama returned an empty response.")
    return content.strip()


st.set_page_config(
    page_title="MCQ Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { max-width: 1100px; padding-top: 3rem; }
    .hero { padding: 1.5rem 0 1rem; }
    .hero h1 { margin-bottom: .35rem; }
    .hero p { color: #667085; font-size: 1.05rem; }
    div[data-testid="stForm"] { border: 1px solid #e5e7eb; border-radius: 12px; padding: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><h1>📝 MCQ Generator</h1>'
    "<p>Turn your notes, articles, or study material into a ready-to-use quiz with Ollama.</p>"
    "</div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Quiz settings")
    model = st.text_input(
        "Ollama model",
        value=os.getenv("OLLAMA_MODEL", "qwen3:4b"),
        help="The model must already be downloaded in Ollama, for example: ollama pull qwen3:4b",
    ).strip()
    question_count = st.slider("Number of questions", min_value=1, max_value=20, value=5)
    st.divider()
    st.caption("Make sure Ollama is running before generating a quiz.")
    st.code("ollama serve", language="powershell")

with st.form("mcq_form"):
    source_text = st.text_area(
        "Source material",
        value=DEFAULT_TEXT,
        height=300,
        placeholder="Paste the content you want to turn into multiple-choice questions...",
        help="Questions are generated only from the text entered here.",
    )
    submitted = st.form_submit_button(
        "✨ Generate MCQs",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not source_text.strip():
        st.warning("Please enter some source material first.")
    elif not model:
        st.warning("Please enter an Ollama model name.")
    else:
        with st.spinner("Generating your quiz..."):
            try:
                st.session_state["mcq_result"] = generate_mcqs(
                    source_text.strip(), question_count, model
                )
                st.session_state["mcq_model"] = model
            except ResponseError as error:
                if error.status_code == 404:
                    st.error(
                        f"Model `{model}` was not found. Download it with `ollama pull {model}` "
                        "and try again."
                    )
                else:
                    st.error(f"Ollama could not generate the quiz: {error}")
            except (ConnectionError, OSError) as error:
                st.error(
                    "Could not connect to Ollama. Start Ollama with `ollama serve` "
                    f"and try again. Details: {error}"
                )
            except ValueError as error:
                st.error(str(error))

result = st.session_state.get("mcq_result")
if result:
    st.divider()
    st.subheader("Your quiz")
    st.caption(f"Generated with `{st.session_state.get('mcq_model', model)}`")
    st.markdown(result)
    st.download_button(
        "⬇️ Download quiz as Markdown",
        data=result,
        file_name="generated_mcq.md",
        mime="text/markdown",
    )
