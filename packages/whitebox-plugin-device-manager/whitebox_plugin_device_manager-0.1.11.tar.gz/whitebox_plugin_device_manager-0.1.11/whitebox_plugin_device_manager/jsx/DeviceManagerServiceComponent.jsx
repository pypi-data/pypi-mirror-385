import { use, useEffect } from "react";
import useDevicesStore from "./stores/devices";

const DeviceManagerServiceComponent = () => {
  // Immediately on page load, fetch device list and populate the state store
  // with it, so that it's immediately available anywhere it's needed

  const fetchDevices = useDevicesStore((state) => state.fetchDevices);
  const updateDeviceConnectionStatus = useDevicesStore(
    (state) => state.updateDeviceConnectionStatus
  );

  useEffect(() => {
    fetchDevices();
  }, []);

  useEffect(() => {
    return Whitebox.sockets.addEventListener(
      "management",
      "message",
      (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "device.connection_status.update") {
          updateDeviceConnectionStatus(
            data.data.device_connection_id,
            data.data.connection_status
          );
        }
      }
    );
  }, []);

  return null;
};

export { DeviceManagerServiceComponent };
export default DeviceManagerServiceComponent;
