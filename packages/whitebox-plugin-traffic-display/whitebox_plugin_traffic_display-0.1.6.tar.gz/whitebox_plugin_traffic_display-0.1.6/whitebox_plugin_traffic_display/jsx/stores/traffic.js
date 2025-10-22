import { create } from "zustand";

const { api } = Whitebox;

const getTrafficLabel = (traffic) => {
  // Create label with callsign (Tail or Reg) and altitude
  const callsign = traffic.Tail || traffic.Reg || traffic.Icao_addr;
  const altitude = traffic.Alt ? traffic.Alt : "N/A";
  const speed = traffic.Speed ? traffic.Speed : "N/A";
  return `${callsign}\n${altitude}ft\n${speed}kt`;
};

const trafficStore = (set, get) => ({
  staleTrafficTimeout: 1000 * 10, // Clear stale traffic after 10 seconds
  staleTrafficRemovalInterval: 1000 * 1, // Check for stale traffic every 1 seconds
  trafficData: [],
  trafficMarkers: {},

  addTrafficMarker: (id, data) => {
    set((state) => ({
      trafficMarkers: {
        ...state.trafficMarkers,
        [id]: data,
      },
    }));
  },

  updateTrafficMarker: (id, data) => {
    set((state) => {
      if (!state.trafficMarkers[id]) return state;
      return {
        trafficMarkers: {
          ...state.trafficMarkers,
          [id]: {
            ...state.trafficMarkers[id],
            ...data,
          },
        },
      };
    });
  },

  removeTrafficMarker: (id) => {
    set((state) => {
      const newTrafficMarkers = { ...state.trafficMarkers };
      delete newTrafficMarkers[id];
      return { trafficMarkers: newTrafficMarkers };
    });
  },

  addTrafficData: (newData) => {
    set((state) => {
      const trafficData = [...state.trafficData];
      const existingTraffic = trafficData.find(
        (traffic) => traffic.Icao_addr === newData.Icao_addr
      );

      if (existingTraffic) {
        Object.assign(existingTraffic, { ...newData, lastUpdate: Date.now() });
      } else {
        trafficData.push({ ...newData, lastUpdate: Date.now() });
      }

      return { trafficData };
    });
  },

  removeStaleTrafficData: () => {
    set((state) => {
      const currentTime = Date.now();
      const trafficData = state.trafficData.filter(
        (traffic) =>
          currentTime - traffic.lastUpdate <= state.staleTrafficTimeout
      );

      return { trafficData };
    });
  },

  renderTrafficData: () => {
    const { trafficData, trafficMarkers } = get();
    const trafficIdsOnMap = new Set(Object.keys(trafficMarkers));

    const currentTrafficIds = new Set(
      trafficData.map((traffic) => traffic.Icao_addr.toString())
    );

    // Remove markers that are no longer in traffic state
    for (const renderedId of trafficIdsOnMap) {
      if (!currentTrafficIds.has(renderedId)) {
        get().removeTrafficMarker(renderedId);
      }
    }

    // Add or update markers for current traffic
    for (const traffic of trafficData) {
      const trafficId = traffic.Icao_addr.toString();
      const label = getTrafficLabel(traffic);
      const iconURL =
        api.getStaticUrl() + "whitebox_plugin_traffic_display/assets/plane.svg";

      if (!trafficIdsOnMap.has(trafficId)) {
        get().addTrafficMarker(trafficId, {
          lat: traffic.Lat,
          lon: traffic.Lng,
          bearing: traffic.Track,
          iconUrl: iconURL,
          label: label,
        });
      } else {
        get().updateTrafficMarker(trafficId, {
          lat: traffic.Lat,
          lon: traffic.Lng,
          bearing: traffic.Track,
          label: label,
        });
      }
    }
  },

  updateTraffic({ data }) {
    get().addTrafficData(data);
    get().renderTrafficData();
  },

  removeStaleTraffic() {
    get().removeStaleTrafficData();
    get().renderTrafficData();
  },
});

const useTrafficStore = create(trafficStore);

export { getTrafficLabel, useTrafficStore };
export default useTrafficStore;
