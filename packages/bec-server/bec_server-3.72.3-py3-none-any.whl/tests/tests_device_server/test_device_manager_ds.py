import copy
import time
from unittest import mock

import numpy as np
import pytest

from bec_lib import messages
from bec_lib.endpoints import MessageEndpoints
from bec_server.device_server.devices.devicemanager import DeviceConfigError, DeviceManagerDS

# pylint: disable=missing-function-docstring
# pylint: disable=protected-access


@pytest.fixture
def dm_with_devices_and_status(dm_with_devices):
    """
    Fixture that adds the scan_info message to the device manager
    """
    device_manager = dm_with_devices
    with mock.patch.object(
        device_manager.scan_info, "msg", new_callable=mock.PropertyMock
    ) as mock_scan_info_msg:
        mock_scan_info_msg.return_value = messages.ScanStatusMessage(
            scan_id="12345", status="open", info={"num_points": 10, "RID": "RID123"}
        )
        yield device_manager


class ControllerMock:
    def __init__(self, parent) -> None:
        self.parent = parent

    def on(self):
        self.parent._connected = True

    def off(self):
        self.parent._connected = False


class DeviceMock:
    def __init__(self) -> None:
        self._connected = False
        self.name = "name"

    @property
    def connected(self):
        return self._connected


class DeviceControllerMock(DeviceMock):
    def __init__(self) -> None:
        super().__init__()
        self.controller = ControllerMock(self)


class EpicsDeviceMock(DeviceMock):
    def wait_for_connection(self, timeout):
        self._connected = True


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
def test_device_init(dm_with_devices):
    device_manager = dm_with_devices
    for dev in device_manager.devices.values():
        if not dev.enabled:
            continue
        assert dev.initialized is True


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
def test_device_proxy_init(dm_with_devices):
    device_manager = dm_with_devices
    assert "sim_proxy_test" in device_manager.devices.keys()
    assert "proxy_cam_test" in device_manager.devices.keys()
    assert "image" in device_manager.devices["proxy_cam_test"].obj.registered_proxies.values()
    assert (
        "sim_proxy_test" in device_manager.devices["proxy_cam_test"].obj.registered_proxies.keys()
    )


@pytest.mark.parametrize(
    "obj,raises_error",
    [(DeviceMock(), True), (DeviceControllerMock(), False), (EpicsDeviceMock(), False)],
)
@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
def test_connect_device(dm_with_devices, obj, raises_error):
    device_manager = dm_with_devices
    if raises_error:
        with pytest.raises(ConnectionError):
            device_manager.connect_device(obj)
        return
    device_manager.connect_device(obj)


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
def test_disable_unreachable_devices(device_manager, session_from_test_config):
    def get_config_from_mock():
        device_manager._session = copy.deepcopy(session_from_test_config)
        device_manager._load_session()

    def mocked_failed_connection(obj):
        if obj.name == "samx":
            raise ConnectionError

    config_reply = messages.RequestResponseMessage(accepted=True, message="")

    with mock.patch.object(device_manager, "connect_device", wraps=mocked_failed_connection):
        with mock.patch.object(device_manager, "_get_config", get_config_from_mock):
            with mock.patch.object(
                device_manager.config_helper, "wait_for_config_reply", return_value=config_reply
            ):
                with mock.patch.object(device_manager.config_helper, "wait_for_service_response"):
                    device_manager.initialize("")
                    assert device_manager.config_update_handler is not None
                    assert device_manager.devices.samx.enabled is False
                    msg = messages.DeviceConfigMessage(
                        action="update", config={"samx": {"enabled": False}}
                    )


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
def test_flyer_event_callback(dm_with_devices, connected_connector):
    device_manager = dm_with_devices
    samx = device_manager.devices.samx
    samx.metadata = {"scan_id": "12345"}
    # Use here fake redis connector to avoid complications with PipelineMock
    device_manager.connector = connected_connector
    device_manager._obj_flyer_callback(
        obj=samx.obj,
        value={"data": {"idata": np.random.rand(20), "edata": np.random.rand(20)}},
        metadata={"scan_id": "test_scan_id"},
    )
    msg = connected_connector.get(MessageEndpoints.device_read("samx"))
    assert "signals" in msg.content
    assert "idata" in msg.content["signals"]
    assert "edata" in msg.content["signals"]
    msg = connected_connector.get(MessageEndpoints.device_status("samx"))
    assert msg.metadata["scan_id"] == "12345"
    assert msg.content["device"] == "samx"
    assert msg.content["status"] == 20


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
def test_obj_callback_progress(dm_with_devices):
    device_manager = dm_with_devices
    samx = device_manager.devices.samx
    samx.metadata = {"scan_id": "12345"}

    with mock.patch.object(device_manager, "connector") as mock_connector:
        device_manager._obj_callback_progress(obj=samx.obj, value=1, max_value=2, done=False)
        mock_connector.set_and_publish.assert_called_once_with(
            MessageEndpoints.device_progress("samx"),
            messages.ProgressMessage(
                value=1, max_value=2, done=False, metadata={"scan_id": "12345"}
            ),
        )


@pytest.mark.parametrize(
    "value", [np.empty(shape=(10, 10)), np.empty(shape=(100, 100)), np.empty(shape=(1000, 1000))]
)
@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
def test_obj_device_monitor_2d_callback(dm_with_devices, value):
    device_manager = dm_with_devices
    eiger = device_manager.devices.eiger
    eiger.metadata = {"scan_id": "12345"}
    value_size = len(value.tobytes()) / 1e6  # MB
    max_size = 1000
    timestamp = time.time()
    with mock.patch.object(device_manager, "connector") as mock_connector:
        device_manager._obj_callback_device_monitor_2d(
            obj=eiger.obj, value=value, timestamp=timestamp
        )
        stream_msg = {
            "data": messages.DeviceMonitor2DMessage(
                device=eiger.name, data=value, metadata={"scan_id": "12345"}, timestamp=timestamp
            )
        }

        assert mock_connector.xadd.call_count == 1
        assert mock_connector.xadd.call_args == mock.call(
            MessageEndpoints.device_monitor_2d(eiger.name),
            stream_msg,
            max_size=min(100, int(max_size // value_size)),
        )


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
def test_device_manager_ds_reset_config(dm_with_devices):
    with mock.patch.object(dm_with_devices, "connector") as mock_connector:
        device_manager = dm_with_devices
        config = device_manager._session["devices"]
        device_manager._reset_config()

        config_msg = messages.AvailableResourceMessage(
            resource=config, metadata=mock_connector.lpush.call_args[0][1].metadata
        )
        mock_connector.lpush.assert_called_once_with(
            MessageEndpoints.device_config_history(), config_msg, max_size=50
        )


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
def test_obj_callback_file_event(dm_with_devices, connected_connector):
    device_manager = dm_with_devices
    eiger = device_manager.devices.eiger
    eiger.metadata = {"scan_id": "12345"}
    # Use here fake redis connector, pipe is used and checks pydantic models
    device_manager.connector = connected_connector
    device_manager._obj_callback_file_event(
        obj=eiger.obj,
        file_path="test_file_path",
        done=True,
        successful=True,
        hinted_h5_entries={"my_entry": "entry/data/data"},
        metadata={"user_info": "my_info"},
    )
    msg = connected_connector.get(MessageEndpoints.file_event(name="eiger"))
    msg2 = connected_connector.get(MessageEndpoints.public_file(scan_id="12345", name="eiger"))
    assert msg == msg2
    assert msg.content["file_path"] == "test_file_path"
    assert msg.content["done"] is True
    assert msg.content["successful"] is True
    assert msg.content["hinted_h5_entries"] == {"my_entry": "entry/data/data"}
    assert msg.content["file_type"] == "h5"
    assert msg.metadata == {"scan_id": "12345", "user_info": "my_info"}
    assert msg.content["is_master_file"] is False


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
def test_subscribe_to_device_events(dm_with_devices):
    opaas_obj = mock.MagicMock()
    opaas_obj.enabled = False
    obj = mock.MagicMock()
    # Test 2 event types together
    obj.event_types = ("file_event", "device_monitor_1d")
    with mock.patch.object(dm_with_devices, "_obj_callback_file_event") as mock_callback_file_event:
        with mock.patch.object(
            dm_with_devices, "_obj_callback_device_monitor_1d"
        ) as mock_callback_device_monitor_1d:
            dm_with_devices._subscribe_to_device_events(obj=obj, opaas_obj=opaas_obj)
            assert obj.subscribe.call_count == 0
            dm_with_devices._subscribe_to_bec_device_events(obj=obj)
            assert obj.subscribe.call_count == 2
            assert (
                mock.call(mock_callback_file_event, event_type="file_event", run=False)
                in obj.subscribe.call_args_list
            )
            assert (
                mock.call(
                    mock_callback_device_monitor_1d, event_type="device_monitor_1d", run=False
                )
                in obj.subscribe.call_args_list
            )

    # Test all event types
    for ii, event_type in enumerate(
        [
            "readback",
            "value",
            "device_monitor_1d",
            "device_monitor_2d",
            "file_event",
            "done_moving",
            "progress",
        ]
    ):
        obj.event_types = (event_type,)
        callback_name = (
            f"_obj_callback_{event_type}" if event_type != "value" else "_obj_callback_readback"
        )
        with mock.patch.object(dm_with_devices, callback_name) as mock_callback:
            dm_with_devices._subscribe_to_device_events(obj=obj, opaas_obj=opaas_obj)
            dm_with_devices._subscribe_to_bec_device_events(obj=obj)
            assert obj.subscribe.call_args == mock.call(
                mock_callback, event_type=event_type, run=False
            )


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
@pytest.mark.parametrize(
    "value",
    [
        None,
        messages.DevicePreviewMessage(
            data=np.random.rand(10, 10), device="bec_signals_device", signal="preview"
        ),
        "some string",
    ],
)
def test_device_manager_ds_obj_callback_preview(dm_with_devices, value):
    device_manager = dm_with_devices
    device = dm_with_devices.devices.bec_signals_device.obj
    with mock.patch.object(device_manager.connector, "xadd") as mock_xadd:
        device_manager._obj_callback_bec_message_signal(obj=device.preview, value=value)

        if not isinstance(value, messages.DevicePreviewMessage):
            mock_xadd.assert_not_called()
        else:
            rot90 = device.preview.num_rotation_90
            transpose = device.preview.transpose
            if rot90:
                value.data = np.rot90(value.data, k=rot90, axes=(0, 1))
            if transpose:
                value.data = np.transpose(value.data)
            mock_xadd.assert_called_once_with(
                MessageEndpoints.device_preview(device="bec_signals_device", signal="preview"),
                {"data": value},
                max_size=100,  # Assuming a default max size
            )


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
@pytest.mark.parametrize(
    "value",
    [
        None,
        messages.FileMessage(
            file_path="some/path/to/file.h5",
            done=True,
            successful=True,
            hinted_h5_entries={"my_entry": "entry/data/data"},
            is_master_file=False,
            metadata={"user_info": "my_info"},
        ),
        "some string",
    ],
)
def test_device_manager_ds_obj_callback_file_event_signal(dm_with_devices_and_status, value):
    device_manager = dm_with_devices_and_status
    device = device_manager.devices.bec_signals_device.obj
    with mock.patch.object(device_manager.connector, "set_and_publish") as mock_set_and_publish:
        device_manager._obj_callback_bec_message_signal(obj=device.file_event, value=value)

        if not isinstance(value, messages.FileMessage):
            mock_set_and_publish.assert_not_called()
        else:
            assert mock_set_and_publish.call_count == 2


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
@pytest.mark.parametrize(
    "value", [None, messages.ProgressMessage(value=1, max_value=2, done=False), "some string"]
)
def test_device_manager_ds_obj_callback_progress_signal(dm_with_devices_and_status, value):
    device_manager = dm_with_devices_and_status
    device = device_manager.devices.bec_signals_device.obj
    with mock.patch.object(device_manager.connector, "set_and_publish") as mock_set_and_publish:
        device_manager._obj_callback_bec_message_signal(obj=device.progress, value=value)

        if not isinstance(value, messages.ProgressMessage):
            mock_set_and_publish.assert_not_called()
        else:
            mock_set_and_publish.assert_called_once()


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
def test_device_manager_ds_obj_callback_progress_signal_disabled_device(dm_with_devices):
    device_manager = dm_with_devices
    device = dm_with_devices.devices.bec_signals_device.obj
    with mock.patch.object(
        type(device.progress), "connected", new_callable=mock.PropertyMock
    ) as mock_connected:
        mock_connected.return_value = False
        with mock.patch.object(device_manager._bec_message_handler, "emit") as mock_emit:
            device_manager._obj_callback_bec_message_signal(
                obj=device.progress,
                value=messages.ProgressMessage(
                    value=1, max_value=2, done=False, metadata={"scan_id": "12345"}
                ),
            )
            mock_emit.assert_not_called()


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
@pytest.mark.parametrize(
    "value",
    [
        None,
        messages.DeviceMessage(
            signals={"async_signal": {"value": np.random.rand(10), "timestamp": time.time()}}
        ),
        "some string",
    ],
)
def test_device_manager_ds_obj_callback_async_signal(dm_with_devices_and_status, value):
    device_manager = dm_with_devices_and_status
    device = device_manager.devices.bec_signals_device.obj
    with mock.patch.object(device_manager.connector, "xadd") as mock_xadd:
        device_manager._obj_callback_bec_message_signal(obj=device.async_signal, value=value)

        if not isinstance(value, messages.DeviceMessage):
            mock_xadd.assert_not_called()
        else:
            mock_xadd.assert_called_once()


@pytest.mark.parametrize("device_manager_class", [DeviceManagerDS])
@pytest.mark.parametrize("metadata", [{}, {"scan_id": 12345}])  # Invalid scan_id type
def test_device_manager_ds_obj_callback_async_signal_incomplete_info(dm_with_devices, metadata):
    device_manager = dm_with_devices
    device = dm_with_devices.devices.bec_signals_device.obj
    dm_with_devices.devices.bec_signals_device.metadata = metadata

    msg = messages.DeviceMessage(
        signals={"async_signal": {"value": np.random.rand(10), "timestamp": time.time()}}
    )
    with mock.patch.object(device_manager.connector, "xadd") as mock_xadd:
        device_manager._obj_callback_bec_message_signal(obj=device.async_signal, value=msg)

        mock_xadd.assert_not_called()
