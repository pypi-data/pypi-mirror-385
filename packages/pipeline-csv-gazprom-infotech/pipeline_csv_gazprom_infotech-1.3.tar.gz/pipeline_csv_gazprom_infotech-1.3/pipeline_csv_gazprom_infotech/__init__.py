"""Pipeline csv file to Infotech IPL."""
from pipeline_csv import TypeHorWeld
from pipeline_gazprom_infotech.codes import NAME, Tube
from pipeline_gazprom_infotech.ipl import Weld as WeldAttr, LineObj as LineObjAttr, Defect as DefectAttr
from .diam import DIAM_DECREASE, DIAM_INCREASE


def pipe_type(pipe):
    """Return Infotech code for type of given pipe."""
    if not pipe.seams:
        return Tube.UNKNOWN

    seam = pipe.seams[0]
    typ = Tube.ODNOSHOV
    code = int(seam.object_code)

    if code == TypeHorWeld.NO_WELD:
        typ = Tube.BEZSHOV
    elif code == TypeHorWeld.UNKNOWN:
        typ = Tube.UNKNOWN
    elif code == TypeHorWeld.SPIRAL:
        typ = Tube.SPIRAL
    else:
        if len(pipe.seams) > 1:
            typ = Tube.DVUSHOV

    return typ


def it_orientation(orient):
    """Convert pipeline_csv.Orientation to Infotech format."""
    if orient is None:
        return ""
    return str(round(orient.as_hour_float % 12, 1)).replace('.', ',')


def get_diam_change(pipe):
    """Return start/end diameters for pipe or None."""
    for diam in pipe.diameters:
        if diam.depth_min and diam.depth_max:
            return diam

    return None


def it_dist(dist_mm):
    """Convert mm to cm."""
    return str(int(round(float(dist_mm) / 10.0)))


def it_size(size):
    """Convert size in mm to Infotech format."""
    if size is None:
        return ""
    if not size:
        return ""
    if not int(float(size)):
        return ""

    return str(int(float(size)))


def get_diam_infotech(start, end, diam_list):
    """Find diam change in dict."""
    for diam in diam_list:
        data = diam.get_code(start, end)
        if data is not None:
            return data

    return None


def add_diam_change(xml, diam_row, obj_dict):
    """Add diam change objrcy to IPL xml."""
    start = int(diam_row.depth_min)
    end = int(diam_row.depth_max)
    diam_list = DIAM_INCREASE

    if start > end:
        diam_list = DIAM_DECREASE

    diam = get_diam_infotech(start, end, diam_list)
    if diam is None:
        return 0

    code, name = diam

    attribs = {
      LineObjAttr.TypeId: code,
      LineObjAttr.Dist: it_dist(int(diam_row.dist_od)),
    }
    xml.add_lineobj(attribs)

    if code not in obj_dict:
        obj_dict[code] = name

    return 1


def add_defect(xml, obj, obj_dict, defect_table, custom_handler):
    """Add defect obj to IPL xml and return number of added defects."""
    dtype = defect_table.get(obj.code, None)
    if not dtype:
        return 0

    attribs = {
      DefectAttr.TypeId: str(dtype),
      DefectAttr.Dist: it_dist(obj.row.dist),
      DefectAttr.LOtch: it_size(obj.length),
      DefectAttr.WOtch: it_size(obj.row.width),
      DefectAttr.Vmin: str(obj.row.depth_min),
      DefectAttr.Vmax: str(obj.row.depth_max),
      DefectAttr.Orient1: it_orientation(obj.orient1),
      DefectAttr.Orient2: it_orientation(obj.orient2),
      DefectAttr.Rem: obj.row.comments,
      # DefectAttr.Kbd: "",
      # DefectAttr.Pbez: "",
      # DefectAttr.TimeLimit: "",
      # DefectAttr.PbezPercent: "",
      # DefectAttr.Method: "",
    }
    defekt = xml.add_defekt(attribs)
    if obj.row.custom_data and custom_handler:
        custom_handler(defekt, obj.row.custom_data)

    if dtype not in obj_dict:
        obj_dict[dtype] = NAME[dtype]

    return 1


def add_lineobject(xml, obj, obj_dict, lineobj_table, custom_handler):
    """Add obj to IPL xml and return number of added objects."""
    ltype = lineobj_table.get(int(obj.object_code), None)
    if not ltype:
        return 0

    attribs = {
      LineObjAttr.TypeId: ltype,
      LineObjAttr.Dist: it_dist(obj.dist),
    }
    lineobj = xml.add_lineobj(attribs)
    if obj.object_name and custom_handler:
        custom_handler(lineobj, obj.object_name)

    if ltype not in obj_dict:
        obj_dict[ltype] = NAME[ltype]

    return 1


def add_pipe(pipe, xml, obj_dict, lineobj_table, defect_table, lineobj_custom_handler, defect_custom_handler):
    """Add pipe data to IPL xml."""
    defects, lineobjs = 0, 0
    ptype = pipe_type(pipe)
    if ptype not in obj_dict:
        obj_dict[ptype] = NAME[ptype]

    attribs = {
      WeldAttr.TypeId: ptype,
      WeldAttr.Dist: it_dist(pipe.dist),
      WeldAttr.Num: str(pipe.number),
      WeldAttr.DlTube: it_dist(pipe.length),
      WeldAttr.Thick: str(round(float(pipe.thick) / 10, 1)),
    }

    if ptype in [Tube.ODNOSHOV, Tube.DVUSHOV]:
        attribs[WeldAttr.Psh1] = it_orientation(pipe.seam1)
        attribs[WeldAttr.Psh2] = it_orientation(pipe.seam2)

    xml.add_weld(attribs)

    for i in pipe.lineobjects:
        lineobjs += add_lineobject(xml, i, obj_dict, lineobj_table, lineobj_custom_handler)

    diam_change = get_diam_change(pipe)
    if diam_change:
        lineobjs += add_diam_change(xml, diam_change, obj_dict)

    for i in pipe.defects:
        defects += add_defect(xml, i, obj_dict, defect_table, defect_custom_handler)

    return (defects, lineobjs)


def translate(csvfile, xml, lineobj_table, defect_table, lineobj_custom_handler, defect_custom_handler):
    """Convert csv to Infotech IPL xml."""
    welds, defects, lineobjs = 0, 0, 0
    obj_dict = {}

    for pipe in csvfile.get_tubes():
        if pipe.length == 0:
            continue

        welds += 1
        p_def, p_line = add_pipe(
          pipe, xml, obj_dict, lineobj_table, defect_table, lineobj_custom_handler, defect_custom_handler
        )
        defects += p_def
        lineobjs += p_line

    xml.add_types(obj_dict)

    return (welds, defects, lineobjs)
