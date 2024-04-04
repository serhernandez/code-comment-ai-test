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
        """I have a Python codebase that may implement various functionalities like database management, account operations, and user authentication.
Objective: I'm seeking an in-depth review and complete documentation of this codebase. The goal is to enhance clarity, efficiency, and maintainability, ensuring it aligns with best practices. The documentation should be detailed, covering every function, and formatted in Markdown for readability.
Requirements:
1.	Overview Creation:
o	Provide a succinct summary of the codebase, highlighting its primary functions and the problems it addresses.
2.	Code Review Components:
o	Efficiency Analysis: Identify any code inefficiencies or redundancies and propose specific optimizations.
o	Clarity Assessment: Evaluate code readability and structure. Offer suggestions for improving clarity, including better naming conventions or necessary refactoring.
o	Error Handling Evaluation: Examine the code's approach to error handling and robustness. Pinpoint potential failure points and recommend improvements.
3.	Documentation Enhancement Criteria:
o	Libraries and Dependencies: List and describe all external libraries or dependencies, emphasizing their roles within the code.
o	Function Documentation: For each function, provide:
-	Name
-	Purpose: A brief description of its functionality.
-	Parameters: Detail each parameter, including type and a short description.
-	Return Values: Specify the return types and their significance.
-	Exceptions/Errors: List any potential exceptions or errors raised.
-	Include simple usage examples where applicable.
o	Global Variables Documentation: Describe any global variables, explaining their purposes and interactions within the code.
4.	Additional Guidelines:
o	The documentation should be thorough, addressing all outlined aspects to support future development and enhance maintainability.
o	Should any code sections require clarification or further explanation, immediate communication is encouraged.
Format: Please format the documentation in Markdown to ensure it is well-organized and easy to navigate.
End Goal: Your expertise and input are highly valued, aiming to significantly elevate the quality and comprehensibility of our codebase through structured and comprehensive documentation.
Additional notes: In the case of multiple files, these files will be preceded by their filename.
""",
    ]
    messages = [{"role": "system", "content": sysprompts[6]}]
    submittedCode = request.form.get('userInput')
    formattedInput = {"role": "user", "content": submittedCode}
    messages.append(formattedInput)
    completion = openai_client.chat.completions.create(model=session['current_model'], messages=messages, max_tokens=app.config['MAX_TOKENS'], temperature=app.config['TEMPERATURE'])
    response = [completion.choices[0].message.content]
    if app.debug:
        print(f"Sent {completion.usage.prompt_tokens} tokens and received {completion.usage.completion_tokens} tokens back")
    while completion.choices[0].finish_reason == "length":
        messages.append({"role": "assistant", "content": response[-1]})
        completion = openai_client.chat.completions.create(model=session['current_model'], messages=messages, max_tokens=app.config['MAX_TOKENS'], temperature=app.config['TEMPERATURE'])
        response.append(completion.choices[0].message.content)
        if app.debug:
            print(f"Sent {completion.usage.prompt_tokens} tokens and received {completion.usage.completion_tokens} tokens back")
    formatted_resp = markdown.markdown("".join(response), extensions=['codehilite', 'fenced_code'])
    
    return jsonify([formatted_resp, "".join(response)])

@app.route("/selectmodel", methods=['PUT'])
def change_model():
    new_model = request.form.get('model')
    if new_model in app.config['OPENAI_MODELS']:
        session['current_model'] = new_model
    if app.debug:
        print(f"Model changed to {new_model} successfully")
    return '', 204