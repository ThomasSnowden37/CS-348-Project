import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from database import Tool, db, Location
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db.init_app(app)

with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run()

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/")
def my_form():
    return render_template('my-form.html')
@app.route("/", methods=['POST'])
def my_form_post():
    text = request.form['text']
    processed_text = text.upper()
    return processed_text

@app.route("/add_tool", methods=['POST'])
def handle_add_tool():
    name = request.json['name']
    type = request.json['type']
    loc = request.json['loc']
    new_tool = Tool(
        name = name,
        type = type
    )
    db.session.add(new_tool)
    db.session.commit()
    return jsonify({"status": 1,
                    "id": new_tool.id,
                    "message": f"Item {new_tool.name} added successfully."
                    }), 200