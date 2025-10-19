#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Copyright (c) 2024 Lanzhou University
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import re
import json
import argparse
import fnmatch

from typing import Optional

from rich.progress import track

from liscopelens.checker import Checker
from liscopelens.utils.graph import GraphManager
from liscopelens.utils.structure import DualLicense, SPDXParser, Config


from liscopelens.parser.base import BaseParser


class ScancodeParser(BaseParser):

    arg_table = {
        "--scancode-file": {
            "type": str,
            "help": "The path of the scancode's output in json format file",
            "group": "scancode",
            "parser_only": True,
        },
        "--scancode-dir": {
            "type": str,
            "help": "The path of the directory that contain json files",
            "group": "scancode",
            "parser_only": True,
        },
        "--shadow-license": {
            "type": str,
            "help": "The file path which storage (node-license) pair. Shadow licenses to certain nodes in advance",
            "default": None,
        },
        "--rm-ref-lang": {
            "action": "store_true",
            "help": "Automatically remove scancode ref prefix and language suffix from spdx ids",
            "default": False,
        },
    }

    def __call__(
        self, license_map: dict[str, str], context: GraphManager | str | dict
    ) -> GraphManager:
        """
        Apply SPDX licenses to nodes from a {label: expression} map, similar to parse().

        The keys in license_map must be node labels starting with '//' (e.g. '//src/main.c').
        The value is an SPDX license expression string.

        Steps:
            - Normalize context into a GraphManager.
            - For each entry, validate label, strip leading '//' to get file path,
              parse the SPDX expression (optionally post-process with remove_ref_lang),
              then write node['licenses'] and node['test'] = expr + '_call'.
            - If --shadow-license is provided, apply shadow rules afterwards.
            - If --output is provided, save to {output}/origin.json.

        Args:
            license_map (dict[str, str]): Mapping of node labels (must start with '//')
                to SPDX license expressions.
            context (GraphManager | str | dict): GraphManager instance, a file path to a
                GraphManager JSON export, or a dict representation.

        Returns:
            GraphManager: The updated GraphManager instance.

        Raises:
            TypeError: If license_map is not a dict.
            ValueError: If a key does not start with '//' or context construction fails.
            FileNotFoundError: If a provided context path does not exist.
        """
        if not isinstance(license_map, dict):
            raise TypeError("license_map must be a dict[str, str].")

        gm = self._normalize_context(context, allow_none=False)
        proproc = (
            self.remove_ref_lang if getattr(self.args, "rm_ref_lang", False) else None
        )

        for label, expr in (license_map or {}).items():
            if not isinstance(label, str) or not label.startswith("//"):
                raise ValueError(f"License map key must start with '//': {label!r}")

            file_path = label[2:].replace("\\", "/")
            spdx_results = self.spdx_parser(expr, file_path, proprocessor=proproc)
            if spdx_results:
                self.add_license(gm, file_path, spdx_results, expr + "_call")

        if getattr(self.args, "shadow_license", None):
            print("Parsing shadow license (from __call__)...")
            self.parse_shadow(self.args.shadow_license, gm)

        if output := getattr(self.args, "output", None):
            os.makedirs(output, exist_ok=True)
            gm.save(output + "/origin.json")

        return gm

    def __init__(self, args: argparse.Namespace, config: Config):
        super().__init__(args, config)
        self.checker = Checker()
        self.spdx_parser = SPDXParser()
        self.count = set()

    def add_license(
        self, context: GraphManager, file_path: str, spdx_results: DualLicense, test
    ):
        parent_label = "//" + file_path.replace("\\", "/")

        context_node = context.query_node_by_label(parent_label)

        if context_node and spdx_results:
            context_node["licenses"] = spdx_results
            context_node["test"] = test
            self.count.add(parent_label)

    def _apply_shadow_licenses(
        self, context: GraphManager, shadow_patterns: dict[str, str]
    ):
        """
        apply shadow licenses to nodes in the context based on wildcard patterns.

        Args:
            context: GraphManager instance containing the nodes
            shadow_patterns: shadow patterns in the form of a dictionary
        """
        spdx = SPDXParser()

        # 预先解析所有的 licenses，避免重复解析
        parsed_licenses = {}
        for pattern, license_str in shadow_patterns.items():
            if license_str not in parsed_licenses:
                parsed_licenses[license_str] = spdx(license_str)

        # 只遍历 code 类型的节点
        for node_id, node_data in context.nodes(data=True):
            if node_data.get("type") == "code":
                for pattern, license_str in shadow_patterns.items():
                    # 修正：fnmatch 的参数顺序应该是 (string, pattern)
                    if fnmatch.fnmatch(node_id, pattern):  # 修正参数顺序
                        spdx_license = parsed_licenses[license_str]
                        if spdx_license:
                            context.modify_node_attribute(
                                node_id, "licenses", spdx_license
                            )
                            print(
                                f"Applied shadow license '{license_str}' to '{node_id}' (matched pattern: '{pattern}')"
                            )
                        break

    def parse_shadow(self, json_path: str, context: GraphManager):
        """
        Parse the shadow license file and add the license to the context.
        The shadow license file should be in JSON format, with the following structure:
        {
            "//kernel/*": "Apache-2.0",
            "//specific/file.c": "MIT"
        }

        Usage:
            ```python

            parser = ScancodeParser(args, config)
            context = parser.parse_shadow("shadow.json", context)
            ```
        """
        if context is None:
            raise ValueError(f"Context can not be None in {self.__class__.__name__}.")

        with open(json_path, "r", encoding="utf-8") as f:
            shadow_rules = json.load(f)

        direct_matches = {}
        wildcard_patterns = {}

        for pattern, license_str in shadow_rules.items():
            if "*" in pattern or "?" in pattern or "[" in pattern:
                wildcard_patterns[pattern] = license_str
            else:
                direct_matches[pattern] = license_str

        spdx = SPDXParser()

        # 预解析所有直接匹配的 licenses
        parsed_direct_licenses = {}
        for key, license_str in direct_matches.items():
            if license_str not in parsed_direct_licenses:
                parsed_direct_licenses[license_str] = spdx(license_str)

            spdx_license = parsed_direct_licenses[license_str]
            if spdx_license:
                context.modify_node_attribute(key, "licenses", spdx_license)
                print(
                    f"Applied shadow license '{license_str}' to '{key}' (direct match)"
                )

        if wildcard_patterns:
            self._apply_shadow_licenses(context, wildcard_patterns)

        return context

    def remove_ref_lang(self, spdx_id: str) -> str:

        if not self.checker.is_license_exist(spdx_id):
            new_spdx_id = re.sub(r"LicenseRef-scancode-", "", spdx_id)
            if self.checker.is_license_exist(new_spdx_id):
                return new_spdx_id
            new_spdx_id = re.sub(r"-(en|cn)$", "", new_spdx_id)
            if self.checker.is_license_exist(new_spdx_id):
                return new_spdx_id
            return spdx_id

        return spdx_id

    def parse_json(self, json_path: str, context: GraphManager):

        if context is None:
            raise ValueError(f"Context can not be None in {self.__class__.__name__}.")

        if root_path := getattr(self.args, "scancode_dir", None):
            rel_path = os.path.relpath(os.path.dirname(json_path), root_path)
        else:
            rel_path = None

        with open(json_path, "r", encoding="utf-8") as f:
            try:
                scancode_results = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON file: {json_path}")
                raise e
            for detects in scancode_results["license_detections"]:
                for match in detects["reference_matches"]:
                    if rel_path:
                        file_path = os.path.join(rel_path, match["from_file"])
                    else:
                        file_path = os.path.relpath(
                            match["from_file"], match["from_file"].split(os.sep)[0]
                        )

                    spdx_results = self.spdx_parser(
                        match["license_expression_spdx"],
                        file_path,
                        proprocessor=(
                            self.remove_ref_lang if self.args.rm_ref_lang else None
                        ),
                    )

                    if spdx_results:
                        self.add_license(
                            context,
                            file_path,
                            spdx_results,
                            match["license_expression_spdx"] + "_m",
                        )

            for file in scancode_results["files"]:
                if rel_path:
                    file_path = os.path.join(rel_path, file["path"])
                else:
                    file_path = os.path.relpath(
                        file["path"], file["path"].split(os.sep)[0]
                    )
                if file["detected_license_expression_spdx"]:

                    spdx_results = self.spdx_parser(
                        file["detected_license_expression_spdx"], file_path
                    )

                    self.add_license(
                        context,
                        file_path,
                        spdx_results,
                        file["detected_license_expression_spdx"] + "_f",
                    )

    def parse(
        self, project_path: str, context: Optional[GraphManager] = None
    ) -> GraphManager:
        """
        The path of the scancode's output is relative path, whatever you pass absolute path or relative path.

        Usage:
        ```shell
        scancode --json-pp license.json .
        # or
        scancode --json-pp license.json /path/to/your/project

        # the path of the scancode's output is relative path
        ```
        """

        if getattr(self.args, "scancode_file", None):
            if not os.path.exists(self.args.scancode_file):
                raise FileNotFoundError(f"File not found: {self.args.scancode_file}")
            self.parse_json(self.args.scancode_file, context)
        elif getattr(self.args, "scancode_dir", None):
            if not os.path.exists(self.args.scancode_dir):
                raise FileNotFoundError(
                    f"Directory not found: {self.args.scancode_dir}"
                )
            for root, _, files in track(
                os.walk(self.args.scancode_dir), "Parsing scancode's output..."
            ):
                for file in files:
                    if file.endswith(".json"):
                        self.parse_json(os.path.join(root, file), context)

            json.dump(
                list(
                    set(
                        node[0]
                        for node in context.nodes(data=True)
                        if node[1].get("type", None) == "code"
                    )
                    - self.count
                ),
                open("scancode.json", "w", encoding="utf-8"),
            )
        else:
            raise ValueError("The path of the scancode's output is not provided.")

        if getattr(self.args, "shadow_license", None):
            print("Parsing shadow license...")
            self.parse_shadow(self.args.shadow_license, context)

        if output := getattr(self.args, "output", None):
            os.makedirs(output, exist_ok=True)
            context.save(output + "/origin.json")

        return context


if __name__ == "__main__":
    print(ScancodeParser(" --rm-ref-lang", None))
