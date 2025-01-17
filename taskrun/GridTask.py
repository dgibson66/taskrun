"""
 * Copyright (c) 2012-2016, Nic McDonald
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - Neither the name of prim nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
"""
# Python 3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os
import subprocess

from .Task import Task

class GridTask(Task):
  """
  This class is a Task that runs as a grid process. See
  http://gridscheduler.sourceforge.net/
  """

  def __init__(self, manager, name, command):
    """
    This instiates a Gridobject with a subprocess command

    Args:
      manager (TaskManager) : passed to Task.__init__()
      name (str)            : passed to Task.__init__()
      command (str)         : the command to be run
    """

    super(GridTask, self).__init__(manager, name)
    self._command = command
    self._stdout_file = None
    self._stderr_file = None
    self._queues = set()
    self._grid_resources = dict()
    self.stdout = None
    self.stderr = None
    self._proc = None

  @property
  def command(self):
    """
    Returns:
      (str) : the process's command
    """
    return self._command

  @command.setter
  def command(self, value):
    """
    Sets the process's command

    Args:
      value (str) : the new command
    """
    self._command = value

  @property
  def stdout_file(self):
    """
    Returns:
      (str) : filename for stdout text
    """
    return self._stdout_file

  @stdout_file.setter
  def stdout_file(self, filename):
    """
    Sets the filename of the stdout text

    Args:
      filename (str) : a filename for stdout text
    """
    self._stdout_file = filename

  @property
  def stderr_file(self):
    """
    Returns:
      (str) : filename for stderr text
    """
    return self._stderr_file

  @stderr_file.setter
  def stderr_file(self, filename):
    """
    Sets the filename of the stderr text.

    Args:
      filename (str) : a filename for stderr text
    """
    self._stderr_file = filename

  @property
  def queues(self):
    """
    Returns:
      (set<str>) : the queues allowed to run in
    """
    return self._queues

  @queues.setter
  def queues(self, value):
    """
    Sets the allowed queues to run in

    Args:
      value (strs): the queues
    """
    self._queues = set(value)

  @property
  def grid_resources(self):
    """
    Returns:
      (dict<str,str>) : the resources in the grid
    """
    return self._grid_resources

  @grid_resources.setter
  def grid_resources(self, value):
    """
    Sets the grid resources for this task

    Args:
      value (strs): the resources
    """
    self._grid_resources = dict(value)

  def describe(self):
    """
    See Task.describe()
    """
    return self._build_command()

  def _build_command(self):
    """
    This builds the command string for this grid task.

    Returns:
      (str) : the full command line
    """
    cmd = ['qsub',
           '-V',            # copy full environment
           '-b', 'yes',     # execute binary file
           '-sync', 'yes',  # wait for job to complete before exiting
           '-cwd',          # use current working directory
           '-N', self.name] # name of the task
    if self._stdout_file:
      cmd.extend(['-o', self._stdout_file])
    else:
      cmd.extend(['-o', os.devnull])
    if self._stderr_file:
      cmd.extend(['-e', self._stderr_file])
    else:
      cmd.extend(['-e', os.devnull])
    if len(self._queues) > 0:
      cmd.extend(['-q', ','.join(self._queues)])
    if len(self._grid_resources) > 0:
      cmd.extend(['-l', ','.join(
        ['{0}={1}'.format(k, v) for k, v in self._grid_resources.items()])])
    cmd.append(self._command)
    return ' '.join(cmd)

  def execute(self):
    """
    See Task.execute()
    """

    # start the command
    cmd = self._build_command()
    self._proc = subprocess.Popen(
      cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # wait for the process to finish, collect output
    self.stdout, self.stderr = self._proc.communicate()
    if self.stdout is not None:
      self.stdout = self.stdout.decode('utf-8')
    if self.stderr is not None:
      self.stderr = self.stderr.decode('utf-8')

    # check the return code
    ret = self._proc.returncode
    if ret == 0:
      return None
    else:
      return ret

  def kill(self):
    """
    See Task.kill()
    This implementation calls subprocess.kill()
    """

    self.killed = True

    # there is a chance the proc hasn't been created yet or has already
    #  completed
    if self._proc:
      try:
        self._proc.kill()
      except ProcessLookupError:
        pass
