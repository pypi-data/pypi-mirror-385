<!--- Licensed to the Apache Software Foundation (ASF) under one -->
<!--- or more contributor license agreements.  See the NOTICE file -->
<!--- distributed with this work for additional information -->
<!--- regarding copyright ownership.  The ASF licenses this file -->
<!--- to you under the Apache License, Version 2.0 (the -->
<!--- "License"); you may not use this file except in compliance -->
<!--- with the License.  You may obtain a copy of the License at -->

<!---   http://www.apache.org/licenses/LICENSE-2.0 -->

<!--- Unless required by applicable law or agreed to in writing, -->
<!--- software distributed under the License is distributed on an -->
<!--- "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY -->
<!--- KIND, either express or implied.  See the License for the -->
<!--- specific language governing permissions and limitations -->
<!--- under the License. -->

# TVM FFI: Open ABI and FFI for Machine Learning Systems

[![CI](https://github.com/apache/tvm-ffi/actions/workflows/ci_test.yml/badge.svg)](https://github.com/apache/tvm-ffi/actions/workflows/ci_test.yml)

Apache TVM FFI is an open ABI and FFI for machine learning systems. It is a minimal, framework-agnostic,
yet flexible open convention with the following systems in mind:

- Kernel libraries: ship one wheel to support multiple frameworks, Python versions, and different languages.
- Kernel DSLs: reusable open ABI for JIT and AOT kernel exposure to PyTorch, JAX, and other ML runtimes.
- ML frameworks and runtimes: unified mechanism to connect libraries and DSLs that adopt the ABI convention.
- Coding agents: unified mechanism to package and ship generated code to production environments.
- ML infrastructure: cross-language support for Python, C++, and Rust, and DSLs.

It has the following technical features:

- DLPack-compatible Tensor data ABI to seamlessly support many frameworks such as PyTorch, JAX, CuPy and others that support DLPack convention.
- Compact value and function calling convention for common data types in machine learning.
- Stable, minimal, and flexible C ABI to support machine learning system use-cases.
- Out-of-the-box multi-language support for Python, C++, Rust, and future path for other languages.

With these technical solutions, we can enable better **interoperability** across machine learning frameworks,
libraries, kernel DSLs, and coding agents, **ship one wheel** to support multiple frameworks and Python versions (including free-threaded python),
and build infrastructure solutions across environments.

## Status and Release Versioning

C ABI stability is the top priority of this effort. We also prioritize minimalism and
efficiency in the core so it is portable and can be used broadly.
We are current in the RFC stage, which means the main features are complete and ABI stable.
We also recognize potential needs for evolution to ensure it works best for the machine
learning systems community, and would like to work together collectively with the community for such evolution.
The RFC stage is a period where we are working with the open source communities
to ensure we evolve the ABI to meet the potential needs of frameworks.

Releases during the RFC stage will be `0.X.Y`, where bumps in `X` indicate C ABI-breaking changes
and `Y` indicates other changes. We anticipate the RFC stage will last for a few months, then we will start to follow
[Semantic Versioning](https://packaging.python.org/en/latest/discussions/versioning/)
(`major.minor.patch`) going forward.
