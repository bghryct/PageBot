#!/bin/bash
export WONT_FIX=invalid-name,bad-indentation,trailing-newlines,wrong-import-position,fixme,c-extension-no-member
export CATCHALL_MAY_FIX_LATER=no-else-continue,line-too-long,trailing-whitespace,duplicate-code,bad-whitespace,no-name-in-module,bad-continuation,no-value-for-parameter,too-many-arguments,too-many-locals,unused-argument,pointless-string-statement,using-constant-test,invalid-encoded-data,too-many-instance-attributes,too-few-public-methods,attribute-defined-outside-init,protected-access,wrong-import-order,missing-final-newline,mixed-indentation,unused-variable,no-member,too-many-function-args,unexpected-keyword-arg,bare-except,no-self-use,no-method-argument,function-redefined,too-many-public-methods,anomalous-backslash-in-string,too-many-branches,arguments-differ,reimported,too-many-boolean-expressions,too-many-statements,no-self-argument,unnecessary-pass,keyword-arg-before-vararg,not-a-mapping,multiple-statements,inconsistent-return-statements,pointless-statement,ungrouped-imports,unnecessary-semicolon,no-else-return,old-style-class,too-many-nested-blocks,unsubscriptable-object,too-many-lines,unidiomatic-typecheck,bare-except,simplifiable-if-statement,too-many-return-statements,blacklisted-name,exec-used,not-callable,eval-used,empty-docstring,super-init-not-called,unreachable,expression-not-assigned,consider-using-enumerate,unbalanced-tuple-unpacking,global-statement,duplicate-key,anomalous-unicode-escape-in-string,no-init,redefined-argument-from-local,missing-docstring,superfluous-parens,unused-wildcard-import,redefined-outer-name,consider-iterating-dictionary,invalid-unary-operand-type,wildcard-import
export PYLINT="pylint --disable=$WONT_FIX,$CATCHALL_MAY_FIX_LATER"

find . -iname "*.py" | xargs $PYLINT
#$PYLINT *.py # > pylint.log
#$PYLINT */*.py # > pylint.log
#$PYLINT */*/*.py # > pylint.log
