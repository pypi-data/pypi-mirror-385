from .setup import *
from .constants import *
from .layers import *
from .utils import *
import gdsfactory as gf
from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np
import math

from gdsfactory.cross_section import Section
from gdsfactory.generic_tech import LAYER_STACK, LAYER


def make_prob(
    path,
    sources,
    modes,
    layer_stack,
    materials_library,
    component=None,
    wavelengths=None,
    wavelength=None,
    entries=None,
    keys=["2,1"],
    study="sparams",
    nres=4,
    monitors=None,
    frequency=None,
    frequencies=None,
    wl1f=None,
    #
    verbose=True,
    #
    targets=[],
    designs=[],
    # layer_design=DESIGN,
    design_ports=None,
    #
    path_length_multiple=0.85,
    approx_2D_mode=None,
    pixel_size=0.01,
    info=None,
    **kwargs
):
    if approx_2D_mode:
        N = 2
    else:
        N = 3

    if wl1f is None:
        ordering = "wavelength"
    else:
        ordering = "frequency"

    if targets:
        study = "inverse_design"

    if frequencies is not None:
        assert wl1f is not None
        assert wavelengths is None
        wavelengths = [wl1f / f for f in frequencies]
    if frequency:
        wavelength = wl1f / frequency

    if type(wavelengths) in [int, float]:
        wavelengths = [wavelengths]
    wavelengths = sorted(wavelengths)
    if wavelength is None:
        wavelength = median(wavelengths)
    # nres *= wavelength / min(map(min, wavelengths))

    for s in sources:
        if s["frequency"]:
            w, bw = convert_frequency_wavelength(s["frequency"], wl1f, s["bandwidth"])
            s["wavelength"] = w
            s["bandwidth"] = bw

    prob = setup(
        path,
        component=component,
        study=study,
        wavelength=wavelength,
        wl1f=wl1f,
        wavelengths=wavelengths,
        sources=sources,
        layer_stack=layer_stack,
        materials_library=materials_library,
        modes=modes,
        verbose=verbose,
        keys=keys,
        ordering=ordering,
        nres=nres,
        approx_2D_mode=approx_2D_mode,
        pixel_size=pixel_size,
        info=info,
        designs=designs,
        targets=targets,
        #  sources=sources, monitors=monitors,
        **kwargs
    )

    if designs:

        def _bbox(b):
            return [[b.left / 1e3, b.bottom / 1e3], [b.right / 1e3, b.top / 1e3]]

        _designs = []
        for d in designs:
            layer = d["layer"]
            fill_material = d["fill_material"]
            void_material = d["void_material"]

            design = get_layers(layer_stack, layer)[0].material

            ks = set(materials_library[fill_material].keys()).intersection(
                set(materials_library[void_material].keys())
            )
            swaps = {
                k: (
                    materials_library[void_material][k],
                    materials_library[fill_material][k],
                )
                for k in ks
            }

            bbox = component.extract([layer]).bbox_np().tolist()
            if N == 3:
                l = get_layers(layer_stack, layer)[0]
                bbox[0].append(l.zmin)
                bbox[1].append(l.zmin + l.thickness)
            _designs.append(
                {
                    **d,
                    "bbox": bbox,
                    "swaps": swaps,
                }
            )
        designs = _designs

        prob = {
            **prob,
            **{
                "designs": designs,
                "path_length_multiple": path_length_multiple,
                "design_ports": design_ports,
            },
        }
    save_problem(prob, path)
    return prob

    # l = [k for k in imow if port_number(k) == pi]
    # if not l:
    #     imow[f"o{pi}@{mi}"] = []
    # else:
    #     k = l[0]
    #     mn = max(mode_number(k), mi)
    #     if mn != mode_number(k):
    #         imow[i] = imow[k]
    #         del imow[k]

    # l = [k for k in imow[i] if port_number(k) == po]
    # if not l:
    #     imow[f"o{pi}@{mi}"]
    # else:
    #     k = l[0]
    #     mn = max(mode_number(k), mi)
    #     if mn != mode_number(k):
    #         imow[f"o{pi}@{mn}"] = imow[k]
    #         del imow[k]

    # if po not in imow[pi]:
    #     imow[pi]["o"][po] = mo
    # else:
    #     imow[pi]["o"][po] = max(imow[pi]["o"][po], mo)
