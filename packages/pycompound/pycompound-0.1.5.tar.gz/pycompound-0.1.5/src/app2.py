

# app.py
from shiny import App, ui, render, reactive
import pandas as pd

# Parameters to choose from + suggested default ranges
PARAMS = {
    "window_size_centroiding": (0.0, 0.5),
    "window_size_matching":    (0.0, 0.5),
    "noise_threshold":         (0.0, 0.25),
    "wf_mz":                   (0.0, 5.0),
    "wf_int":                  (0.0, 5.0),
    "LET_threshold":           (0.0, 5.0),
    "entropy_dimension":       (1.0, 3.0),
}

app_ui = ui.page_fillable(
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3("Select parameters"),
            ui.input_checkbox_group(
                id="params",
                label=None,
                choices=list(PARAMS.keys()),
                selected=["window_size_centroiding", "noise_threshold"],
            ),
            ui.hr(),
            ui.h4("Bounds for selected parameters"),
            ui.output_ui("bounds_inputs"),
            width=360,
        ),
    )
)

def server(input, output, session):
    @output
    @render.ui
    def bounds_inputs():
        selected = input.params()
        if not selected:
            return ui.div(ui.em("Select one or more parameters above."))

        blocks = []
        for name in selected:
            lo, hi = PARAMS.get(name, (0.0, 1.0))
            blocks.append(
                ui.card(
                    ui.card_header(name),
                    ui.layout_columns(
                        ui.input_numeric(f"min_{name}", "Lower", lo, step=0.001),
                        ui.input_numeric(f"max_{name}", "Upper", hi, step=0.001),
                    )
                )
            )
        return ui.div(*blocks)

    def _read_bounds_dict():
        selected = input.params()
        out = {}
        for name in selected:
            lo_default, hi_default = PARAMS.get(name, (0.0, 1.0))
            lo_id = f"min_{name}"
            hi_id = f"max_{name}"

            # Use input[...]() and guard with "in input"
            lo_val = input[lo_id]() if lo_id in input else lo_default
            hi_val = input[hi_id]() if hi_id in input else hi_default

            out[name] = (float(lo_val), float(hi_val))
        return out



    # Table of current bounds
    @output
    @render.data_frame
    def bounds_table():
        b = _read_bounds_dict()
        if not b:
            return pd.DataFrame(columns=["parameter", "lower", "upper"])
        rows = [{"parameter": k, "lower": v[0], "upper": v[1]} for k, v in b.items()]
        return pd.DataFrame(rows)

    # JSON-ish view (string) you can parse/use elsewhere
    @output
    @render.text
    def bounds_json():
        b = _read_bounds_dict()
        if not b:
            return "{}"
        # Pretty-print as Python dict literal for quick copy/paste
        lines = ["{"]
        for k, (lo, hi) in b.items():
            lines.append(f"  '{k}': ({lo}, {hi}),")
        lines.append("}")
        return "\n".join(lines)

app = App(app_ui, server)


