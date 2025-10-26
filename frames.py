from communication_library.frame import Frame
from communication_library import ids

oxidizer_intake_open = Frame(
    ids.BoardID.ROCKET,
    ids.PriorityID.LOW,
    ids.ActionID.SERVICE,
    ids.BoardID.SOFTWARE,
    ids.DeviceID.SERVO,
    1,
    ids.DataTypeID.INT16,
    ids.OperationID.SERVO.value.POSITION,
    (0,),
)
oxidizer_intake_close = Frame(
    ids.BoardID.ROCKET,
    ids.PriorityID.LOW,
    ids.ActionID.SERVICE,
    ids.BoardID.SOFTWARE,
    ids.DeviceID.SERVO,
    1,
    ids.DataTypeID.INT16,
    ids.OperationID.SERVO.value.POSITION,
    (100,),
)
fuel_intake_open = Frame(
    ids.BoardID.ROCKET,
    ids.PriorityID.LOW,
    ids.ActionID.SERVICE,
    ids.BoardID.SOFTWARE,
    ids.DeviceID.SERVO,
    0,
    ids.DataTypeID.INT16,
    ids.OperationID.SERVO.value.POSITION,
    (0,),
)
fuel_intake_close = Frame(
    ids.BoardID.ROCKET,
    ids.PriorityID.LOW,
    ids.ActionID.SERVICE,
    ids.BoardID.SOFTWARE,
    ids.DeviceID.SERVO,
    0,
    ids.DataTypeID.INT16,
    ids.OperationID.SERVO.value.POSITION,
    (100,),
)
oxidizer_heater_on = Frame(
    ids.BoardID.ROCKET,
    ids.PriorityID.LOW,
    ids.ActionID.SERVICE,
    ids.BoardID.SOFTWARE,
    ids.DeviceID.RELAY,
    0,
    ids.DataTypeID.NO_DATA,
    ids.OperationID.RELAY.value.OPEN,
)
fuel_main_open = Frame(
    ids.BoardID.ROCKET,
    ids.PriorityID.HIGH,
    ids.ActionID.SERVICE,
    ids.BoardID.SOFTWARE,
    ids.DeviceID.SERVO,
    2,
    ids.DataTypeID.INT16,
    ids.OperationID.SERVO.value.POSITION,
    (0,),
)
oxidizer_main_open = Frame(
    ids.BoardID.ROCKET,
    ids.PriorityID.HIGH,
    ids.ActionID.SERVICE,
    ids.BoardID.SOFTWARE,
    ids.DeviceID.SERVO,
    3,
    ids.DataTypeID.INT16,
    ids.OperationID.SERVO.value.POSITION,
    (0,),
)
igniter_on = Frame(
    ids.BoardID.ROCKET,
    ids.PriorityID.HIGH,
    ids.ActionID.SERVICE,
    ids.BoardID.SOFTWARE,
    ids.DeviceID.RELAY,
    1,
    ids.DataTypeID.NO_DATA,
    ids.OperationID.RELAY.value.OPEN,
)
parachute_deploy = Frame(
    ids.BoardID.ROCKET,
    ids.PriorityID.HIGH,
    ids.ActionID.SERVICE,
    ids.BoardID.SOFTWARE,
    ids.DeviceID.RELAY,
    2,
    ids.DataTypeID.NO_DATA,
    ids.OperationID.RELAY.value.OPEN,
)
oxidizer_level_frame = Frame(
    ids.BoardID.SOFTWARE,
    ids.PriorityID.LOW,
    ids.ActionID.FEED,
    ids.BoardID.ROCKET,
    ids.DeviceID.SENSOR,
    1,
    ids.DataTypeID.FLOAT,
    ids.OperationID.SENSOR.value.READ,
)
fuel_level_frame = Frame(
    ids.BoardID.SOFTWARE,
    ids.PriorityID.LOW,
    ids.ActionID.FEED,
    ids.BoardID.ROCKET,
    ids.DeviceID.SENSOR,
    0,
    ids.DataTypeID.FLOAT,
    ids.OperationID.SENSOR.value.READ,
)
oxidizer_pressure_frame = Frame(
    ids.BoardID.SOFTWARE,
    ids.PriorityID.LOW,
    ids.ActionID.FEED,
    ids.BoardID.ROCKET,
    ids.DeviceID.SENSOR,
    3,
    ids.DataTypeID.FLOAT,
    ids.OperationID.SENSOR.value.READ,
)
altitude_frame = Frame(
    ids.BoardID.SOFTWARE,
    ids.PriorityID.LOW,
    ids.ActionID.FEED,
    ids.BoardID.ROCKET,
    ids.DeviceID.SENSOR,
    2,
    ids.DataTypeID.FLOAT,
    ids.OperationID.SENSOR.value.READ,
)
