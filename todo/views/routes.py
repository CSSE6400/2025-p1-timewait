from flask import Blueprint, jsonify, request, abort
from datetime import datetime, timedelta

api = Blueprint('api', __name__, url_prefix='/api/v1')
@api.route('/health')
def health():
    return jsonify({"status": "ok"})


# just saving tasks in memory.
tasks = []
next_id = 1
@api.route('/todos', methods=['GET'])
def get_todos():
    completed = request.args.get('completed')
    window = request.args.get('window', type=int)
    filtered_tasks = tasks

    if completed is not None:
        completed = completed.lower() == 'true'
        filtered_tasks = [task for task in filtered_tasks if task['completed'] == completed]

    if window is not None:
        due_date = datetime.now() + timedelta(days=window)
        filtered_tasks = [task for task in filtered_tasks if datetime.fromisoformat(task['deadline_at']) <= due_date]

    return jsonify(filtered_tasks), 200

@api.route('/todos/<int:task_id>', methods=['GET'])
def get_todo(task_id):
    task = next((task for task in tasks if task['id'] == task_id), None)
    if task is None:
        abort(404)
    return jsonify(task), 200

@api.route('/todos', methods=['POST'])
def create_todo():
    if not request.json or 'title' not in request.json:
        abort(400)

    global next_id
    task = {
        'id': next_id,
        'title': request.json['title'],
        'description': request.json.get('description', ''),
        'completed': request.json.get('completed', False),
        'deadline_at': request.json.get('deadline_at', datetime.now().isoformat()),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    tasks.append(task)
    next_id += 1
    return jsonify(task), 201

@api.route('/todos/<int:task_id>', methods=['PUT'])
def update_todo(task_id):
    task = next((task for task in tasks if task['id'] == task_id), None)
    if task is None:
        abort(404)

    if not request.json:
        abort(400)

    for key in ['title', 'description', 'completed', 'deadline_at']:
        if key in request.json:
            task[key] = request.json[key]

    task['updated_at'] = datetime.now().isoformat()
    return jsonify(task), 200

@api.route('/todos/<int:task_id>', methods=['DELETE'])
def delete_todo(task_id):
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    return '', 200

if __name__ == '__main__':
    app.run(debug=True)
