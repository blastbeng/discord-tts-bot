from flask import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('index.html')

@app.route('/conversation', methods=['GET', 'POST'])
def conversation():
    return render_template('conversation.html')

if __name__ == '__main__':
    app.run(debug=True)
