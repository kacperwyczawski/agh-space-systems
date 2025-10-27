from nicegui import ui, app

from frames import *

from communication_library.communication_manager import (
    CommunicationManager,
    TransportType,
)
from communication_library.tcp_transport import TcpSettings
from communication_library.frame import Frame
from communication_library.exceptions import (
    TransportTimeoutError,
    UnregisteredCallbackError,
)

cm = CommunicationManager()
cm.change_transport_type(TransportType.TCP)

oxidizer_level = 0.0
fuel_level = 0.0
oxidizer_pressure = 0.0
altitude = 0.0
angle = 0.0

oxidizer_sequence_complete = False
fuel_sequence_complete = False
ignition_sequence_started = False
apogee_reached = False

ui.label("Rocket Control Panel").classes('text-h4')

with ui.card().classes('w-full'):
    ox_level_label = ui.label(f'Oxidizer: {oxidizer_level:.1f}%')
    # Set show_value=False to hide the text on the progress bar
    ox_level_progress = ui.linear_progress(value=0.0, show_value=False, color='cyan')

    fuel_level_label = ui.label(f'Fuel: {fuel_level:.1f}%')
    # Set show_value=False to hide the text on the progress bar
    fuel_level_progress = ui.linear_progress(value=0.0, show_value=False, color='yellow')

    pressure_label = ui.label(f'Pressure: {oxidizer_pressure:.1f} bar')
    # Set show_value=False to hide the text on the progress bar
    pressure_progress = ui.linear_progress(value=0.0, show_value=False, color='red')

    altitude_label = ui.label(f'Altitude: {altitude:.1f} m')
    angle_label = ui.label(f'Angle: {angle:.1f}°')

def on_oxidizer_level_update(frame: Frame):
    global oxidizer_level
    oxidizer_level = float(frame.payload[0])

def on_fuel_level_update(frame: Frame):
    global fuel_level
    fuel_level = float(frame.payload[0])

def on_oxidizer_pressure_update(frame: Frame):
    global oxidizer_pressure
    oxidizer_pressure = float(frame.payload[0])

def on_altitude_update(frame: Frame):
    global altitude
    altitude = float(frame.payload[0])

def on_angle_update(frame: Frame):
    global angle
    angle = float(frame.payload[0])


def start_mission():
    global cm
    # Register the simple data-updating callbacks once
    cm.register_callback(on_oxidizer_level_update, oxidizer_level_frame)
    cm.register_callback(on_fuel_level_update, fuel_level_frame)
    cm.register_callback(on_oxidizer_pressure_update, oxidizer_pressure_frame)
    cm.register_callback(on_altitude_update, altitude_frame)
    cm.register_callback(on_angle_update, angle_frame)

    # Connect to the simulator and start the sequence
    cm.connect(TcpSettings("127.0.0.1", 3000))
    cm.push(oxidizer_intake_open)
    cm.send()
    
    # Start the main loop
    ui.timer(0.1, main_loop)
    ui.notify('Mission Started: Opening oxidizer intake valve.', color='positive')

# --- Main Application Loop ---
def main_loop():
    global oxidizer_sequence_complete, fuel_sequence_complete, ignition_sequence_started, apogee_reached

    # 1. Process any incoming messages, which will trigger the simple callbacks
    try:
        cm.receive()
    except (TransportTimeoutError, UnregisteredCallbackError):
        pass

    # 2. Update all UI elements with the latest data from the global variables
    ox_level_label.set_text(f'Oxidizer: {oxidizer_level:.1f}%')
    ox_level_progress.set_value(oxidizer_level / 100) # Progress bar value is 0.0 to 1.0

    fuel_level_label.set_text(f'Fuel: {fuel_level:.1f}%')
    fuel_level_progress.set_value(fuel_level / 100)

    pressure_label.set_text(f'Pressure: {oxidizer_pressure:.1f} bar')
    pressure_progress.set_value(oxidizer_pressure / 70)

    altitude_label.set_text(f'Altitude: {altitude:.1f} m')
    angle_label.set_text(f'Angle: {angle:.1f}°')

    # 3. Execute the state machine logic based on the current data
    # Step 1: Oxidizer Tanking
    if not oxidizer_sequence_complete and oxidizer_level == 100:
        oxidizer_sequence_complete = True
        ui.notify('Oxidizer tanking complete. Opening fuel intake.', color='info')
        cm.push(oxidizer_intake_close)
        cm.send()
        cm.push(fuel_intake_open)
        cm.send()

    # Step 2: Fuel Tanking
    if oxidizer_sequence_complete and not fuel_sequence_complete and fuel_level == 100:
        fuel_sequence_complete = True
        ui.notify('Fuel tanking complete. Activating oxidizer heater.', color='info')
        cm.push(fuel_intake_close)
        cm.send()
        cm.push(oxidizer_heater_on)
        cm.send()

    # Step 3: Ignition
    if fuel_sequence_complete and not ignition_sequence_started and oxidizer_pressure >= 55:
        ignition_sequence_started = True
        ui.notify(f'Optimal pressure ({oxidizer_pressure:.1f} bar) reached. LIFTOFF!', color='accent')
        cm.push(fuel_main_open)
        cm.send()
        cm.push(oxidizer_main_open)
        cm.send()
        cm.push(igniter_on)
        cm.send()

    # Step 4: Apogee Detection and Landing
    if ignition_sequence_started and not apogee_reached and angle >= 90:
        apogee_reached = True
        ui.notify(f'Apogee detected at angle {angle:.1f}°. Deploying parachute.', color='purple')
        cm.push(parachute_deploy)
        cm.send()

# --- Start Button ---
ui.button("Start Mission", on_click=start_mission)

ui.run()
