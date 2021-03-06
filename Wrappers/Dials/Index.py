#!/usr/bin/env python
# Index.py
#
#   Copyright (C) 2014 Diamond Light Source, Richard Gildea, Graeme Winter
#
#   This code is distributed under the BSD license, a copy of which is
#   included in the root directory of this package.
#
# Autoindex using the DIALS code: assumes spots found from same.

from __future__ import absolute_import, division
import os

from xia2.Handlers.Phil import PhilIndex

def Index(DriverType = None):
  '''A factory for IndexWrapper classes.'''

  from xia2.Driver.DriverFactory import DriverFactory
  DriverInstance = DriverFactory.Driver(DriverType)

  class IndexWrapper(DriverInstance.__class__):

    def __init__(self):
      DriverInstance.__class__.__init__(self)
      self.set_executable('dials.index')

      self._sweep_filenames = []
      self._spot_filenames = []
      self._unit_cell = None
      self._space_group = None
      self._maximum_spot_error = None
      self._detector_fix = None
      self._beam_fix = None
      self._indexing_method = "fft3d"
      self._p1_cell = None
      self._indxr_input_cell = None
      self._indxr_input_lattice = None
      self._reflections_per_degree = None
      self._fft3d_n_points = None
      self._histogram_binning = None

      self._experiment_filename = None
      self._indexed_filename = None

      self._nref = None
      self._rmsd_x = None
      self._rmsd_y = None
      self._rmsd_z = None

      self._max_cell = None
      self._min_cell = None

      self._d_min_start = None

      self._phil_file = None
      self._outlier_algorithm = None
      self._close_to_spindle_cutoff = None

    def add_sweep_filename(self, sweep_filename):
      self._sweep_filenames.append(sweep_filename)

    def add_spot_filename(self, spot_filename):
      self._spot_filenames.append(spot_filename)

    def set_indexer_input_lattice(self, lattice):
      self._indxr_input_lattice = lattice

    def set_indexer_user_input_lattice(self, user):
      self._indxr_user_input_lattice = user

    def set_indexer_input_cell(self, cell):
      if not type(cell) == type(()):
        raise RuntimeError, 'cell must be a 6-tuple de floats'

      if len(cell) != 6:
        raise RuntimeError, 'cell must be a 6-tuple de floats'

      self._indxr_input_cell = tuple(map(float, cell))

    def set_maximum_spot_error(self, maximum_spot_error):
      self._maximum_spot_error = maximum_spot_error

    def set_detector_fix(self, detector_fix):
      self._detector_fix = detector_fix

    def set_beam_fix(self, beam_fix):
      self._beam_fix = beam_fix

    def set_indexing_method(self, method):
      self._indexing_method = method

    def set_indexing_method(self):
      return self._indexing_method

    def set_reflections_per_degree(self, reflections_per_degree):
      self._reflections_per_degree = int(reflections_per_degree)

    def set_fft3d_n_points(self, n_points):
      self._fft3d_n_points = n_points

    def set_histogram_binning(self, histogram_binning):
      self._histogram_binning = histogram_binning

    def get_sweep_filenames(self):
      return self._sweep_filenames

    def get_experiments_filename(self):
      return self._experiment_filename

    def get_indexed_filename(self):
      return self._indexed_filename

    def get_p1_cell(self):
      return self._p1_cell

    def set_phil_file(self, phil_file):
      self._phil_file = phil_file

    def set_outlier_algorithm(self, outlier_algorithm):
      self._outlier_algorithm = outlier_algorithm

    def get_nref_rmsds(self):
      return self._nref, (self._rmsd_x, self._rmsd_y, self._rmsd_z)

    def set_max_cell(self, max_cell):
      self._max_cell = max_cell

    def set_min_cell(self, min_cell):
      self._min_cell = min_cell

    def set_d_min_start(self, d_min_start):
      self._d_min_start = d_min_start

    def set_close_to_spindle_cutoff(self, close_to_spindle_cutoff):
      self._close_to_spindle_cutoff = close_to_spindle_cutoff

    def run(self, method):
      from xia2.Handlers.Streams import Debug
      Debug.write('Running dials.index')

      self.clear_command_line()
      for f in self._sweep_filenames:
        self.add_command_line(f)
      for f in self._spot_filenames:
        self.add_command_line(f)
      self.add_command_line('indexing.method=%s' % method)
      nproc = PhilIndex.params.xia2.settings.multiprocessing.nproc
      self.set_cpu_threads(nproc)
      self.add_command_line('indexing.nproc=%i' % nproc)
      if PhilIndex.params.xia2.settings.small_molecule == True:
        self.add_command_line('filter_ice=false')
      if self._reflections_per_degree is not None:
        self.add_command_line(
          'reflections_per_degree=%i' %self._reflections_per_degree)
      if self._fft3d_n_points is not None:
        self.add_command_line(
          'fft3d.reciprocal_space_grid.n_points=%i' %self._fft3d_n_points)
      if self._close_to_spindle_cutoff is not None:
        self.add_command_line(
          'close_to_spindle_cutoff=%f' %self._close_to_spindle_cutoff)
      if self._outlier_algorithm:
        self.add_command_line('outlier.algorithm=%s' % self._outlier_algorithm)
      if self._max_cell:
        self.add_command_line('max_cell=%d' % self._max_cell)
      if self._min_cell:
        self.add_command_line('min_cell=%d' % self._min_cell)
      if self._histogram_binning is not None:
        self.add_command_line('max_cell_estimation.histogram_binning=%s' %self._histogram_binning)
      if self._d_min_start:
        self.add_command_line('d_min_start=%f' % self._d_min_start)
      if self._indxr_input_lattice is not None:
        from xia2.Experts.SymmetryExpert import lattice_to_spacegroup_number
        self._symm = lattice_to_spacegroup_number(
            self._indxr_input_lattice)
        self.add_command_line('known_symmetry.space_group=%s' % self._symm)
      if self._indxr_input_cell is not None:
        self.add_command_line(
          'known_symmetry.unit_cell="%s,%s,%s,%s,%s,%s"' %self._indxr_input_cell)
      if self._maximum_spot_error:
        self.add_command_line('maximum_spot_error=%.f' %
                              self._maximum_spot_error)
      if self._detector_fix:
        self.add_command_line('detector.fix=%s' % self._detector_fix)
      if self._beam_fix:
        self.add_command_line('beam.fix=%s' % self._beam_fix)
      if self._phil_file is not None:
        self.add_command_line("%s" %self._phil_file)

      self._experiment_filename = os.path.join(
        self.get_working_directory(), '%d_experiments.json' %self.get_xpid())
      self._indexed_filename = os.path.join(
        self.get_working_directory(), '%d_indexed.pickle' %self.get_xpid())
      self.add_command_line("output.experiments=%s" %self._experiment_filename)
      self.add_command_line("output.reflections=%s" %self._indexed_filename)

      self.start()
      self.close_wait()
      self.check_for_errors()

      if not os.path.isfile(self._experiment_filename) or \
         not os.path.isfile(self._indexed_filename):
        raise RuntimeError(
          "dials.index failed, see log file for more details: %s"
          %self.get_log_file())

      from dials.array_family import flex
      from dxtbx.serialize import load
      self._experiment_list = load.experiment_list(self._experiment_filename)
      self._reflections = flex.reflection_table.from_pickle(
        self._indexed_filename)

      crystal = self._experiment_list.crystals()[0]
      self._p1_cell = crystal.get_unit_cell().parameters()

      refined_sel = self._reflections.get_flags(self._reflections.flags.used_in_refinement)
      refl = self._reflections.select(refined_sel)
      xc, yc, zc = refl['xyzcal.px'].parts()
      xo, yo, zo = refl['xyzobs.px.value'].parts()
      import math
      self._nref = refl.size()
      self._rmsd_x = math.sqrt(flex.mean(flex.pow2(xc - xo)))
      self._rmsd_y = math.sqrt(flex.mean(flex.pow2(yc - yo)))
      self._rmsd_z = math.sqrt(flex.mean(flex.pow2(zc - zo)))

  return IndexWrapper()
