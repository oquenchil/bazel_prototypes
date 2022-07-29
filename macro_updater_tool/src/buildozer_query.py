import utils as utils
import string
import re
import os
import sys
import pathlib

rule_print_buildozer_template = string.Template("""
buildozer 'print rule' $target_location
""")

def buildozer_target(target_location):
  return utils.run_command(
      rule_print_buildozer_template, target_location=target_location)[0]

if __name__ == "__main__":
  #print(query_target("//third_party/python_runtime/v3_9:tkinter"))
  print(str(query_target(sys.argv[1])))
