from flask_bootstrap import Bootstrap5
from flask import Flask, jsonify, render_template, request

from langchain import SQLDatabase, SQLDatabaseChain
from langchain.chat_models import ChatOpenAI

API_KEY = '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'


app = Flask(__name__)
bootstrap = Bootstrap5(app)

db = SQLDatabase.from_uri(
    f"postgresql+psycopg2://postgres:mysecretpassword@localhost:5432/NorthWind",
)

llm = ChatOpenAI(temperature=0, openai_api_key=API_KEY, model_name='gpt-3.5-turbo')

# Create query instruction
QUERY = """
Given an input question, first create a syntactically correct postgresql query to run, then look at the results of the query and return the answer.
Use the following format:

Question: "Question here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Answer"

{question}
"""

# Setup the database chain
db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=False)

def get_prompt(question):
    response = 'failed'
    try:
        prompt = QUERY.format(question=question)
        response = db_chain.run(prompt)
    except Exception as e:
        print(e)
    return response


@app.route('/', methods=['GET','POST'])
def index():
    print("HI")
    print(request.form)
    if request.method == "POST":
        print("requested")
        question = request.form['question']
        print(question)
        if question:
            response = get_prompt(question)
            return jsonify({'output': response})
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)