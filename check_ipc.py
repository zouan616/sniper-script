"""
ipctrace.py

Write a trace of instantaneous IPC values for all cores.
First argument is either a filename, or none to write to standard output.
Second argument is the interval size in nanoseconds (default is 10000)
"""

import sys, os, sim

# from energystats import *# print dir(energystats.Energystats())
# print energystats.dvfs_table
print "Im here"
avg_ipcs = []

for core in range(sim.config.ncores):
    avg_ipcs.append(0)
    sim.dvfs.set_frequency(core,2000)
# import numpy as np
n_steps = 0
class IpcTrace:
  def setup(self, args):
    args = dict(enumerate((args or '').split(':')))
    filename = args.get(0, None)
    # interval_ns = long(args.get(1, 10000))
    interval_ns = long(args.get(1,1000))
    print "Interval:", interval_ns
    if filename:
      self.fd = file(os.path.join(sim.config.output_dir, filename), 'w')
      self.isTerminal = False
    else:
      self.fd = sys.stdout
      self.isTerminal = True
    self.sd = sim.util.StatsDelta()
    self.stats = {
      'time': [ self.sd.getter('performance_model', core, 'elapsed_time') for core in range(sim.config.ncores) ],
      'ffwd_time': [ self.sd.getter('fastforward_performance_model', core, 'fastforwarded_time') for core in range(sim.config.ncores) ],
      'instrs': [ self.sd.getter('performance_model', core, 'instruction_count') for core in range(sim.config.ncores) ],
      'coreinstrs': [ self.sd.getter('core', core, 'instructions') for core in range(sim.config.ncores) ],
    }
    sim.util.Every(interval_ns * sim.util.Time.NS, self.periodic, statsdelta = self.sd, roi_only = True)

  def periodic(self, time, time_delta):
    global n_steps
    n_steps += 1



    # for core in range(sim.config.ncores):
    #     sim.dvfs.set_frequency(core,1000)
    # global counter
    # if counter == 5:
    #     for core in range(sim.config.ncores):
    #         sim.dvfs.set_frequency(core, 3000) ## Number is in MHz
    # if counter == 0:
    #     for core in range(sim.config.ncores):
    #         sim.dvfs.set_frequency(core, 1000)
    # for core in range(sim.config.ncores):
    #     print "DVFS per Core:", sim.dvfs.get_frequency(core)
    if self.isTerminal:
      self.fd.write('[IPC] ')
    self.fd.write('%u ns' % (time / 1e6)) # Time in ns
    qq = 0
    for core in range(sim.config.ncores):
      # detailed-only IPC
      cycles = (self.stats['time'][core].delta - self.stats['ffwd_time'][core].delta) * sim.dvfs.get_frequency(core) / 1e9 # convert fs to cycles
      instrs = self.stats['instrs'][core].delta
      ipc = instrs / (cycles or 1) # Avoid division by zero
      #self.fd.write(' %.3f' % ipc)

      # include fast-forward IPCs
      cycles = self.stats['time'][core].delta * sim.dvfs.get_frequency(core) / 1e9 # convert fs to cycles
      instrs = self.stats['coreinstrs'][core].delta
      ipc = instrs / (cycles or 1)
      self.fd.write(' %.3f' % ipc)

      avg_ipcs[qq] = (n_steps * avg_ipcs[qq] + ipc) / (n_steps + 1)
      print(avg_ipcs)
      if ipc > 0.8 * avg_ipcs[qq]:
          sim.dvfs.set_frequency(core, 2000)
      else:
          sim.dvfs.set_frequency(core, 1600)
    self.fd.write('\n')


sim.util.register(IpcTrace())
