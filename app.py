from flask import Flask, request, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, render_template
from json import JSONEncoder
from sqlalchemy.ext.declarative import DeclarativeMeta
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'


db = SQLAlchemy(app)

class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    done = db.Column(db.Boolean, default=False)

    def __init__(self, content):
        self.content = content
        self.done = False

    def __repr__(self):
        return 'title: %s' % self.content


db.create_all()


# @app.route('/')
# def tasks_list():
#     tasks = Task.query.all()   
#     #print(type(tasks))
#     json_string = json.dumps(tasks, cls=AlchemyEncoder)
#     #print(json_string)
#     return render_template('list.html', tasks=tasks)

@app.route('/send')
def tasks_view():
    tasks = Task.query.all()   
    print(type(tasks))
    json_string = json.dumps(tasks, cls=AlchemyEncoder)
    print(json_string)
    return json_string




# @app.route('/task', methods=['POST'])
# def add_task():
#     content = request.form['content']
#     if not content:
#         return 'Error'

#     task = Task(content)
#     db.session.add(task)
#     db.session.commit()
#     return redirect('/')

@app.route('/task/<string:content>')
def add_task(content):
    content = content
    if not content:
        return 'Error'

    task = Task(content)
    db.session.add(task)
    db.session.commit()
    return redirect('/send')


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return redirect('/send')

    db.session.delete(task)
    db.session.commit()
    return redirect('/send')


@app.route('/done/<int:task_id>')
def resolve_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return redirect('/send')
    if task.done:
        task.done = False
    else:
        task.done = True

    db.session.commit()
    return redirect('/send')




if __name__=='__main__':
    app.run(debug=True)