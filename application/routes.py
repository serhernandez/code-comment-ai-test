from flask import current_app as app
from flask import render_template, request, session

from .clients import openai_client

import markdown

@app.route("/")
def home_page():
    if 'current_model' not in session:
        session['current_model'] = app.config['OPENAI_MODELS'][0]
    return render_template("index.html", models=app.config['OPENAI_MODELS'], curmodel=session['current_model'])

@app.route("/generatecomments", methods=['POST'])
def generate_comments():
    messages = [{"role": "system", "content": "You are an AI assistant who will receive code from the user and output the code with helpful comments added explaining what the code is doing. Please do not include extra comments outside of the returned code block."}]
    submittedCode = request.form.get('userInput')
    formattedInput = {"role": "user", "content": submittedCode}
    messages.append(formattedInput)
    completion = openai_client.chat.completions.create(model=session['current_model'], messages=messages, max_tokens=4096)
    response = completion.choices[0].message.content
    formatted_resp = markdown.markdown(response, extensions=['codehilite', 'fenced_code'])
    if app.debug:
        print(f"Sent {completion.usage.prompt_tokens} tokens and received {completion.usage.completion_tokens} tokens back")
    return formatted_resp

@app.route("/selectmodel", methods=['PUT'])
def change_model():
    new_model = request.form.get('model')
    if new_model in app.config['OPENAI_MODELS']:
        session['current_model'] = new_model
    if app.debug:
        print(f"Model changed to {new_model} successfully")
    return '', 204