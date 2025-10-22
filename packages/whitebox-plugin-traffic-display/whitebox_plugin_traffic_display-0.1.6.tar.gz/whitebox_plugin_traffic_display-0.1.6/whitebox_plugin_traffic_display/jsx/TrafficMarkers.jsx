import { useEffect, useRef, useState } from "react";
import { Marker, Tooltip } from "react-leaflet";
import L from "leaflet";
import useTrafficStore from "./stores/traffic";

const createIcon = (iconUrl, bearing = 0) => {
  return L.divIcon({
    html: `<div style="transform: rotate(${90 + bearing}deg);">
               <img src="${iconUrl}" style="width: 32px; height: 32px;" />
             </div>`,
    className: "traffic-icon-container",
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

const TrafficMarker = ({ id, marker }) => {
  const markerRef = useRef(null);
  const [icon, setIcon] = useState(
    marker.iconUrl ? createIcon(marker.iconUrl, marker.bearing) : null
  );

  // Update position without re-rendering
  useEffect(() => {
    if (markerRef.current) {
      markerRef.current.setLatLng([marker.lat, marker.lon]);
    }
  }, [marker.lat, marker.lon]);

  // Update icon when bearing changes
  useEffect(() => {
    if (marker.iconUrl && marker.bearing !== undefined) {
      setIcon(createIcon(marker.iconUrl, marker.bearing));
    }
  }, [marker.bearing, marker.iconUrl]);

  return (
    <Marker position={[marker.lat, marker.lon]} icon={icon} ref={markerRef}>
      {marker.label && (
        <Tooltip direction="bottom" offset={[0, 20]} opacity={1} permanent>
          {marker.label.split("\n").map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </Tooltip>
      )}
    </Marker>
  );
};

const TrafficMarkers = () => {
  const trafficMarkers = useTrafficStore((state) => state.trafficMarkers);
  const updateTraffic = useTrafficStore((state) => state.updateTraffic);
  const removeStaleTraffic = useTrafficStore(
    (state) => state.removeStaleTraffic
  );
  const staleTrafficRemovalInterval = useTrafficStore(
    (state) => state.staleTrafficRemovalInterval
  );

  useEffect(() => {
    // Set up stale traffic removal interval
    const interval = setInterval(() => {
      removeStaleTraffic();
    }, staleTrafficRemovalInterval);

    // Set up WebSocket listener for traffic updates
    const wbSocket = Whitebox.sockets.addEventListener(
      "flight",
      "message",
      (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "traffic.update") {
          updateTraffic({ data });
        }
      }
    );

    // Cleanup both interval and WebSocket listener
    return () => {
      clearInterval(interval);
      wbSocket();
    };
  }, [removeStaleTraffic, staleTrafficRemovalInterval, updateTraffic]);

  return (
    <>
      {Object.entries(trafficMarkers).map(([id, marker]) => (
        <TrafficMarker key={id} id={id} marker={marker} />
      ))}
    </>
  );
};

export { TrafficMarkers };
export default TrafficMarkers;
