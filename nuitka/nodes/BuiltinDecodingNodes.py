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
""" Builtin ord/chr nodes

These are good for optimizations, as they give a very well known result. In the case of
'chr', it's one of 256 strings, and in case of 'ord' it's one of 256 numbers, so these can
answer quite a few questions at compile time.

"""

from .NodeBases import CPythonExpressionBuiltinSingleArgBase

from nuitka.transform.optimizations import BuiltinOptimization


class CPythonExpressionBuiltinOrd( CPythonExpressionBuiltinSingleArgBase ):
    kind = "EXPRESSION_BUILTIN_ORD"

    builtin_spec = BuiltinOptimization.builtin_ord_spec

    def isKnownToBeIterable( self, count ):
        return False


class CPythonExpressionBuiltinChr( CPythonExpressionBuiltinSingleArgBase ):
    kind = "EXPRESSION_BUILTIN_CHR"

    builtin_spec = BuiltinOptimization.builtin_chr_spec

    def isKnownToBeIterable( self, count ):
        return count is None or count == 1
