"""
This module contains functions to get the device info from an object. The device info
is used to create the device interface for proxy objects on other services.
"""

import functools
from contextlib import contextmanager
from typing import Any, Generator

import msgpack
from ophyd import Device, Kind, PositionerBase, Signal
from ophyd_devices import BECDeviceBase, ComputedSignal
from ophyd_devices.utils.bec_signals import BECMessageSignal

from bec_lib.bec_errors import DeviceConfigError
from bec_lib.device import DeviceBaseWithConfig
from bec_lib.logger import bec_logger
from bec_lib.numpy_encoder import numpy_encode
from bec_lib.signature_serializer import signature_to_dict

logger = bec_logger.logger


@contextmanager
def disable_lazy_wait_for_connection(
    device: PositionerBase | ComputedSignal | Signal | Device | BECDeviceBase,
) -> Generator[None, None, None]:
    """Context manager to disable lazy wait for connection for a device and its subdevices."""
    device_dict = get_lazy_wait_for_connection(device)
    try:
        for dev, _ in device_dict.values():  # Set all to False
            dev.lazy_wait_for_connection = False
        yield
    finally:
        for dev, initial_value in device_dict.values():
            dev.lazy_wait_for_connection = initial_value


def is_serializable(var: Any) -> bool:
    """
    Check if a variable is serializable

    Args:
        var (Any): variable to check

    Returns:
        bool: True if the variable is serializable, False otherwise
    """
    try:
        msgpack.dumps(var, default=numpy_encode)
        return True
    except (TypeError, OverflowError):
        return False


def get_custom_user_access_info(obj: Any, obj_interface: dict) -> dict:
    """
    Get the custom user access info

    Args:
        obj (Any): object to get the user access info from
        obj_interface (dict): object interface

    Returns:
        dict: updated object interface
    """
    # user_funcs = get_user_functions(obj)
    if hasattr(obj, "USER_ACCESS"):
        for var in [func for func in dir(obj) if func in obj.USER_ACCESS]:
            obj_member = getattr(obj, var)
            if not callable(obj_member):
                if is_serializable(obj_member):
                    obj_interface[var] = {"type": type(obj_member).__name__}
                elif get_device_base_class(obj_member) == "unknown":
                    obj_interface[var] = {
                        "info": get_custom_user_access_info(obj_member, {}),
                        "device_class": obj_member.__class__.__name__,
                    }
                else:
                    continue
            else:
                obj_interface[var] = {
                    "type": "func",
                    "doc": obj_member.__doc__,
                    "signature": signature_to_dict(obj_member),
                }
    return obj_interface


@functools.lru_cache(maxsize=2)
def get_protected_class_methods():
    """get protected methods of the DeviceBase class"""
    return [func for func in dir(DeviceBaseWithConfig) if not func.startswith("__")]


def get_device_base_class(obj: Any) -> str:
    """
    Get the base class of the object

    Args:
        obj (Any): object to get the base class from

    Returns:
        str: base class of the object
    """
    if isinstance(obj, PositionerBase):
        return "positioner"
    if isinstance(obj, ComputedSignal):
        return "computed_signal"
    if isinstance(obj, Signal):
        return "signal"
    if isinstance(obj, Device):
        return "device"
    if isinstance(obj, BECDeviceBase):
        return "device"

    return "unknown"


def get_device_info(
    obj: PositionerBase | ComputedSignal | Signal | Device | BECDeviceBase, connect=True
) -> dict:
    """
    Get the device info from the object

    Args:
        obj (PositionerBase | ComputedSignal | Signal | Device | BECDeviceBase): object to get the device info from
        device_info (dict): device info

    Returns:
        dict: updated device info
    """
    # Check if the object namespace is valid

    protected_names = get_protected_class_methods()
    user_access = get_custom_user_access_info(obj, {})
    if set(user_access.keys()) & set(protected_names):
        raise DeviceConfigError(
            f"User access method name {set(user_access.keys()) & set(protected_names)} is protected and cannot be used. Please rename the method."
        )
    # Collect signals and their metadata
    signals = {}  # []

    if hasattr(obj, "component_names") and connect:
        signal_names = []
        walk = obj.walk_components()
        for _ancestor, component_name, comp in walk:
            if get_device_base_class(getattr(obj, component_name)) == "signal":

                if component_name in protected_names:
                    raise DeviceConfigError(
                        f"Signal name {component_name} is protected and cannot be used. Please rename the signal."
                    )
                signal_obj = getattr(obj, component_name)
                doc = (
                    comp.doc
                    if isinstance(comp.doc, str)
                    and not comp.doc.startswith("Component attribute\n::")
                    else ""
                )
                if isinstance(signal_obj, BECMessageSignal):
                    info = signal_obj.describe().get(signal_obj.name, {}).get("signal_info", {})
                    if not info:
                        continue
                    for signal_name, kind in info.get("signals", []):
                        if len(info.get("signals")) == 1:
                            obj_name = signal_obj.name
                            comp_name = component_name
                        else:
                            obj_name = "_".join([signal_obj.name, signal_name])
                            comp_name = ".".join([component_name, signal_name])
                        signals.update(
                            {
                                comp_name: {
                                    "component_name": component_name,
                                    "signal_class": signal_obj.__class__.__name__,
                                    "obj_name": obj_name,
                                    "kind_int": kind,
                                    "kind_str": Kind(kind).name,
                                    "doc": doc,
                                    "describe": signal_obj.describe().get(signal_obj.name, {}),
                                    # pylint: disable=protected-access
                                    "metadata": signal_obj._metadata,
                                }
                            }
                        )
                else:
                    obj_name = signal_obj.name
                    signals.update(
                        {
                            component_name: {
                                "component_name": component_name,
                                "signal_class": signal_obj.__class__.__name__,
                                "obj_name": obj_name,
                                "kind_int": signal_obj.kind.value,
                                "kind_str": signal_obj.kind.name,
                                "doc": doc,
                                "describe": signal_obj.describe().get(signal_obj.name, {}),
                                # pylint: disable=protected-access
                                "metadata": signal_obj._metadata,
                            }
                        }
                    )
                signal_names.append(obj_name)
        # Read attrs are only available if the device is connected
        unique_signal_names = set(signal_names)
        if len(unique_signal_names) < len(signal_names):
            raise DeviceConfigError(
                f"Signal names of {obj.name} must be unique, found duplicates. All signal names: {signal_names}. \n Unique signal names: {unique_signal_names}."
            )
    sub_devices = []

    if hasattr(obj, "walk_subdevices") and connect:
        for _, dev in obj.walk_subdevices():
            sub_devices.append(get_device_info(dev, connect=connect))
    if obj.name in protected_names or getattr(obj, "dotted_name", None) in protected_names:
        raise DeviceConfigError(
            f"Device name {obj.name} is protected and cannot be used. Please rename the device."
        )
    if isinstance(obj, Signal):
        # needed because ophyd signals have empty hints
        hints = {"fields": [obj.name]}
    elif connect:  # only works if PVs are connected
        with disable_lazy_wait_for_connection(obj):
            hints = obj.hints
    else:
        hints = {}

    if connect:
        describe = obj.describe()
        describe_configuration = obj.describe_configuration() | {"egu": getattr(obj, "egu", None)}
    else:
        describe = {}
        describe_configuration = {}
    return {
        "device_name": obj.name,
        "device_info": {
            "device_attr_name": getattr(obj, "attr_name", ""),
            "device_dotted_name": getattr(obj, "dotted_name", ""),
            "device_base_class": get_device_base_class(obj),
            "device_class": obj.__class__.__name__,
            "read_access": getattr(obj, "read_access", None),
            "write_access": getattr(obj, "write_access", None),
            "signals": signals,
            "hints": hints,
            "describe": describe,
            "describe_configuration": describe_configuration,
            "sub_devices": sub_devices,
            "custom_user_access": user_access,
        },
    }


def get_lazy_wait_for_connection(
    device: PositionerBase | ComputedSignal | Signal | Device | BECDeviceBase,
    output: dict | None = None,
) -> dict[str, tuple[PositionerBase | ComputedSignal | Signal | Device | BECDeviceBase, bool]]:
    """
    Method to retrieve the lazy_wait_for_connection attribute of a device and its subdevices. It returns
    a dictionary with device names (device & subdevices) as keys and tuples of (device, lazy_wait_for_connection)
    as values. If the device does not have the lazy_wait_for_connection attribute, it will log a warning.

    Args:
        device (PositionerBase | ComputedSignal | Signal | Device | BECDeviceBase): Device to check
        output (dict | None): Output dictionary to store the results. If None, a new dictionary will be created.

    Returns:
        dict[str, tuple[PositionerBase | ComputedSignal | Signal | Device | BECDeviceBase, bool]]: Dictionary with device names as keys and tuples of (device, lazy_wait_for_connection) as values.
    """
    if output is None:
        output = {}
    if isinstance(device, BECDeviceBase):
        return output
    if hasattr(device, "lazy_wait_for_connection"):
        output[device.name] = (device, device.lazy_wait_for_connection)
    else:
        logger.warning(f"Device {device.name} does not have lazy_wait_for_connection attribute")

    for attr, cpt in device._sig_attrs.items():  # pylint: disable=protected-access
        if issubclass(cpt.cls, Device):
            output.update(get_lazy_wait_for_connection(getattr(device, attr), output=output))
    return output
