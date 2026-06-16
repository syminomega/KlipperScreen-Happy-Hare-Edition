# Happy Hare MMU UI translation helpers

TOOL_UNKNOWN = -1
TOOL_BYPASS = -2


def format_mmu_state(value):
    translations = {
        "Available": _("Available"),
        "Buffered": _("Buffered"),
        "Empty": _("Empty"),
        "Unknown": _("Unknown"),
        "Loaded": _("Loaded"),
        "Unloaded": _("Unloaded"),
        "Loading": _("Loading"),
        "Unloading": _("Unloading"),
        "Idle": _("Idle"),
        "Disabled": _("Disabled"),
        "Complete": _("Complete"),
        "Error": _("Error"),
        "Cancelled": _("Cancelled"),
        "Started": _("Started"),
        "Printing": _("Printing"),
        "Paused": _("Paused"),
        "Pause Locked": _("Pause Locked"),
        "complete": _("Complete"),
        "error": _("Error"),
        "cancelled": _("Cancelled"),
        "started": _("Started"),
        "printing": _("Printing"),
        "paused": _("Paused"),
        "pause_locked": _("Pause Locked"),
    }
    return translations.get(value, value)


def format_tool(tool, na=False):
    if tool >= 0:
        return f"T{tool}"
    if tool == TOOL_BYPASS:
        return _("Bypass")
    return _("n/a") if na else _("Unknown")


def format_gate(gate, na=False, with_label=True):
    if gate >= 0:
        if with_label:
            return _("Gate #{gate}").format(gate=gate)
        return f"#{gate}"
    if gate == TOOL_BYPASS:
        return _("Bypass")
    return _("n/a") if na else _("Unknown")


def format_filament_state(state):
    return format_mmu_state(state)
