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
""" Return node

This one exits functions. The only other exit is the default exit of functions with 'None'
value, if no return is done.
"""

from .NodeBases import CPythonExpressionChildrenHavingBase


class CPythonStatementReturn( CPythonExpressionChildrenHavingBase ):
    kind = "STATEMENT_RETURN"

    named_children = ( "expression", )

    def __init__( self, expression, source_ref ):
        CPythonExpressionChildrenHavingBase.__init__(
            self,
            values     = {
                "expression" : expression
            },
            source_ref = source_ref
        )

    getExpression = CPythonExpressionChildrenHavingBase.childGetter( "expression" )

    def isStatementAbortative( self ):
        return True

    def mayRaiseException( self, exception_type ):
        return self.getExpression().mayRaiseException( exception_type )
