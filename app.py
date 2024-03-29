# app.py
from __future__ import print_function
import io
import os
import csv
import sys
import json
from flask import Flask, request, render_template, url_for
import numpy as np
import pandas as pd
from werkzeug.utils import secure_filename
from io import StringIO
import pickle



# Create the Flask app instance
app = Flask(__name__)
# app = FastAPI()

basedir = os.path.abspath(os.path.join('../', os.path.dirname(__file__)))
app.config["UPLOAD_FOLDER"] = os.path.join(basedir, 'uploads')

vectorizer = pickle.load(open('models/vectorizer.pkl', 'rb'))
model = pickle.load(open('models/model.pkl', 'rb'))


# Define a route for the root URL
@app.route('/', methods=['GET','POST'])
def index():    
    if request.method == 'POST':
        uploaded_file = request.files['csv_file']
        print(uploaded_file, file=sys.stderr)
        
        filename = secure_filename(uploaded_file.filename)
        print(filename, file=sys.stderr)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(file_path)

        df = pd.read_csv(file_path, encoding = "ISO-8859-1")
        #Drop all the Null/Misiing Values.
        df.dropna(inplace=True)

        # df['Cost'] = np.random.randint(0,10000, size=len(df))

        df_Internal = df[(df['Supplier ID'] == 'RSK')]
        df_Internal['Category'] = 'Internal Supplier'

        df = df[(df['Supplier ID'] != 'RSK')]

        X_test = df['Description']

        # Now we can fit our test data with the same vectorizer
        x_test_tfidf = vectorizer.transform(X_test)

        # Model prediction
        prediction = model.predict(x_test_tfidf)

        df['Category'] = prediction

        df['Category'].replace([0, 1, 2], ['Hire Supplier', 'Material Supplier', 'Subcontractor'], inplace=True)

        df_combined = pd.concat([df, df_Internal], ignore_index=True, sort=True)
        new_df = df_combined.copy()

        new_df.to_csv('static/docs/classified_invoice.csv', index=False)
        
        # with open("classified_invoice.csv", "w") as csv_file:
        #     csv_file.write(f'{new_file}')

        category_agg = df_combined.groupby('Category')['Value'].agg(['sum','count'])

        category_costs = category_agg["sum"].values.tolist()
        category_counts = category_agg["count"].values.tolist()

        print(category_agg['sum'], file=sys.stderr)
        print(category_agg['count'], file=sys.stderr)

        # print(df, file=sys.stderr)
        jsonData = df_combined.to_json(orient='records')
        tableData = json.loads(jsonData)

        #Pagination
        page = request.args.get('page', 1, type='int')
        per_page = 200
        start = (page - 1) * per_page
        end = start + per_page
        total_pages = (len(tableData) + per_page - 1) // per_page
        data_per_page = tableData[start:end] 

        # print(tableData[0], file=sys.stderr)
        category_names = ['Hire Supplier', 'Internal Supplier', 'Material Supplier', 'Subcontractor']

        columnNames = ['Unit', 'Nominal Code', 'Ref', 'Description', 'Value', 'Supplier ID', 'Category']

        return render_template(
            'index.html', 
            colnames=columnNames, 
            records=data_per_page, 
            pages_count=total_pages, 
            current_page=page,
            categories = category_names,
            cost_sum = category_costs, 
            category_counts = category_counts,
            display_style = 'hidden'
        )
    
    return render_template('index.html', display_style = 'visible')
    

# Run the app if this script is executed directly
if __name__ == '__main__':
    app.debug = True
    app.run()