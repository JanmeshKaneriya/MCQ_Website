# MCQ Generator

This project includes a Streamlit website that generates multiple-choice questions
from user-provided text using a local Ollama model.

## Run the website

1. Install the dependencies:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. Make sure Ollama is installed and running, then download a model:

   ```powershell
   ollama serve
   ollama pull qwen3:1.7b
   ```

3. Start Streamlit:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run stream.py
   ```

Paste source material into the text box, choose the number of questions, and
generate the quiz. Select one answer for each generated MCQ and submit the test
to see your score, correct and incorrect answers, and explanations. The generated
questions can also be downloaded as JSON.
