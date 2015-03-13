import os
import sys

if not os.environ.has_key('XIA2_ROOT'):
  raise RuntimeError, 'XIA2_ROOT not defined'
if not 'XIA2CORE_ROOT' in os.environ:
  os.environ['XIA2CORE_ROOT'] = os.path.join(os.environ['XIA2_ROOT'], 'core')

if not os.environ['XIA2_ROOT'] in sys.path:
  sys.path.append(os.path.join(os.environ['XIA2_ROOT']))


from libtbx.containers import OrderedDict

from Handlers.Phil import PhilIndex


class _ImagesetCache(dict):
  pass


imageset_cache = _ImagesetCache()

def load_imagesets(template, directory, id_image=None, image_range=None,
                   use_cache=True):
  global imageset_cache

  full_template_path = os.path.join(directory, template)
  if full_template_path not in imageset_cache or not use_cache:

    from dxtbx.datablock import DataBlockFactory
    from dxtbx.sweep_filenames import locate_files_matching_template_string

    from Handlers.Phil import PhilIndex
    params = PhilIndex.get_python_object()
    read_all_image_headers = params.xia2.settings.read_all_image_headers

    if read_all_image_headers:
      paths = sorted(locate_files_matching_template_string(full_template_path))
      unhandled = []
      datablocks = DataBlockFactory.from_filenames(
        paths, verbose=False, unhandled=unhandled)
      assert len(unhandled) == 0, "unhandled image files identified: %s" % \
          unhandled
      assert len(datablocks) == 1, "1 datablock expected, %d found" % \
          len(datablocks)

    else:
      from dxtbx.datablock import DataBlockTemplateImporter
      importer = DataBlockTemplateImporter([full_template_path])
      datablocks = importer.datablocks

    imagesets = datablocks[0].extract_sweeps()
    assert len(imagesets) > 0, "no imageset found"

    imageset_cache[full_template_path] = OrderedDict()

    reference_geometry = PhilIndex.params.xia2.settings.input.reference_geometry
    if reference_geometry is not None:
      update_with_reference_geometry(imagesets, reference_geometry)

    for imageset in imagesets:
      scan = imageset.get_scan()
      _id_image = scan.get_image_range()[0]
      imageset_cache[full_template_path][_id_image] = imageset

  if id_image is not None:
    return [imageset_cache[full_template_path][id_image]]
  elif image_range is not None:
    for imageset in imageset_cache[full_template_path].values():
      scan = imageset.get_scan()
      scan_image_range = scan.get_image_range()
      if (image_range[0] >= scan_image_range[0] and
          image_range[1] <= scan_image_range[1]):
        imagesets = [imageset[
          image_range[0] - scan_image_range[0]:
          image_range[1] + 1 - scan_image_range[0]]]
        assert len(imagesets[0]) == image_range[1] - image_range[0] + 1, len(imagesets[0])
        return imagesets
  return imageset_cache[full_template_path].values()

def update_with_reference_geometry(imagesets, reference_geometry):
  assert reference_geometry is not None
  from dxtbx.serialize import load
  try:
    experiments = load.experiment_list(
      reference_geometry, check_format=False)
    assert len(experiments.detectors()) == 1
    assert len(experiments.beams()) == 1
    reference_detector = experiments.detectors()[0]
    reference_beam = experiments.beams()[0]
  except Exception, e:
    datablock = load.datablock(reference_geometry)
    assert len(datablock) == 1
    imageset = datablock[0].extract_imagesets()[0]
    reference_detector = imageset.get_detector()
    reference_beam = imageset.get_beam()

  for imageset in imagesets:
    assert reference_detector.is_similar_to(imageset.get_detector())
    imageset.set_beam(reference_beam)
    imageset.set_detector(reference_detector)
