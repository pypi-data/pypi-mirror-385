import copy as libcopy
import json
import pathlib
import struct
import warnings
import zlib
from collections.abc import Sequence
from typing import Any, ClassVar, Literal, Optional, Union

import numpy
import pydantic
import tidy3d
from tidy3d.plugins.mode import ModeSolver

from . import tidy3d_model
from . import typing as pft
from .cache import _cache_path, _tidy3d_model_cache, cache_s_matrix
from .extension import (
    Z_MAX,
    Component,
    FiberPort,
    GaussianPort,
    Model,
    Port,
    SMatrix,
    Technology,
    _content_repr,
    _from_bytes,
    config,
    frequency_classification,
    register_model_class,
    snap_to_grid,
)
from .parametric_utils import _filename_cleanup, _safe_hash
from .utils import C_0


class _EMEModelRunner:
    def __init__(
        self,
        simulation: tidy3d.EMESimulation,
        ports: dict[str, Union[Port, FiberPort]],
        port_groups: tuple[tuple[str], tuple[str]],
        mesh_refinement: Union[tidy3d.components.grid.grid_spec.GridSpec1d, float],
        technology: Technology,
        folder_name: str,
        data_path: str,
        cost_estimation: bool,
        verbose: bool,
    ):
        key = (tidy3d_model._tidy3d_to_bytes(simulation), folder_name, data_path)
        runner = _tidy3d_model_cache[key]
        if runner is None or runner.status["message"] == "error":
            task_name = "EME" if "EME" not in ports else ("EME " + " ".join(ports))
            runner = tidy3d_model._simulation_runner(
                simulation=simulation,
                task_name=task_name,
                remote_path=folder_name,
                data_path=data_path,
                cost_estimation=cost_estimation,
                verbose=verbose,
            )
            _tidy3d_model_cache[key] = runner
        self.runners = {0: runner}

        # Port modes for decomposition
        filter_polarization = False
        for name in port_groups[0] + port_groups[1]:
            self.runners[name] = tidy3d_model._ModeSolverRunner(
                port=ports[name],
                frequencies=simulation.freqs,
                mesh_refinement=mesh_refinement,
                technology=technology,
                center_in_origin=False,
                verbose=verbose,
            )
            filter_polarization = filter_polarization or (ports[name].spec.polarization != "")

        self.ports = ports
        self.port_groups = port_groups
        self._s_matrix = None

        # If the model uses any symmetry or polarization filter, it will impact the mode numbering
        # of the ports. We need to remap port modes from the symmetry-applied to the full version.
        self.mode_remap = simulation.symmetry != (0, 0, 0) or filter_polarization
        if self.mode_remap:
            classification = frequency_classification(simulation.freqs)
            use_angle_rotation = tidy3d_model._isotropic_uniform(technology, classification)
            sim_kwargs = simulation.dict()
            for kw in (
                "attrs",
                "type",
                "eme_grid_spec",
                "axis",
                "constraint",
                "freqs",
                "normalize",
                "port_offsets",
                "store_port_modes",
                "sweep_spec",
                "symmetry",
            ):
                del sim_kwargs[kw]
            full_sim = tidy3d.Simulation(run_time=1e-12, **sim_kwargs)
            for name in port_groups[0] + port_groups[1]:
                monitor = ports[name].to_tidy3d_monitor(
                    simulation.freqs, name="M", use_angle_rotation=use_angle_rotation
                )
                mode_solver = ModeSolver(
                    simulation=full_sim,
                    plane=monitor.bounding_box,
                    mode_spec=monitor.mode_spec.copy(update={"filter_pol": None}),
                    freqs=simulation.freqs,
                    direction=monitor.store_fields_direction,
                )
                self.runners[(name, "full")] = tidy3d_model._simulation_runner(
                    simulation=mode_solver,
                    task_name=name + "-no_sym",
                    remote_path=folder_name,
                    data_path=data_path,
                    cost_estimation=cost_estimation,
                    verbose=verbose,
                )

    @property
    def status(self) -> dict[str, Any]:
        """Monitor S matrix computation progress."""
        all_stat = [runner.status for runner in self.runners.values()]
        if all(s["message"] == "success" for s in all_stat):
            message = "success"
            progress = 100
        elif any(s["message"] == "error" for s in all_stat):
            message = "error"
            progress = 100
        else:
            message = "running"
            progress = sum(
                100 if s["message"] == "success" else s["progress"] for s in all_stat
            ) / len(all_stat)
        return {"progress": progress, "message": message}

    @property
    def s_matrix(self) -> SMatrix:
        """Get the model S matrix."""
        if self._s_matrix is None:
            # Original S matrix in EME basis
            eme_data = self.runners[0].data
            eme_modes = eme_data.port_modes_tuple
            eme_modes = (eme_modes[0], eme_modes[1].time_reversed_copy)

            num_eme_modes = (
                eme_data.smatrix.S11.coords["mode_index_in"].size,
                eme_data.smatrix.S22.coords["mode_index_in"].size,
            )
            num_freqs = len(eme_data.simulation.freqs)
            s = numpy.empty((num_freqs, sum(num_eme_modes), sum(num_eme_modes)), dtype=complex)
            s[:, : num_eme_modes[0], : num_eme_modes[0]] = (
                eme_data.smatrix.S11.isel(sweep_index=0, drop=True)
                .transpose("f", "mode_index_out", "mode_index_in")
                .values
            )
            s[:, : num_eme_modes[0], num_eme_modes[0] :] = (
                eme_data.smatrix.S12.isel(sweep_index=0, drop=True)
                .transpose("f", "mode_index_out", "mode_index_in")
                .values
            )
            s[:, num_eme_modes[0] :, : num_eme_modes[0]] = (
                eme_data.smatrix.S21.isel(sweep_index=0, drop=True)
                .transpose("f", "mode_index_out", "mode_index_in")
                .values
            )
            s[:, num_eme_modes[0] :, num_eme_modes[0] :] = (
                eme_data.smatrix.S22.isel(sweep_index=0, drop=True)
                .transpose("f", "mode_index_out", "mode_index_in")
                .values
            )

            # Port mode transformation matrix
            # M_ij = <e_i, e_j'> / <e_i, e_i>
            # S' = pinv(M) × S × M
            port_names = self.port_groups[0] + self.port_groups[1]
            port_num_modes = {
                name: self.ports[name].num_modes + self.ports[name].added_solver_modes
                for name in port_names
            }
            sum_modes = sum(port_num_modes.values())
            m = numpy.zeros((num_freqs, sum(num_eme_modes), sum_modes), dtype=complex)
            mode_index = 0
            for i in range(2):
                norms = eme_modes[i].dot(eme_modes[i], conjugate=False)
                for name in self.port_groups[i]:
                    num_modes = port_num_modes[name]
                    port_data = self.runners[name].data
                    projection = eme_modes[i].outer_dot(port_data, conjugate=False)
                    m_block = (
                        projection.transpose("mode_index_1", "mode_index_0", "f").values
                        / norms.transpose("mode_index", "f").values
                    )
                    # Mode data from EME comes with max(num_eme_modes) modes
                    m_block = m_block[:, : num_eme_modes[i], :].T
                    if i == 0:
                        m[:, : num_eme_modes[0], mode_index : mode_index + num_modes] = m_block
                    else:
                        m[:, num_eme_modes[0] :, mode_index : mode_index + num_modes] = m_block
                    mode_index += num_modes
            s = numpy.linalg.pinv(m) @ s @ m

            elements = {}
            j = 0
            for src in port_names:
                for src_mode in range(port_num_modes[src]):
                    i = 0
                    for dst in port_names:
                        for dst_mode in range(port_num_modes[dst]):
                            if (
                                src_mode < self.ports[src].num_modes
                                and dst_mode < self.ports[dst].num_modes
                            ):
                                elements[f"{src}@{src_mode}", f"{dst}@{dst_mode}"] = s[:, i, j]
                            i += 1
                    j += 1

            # If symmetry or polarization filter was used, calculate and apply mode mapping
            if self.mode_remap:
                data_sym = {
                    name: self.runners[name].data
                    for name, port in self.ports.items()
                    if not isinstance(port, GaussianPort)
                }
                data_full = {
                    name: self.runners[(name, "full")].data
                    for name, port in self.ports.items()
                    if not isinstance(port, GaussianPort)
                }
                elements = tidy3d_model._mode_remap_from_symmetry(
                    elements, self.ports, data_sym, data_full
                )

            self._s_matrix = SMatrix(eme_data.simulation.freqs, elements, self.ports)

        return self._s_matrix


class EMEModel(Model):
    """S matrix model based on Eigenmode Expansion calculation.

    Args:
        eme_grid_spec: 1D grid in the that specifies the EME cells where
          mode solving is performed along the propagation direction.
        medium: Background medium. If ``None``, the technology default is
          used.
        symmetry: Component symmetries.
        monitors: Extra field monitors added to the simulation.
        structures: Additional structures included in the simulations.
        grid_spec: Simulation grid specification. A single float can be used
          to specify the ``min_steps_per_wvl`` for an auto grid.
        subpixel: Flag controlling subpixel averaging in the simulation
          grid or an instance of ``tidy3d.SubpixelSpec``.
        bounds: Bound overrides for the final simulation.
        constraint: Constraint for EME propagation. Possible values are
          ``"passive"`` and ``"unitary"``.
        simulation_updates: Dictionary of updates applied to the simulation
          generated by this model. See example in :class:`Tidy3DModel`.
        verbose: Control solver verbosity.

    If not set, the default values for the component simulations are defined
    based on the wavelengths used in the ``s_matrix`` call.
    """

    _data_cache: ClassVar[dict[bytes, pathlib.Path]] = {}

    def __init__(
        self,
        eme_grid_spec: pft.annotate(
            tidy3d.components.eme.grid.EMESubgridType, brand="Tidy3dEMEGridSpec"
        ),
        medium: Optional[pft.Medium] = None,
        symmetry: tidy3d_model._SymmetryType = (0, 0, 0),
        monitors: Sequence[tidy3d_model._MonitorType] = (),
        structures: Sequence[tidy3d.Structure] = (),
        grid_spec: Optional[Union[pft.PositiveFloat, tidy3d.GridSpec]] = None,
        subpixel: tidy3d_model._SubpixelType = True,
        bounds: tidy3d_model._BoundsType = ((None, None, None), (None, None, None)),
        constraint: Optional[Literal["passive", "unitary"]] = "passive",
        simulation_updates: dict[str, Any] = {},
        verbose: bool = True,
    ):
        super().__init__(
            eme_grid_spec=eme_grid_spec,
            medium=medium,
            symmetry=symmetry,
            monitors=monitors,
            structures=structures,
            grid_spec=grid_spec,
            subpixel=subpixel,
            bounds=bounds,
            constraint=constraint,
            simulation_updates=simulation_updates,
            verbose=verbose,
        )
        self.eme_grid_spec = eme_grid_spec
        self.medium = medium
        self.symmetry = symmetry
        self.monitors = monitors
        self.structures = structures
        self.grid_spec = grid_spec
        self.subpixel = subpixel
        self.bounds = bounds
        self.constraint = constraint
        self.simulation_updates = simulation_updates
        self.verbose = verbose

    def __copy__(self) -> "EMEModel":
        return EMEModel(
            self.eme_grid_spec,
            self.medium,
            self.symmetry,
            self.monitors,
            self.structures,
            self.grid_spec,
            self.subpixel,
            self.bounds,
            self.constraint,
            self.simulation_updates,
            self.verbose,
        )

    def __deepcopy__(self, memo: Optional[dict] = None) -> "EMEModel":
        return EMEModel(
            self.eme_grid_spec,
            self.medium,
            libcopy.deepcopy(self.symmetry),
            libcopy.deepcopy(self.monitors),
            libcopy.deepcopy(self.structures),
            self.grid_spec,
            self.subpixel,
            libcopy.deepcopy(self.bounds),
            self.constraint,
            libcopy.deepcopy(self.simulation_updates),
            self.verbose,
        )

    def __str__(self) -> str:
        return "EMEModel"

    def __repr__(self) -> str:
        return (
            f"EMEModel(eme_grid_spec={self.eme_grid_spec!r}, medium={self.medium!r}, "
            f"symmetry={self.symmetry!r}, monitors={self.monitors!r}, "
            f"structures={self.structures!r}, grid_spec={self.grid_spec!r}, "
            f"subpixel={self.subpixel!r}, bounds={self.bounds!r}, constraint={self.constraint!r}, "
            f"simulation_updates={self.simulation_updates!r}, verbose={self.verbose!r})"
        )

    def data_path_for(self, component: Component) -> pathlib.Path:
        return _cache_path(_safe_hash(component.name.encode("utf-8")))

    def data_file_for(self, component: Component) -> Optional[pathlib.Path]:
        result = EMEModel._data_cache.get(_content_repr(component))
        if not result:
            raise RuntimeError(
                "No data found in runtime cache. Please run the model for this component before "
                "trying to load the simulation data to populate the cache."
            )
        return result

    def simulation_data_for(self, component: Component) -> Optional[tidy3d.EMESimulationData]:
        """Return the EME simulation data for a given component."""
        data_file = self.data_file_for(component)
        if data_file.is_file():
            return tidy3d.EMESimulationData.from_file(str(data_file))
        return None

    @staticmethod
    def _group_ports(ports: dict[str, Port]) -> tuple[int, tuple[tuple[str], tuple[str]]]:
        port_groups = {}
        for name, port in ports.items():
            if isinstance(port, Port):
                fraction = port.input_direction % 90
                if fraction > 1e-12 and 90 - fraction > 1e-12:
                    raise RuntimeError(
                        f"Input direction of port '{name}' is not a multiple of 90°."
                    )
                direction = round(port.input_direction % 360) // 90
                coordinate = port.center[direction % 2]
                key = (coordinate, direction)
            elif isinstance(port, FiberPort):
                center, size, direction, *_ = port._axis_aligned_properties()
                axis = size.tolist().index(0)
                if axis > 1:
                    raise RuntimeError(f"Input direction of port '{name}' is not in the xy plane.")
                key = (center[axis], axis + (2 if direction == "-" else 0))
            else:
                warnings.warn(
                    f"EMEModel only works with Port and FiberPort instances. Port named '{name}' "
                    f"of type {type(port)} will be ignored.",
                    RuntimeWarning,
                    2,
                )
                continue
            port_groups[key] = (*port_groups.get(key, ()), name)

        if len(port_groups) == 1:
            key, group = next(iter(port_groups.items()))
            if key < 2:
                return (key[1], (group, ()))
            else:
                return (key[1] - 2, ((), group))

        if len(port_groups) == 2:
            key0, key1 = sorted(port_groups)
            if key1[1] - key0[1] == 2 and key0[0] < key1[0]:
                return (key0[1], (port_groups[key0], port_groups[key1]))

        raise RuntimeError(
            "Component ports need to be placed at 2 opposite sides, facing each other. Multiple "
            "ports on each side are allowed as long as they are aligned in the normal direction."
        )

    def get_simulation(
        self, component: Component, frequencies: Sequence[float]
    ) -> tuple[tidy3d.EMESimulation, tuple[tuple[str], tuple[str]]]:
        """Create an EME simulation for a component.

        Args:
            component: Instance of Component for calculation.
            frequencies: Sequence of frequencies for the simulation.

        Returns:
            EME simulation and 2 tuples with the names of the ports on each side of the domain.
        """
        frequencies = numpy.array(frequencies, dtype=float, ndmin=1)
        fmin = frequencies.min()
        fmax = frequencies.max()
        fmed = 0.5 * (fmin + fmax)
        max_wavelength = C_0 / fmin
        min_wavelength = C_0 / fmax

        classification = frequency_classification(frequencies)
        medium = (
            component.technology.get_background_medium(classification)
            if self.medium is None
            else self.medium
        )
        use_angle_rotation = tidy3d_model._isotropic_uniform(component.technology, classification)

        mesh_refinement = (
            config.default_mesh_refinement
            if self.grid_spec is None or isinstance(self.grid_spec, tidy3d.GridSpec)
            else self.grid_spec
        )

        grid_spec = (
            self.grid_spec
            if isinstance(self.grid_spec, tidy3d.GridSpec)
            else tidy3d.GridSpec.auto(
                wavelength=min_wavelength,
                min_steps_per_wvl=mesh_refinement,
                min_steps_per_sim_size=mesh_refinement,
            )
        )

        extrusion_tolerance = 0
        if isinstance(grid_spec.grid_z, tidy3d.AutoGrid):
            grid_lda = min_wavelength if grid_spec.wavelength is None else grid_spec.wavelength
            temp_scene = tidy3d.Scene(
                medium=medium,
                structures=[
                    tidy3d.Structure(
                        geometry=tidy3d.Box(size=(1, 1, 1)), medium=spec.get_medium(classification)
                    )
                    for spec in component.technology.extrusion_specs
                ],
            )
            _, eps_max = temp_scene.eps_bounds(fmed)
            extrusion_tolerance = grid_lda / (grid_spec.grid_z.min_steps_per_wvl * eps_max**0.5)
        elif isinstance(grid_spec.grid_z, tidy3d.UniformGrid):
            extrusion_tolerance = grid_spec.grid_z.dl
        elif isinstance(grid_spec.grid_z, tidy3d.CustomGrid) and len(grid_spec.grid_z.dl) > 0:
            extrusion_tolerance = min(grid_spec.grid_z.dl)

        (xmin, ymin), (xmax, ymax) = component.bounds()
        structures = [
            struct.to_tidy3d()
            for struct in component.extrude(
                0.5 * max_wavelength + max(xmax - xmin, ymax - ymin),
                extrusion_tolerance=extrusion_tolerance,
                classification=classification,
            )
        ]

        # Sort to improve caching, but don't reorder different media
        i = 0
        while i < len(structures):
            current_medium = structures[i].medium
            j = i + 1
            while j < len(structures) and structures[j].medium == current_medium:
                j += 1
            # Even if j == i + 1 we want to sort internal geometries
            structures[i:j] = (
                tidy3d.Structure(geometry=geometry, medium=current_medium)
                for geometry in sorted(
                    [tidy3d_model._inner_geometry_sort(s.geometry) for s in structures[i:j]],
                    key=tidy3d_model._geometry_key,
                )
            )
            i = j

        component_ports = component.select_ports(classification)
        port_structures = [
            structure
            for _, port in sorted(component_ports.items())
            if isinstance(port, FiberPort)
            for structure in port.to_tidy3d_structures()
        ]
        all_structures = structures + port_structures + list(self.structures)
        axis, port_groups = self._group_ports(component_ports)

        # Simulation bounds
        zmin = 1e30
        zmax = -1e30
        for name in port_groups[0] + port_groups[1]:
            monitor = component_ports[name].to_tidy3d_monitor(
                frequencies, name="M", use_angle_rotation=use_angle_rotation
            )
            xmin = min(xmin, monitor.bounds[0][0])
            ymin = min(ymin, monitor.bounds[0][1])
            zmin = min(zmin, monitor.bounds[0][2])
            xmax = max(xmax, monitor.bounds[1][0])
            ymax = max(ymax, monitor.bounds[1][1])
            zmax = max(zmax, monitor.bounds[1][2])
        for s in structures:
            for i in range(2):
                lim = s.geometry.bounds[i][2]
                if -Z_MAX <= lim <= Z_MAX:
                    zmin = min(zmin, lim)
                    zmax = max(zmax, lim)
        if zmin > zmax:
            raise RuntimeError("No valid extrusion elements present in the component.")

        bounds = numpy.array(((xmin, ymin, zmin), (xmax, ymax, zmax)))

        # Bounds override
        for i in range(3):
            if self.bounds[0][i] is not None:
                bounds[0, i] = self.bounds[0][i]
            if self.bounds[1][i] is not None:
                bounds[1, i] = self.bounds[1][i]

        port_offsets = []
        safe_margin = min_wavelength / 4
        for i in range(2):
            sign = 2 * i - 1
            if len(port_groups[i]) > 0:
                port_offset = sign * (
                    bounds[i][axis] - component_ports[port_groups[i][0]].center[axis]
                )
                if port_offset < safe_margin:
                    port_offset = safe_margin
                    bounds[i][axis] = (
                        component_ports[port_groups[i][0]].center[axis] + sign * safe_margin
                    )
            else:
                port_offset = 0
            port_offsets.append(port_offset)

        center = tuple(snap_to_grid(v) / 2 for v in bounds[0] + bounds[1])
        size = tuple(snap_to_grid(v) for v in bounds[1] - bounds[0])
        bounding_box = tidy3d.Box(center=center, size=size)

        eme_simulation = tidy3d.EMESimulation(
            freqs=frequencies,
            center=center,
            size=size,
            medium=medium,
            symmetry=self.symmetry,
            structures=[s for s in all_structures if bounding_box.intersects(s.geometry)],
            monitors=list(self.monitors),
            grid_spec=grid_spec,
            eme_grid_spec=self.eme_grid_spec,
            subpixel=self.subpixel,
            axis=axis,
            port_offsets=port_offsets,
            constraint=self.constraint,
        )

        for path, value in self.simulation_updates.items():
            eme_simulation = tidy3d_model._updated_tidy3d(eme_simulation, path.split("/"), value)

        return eme_simulation, port_groups

    @cache_s_matrix
    def start(
        self,
        component: Component,
        frequencies: Sequence[float],
        *,
        verbose: Optional[bool] = None,
        cost_estimation: bool = False,
        **kwargs: Any,
    ) -> _EMEModelRunner:
        """Start computing the S matrix response from a component.

        Args:
            component: Component from which to compute the S matrix.
            frequencies: Sequence of frequencies at which to perform the
              computation.
            verbose: If set, overrides the model's `verbose` attribute.
            cost_estimation: If set, simulations are uploaded, but not
              executed. S matrix will *not* be computed.
            **kwargs: Unused.

        Returns:
            Result object with attributes ``status`` and ``s_matrix``.

        Important:
            When using geometry symmetry, the mode numbering in ``inputs``
            is relative to the solver run *with the symmetry applied*, not
            the mode number presented in the final S matrix.
        """
        simulation, port_groups = self.get_simulation(component, frequencies)
        folder_name = _filename_cleanup(component.name)

        classification = frequency_classification(frequencies)
        component_ports = {
            name: port.copy(True) for name, port in component.select_ports(classification).items()
        }

        if verbose is None:
            verbose = self.verbose

        mesh_refinement = (
            config.default_mesh_refinement
            if self.grid_spec is None or isinstance(self.grid_spec, tidy3d.GridSpec)
            else self.grid_spec
        )

        if len(folder_name) == 0:
            folder_name = "default"
        result = _EMEModelRunner(
            simulation=simulation,
            ports=component_ports,
            port_groups=port_groups,
            mesh_refinement=mesh_refinement,
            technology=component.technology,
            folder_name=folder_name,
            data_path=self.data_path_for(component),
            cost_estimation=cost_estimation,
            verbose=verbose,
        )

        if isinstance(result.runners[0], tidy3d_model._Tidy3DTaskRunner):
            EMEModel._data_cache[_content_repr(component)] = result.runners[0].data_file()

        return result

    # Deprecated: kept for backwards compatibility
    @classmethod
    def from_bytes(cls, byte_repr: bytes) -> "EMEModel":
        """De-serialize this model."""
        version = byte_repr[0]
        if version == 1:
            obj = dict(_from_bytes(byte_repr[1:]))

        elif version == 0:
            n_size = struct.calcsize("<BL")
            n = struct.unpack("<L", byte_repr[1:n_size])[0]
            cursor = struct.calcsize("<BL" + n * "Q")
            lengths = struct.unpack("<" + n * "Q", byte_repr[n_size:cursor])

            obj = json.loads(byte_repr[cursor : cursor + lengths[0]].decode("utf-8"))
            cursor += lengths[0]

            models = [None] * (n - 1)
            for i, length in enumerate(lengths[1:]):
                models[i] = tidy3d_model._tidy3d_from_bytes(byte_repr[cursor : cursor + length])
                cursor += length

            if cursor != len(byte_repr):
                raise RuntimeError("Invalid byte representation for Tidy3DModel.")

            indices = obj.pop("_tidy3d_indices_")
            for name, (i, j) in indices.items():
                if j < 0:
                    obj[name] = models[i]
                else:
                    obj[name] = [models[m] for m in range(i, j)]

        # zlib-compressed json used before versioning
        elif version == 0x78:
            obj = json.loads(zlib.decompress(byte_repr).decode("utf-8"))
            obj = tidy3d_model._decode_arrays(obj)

            item = obj.get("eme_grid_spec")
            if isinstance(item, dict):
                obj["eme_grid_spec"] = pydantic.v1.parse_obj_as(
                    tidy3d.components.eme.grid.EMESubgridType, item, type_name=item["type"]
                )

            item = obj.get("medium")
            if isinstance(item, dict):
                obj["medium"] = pydantic.v1.parse_obj_as(
                    tidy3d.components.medium.MediumType3D, item, type_name=item["type"]
                )

            item = obj.get("grid_spec")
            if isinstance(item, dict):
                obj["grid_spec"] = pydantic.v1.parse_obj_as(
                    tidy3d.GridSpec, item, type_name=item["type"]
                )

            obj["monitors"] = [
                pydantic.v1.parse_obj_as(
                    tidy3d.components.monitor.MonitorType, mon, type_name=mon["type"]
                )
                for mon in obj.get("monitors", ())
            ]

            obj["structures"] = [
                pydantic.v1.parse_obj_as(tidy3d.Structure, s, type_name=s["type"])
                for s in obj.get("structures", ())
            ]

        return cls(**obj)


register_model_class(EMEModel)
