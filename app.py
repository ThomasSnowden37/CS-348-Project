import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from database import Tool, db, Location
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, desc


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run()

class RegistrationForm(Form):
    name = StringField('name')
    type = StringField('type')

@app.route('/', methods=['GET', 'POST'])
def add_tool():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        new_tool = Tool(name = form.name.data, type = form.type.data)
        try:
            db.session.add(new_tool)
            db.session.commit()
        except:
            return jsonify({'status': 0, 'message': 'Tool could not be added to database.'}), 500
        return redirect(url_for('handle_all_tool'))
    return render_template('add_tool.html', form = form)
'''
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
'''
@app.route("/get_all_tools", methods=['GET'])
def handle_all_tool():
    tools = db.session.execute(db.select(Tool).
        order_by(desc(Tool.id))).scalars()
    tool_text = ''
    for tool in tools:
        tool_text += tool.name + ', ' + tool.type + '<br>'
    #return tool_text
    return render_template('all_tools.html', tool_text = tool_text)
@app.route("/tool", methods=['POST'])
def my_form_post():
    return redirect(url_for('add_tool'))