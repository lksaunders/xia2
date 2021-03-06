from __future__ import absolute_import, division

def to_shelxcde(hklin, prefix, sites=0):
  '''Read hklin (unmerged reflection file) and generate SHELXC input file
  and HKL file'''

  from iotbx.reflection_file_reader import any_reflection_file
  from iotbx.shelx.hklf import miller_array_export_as_shelx_hklf
  reader = any_reflection_file(hklin)
  intensities = [ma for ma in reader.as_miller_arrays(merge_equivalents=False)
                 if ma.info().labels == ['I', 'SIGI']][0]
  mtz_object = reader.file_content()
  indices = reader.file_content().extract_original_index_miller_indices()
  intensities = intensities.customized_copy(indices=indices, info=intensities.info())
  with open('%s.hkl' % prefix, 'wb') as hkl_file_handle:
    miller_array_export_as_shelx_hklf(intensities, hkl_file_handle)
  uc = intensities.unit_cell().parameters()
  sg = intensities.space_group().type().lookup_symbol().replace(' ', '')
  open('%s.sh' % prefix, 'w').write('\n'.join([
    'shelxc %s << eof' % prefix,
    'cell %f %f %f %f %f %f' % uc,
    'spag %s' % sg,
    'sad %s.hkl' % prefix,
    'find %d' % sites,
    'maxm %d' % ((2 * intensities.data().size() // 1000000) + 1),
    'eof', '']))

if __name__ == '__main__':
  import sys

  if len(sys.argv) > 3:
    sites = int(sys.argv[3])
    to_shelxcde(sys.argv[1], sys.argv[2], sites)
  else:
    to_shelxcde(sys.argv[1], sys.argv[2])
