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
    location = StringField('location')

@app.route('/', methods=['GET', 'POST'])
def add_tool():
    form = RegistrationForm(request.form)
    if request.form.get('Add'):
        if request.method == 'POST' and form.validate():
            new_tool = Tool(name = form.name.data, type = form.type.data)
            new_location = Location(name = form.location.data)
            try:
                db.session.add(new_tool)
                db.session.add(new_location)
                db.session.commit()
            except:
                return jsonify({'status': 0, 'message': 'Tool could not be added to database.'}), 500
            return redirect(url_for('handle_new_tool'))
    if request.form.get('All Tools'):
        return redirect(url_for('handle_all_tool'))
    return render_template('add_tool.html', form = form)

@app.route("/new_tool", methods=['GET'])
def handle_new_tool():
    tool = db.session.execute(db.select(Tool).order_by(desc(Tool.id))).scalars().first()
    tool_text = ''
    tool_text = tool.name + ', ' + tool.type + '<br>'
    return render_template('all_tools.html', tool_text = tool_text)
@app.route("/new_tool", methods=['POST'])
def new_tool_post():
    return redirect(url_for('add_tool'))

@app.route("/get_all_tool", methods=['GET'])
def handle_all_tool():
    tools = db.session.execute(db.select(Tool).
        order_by(desc(Tool.id))).scalars()
    tool_text = ''
    for tool in tools:
        tool_text += tool.name + ', ' + tool.type + '<br>'
    #return tool_text
    return render_template('all_tools.html', tool_text = tool_text)
@app.route("/get_all_tool", methods=['POST'])
def all_tool_post():
    return redirect(url_for('add_tool'))

@app.route("/get_all_loc", methods=['GET'])
def handle_all_loc():
    locations = db.session.execute(db.select(Location).
        order_by(desc(Location.id))).scalars()
    loc_text = ''
    for location in locations:
        loc_text += location.name + '<br>'
    #return tool_text
    return render_template('all_tools.html', tool_text = loc_text)
@app.route("/get_all_loc", methods=['POST'])
def all_loc_post():
    return redirect(url_for('add_tool'))