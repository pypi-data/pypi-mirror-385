# Copyright 2024 CrackNuts. All rights reserved.

__version__ = "0.19.2"

import sys
import typing
from collections.abc import Callable

from cracknuts.acquisition import Acquisition, AcquisitionBuilder
from cracknuts.cracker.cracker_basic import CrackerBasic
from cracknuts.cracker.cracker_g1 import CrackerG1
from cracknuts.cracker.cracker_s1 import CrackerS1

try:
    from IPython.display import display

    if "ipykernel" not in sys.modules:
        display = None
    else:
        from cracknuts import jupyter as cn_jupyter
except ImportError:
    display = None
    cn_jupyter = None


def version():
    return __version__


CRACKER = typing.TypeVar("CRACKER", bound=CrackerBasic)


def new_cracker(
    address: tuple | str | None = None,
    bin_server_path: str | None = None,
    bin_bitstream_path: str | None = None,
    operator_port: int = None,
    model: type[CRACKER] | str | None = None,
) -> CRACKER:
    kwargs = {
        "address": address,
        "bin_server_path": bin_server_path,
        "bin_bitstream_path": bin_bitstream_path,
        "operator_port": operator_port,
    }
    if model is None:
        model = CrackerS1
    else:
        if isinstance(model, str):
            if model.lower() == "s1":
                model = CrackerS1
            elif model.lower() == "g1":
                model = CrackerG1
            else:
                raise ValueError(f"Unknown cracker model: {model}")
    return model(**kwargs)


def new_acquisition(
    cracker: CrackerBasic,
    init: Callable[[CrackerBasic], None] | None = None,
    do: Callable[[CrackerBasic], dict[str, bytes]] | None = None,
    finish: Callable[[CrackerBasic], None] | None = None,
    sample_length: int | None = None,
    data_plaintext_length: int | None = None,
    data_ciphertext_length: int | None = None,
    data_key_length: int | None = None,
    data_extended_length: int | None = None,
    **acq_kwargs,
) -> Acquisition:
    acq_kwargs["sample_length"] = sample_length
    acq_kwargs["data_plaintext_length"] = data_plaintext_length
    acq_kwargs["data_ciphertext_length"] = data_ciphertext_length
    acq_kwargs["data_key_length"] = data_key_length
    acq_kwargs["data_extended_length"] = data_extended_length
    return AcquisitionBuilder().cracker(cracker).init(init).do(do).finish(finish).build(**acq_kwargs)


if display is not None:

    def panel(acq: Acquisition):
        return cn_jupyter.display_cracknuts_panel(acq)


if display is not None:

    def panel_cracker(cracker: CrackerBasic):
        return cn_jupyter.display_cracker_panel(cracker)


if display is not None:

    def panel_scope(acq: Acquisition):
        return cn_jupyter.display_scope_panel(acq)


if display is not None:

    def panel_acquisition(acq: Acquisition):
        return cn_jupyter.display_acquisition_panel(acq)


if display is not None:

    def panel_trace():
        return cn_jupyter.display_trace_panel()
