from flask import Flask, jsonify, json, request


app = Flask(__name__)

with open('lines.json') as l:
    lines = json.load(l)

@app.route('/trains', methods=['GET'])
def get_lines():
    return jsonify(lines)


@app.route('/trains/<line>', methods=['GET'])
def get_line(line):
    train = [subway for subway in lines if subway['name'] == line]
    if len(train) == 0:
      return jsonify({'error':'train line not found!'}), 404
    else:
      return jsonify({'Lines' : train}), 200


@app.route('/trains/type/<mode>', methods=['GET'])
def get_mode(mode):
    tubes = [type['name'] for type in lines if type['modeName'] == mode]
    if len(tubes) == 0:
      return jsonify({'error':'mode not found!'}), 404
    else:
      return jsonify({'Line(s)' : tubes}), 200


@app.route('/trains', methods=['POST'])
def add_line():
    new_line = {
        'name': request.json['name'],
        'modeName': request.json.get('modeName', ""),
        'id': request.json.get('id', ""),
        'modified': request.json.get('modified', "")
    }
    lines.append(new_line)
    return jsonify({'Lines' : lines}), 201


@app.route('/trains/<line>', methods=['PUT'])
def update_line(line):
    train = [subway for subway in lines if subway['name'] == line]
    train[0]['name'] = request.json.get('name', train[0]['name'])
    train[0]['modeName'] = request.json.get('modeName', train[0]['modeName'])
    train[0]['id'] = request.json.get('id', train[0]['id'])
    train[0]['modified'] = request.json.get('modified', train[0]['modified'])
    return jsonify({'train' : train[0]}), 200


@app.route('/trains/<line>', methods=['DELETE'])
def remove_line(line):
    trains = [subway for subway in lines if subway['name'] == line]
    if len(trains) == 0:
        return jsonify({'error':'train line not found!'}), 404
    else:
        lines.remove(trains[0])
        return jsonify({'Removed!' : lines})


if __name__ == '__main__':
	app.run(debug=True)
