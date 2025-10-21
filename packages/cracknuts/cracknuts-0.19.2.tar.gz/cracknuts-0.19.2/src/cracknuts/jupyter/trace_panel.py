# Copyright 2024 CrackNuts. All rights reserved.

import colorsys
import functools
import os
import pathlib
import typing
from dataclasses import dataclass, field
from numbers import Number

import numpy as np
import zarr
from numpy import ndarray

from cracknuts import logger

from cracknuts.trace.trace import TraceDataset, NumpyTraceDataset
from traitlets import traitlets

from cracknuts.jupyter.panel import MsgHandlerPanelWidget

from cracknuts.utils import user_config


@dataclass
class _TraceSeriesData:
    name: str
    data: ndarray
    color: None | str
    channel_index: int
    trace_index: int
    z: int

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "data": self.data,
            "color": self.color,
            "channel_index": self.channel_index,
            "trace_index": self.trace_index,
            "z": self.z,
        }


def correlation_zarr_substitute(substitute_func_name: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self: "TracePanelWidget", *args, **kwargs):
            if self._correlation_traces is not None:
                substitute_func = getattr(self, substitute_func_name, None)
                if substitute_func is not None:
                    return substitute_func(*args, **kwargs)
                else:
                    raise ValueError(f"The substitute function {substitute_func_name} is not defined.")
            else:
                return func(self, *args, **kwargs)

        return wrapper

    return decorator


@dataclass
class _TraceSeries:
    series_data_list: list[_TraceSeriesData] = field(default_factory=list)
    x_data: ndarray = field(default_factory=lambda: np.empty(0))
    percent_range: list = field(default_factory=lambda: [0, 100])
    range: list = field(default_factory=lambda: [0, 0])

    def to_dict(self) -> dict:
        return {
            "seriesDataList": [s.to_dict() for s in self.series_data_list],
            "xData": self.x_data,
            "percentRange": self.percent_range,
            "range": self.range,
        }


class TracePanelWidget(MsgHandlerPanelWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "TracePanelWidget.js"
    _css = pathlib.Path(__file__).parent / "static" / "TracePanelWidget.css"

    chart_size: dict[str, int] = traitlets.Dict({"width": 0, "height": 0}).tag(sync=True)

    trace_series = traitlets.Dict(_TraceSeries().to_dict()).tag(sync=True)

    range_start = traitlets.Float(0).tag(sync=True)
    range_end = traitlets.Float(100).tag(sync=True)

    selected_range = traitlets.Tuple((0, 0)).tag(sync=True)
    percent_range = traitlets.Tuple((0, 100)).tag(sync=True)
    overview_select_range = traitlets.Tuple((0, 0)).tag(sync=True)

    overview_trace_series = traitlets.Dict(_TraceSeries().to_dict()).tag(sync=True)

    language = traitlets.Unicode("en").tag(sync=True)

    _DEFAULT_SHOW_INDEX_THRESHOLD = 3

    _DEFAULT_SERIES_Z = 2

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._logger = logger.get_logger(self)
        self._emphasis = kwargs.get("emphasis", False)
        self._trace_dataset: TraceDataset | None = None
        self.show_trace: ShowTrace = ShowTrace(self._show_trace)
        self._auto_sync = False
        self._overview_trace_series: _TraceSeries | None = None
        self._trace_series: _TraceSeries | None = None
        self._trace_cache_channel_indices: list | None = None
        self._trace_cache_trace_indices: list | None = None
        self._trace_cache_traces: ndarray | None = None
        self._trace_cache_x_indices: ndarray | None = None
        self._trace_cache_x_range_start: int | None = None
        self._trace_cache_x_range_end: int | None = None
        self._trace_cache_trace_highlight_indices: dict[int, list[int]] | None = None

        self._correlation_traces = None
        self._is_correlation_traces_setting = False

        self._trace_series_color_background = "gray"

        self.reg_msg_handler("reset", "onClick", self.reset)

        self.language = user_config.get_option("language", fallback="en")

    def _repr_mimebundle_(self, **kwargs: dict) -> tuple[dict, dict] | None:
        self._trace_series_send_state()
        self._auto_sync = True
        return super()._repr_mimebundle_(**kwargs)

    def set_numpy_data(self, trace: np.ndarray, data: np.ndarray = None) -> None:
        """
        展示numpy格式的曲线数据

        :param trace: 曲线数据
        :type trace: np.ndarray
        """
        self.set_numpy_like_data(trace, data)

    def set_numpy_like_data(self, trace: np.ndarray | zarr.core.Array, data: np.ndarray = None) -> None:
        ds = NumpyTraceDataset.load_from_numpy_array(trace)
        self.set_trace_dataset(ds)

    @correlation_zarr_substitute("_correlation_zarr_show_trace")
    def _show_trace(self, channel_slice, trace_slice, display_range: tuple[int, int] = None):
        channel_indexes, trace_indices, traces, data = self._trace_dataset.trace_data_with_indices[
            channel_slice, trace_slice
        ]
        self._trace_cache_channel_indices = channel_indexes
        self._trace_cache_trace_indices = trace_indices
        self._trace_cache_traces = traces

        if display_range is None:
            if self._trace_cache_x_range_start is None:
                self._trace_cache_x_range_start = 0
            if self._trace_cache_x_range_end is None:
                self._trace_cache_x_range_end = self._trace_dataset.sample_count - 1
        else:
            self._trace_cache_x_range_start = display_range[0]
            self._trace_cache_x_range_end = display_range[1]

        self._trace_series = self._get_trace_series_by_index_range(
            self._trace_cache_x_range_start, self._trace_cache_x_range_end
        )
        self._trace_series.percent_range = [
            self._trace_cache_x_range_start / (self._trace_dataset.sample_count - 1) * 100,
            self._trace_cache_x_range_end / (self._trace_dataset.sample_count - 1) * 100,
        ]

        self._update_overview_trace()

        if self._auto_sync:
            self._trace_series_send_state()

    def _update_overview_trace(self):
        if self._trace_cache_trace_highlight_indices is not None:
            overview_channel_index, overview_trace_indices = list(self._trace_cache_trace_highlight_indices.items())[0]
            overview_trace_index = overview_trace_indices[0]
            if (
                overview_channel_index not in self._trace_cache_channel_indices
                or overview_trace_index not in self._trace_cache_trace_indices
            ):
                self.highlight(None)
            if overview_channel_index not in self._trace_cache_channel_indices:
                overview_channel_index = self._trace_cache_channel_indices[0]
            if overview_trace_index not in self._trace_cache_trace_indices:
                overview_trace_index = self._trace_cache_trace_indices[0]

        else:
            overview_channel_index = self._trace_cache_channel_indices[0]
            overview_trace_index = self._trace_cache_trace_indices[0]

        c_idx = self._trace_cache_channel_indices.index(overview_channel_index)
        t_idx = self._trace_cache_trace_indices.index(overview_trace_index)

        x_idx, y_data = self._get_by_range(
            self._trace_cache_traces[c_idx, t_idx, :],
            0,
            self._trace_dataset.sample_count,
        )
        self._overview_trace_series = _TraceSeries(
            series_data_list=[
                _TraceSeriesData(
                    name=str(overview_channel_index) + "-" + str(overview_trace_index),
                    data=y_data,
                    trace_index=overview_trace_index,
                    channel_index=overview_channel_index,
                    z=self._DEFAULT_SERIES_Z,
                    color="blue",
                )
            ],
            x_data=x_idx,
        )

        percent_start = self._trace_cache_x_range_start / (self._trace_dataset.sample_count - 1) * 100
        percent_end = self._trace_cache_x_range_end / (self._trace_dataset.sample_count - 1) * 100

        self._overview_trace_series.range = [
            round((self._overview_trace_series.x_data.shape[0] - 1) * percent_start / 100),
            round((self._overview_trace_series.x_data.shape[0] - 1) * percent_end / 100),
        ]

        if self._auto_sync:
            self.overview_trace_series = self._overview_trace_series.to_dict()

    def _trace_series_send_state(self):
        if self._trace_series is None:
            return
        self.trace_series = self._trace_series.to_dict()
        self.overview_trace_series = self._overview_trace_series.to_dict()

    def _get_by_range(self, trace: np.ndarray, start, end):
        pixel = self.chart_size["width"]
        if pixel is None or pixel == 0:
            pixel = 1920
        x_idx, y_data = self._down_sample(trace, start, end, pixel)
        return x_idx, y_data

    @staticmethod
    def _down_sample(value: np.ndarray, mn, mx, down_count) -> tuple[np.ndarray, np.ndarray]:
        mn = max(0, mn)
        mx = min(value.shape[0], mx)

        _value = value[mn:mx]
        _index = np.arange(mn, mx).astype(np.int32)

        ds = int(max(1, int(mx - mn) / down_count))

        if ds == 1:
            return _index, _value
        sample_count = int((mx - mn) // ds)

        down_index = np.empty((sample_count, 2), dtype=np.int32)
        down_index[:] = _index[: sample_count * ds : ds, np.newaxis]

        _value = _value[: sample_count * ds].reshape((sample_count, ds))
        down_value = np.empty((sample_count, 2))
        down_value[:, 0] = _value.max(axis=1)
        down_value[:, 1] = _value.min(axis=1)

        return down_index.reshape(sample_count * 2), down_value.reshape(sample_count * 2)

    def _change_range(self, start: int, end: int):
        if self._trace_cache_x_indices is not None:
            start, end = self._trace_cache_x_indices[start], self._trace_cache_x_indices[end]
        self.change_range(start, end)

    def change_range(self, start: int, end: int):
        """
        改变曲线展示的区间

        :param start: 开始索引
        :type start: int
        :param end: 结束索引
        :type end: int
        """
        self._trace_cache_x_range_start = start
        self._trace_cache_x_range_end = end
        self._trace_series = self._get_trace_series_by_index_range(start, end)

        percent_start = start / (self._trace_dataset.sample_count - 1) * 100
        percent_end = end / (self._trace_dataset.sample_count - 1) * 100
        self._trace_series.percent_range = [percent_start, percent_end]

        self._overview_trace_series.range = [
            round((self._overview_trace_series.x_data.shape[0] - 1) * percent_start / 100),
            round((self._overview_trace_series.x_data.shape[0] - 1) * percent_end / 100),
        ]

        if self._auto_sync:
            self._trace_series_send_state()

    def _overview_selected_range_changed(self, start: int, end: int):
        start = int(self._overview_trace_series.x_data[start])
        end = int(self._overview_trace_series.x_data[end])
        self._trace_cache_x_range_start = start
        self._trace_cache_x_range_end = end
        self._trace_series = self._get_trace_series_by_index_range(start, end)

        self._trace_series.percent_range = [
            start / (self._trace_dataset.sample_count - 1) * 100,
            end / (self._trace_dataset.sample_count - 1) * 100,
        ]

        if self._auto_sync:
            self._trace_series_send_state()

    def change_percent_range(self, percent_start: float, percent_end: float):
        """
        改变展示曲线的百分比

        :param percent_start: 开始
        :type percent_start: float
        :param percent_end: 结束
        :type percent_end: float
        """
        start = round((self._trace_dataset.sample_count - 1) * percent_start / 100)
        end = round((self._trace_dataset.sample_count - 1) * percent_end / 100)

        self._trace_cache_x_range_start = start
        self._trace_cache_x_range_end = end

        self._trace_series = self._get_trace_series_by_index_range(start, end)

        self._trace_series.percent_range = [percent_start, percent_end]

        self._overview_trace_series.range = [
            round((self._overview_trace_series.x_data.shape[0] - 1) * percent_start / 100),
            round((self._overview_trace_series.x_data.shape[0] - 1) * percent_end / 100),
        ]
        if self._auto_sync:
            self._trace_series_send_state()

    def _get_trace_series_by_index_range(self, start: int, end: int) -> _TraceSeries:
        series_data_list = []

        if self._trace_cache_trace_highlight_indices is not None:
            highlight_colors = self._generate_colors(
                sum(len(v) for v in self._trace_cache_trace_highlight_indices.values())
            )
            highlight_colors.append(self._trace_series_color_background)
            color_i = 0
        else:
            highlight_colors = None
            color_i = 0

        x_idx = None
        for c, channel_index in enumerate(self._trace_cache_channel_indices):
            for t, trace_index in enumerate(self._trace_cache_trace_indices):
                x_idx, y_data = self._get_by_range(self._trace_cache_traces[c, t, :], start, end)
                color, z_increase = self._get_highlight_color(
                    channel_index, trace_index, None if highlight_colors is None else highlight_colors[color_i]
                )
                if z_increase > 0:
                    color_i += 1
                series_data_list.append(
                    _TraceSeriesData(
                        name=str(channel_index) + "-" + str(trace_index),
                        data=y_data,
                        color=color,
                        trace_index=trace_index,
                        channel_index=channel_index,
                        z=self._DEFAULT_SERIES_Z
                        if z_increase == 0
                        else self._DEFAULT_SERIES_Z + z_increase + c * len(self._trace_cache_trace_indices) + t,
                    )
                )

        self._trace_cache_x_indices = x_idx

        return _TraceSeries(series_data_list=series_data_list, x_data=x_idx)

    def _get_highlight_color(
        self, channel_index: int, trace_index: int, highlight_color: str
    ) -> tuple[None, int] | tuple[str, int]:
        if self._trace_cache_trace_highlight_indices is None:
            return None, 0
        else:
            if channel_index in self._trace_cache_trace_highlight_indices:
                trace_indices = self._trace_cache_trace_highlight_indices[channel_index]
                if trace_index in trace_indices:
                    return highlight_color, 1
                else:
                    return self._trace_series_color_background, 0
            else:
                return self._trace_series_color_background, 0

    @staticmethod
    def _generate_colors(count):
        colors = []
        for i in range(count):
            hue = i / count
            r, g, b = colorsys.hls_to_rgb(hue, 0.5, 0.7)
            hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
            colors.append(hex_color)
        return colors

    def show_default_trace(self):
        trace_count = self._trace_dataset.trace_count
        self._show_trace(
            0,
            slice(
                0,
                trace_count if trace_count < self._DEFAULT_SHOW_INDEX_THRESHOLD else self._DEFAULT_SHOW_INDEX_THRESHOLD,
            ),
        )

    def show_all_trace(self):
        """
        展示全部曲线。
        提示: 谨慎使用该函数，当曲线长度过大或曲线数量过大时，容易造成卡顿
        """
        self._show_trace(slice(0, self._trace_dataset.channel_count), slice(0, self._trace_dataset.trace_count))

    def highlight(self, indices: dict[int, list[int] | int] | list[int] | int | None) -> None:
        """
        高亮曲线

        高亮指定曲线索引的曲线：高亮时，未被包含在高亮索引(indices)现有展示的曲线将以灰色展示。
        该函数一般用于展示相关性曲线中分数最高的曲线。
        """
        if isinstance(indices, int):
            indices = {0: [indices]}
        elif isinstance(indices, list):
            indices = {0: indices}
        elif isinstance(indices, dict):
            for k, v in indices.items():
                if isinstance(v, int):
                    indices[k] = [v]
                else:
                    raise ValueError("The indices value type is not supported, it should be int or list of int.")

        if indices is None or len(indices) == 0:
            self._trace_cache_trace_highlight_indices = None
            for series in self._trace_series.series_data_list:
                series.color = None
                series.z = self._trace_cache_trace_highlight_indices
            if self._auto_sync:
                self._trace_series_send_state()
            return

        series_indices = [(series.channel_index, series.trace_index) for series in self._trace_series.series_data_list]

        for channel_index in indices.keys():
            for trace_index in indices[channel_index]:
                if (channel_index, trace_index) not in series_indices:
                    self._logger.error(
                        f"The highlighted item [channel index: {channel_index}, "
                        f"trace index: {trace_index}] is not visible."
                    )
                    return

        self._trace_cache_trace_highlight_indices = indices

        highlight_colors = self._generate_colors(sum(len(v) for v in indices.values()))
        highlight_colors.append(self._trace_series_color_background)
        color_i = 0
        for series in self._trace_series.series_data_list:
            color, z_increase = self._get_highlight_color(
                series.channel_index, series.trace_index, highlight_colors[color_i]
            )
            series.color = color
            series.z = (
                self._DEFAULT_SERIES_Z
                if z_increase == 0
                else (
                    self._DEFAULT_SERIES_Z
                    + z_increase
                    + series.channel_index * len(self._trace_cache_trace_indices)
                    + series.trace_index
                )
            )
            if z_increase > 0:
                color_i += 1

        if self._auto_sync:
            self._trace_series_send_state()

        self._update_overview_trace()

    def reset(self, args):
        """
        重置曲线展示
        """
        self._trace_cache_trace_highlight_indices = None
        self._trace_cache_x_range_start = 0
        self._trace_cache_x_range_end = self._trace_dataset.sample_count - 1
        self._trace_series = self._get_trace_series_by_index_range(
            self._trace_cache_x_range_start, self._trace_cache_x_range_end
        )
        self._trace_series.percent_range = [
            self._trace_cache_x_range_start / (self._trace_dataset.sample_count - 1) * 100,
            self._trace_cache_x_range_end / (self._trace_dataset.sample_count - 1) * 100,
        ]

        if self._auto_sync:
            self._trace_series_send_state()

        self._update_overview_trace()

    def set_trace_dataset(
        self, trace_dataset: TraceDataset, show_all_trace=False, channel_slice=None, trace_slice=None
    ) -> None:
        """
        展示曲线数据集中的曲线

        :param trace_dataset: 曲线数据集
        :type trace_dataset: TraceDataset
        :param show_all_trace: 是否展示全部曲线
        :type show_all_trace: bool
        :param channel_slice: 曲线通道索引切片，该参数支持类似numpy的高级切片操作
        :type channel_slice: slice
        :param trace_slice: 曲线索引切片，该参数支持类似numpy的高级切片操作
        :type trace_slice: slice
        """
        if not self._is_correlation_traces_setting:
            self._correlation_traces = None
        self._trace_dataset = trace_dataset
        if show_all_trace:
            self.show_all_trace()
        elif channel_slice is not None and trace_slice is not None:
            self._show_trace(channel_slice, trace_slice)
        else:
            self.show_default_trace()

    def open_numpy_file(self, path: str):
        if os.path.isdir(path):
            trace_path = os.path.join(path, "trace.npy")
            if os.path.exists(trace_path):
                trace = np.load(trace_path)
                self.set_numpy_data(trace)
            else:
                raise ValueError(f"The directory {path} does not contain trace.npy file.")
        elif os.path.isfile(path):
            trace = np.load(path)
        else:
            raise ValueError(f"The path {path} is neither a file nor a directory containing trace.npy.")

        if len(trace.shape) == 2:
            self.set_numpy_data(trace)
        else:
            raise ValueError(f"The file {path} does not contain valid trace data, it should be a 2D array.")

    def open_zarr(self, path: str):
        zarr_data = zarr.open(path, mode="r")
        self.set_zarr(zarr_data)

    def set_zarr(self, zarr_trace: zarr.hierarchy.Group | zarr.core.Array):
        if isinstance(zarr_trace, zarr.hierarchy.Group):
            traces_data = zarr_trace.get("/0/0/traces")
            if traces_data is not None:
                self.set_numpy_data(traces_data)
            else:
                traces_data = zarr_trace.get("/0/0/correlation")
                if traces_data is not None:
                    self.set_correlation_zarr_trace(traces_data)
                else:
                    raise ValueError(
                        "The zarr group does not contain valid trace data, "
                        "it should contain /0/0/traces dataset or /0/0/correlation."
                    )
        elif isinstance(zarr_trace, zarr.core.Array):
            if len(zarr_trace.shape) == 2:
                self.set_numpy_like_data(zarr_trace)
            elif len(zarr_trace.shape) == 3:
                self.set_correlation_zarr_trace(zarr_trace)
            else:
                raise ValueError("The zarr data zarr should be a 2D array.")
        else:
            raise ValueError("The zarr parameter type is not supported.")

    def set_correlation_zarr(self, correlation_zarr: zarr.hierarchy.Group):
        self.set_correlation_zarr_trace(correlation_zarr.get("/0/0/correlation"))

    def set_correlation_zarr_trace(self, correlation_zarr_trace: zarr.core.Array):
        self._correlation_traces = correlation_zarr_trace
        if self._correlation_traces is None:
            raise ValueError(
                "The correlation zarr does not contain valid trace data, it should contain /0/0/correlation."
            )
        default_show_traces = self._correlation_traces[:, 0, :]
        self._is_correlation_traces_setting = True
        self.set_numpy_like_data(default_show_traces)
        self._is_correlation_traces_setting = False

    def _correlation_zarr_show_trace(self, guss_slice: slice, byte_slice: slice):
        channel_indices = TraceDataset._parse_slice(
            self._correlation_traces.shape[0], guss_slice
        )  # 使用Guss索引模拟通道索引
        trace_indices = TraceDataset._parse_slice(
            self._correlation_traces.shape[1], byte_slice
        )  # 使用字节索引模拟曲线索引
        if isinstance(guss_slice, int):
            guss_slice = slice(guss_slice, guss_slice + 1)
        if isinstance(byte_slice, int):
            byte_slice = slice(byte_slice, byte_slice + 1)

        if isinstance(byte_slice, list):
            # 这里如果 guss_slice 也是一个列表的化，不支持numpy 那样的 配对形式的切片，
            # 所以不能实现指定多个猜测字节下单个比特位曲线的效果
            sub_traces = []
            for trace_index in trace_indices:
                sub_traces.append(self._correlation_traces[guss_slice, trace_index, :])
            traces = np.stack(sub_traces, axis=1)
        else:
            traces = self._correlation_traces[guss_slice, byte_slice, :]

        self._trace_cache_channel_indices = channel_indices
        self._trace_cache_trace_indices = trace_indices
        self._trace_cache_traces = traces

        if self._trace_cache_x_range_start is None:
            self._trace_cache_x_range_start = 0
        if self._trace_cache_x_range_end is None:
            self._trace_cache_x_range_end = self._trace_dataset.sample_count - 1

        self._trace_series = self._get_trace_series_by_index_range(
            self._trace_cache_x_range_start, self._trace_cache_x_range_end
        )

        self._trace_series.percent_range = [
            self._trace_cache_x_range_start / (self._trace_dataset.sample_count - 1) * 100,
            self._trace_cache_x_range_end / (self._trace_dataset.sample_count - 1) * 100,
        ]

        self._update_overview_trace()

        if self._auto_sync:
            self._trace_series_send_state()

    def set_trace(
        self, trace: TraceDataset | np.ndarray | zarr.hierarchy.Group | zarr.core.Array | list[list[Number]] | str
    ):
        if isinstance(trace, TraceDataset):
            self.set_trace_dataset(trace)
        elif isinstance(trace, np.ndarray):
            self.set_numpy_data(trace)
        elif isinstance(trace, zarr.hierarchy.Group) or isinstance(trace, zarr.core.Array):
            self.set_zarr(trace)
        elif isinstance(trace, list):
            self.set_numpy_data(np.array(trace))
        elif isinstance(trace, str):
            if pathlib.Path(trace).suffix in [".npy"]:
                self.open_numpy_file(trace)
            elif pathlib.Path(trace).suffix in [".zarr"]:
                self.open_zarr(trace)
        else:
            raise ValueError("The trace parameter type is not supported.")

    @traitlets.observe("selected_range")
    def selected_range_changed(self, change) -> None:
        if change.get("new") is not None:
            s, e = change.get("new")
            self._change_range(s, e)

    @traitlets.observe("overview_select_range")
    def overview_select_range_changed(self, change) -> None:
        if change.get("new") is not None:
            s, e = change.get("new")
            self._overview_selected_range_changed(s, e)

    @traitlets.observe("percent_range")
    def percent_range_changed(self, change) -> None:
        if change.get("new") is not None:
            s, e = change.get("new")
            self.change_percent_range(s, e)


class ShowTrace:
    def __init__(self, func_show_trace):
        self._func_trace = func_show_trace

    def __getitem__(self, item):
        return self._func_trace(item[0], item[1])
