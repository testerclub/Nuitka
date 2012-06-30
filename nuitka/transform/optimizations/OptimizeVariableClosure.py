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
""" Variable closure taking.

Run away, don't read it, quick. Heavily underdocumented rules are implemented here.

"""

from .OptimizeBase import OptimizationVisitorScopedBase

# TODO: The variable closure thing looks like it should be collapsed into tree building,
# this does not at all depend on completion of the node tree. Just the not early closure
# kinds need to make an extra pass, once their body is complete, in order to assign the
# variable.

class VariableClosureLookupVisitorPhase2( OptimizationVisitorScopedBase ):
    """ Variable closure phase 2: Find assignments and early closure references.

        In class context, a reference to a variable must be obeyed immediately, so
        that "variable = variable" takes first "variable" as a closure and then adds
        a new local "variable" to override it from there on. For the not early closure
        case of a function, this will not be done and only assigments shall add local
        variables, and references be ignored until phase 3.
    """

    def onEnterNode( self, node ):
        if node.isExpressionTargetVariableRef():
            if node.getVariable() is None:
                provider = node.getParentVariableProvider()

                node.setVariable(
                    provider.getVariableForAssignment(
                        variable_name = node.getVariableName()
                    )
                )
        elif node.isExpressionVariableRef():
            if node.getVariable() is None:
                provider = node.getParentVariableProvider()

                if provider.isEarlyClosure():
                    node.setVariable(
                        provider.getVariableForReference(
                            variable_name = node.getVariableName()
                        )
                    )


class VariableClosureLookupVisitorPhase3( OptimizationVisitorScopedBase ):
    def onEnterNode( self, node ):
        if node.isExpressionVariableRef() and node.getVariable() is None:
            provider = node.getParentVariableProvider()

            # print "Late reference", node.getVariableName(), "for", provider, "caused at", node, "of", node.getParent()

            node.setVariable(
                provider.getVariableForReference(
                    variable_name = node.getVariableName()
                )
            )

VariableClosureLookupVisitors = (
    VariableClosureLookupVisitorPhase2,
    VariableClosureLookupVisitorPhase3
)
