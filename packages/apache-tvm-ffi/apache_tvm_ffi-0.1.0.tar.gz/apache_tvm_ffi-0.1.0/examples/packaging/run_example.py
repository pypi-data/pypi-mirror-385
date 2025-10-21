# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations.
# Base logic to load library for extension package
"""Run functions from the example packaged tvm-ffi extension."""

import sys

import my_ffi_extension
import torch


def run_add_one() -> None:
    """Invoke add_one from the extension and print the result."""
    x = torch.tensor([1, 2, 3, 4, 5], dtype=torch.float32)
    y = torch.empty_like(x)
    my_ffi_extension.add_one(x, y)
    print(y)


def run_raise_error() -> None:
    """Invoke raise_error from the extension to demonstrate error handling."""
    my_ffi_extension.raise_error("This is an error")


def run_int_pair() -> None:
    """Invoke IntPair from the extension to demonstrate object handling."""
    pair = my_ffi_extension.IntPair(1, 2)
    print(f"first={pair.get_first()}")
    print(f"second={my_ffi_extension.IntPair.static_get_second(pair)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "add_one":
            run_add_one()
        elif sys.argv[1] == "int_pair":
            run_int_pair()
        elif sys.argv[1] == "raise_error":
            run_raise_error()
    else:
        print("Usage: python run_example.py <add_one|int_pair|raise_error>")
