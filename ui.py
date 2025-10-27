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

class Rocket:
    def __init__(self, cm: CommunicationManager):
        self.cm = cm
        self.oxidizer_level = 0.0
        self.fuel_level = 0.0
        self.oxidizer_pressure = 0.0
        self.altitude = 0.0
        self.angle = 0.0
        self.servo_states = {0: 100, 1: 100, 2: 100, 3: 100}
        self.relay_states = {0: 0, 1: 0, 2: 0}
        self.oxidizer_sequence_complete = False
        self.fuel_sequence_complete = False
        self.ignition_sequence_started = False
        self.apogee_reached = False

    def _update_oxidizer_level(self, frame: Frame): self.oxidizer_level = float(frame.payload[0])
    def _update_fuel_level(self, frame: Frame): self.fuel_level = float(frame.payload[0])
    def _update_oxidizer_pressure(self, frame: Frame): self.oxidizer_pressure = float(frame.payload[0])
    def _update_altitude(self, frame: Frame): self.altitude = float(frame.payload[0])
    def _update_angle(self, frame: Frame): self.angle = float(frame.payload[0])
    def _update_servo_state(self, frame: Frame): self.servo_states[frame.device_id] = int(frame.payload[0])

    def register_callbacks(self):
        self.cm.register_callback(self._update_oxidizer_level, oxidizer_level_frame)
        self.cm.register_callback(self._update_fuel_level, fuel_level_frame)
        self.cm.register_callback(self._update_oxidizer_pressure, oxidizer_pressure_frame)
        self.cm.register_callback(self._update_altitude, altitude_frame)
        self.cm.register_callback(self._update_angle, angle_frame)
        self.cm.register_callback(self._update_servo_state, servo_fuel_intake_frame)
        self.cm.register_callback(self._update_servo_state, servo_oxidizer_intake_frame)
        self.cm.register_callback(self._update_servo_state, servo_fuel_main_frame)
        self.cm.register_callback(self._update_servo_state, servo_oxidizer_main_frame)

    def update_mission_logic(self):
        if not self.oxidizer_sequence_complete and self.oxidizer_level == 100:
            self.oxidizer_sequence_complete = True
            ui.notify('Oxidizer tanking complete. Opening fuel intake.', color='info')
            self.cm.push(oxidizer_intake_close); self.cm.send()
            self.cm.push(fuel_intake_open); self.cm.send()

        if self.oxidizer_sequence_complete and not self.fuel_sequence_complete and self.fuel_level == 100:
            self.fuel_sequence_complete = True
            ui.notify('Fuel tanking complete. Activating oxidizer heater.', color='info')
            self.cm.push(fuel_intake_close); self.cm.send()
            self.relay_states[0] = 1
            self.cm.push(oxidizer_heater_on); self.cm.send()

        if self.fuel_sequence_complete and not self.ignition_sequence_started and self.oxidizer_pressure >= 55:
            self.ignition_sequence_started = True
            ui.notify(f'Optimal pressure ({self.oxidizer_pressure:.1f} bar) reached. LIFTOFF!', color='accent')
            self.cm.push(fuel_main_open); self.cm.send()
            self.cm.push(oxidizer_main_open); self.cm.send()
            self.relay_states[1] = 1
            self.cm.push(igniter_on); self.cm.send()

        if self.ignition_sequence_started and not self.apogee_reached and self.angle >= 90:
            self.apogee_reached = True
            ui.notify(f'Apogee detected at angle {self.angle:.1f}°. Deploying parachute.', color='purple')
            self.relay_states[2] = 1
            self.cm.push(parachute_deploy); self.cm.send()

class StatusLabel(ui.label):
    def __init__(self, text: str):
        super().__init__(text)
        self._apply_styling()

    def _handle_text_change(self, text: str) -> None:
        super()._handle_text_change(text)
        self._apply_styling()

    def _apply_styling(self) -> None:
        status = self.text.split(': ')[1]
        status_classes = {
            'Open': 'bg-positive text-white', 'Closed': 'bg-negative text-white',
            'On': 'bg-positive text-white', 'Off': 'bg-negative text-white',
            'Deployed': 'bg-accent text-white', 'Stowed': 'bg-gray-500 text-white',
        }
        base_classes = 'p-2 rounded text-sm text-center flex-grow w-0'
        self.classes(replace=f'{base_classes} {status_classes.get(status, "bg-gray-300")}')

rocket = Rocket(CommunicationManager())
rocket.cm.change_transport_type(TransportType.TCP)

ui.label("Rocket Control Panel").classes('text-h4 text-center w-full')

with ui.card().classes('w-full'):
    ui.label().bind_text_from(rocket, 'oxidizer_level', backward=lambda v: f'Oxidizer: {v:.1f}%')
    ui.linear_progress(show_value=False, color='cyan').bind_value_from(rocket, 'oxidizer_level', backward=lambda v: v / 100)
    
    ui.label().bind_text_from(rocket, 'fuel_level', backward=lambda v: f'Fuel: {v:.1f}%')
    ui.linear_progress(show_value=False, color='orange').bind_value_from(rocket, 'fuel_level', backward=lambda v: v / 100)
    
    ui.label().bind_text_from(rocket, 'oxidizer_pressure', backward=lambda v: f'Pressure: {v:.1f} bar')
    ui.linear_progress(show_value=False, color='red').bind_value_from(rocket, 'oxidizer_pressure', backward=lambda v: v / 70)
    
    ui.label().bind_text_from(rocket, 'altitude', backward=lambda v: f'Altitude: {v:.1f} m')
    ui.label().bind_text_from(rocket, 'angle', backward=lambda v: f'Angle: {v:.1f}°')

with ui.row().classes('w-full items-center mt-2 gap-2'):
    device_labels = {
        'fuel_intake': StatusLabel('Fuel Intake: Closed'), 'oxidizer_intake': StatusLabel('Oxidizer Intake: Closed'),
        'fuel_main': StatusLabel('Fuel Main: Closed'), 'oxidizer_main': StatusLabel('Oxidizer Main: Closed'),
        'oxidizer_heater': StatusLabel('Heater: Off'), 'igniter': StatusLabel('Igniter: Off'),
        'parachute': StatusLabel('Parachute: Stowed'),
    }

def main_loop():
    try: rocket.cm.receive()
    except (TransportTimeoutError, UnregisteredCallbackError): pass
    
    rocket.update_mission_logic()

    def get_servo_status(pos): return "Closed" if pos == 100 else "Open"
    def get_relay_status(state, on="On", off="Off"): return on if state == 1 else off

    device_labels['fuel_intake'].set_text(f'Fuel Intake: {get_servo_status(rocket.servo_states[0])}')
    device_labels['oxidizer_intake'].set_text(f'Oxidizer Intake: {get_servo_status(rocket.servo_states[1])}')
    device_labels['fuel_main'].set_text(f'Fuel Main: {get_servo_status(rocket.servo_states[2])}')
    device_labels['oxidizer_main'].set_text(f'Oxidizer Main: {get_servo_status(rocket.servo_states[3])}')
    device_labels['oxidizer_heater'].set_text(f'Heater: {get_relay_status(rocket.relay_states[0])}')
    device_labels['igniter'].set_text(f'Igniter: {get_relay_status(rocket.relay_states[1])}')
    device_labels['parachute'].set_text(f'Parachute: {get_relay_status(rocket.relay_states[2], on="Deployed", off="Stowed")}')

def start_mission():
    start_button.disable()
    rocket.register_callbacks()
    rocket.cm.connect(TcpSettings("127.0.0.1", 3000))
    rocket.cm.push(oxidizer_intake_open)
    rocket.cm.send()
    ui.timer(0.1, main_loop)
    ui.notify('Mission Started: Opening oxidizer intake valve.', color='positive')

with ui.row().classes('w-full justify-center mt-4'):
    start_button = ui.button('Start Mission', on_click=start_mission, color='positive', icon='rocket_launch')

ui.run()
