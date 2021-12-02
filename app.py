from flask import Flask, render_template, request, redirect
import pymongo
import os 
from dotenv import load_dotenv
from pymongo import MongoClient

app = Flask(__name__)


# cluster = MongoClient()
load_dotenv()
MONGO_URI   = os.getenv("MONGO_URI")
cluster = MongoClient(MONGO_URI)


# Database name
db = cluster['paper']


# Collection name
collection = db['paper_review']
score = db['score']
    
@app.route('/')
def my_form():
    
    return render_template('submit.html')


@app.route("/", methods=["GET", "POST"])
def submit():
    
    title       = request.form.get('title')
    paper_link  = request.form.get('paper_link')
    
    new_title_id = get_last_title_id()
    collection.insert_one(
        {'title': title, 'paper_link': paper_link, 'title_id':new_title_id })

    
    return render_template('submit.html')

def get_last_title_id():
    
    last_title_id = collection.find().sort([('title_id',-1)]).limit(1)
    try:
        last_title_id = last_title_id[0]['title_id']
    except:
        last_title_id = 0

    return last_title_id + 1


@app.route('/papers')
def choose_paper():
    
    all_links = collection.find({})
    result = []
    for data in all_links:
        del data['_id']
        result.append(data)
        
    
    return render_template('papers.html', result = result)


@app.route("/review/<title_id>", methods=['GET'])

def get_info(title_id):
    
    all_links = collection.find_one({'title_id': int(title_id)})
    return render_template('review.html' , result = all_links )


@app.route("/review/submit", methods=['POST'])
def review():

    if request.method == 'POST':
        
        title_id        = request.form.get('title_id')
        
        category        = request.form.get('category')
        context         = request.form.get('context')
        correct         = request.form.get('correct')
        contributions   = request.form.get('contributions')
        clarity         = request.form.get('clarity')
        overall_score   = request.form.get('overall_score')

        paper = collection.find({'title_id': int(title_id)})

        try:

             for item in paper:
                paper_id = item['title_id']
                current_data = { 'reference': paper_id, 'category': category, 'context': context, 'correct': correct,
                                    'contributions': contributions, 'clarity': clarity, 'overall_score': overall_score}
                score.insert_one(current_data)
                
                print(current_data)
        
        except:
            return "Paper Doesn't Exist"
        

    return redirect(f'/review/{title_id}')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")