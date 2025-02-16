#! python3

###########
# IMPORTS #
###########

from flask import Flask, render_template, jsonify
from pyModbusTCP.client import ModbusClient
from time import sleep
import threading

#############
# VARIABLES #
#############

slaveAddress = '192.168.1.22'
slavePort = 502

# Inputs
button_stop = 0
button_fill = 1
button_empty = 2

# Input Register
level = 0
pressure = 1

# Coils
siren = 5
light = 6

# Holding Register
valve_fill = 1
valve_empty = 2

########
# CODE #
########

app = Flask(__name__)
client = ModbusClient(slaveAddress, port=slavePort, unit_id=1)

def modbus_control():
    while True:
        if client.read_discrete_inputs(button_fill, 1)[0]:
            client.write_single_register(valve_empty, 0)
            client.write_single_register(valve_fill, 5000)

        if not client.read_discrete_inputs(button_empty, 1)[0]:
            client.write_single_register(valve_fill, 0)
            client.write_single_register(valve_empty, 5000)

        if not client.read_discrete_inputs(button_stop, 1)[0]:
            client.write_single_register(valve_fill, 0)
            client.write_single_register(valve_empty, 0)

        if client.read_input_registers(level, 1)[0] > 850:
            client.write_single_coil(light, 1)
        else:
            client.write_single_coil(light, 0)

        if client.read_input_registers(pressure, 1)[0] > 950:
            client.write_single_coil(siren, 1)
        else:
            client.write_single_coil(siren, 0)

        if client.read_input_registers(level, 1)[0] >= 980:
            client.write_single_register(valve_fill, 0)
            client.write_single_register(valve_empty, 0)

        sleep(1)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/fill')
def fill():
    if client.is_open:
        client.write_single_register(valve_empty, 0)
        client.write_single_register(valve_fill, 5000)
        return jsonify({"status": "success", "message": "Remplissage démarré"})
    return jsonify({"status": "error", "message": "Erreur de connexion"})

@app.route('/empty')
def empty():
    if client.is_open:
        client.write_single_register(valve_fill, 0)
        client.write_single_register(valve_empty, 5000)
        return jsonify({"status": "success", "message": "Vidage démarré"})
    return jsonify({"status": "error", "message": "Erreur de connexion"})

@app.route('/stop')
def stop():
    if client.is_open:
        client.write_single_register(valve_fill, 0)
        client.write_single_register(valve_empty, 0)
        return jsonify({"status": "success", "message": "Système arrêté"})
    return jsonify({"status": "error", "message": "Erreur de connexion"})

@app.route('/get_status')
def get_status():
    if client.is_open:
        current_level = client.read_input_registers(level, 1)[0]
        current_pressure = client.read_input_registers(pressure, 1)[0]
        valve_fill_status = client.read_holding_registers(valve_fill, 1)[0]
        valve_empty_status = client.read_holding_registers(valve_empty, 1)[0]
        return jsonify({
            "level": current_level,
            "pressure": current_pressure,
            "light": client.read_coils(light, 1)[0],
            "siren": client.read_coils(siren, 1)[0],
            "valve_fill": "Ouverte" if valve_fill_status > 0 else "Fermée",
            "valve_empty": "Ouverte" if valve_empty_status > 0 else "Fermée"
        })
    return jsonify({"status": "error", "message": "Erreur de connexion"})

if __name__ == '__main__':
    client.open()
    if client.is_open:
        print("OK")
        modbus_thread = threading.Thread(target=modbus_control, daemon=True)
        modbus_thread.start()
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("KO")