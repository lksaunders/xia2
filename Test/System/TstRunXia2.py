# System testing: run xia2 and check for zero exit code

def start_xia2():
  import os
  from subprocess import Popen, PIPE

  process = Popen(["xia2"], stdout=PIPE)
  (output, err) = process.communicate()
  exit_code = process.wait()
  if (exit_code != 0):
    exit(exit_code)
  print "OK"

if __name__ == '__main__':
  start_xia2()
