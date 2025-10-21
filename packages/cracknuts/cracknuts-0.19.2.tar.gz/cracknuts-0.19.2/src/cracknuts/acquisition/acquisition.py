# Copyright 2024 CrackNuts. All rights reserved.

import abc
import dataclasses
from dataclasses import dataclass
import datetime
import json
import os.path
import threading
import time
import traceback
import typing

import numpy as np

from cracknuts import logger
from cracknuts.cracker.cracker_basic import CrackerBasic
from cracknuts.trace.trace import ZarrTraceDataset, NumpyTraceDataset


@dataclass
class AcquisitionConfig:
    trace_count: int = 1
    sample_length: int = 1024
    sample_offset: int = 0
    trigger_judge_timeout: float = 0.005
    trigger_judge_wait_time: float = 0.05
    do_error_max_count: int = 1
    file_path: str = ""
    file_format: str = "zarr"


class AcqProgress:
    def __init__(self, finished: int, total: int):
        self.finished: int = finished
        self.total: int = total


class Acquisition(abc.ABC):
    """
    Trace acquisition process control class
    """

    STATUS_STOPPED: int = 0
    STATUS_TESTING: int = 1
    STATUS_RUNNING: int = 2
    _STATUS_PAUSED_SWITCH: int = -1

    DO_ERROR_HANDLER_STRATEGY_EXIT: int = 0
    DO_ERROR_HANDLER_STRATEGY_CONTINUE_UNTIL_MAX_ERROR_COUNT: int = 1

    _DATASET_DEFAULT_PATH = "./dataset/"

    def __init__(
        self,
        cracker: CrackerBasic,
        trace_count: int = 1000,
        sample_length: int = -1,
        sample_offset: int = 0,
        data_plaintext_length: int | None = None,
        data_ciphertext_length: int | None = None,
        data_key_length: int | None = None,
        data_extended_length: int | None = None,
        trigger_judge_wait_time: float = 0.05,
        trigger_judge_timeout: float = 1.0,
        do_error_handler_strategy: int = DO_ERROR_HANDLER_STRATEGY_EXIT,
        do_error_max_count: int = -1,
        file_format: str = "zarr",
        file_path: str = "auto",
        trace_fetch_interval: float = 0,
    ):
        """
        :param cracker: The controlled Cracker object.
        :type cracker: CrackerBasic
        :param trace_count: The number of traces to acquire.
        :type trace_count: int
        :param sample_length: the sample length to be acquired,
                              If it is -1, it will be set to the value of `cracker.current_count().sample_len`.
        :type sample_length: int
        :param sample_offset: the sample offset to be acquired.
        :type sample_offset: int
        :param trigger_judge_timeout: The trigger judge timeout in seconds.
        :type trigger_judge_timeout: float
        :param trigger_judge_wait_time: The trigger judge wait time in seconds.
        :type trigger_judge_wait_time: float
        :param do_error_handler_strategy: The strategy to handle error handling.
                                          0: Exit immediately, 1: Exit after exceeding the error count.
        :type do_error_handler_strategy: int
        :param do_error_max_count: The maximum number of error count.
                                   If `do_error_handler_strategy` is 0, this setting is invalid.
        :type do_error_max_count: int
        :param file_format: The file format of the trace dataset. "zarr" or "numpy".
        :type file_format: str
        :param file_path: The file path of the trace dataset. If set to "auto", a folder with a timestamp format
                          will be created in the current working directory to save the data.
        :type file_path: str
        """
        self._logger = logger.get_logger(self)
        self._last_wave: dict[int, np.ndarray] | None = {1: np.zeros(1)}
        self._status: int = self.STATUS_STOPPED
        self._current_trace_count = 1
        self._run_thread_pause_event: threading.Event = threading.Event()

        self.cracker: CrackerBasic = cracker
        self.trace_count: int = trace_count
        self.sample_length = sample_length
        self.sample_offset: int = sample_offset
        self.metadata_plaintext_length: int = data_plaintext_length
        self.metadata_ciphertext_length: int = data_ciphertext_length
        self.metadata_key_length: int = data_key_length
        self.metadata_extended_length: int = data_extended_length
        self.trigger_judge_wait_time: float = trigger_judge_wait_time  # second
        self.trigger_judge_timeout: float = trigger_judge_timeout  # second
        self.do_error_handler_strategy: int = do_error_handler_strategy
        self.do_error_max_count: int = do_error_max_count  # -1 never exit
        self.file_format: str = file_format
        if file_path is None or file_path == "auto":
            file_path = os.path.abspath(self._DATASET_DEFAULT_PATH)
        self.file_path: str = file_path

        self._on_wave_loaded_callback: typing.Callable[[typing.Any], None] | None = None
        self._on_status_change_listeners: list[typing.Callable[[int], None]] = []
        self._on_run_progress_changed_listeners: list[typing.Callable[[dict], None]] = []
        self.trace_fetch_interval = trace_fetch_interval

    def get_status(self):
        return self._status

    def set_cracker(self, cracker: CrackerBasic):
        self.cracker = cracker

    def on_status_changed(self, callback: typing.Callable[[int], None]) -> None:
        """
        User should not use this function. If you need to perform actions when the ACQ state changes,
        please use the node functions in the ACQ lifecycle point: `init`, `do`, and `finish`.

        status: 0 stopped, 1 testing, 2 running 3 paused
        """
        self._on_status_change_listeners.append(callback)

    def on_run_progress_changed(self, callback: typing.Callable[[dict], None]) -> None:
        self._on_run_progress_changed_listeners.append(callback)

    def on_wave_loaded(self, callback: typing.Callable[[typing.Any], None]) -> None:
        self._on_wave_loaded_callback = callback

    def run(
        self,
        count: int = 1,
        sample_length: int = 1024,
        sample_offset: int = 0,
        data_plaintext_length: int | None = None,
        data_ciphertext_length: int | None = None,
        data_key_length: int | None = None,
        data_extended_length: int | None = None,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
        file_format: str | None = "zarr",
        file_path: str | None = "auto",
    ):
        """
        Start run mode in the background.
        The parameters configured here will override the settings specified in `__init__`.

        :param count: The number of traces to acquire.
        :type count: int
        :param sample_length: The sample length to be acquired.
        :type sample_length: int
        :param sample_offset: The sample offset to be acquired.
        :type sample_offset: int
        :param trigger_judge_wait_time: The trigger judge wait time in seconds.
        :type trigger_judge_wait_time: float
        :param trigger_judge_timeout: The trigger judge timeout in seconds.
        :type trigger_judge_timeout: float
        :param do_error_max_count: The maximum number of error count.
                                   If `do_error_handler_strategy` is 0, this setting is invalid.
        :type do_error_max_count: int
        :param do_error_handler_strategy: The strategy to handle error handling.
                                          0: Exit immediately, 1: Exit after exceeding the error count.
        :type do_error_handler_strategy: int
        :param file_format: The file format of the trace dataset. "zarr" or "numpy".
        :type file_format: str
        :param file_path: The file path of the trace dataset. If set to "auto", a folder with a timestamp format
                          will be created in the current working directory to save the data.
        :type file_path: str
        """
        if self._status < 0:
            self.resume()
        else:
            self._run(
                test=False,
                count=count,
                sample_length=sample_length,
                sample_offset=sample_offset,
                data_plaintext_length=data_plaintext_length,
                data_ciphertext_length=data_ciphertext_length,
                data_key_length=data_key_length,
                data_extended_length=data_extended_length,
                trigger_judge_wait_time=trigger_judge_wait_time,
                trigger_judge_timeout=trigger_judge_timeout,
                do_error_max_count=do_error_max_count,
                do_error_handler_strategy=do_error_handler_strategy,
                file_format=file_format,
                file_path=file_path,
            )

    def run_sync(
        self,
        count=1,
        sample_length: int = 1024,
        sample_offset: int = 0,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
        file_format: str | None = "zarr",
        file_path: str | None = "auto",
    ):
        """
        Start run mode in the foreground, which will cause blocking.

        :param count: The number of traces to acquire.
        :type count: int
        :param sample_length: The sample length to be acquired.
        :type sample_length: int
        :param sample_offset: The sample offset to be acquired.
        :type sample_offset: int
        :param trigger_judge_wait_time: The trigger judge wait time in seconds.
        :type trigger_judge_wait_time: float
        :param trigger_judge_timeout: The trigger judge timeout in seconds.
        :type trigger_judge_timeout: float
        :param do_error_max_count: The maximum number of error count.
                                   If `do_error_handler_strategy` is 0, this setting is invalid.
        :type do_error_max_count: int
        :param do_error_handler_strategy: The strategy to handle error handling.
                                          0: Exit immediately, 1: Exit after exceeding the error count.
        :type do_error_handler_strategy: int
        :param file_format: The file format of the trace dataset. "zarr" or "numpy".
        :type file_format: str
        :param file_path: The file path of the trace dataset. If set to "auto", a folder with a timestamp format
                          will be created in the current working directory to save the data.
        :type file_path: str
        """
        try:
            self._do_run(
                test=False,
                count=count,
                sample_length=sample_length,
                sample_offset=sample_offset,
                trigger_judge_wait_time=trigger_judge_wait_time,
                trigger_judge_timeout=trigger_judge_timeout,
                do_error_max_count=do_error_max_count,
                do_error_handler_strategy=do_error_handler_strategy,
                file_format=file_format,
                file_path=file_path,
            )
            self._logger.debug("stop by timeout.")
        except KeyboardInterrupt:
            self._logger.debug("stop by interrupted.")
            self.stop()

    def test(
        self,
        count=-1,
        sample_length: int | None = None,
        sample_offset: int | None = None,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
        trace_fetch_interval: float = 2.0,
    ):
        """
        Start test mode in background.

        :param count: The number of traces to acquire. normally this value should be -1.
        :type count: int
        :param sample_length: The sample length to be acquired.
        :type sample_length: int
        :param sample_offset: The sample offset to be acquired.
        :type sample_offset: int
        :param trigger_judge_wait_time: The trigger judge wait time in seconds.
        :type trigger_judge_wait_time: float
        :param trigger_judge_timeout: The trigger judge timeout in seconds.
        :type trigger_judge_timeout: float
        :param do_error_max_count: The maximum number of error count.
                                   If `do_error_handler_strategy` is 0, this setting is invalid.
        :type do_error_max_count: int
        :param do_error_handler_strategy: The strategy to handle error handling.
                                          0: Exit immediately, 1: Exit after exceeding the error count.
        """
        if self._status < 0:
            self._logger.debug("Resume to test mode.")
            self.resume()
        else:
            self._logger.debug("Start test mode.")
            self._run(
                test=True,
                count=count,
                sample_length=sample_length,
                sample_offset=sample_offset,
                trigger_judge_wait_time=trigger_judge_wait_time,
                trigger_judge_timeout=trigger_judge_timeout,
                do_error_max_count=do_error_max_count,
                do_error_handler_strategy=do_error_handler_strategy,
                trace_fetch_interval=trace_fetch_interval,
            )

    def test_sync(
        self,
        count=-1,
        sample_length: int | None = None,
        sample_offset: int | None = None,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
    ):
        """
        Start test mode in foreground, which will cause blocking.

        :param count: The number of traces to acquire. normally this value should be -1.
        :type count: int
        :param sample_length: The sample length to be acquired.
        :type sample_length: int
        :param sample_offset: The sample offset to be acquired.
        :type sample_offset: int
        :param trigger_judge_wait_time: The trigger judge wait time in seconds.
        :type trigger_judge_wait_time: float
        :param trigger_judge_timeout: The trigger judge timeout in seconds.
        :type trigger_judge_timeout: float
        :param do_error_max_count: The maximum number of error count.
                                   If `do_error_handler_strategy` is 0, this setting is invalid.
        :type do_error_max_count: int
        :param do_error_handler_strategy: The strategy to handle error handling.
                                          0: Exit immediately, 1: Exit after exceeding the error count.
        """
        try:
            self._do_run(
                test=True,
                count=count,
                sample_length=sample_length,
                sample_offset=sample_offset,
                trigger_judge_wait_time=trigger_judge_wait_time,
                trigger_judge_timeout=trigger_judge_timeout,
                do_error_max_count=do_error_max_count,
                do_error_handler_strategy=do_error_handler_strategy,
            )
        except KeyboardInterrupt:
            self._logger.debug("stop by interrupted.")
            self.stop()

    def pause(self):
        """
        Pause test or run mode.

        """
        if self._status > 0:
            self._run_thread_pause_event.clear()
            self._status = self._status * self._STATUS_PAUSED_SWITCH

    def resume(self):
        """
        Resume from paused test or run mode.

        """
        if self._status < 0:
            self._run_thread_pause_event.set()
            self._status = self._status * self._STATUS_PAUSED_SWITCH

    def stop(self):
        """
        Stop test or run mode.

        """
        if not self._run_thread_pause_event.is_set():
            self._run_thread_pause_event.set()
        self._status = self.STATUS_STOPPED

    def _run(
        self,
        test: bool = True,
        count: int = 1,
        sample_length: int | None = None,
        sample_offset: int | None = None,
        data_plaintext_length: int | None = None,
        data_ciphertext_length: int | None = None,
        data_key_length: int | None = None,
        data_extended_length: int | None = None,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
        file_format: str | None = "zarr",
        file_path: str | None = "auto",
        trace_fetch_interval: float = 0.1,
    ):
        self._run_thread_pause_event.set()
        threading.Thread(
            target=self._do_run,
            kwargs={
                "test": test,
                "count": count,
                "sample_length": sample_length,
                "sample_offset": sample_offset,
                "data_plaintext_length": data_plaintext_length,
                "data_ciphertext_length": data_ciphertext_length,
                "data_key_length": data_key_length,
                "data_extended_length": data_extended_length,
                "trigger_judge_wait_time": trigger_judge_wait_time,
                "trigger_judge_timeout": trigger_judge_timeout,
                "do_error_max_count": do_error_max_count,
                "do_error_handler_strategy": do_error_handler_strategy,
                "file_format": file_format,
                "file_path": file_path,
                "trace_fetch_interval": trace_fetch_interval,
            },
        ).start()

    def _do_run(
        self,
        test: bool = True,
        count: int = 1,
        sample_length: int | None = None,
        sample_offset: int | None = None,
        data_plaintext_length: int | None = None,
        data_ciphertext_length: int | None = None,
        data_key_length: int | None = None,
        data_extended_length: int | None = None,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
        file_format: str | None = "zarr",
        file_path: str | None = "auto",
        trace_fetch_interval: float = 0.1,
    ):
        if self._status > 0:
            self._logger.warning(
                f'AcquisitionTemplate is already running in {'run' if self._status == 2 else 'test'} mode.'
            )
            return

        if not test:
            self._status = self.STATUS_RUNNING
            self._status_changed()
        else:
            self._status = self.STATUS_TESTING
            self._status_changed()

        self.trace_count = count
        if sample_length is not None:
            self.sample_length = sample_length
        if sample_offset is not None:
            self.sample_offset = sample_offset
        if data_plaintext_length is not None:
            self.metadata_plaintext_length = data_plaintext_length
        if data_ciphertext_length is not None:
            self.metadata_ciphertext_length = data_ciphertext_length
        if data_key_length is not None:
            self.metadata_key_length = data_key_length
        if data_extended_length is not None:
            self.metadata_extended_length = data_extended_length
        if trigger_judge_wait_time is not None:
            self.trigger_judge_wait_time = trigger_judge_wait_time
        if trigger_judge_timeout is not None:
            self.trigger_judge_timeout = trigger_judge_timeout
        if do_error_max_count is not None:
            self.do_error_max_count = do_error_max_count
        if do_error_handler_strategy is not None:
            self.do_error_handler_strategy = do_error_handler_strategy
        if file_format is not None:
            self.file_format = file_format
        if file_path is not None:
            self.file_path = file_path
        if trace_fetch_interval is not None:
            self.trace_fetch_interval = trace_fetch_interval
        self.pre_init()
        self.init()
        self._post_init()
        self._loop(not test, self.file_path, self.file_format)
        self._pre_finish()
        self.finish()
        self._post_finish()

    def _status_changed(self):
        for listener in self._on_status_change_listeners:
            listener(self._status)

    def _loop(self, persistent: bool = True, file_path: str | None = None, file_format: str = "zarr"):
        do_error_count = 0
        trace_index = 0
        self._progress_changed(AcqProgress(trace_index, self.trace_count))

        cracker_version = self.cracker.get_firmware_version()
        if persistent:
            cracker_config = self.cracker.get_current_config()
            channel_names = []
            if cracker_config.osc_channel_0_enable:
                channel_names.append("0")
            if cracker_config.osc_channel_1_enable:
                channel_names.append("1")
            if self.sample_length == -1:
                sample_length = self.cracker.get_current_config().osc_sample_length
            else:
                sample_length = self.sample_length

            if file_path is None or file_path == "auto":
                file_path = self._DATASET_DEFAULT_PATH
            if not file_path.endswith("/"):
                file_path += "/"
            file_path += datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            if file_format == "zarr":
                file_path += ".zarr"
            elif file_format == "numpy":
                file_path += ".npy"

            if file_format == "zarr":
                dataset = ZarrTraceDataset.new(
                    file_path,
                    channel_names,
                    self.trace_count,
                    sample_length,
                    version=f"({cracker_version}, {cracker_version})",
                    data_plaintext_length=self.metadata_plaintext_length,
                    data_ciphertext_length=self.metadata_ciphertext_length,
                    data_extended_length=self.metadata_extended_length,
                    data_key_length=self.metadata_key_length,
                )
            elif file_format == "numpy":
                dataset = NumpyTraceDataset.new(
                    file_path,
                    channel_names,
                    self.trace_count,
                    sample_length,
                    version=f"({cracker_version}, {cracker_version})",
                    data_plaintext_length=self.metadata_plaintext_length,
                    data_ciphertext_length=self.metadata_ciphertext_length,
                    data_extended_length=self.metadata_extended_length,
                    data_key_length=self.metadata_key_length,
                )
            else:
                self._logger.error(f"Unsupported file format: {file_format}")
                return
        else:
            dataset = None

        while self._status != 0 and self.trace_count - trace_index != 0:
            if self._status < 0:
                self._status_changed()
                self._run_thread_pause_event.wait()
                self._status_changed()
            self._logger.debug("Get wave data: %s", trace_index)
            self.pre_do()
            start = time.time()
            try:
                data = self.do()
            except Exception as e:
                self._logger.error(f"Do error <{e}>:\n {traceback.format_exc()}")
                do_error_count += 1
                if self.do_error_handler_strategy == self.DO_ERROR_HANDLER_STRATEGY_EXIT:
                    self._logger.error("Exit with do error")
                    break
                elif do_error_count > self.do_error_max_count:
                    self._logger.error(
                        f"Exit with do function get error count: {do_error_count} is grate than do_error_max_count"
                    )
                    break
                else:
                    self._logger.error(f"Do function get error count: {do_error_count}")
                    continue
            self._logger.debug(f"count: {trace_index} delay: {time.time() - start}")
            trigger_judge_start_time = time.time()
            while self._status != 0:
                trigger_judge_time = time.time() - trigger_judge_start_time
                if trigger_judge_time > self.trigger_judge_timeout:
                    self._logger.error(
                        "Triggered judge timeout and will get next waves, " "judge time: %s and timeout is %s",
                        trigger_judge_time,
                        self.trigger_judge_timeout,
                    )
                    break
                self._logger.debug("Judge trigger status.")
                if self._is_triggered():
                    self._logger.debug(f"Triggered! Cost {trigger_judge_time}.")
                    self._last_wave = self._get_waves(self.sample_offset, self.sample_length)
                    if self._last_wave is not None:
                        self._logger.debug(
                            "Got wave: %s.",
                            {k: v.shape for k, v in self._last_wave.items()},
                        )
                        # self._logger.debug('Got wave: ')
                    if self._on_wave_loaded_callback and callable(self._on_wave_loaded_callback):
                        try:
                            self._on_wave_loaded_callback(self._last_wave)
                        except Exception as e:
                            self._logger.error("Wave loaded event callback error: %s", e.args)
                    break

                time.sleep(self.trigger_judge_wait_time)
            if dataset is not None and self._last_wave is not None:
                for k in self._last_wave.keys():
                    dataset.set_trace(str(k), trace_index, self._last_wave[k], data)
            self._post_do()
            trace_index += 1
            self._current_trace_count = trace_index
            self._progress_changed(AcqProgress(trace_index, self.trace_count))
            # Reduce the execution frequency in test mode.
            if not persistent:
                if self.trace_fetch_interval is not None and self.trace_fetch_interval != 0:
                    time.sleep(self.trace_fetch_interval)

        if dataset is not None:
            dataset.dump()
        self._status = self.STATUS_STOPPED
        self._status_changed()

    def _progress_changed(self, progress: "AcqProgress"):
        for listener in self._on_run_progress_changed_listeners:
            listener({"finished": progress.finished, "total": progress.total})

    def _loop_without_log(self):
        ...
        # for i in range(self.trace_count):
        #     # print('yes', self._logger.handlers[0].stream)
        #     # self._logger.debug('Get wave data: %s', i)
        #     self.pre_do()
        #     self.do()
        #     trigger_judge_start_time = time.time()
        #     while self._status:
        #         trigger_judge_time = time.time() - trigger_judge_start_time
        #         if trigger_judge_time > self.trigger_judge_timeout:
        #             # self._logger.error("Triggered judge timeout and will get next waves, "
        #             #                    "judge time: %s and timeout is %s",
        #             #                    trigger_judge_time, self._trigger_judge_timeout)
        #             break
        #         # self._logger.debug('Judge trigger status.')
        #         if self._is_triggered():
        #             self._last_wave = self._get_waves()
        #             if self._last_wave is not None:
        #                 ...
        #                 # self._logger.debug('Got wave: %s.', self._last_wave.shape)
        #             if self._on_wave_loaded_callback and callable(self._on_wave_loaded_callback):
        #                 try:
        #                     self._on_wave_loaded_callback(self._last_wave)
        #                 except Exception as e:
        #                     ...
        #                     # self._logger.error('Wave loaded event callback error: %s', e.args)
        #             time.sleep(1)
        #             break
        #         time.sleep(self.trigger_judge_wait_time)
        #     self._save_wave()
        #     self._post_do()

    def connect_scrat(self):
        """
        Connect to scrat device
        :return:
        """
        ...

    def connect_cracker(self):
        """
        Connect to cracker device.
        :return:
        """
        self.cracker.connect()

    def connect_net(self): ...

    def config_scrat(self): ...

    def config_cracker(self): ...

    def pre_init(self): ...

    @abc.abstractmethod
    def init(self):
        """
        The `init` logic, which the user should implement in the subclass.

        """
        ...

    def _post_init(self): ...

    def transfer(self): ...

    def pre_do(self):
        self.cracker.osc_single()

    @abc.abstractmethod
    def do(self) -> dict[str, bytes]:
        """
        The `do` logic, which the user should implement in the subclass.

        :return: The data in dictionary format to be saved should contain the ciphertext and plaintext keys,
                 and may optionally include the key and extended keys.
                 The plaintext is the data to be encrypted, the ciphertext is the encrypted result, the key is used
                 to encrypt the plaintext, and the extended field is for any custom data you want to save.
                 The data is structured as follows:
                 {
                    "plaintext": plaintext_data_bytes,
                    "ciphertext": ciphertext_data_bytes,
                    "key": key_data_bytes,
                    "extended": extended_data_bytes,
                }
        :rtype: dict[str, bytes]
        """
        ...

    def _do(self):
        try:
            self.do()
            return True
        except Exception as e:
            self._logger.error("Do error: %s", e.args)
            return False

    def _post_do(self): ...

    def _is_triggered(self):
        _, triggered = self.cracker.osc_is_triggered()
        return triggered

    def _get_waves(self, offset: int, sample_length: int) -> dict[int, np.ndarray]:
        if sample_length == -1:
            sample_length = self.cracker.get_current_config().osc_sample_length
        config = self.cracker.get_current_config()

        enable_channels = []
        if config.osc_channel_0_enable:
            enable_channels.append(0)
        if config.osc_channel_1_enable:
            enable_channels.append(1)
        wave_dict = {}
        for c in enable_channels:
            status, wave_dict[c] = self.cracker.osc_get_analog_wave(c, offset, sample_length)
        return wave_dict

    def _pre_finish(self): ...

    def _post_finish(self): ...

    def _save_dataset(self): ...

    def finish(self):
        pass

    def get_last_wave(self) -> dict[int, np.ndarray] | None:
        """
        Get the last wave.

        """
        return self._last_wave

    def dump_config(self, path: str = None) -> str | None:
        """
        Dump the current config to a JSON file if a path is specified, or to a JSON string if no path is specified.

        :param path: the path to the JSON file
        :return: the content of JSON string or None if no path is specified.
        """
        config = AcquisitionConfig(
            self.trace_count,
            self.sample_length,
            self.sample_offset,
            self.trigger_judge_timeout,
            self.trigger_judge_wait_time,
            self.do_error_max_count,
            self.file_path,
            self.file_format,
        )

        if path is None:
            return json.dumps(dataclasses.astuple(config))
        else:
            with open(path, "w") as f:
                json.dump(dataclasses.astuple(config), f)

    def load_config_from_file(self, path: str) -> None:
        """
        Load config from a JSON file.

        :param path: the path to the JSON file
        """
        with open(path) as f:
            self.load_config_from_str(json.load(f))

    def load_config_from_str(self, json_str: str) -> None:
        """
        Load config from a JSON string.

        :param json_str: the JSON string
        """
        config = json.loads(json_str)
        self.load_config_from_json(config)

    def load_config_from_json(self, config: dict):
        """
        Load config from a JSON object.

        :param config: the JSON object
        """
        self.trace_count = config["trace_count"]
        self.sample_length = config["sample_length"]
        self.sample_offset = config["sample_offset"]
        self.trigger_judge_timeout = config["trigger_judge_timeout"]
        self.trigger_judge_wait_time = config["trigger_judge_wait_time"]
        self.do_error_max_count = config["do_error_max_count"]
        self.file_path = config["file_path"]
        self.file_format = config["file_format"]

    def is_running(self):
        return self._status != self.STATUS_STOPPED

    @staticmethod
    def builder():
        return AcquisitionBuilder()


class AcquisitionBuilder:
    """
    The helper class for create a Sub acquisition class.

    """

    def __init__(self):
        self._cracker = None
        self._do_function = lambda _: ...
        self._init_function = lambda _: ...
        self._finish_function = lambda _: ...

    def cracker(self, cracker: CrackerBasic):
        """
        Specify the cracker for acquisition.

        :param cracker: the cracker
        :type cracker: CrackerBasic
        :return: 'AcquisitionBuilder'
        """
        self._cracker = cracker
        return self

    def init(self, init_function: typing.Callable[[CrackerBasic], None]):
        """
        The init function of acquisition.

        :param init_function: the init function
        :type init_function: typing.Callable[[CrackerBasic], None]
        :return: 'AcquisitionBuilder'
        """
        if init_function is not None:
            self._init_function = init_function
        return self

    def do(self, do_function: typing.Callable[[CrackerBasic], dict[str, bytes]]):
        """
        The do function of acquisition.

        :param do_function: the do function
        :type do_function: typing.Callable[[CrackerBasic], None]
        :return: 'AcquisitionBuilder'
        """
        if do_function is not None:
            self._do_function = do_function
        return self

    def finish(self, finish_function: typing.Callable[[CrackerBasic], None]):
        """
        The finish function of acquisition.

        :param finish_function: the finish function
        :type finish_function: typing.Callable[[CrackerBasic], None]
        :return: 'AcquisitionBuilder'
        """
        if finish_function is not None:
            self._finish_function = finish_function
        return self

    def build(self, **kwargs):
        """
        Build the acquisition object.

        :param kwargs: other keyword arguments of Acquisition.
        :type kwargs: dict
        :return Acquisition
        """
        if self._cracker is None:
            raise ValueError("No cracker")

        builder_self = self

        class AnonymousAcquisition(Acquisition):
            def __init__(self, *ana_args, **ana_kwargs):
                super().__init__(*ana_args, **ana_kwargs)

            def init(self):
                builder_self._init_function(self.cracker)

            def do(self):
                return builder_self._do_function(self.cracker)

            def finish(self):
                builder_self._finish_function(self.cracker)

        return AnonymousAcquisition(self._cracker, **kwargs)
