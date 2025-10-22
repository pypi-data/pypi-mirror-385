from typing import Any, Callable
import array
import anywidget
import pathlib

import traitlets

base_path = pathlib.Path(__file__).parent / "static"


class ScatterPlotData:
    x: list[float]
    y: list[float]
    name: str
    mode: str

    def __init__(self) -> None:
        self.x = []
        self.y = []
        self.name = ""
        self.mode = "markers"


class EnsembleWidget(anywidget.AnyWidget):
    _esm = base_path / "ensemble_widget.js"

    row_metadata = traitlets.List([]).tag(sync=True)
    n_rows = traitlets.Int(1).tag(sync=True)
    n_cols = traitlets.Int(1).tag(sync=True)
    cell_data = traitlets.Dict({}).tag(sync=True)
    loaded_rows = traitlets.List([]).tag(sync=True)  # List of row indices that have data loaded

    # Callback for loading row data on demand
    _row_data_callback: Callable[[int], None] | None = None

    def __init__(
        self, row_metadata: list[dict[str, str | float]], n_rows: int, n_cols: int, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.on_msg(self._receive_widget_message)
        self.row_metadata = row_metadata
        self.n_rows = n_rows
        self.n_cols = n_cols

    def set_cell_data(self, row: int, col: int, data: bytes, data_type: str) -> None:
        cell_key = f"{row},{col}"
        self.cell_data = {
            **self.cell_data,
            cell_key: {
                "cell": [row, col],
                "data_type": data_type,
                "data": data,
            },
        }

    def set_cell_scatter_plot(
        self,
        row: int,
        col: int,
        title: str,
        axis_labels: list[str],
        axis_data: list[list[float]],
        plot_name: str = "data",
        plot_mode: str = "markers",
    ) -> None:
        cell_key = f"{row},{col}"
        scatter_data: list[bytes] = []

        for axis_values in axis_data:
            scatter_data.append(array.array("f", axis_values).tobytes())

        self.cell_data = {
            **self.cell_data,
            cell_key: {
                "cell": [row, col],
                "data_type": "scatter_plot",
                "cell_extra": {
                    "title": title,
                    "axis_labels": axis_labels,
                    "plot_names": [plot_name],
                    "plot_modes": [plot_mode],
                },
                "data": scatter_data,
            },
        }

    def set_row_data_callback(self, callback: Callable[[int], None]) -> None:
        """Set the callback function to be called when row data is requested."""
        self._row_data_callback = callback

    def _maybe_execute_callback(self, row: int) -> bool:
        """Execute the row data callback if it exists. Returns True if executed."""
        if self._row_data_callback is not None:
            self._row_data_callback(row)
            return True
        return False

    def _receive_widget_message(self, widget: Any, content: Any, buffers: list[memoryview]) -> None:
        if isinstance(content, str):
            if content == "request_row_data":
                # Decode row indices from buffer (sent as Int32Array)
                if buffers and len(buffers) > 0:
                    import struct

                    # Each int32 is 4 bytes
                    num_rows = len(buffers[0]) // 4
                    rows = struct.unpack(f"{num_rows}i", buffers[0])

                    # Load all rows
                    executed_rows = [row for row in rows if self._maybe_execute_callback(row)]

                    # Mark all rows as loaded in one update
                    new_loaded = [r for r in executed_rows if r not in self.loaded_rows]
                    if new_loaded:
                        self.loaded_rows = self.loaded_rows + new_loaded
