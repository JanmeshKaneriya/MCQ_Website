from ollama import chat
import threading
import itertools
import time
import sys


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

# ▶️Animation trigger
stop_animation = False


def loading_animation():

    spinner = itertools.cycle(["|", "/", "-", "\\"])

    message_index = 0
    counter = 0

    while not stop_animation:

        message = messages[message_index]
        symbol = next(spinner)

        sys.stdout.write(
            f"\r{message} {symbol}                        "
        )

        sys.stdout.flush()

        time.sleep(0.15)

        counter += 1

        # Change status every ~2 seconds
        if counter >= 13:
            counter = 0
            message_index = (message_index + 1) % len(messages)


text = """ text here """


prompt = f"""
Create 20 multiple-choice questions from the following text.

Rules:
- Each question must have exactly 4 options.
- There must be exactly one correct answer.
- Questions must be based only on the supplied text.
- Include the correct answer only at the end of the test.
- Include a short explanation of the answer.
- The format should look like this
Q#: 
A. 
B. 
C. 
D. 

Text:
{text}
"""


# Start loading animation
animation_thread = threading.Thread(target=loading_animation)
animation_thread.start()


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

finally:

    # Stop animation
    stop_animation = True
    animation_thread.join()

    # Clear the loading message
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()


print("\nMCQs generated:\n")
print(response.message.content)