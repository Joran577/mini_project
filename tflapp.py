from flask import Flask, jsonify, json, request
from cassandra.cluster import Cluster

cluster = Cluster(['cassandra'])
session = cluster.connect()

app = Flask(__name__)

with open('lines.json') as l:
    lines = json.load(l)

#method to get the names of all train lines
@app.route('/trains', methods=['GET'])
def get_lines():
    train = [subway['name'] for subway in lines]
    return jsonify({'Train Lines' : train}), 200


#GET method to return the type mode the train is based on the given line
@app.route('/trains/<line>', methods=['GET'])
def get_line(line):
    train = [subway['modeName'] for subway in lines if subway['name'] == line]
    if len(train) == 0:
      return jsonify({'error':'train line not found!'}), 404
    else:
      return jsonify({'Train Type' : train}), 200


#GET method to return the train lines that run on the given mode
@app.route('/trains/type/<mode>', methods=['GET'])
def get_mode(mode):
    tubes = [type['name'] for type in lines if type['modeName'] == mode]
    if len(tubes) == 0:
      return jsonify({'error':'mode not found!'}), 404
    else:
      return jsonify({'Line(s)' : tubes}), 200


#This method adds a train into the database
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


#A method to update the information in the database
@app.route('/trains/<line>', methods=['PUT'])
def update_line(line):
    train = [subway for subway in lines if subway['name'] == line]
    train[0]['name'] = request.json.get('name', train[0]['name'])
    train[0]['modeName'] = request.json.get('modeName', train[0]['modeName'])
    train[0]['id'] = request.json.get('id', train[0]['id'])
    train[0]['modified'] = request.json.get('modified', train[0]['modified'])
    return jsonify({'train' : train[0]}), 200


#This method deletes a train line based on the given name
@app.route('/trains/<line>', methods=['DELETE'])
def remove_line(line):
    trains = [subway for subway in lines if subway['name'] == line]
    if len(trains) == 0:
        return jsonify({'error':'train line not found!'}), 404
    else:
        lines.remove(trains[0])
        return jsonify({'Removed!' : lines})


#This methods returns data from a cassandra database that has statistics on mario kart racers
@app.route('/mario/<name>', methods=['GET'])
def racer(name):
    rows = session.execute( """Select * From characters.stats
                           Where character = '{}'""".format(name))
    for characters in rows:
        return('<h1>{} has a speed of {}!</h1>'.format(name,characters.speed))

    return('<h1>That Racer does not exist!</h1>')  



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
