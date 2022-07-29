import subprocess


# TODO: Add option to output to terminal
def run_command(command_template, **kwargs):
  command = command_template.substitute(**kwargs)

  result = subprocess.Popen(
      command, shell=True, stdout=subprocess.PIPE,
      stderr=subprocess.PIPE).communicate()

  return result[0].decode("utf-8"), result[1].decode("utf-8")


def package(target):
  return target.split(":")[0]


def target_name(target):
  return target.split(":")[1]
