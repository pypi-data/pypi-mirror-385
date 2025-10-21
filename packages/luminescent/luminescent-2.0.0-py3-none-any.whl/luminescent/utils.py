import math
import cv2
from IPython.display import Image
from PIL import Image as PILImage
import os
from matplotlib import pylab
import shapely
import json
from statistics import median
from .constants import *
import gdsfactory as gf
from gdsfactory.cross_section import Section
from .constants import *
from .materials import *
import pyvista as pv

try:
    from IPython.display import display
except ImportError:
    pass
# import pyvista as pv

# from .picToGDS import main

from math import ceil, cos, pi, sin, tan
import matplotlib.pyplot as plt
import numpy as np
from gdsfactory.generic_tech import LAYER_STACK, LAYER
import copy
import shutil
import trimesh


def isnum(x):
    return isinstance(
        x,
        (
            float,
            int,
            np.floating,
            np.integer,
            np.complexfloating,
            np.float64,
            np.complex64,
            complex,
        ),
    )


def _writejsonnp(pre, d):
    # print(f"keeping {pre} as is {type(d)}")
    # if type(d) is list:
    #     print(type(d[0]))
    if isinstance(d, dict):
        return {k: _writejsonnp(f"{pre}#{k}", v) for k, v in d.items()}
    if isinstance(d, np.ndarray):  # or (
        #     type(d) is list and (isnum(d[0]) or (type(d[0]) is list and isnum(d[0][0])))
        # ):
        name = f"{pre}.npy"
        np.save(name, d)
        return os.path.basename(name)

    if type(d) is list or type(d) is tuple:
        return [_writejsonnp(f"{pre}#{i+1}", x) for i, x in enumerate(d)]
    # if isinstance(d, np.complex64):
    #     raise ValueError("complex numbers should be in dict {'re':..., 'im':...}")
    if isnum(d) or isinstance(d, str) or d is None:
        return d
    print(d)
    raise ValueError(f"cannot serialize {pre} of type {type(d)}")


def writejsonnp(path, d):
    DATA = os.path.join(os.path.dirname(path), f".{os.path.basename(path)}")
    os.makedirs(DATA, exist_ok=True)
    with open(path, "w") as io:
        r = {k: _writejsonnp(str(os.path.join(DATA, str(k))), v) for k, v in d.items()}
        json.dump(
            r,
            io,
            indent=4,
        )


def _readjsonnp(pre, x):
    if type(x) is dict:
        return {k: _readjsonnp(f"{pre}#{k}", v) for k, v in x.items()}
    if type(x) is list:
        return [_readjsonnp(f"{pre}#{i+1}", x) for i, x in enumerate(x)]
    if str(x).endswith(".npy"):
        return np.load(f"{pre}.npy")
    return x


def readjsonnp(path):
    return {
        k: _readjsonnp(
            str(os.path.join(os.path.dirname(path), f".{os.path.basename(path)}", k)), v
        )
        for k, v in json.load(open(path, "r")).items()
    }


# from gdsfactory import LAYER_VIEWS

tol = 0.001


def get(c, i):
    try:
        return c[i]
    except:
        try:
            return getattr(c, i)
        except:
            return None


def arange(a, b, d):
    ret = np.linspace(a, b, round((b - a) / (d)) + 1).tolist()
    return ret


def trim(x, dx):
    return round(x / dx) * dx


def extend(endpoints, wm):
    v = endpoints[1] - endpoints[0]
    v = v / np.linalg.norm(v)
    return [(endpoints[0] - wm * v).tolist(), (endpoints[1] + wm * v).tolist()]


def portsides(c):
    ports = c.ports
    bbox = c.bbox_np()
    res = [[], [], [], []]
    xmin0, ymin0 = bbox[0]
    xmax0, ymax0 = bbox[1]
    for p in ports:
        x, y = np.array(p.center) / 1e0

        if abs(x - xmin0) < tol:
            res[2].append(p.name)
        if abs(x - xmax0) < tol:
            res[0].append(p.name)
        if abs(y - ymin0) < tol:
            res[3].append(p.name)
        if abs(y - ymax0) < tol:
            res[1].append(p.name)
    return res


def add_bbox(c, layer, nonport_margin=0):  # , dx=None):
    bbox = c.bbox_np()
    xmin0, ymin0 = bbox[0]
    xmax0, ymax0 = bbox[1]
    l = xmax0 - xmin0
    w = ymax0 - ymin0

    # l = dx*np.ceil((xmax0-xmin0)/dx)
    # w = dx*np.ceil((ymax0-ymin0)/dx)

    # if dx is not None:
    #     if nonport_margin is None:
    #         nonport_margin = dx
    # if nonport_margin is None:
    #     nonport_margin = 0
    margin = nonport_margin
    xmin, ymin, xmax, ymax = (
        xmin0 - margin,
        ymin0 - margin,
        xmin0 + l + margin,
        ymin0 + w + margin,
    )

    for p in c.ports:
        # p = c.ports[k]
        x, y = np.array(p.center) / 1e0
        if abs(x - xmin0) < tol:
            xmin = x
        if abs(x - xmax0) < tol:
            xmax = x
        if abs(y - ymin0) < tol:
            ymin = y
        if abs(y - ymax0) < tol:
            ymax = y
    p = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
    _c = gf.Component()
    _c << c

    if type(layer[0]) is int:
        layer = [layer]
    for layer in layer:
        layer = tuple(layer)
        _c.add_polygon(p, layer=layer)
    for port in c.ports:
        _c.add_port(name=port.name, port=port)
    return _c

    # def pic2gds(fileName, sizeOfTheCell, layerNum=1, isDither=False, scale=1):
    main(fileName, sizeOfTheCell, layerNum, isDither, scale)
    return "image.bmp", "image.gds"


def finish(c, name):
    c.add_label(name, position=c.bbox_np()[1])


def normal_from_orientation(orientation):
    return [cos(orientation / 180 * pi), sin(orientation / 180 * pi)]


def generate_background_mesh(bounds, resolution=20, eps=1e-6):
    x_min, x_max, y_min, y_max, z_min, z_max = bounds
    grid_x, grid_y, grid_z = np.meshgrid(
        np.linspace(x_min - eps, x_max + eps, resolution),
        np.linspace(y_min - eps, y_max + eps, resolution),
        np.linspace(z_min - eps, z_max + eps, resolution),
        indexing="ij",
    )
    return pv.StructuredGrid(grid_x, grid_y, grid_z).triangulate()


def sizing_function(
    points, focus_point=np.array([0, 0, 0]), max_size=1.0, min_size=0.1
):
    distances = np.linalg.norm(points - focus_point, axis=1)
    return np.clip(max_size - distances, min_size, max_size)


def rectify(v):
    for i, x in enumerate(v):
        if abs(x) < 1e-4:
            v[i] = 0
    v /= np.linalg.norm(v)
    return v


def section_mesh(mesheps, center, frame, start, stop, bg):
    N = len(center)
    center = np.array(center) - np.array(frame[:, 2][:N]) / 1e6
    bbox = [start[0], start[1], stop[0], stop[1]]
    bbox = shapely.geometry.box(*bbox)
    polyeps = []
    for mesh, eps, layer_name in mesheps:
        slice_2D = mesh.section(plane_origin=center, plane_normal=frame[:, 2])
        if slice_2D is not None:
            slice_2D.apply_transform(
                trimesh.transformations.translation_matrix(-np.array(center))
            )
            A = np.linalg.inv(frame)
            to_2D = np.zeros((4, 4))
            to_2D[:3, :3] = A
            to_2D[3, 3] = 1
            slice_2D, _ = slice_2D.to_planar(to_2D=to_2D)
            # slice_2D.show()

            # 4. Get the polygons from the slice
            polygons_full = slice_2D.polygons_full

            # Perform 2D intersections with a line
            # Assuming 'line' is a shapely LineString
            for polygon in polygons_full:
                # shapely.set_precision(polygon, 1e-4)
                intersection = polygon.intersection(bbox)
                if intersection and intersection.area > 1e-3:
                    polyeps.append((intersection, eps, layer_name))
    polyeps.append((bbox, bg, ""))
    # print(polyeps)
    return polyeps


def material_voxelate(c, zmin, zmax, layers, layer_stack, materials_library, path):
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)
    stacks = sum(
        [
            [
                [v.mesh_order, v.material, tuple(layer), k, v.info, v.zmin, v.thickness]
                for k, v in get_layers(layer_stack, layer, withkey=True)
            ]
            for layer in layers
        ],
        [],
    )
    stacks = sorted(stacks, key=lambda x: x[0])
    layer_stack_info = dict()
    # raise NotImplementedError("This is a stub")
    lb, ub = c.bbox_np()
    # bbox = [[**lb, zmin], [**ub, zmax]]
    bbox = [[lb[0], lb[1], zmin], [ub[0], ub[1], zmax]]
    layers = [x[2] for x in stacks]

    i = 1
    polygons_by_layer = c.get_polygons_points(by="tuple", merge=False)
    for stack in stacks:
        order = stack[0]
        m = stack[1]
        l1, l2 = layer = stack[2]
        k = stack[3]
        zmin = stack[5]
        thickness = stack[6]

        d = copy.deepcopy(get(layer_stack, "layers")[k])
        if d.zmin <= zmax and d.bounds[1] >= zmin:
            polys = polygons_by_layer[layer]
            for poly in polys:
                mesh = trimesh.creation.extrude_polygon(
                    shapely.geometry.Polygon(poly),
                    height=thickness,
                    transform=[
                        [1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, zmin],
                        [0, 0, 0, 1],
                    ],
                )
                OBJ = os.path.join(path, f"{i}#{m}#{k}#unnamed{i}1.obj")
                i += 1
                # print(mesh.bounds)
                mesh = mesh.slice_plane([0, 0, zmin], [0, 0, 1])
                mesh = mesh.slice_plane([0, 0, zmax], [0, 0, -1])
                # print(mesh.bounds)
                trimesh.exchange.export.export_mesh(mesh, OBJ, "obj")

            layer_stack_info[k] = {
                "layer": (l1, l2),
                "zmin": d.zmin,
                "thickness": d.thickness,
                # "material": matname(m),
                "mesh_order": stack[0],
                # "origin": origin,
            }
    return layer_stack_info


from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import box
from shapely.ops import clip_by_rect
from skfem.io.meshio import from_meshio
from tqdm import tqdm

from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict
from skfem import Basis, ElementTriP0, ElementVector, ElementDG, ElementTriP1
import rasterio.features
import EMpy


def atcentroid(a):
    # for i in a.ndim:
    a = (a[0:-1, :] + a[1:, :]) / 2
    a = (a[:, 0:-1] + a[:, 1:]) / 2
    return a


def epsilon_from_polyeps(polyeps, background_eps, start, stop, dx, dy):
    L = stop[0] - start[0]
    W = stop[1] - start[1]
    m = int(L / dx)
    n = int(W / dy)

    epsilon = np.zeros((m, n)) + background_eps
    polyeps.reverse()
    for poly, eps, _ in polyeps:
        if not isPEC(eps):
            poly = shapely.affinity.translate(poly, xoff=-start[0], yoff=-start[1])
            poly = shapely.affinity.scale(
                poly, xfact=1 / dx, yfact=1 / dy, origin=(0, 0)
            )
            poly = clip_by_rect(poly, 0, 0, m, n)
            mask = rasterio.features.rasterize([poly], out_shape=epsilon.T.shape)
            mask = mask.T
            epsilon *= 1 - mask
            epsilon += mask * eps
    polyeps.reverse()
    return epsilon


def solvemodes(polyeps, background_eps, start, stop, wavelength, num_modes, dx, dy):
    L = stop[0] - start[0]
    W = stop[1] - start[1]
    m = int(L / dx)
    n = int(W / dy)

    epsilon = np.zeros((m - 1, n - 1)) + background_eps
    polyeps.reverse()
    for poly, eps, _ in polyeps:
        poly = shapely.affinity.translate(poly, xoff=-start[0], yoff=-start[1])
        poly = shapely.affinity.scale(poly, xfact=1 / dx, yfact=1 / dy, origin=(0, 0))
        poly = clip_by_rect(poly, 0.5, 0.5, m - 0.5, n - 0.5)
        mask = rasterio.features.rasterize([poly], out_shape=epsilon.T.shape)
        mask = mask.T
        epsilon *= 1 - mask
        epsilon += mask * eps
    polyeps.reverse()

    # x = np.linspace(0, L, m)
    # y = np.linspace(0, W, n)
    x = np.linspace(dx / 2, L - dx / 2, m)
    y = np.linspace(dy / 2, W - dy / 2, n)
    # plt.matshow(epsilon)
    # plt.colorbar()  # Add a colorbar to show the mapping
    # plt.show()

    # print(start, stop)

    def ϵfunc(x_, y_):
        return epsilon

    tol = 1e-6
    solver = EMpy.modesolvers.FD.VFDModeSolver(wavelength, x, y, ϵfunc, "0000").solve(
        num_modes, tol
    )
    modes = solver.modes
    # modes = sorted(solver.modes, key=lambda x: -np.abs(x.neff))

    for mode in modes:
        fig = pylab.figure()

        fig.add_subplot(2, 3, 1)
        Ex = np.transpose(mode.get_field("Ex", x, y))
        pylab.contourf(x, y, abs(Ex), 25)
        pylab.title("Ex")

        fig.add_subplot(2, 3, 2)
        Ey = np.transpose(mode.get_field("Ey", x, y))
        pylab.contourf(x, y, abs(Ey), 25)
        pylab.title("Ey")

        fig.add_subplot(2, 3, 3)
        Ez = np.transpose(mode.get_field("Ez", x, y))
        pylab.contourf(x, y, abs(Ez), 25)
        pylab.title("Ez")

        fig.add_subplot(2, 3, 4)
        Hx = np.transpose(mode.get_field("Hx", x, y))
        pylab.contourf(x, y, abs(Hx), 25)
        pylab.title("Hx")

        fig.add_subplot(2, 3, 5)
        Hy = np.transpose(mode.get_field("Hy", x, y))
        pylab.contourf(x, y, abs(Hy), 25)
        pylab.title("Hy")

        fig.add_subplot(2, 3, 6)
        Hz = np.transpose(mode.get_field("Hz", x, y))
        pylab.contourf(x, y, abs(Hz), 25)
        pylab.title("Hz")

        pylab.show()

    neffs = [np.real(m.neff) for m in modes]
    modes = [
        # {k: m.get_field(k, x, y).T for k in ["Ex", "Ey", "Ez", "Hx", "Hy", "Hz"]}
        {
            k: m.get_field(k, x, y)
            for k in [
                "Ex",
                "Ey",
                "Hx",
                "Hy",
            ]
        }
        for m in modes
    ]
    # for i, mode in enumerate(modes):
    #     np.savez(os.path.join(path, f"{name}_mode_{i}.npz"), **modes[i])

    return modes


def solvemodes_femwell(
    polyeps,
    start,
    stop,
    wavelength,
    num_modes,
    dx,
    dy,
    metallic_boundaries,
    nmetals=3452,
):
    print("Solving port modes with FEM...")
    xmin, ymin = start
    xmax, ymax = stop
    L = xmax - xmin
    W = ymax - ymin

    polygons = OrderedDict()
    epsilons = OrderedDict()
    _metallic_boundaries = []
    i = 0
    for x in metallic_boundaries:
        found = True
        if x == "x+":
            p = shapely.LineString([(xmax, ymin), (xmax, ymax)])
        elif x == "x-":
            p = shapely.LineString([(xmin, ymin), (xmin, ymax)])
        elif x == "y+":
            p = shapely.LineString([(xmin, ymax), (xmax, ymax)])
        elif x == "-y":
            p = shapely.LineString([(xmin, ymin), (xmax, ymin)])
        else:
            found = False
        if found:
            k = f"b{i}"
            i += 1
            _metallic_boundaries.append(k)
            polygons[k] = p

    i = 0
    j = 0
    for poly, eps, layer_name in polyeps:
        if layer_name in metallic_boundaries:
            # if j < nmetals:
            #     j += 1
            i += 1
            k = f"p{i}"

            _metallic_boundaries.append(k)
            # if type(poly) is shapely.LineString:
            #     # polygons[k] = poly
            #     0
            # else:
            l = list(poly.exterior.coords)
            polygons[k] = shapely.simplify(
                shapely.LineString(l), tolerance=0.25 * math.sqrt(dx * dx + dy * dy)
            )
            #     # v = shapely.LinearRing(l)
        if isPEC(eps):
            0
        else:
            i += 1
            k = f"p{i}"
            polygons[k] = poly
            epsilons[k] = eps

    resolutions = {
        k: {
            "resolution": dx,
            "distance": wavelength,
        }
        for k in epsilons
    }

    for key in polygons.keys():
        polygons[key] = shapely.set_precision(polygons[key], 1e-4)

    mesh = from_meshio(
        mesh_from_OrderedDict(polygons, resolutions, default_resolution_max=wavelength)
    )

    basis0 = Basis(mesh, ElementTriP0())
    epsilon = basis0.zeros()
    for subdomain in reversed(epsilons.keys()):
        epsilon[basis0.get_dofs(elements=subdomain)] = epsilons[subdomain]

    modes = compute_modes(
        basis0,
        epsilon,
        wavelength=wavelength,
        num_modes=num_modes,
        metallic_boundaries=_metallic_boundaries,
    )
    for i, mode in enumerate(modes):
        mode.show("E", part="real", colorbar=True, title=f"Mode {i}")
        # mode.show("E", part="imag", colorbar=True, title=f"Mode {i}")
        mode.show("H", part="real", colorbar=True, title=f"Mode {i}")
        # mode.show("H", part="imag", colorbar=True, title=f"Mode {i}")

    basis = modes[0].basis
    basis_fix = basis.with_element(ElementVector(ElementDG(ElementTriP1())))

    grid_x, grid_y = np.meshgrid(
        np.linspace(
            xmin + dx / 2, xmax - dx / 2, round((xmax - xmin) / dx), dtype=np.float32
        ),
        np.linspace(
            ymin + dy / 2, ymax - dy / 2, round((ymax - ymin) / dy), dtype=np.float32
        ),
    )
    coordinates = np.array([grid_x.flatten(), grid_y.flatten()])
    shape = grid_x.shape

    r = []
    for mode in modes:
        (et, et_basis), (ez, ez_basis) = basis.split(mode.E)
        (et_x, et_x_basis), (et_y, et_y_basis) = basis_fix.split(
            basis_fix.project(et_basis.interpolate(et))
        )
        E = np.array(
            (
                et_x_basis.interpolator(et_x)(coordinates),
                et_y_basis.interpolator(et_y)(coordinates),
                ez_basis.interpolator(ez)(coordinates),
            )
        ).T

        (ht, ht_basis), (hz, hz_basis) = basis.split(mode.H)
        (ht_x, ht_x_basis), (ht_y, ht_y_basis) = basis_fix.split(
            basis_fix.project(ht_basis.interpolate(ht))
        )
        H = np.array(
            (
                ht_x_basis.interpolator(ht_x)(coordinates),
                ht_y_basis.interpolator(ht_y)(coordinates),
                hz_basis.interpolator(hz)(coordinates),
            )
        ).T

        # plt.imshow(E[:, 1].reshape(shape).real)
        # plt.show()
        d = {
            "Ex": E[:, 0],
            "Ey": E[:, 1],
            "Ez": E[:, 2],
            "Hx": H[:, 0] * 377,
            "Hy": H[:, 1] * 377,
            "Hz": H[:, 2] * 377,
        }
        d = {k: v.reshape(shape).T for k, v in d.items()}
        r.append(d)

    return r


def get_layers(layer_stack, layer, withkey=False):
    r = []
    d = get(layer_stack, "layers").items()

    for k, x in d:
        l = get(x, "layer")
        if l is not None:
            t = get(l, "layer")
            if t is not None and tuple(t) == tuple(layer):
                if withkey:
                    x = k, x
                r.append(x)
    if r:
        return r

    for k, x in d:
        l = get(x, "derived_layer")
        if l is not None:
            t = get(l, "layer")
            if t is not None and tuple(t) == tuple(layer):
                if withkey:
                    x = k, x
                r.append(x)
    return r


def wavelength_range(center, bandwidth, length=3):
    f1 = 1 / (center + bandwidth / 2)
    f2 = 1 / (center - bandwidth / 2)
    hw = (f2 - f1) / 2
    f1 = 1 / center - hw
    f2 = 1 / center + hw
    return sorted([1 / x for x in np.linspace(f1, f2, length).tolist()])


def wrap(wavelengths):
    if isinstance(wavelengths, float) or isinstance(wavelengths, int):
        wavelengths = [[wavelengths]]
    elif isinstance(wavelengths[0], float) or isinstance(wavelengths[0], int):
        wavelengths = [wavelengths]
    return wavelengths


def save_problem(prob, path):
    path = os.path.abspath(path)

    path = prob["path"]
    if not os.path.exists(path):
        os.makedirs(path)
        #   compiling julia code...
        #   """)
    prob_path = os.path.join(path, "problem.json")
    writejsonnp(prob_path, prob)
    path = os.path.abspath(path)
    print("using simulation folder", path)


def load_prob(path):
    path = os.path.abspath(path)
    print(f"loading problem from {path}")
    return json.loads(open(os.path.join(path, "problem.json"), "rb").read())


def create_gif(image_path, output_path, duration):
    """
    Creates a GIF from a list of image paths.

    Args:
        image_paths: A list of file paths to the images.
        output_path: The output path for the generated GIF.
        duration: The duration of each frame in milliseconds (default: 200).
    """
    image_paths = os.listdir(image_path)
    image_paths = sorted(image_paths, key=lambda x: float(x[0:-4]))
    frames = [PILImage.open(os.path.join(image_path, f)) for f in image_paths]

    # Ensure all frames have the same palette if necessary
    for i in range(len(frames)):
        if frames[i].mode != "RGB":
            frames[i] = frames[i].convert("RGB")

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,  # 0 means infinite loop
    )


def make_movie(path, fps=5, frames_folder=None, video_name=None):
    # shutil.rmtree(MOVIE, ignore_errors=True)
    # GIF = os.path.join(path, "sim.gif")
    # create_gif(FRAMES, GIF, duration)
    # return Image(open(GIF, "rb").read())
    if frames_folder is None:
        frames_folder = os.path.join(path, "frames")
    if video_name is None:
        video_name = os.path.join(path, "simulation.mp4")

    images = [
        img
        for img in os.listdir(frames_folder)
        if img.endswith((".jpg", ".jpeg", ".png"))
    ]
    try:
        images = sorted(images, key=lambda x: float(x[0:-4]))
    except:
        images = sorted(images)

    # print("Images:", images)

    # Set frame from the first image
    frame = cv2.imread(os.path.join(frames_folder, images[0]))
    height, width, layers = frame.shape

    # Video writer to create .avi file
    video = cv2.VideoWriter(
        video_name, cv2.VideoWriter_fourcc(*"DIVX"), fps, (width, height)
    )

    # Appending images to video
    for image in images:
        video.write(cv2.imread(os.path.join(frames_folder, image)))

    # Release the video file
    video.release()
    cv2.destroyAllWindows()
    print(f"Video generated successfully at {video_name}!")
    return video


def make_top_movie(path, **kwargs):
    FRAMES = os.path.join(path, "temp", "frames")
    os.makedirs(FRAMES, exist_ok=True)
    for d in os.listdir(os.path.join(path, "checkpoints")):
        shutil.copy(
            os.path.join(path, "checkpoints", d, "peak.png"),
            os.path.join(FRAMES, f"{d}_peak.png"),
        )
    make_movie(
        path, frames_folder=FRAMES, video_name=os.path.join(path, "opt.mp4"), **kwargs
    )


def make_design_gds(path, prob=None):
    if prob is None:
        prob = load_prob(path)
    for fn in os.listdir(path):
        if fn.endswith(".npy") and fn.startswith("design"):
            a = np.load(os.path.join(path, fn))
            c = gf.read.from_np(a, prob["pixel_size"] * 1e3, threshold=0.5)
            c.write_gds(os.path.join(path, f"{fn[:-4]}.gds"))

            a = np.uint8(a) * 255  # Convert to uint8
            image = PILImage.fromarray(a)  # Convert to uint8 if needed
            image.save(os.path.join(path, f"{fn[:-4]}.png"))
    # CKPT = os.path.join(path, "checkpoints")
    # if os.path.exists(CKPT):
    #     for d in os.listdir(CKPT):
    #         make_design_gds(os.path.join(CKPT, d), prob)


def port_name(port):
    s = str(port).split("@")[0]
    if s[0] in ("o", "e"):
        return s
    return f"o{s}"


def port_number(port):
    s = str(port).split("@")[0]
    if s[0] in ("o", "e"):
        s = s[1:]
    return int(s)


def mode_number(port):
    l = str(port).split("@")
    return 0 if len(l) == 1 else int(l[1])


def unpack_sparam_key(k):
    o, i = k.split(",")
    po, pi = port_name(o), port_name(i)
    mo, mi = mode_number(o), mode_number(i)
    return po, mo, pi, mi


def long_sparam_key(k):
    po, mo, pi, mi = unpack_sparam_key(k)
    return f"{po}@{mo},{pi}@{mi}"


def query(sol, q):
    t = q[0]
    q = q[1:]
    q2, q1 = q.split(",")
    er = 'For S params you need to specify modes like "So1@0,o2@0". Alternatively you can query T params of total flux like "T2,1"'
    if "@" in q1:
        y1 = sol["waves"][f"{q1}-"]
    else:
        if q1[0] in "0123456789":
            q1 = f"o{q1}"
        y1 = sol["flux"][f"{q1}-"]
    if "@" in q2:
        y2 = sol["waves"][f"{q2}+"]
    else:
        if q2[0] in "0123456789":
            q2 = f"o{q2}"
        y2 = sol["flux"][f"{q2}+"]

    if t == "S":
        if "@" not in q1 or "@" not in q2:
            raise ValueError(er)
        return y2 / y1
    elif t == "T":
        if "@" in q1:
            y1 = np.vectorize(lambda x: abs(x) ** 2)(y1)
        if "@" in q2:
            y2 = np.vectorize(lambda x: abs(x) ** 2)(y2)
        return y2 / y1


def convert_frequency_wavelength(f, w1f, bw=None):
    if bw:
        w2 = w1f / (f - bw / 2)
        w1 = w1f / (f + bw / 2)
        bw = w2 - w1
        w = (w1 + w2) / 2
        return w, bw
    w = w1f / f
    return w, None
