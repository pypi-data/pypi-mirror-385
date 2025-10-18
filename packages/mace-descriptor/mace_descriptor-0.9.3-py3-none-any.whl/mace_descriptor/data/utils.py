###########################################################################################
# Modified from ACEsuit/mace_descriptor
# Original Copyright (c) 2022 ACEsuit/mace_descriptor
# Licensed under the MIT License
###########################################################################################

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import ase.data
import ase.io
import numpy as np

from mace_descriptor.tools import DefaultKeys

Positions = np.ndarray  # [..., 3]
Cell = np.ndarray  # [3,3]
Pbc = tuple  # (3,)

DEFAULT_CONFIG_TYPE = "Default"
DEFAULT_CONFIG_TYPE_WEIGHTS = {DEFAULT_CONFIG_TYPE: 1.0}


@dataclass
class KeySpecification:
    info_keys: Dict[str, str] = field(default_factory=dict)
    arrays_keys: Dict[str, str] = field(default_factory=dict)

    def update(
        self,
        info_keys: Optional[Dict[str, str]] = None,
        arrays_keys: Optional[Dict[str, str]] = None,
    ):
        if info_keys is not None:
            self.info_keys.update(info_keys)
        if arrays_keys is not None:
            self.arrays_keys.update(arrays_keys)
        return self

    @classmethod
    def from_defaults(cls):
        instance = cls()
        return update_keyspec_from_kwargs(instance, DefaultKeys.keydict())


def update_keyspec_from_kwargs(
    keyspec: KeySpecification, keydict: Dict[str, str]
) -> KeySpecification:
    # convert command line style property_key arguments into a keyspec
    infos = [
        "energy_key",
        "stress_key",
        "virials_key",
        "dipole_key",
        "head_key",
        "elec_temp_key",
        "total_charge_key",
        "polarizability_key",
        "total_spin_key",
    ]
    arrays = ["forces_key", "charges_key"]
    info_keys = {}
    arrays_keys = {}
    for key in infos:
        if key in keydict:
            info_keys[key[:-4]] = keydict[key]
    for key in arrays:
        if key in keydict:
            arrays_keys[key[:-4]] = keydict[key]
    keyspec.update(info_keys=info_keys, arrays_keys=arrays_keys)
    return keyspec


@dataclass
class Configuration:
    atomic_numbers: np.ndarray
    positions: Positions  # Angstrom
    properties: Dict[str, Any]
    property_weights: Dict[str, float]
    cell: Optional[Cell] = None
    pbc: Optional[Pbc] = None

    weight: float = 1.0  # weight of config in loss
    config_type: str = DEFAULT_CONFIG_TYPE  # config_type of config
    head: str = "Default"  # head used to compute the config


Configurations = List[Configuration]


def config_from_atoms_list(
    atoms_list: List[ase.Atoms],
    key_specification: KeySpecification,
    config_type_weights: Optional[Dict[str, float]] = None,
    head_name: str = "Default",
) -> Configurations:
    """Convert list of ase.Atoms into Configurations"""
    if config_type_weights is None:
        config_type_weights = DEFAULT_CONFIG_TYPE_WEIGHTS

    all_configs = []
    for atoms in atoms_list:
        all_configs.append(
            config_from_atoms(
                atoms,
                key_specification=key_specification,
                config_type_weights=config_type_weights,
                head_name=head_name,
            )
        )
    return all_configs


def config_from_atoms(
    atoms: ase.Atoms,
    key_specification: KeySpecification = KeySpecification(),
    config_type_weights: Optional[Dict[str, float]] = None,
    head_name: str = "Default",
) -> Configuration:
    """Convert ase.Atoms to Configuration"""
    if config_type_weights is None:
        config_type_weights = DEFAULT_CONFIG_TYPE_WEIGHTS

    atomic_numbers = np.array(
        [ase.data.atomic_numbers[symbol] for symbol in atoms.symbols]
    )
    pbc = tuple(atoms.get_pbc())
    cell = np.array(atoms.get_cell())
    config_type = atoms.info.get("config_type", "Default")
    weight = atoms.info.get("config_weight", 1.0) * config_type_weights.get(
        config_type, 1.0
    )

    properties = {}
    property_weights = {}
    for name in list(key_specification.arrays_keys) + list(key_specification.info_keys):
        property_weights[name] = atoms.info.get(f"config_{name}_weight", 1.0)

    for name, atoms_key in key_specification.info_keys.items():
        properties[name] = atoms.info.get(atoms_key, None)
        if not atoms_key in atoms.info:
            property_weights[name] = 0.0

    for name, atoms_key in key_specification.arrays_keys.items():
        properties[name] = atoms.arrays.get(atoms_key, None)
        if not atoms_key in atoms.arrays:
            property_weights[name] = 0.0

    return Configuration(
        atomic_numbers=atomic_numbers,
        positions=atoms.get_positions(),
        properties=properties,
        weight=weight,
        property_weights=property_weights,
        head=head_name,
        config_type=config_type,
        pbc=pbc,
        cell=cell,
    )


def test_config_types(
    test_configs: Configurations,
) -> List[Tuple[str, List[Configuration]]]:
    """Split test set based on config_type-s"""
    test_by_ct = []
    all_cts = []
    for conf in test_configs:
        if conf.head is None:
            conf.head = ""
        config_type_name = conf.config_type + "_" + conf.head
        if config_type_name not in all_cts:
            all_cts.append(config_type_name)
            test_by_ct.append((config_type_name, [conf]))
        else:
            ind = all_cts.index(config_type_name)
            test_by_ct[ind][1].append(conf)
    return test_by_ct


def load_from_xyz(
    file_path: str,
    key_specification: KeySpecification,
    head_name: str = "Default",
    config_type_weights: Optional[Dict] = None,
    extract_atomic_energies: bool = False,
    keep_isolated_atoms: bool = False,
    no_data_ok: bool = False,
) -> Tuple[Dict[int, float], Configurations]:
    atoms_list = ase.io.read(file_path, index=":")
    energy_key = key_specification.info_keys["energy"]
    forces_key = key_specification.arrays_keys["forces"]
    stress_key = key_specification.info_keys["stress"]
    head_key = key_specification.info_keys["head"]
    original_energy_key = energy_key
    original_forces_key = forces_key
    original_stress_key = stress_key
    if energy_key == "energy":
        logging.warning(
            "Since ASE version 3.23.0b1, using energy_key 'energy' is no longer safe when communicating between MACE and ASE. We recommend using a different key, rewriting 'energy' to 'REF_energy'. You need to use --energy_key='REF_energy' to specify the chosen key name."
        )
        key_specification.info_keys["energy"] = "REF_energy"
        for atoms in atoms_list:
            try:
                # print("OK")
                atoms.info["REF_energy"] = atoms.get_potential_energy()
                # print("atoms.info['REF_energy']:", atoms.info["REF_energy"])
            except Exception as e:  # pylint: disable=W0703
                logging.error(f"Failed to extract energy: {e}")
                atoms.info["REF_energy"] = None
    if forces_key == "forces":
        logging.warning(
            "Since ASE version 3.23.0b1, using forces_key 'forces' is no longer safe when communicating between MACE and ASE. We recommend using a different key, rewriting 'forces' to 'REF_forces'. You need to use --forces_key='REF_forces' to specify the chosen key name."
        )
        key_specification.arrays_keys["forces"] = "REF_forces"
        for atoms in atoms_list:
            try:
                atoms.arrays["REF_forces"] = atoms.get_forces()
            except Exception as e:  # pylint: disable=W0703
                logging.error(f"Failed to extract forces: {e}")
                atoms.arrays["REF_forces"] = None
    if stress_key == "stress":
        logging.warning(
            "Since ASE version 3.23.0b1, using stress_key 'stress' is no longer safe when communicating between MACE and ASE. We recommend using a different key, rewriting 'stress' to 'REF_stress'. You need to use --stress_key='REF_stress' to specify the chosen key name."
        )
        key_specification.info_keys["stress"] = "REF_stress"
        for atoms in atoms_list:
            try:
                atoms.info["REF_stress"] = atoms.get_stress()
            except Exception as e:  # pylint: disable=W0703
                atoms.info["REF_stress"] = None

    final_energy_key = key_specification.info_keys["energy"]
    final_forces_key = key_specification.arrays_keys["forces"]
    final_dipole_key = key_specification.info_keys.get("dipole", "REF_dipole")
    has_energy = any(final_energy_key in atoms.info for atoms in atoms_list)
    has_forces = any(final_forces_key in atoms.arrays for atoms in atoms_list)
    has_dipole = any(final_dipole_key in atoms.info for atoms in atoms_list)

    if not has_energy and not has_forces and not has_dipole:
        msg = f"None of '{final_energy_key}', '{final_forces_key}', and '{final_dipole_key}' found in '{file_path}'."
        if no_data_ok:
            logging.warning(msg + " Continuing because no_data_ok=True was passed in.")
        else:
            raise ValueError(
                msg
                + " Please change the key names in the command line arguments or ensure that the file contains the required data."
            )
    if not has_energy:
        logging.warning(
            f"No energies found with key '{final_energy_key}' in '{file_path}'. If this is unexpected, please change the key name in the command line arguments or ensure that the file contains the required data."
        )
    if not has_forces:
        logging.warning(
            f"No forces found with key '{final_forces_key}' in '{file_path}'. If this is unexpected, Please change the key name in the command line arguments or ensure that the file contains the required data."
        )

    if not isinstance(atoms_list, list):
        atoms_list = [atoms_list]

    atomic_energies_dict = {}
    if extract_atomic_energies:
        atoms_without_iso_atoms = []

        for idx, atoms in enumerate(atoms_list):
            atoms.info[head_key] = head_name
            isolated_atom_config = (
                len(atoms) == 1 and atoms.info.get("config_type") == "IsolatedAtom"
            )
            if isolated_atom_config:
                atomic_number = int(atoms.get_atomic_numbers()[0])
                if energy_key in atoms.info.keys():
                    atomic_energies_dict[atomic_number] = float(atoms.info[energy_key])
                else:
                    logging.warning(
                        f"Configuration '{idx}' is marked as 'IsolatedAtom' "
                        "but does not contain an energy. Zero energy will be used."
                    )
                    atomic_energies_dict[atomic_number] = 0.0
            else:
                atoms_without_iso_atoms.append(atoms)

        if len(atomic_energies_dict) > 0:
            logging.info("Using isolated atom energies from training file")
        if not keep_isolated_atoms:
            atoms_list = atoms_without_iso_atoms

    for atoms in atoms_list:
        atoms.info[head_key] = head_name

    configs = config_from_atoms_list(
        atoms_list,
        config_type_weights=config_type_weights,
        key_specification=key_specification,
        head_name=head_name,
    )
    key_specification.info_keys["energy"] = original_energy_key
    key_specification.arrays_keys["forces"] = original_forces_key
    key_specification.info_keys["stress"] = original_stress_key
    return atomic_energies_dict, configs