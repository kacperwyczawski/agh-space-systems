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

oxidizer_sequence_complete = False
fuel_sequence_complete = False
ignition_sequence_started = False
apogee_reached = False

def rocket():
    global cm, oxidizer_sequence_complete, fuel_sequence_complete, ignition_sequence_started, apogee_reached

    def on_oxidizer_level(frame: Frame):
        global oxidizer_sequence_complete
        if oxidizer_sequence_complete or float(frame.payload[0]) != 100:
            return
        oxidizer_sequence_complete = True
        # console.log("[green]Success:[/green] Oxidizer tanking complete.")
        # console.log("Opening fuel intake valve")
        cm.push(oxidizer_intake_close)
        cm.send()
        cm.push(fuel_intake_open)
        cm.send()

    cm.register_callback(on_oxidizer_level, oxidizer_level_frame)

    def on_fuel_level(frame: Frame):
        global fuel_sequence_complete
        if fuel_sequence_complete or float(frame.payload[0]) != 100:
            return
        fuel_sequence_complete = True
        # console.log("[green]Success:[/green] Fuel tanking complete.")
        # console.log("Activating oxidizer heater")
        cm.push(fuel_intake_close)
        cm.send()
        cm.push(oxidizer_heater_on)
        cm.send()

    cm.register_callback(on_fuel_level, fuel_level_frame)

    def on_oxidizer_pressure(frame: Frame):
        global ignition_sequence_started
        pressure = frame.payload[0]
        if ignition_sequence_started or float(pressure) < 55:
            return
        ignition_sequence_started = True
        # console.log(
            # f"[bold yellow]Optimal pressure ({float(pressure):.1f} bar) reached. Commencing ignition sequence![/bold yellow]"
        # )
        cm.push(fuel_main_open)
        cm.send()
        cm.push(oxidizer_main_open)
        cm.send()
        cm.push(igniter_on)
        cm.send()
        # console.log("[bold red]LIFTOFF![/bold red]")

    cm.register_callback(on_oxidizer_pressure, oxidizer_pressure_frame)

    def on_angle(frame: Frame):
        global ignition_sequence_started, apogee_reached

        if apogee_reached:
            return

        if (
            int(frame.payload[0]) == 90
        ):
            apogee_reached = True
            # console.log(
                # f"[bold magenta]Apogee detected at {last_altitude:.1f}m.[/bold magenta]"
            # )
            # console.log("Deploying parachute for safe landing")
            cm.push(parachute_deploy)
            cm.send()

    cm.register_callback(on_angle, angle_frame)
    cm.connect(TcpSettings("127.0.0.1", 3000))
    # console.log("[bold]Rocket Control Script Initialized[/bold]")
    # console.log("Opening oxidizer intake valve")
    cm.push(oxidizer_intake_open)
    cm.send()
    def receive():
        try:
            frame = cm.receive()
        except TransportTimeoutError:
            pass
        except UnregisteredCallbackError:
            pass
    ui.timer(0.1, receive)

ui.label("test")
ui.button("rocket", on_click=rocket)
ui.run()
