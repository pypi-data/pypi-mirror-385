import whitebox


class WhiteboxPluginTrafficDisplay(whitebox.Plugin):
    name = "Traffic Display"

    provides_capabilities = ["traffic"]
    slot_component_map = {
        "traffic.markers": "TrafficMarkers",
        "traffic.unknown-traffic-overlay": "UnknownTraffic",
    }


plugin_class = WhiteboxPluginTrafficDisplay
