import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField
from wtforms.validators import DataRequired
from database import Tool, db, Location, locationrel
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, desc, event
from sqlalchemy.engine import Engine
import sqlite3

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'pizza'

db.init_app(app)
@event.listens_for(Engine, "connect")
def enforce_foreign_keys(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

migrate = Migrate(app, db)

with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run()

@event.listens_for(Engine, "connect")
def enforce_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class ToolForm(FlaskForm):
    name = StringField('Tool Name', validators=[DataRequired()])
    type = StringField('Tool Type', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])

@app.route('/', methods=['GET', 'POST'])
def home():
    form = ToolForm()
    return render_template('add_tool.html', form = form)

@app.route('/add_tool', methods=['GET', 'POST'])
def add_tool():
    form = ToolForm()
    used = 0
    if form.validate_on_submit():
        new_tool = Tool(name = form.name.data, type = form.type.data)
        new_location = Location(name = form.location.data)

        db.session.add(new_tool)
        db.session.commit()
        new_tool = db.session.execute(db.select(Tool).order_by(desc(Tool.id))).scalars().first()
        locations = db.session.execute(db.select(Location).
            order_by(desc(Location.id))).scalars()
        for location in locations:
            if new_location.name == location.name:
                new_location = location
                used = 1
                break
        if used == 0:
            db.session.add(new_location)
            new_location = db.session.execute(db.select(Location).order_by(desc(Location.id))).scalars().first()
         
        used = 0
        rel = locationrel.insert().values(tool_id = new_tool.id, loc_id = new_location.id)
        db.session.execute(rel)
        db.session.commit()
        return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/add_location', methods=['POST'])
def add_location():
    loc_name = request.form.get('loc_name')
    if loc_name:
        location = Location(name=loc_name)
        db.session.add(location)
        db.session.commit()
    return redirect(url_for('add_tool'))

@app.route("/new_tool", methods=['GET'])
def handle_new_tool():
    tool = db.session.execute(db.select(Tool).order_by(desc(Tool.id))).scalars().first()
    location = db.session.execute(db.select(Location)
        .join(locationrel, locationrel.c.loc_id == Location.id)
        .where(locationrel.c.tool_id == tool.id)).scalars().first()
    tool_text = ''
    tool_text = tool.name + ' (' + tool.type + ') - Location: ' + location.name + '<br>'
    return render_template('new_tool.html', tool_text = tool_text)
@app.route("/new_tool", methods=['POST'])
def new_tool_post():
    return redirect(url_for('add_tool'))

@app.route("/get_all_tool", methods=['GET'])
def handle_all_tool():
    sort = request.args.get('sort', 'name')  # default to name
    order = request.args.get('order', 'asc')    # Default: ascending

    tools = Tool.query.all()
    tools_with_locations = []

    for tool in tools:
        location = tool.locations[0] if tool.locations else None
        tools_with_locations.append({'tool': tool, 'location': location})

    reverse = (order == 'desc')

    if sort == 'name':
        tools_with_locations.sort(key=lambda x: x['tool'].name.lower(), reverse = reverse)
    elif sort == 'type':
        tools_with_locations.sort(key=lambda x: x['tool'].type.lower(), reverse = reverse)
    elif sort == 'location':
        tools_with_locations.sort(
            key=lambda x: x['location'].name.lower() if x['location'] else '', reverse = reverse
        )

    return render_template(
        'all_tools.html',
        tools_with_locations = tools_with_locations,
        sort = sort,
        order = order
    )
@app.route("/get_all_tool", methods=['POST'])
def all_tool_post():
    return redirect(url_for('add_tool'))

@app.route("/get_all_loc", methods=['GET'])
def handle_all_loc():
    order = request.args.get('order', 'asc')
    reverse = (order == 'desc')

    locations = Location.query.order_by(Location.name.asc()).all()

    locations.sort(key=lambda x: x.name.lower(), reverse=reverse)

    return render_template(
        'all_locs.html',
        locations = locations,
        order = order
    )
@app.route("/get_all_loc", methods=['POST'])
def all_loc_post():
    return redirect(url_for('add_tool'))

@app.route('/delete_tool/<int:tool_id>', methods=['POST'])
def delete_tool(tool_id):
    tool = db.session.get(Tool, tool_id)
    if tool:
        db.session.delete(tool)
        db.session.commit()
    return redirect(url_for('handle_all_tool'))

@app.route('/delete_loc/<int:loc_id>', methods=['POST'])
def delete_loc(loc_id):
    location = db.session.get(Location, loc_id)
    if location:
        db.session.delete(location)
        db.session.commit()
    return redirect(url_for('handle_all_loc'))

@app.route('/change_location/<int:tool_id>', methods=['GET', 'POST'])
def change_location_form(tool_id):
    tool = Tool.query.get_or_404(tool_id)
    locations = Location.query.all()

    if request.method == 'POST':
        new_loc_id = request.form.get('loc_id')

        # Delete existing locationrel entry
        db.session.execute(locationrel.delete().where(locationrel.c.tool_id == tool.id))

        # Add new one if selected
        if new_loc_id:
            db.session.execute(locationrel.insert().values(tool_id=tool.id, loc_id=int(new_loc_id)))

        db.session.commit()
        return redirect(request.form.get('next') or url_for('all_tools'))

    return render_template('change_location.html', tool=tool, locations=locations)

@app.route('/location_tools/<int:loc_id>', methods=['GET', 'POST'])
def location_tools(loc_id):
    # Fetch location and associated tools
    sort = request.args.get('sort', 'name')  # default to name
    order = request.args.get('order', 'asc')    # Default: ascending
    location = Location.query.get_or_404(loc_id)
    tools = location.tools
    tools_with_locations = [{'tool': t, 'location': location} for t in tools]

    reverse = (order == 'desc')

    if sort == 'name':
        tools_with_locations.sort(key=lambda x: x['tool'].name.lower(), reverse = reverse)
    elif sort == 'type':
        tools_with_locations.sort(key=lambda x: x['tool'].type.lower(), reverse = reverse)
    elif sort == 'location':
        tools_with_locations.sort(
            key=lambda x: x['location'].name.lower() if x['location'] else '', reverse = reverse
        )
    
    return render_template(
        'all_tools.html',
        tools_with_locations = tools_with_locations,
        location = location,
        sort = sort,
        order = order
    )
