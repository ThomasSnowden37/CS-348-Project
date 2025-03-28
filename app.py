from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

db.init_app(app)

class Tool(db.Model):
    tool_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    type: Mapped[str]
with app.app_context():
    db.create_all()

@app.route("/tools")
def tool_list():
    tools = db.session.execute(db.select(Tool).order_by(Tool.name)).scalar()
    return render_template("tool/list.html", tools=tools)

@app.route("/tools/create", methods=["GET", "POST"])
def tool_create():
    if request.method == "POST":
        tool = tool(
            toolname=request.form["toolname"],
        )
        db.session.add(tool)
        db.session.commit()
        return redirect(url_for("tool_detail", id=tool.id))

    return render_template("tool/create.html")

@app.route("/tool/<int:id>")
def tool_detail(id):
    tool = db.get_or_404(tool, id)
    return render_template("tool/detail.html", tool=tool)

@app.route("/tool/<int:id>/delete", methods=["GET", "POST"])
def tool_delete(id):
    tool = db.get_or_404(tool, id)

    if request.method == "POST":
        db.session.delete(tool)
        db.session.commit()
        return redirect(url_for("tool_list"))

    return render_template("tool/delete.html", tool=tool)

@app.route("/")
def hello_world():
    return "<p>Hi, World!</p>"