# Copyright 2025 The EasyDeL/eFormer Author @erfanzar (Erfan Zare Chavoshi).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import typing as tp

import jax
import numpy as np
from jax.sharding import Mesh, PartitionSpec


class MeshPartitionHelper:
    def __init__(self, mesh: Mesh):
        self.mesh = mesh
        self.axis_sizes = dict(zip(self.mesh.axis_names, self.mesh.devices.shape, strict=False))

    def analyze_pytree(self, pytree: tp.Any) -> dict[tuple[int, ...], PartitionSpec]:
        """Analyze pytree and suggest partitioning for each unique array shape."""
        shapes_dict = {}

        def collect_shapes(x):
            if hasattr(x, "shape"):
                shapes_dict[x.shape] = None
            return x

        jax.tree_util.tree_map(collect_shapes, pytree)

        for shape in shapes_dict.keys():
            shapes_dict[shape] = self._suggest_methods(shape)

        return shapes_dict

    def _suggest_methods(self, shape: tuple[int, ...]) -> list[tuple]:
        """Suggest sharding methods based on array shape and mesh.
        Now returns tuples of methods for combined sharding.
        """
        methods = []
        dims = len(shape)

        if (
            dims > 1
            and "fsdp" in self.axis_sizes
            and "sp" in self.axis_sizes
            and shape[0] * shape[1] >= self.axis_sizes["fsdp"] * self.axis_sizes["sp"]
        ):
            methods.append(("fsdp", "sp"))

        if dims > 0 and "dp" in self.axis_sizes:
            methods.append(("dp",))

        if dims > 1 and "sp" in self.axis_sizes and ("fsdp", "sp") not in methods:
            methods.append(("sp",))

        if "tp" in self.axis_sizes:
            methods.append(("tp",))

        if "fsdp" in self.axis_sizes and all("fsdp" not in m for m in methods):
            methods.append(("fsdp",))

        return methods

    def create_partition_spec(
        self,
        array_shape: tuple[int, ...],
        methods: list[tuple],
        min_shard_size: int = 1024,
    ) -> PartitionSpec:
        if not array_shape:
            return PartitionSpec()

        dims = len(array_shape)
        spec = [None] * dims

        total_elements = np.prod(array_shape)
        total_devices = int(np.prod(self.mesh.devices.shape))
        min_elements_per_device = max(min_shard_size, total_elements // (total_devices * 2))

        for method_tuple in methods:
            combined_mesh_size = np.prod([self.axis_sizes[m] for m in method_tuple if m in self.axis_sizes])

            if len(method_tuple) == 1:
                method = method_tuple[0]
                for dim, dim_size in enumerate(array_shape):
                    if (
                        dim_size >= min_elements_per_device
                        and dim_size % self.axis_sizes[method] == 0
                        and spec[dim] is None
                    ):
                        spec[dim] = method
                        break
            elif len(method_tuple) == 2:
                if (
                    dims >= 2
                    and (array_shape[0] * array_shape[1]) >= combined_mesh_size
                    and (array_shape[0] * array_shape[1]) % combined_mesh_size == 0
                ):
                    if (
                        array_shape[0] >= self.axis_sizes[method_tuple[0]]
                        and array_shape[1] >= self.axis_sizes[method_tuple[1]]
                        and spec[0] is None
                        and spec[1] is None
                    ):
                        spec[0], spec[1] = method_tuple
                        break
                elif (
                    dims >= 2
                    and array_shape[0] >= combined_mesh_size
                    and array_shape[0] % combined_mesh_size == 0
                    and spec[0] is None
                ):
                    spec[0] = method_tuple
                    break

        print(spec)
        if all(s is None for s in spec):
            for method_tuple in methods:
                if len(method_tuple) == 1:
                    method = method_tuple[0]
                    for dim, dim_size in enumerate(array_shape):
                        if dim_size >= min_shard_size and dim_size % self.axis_sizes[method] == 0 and spec[dim] is None:
                            spec[dim] = method
                            break
                elif len(method_tuple) == 2:
                    if method_tuple == ("fsdp", "sp"):
                        if spec[0] is None and spec[1] is None:
                            spec[0], spec[1] = method_tuple
                            break
                        elif spec[0] is None:
                            spec[0] = method_tuple
                            break

        return PartitionSpec(*spec)

    def shard_array(self, array, partition_spec):
        return jax.device_put(array, jax.sharding.NamedSharding(self.mesh, partition_spec))

    def auto_shard_pytree(self, pytree: tp.Any, min_shard_size: int = 1024):
        """Automatically shard entire pytree based on analysis."""
        shape_specs = self.analyze_pytree(pytree)

        def shard_leaf(x):
            if hasattr(x, "shape"):
                methods = shape_specs[x.shape]
                spec = self.create_partition_spec(x.shape, methods, min_shard_size)
                return self.shard_array(x, spec)
            return x

        return jax.tree_util.tree_map(shard_leaf, pytree)
