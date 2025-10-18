###########################################################################################
# Modified from ACEsuit/mace_descriptor
# Original Copyright (c) 2022 ACEsuit/mace_descriptor
# Licensed under the MIT License
###########################################################################################

import logging

# pylint: disable=wrong-import-position
import os
from glob import glob
from pathlib import Path
from typing import List, Union

os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"

import numpy as np
import torch
from ase.calculators.calculator import Calculator, all_changes
from e3nn import o3

from mace_descriptor import data
from mace_descriptor.data.atomic_data import get_data_loader

from mace_descriptor.tools import torch_geometric, torch_tools, utils
from mace_descriptor.tools.compile import prepare
from mace_descriptor.tools.scripts_utils import extract_model

try:
    import intel_extension_for_pytorch as ipex

    has_ipex = True
except ImportError:
    has_ipex = False


def get_model_dtype(model: torch.nn.Module) -> torch.dtype:
    """Get the dtype of the model"""
    mode_dtype = next(model.parameters()).dtype
    if mode_dtype == torch.float64:
        return "float64"
    if mode_dtype == torch.float32:
        return "float32"
    raise ValueError(f"Unknown dtype {mode_dtype}")


def extract_invariant(x: torch.Tensor, num_layers: int, num_features: int, l_max: int):
    out = []
    out.append(x[:, :num_features])
    for i in range(1, num_layers):
        out.append(x[:, i * (l_max + 1) ** 2 * num_features: (i * (l_max + 1) ** 2 + 1) * num_features,])
    return torch.cat(out, dim=-1)


class MACECalculator(Calculator):
    """MACE ASE Calculator
    args:
        model_paths: str, path to model or models if a committee is produced
                to make a committee use a wild card notation like mace_*.model
        device: str, device to run on (cuda or cpu or xpu)
        energy_units_to_eV: float, conversion factor from model energy units to eV
        length_units_to_A: float, conversion factor from model length units to Angstroms
        default_dtype: str, default dtype of model
        charges_key: str, Array field of atoms object where atomic charges are stored
        model_type: str, type of model to load
                    Options: [MACE, DipoleMACE, EnergyDipoleMACE]

    Dipoles are returned in units of Debye
    """

    def __init__(
            self,
            model_paths: Union[list, str, None] = None,
            models: Union[List[torch.nn.Module], torch.nn.Module, None] = None,
            device: str = "cpu",
            energy_units_to_eV: float = 1.0,
            length_units_to_A: float = 1.0,
            default_dtype="",
            charges_key="Qs",
            info_keys=None,
            arrays_keys=None,
            model_type="MACE",
            compile_mode=None,
            fullgraph=True,
            **kwargs,
    ):
        Calculator.__init__(self, **kwargs)
        if "model_path" in kwargs:
            deprecation_message = (
                "'model_path' argument is deprecated, please use 'model_paths'"
            )
            if model_paths is None:
                logging.warning(f"{deprecation_message} in the future.")
                model_paths = kwargs["model_path"]
            else:
                raise ValueError(
                    f"both 'model_path' and 'model_paths' given, {deprecation_message} only."
                )

        if (model_paths is None) == (models is None):
            raise ValueError(
                "Exactly one of 'model_paths' or 'models' must be provided"
            )

        self.results = {}
        if info_keys is None:
            info_keys = {"total_spin": "spin", "total_charge": "charge"}
        if arrays_keys is None:
            arrays_keys = {}
        self.info_keys = info_keys
        self.arrays_keys = arrays_keys

        self.model_type = model_type
        self.compute_atomic_stresses = False

        if model_type == "MACE":
            self.implemented_properties = [
                "energy",
                "free_energy",
                "node_energy",
                "forces",
                "stress",
            ]
            if kwargs.get("compute_atomic_stresses", False):
                self.implemented_properties.extend(["stresses", "virials"])
                self.compute_atomic_stresses = True
        elif model_type == "DipoleMACE":
            self.implemented_properties = ["dipole"]
        elif model_type == "DipolePolarizabilityMACE":
            self.implemented_properties = [
                "charges",
                "dipole",
                "polarizability",
                "polarizability_sh",
            ]
        elif model_type == "EnergyDipoleMACE":
            self.implemented_properties = [
                "energy",
                "free_energy",
                "node_energy",
                "forces",
                "stress",
                "dipole",
            ]
        else:
            raise ValueError(
                f"Give a valid model_type: [MACE, DipoleMACE, DipolePolarizabilityMACE, EnergyDipoleMACE], {model_type} not supported"
            )

        if model_paths is not None:
            if isinstance(model_paths, str):
                # Find all models that satisfy the wildcard (e.g. mace_model_*.pt)
                model_paths_glob = glob(model_paths)

                if len(model_paths_glob) == 0:
                    raise ValueError(f"Couldn't find MACE model files: {model_paths}")

                model_paths = model_paths_glob
            elif isinstance(model_paths, Path):
                model_paths = [model_paths]

            if len(model_paths) == 0:
                raise ValueError("No mace_descriptor file names supplied")
            self.num_models = len(model_paths)

            # Load models from files
            self.models = [
                torch.load(f=model_path, map_location=device)
                for model_path in model_paths
            ]

        elif models is not None:
            if not isinstance(models, list):
                models = [models]

            if len(models) == 0:
                raise ValueError("No models supplied")

            self.models = models
            self.num_models = len(models)

        if self.num_models > 1:
            print(f"Running committee mace_descriptor with {self.num_models} models")

            if model_type in ["MACE", "EnergyDipoleMACE"]:
                self.implemented_properties.extend(
                    ["energies", "energy_var", "forces_comm", "stress_var"]
                )
            elif model_type == "DipoleMACE":
                self.implemented_properties.extend(["dipole_var"])

        if compile_mode is not None:
            print(f"Torch compile is enabled with mode: {compile_mode}")
            self.models = [
                torch.compile(
                    prepare(extract_model)(model=model, map_location=device),
                    mode=compile_mode,
                    fullgraph=fullgraph,
                )
                for model in self.models
            ]
            self.use_compile = True
        else:
            self.use_compile = False

        # Ensure all models are on the same device
        for model in self.models:
            model.to(device)

        if has_ipex and device == "xpu":
            for model in self.models:
                model = ipex.optimize(model)

        r_maxs = [model.r_max.cpu() for model in self.models]
        r_maxs = np.array(r_maxs)
        if not np.all(r_maxs == r_maxs[0]):
            raise ValueError(f"committee r_max are not all the same {' '.join(r_maxs)}")
        self.r_max = float(r_maxs[0])

        self.device = torch_tools.init_device(device)
        self.energy_units_to_eV = energy_units_to_eV
        self.length_units_to_A = length_units_to_A
        self.z_table = utils.AtomicNumberTable(
            [int(z) for z in self.models[0].atomic_numbers]
        )
        self.charges_key = charges_key

        try:
            self.available_heads: List[str] = self.models[0].heads  # type: ignore
        except AttributeError:
            self.available_heads = ["Default"]
        kwarg_head = kwargs.get("head", None)
        if kwarg_head is not None:
            self.head = kwarg_head
            if isinstance(self.head, str):
                if self.head not in self.available_heads:
                    last_head = self.available_heads[-1]
                    logging.warning(
                        f"Head {self.head} not found in available heads {self.available_heads}, defaulting to the last head: {last_head}"
                    )
                    self.head = last_head
        elif len(self.available_heads) == 1:
            self.head = self.available_heads[0]
        else:
            self.head = [
                head for head in self.available_heads if head.lower() == "default"
            ]
            if len(self.head) == 0:
                raise ValueError(
                    "Head keyword was not provided, and no head in the model is 'default'. "
                    "Please provide a head keyword to specify the head you want to use. "
                    f"Available heads are: {self.available_heads}"
                )
            self.head = self.head[0]

        print("Using head", self.head, "out of", self.available_heads)

        model_dtype = get_model_dtype(self.models[0])

        if default_dtype == "":
            print(
                f"No dtype selected, switching to {model_dtype} to match model dtype."
            )
            default_dtype = model_dtype

        if model_dtype != default_dtype:
            print(
                f"Default dtype {default_dtype} does not match model dtype {model_dtype}, converting models to {default_dtype}."
            )
            if default_dtype == "float64":
                self.models = [model.double() for model in self.models]
            elif default_dtype == "float32":
                self.models = [model.float() for model in self.models]
        torch_tools.set_default_dtype(default_dtype)

        for model in self.models:
            for param in model.parameters():
                param.requires_grad = False

    def check_state(self, atoms, tol: float = 1e-15) -> list:
        """
        Check for any system changes since the last calculation.

        Args:
            atoms (ase.Atoms): The atomic structure to check.
            tol (float): Tolerance for detecting changes.

        Returns:
            list: A list of changes detected in the system.
        """
        state = super().check_state(atoms, tol=tol)
        if (not state) and (self.atoms.info != atoms.info):
            state.append("info")
        return state

    def _atoms_to_batch(self, atoms):
        self.arrays_keys.update({self.charges_key: "charges"})
        keyspec = data.KeySpecification(
            info_keys=self.info_keys, arrays_keys=self.arrays_keys
        )
        config = data.config_from_atoms(
            atoms, key_specification=keyspec, head_name=self.head
        )
        data_loader = torch_geometric.dataloader.DataLoader(
            dataset=[
                data.AtomicData.from_config(
                    config,
                    z_table=self.z_table,
                    cutoff=self.r_max,
                    heads=self.available_heads,
                )
            ],
            batch_size=1,
            shuffle=False,
            drop_last=False,
        )
        batch = next(iter(data_loader)).to(self.device)
        return batch

    def _clone_batch(self, batch):
        batch_clone = batch.clone()
        if self.use_compile:
            batch_clone["node_attrs"].requires_grad_(True)
            batch_clone["positions"].requires_grad_(True)
        return batch_clone

    def get_hessian(self, atoms=None):
        if atoms is None and self.atoms is None:
            raise ValueError("atoms not set")
        if atoms is None:
            atoms = self.atoms
        if self.model_type != "MACE":
            raise NotImplementedError("Only implemented for MACE models")
        batch = self._atoms_to_batch(atoms)
        hessians = [
            model(
                self._clone_batch(batch).to_dict(),
                compute_hessian=True,
                compute_stress=False,
                training=self.use_compile,
            )["hessian"]
            for model in self.models
        ]
        hessians = [hessian.detach().cpu().numpy() for hessian in hessians]
        if self.num_models == 1:
            return hessians[0]
        return hessians

    def get_descriptors(self, atoms=None, invariants_only=True, num_layers=-1):
        """Extracts the descriptors from MACE model."""
        if atoms is None and self.atoms is None:
            raise ValueError("atoms not set")
        if atoms is None:
            atoms = self.atoms
        if self.model_type != "MACE":
            raise NotImplementedError("Only implemented for MACE models")

        num_interactions = int(self.models[0].num_interactions)
        if num_layers == -1:
            num_layers = num_interactions

        batch = self._atoms_to_batch(atoms)
        descriptors = [model(batch.to_dict())["node_feats"] for model in self.models]

        irreps_out = o3.Irreps(str(self.models[0].products[0].linear.irreps_out))
        l_max = irreps_out.lmax
        num_invariant_features = irreps_out.dim // (l_max + 1) ** 2
        per_layer_features = [irreps_out.dim for _ in range(num_interactions)]
        per_layer_features[-1] = num_invariant_features  # last layer is scalar-only

        if invariants_only:
            descriptors = [
                extract_invariant(descriptor,
                                  num_layers=num_layers,
                                  num_features=num_invariant_features,
                                  l_max=l_max, )
                for descriptor in descriptors]

        to_keep = np.sum(per_layer_features[:num_layers])
        descriptors = [desc[:, :to_keep].detach().clone() for desc in descriptors]

        return descriptors[0] if self.num_models == 1 else descriptors

    def get_descriptors_batch(self, atoms_list, invariants_only=True, num_layers=-1):
        """Batch version of descriptor extraction for multiple structures."""
        num_interactions = int(self.models[0].num_interactions)
        if num_layers == -1:
            num_layers = num_interactions

        self.arrays_keys.update({self.charges_key: "charges"})
        keyspec = data.KeySpecification(info_keys=self.info_keys, arrays_keys=self.arrays_keys)

        # Convert list of ASE atoms → list of config dicts
        configs = data.config_from_atoms_list(atoms_list, key_specification=keyspec, head_name=self.head)

        atomic_data_list = [data.AtomicData.from_config(config,
                                                        z_table=self.z_table,
                                                        cutoff=self.r_max,
                                                        heads=self.available_heads, ) for config in configs]

        # Batch all together
        data_loader = get_data_loader(dataset=atomic_data_list, batch_size=len(atoms_list), shuffle=False,
                                      drop_last=False)
        batch = next(iter(data_loader)).to(self.device)

        # Feedforward through model
        desc_all = [model(batch.to_dict())["node_feats"] for model in self.models]  # shape: (total_atoms, descriptor_dim)
        print(len(desc_all), desc_all[0].shape)

        irreps_out = o3.Irreps(str(self.models[0].products[0].linear.irreps_out))
        l_max = irreps_out.lmax
        num_invariant_features = irreps_out.dim // (l_max + 1) ** 2
        per_layer_features = [irreps_out.dim for _ in range(num_interactions)]
        per_layer_features[-1] = num_invariant_features  # last layer is scalar-only

        if invariants_only:
            desc_all = [
                extract_invariant(descriptor,
                                  num_layers=num_layers,
                                  num_features=num_invariant_features,
                                  l_max=l_max, )
                for descriptor in desc_all]
        print(len(desc_all), desc_all[0].shape)

        to_keep = np.sum(per_layer_features[:num_layers])
        desc_all = [desc[:, :to_keep].detach().clone() for desc in desc_all]
        print(len(desc_all), desc_all[0].shape)

        # if self.num_models == 1:
        atom_counts = [len(atoms) for atoms in atoms_list]
        descriptor_splits = torch.split(desc_all[0], atom_counts, dim=0)
        print(len(descriptor_splits), descriptor_splits[0].shape)
        # shape: (num_structures, num_atoms, descriptor_dim)

        return descriptor_splits

    def numerical_descriptor_gradient(self, atoms, delta=1e-4):
        atoms = atoms.copy()
        n_atoms = len(atoms)

        desc_0 = self.get_descriptors(atoms)
        D = desc_0.shape[1]

        # 전체 forward/backward 구조 리스트
        displaced_atoms = []

        # mapping: (atom_idx, coord_idx) -> index in descriptor list
        index_map = {}

        counter = 0
        for i in range(n_atoms):
            for j in range(3):  # x, y, z
                # forward
                atoms_f = atoms.copy()
                atoms_f.positions[i, j] += delta
                displaced_atoms.append(atoms_f)
                index_map[(i, j, "f")] = counter
                counter += 1

                # backward
                atoms_b = atoms.copy()
                atoms_b.positions[i, j] -= delta
                displaced_atoms.append(atoms_b)
                index_map[(i, j, "b")] = counter
                counter += 1

        all_desc = self.get_descriptors_batch(displaced_atoms)
        grad = torch.empty((n_atoms, n_atoms, 3, D))

        for i in range(n_atoms):
            for j in range(3):
                f_idx = index_map[(i, j, "f")]
                b_idx = index_map[(i, j, "b")]

                desc_f = all_desc[f_idx]
                desc_b = all_desc[b_idx]

                grad[:, i, j, :] = (desc_f - desc_b) / (2 * delta)

        return grad
