from flask import Flask, render_template, jsonify
from pyModbusTCP.client import ModbusClient
from time import sleep

app = Flask(__name__)

# Configuration Modbus
slaveAddress = '192.168.1.22'
slavePort = 502
client = ModbusClient(slaveAddress, port=slavePort, unit_id=1)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_filling')
def start_filling():
    if client.is_open:
        client.write_single_register(valve_empty, 0)  # Ferme valve vidange
        client.write_single_register(valve_fill, 5000)  # Ouvre valve remplissage
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

if __name__ == '__main__':
    app.run(debug=True)
