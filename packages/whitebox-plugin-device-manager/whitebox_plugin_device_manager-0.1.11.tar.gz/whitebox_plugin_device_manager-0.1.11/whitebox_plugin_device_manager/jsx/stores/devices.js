import { create } from "zustand";

const { api } = Whitebox;

const devicesStore = (set) => ({
  fetchState: "initial",
  devices: null,

  fetchDevices: async () => {
    let data;

    const url = api.getPluginProvidedPath(
      "device.device-connection-management"
    );

    try {
      const response = await api.client.get(url);
      data = await response.data;
    } catch {
      set({ fetchState: "error" });
      return false;
    }

    set({
      devices: data,
      fetchState: "loaded",
    });
    return true;
  },

  toggleDeviceConnection: async (deviceId, isConnected) => {
    const url = api.getPluginProvidedPath(
      "device.device-connection-management"
    );

    try {
      const usePath = isConnected ? "wifi/disconnect" : "wifi/connect";
      const fullUrl = `${url}${usePath}?device_id=${deviceId}`;

      const response = await api.client.get(fullUrl);
      const data = await response.data;
      console.log("Toggle response data:", data);
    } catch (e) {
      console.error("Error toggling device connection:", e);
    }

    // Reflect the change in local state for immediate UI feedback
    set((state) => {
      const updatedDevices = state.devices.map((device) => {
        if (device.id === deviceId) {
          return {
            ...device,
            connection_status: isConnected ? "disconnected" : "connected",
          };
        }
        return device;
      });
      return { devices: updatedDevices };
    });
  },

  updateDeviceConnectionStatus: (deviceId, newStatus) => {
    set((state) => {
      if (!state.devices) {
        return state;
      }

      const updatedDevices = state.devices.map((device) => {
        if (device.id === deviceId) {
          return {
            ...device,
            connection_status: newStatus,
          };
        }
        return device;
      });

      return { devices: updatedDevices };
    });
  },
});

const useDevicesStore = create(devicesStore);

export default useDevicesStore;
