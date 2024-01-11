# app.py
from __future__ import print_function
from flask import Flask, request, render_template, url_for
import pandas as pd
import sys

# Create the Flask app instance
app = Flask(__name__)

# Define a route for the root URL
@app.route('/', methods=['GET','POST'])
def start():
    if request.method == 'POST':
        f = request.files['csv_file']
        print(f, file=sys.stderr)
        # f.seek(0)
        # myfile = f.read()
        # print(myfile, file=sys.stderr)
        # df = pd.read_csv(request.files.get('file'))
        # print(df, file=sys.stderr)
        return render_template('index.html')
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