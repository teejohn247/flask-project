# app.py

from flask import Flask, render_template

# Create the Flask app instance
app = Flask(__name__)

# Define a route for the root URL
@app.route('/', methods=['GET', 'POST'])
def start():
    return render_template('index.html')

# Run the app if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)