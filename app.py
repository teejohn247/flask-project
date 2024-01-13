# app.py
from __future__ import print_function
import io
import os
import csv
import sys
import json
from flask import Flask, request, render_template, url_for
import pandas as pd
from werkzeug.utils import secure_filename
from io import StringIO

import pickle
import sklearn

# import nltk

# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('punkt')

# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
# from nltk.stem import WordNetLemmatizer



# Create the Flask app instance
app = Flask(__name__)
# app = FastAPI()

basedir = os.path.abspath(os.path.join('../', os.path.dirname(__file__)))
app.config["UPLOAD_FOLDER"] = os.path.join(basedir, 'uploads')

vectorizer = pickle.load(open('models/vectorizer.pkl', 'rb'))
model = pickle.load(open('models/model.pkl', 'rb'))


# Define a route for the root URL
@app.route('/', methods=['GET','POST'])
def start():
    if request.method == 'POST':
        uploaded_file = request.files['csv_file']
        print(uploaded_file, file=sys.stderr)
        
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(file_path)

        df = pd.read_csv(file_path, encoding = "ISO-8859-1")
        df = df[(df['Supplier ID'] != 'RSK')]
        df = df.head()

        X_test = df['Description']

        # Now we can fit our test data with the same vectorizer
        x_test_tfidf = vectorizer.transform(X_test)

        # Model prediction
        prediction = model.predict(x_test_tfidf)

        df['Category'] = prediction

        df['Category'].replace([0, 1, 2], ['Hire Supplier', 'Material Supplier', 'Subcontractor'], inplace=True)

        print(df, file=sys.stderr)
        jsonData = df.to_json(orient='records')
        tableData = json.loads(jsonData)

        # print(tableData[0], file=sys.stderr)

        columnNames = ['Unit', 'Nominal Code', 'Ledger', 'Type', 'Value', 'Ref', 'Date', 'Description', 'Category']
        return render_template('index.html', records=tableData, colnames=columnNames)
    return render_template('index.html')

# def upload():
#     if request.method == 'POST':
#         df = pd.read_csv(request.files.get('file'))
#         print(df, file=sys.stderr)
#         return render_template('index.html')
#     return render_template('index.html')
    

# Run the app if this script is executed directly
if __name__ == '__main__':
    app.debug = True
    app.run()