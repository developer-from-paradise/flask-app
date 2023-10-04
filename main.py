from flask import Flask, render_template

app = Flask(__name__)

@app.route('/website1')
def website1_home():
    return render_template('website1/index.html')

@app.route('/website2')
def website2_home():
    return render_template('website2/index.html')



if __name__ == '__main__':
    app.run()