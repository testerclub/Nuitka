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
""" Nodes for functions and their creations.

Lambdas are functions too. The functions are at the core of the language and have their
complexities.

"""

from .NodeBases import (
    CPythonExpressionChildrenHavingBase,
    CPythonParameterHavingNodeBase,
    CPythonExpressionMixin,
    CPythonChildrenHaving,
    CPythonClosureTaker
)

from .IndicatorMixins import (
    MarkUnoptimizedFunctionIndicator,
    MarkContainsTryExceptIndicator,
    MarkLocalsDictIndicator,
    MarkGeneratorIndicator
)

from nuitka import Variables, Utils

class CPythonExpressionFunctionBody( CPythonChildrenHaving, CPythonParameterHavingNodeBase, \
                                     CPythonClosureTaker, MarkContainsTryExceptIndicator, \
                                     CPythonExpressionMixin, MarkGeneratorIndicator, \
                                     MarkLocalsDictIndicator, MarkUnoptimizedFunctionIndicator ):
    # We really want these many ancestors, as per design, we add properties via base class
    # mixins a lot, pylint: disable=R0901

    kind = "EXPRESSION_FUNCTION_BODY"

    early_closure = False

    named_children = ( "body", )

    def __init__( self, provider, name, doc, parameters, source_ref ):
        code_prefix = "function"

        if name == "<lambda>":
            name = "lambda"
            code_prefix = name

            self.is_lambda = True
        else:
            self.is_lambda = False

        if name == "<listcontraction>":
            code_prefix = "listcontr"
            name = ""

            self.local_locals = Utils.python_version >= 300
        else:
            self.local_locals = True

        if name == "<setcontraction>":
            code_prefix = "setcontr"
            name = ""

        if name == "<dictcontraction>":
            code_prefix = "dictcontr"
            name = ""

        if name == "<genexpr>":
            code_prefix = "genexpr"
            name = ""

            self.is_genexpr = True

        else:
            self.is_genexpr = False

        CPythonClosureTaker.__init__(
            self,
            provider = provider
        )

        CPythonParameterHavingNodeBase.__init__(
            self,
            name        = name,
            code_prefix = code_prefix,
            parameters  = parameters,
            source_ref  = source_ref
        )

        CPythonChildrenHaving.__init__(
            self,
            values = {}
        )

        MarkContainsTryExceptIndicator.__init__( self )

        MarkGeneratorIndicator.__init__( self )

        MarkLocalsDictIndicator.__init__( self )

        MarkUnoptimizedFunctionIndicator.__init__( self )

        self.doc = doc

    def getDetails( self ):
        return {
            "name"       : self.getFunctionName(),
            "parameters" : self.getParameters(),
            "provider"   : self.provider,
            "doc"        : self.doc
        }

    def getDetail( self ):
        return "named %s with %s" % ( self.name, self.parameters )

    def getFunctionName( self ):
        if self.is_lambda:
            return "<lambda>"
        elif self.is_genexpr:
            return "<genexpr>"
        else:
            return self.name

    def getDoc( self ):
        return self.doc

    def getLocalVariableNames( self ):
        return Variables.getNames( self.getLocalVariables() )

    def getLocalVariables( self ):
        return [
            variable for
            variable in
            self.providing.values()
            if variable.isLocalVariable()
        ]

    def getUserLocalVariables( self ):
        return tuple(
            variable for
            variable in
            self.providing.values()
            if variable.isLocalVariable() and not variable.isParameterVariable()
        )

    def getVariables( self ):
        return self.providing.values()

    def getVariableForAssignment( self, variable_name ):
        # print ( "ASS func", self, variable_name )

        if self.hasTakenVariable( variable_name ):
            result = self.getTakenVariable( variable_name )
        else:
            result = self.getProvidedVariable( variable_name )

        return result

    def getVariableForReference( self, variable_name ):
        # print ( "REF func", self, variable_name )

        if self.hasProvidedVariable( variable_name ):
            result = self.getProvidedVariable( variable_name )
        else:
            # For exec containing/star import containing, get a closure variable and if it
            # is a module variable, only then make it a maybe local variable.
            result = self.getClosureVariable(
                variable_name = variable_name
            )

            if self.isUnoptimized() and result.isModuleVariable():
                result = Variables.MaybeLocalVariable(
                    owner         = self,
                    variable_name = variable_name
                )

            # Remember that we need that closure for something.
            self.registerProvidedVariable( result )

        return result

    def getVariableForClosure( self, variable_name ):
        # print( "createProvidedVariable", self, variable_name )

        if self.hasProvidedVariable( variable_name ):
            return self.getProvidedVariable( variable_name )
        else:
            return self.provider.getVariableForClosure( variable_name )

    def createProvidedVariable( self, variable_name ):
        # print( "createProvidedVariable", self, variable_name )

        if self.local_locals:
            return Variables.LocalVariable(
                owner         = self,
                variable_name = variable_name
            )
        else:
            # Make sure the provider knows it has to provide a variable of this name for
            # the assigment.
            self.provider.getVariableForAssignment(
                variable_name = variable_name
            )

            return self.getClosureVariable(
                variable_name = variable_name
            )

    getBody = CPythonChildrenHaving.childGetter( "body" )
    setBody = CPythonChildrenHaving.childSetter( "body" )

    def needsCreation( self ):
        return not self.parent.isExpressionFunctionCall()

    def computeNode( self, constraint_collection ):
        # Function body is quite irreplacable.
        return self, None, None

    def isCompileTimeConstant( self ):
        # TODO: It's actually pretty much compile time accessible mayhaps.
        return None

    def mayHaveSideEffects( self, constraint_collection ):
        # The function definition has no side effects, calculating the defaults would be,
        # but that is done outside of this.
        return False

    def makeCloneAt( self, source_ref ):
        result = self.__class__(
            provider   = self.provider,
            name       = self.name,
            doc        = self.name,
            # TODO: Clone parameters too, when we start to mutate them.
            parameters = self.parameters,
            source_ref =  source_ref
        )

        result.setBody(
            self.getBody().makeCloneAt( source_ref )
        )

        return result


class CPythonExpressionFunctionBodyDefaulted( CPythonExpressionChildrenHavingBase ):
    kind = "EXPRESSION_FUNCTION_BODY_DEFAULTED"

    named_children = ( "defaults", "function_body", )

    def __init__( self, defaults, function_body, source_ref ):
        CPythonExpressionChildrenHavingBase.__init__(
            self,
            values     = {
                "function_body" : function_body,
                "defaults"      : tuple( defaults )
            },
            source_ref = source_ref
        )

    getFunctionBody = CPythonExpressionChildrenHavingBase.childGetter( "function_body" )
    getDefaults = CPythonExpressionChildrenHavingBase.childGetter( "defaults" )

    def computeNode( self, constraint_collection ):
        # Function body is quite irreplacable.
        return self, None, None

    def isCompileTimeConstant( self ):
        # TODO: It's actually pretty much compile time accessible mayhaps.
        return None


class CPythonExpressionFunctionCall( CPythonExpressionChildrenHavingBase ):
    kind = "EXPRESSION_FUNCTION_CALL"

    named_children = ( "function_body", "values" )

    def __init__( self, function_body, values, source_ref ):
        assert function_body.isExpressionFunctionBody()

        CPythonExpressionChildrenHavingBase.__init__(
            self,
            values     = {
                "function_body" : function_body,
                "values"        : tuple( values ),
            },
            source_ref = source_ref
        )

    def computeNode( self, constraint_collection ):
        return self, None, None

    getFunctionBody = CPythonExpressionChildrenHavingBase.childGetter( "function_body" )
    getArgumentValues = CPythonExpressionChildrenHavingBase.childGetter( "values" )
