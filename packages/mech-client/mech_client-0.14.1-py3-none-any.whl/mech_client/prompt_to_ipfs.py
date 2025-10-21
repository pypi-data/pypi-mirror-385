# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2023 Valory AG
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

"""
This script allows pushing a prompt compatible with the on-chain mechs directly to IPFS.

Usage:

python push_to_ipfs.py <prompt> <tool>
"""

import json
import shutil
import tempfile
import uuid
from typing import Any, Dict, Optional, Tuple

from mech_client.push_to_ipfs import push_to_ipfs


def push_metadata_to_ipfs(
    prompt: str, tool: str, extra_attributes: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """
    Pushes metadata object to IPFS.

    :param prompt: Prompt string.
    :type prompt: str
    :param tool: Tool string.
    :type tool: str
    :param extra_attributes: Extra attributes to be included in the request metadata.
    :type extra_attributes: Optional[Dict[str,Any]]
    :return: Tuple containing the IPFS hash and truncated IPFS hash.
    :rtype: Tuple[str, str]
    """
    metadata = {"prompt": prompt, "tool": tool, "nonce": str(uuid.uuid4())}
    if extra_attributes:
        metadata.update(extra_attributes)
    dirpath = tempfile.mkdtemp()
    file_name = dirpath + "metadata.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(metadata, f)
    _, v1_file_hash_hex = push_to_ipfs(file_name)
    shutil.rmtree(dirpath)
    return "0x" + v1_file_hash_hex[9:], v1_file_hash_hex


def main(prompt: str, tool: str) -> None:
    """
    Prints the IPFS hash and truncated IPFS hash for the metadata object.

    :param prompt: Prompt string.
    :type prompt: str
    :param tool: Tool string.
    :type tool: str
    """
    v1_file_hash_hex_truncated, v1_file_hash_hex = push_metadata_to_ipfs(prompt, tool)
    print("Visit url: https://gateway.autonolas.tech/ipfs/{}".format(v1_file_hash_hex))
    print("Hash for Request method: {}".format(v1_file_hash_hex_truncated))
