from flask import current_app as app
from flask import render_template, request

from .clients import openai_client

import markdown

@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/generatecomments", methods=['POST'])
def generate_comments():
    messages = [{"role": "system", "content": "You are an AI assistant who will receive code from the user and output the code with helpful comments added explaining what the code is doing. Please do not include extra comments outside of the returned code block."}]
    submittedCode = request.form.get('userInput')
    formattedInput = {"role": "user", "content": submittedCode}
    messages.append(formattedInput)
    completion = openai_client.chat.completions.create(model='gpt-4-turbo-preview', messages=messages, max_tokens=4096)
    response = completion.choices[0].message.content
    formatted_resp = markdown.markdown(response, extensions=['codehilite', 'fenced_code'])
    if app.debug:
        print(f"Sent {completion.usage.prompt_tokens} tokens and received {completion.usage.completion_tokens} tokens back")
    return formatted_resp