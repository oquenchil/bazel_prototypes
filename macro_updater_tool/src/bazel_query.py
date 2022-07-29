import utils as utils
import string
import re
import os
import sys
import pathlib

bazel_query = string.Template("""
bazel $query
""")

bazel_query_output = {}

class QueryTargetResult:
  def __init__(self, pkg, target, kind, expanded_target_with_all_attrs, macro_stacktrace):
    self.pkg = pkg
    self.target = target
    self.kind = kind
    self.expanded_target_with_all_attrs = expanded_target_with_all_attrs
    self.macro_stacktrace = macro_stacktrace

  def __repr__(self):
    str_builder = ["-------"]
    str_builder.append("%s %s:%s" % (self.kind, self.pkg, self.target))
    str_builder.append(self.expanded_target_with_all_attrs)
    str_builder.append("stacktrace:")
    for entry in self.macro_stacktrace:
      str_builder.append("   " + str(entry))
    return "\n" + "\n".join(str_builder) + "\n----------"

class MacroStackTraceEntry:
  def __init__(self, filename, line_number, macro_name):
    self.filename = filename
    self.line_number = line_number
    self.macro_name = macro_name

  def __repr__(self):
    return " - ".join([self.filename, self.line_number, self.macro_name])

def _parse_stack_trace(lines):
  filepath_regex = re.compile(".*/(.*):(.*):.*in (.*)")
  stack_trace = []
  for line in lines:
    if line.startswith("#   /virtual_builtins_bzl/"):
      # Reached a builtin macro which we are not interested of. We have the
      # full stack trace
      break
    if not line.startswith("#   /"):
      raise Exception(
          "Stacktrace entry should start with #   /google/src/. Started with: %s"
          % line[:95])

    groups = filepath_regex.match(line)
    stack_trace.append(MacroStackTraceEntry(filename=groups.group(1), line_number = groups.group(2), macro_name=groups.group(3)))

  if "<toplevel>" != stack_trace[0].macro_name:
    raise Exception("Stacktrace does not contain a BUILD file as first element")

  return stack_trace

def _get_indexes_of_stack_trace_in_output(lines):
    # When --output=build, the last few lines for a target are a comment containing
    # the stack trace. They start with the comment "# Rule"
    index_first_line_stack_trace = None
    for i, line in enumerate(lines):
      if line.startswith("# Rule"):
        index_first_line_stack_trace = i
        break
    assert index_first_line_stack_trace != None

    index_last_line_stack_trace = index_first_line_stack_trace + 1
    for line in lines[index_first_line_stack_trace + 1:]:
      if not line.startswith("#   /"):
        break
      index_last_line_stack_trace +=1

    return (index_first_line_stack_trace, index_last_line_stack_trace)

# FIXME: Comment explaining how we obtain the target.
def query_target(target, workspace = None):
  pkg = utils.package(target)
  name = utils.target_name(target)
  if pkg in bazel_query_output:
    if name == "all":
      results = []
      for query_target_result in bazel_query_output[pkg].values():
        results.append(query_target_result)
      return results
    elif name in bazel_query_output[pkg]:
      return [bazel_query_output[pkg][name]]
    else:
      raise Exception("Target %s not in pkg" % target)

  target_to_query_target_result = {}
  bazel_query_output[pkg] = target_to_query_target_result

  output = utils.run_command(
      bazel_query, query="query --output=build %s:all" % pkg)[0]

  # This separates the output from bazel query --output=build into all the
  # different targets.
  results = re.split("# /", output)

  name_regex = re.compile(".*name = \"(.*)\",")
  for result in results[1:]:
    lines = result.split("\n")
    # e.g. cc_binary(
    second_line_which_has_kind = lines[1]
    kind = second_line_which_has_kind[:-1]
    #  name = "foo"
    third_line_which_has_name = lines[2]
    name = name_regex.match(third_line_which_has_name).group(1)

    index_1st_line, index_last_line = _get_indexes_of_stack_trace_in_output(lines)
    expanded_target_with_all_attrs = "\n".join(lines[1:index_1st_line])

    stack_trace = _parse_stack_trace(lines[index_1st_line + 1:index_last_line])
    target_to_query_target_result[name] = QueryTargetResult(pkg, name, kind, expanded_target_with_all_attrs, stack_trace)

  return query_target(target)

if __name__ == "__main__":
  #print(query_target("//third_party/python_runtime/v3_9:tkinter"))
  print(str(query_target(sys.argv[1])))
