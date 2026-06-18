# Switch Burner dual hotend concept panel

import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

from ks_includes.screen_panel import ScreenPanel


class ToolheadDrawing(Gtk.DrawingArea):
    def __init__(self, side):
        super().__init__(hexpand=True, vexpand=True)
        self.side = side
        self.active = False
        self.progress = 0.0
        self.target = 0.0
        self.animation_id = None
        self.tool_label = "T?"
        self.filament_color = (0.45, 0.45, 0.45, 1.0)
        self.loaded = False
        self.set_size_request(160, 300)
        self.connect("draw", self.draw)

    def set_tool(self, label, color, loaded):
        self.tool_label = label
        self.filament_color = color
        self.loaded = loaded
        self.queue_draw()

    def set_active(self, active):
        self.active = active
        self.target = 1.0 if active else 0.0
        if self.animation_id is None:
            self.animation_id = GLib.timeout_add(24, self._animate)

    def _animate(self):
        if abs(self.progress - self.target) < 0.02:
            self.progress = self.target
            self.animation_id = None
            self.queue_draw()
            return False
        step = 0.11 if self.progress < self.target else -0.11
        self.progress = max(0.0, min(1.0, self.progress + step))
        self.queue_draw()
        return True

    @staticmethod
    def _rounded_rectangle(cr, x, y, width, height, radius):
        radius = min(radius, width / 2, height / 2)
        cr.new_sub_path()
        cr.arc(x + width - radius, y + radius, radius, -1.5708, 0)
        cr.arc(x + width - radius, y + height - radius, radius, 0, 1.5708)
        cr.arc(x + radius, y + height - radius, radius, 1.5708, 3.1416)
        cr.arc(x + radius, y + radius, radius, 3.1416, 4.7124)
        cr.close_path()

    def _draw_centered_text(self, cr, text, x, y, size, color):
        cr.save()
        cr.select_font_face("Sans", 0, 1)
        cr.set_font_size(size)
        xbearing, ybearing, width, height, _, _ = cr.text_extents(text)
        cr.set_source_rgba(*color)
        cr.move_to(x - width / 2 - xbearing, y - height / 2 - ybearing)
        cr.show_text(text)
        cr.restore()

    def draw(self, widget, cr):
        alloc = self.get_allocation()
        width = max(1, alloc.width)
        height = max(1, alloc.height)
        scale = min(width / 220.0, height / 360.0)
        line_width = max(2.0, 3.0 * scale)

        style = self.get_style_context()
        fg = style.get_color(Gtk.StateFlags.NORMAL)
        line = (fg.red, fg.green, fg.blue, max(fg.alpha, 0.85))
        dim_line = (fg.red, fg.green, fg.blue, 0.38)
        fill = (fg.red, fg.green, fg.blue, 0.04)

        active_offset = height * 0.16 * self.progress
        outer_x = width * 0.08
        outer_y = height * 0.04
        outer_w = width * 0.84
        outer_h = height * 0.91

        cr.set_line_width(line_width)
        cr.set_source_rgba(*fill)
        self._rounded_rectangle(cr, outer_x, outer_y, outer_w, outer_h, 18 * scale)
        cr.fill_preserve()
        cr.set_source_rgba(*(line if self.active else dim_line))
        cr.stroke()

        body_w = width * 0.56
        body_h = height * 0.50
        body_x = (width - body_w) / 2
        body_y = height * 0.14 + active_offset
        nozzle_h = height * 0.10

        cr.set_source_rgba(1, 1, 1, 0.03)
        self._rounded_rectangle(cr, body_x, body_y, body_w, body_h, 14 * scale)
        cr.fill_preserve()
        cr.set_source_rgba(*(line if self.active else dim_line))
        cr.stroke()

        nozzle_top = body_y + body_h
        cr.move_to(body_x + body_w * 0.18, nozzle_top)
        cr.line_to(body_x + body_w * 0.82, nozzle_top)
        cr.line_to(width / 2, nozzle_top + nozzle_h)
        cr.close_path()
        cr.set_source_rgba(1, 1, 1, 0.02)
        cr.fill_preserve()
        cr.set_source_rgba(*(line if self.active else dim_line))
        cr.stroke()

        filament = self.filament_color if self.loaded else (fg.red, fg.green, fg.blue, 0.18)
        stripe_w = max(10 * scale, width * 0.11)
        stripe_x = (width - stripe_w) / 2
        cr.rectangle(stripe_x, outer_y, stripe_w, max(0, body_y - outer_y + height * 0.05))
        cr.rectangle(stripe_x, body_y + body_h * 0.62, stripe_w, body_h * 0.32)
        cr.set_source_rgba(*filament)
        cr.fill()
        cr.set_line_width(max(1.0, line_width * 0.65))
        cr.rectangle(stripe_x, outer_y, stripe_w, max(0, body_y - outer_y + height * 0.05))
        cr.rectangle(stripe_x, body_y + body_h * 0.62, stripe_w, body_h * 0.32)
        cr.set_source_rgba(filament[0], filament[1], filament[2], 0.85 if self.loaded else 0.28)
        cr.stroke()

        text_color = line if self.loaded or self.active else dim_line
        self._draw_centered_text(
            cr,
            self.tool_label,
            width / 2,
            body_y + body_h * 0.43,
            max(20, min(width, height) * 0.16),
            text_color,
        )
        return False


class ColorSwatch(Gtk.DrawingArea):
    def __init__(self):
        super().__init__(hexpand=False, vexpand=False)
        self.color = (0.45, 0.45, 0.45, 1.0)
        self.set_size_request(32, 32)
        self.connect("draw", self.draw)

    def set_color(self, color):
        self.color = color
        self.queue_draw()

    def draw(self, widget, cr):
        alloc = self.get_allocation()
        radius = min(alloc.width, alloc.height) / 2 - 2
        cr.arc(alloc.width / 2, alloc.height / 2, max(2, radius), 0, 6.2832)
        cr.set_source_rgba(*self.color)
        cr.fill_preserve()
        cr.set_source_rgba(0, 0, 0, 0.35)
        cr.set_line_width(2)
        cr.stroke()
        return False


class Panel(ScreenPanel):
    GATE_EMPTY = 0
    GATE_AVAILABLE = 1
    GATE_AVAILABLE_FROM_BUFFER = 2

    COLOR_GREY = (0.45, 0.45, 0.45, 1.0)

    CSS = b"""
    .switch_burner_root {
        padding: 0.35em;
    }
    .switch_burner_tool_button {
        border-radius: 8px;
        padding: 0.25em;
    }
    .switch_burner_tool_button_active {
        border-color: @theme_selected_bg_color;
        box-shadow: inset 0 0 0 0.14em @theme_selected_bg_color;
    }
    .switch_burner_meta {
        opacity: 0.82;
    }
    .switch_burner_select_button label {
        font-size: 2.1em;
        font-weight: bold;
    }
    """

    def __init__(self, screen, title):
        super().__init__(screen, title or "Switch Burner")
        self.active_side = "right"
        self.selected_tool = 0
        self.tool_count = 0
        self._install_css()
        self._create_widgets()
        self._refresh_from_mmu(init_selection=True)

    def _install_css(self):
        try:
            provider = Gtk.CssProvider()
            provider.load_from_data(self.CSS)
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
            self.css_provider = provider
        except Exception as e:
            logging.debug(f"Switch Burner CSS could not be loaded: {e}")

    def _create_widgets(self):
        root_orientation = Gtk.Orientation.VERTICAL if self._screen.vertical_mode else Gtk.Orientation.HORIZONTAL
        root = Gtk.Box(orientation=root_orientation, spacing=10, hexpand=True, vexpand=True)
        root.get_style_context().add_class("switch_burner_root")

        toolheads = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, homogeneous=True, hexpand=True, vexpand=True)
        self.left_drawing = ToolheadDrawing("left")
        self.right_drawing = ToolheadDrawing("right")
        self.labels["left_toolhead"] = self._toolhead_button(self.left_drawing, "left")
        self.labels["right_toolhead"] = self._toolhead_button(self.right_drawing, "right")
        toolheads.add(self.labels["left_toolhead"])
        toolheads.add(self.labels["right_toolhead"])

        controls = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True, vexpand=True)
        controls.set_size_request(260, -1)
        controls.pack_start(self._build_tool_selector(), False, False, 0)
        controls.pack_start(self._build_action_grid(), True, True, 0)

        root.pack_start(toolheads, True, True, 0)
        root.pack_start(controls, True, True, 0)
        self.content.add(root)

    def _toolhead_button(self, drawing, side):
        button = Gtk.Button(hexpand=True, vexpand=True, can_focus=False)
        button.get_style_context().add_class("switch_burner_tool_button")
        button.add(drawing)
        button.connect("clicked", self._select_side, side)
        return button

    def _build_tool_selector(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, hexpand=True, vexpand=False)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, homogeneous=False, hexpand=True, vexpand=False)
        self.labels["tool_prev"] = self._gtk.Button("decrease", None, scale=self.bts * 1.25)
        self.labels["tool_next"] = self._gtk.Button("increase", None, scale=self.bts * 1.25)
        self.labels["tool_load"] = self._gtk.Button("extruder", "T?", "color2")
        self.labels["tool_load"].get_style_context().add_class("switch_burner_select_button")
        self.labels["tool_prev"].connect("clicked", self._change_selected_tool, -1)
        self.labels["tool_next"].connect("clicked", self._change_selected_tool, 1)
        self.labels["tool_load"].connect("clicked", self._load_selected_tool)
        self.labels["tool_prev"].set_hexpand(False)
        self.labels["tool_next"].set_hexpand(False)

        row.pack_start(self.labels["tool_prev"], False, False, 0)
        row.pack_start(self.labels["tool_load"], True, True, 0)
        row.pack_start(self.labels["tool_next"], False, False, 0)

        meta_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, hexpand=True, vexpand=False)
        self.labels["selected_swatch"] = ColorSwatch()
        self.labels["selector_meta"] = Gtk.Label(label=_("No MMU data"), xalign=0, hexpand=True)
        self.labels["selector_meta"].get_style_context().add_class("switch_burner_meta")
        meta_row.pack_start(self.labels["selected_swatch"], False, False, 0)
        meta_row.pack_start(self.labels["selector_meta"], True, True, 0)

        box.pack_start(row, False, False, 0)
        box.pack_start(meta_row, False, False, 0)
        return box

    def _build_action_grid(self):
        grid = Gtk.Grid(row_spacing=8, column_spacing=8, hexpand=True, vexpand=True)
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)

        actions = [
            ("unload_left", "arrow-up", _("Unload Left"), "color1"),
            ("unload_right", "arrow-up", _("Unload Right"), "color2"),
            ("offset", "z-farther", _("Offset Calibrate"), "color3"),
            ("more", "settings", _("More Settings"), "color4"),
        ]
        for index, (key, icon, label, style) in enumerate(actions):
            button = self._gtk.Button(icon, label, style)
            button.connect("clicked", self._reserved_action, label)
            self.labels[key] = button
            grid.attach(button, index % 2, index // 2, 1, 1)
        return grid

    def activate(self):
        self._refresh_from_mmu()

    def process_update(self, action, data):
        if action != "notify_status_update":
            return
        if "mmu" in data:
            self._refresh_from_mmu()

    def _select_side(self, widget, side):
        self.active_side = side
        self._update_active_side()

    def _change_selected_tool(self, widget, delta):
        if self.tool_count <= 0:
            return
        self.selected_tool = max(0, min(self.tool_count - 1, self.selected_tool + delta))
        self._refresh_from_mmu()

    def _load_selected_tool(self, widget):
        if self.tool_count <= 0:
            self._screen.show_popup_message(_("No MMU tool data available"), level=2)
            return
        self.active_side = "right"
        self._update_active_side()
        script = f"MMU_CHANGE_TOOL TOOL={self.selected_tool} QUIET=1"
        logging.info(f"Switch Burner: {script}")
        self._screen._ws.klippy.gcode_script(script)

    def _reserved_action(self, widget, label):
        self._screen.show_popup_message(_("{name} is reserved for a future Switch Burner workflow").format(name=label), level=1)

    def _get_mmu(self):
        mmu = self._printer.get_stat("mmu")
        return mmu if isinstance(mmu, dict) else {}

    def _refresh_from_mmu(self, init_selection=False):
        mmu = self._get_mmu()
        self.tool_count = self._tool_count(mmu)
        current_tool = self._int_or_none(mmu.get("tool"))
        filament = mmu.get("filament", "Unknown")
        loaded = filament == "Loaded" and current_tool is not None and current_tool >= 0

        if init_selection and current_tool is not None and current_tool >= 0:
            self.selected_tool = current_tool
        if self.tool_count > 0:
            self.selected_tool = max(0, min(self.tool_count - 1, self.selected_tool))
        else:
            self.selected_tool = 0

        self.left_drawing.set_tool(_("Empty"), self.COLOR_GREY, False)

        right_tool = current_tool if current_tool is not None and current_tool >= 0 else self.selected_tool
        right_color = self._tool_color(mmu, right_tool)
        right_label = f"T{right_tool}" if self.tool_count > 0 else "T?"
        self.right_drawing.set_tool(right_label, right_color, loaded)

        selected_color = self._tool_color(mmu, self.selected_tool)
        self.labels["selected_swatch"].set_color(selected_color)
        self.labels["tool_load"].set_label(f"T{self.selected_tool}" if self.tool_count > 0 else "T?")
        self.labels["selector_meta"].set_label(self._selector_meta(mmu, self.selected_tool))

        action = mmu.get("action", "Idle")
        can_select = self.tool_count > 0 and action in ("Idle", "Unknown", None) and self._tool_available(mmu, self.selected_tool)
        self.labels["tool_load"].set_sensitive(can_select)
        self.labels["tool_prev"].set_sensitive(self.tool_count > 0 and self.selected_tool > 0)
        self.labels["tool_next"].set_sensitive(self.tool_count > 0 and self.selected_tool < self.tool_count - 1)
        self._update_active_side()

    def _update_active_side(self):
        left_active = self.active_side == "left"
        right_active = self.active_side == "right"
        self.left_drawing.set_active(left_active)
        self.right_drawing.set_active(right_active)
        for key, active in (("left_toolhead", left_active), ("right_toolhead", right_active)):
            ctx = self.labels[key].get_style_context()
            if active:
                ctx.add_class("button_active")
                ctx.add_class("switch_burner_tool_button_active")
            else:
                ctx.remove_class("button_active")
                ctx.remove_class("switch_burner_tool_button_active")

    @staticmethod
    def _int_or_none(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _tool_count(self, mmu):
        for key in ("ttg_map", "gate_status", "gate_color", "gate_material"):
            value = mmu.get(key)
            if isinstance(value, list) and len(value) > 0:
                return len(value)
        return 0

    def _gate_for_tool(self, mmu, tool):
        ttg_map = mmu.get("ttg_map")
        if isinstance(ttg_map, list) and 0 <= tool < len(ttg_map):
            gate = self._int_or_none(ttg_map[tool])
            if gate is not None and gate >= 0:
                return gate
        return tool

    def _tool_color(self, mmu, tool):
        gate = self._gate_for_tool(mmu, tool)
        gate_color = mmu.get("gate_color", [])
        if isinstance(gate_color, list) and 0 <= gate < len(gate_color):
            return self._parse_color(gate_color[gate], self.COLOR_GREY)
        return self.COLOR_GREY

    def _tool_available(self, mmu, tool):
        gate = self._gate_for_tool(mmu, tool)
        gate_status = mmu.get("gate_status", [])
        if not isinstance(gate_status, list) or not gate_status:
            return True
        if not 0 <= gate < len(gate_status):
            return False
        return gate_status[gate] in (self.GATE_AVAILABLE, self.GATE_AVAILABLE_FROM_BUFFER)

    def _selector_meta(self, mmu, tool):
        if self.tool_count <= 0:
            return _("No MMU data")
        gate = self._gate_for_tool(mmu, tool)
        material = ""
        gate_material = mmu.get("gate_material", [])
        if isinstance(gate_material, list) and 0 <= gate < len(gate_material):
            material = gate_material[gate]
        status = self._gate_status_text(mmu, gate)
        suffix = f" / {material}" if material else ""
        return _("Gate #{gate}: {status}").format(gate=gate, status=status) + suffix

    def _gate_status_text(self, mmu, gate):
        gate_status = mmu.get("gate_status", [])
        if not isinstance(gate_status, list) or not 0 <= gate < len(gate_status):
            return _("Unknown")
        status = gate_status[gate]
        if status == self.GATE_AVAILABLE:
            return _("Available")
        if status == self.GATE_AVAILABLE_FROM_BUFFER:
            return _("Buffered")
        if status == self.GATE_EMPTY:
            return _("Empty")
        return _("Unknown")

    @staticmethod
    def _parse_color(value, fallback):
        if not value:
            return fallback
        value = str(value).strip()
        if len(value) == 8:
            try:
                int(value, 16)
                value = value[:6]
            except ValueError:
                pass
        color = Gdk.RGBA()
        if Gdk.RGBA.parse(color, value) or Gdk.RGBA.parse(color, f"#{value}"):
            return color.red, color.green, color.blue, max(color.alpha, 1.0)
        return fallback
