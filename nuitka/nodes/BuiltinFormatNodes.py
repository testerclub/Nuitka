#     Copyright 2012, Kay Hayen, mailto:kayhayen@gmx.de
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
""" Format nodes bin/oct/hex.

These will most often be used for outputs, and the hope is, the type prediction or the
result prediction will help to be smarter, but generally these should not be that much
about performance critical.

"""
from .NodeBases import CPythonExpressionBuiltinSingleArgBase

from nuitka.transform.optimizations import BuiltinOptimization

class CPythonExpressionBuiltinBin( CPythonExpressionBuiltinSingleArgBase ):
    kind = "EXPRESSION_BUILTIN_BIN"

    builtin_spec = BuiltinOptimization.builtin_bin_spec

class CPythonExpressionBuiltinOct( CPythonExpressionBuiltinSingleArgBase ):
    kind = "EXPRESSION_BUILTIN_OCT"

    builtin_spec = BuiltinOptimization.builtin_oct_spec

class CPythonExpressionBuiltinHex( CPythonExpressionBuiltinSingleArgBase ):
    kind = "EXPRESSION_BUILTIN_HEX"

    builtin_spec = BuiltinOptimization.builtin_hex_spec
