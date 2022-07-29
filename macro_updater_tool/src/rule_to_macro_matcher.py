import bazel_query
import buildozer_query
import utils as utils
import string
import re
import os
import sys
import pathlib
import ast


# Not yet handling lots of edge cases
# e.g.:
# 1. //foo:foo is the same as "foo" or ":foo" within the same pkg
# 2. The value of in the buildozer entry being a constant
# 3. Only handles strings and lists. But no selects for example.
#
# Only works for deps right now but can be expanded for other attributes.

def _parse_ast(text):
  parsed_text = ast.parse(text)
  attributes = {}
  for keyword in parsed_text.body[0].value.keywords:
    value = None
    if isinstance(keyword.value, ast.List):
      parsed_list = []
      for elt in keyword.value.elts:
        parsed_list.append(ast.unparse(elt))
      value = parsed_list
    else:
      value = ast.unparse(keyword.value)

    attributes[keyword.arg] = value

  return attributes

if __name__ == "__main__":
  target = sys.argv[1]

  bazel_query_result = bazel_query.query_target(target)[0]
  buildozer_target = "%s:%%%s" % (bazel_query_result.pkg, bazel_query_result.macro_stacktrace[0].line_number)

  macro_attrs = _parse_ast(buildozer_query.buildozer_target(buildozer_target))

  real_attrs = _parse_ast(bazel_query_result.expanded_target_with_all_attrs)

  macro_attribute_name = None
  final_values = real_attrs["deps"]
  for final_value in final_values:
    if not macro_attribute_name:
      for attribute_name, value in macro_attrs.items():
        if type(value) != list:
          continue

        if final_value in value:
          macro_attribute_name = attribute_name
          break

  print("The attribute name on the macro is %s" % macro_attribute_name)

