# Copyright 2024 CrackNuts. All rights reserved.

from cracknuts.cracker.cracker_basic import CrackerBasic
from cracknuts.acquisition import Acquisition

from cracknuts.jupyter.acquisition_panel import AcquisitionPanelWidget
from cracknuts.jupyter.cracker_s1_panel import CrackerS1PanelWidget
from cracknuts.jupyter.cracknuts_panel import CracknutsPanelWidget
from cracknuts.jupyter.trace_panel import TracePanelWidget
from cracknuts.jupyter.scope_panel import ScopePanelWidget
from cracknuts.trace.trace import TraceDataset


def display_cracknuts_panel(acq: "Acquisition"):
    acq.sample_length = -1  # ignore the sample_length of acquisition when use ui.
    cnpw = CracknutsPanelWidget(acquisition=acq)
    # cnpw.sync_config()
    # cnpw.listen_config()
    return cnpw


def display_trace_panel(trace_dataset: TraceDataset = None):
    tpw = TracePanelWidget()
    if trace_dataset:
        tpw.set_trace_dataset(trace_dataset)
    return tpw


def display_scope_panel(acq: "Acquisition"):
    acq.sample_length = -1  # ignore the sample_length of acquisition when use ui.
    return ScopePanelWidget(acquisition=acq)


def display_acquisition_panel(acq: "Acquisition"):
    acq.sample_length = -1  # ignore the sample_length of acquisition when use ui.
    acqw = AcquisitionPanelWidget(acquisition=acq)
    acqw.sync_config_from_acquisition()
    return acqw


def display_cracker_panel(cracker: "CrackerBasic"):
    cpw = CrackerS1PanelWidget(cracker=cracker)
    cpw.read_config_from_cracker()
    cpw.listen_cracker_config()
    return cpw


__all__ = [
    "display_cracknuts_panel",
    "display_trace_panel",
    "display_acquisition_panel",
    "display_cracker_panel",
    "display_scope_panel",
]
