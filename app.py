from flask import Flask, request, render_template, redirect, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import pandas as pd
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key='secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password=db.Column(db.String(100))

    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
        
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

with app.app_context():
    db.create_all()



@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        #handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/templates/login.html')

    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        #handle request
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['name'] = user.name
            session['email'] = user.email
            session['password'] = user.password
            return redirect('templates/dashboard.html')
        else:
            return render_template('templates/login.html',error='Invalid user')

    return render_template('login.html')


@app.route('/templates/dashboard.html')
def dashboard():
    if session['name']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('templates/dashboard.html')


    return render_template('templates/login.html')



@app.route('/filter', methods=['POST'])
def filter_data():
    # Implement filtering logic here based on user inputs (request.form)
    # Retrieve filtered data from the database and return as JSON
    filtered_data = []
    return jsonify(filtered_data)

@app.route('/export/<format>', methods=['POST'])
def export_data(format):
    data = Data.query.all()

    # Convert data to a Pandas DataFrame
    df = pd.DataFrame([(item.name, item.email) for item in data], columns=['Name', 'Email'])

    # Export data based on the selected format
    if format == 'csv':
        filepath = 'exported_data.csv'
        df.to_csv(filepath, index=False)
    elif format == 'xls':
        filepath = 'exported_data.xls'
        df.to_excel(filepath, index=False, engine='openpyxl')
    elif format == 'pdf':
        filepath = 'exported_data.pdf'
        df.to_pdf(filepath, index=False)  # You need to have a library for PDF export (e.g., xlsxwriter)

    # Return the exported file to the user
    return send_file(filepath, as_attachment=True)    

#@app.route('/logout')
#def logout():
#    session.pop('email',none)
#    return redirect('templates/login.html')

if __name__ == '__main__':
#    db.create_all()
    app.run(debug=True)