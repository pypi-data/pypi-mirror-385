# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2022-2025 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""Tests for specs commands."""


import copy
import importlib
import os
import re
import shutil
from enum import Enum
from pathlib import Path
from typing import Tuple, cast
from unittest import mock

import pytest
import yaml
from aea.cli.registry.settings import REGISTRY_LOCAL
from aea.cli.utils.constants import CLI_CONFIG_PATH, DEFAULT_CLI_CONFIG
from aea.configurations.constants import PACKAGES
from jsonschema.exceptions import ValidationError

from autonomy.analyse.abci.app_spec import (
    DFA,
    DFASpecificationError,
    FSMSpecificationLoader,
    check_unreferenced_events,
)

from tests.conftest import ROOT_DIR
from tests.test_autonomy.test_cli.base import BaseCliTest


class TestGenerateSpecs(BaseCliTest):
    """Test generate-app-specs"""

    cli_options: Tuple[str, ...] = ("analyse", "fsm-specs")

    dfa: DFA
    app_name: str
    skill_path: Path

    def setup(self) -> None:
        """Setup test method."""
        super().setup()

        self.app_name = "OffendAbciApp"
        self.skill_path = Path(PACKAGES, "valory", "skills", "offend_abci")

        module_name = ".".join((*self.skill_path.parts, "rounds"))
        module = importlib.import_module(module_name)
        abci_app_cls = getattr(module, self.app_name)

        shutil.copytree(ROOT_DIR / PACKAGES, self.t / PACKAGES)

        self.dfa = DFA.abci_to_dfa(abci_app_cls)
        self.cli_options = (
            "--registry-path",
            str(self.t / PACKAGES),
            "analyse",
            "fsm-specs",
        )

        os.chdir(self.t)

    def get_expected_output(self, output_format: str) -> str:
        """Get expected output."""

        temp_file = self.t / "temp"
        FSMSpecificationLoader.dump(self.dfa, file=temp_file, spec_format=output_format)

        return temp_file.read_text(encoding="utf-8")

    def _run_test(self, output_format: str) -> None:
        """Run test for given output format type."""

        output_file = self.skill_path / cast(
            Path,
            FSMSpecificationLoader.OutputFormats.default_output_files.get(
                output_format
            ),
        )
        result = self.run_cli(
            (
                "--package",
                str(self.skill_path),
                f"--{output_format}",
                "--app-class",
                self.app_name,
                "--update",
            )
        )

        assert result.exit_code == 0, result.output
        assert output_file.read_text() == self.get_expected_output(output_format)

    def test_generate_yaml(
        self,
    ) -> None:
        """Run tests."""

        self._run_test(FSMSpecificationLoader.OutputFormats.YAML)

    def test_generate_json(
        self,
    ) -> None:
        """Run tests."""

        self._run_test(FSMSpecificationLoader.OutputFormats.JSON)

    def test_generate_mermaid(
        self,
    ) -> None:
        """Run tests."""

        self._run_test(FSMSpecificationLoader.OutputFormats.MERMAID)

    def test_failures(
        self,
    ) -> None:
        """Test failures."""

        with pytest.raises(ValueError, match="Unrecognized input format .exe"):
            FSMSpecificationLoader.dump(self.dfa, self.skill_path, ".exe")

        with pytest.raises(ValueError, match="Unrecognized input format .exe"):
            FSMSpecificationLoader.load(self.skill_path, ".exe")

        result = self.run_cli(
            (
                "--app-class",
                "SOME_CLASS_NAME",
                "--package",
                str(Path(*self.skill_path.parts, "dummy_abci")),
                "--yaml",
            )
        )

        assert result.exit_code == 1, result.output
        assert (
            "Cannot find the rounds module or the composition module" in result.stderr
        ), result.output

        result = self.run_cli(
            (
                "--app-class",
                "SomeAppName",
                "--package",
                str(self.skill_path),
                "--yaml",
            )
        )

        assert result.exit_code == 1, result.output
        assert 'Class "SomeAppName" is not in' in result.stderr, result.output

        self.skill_path = self.skill_path.rename(self.skill_path.parent / "offend")
        result = self.run_cli(("--package", str(self.skill_path)))
        assert result.exit_code == 1, result.output
        assert (
            "The name of the skill 'offend' must end with `_abci`." in result.stderr
        ), result.output


class TestCheckSpecs(BaseCliTest):
    """Test `check-app-specs` command."""

    cli_options: Tuple[str, ...] = ("analyse", "fsm-specs")
    skill_path = Path(PACKAGES, "valory", "skills", "offend_abci")
    module_name = ".".join(skill_path.parts)
    app_name = "OffendAbciApp"
    cls_name = ".".join([module_name, app_name])

    packages_dir: Path
    specification_path: Path

    def setup(self) -> None:
        """Setup class."""
        super().setup()

        self.packages_dir = self.t / PACKAGES
        shutil.copytree(ROOT_DIR / PACKAGES, self.packages_dir)
        self.specification_path = (
            self.t / self.skill_path.parent / "fsm_specification.yaml"
        )

        # make a copy of 'packages' in a subdirectory with depth > 1 from cwd
        subdirectory = self.t / Path("path", "to", "subdirectory")
        self.packages_dir_in_subdir = subdirectory / PACKAGES
        self.specification_path_in_subdir = (
            subdirectory / self.skill_path.parent / "fsm_specification.yaml"
        )
        shutil.copytree(self.packages_dir, self.packages_dir_in_subdir)

        self.specification_path = self.t / self.skill_path / "fsm_specification.yaml"
        os.chdir(self.t)
        DEFAULT_CLI_CONFIG["registry_config"]["settings"][REGISTRY_LOCAL][
            "default_packages_path"
        ] = (self.t / PACKAGES).as_posix()
        Path(CLI_CONFIG_PATH).write_text(yaml.dump(DEFAULT_CLI_CONFIG))

    def teardown(self) -> None:
        """Teardown class."""
        super().teardown()
        DEFAULT_CLI_CONFIG["registry_config"]["settings"][REGISTRY_LOCAL][
            "default_packages_path"
        ] = None
        Path(CLI_CONFIG_PATH).write_text(yaml.dump(DEFAULT_CLI_CONFIG))

    def _corrupt_spec_file(
        self,
    ) -> None:
        """Corrupt spec file to fail the check."""
        content = self.specification_path.read_text()
        content = content.replace("(OffendRound, ROUND_TIMEOUT): OffendRound\n", "")
        content = content.replace("- ROUND_TIMEOUT\n", "")
        self.specification_path.write_text(content)

    def test_one_pass(
        self,
    ) -> None:
        """Test with one class."""
        return_code, stdout, stderr = self.run_cli_subprocess(
            ("--app-class", self.app_name, "--package", str(self.skill_path))
        )

        assert return_code == 0, stderr
        assert "Check successful" in stdout

    def test_one_fail(
        self,
    ) -> None:
        """Test with one class failing."""
        self._corrupt_spec_file()
        return_code, stdout, stderr = self.run_cli_subprocess(
            ("--app-class", self.app_name, "--package", str(self.skill_path))
        )

        assert return_code == 1, stderr
        assert (
            "FSM Spec definition does not match in specification file and class definitions"
            in stderr
        )

    def test_analyse_fsm_specs(
        self,
    ) -> None:
        """Test the `analyse fsm-specs` command."""
        return_code, stdout, stderr = self.run_cli_subprocess(())

        assert return_code == 0, stderr
        assert "Done" in stdout

    def test_analyse_fsm_specs_when_packages_is_not_in_working_dir(
        self,
    ) -> None:
        """Test `analyse fsm-specs` command when the packages directory is not in the working directory."""
        return_code, stdout, stderr = self.run_cli_subprocess(())

        assert return_code == 0
        assert "Checking all available packages" in stdout
        assert "Done" in stdout

    def test_check_fail_when_packages_dir_is_not_named_packages(
        self,
    ) -> None:
        """Test `analyse fsm-specs` command when the packages directory is not named 'packages'."""
        wrong_dir = self.t / "some-directory"
        wrong_dir.mkdir(exist_ok=True)

        self.cli_options = (
            "--registry-path",
            str(wrong_dir),
            "analyse",
            "fsm-specs",
        )
        return_code, _, stderr = self.run_cli_subprocess(())

        assert return_code == 1, stderr
        assert f"packages directory {wrong_dir} is not named '{PACKAGES}'" in stderr

    def test_analyse_fsm_specs_fail(
        self,
    ) -> None:
        """Test `analyse fsm-specs` command failure."""
        self._corrupt_spec_file()
        return_code, stdout, stderr = self.run_cli_subprocess(())

        assert return_code == 1
        assert "Specifications check for following packages failed" in stderr


class TestDFA:
    """Test the DFA class."""

    good_dfa_kwargs = dict(
        label="DummyAbciApp",
        states={"StateARound", "StateBRound", "StateCRound"},
        default_start_state="StateARound",
        start_states={"StateARound"},
        final_states={"StateCRound"},
        alphabet_in={"event_a", "event_b", "event_c"},
        transition_func={
            ("StateARound", "event_b"): "StateBRound",
            ("StateBRound", "event_a"): "StateARound",
            ("StateBRound", "event_c"): "StateCRound",
        },
    )

    bad_dfa_kwargs = dict(
        label="DummyAbciApp",
        states={"StateARound", "StateBRound", "StateCRound", "unreachable_state"},
        default_start_state="state_other",
        start_states={"StateARound", "ExtraRound"},
        final_states={"StateARound", "StateCRound", "ExtraRound"},
        alphabet_in={"event_a", "event_b", "event_c", "other_extra_event"},
        transition_func={
            ("StateARound", "event_b"): "StateBRound",
            ("StateBRound", "event_a"): "StateARound",
            ("StateBRound", "event_c"): "StateCRound",
            ("ExtraRound", "extra_event"): "ExtraRound",
        },
    )

    def test_dfa(self) -> None:
        """Test DFA."""
        good_dfa = DFA(**self.good_dfa_kwargs)  # type: ignore

        assert not good_dfa.is_transition_func_total()
        assert good_dfa.get_transitions(["event_a"]) == ["StateARound", "StateARound"]
        assert good_dfa.get_transitions(["event_x"]) == ["StateARound"]
        assert isinstance(good_dfa.parse_transition_func(), dict)
        assert good_dfa.__eq__(None) == NotImplemented

        with pytest.raises(
            DFASpecificationError, match="DFA spec. object {} is not of type List."
        ):
            assert good_dfa._norep_list_to_set(dict())  # type: ignore

        with pytest.raises(
            DFASpecificationError,
            match=re.escape(
                "DFA spec. List ['value', 'value'] contains repeated values."
            ),
        ):
            assert good_dfa._norep_list_to_set(["value", "value"])

        with pytest.raises(
            DFASpecificationError,
            match="DFA spec. JSON file contains an invalid transition function key: .",
        ):
            assert good_dfa._str_to_tuple("")

        with pytest.raises(
            DFASpecificationError,
            match=re.escape(
                "DFA spec. JSON file contains an invalid transition function key: (a, )."
            ),
        ):
            assert good_dfa._str_to_tuple("(a, )")

        with pytest.raises(
            DFASpecificationError,
            match=re.escape(
                "DFA spec. JSON file contains an invalid transition function key: (, b)."
            ),
        ):
            assert good_dfa._str_to_tuple("(, b)")

        with pytest.raises(
            DFASpecificationError,
            match=re.escape(
                "DFA spec. JSON file contains an invalid transition function key: (, )."
            ),
        ):
            assert good_dfa._str_to_tuple("(, )")

        with pytest.raises(
            DFASpecificationError, match="DFA spec has the following issues"
        ):
            DFA(**self.bad_dfa_kwargs)  # type: ignore

    def test_load(self) -> None:
        """Test test_load"""

        json_spec = Path(
            ROOT_DIR,
            "tests",
            "data",
            "specs",
            "fsm_specification.json",
        )

        assert isinstance(
            DFA.load(json_spec, FSMSpecificationLoader.OutputFormats.JSON), DFA
        )

        with pytest.raises(ValueError):
            DFA.load(json_spec, "wrong_format")

    def test_load_empty(self) -> None:
        """Test test_load_empty"""

        json_spec = Path(
            ROOT_DIR,
            "tests",
            "data",
            "specs",
            "fsm_specification_empty.json",
        )

        with pytest.raises(ValidationError, match="is a required property"):
            DFA.load(json_spec, FSMSpecificationLoader.OutputFormats.JSON)

    def test_load_extra(self) -> None:
        """Test test_load_extra"""

        json_spec = Path(
            ROOT_DIR,
            "tests",
            "data",
            "specs",
            "fsm_specification_extra.json",
        )

        with pytest.raises(
            ValidationError,
            match=re.escape("Additional properties are not allowed"),
        ):
            DFA.load(json_spec, FSMSpecificationLoader.OutputFormats.JSON)

    def test_check_unreferenced_events(self) -> None:
        """Test check_unreferenced_events"""

        class MockABCIApp:
            """Mock ABCIApp class"""

            class Round:
                """Mock Round class"""

                __name__ = "round"

            class Event(Enum):
                """Mock Event class"""

                A = "A"
                B = "B"

            initial_round_cls = "initial_round_cls"
            transition_function = {
                Round: {
                    Event.A: "round_b",
                    Event.B: "round_b",
                },
            }
            event_to_timeout = {
                Event.A: 30.0,
            }

        with mock.patch("inspect.getmro", return_value=[]):
            strings = check_unreferenced_events(MockABCIApp)
            assert len(strings) > 0

    def test_name_verification(self) -> None:
        """Test `validate_naming_conventions`"""

        dfa_kwargs = copy.deepcopy(self.good_dfa_kwargs)
        dfa_kwargs["label"] = "abci_app"
        with pytest.raises(
            DFASpecificationError,
            match="ABCI app class name should end in `AbciApp`; ABCI app name found `abci_app`",
        ):
            DFA(**dfa_kwargs)  # type: ignore

        with pytest.raises(
            DFASpecificationError,
            match="Round class name should end in `Round`; Round app name found `StateBRoun`",
        ):
            DFA(
                label="DummyAbciApp",
                states={"StateARound", "StateBRoun"},
                default_start_state="StateARound",
                start_states={"StateARound"},
                final_states={"StateBRoun"},
                alphabet_in={"event_b"},
                transition_func={
                    ("StateARound", "event_b"): "StateBRoun",
                },
            )
