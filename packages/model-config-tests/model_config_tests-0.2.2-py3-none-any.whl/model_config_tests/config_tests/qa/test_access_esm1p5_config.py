# Copyright 2024 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""ACCESS-ESM1.5 specific configuration tests"""

import re
import warnings
from typing import Any

import f90nml
import pytest

from model_config_tests.config_tests.qa.test_config import (
    check_manifest_exes_in_spack_location,
)
from model_config_tests.util import get_git_branch_name

# Name of module on NCI
ACCESS_ESM1P5_MODULE_NAME = "access-esm1p5"
# Name of Model Repository - used for retrieving spack location files for released versions
ACCESS_ESM1P5_REPOSITORY_NAME = "ACCESS-ESM1.5"


######################################
# Bunch of expected values for tests #
######################################
VALID_REALMS: set[str] = {"atmos", "land", "ocean", "ocnBgchem", "seaIce"}
VALID_KEYWORDS: set[str] = {"global", "access-esm1.5"}
VALID_NOMINAL_RESOLUTION: str = "100 km"
VALID_REFERENCE: str = "https://doi.org/10.1071/ES19035"
VALID_RUNTIME: dict[str, int] = {"years": 1, "months": 0, "days": 0}
VALID_RESTART_FREQ: str = "10YS"
VALID_MPPNCCOMBINE_EXE: str = "mppnccombine.spack"

CICE_IN_NML_FNAME = "cice_in.nml"
ICE_HISTORY_NML_FNAME = "ice_history.nml"
ICEFIELDS_NML_NAME = "icefields_nml"


### Some functions to avoid copying assertion error text
def error_field_nonexistence(field: str, file: str) -> str:
    return f"Field '{field}' is null or does not exist in {file}."


def error_field_incorrect(field: str, file: str, expected: Any) -> str:
    return f"Field '{field}' in {file} is not expected value: {expected}"


class AccessEsm1p5Branch:
    """Use the naming patterns of the branch name to infer information of
    the ACCESS-ESM1.5 config"""

    def __init__(self, branch_name):
        self.branch_name = branch_name
        self.config_scenario = self.set_config_scenario()
        self.config_modifiers = self.set_config_modifiers()

    def set_config_scenario(self) -> str:
        # Regex below is split into three sections:
        # Config type start section: '(?:release|dev)-' for 'release-' or 'dev-'
        # Scenario section: '([^+]+)' for 'preindustrial', 'historical'...anything that isn't the '+' modifier sigil
        # Modifiers end section: '(?:\+.+)*' any amount of '+modifer' sections
        scenario_match = re.match(
            r"^(?:release|dev)-(?P<scenario>[^+]+)(?:\+.+)*$", self.branch_name
        )
        if not scenario_match or "scenario" not in scenario_match.groupdict():
            pytest.fail(
                f"Could not find a scenario in the branch {self.branch_name}. "
                + "Branches must be of the form 'type-scenario[+modifier...]'. "
                + "See README.md for more information."
            )
        return scenario_match.group("scenario")

    def set_config_modifiers(self) -> list[str]:
        # Regex below is essentially 'give me the 'modifier' part in all the '+modifier's in the branch name'
        return re.findall(r"\+([^+]+)", self.branch_name)


@pytest.fixture(scope="class")
def branch(control_path, target_branch):
    branch_name = target_branch
    if branch_name is None:
        # Default to current branch name
        branch_name = get_git_branch_name(control_path)
        assert (
            branch_name is not None
        ), f"Failed getting git branch name of control path: {control_path}"
        warnings.warn(
            "Target branch is not specifed, defaulting to current git branch: "
            f"{branch_name}. As some ACCESS-ESM1.5 tests infer information, "
            "such as scenario and modifiers, from the target branch name, some "
            "tests may not be run. To set use --target-branch flag in pytest call"
        )

    return AccessEsm1p5Branch(branch_name)


@pytest.mark.access_esm1p5
class TestAccessEsm1p5:
    """ACCESS-ESM1.5 Specific configuration and metadata tests"""

    def test_access_esm1p5_manifest_exe_in_release_spack_location(
        self, config, control_path
    ):
        check_manifest_exes_in_spack_location(
            model_module_name=ACCESS_ESM1P5_MODULE_NAME,
            model_repo_name=ACCESS_ESM1P5_REPOSITORY_NAME,
            control_path=control_path,
            config=config,
        )

    @pytest.mark.parametrize(
        "field,expected", [("realm", VALID_REALMS), ("keywords", VALID_KEYWORDS)]
    )
    def test_metadata_field_equal_expected_sequence(self, field, expected, metadata):

        assert (
            field in metadata and metadata[field] is not None
        ), error_field_nonexistence(field, "metadata.yaml")

        field_set: set[str] = set(metadata[field])

        assert field_set == expected, error_field_incorrect(
            field, "metadata.yaml", expected
        )

    @pytest.mark.parametrize(
        "field,expected",
        [
            ("nominal_resolution", VALID_NOMINAL_RESOLUTION),
            ("reference", VALID_REFERENCE),
        ],
    )
    def test_metadata_field_equal_expected_value(self, field, expected, metadata):
        assert field in metadata and metadata[field] == expected, error_field_incorrect(
            field, "metadata.yaml", expected
        )

    def test_config_runtime(self, config):
        assert (
            "calendar" in config
            and config["calendar"] is not None
            and "runtime" in config["calendar"]
            and config["calendar"]["runtime"] is not None
        ), error_field_nonexistence("calendar.runtime", "config.yaml")

        runtime: dict[str, int] = config["calendar"]["runtime"]

        assert runtime == VALID_RUNTIME, error_field_incorrect(
            "calendar.runtime", "config.yaml", VALID_RUNTIME
        )

    def test_config_restart_freq(self, config):
        assert (
            "restart_freq" in config and config["restart_freq"] is not None
        ), error_field_nonexistence("restart_freq", "config.yaml")
        assert config["restart_freq"] == VALID_RESTART_FREQ, error_field_incorrect(
            "restart_freq", "config.yaml", VALID_RESTART_FREQ
        )

    def test_mppnccombine_fast_collate_exe(self, config):
        if "collate" in config:
            assert (
                config["collate"]["exe"] == VALID_MPPNCCOMBINE_EXE
            ), error_field_incorrect(
                "collate.exe", "config.yaml", VALID_MPPNCCOMBINE_EXE
            )

            assert "mpi" in config["collate"], error_field_nonexistence(
                "collate.mpi", "config.yaml"
            )

            # Loading the yaml into a dict also converts
            # `collate.mpi:true`/`collate.mpi:false` to `True`/`False` so we
            # can assert if it is a `bool`.
            assert isinstance(config["collate"]["mpi"], bool), error_field_incorrect(
                "collate.mpi", "config.yaml", "true or false"
            )

    def test_cice_configuration_icefields_nml_in_ice_history_nml(
        self, branch, config, control_path
    ):
        if branch.config_scenario == "amip":
            pytest.skip("amip scenarios do not contain the CICE sub-model.")

        # Find CICE sub-model control path
        model_name = None
        for sub_model in config["submodels"]:
            if sub_model["model"] == "cice":
                model_name = sub_model["name"]
        assert model_name
        cice_control_path = control_path / model_name

        icefields_nml_error_msg = (
            f"Expected CICE configuration to have {ICE_HISTORY_NML_FNAME} that "
            f"contains an {ICEFIELDS_NML_NAME} namelist. This is to keep icefields "
            f"namelist separate from the {CICE_IN_NML_FNAME} to allow simpler changes."
        )

        # Check ice_history.nml exists
        ice_history_nml_path = cice_control_path / ICE_HISTORY_NML_FNAME
        assert ice_history_nml_path.is_file(), icefields_nml_error_msg

        # Check icefields_nml in ice_history.nml
        ice_history_nml = f90nml.read(ice_history_nml_path)
        assert ICEFIELDS_NML_NAME in ice_history_nml, icefields_nml_error_msg

        # Check icefields_nml not in cice_in.nml
        cice_in_path = cice_control_path / CICE_IN_NML_FNAME
        assert cice_in_path.is_file(), (
            f"No {CICE_IN_NML_FNAME} file found. This is a required "
            "configuration file for the CICE model component."
        )
        cice_in = f90nml.read(cice_in_path)
        assert ICEFIELDS_NML_NAME not in cice_in, (
            f"{ICEFIELDS_NML_NAME} namelist found in {CICE_IN_NML_FNAME}. "
            f"This should only be in {ICE_HISTORY_NML_FNAME} to prevent duplication."
        )

        # Check no repeated fields between the two namelist files
        common_nmls = set(cice_in) & set(ice_history_nml)
        for nml in common_nmls:
            repeated_fields = set(cice_in[nml]) & set(ice_history_nml[nml])
            assert repeated_fields == set(), (
                f"Found repeated fields for '{nml}' namelist"
                f" in {CICE_IN_NML_FNAME} and {ICE_HISTORY_NML_FNAME}"
                f": {repeated_fields}"
            )
