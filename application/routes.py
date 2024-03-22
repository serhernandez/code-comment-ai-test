from flask import current_app as app
from flask import jsonify, render_template, request, session

from .clients import openai_client

import markdown

@app.route("/")
def home_page():
    if 'current_model' not in session:
        session['current_model'] = app.config['OPENAI_MODELS'][0]
    return render_template("index.html", models=app.config['OPENAI_MODELS'], curmodel=session['current_model'])

@app.route("/generatecomments", methods=['POST'])
def generate_comments():
    sysprompts =[
        "You are an AI assistant who will receive code from the user and output the code with helpful comments added explaining what the code is doing. Please do not include extra comments outside of the returned code block.",
        "Make a document that goes over the code provided. Please make it detailed and add the params and return values for all methods.",
        "Hello! As a computer scientist, I am seeking your expertise in interpreting and documenting code specifically for Python and SAS languages. When I provide you with code snippets, my expectation is for you to analyze them and then create documentation that clearly explains their functionality, parameters, returns, and any exceptions they might raise. For Python code, please ensure that the documentation follows the official Python documentation style, adhering to docstring conventions and PEP 257. For SAS code, documentation should be similarly detailed, including explanations of data steps, proc steps, and any macros, with clear descriptions of the purpose, usage, parameters, and outputs.The goal is to produce documentation that is both comprehensive and accessible, making it easy for developers of various skill levels to understand and use the code effectively. Could you please assist me with this task?",
        "You are an AI Assistant who will be helping developers understand code. The user will provide code that they would like you to explain, providing clarification for what various libraries and function calls are doing. Please keep explanations simple enough for programmers of all levels to understand, and don't include any extra comments unrelated to the program being explained.",
        "You are an AI Assistant who will be helping developers understand code. The user will provide code that they would like you to explain, providing clarification for what various libraries and function calls are doing. Please keep explanations simple enough for programmers of all levels to understand, and don't include any extra comments unrelated to the program being explained. If possible, please include these comments as annotations to the code itself so the user can reference the explanations as well as the relevant code easily.",
        "You are an AI Assistant who will be helping developers understand code. The user will provide code that they would like you to explain, providing clarification for what various libraries and function calls are doing. Please keep explanations simple enough for programmers of all levels to understand, and don't include any extra comments unrelated to the program being explained. Please include explanations as comments added to the code itself, so that the user can follow along with explanations while also seeing the code being referenced.",
    ]
    messages = [{"role": "system", "content": sysprompts[5]}]
    submittedCode = request.form.get('userInput')
    formattedInput = {"role": "user", "content": submittedCode}
    messages.append(formattedInput)
    completion = openai_client.chat.completions.create(model=session['current_model'], messages=messages, max_tokens=4096)
    response = completion.choices[0].message.content
    formatted_resp = markdown.markdown(response, extensions=['codehilite', 'fenced_code'])
    if app.debug:
        print(f"Sent {completion.usage.prompt_tokens} tokens and received {completion.usage.completion_tokens} tokens back")
    return jsonify([formatted_resp, response])

@app.route("/selectmodel", methods=['PUT'])
def change_model():
    new_model = request.form.get('model')
    if new_model in app.config['OPENAI_MODELS']:
        session['current_model'] = new_model
    if app.debug:
        print(f"Model changed to {new_model} successfully")
    return '', 204