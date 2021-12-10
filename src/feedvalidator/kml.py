__author__ = "Gregor J. Rothfuss <http://greg.abstrakt.ch/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

from .base import validatorBase
from .validators import *
import re

# This code tries to mimic the structure of the canonical KML XSD as much as possible.
# The KML XSD is at http://code.google.com/apis/kml/schema/kml21.xsd

# FeatureType from the XSD schema
#
class FeatureType(validatorBase):

  def do_name(self):
    return text(),noduplicates()

  def do_visibility(self):
    return zeroone(),noduplicates()

  def do_open(self):
    return zeroone(),noduplicates()

  def do_address(self):
    return nonhtml(),noduplicates()

  def do_phoneNumber(self):
    return text(),noduplicates() # todo: implement full check from http://www.koders.com/perl/fid426DF448FE99166A1AD0162538E583A0FA956EEA.aspx

  def do_Snippet(self):
    return Snippet(), noduplicates()

  def do_description(self):
    return text(), noduplicates()

  def do_LookAt(self):
    return LookAt(),noduplicates()

# TimePrimitive
  def do_TimeStamp(self):
    return TimeStamp(),noduplicates()

  def do_TimeSpan(self):
    return TimeSpan(),noduplicates()
# /TimePrimitive

  def do_styleUrl(self):
    return text(), noduplicates()

# StyleSelector
  def do_Style(self):
    return Style()

  def do_StyleMap(self):
    return StyleMap()
# /StyleSelector

# 2.0 only
  def do_View(self):
    return View(),noduplicates()
# /2.0 only

  def do_Region(self):
    return Region(), noduplicates()

  def do_Metadata(self):
    return Metadata()

  def do_atom_link(self):
    from .link import link
    return link()

  def do_atom_author(self):
    from .author import author
    return author()

# OverlayType from the XSD schema
#
class OverlayType(validatorBase):

  def do_color(self):
    return color(),noduplicates()

  def do_drawOrder(self):
    return Integer(),noduplicates()

  def do_Icon(self):
    return Icon(), noduplicates()

# ColorStyleType from the XSD schema
#
class ColorStyleType(validatorBase):

  def do_color(self):
    return color(),noduplicates()

  def do_colorMode(self):
    return colorMode(),noduplicates()

#
# Container from the XSD schema
#
class Container(validatorBase):

  def do_Document(self):
    return Document()

  def do_Folder(self):
    return Folder()

#
# Feature from the XSD schema
#
class Feature(validatorBase):

  def do_Placemark(self):
    return Placemark()

#
# Geometry from the XSD schema
#
class Geometry(Feature):
# TODO these should all be noduplicates(), but because they can appear
# inside MultiGeometry, they are not.
  def do_Model(self):
    return Model()

  def do_LineString(self):
    return LineString()

  def do_LinearRing(self):
    return LinearRing()

  def do_Point(self):
    return Point()

  def do_Polygon(self):
    return Polygon()

  def do_MultiGeometry(self):
    return MultiGeometry()

#
# GeometryElements from the XSD schema
#
class GeometryElements(Geometry):

  def do_extrude(self):
    return zeroone(),noduplicates()

  def do_tessellate(self):
    return zeroone(),noduplicates()

  def do_altitudeMode(self):
    return altitudeMode(),noduplicates()

#
# LinkType from the XSD schema
#
class LinkType(validatorBase):

  def do_href(self):
    return text(),noduplicates()

  def do_refreshMode(self):
    return refreshMode(),noduplicates()

  def do_viewRefreshMode(self):
    return viewRefreshMode(),noduplicates()

  def do_viewRefreshTime(self):
    return Float(), noduplicates()

  def do_viewBoundScale(self):
    return Float(), noduplicates()

  def do_refreshVisibility(self):
    return refreshVisibility(),noduplicates()

  def do_refreshInterval(self):
    return Float(), noduplicates()

  def do_viewFormat(self):
    return text(),noduplicates()

  def do_httpQuery(self):
    return text(),noduplicates()

#
# LookAtType from the XSD schema
#
class LookAtType(Feature):

  def do_longitude(self):
    return longitude(),noduplicates()

  def do_latitude(self):
    return latitude(),noduplicates()

  def do_altitude(self):
    return FloatWithNegative(),noduplicates()

  def do_range(self):
    return Float(),noduplicates()

  def do_tilt(self):
    return latitude(),noduplicates()

  def do_heading(self):
    return angle360(),noduplicates()

  def do_altitudeMode(self):
    return altitudeMode(),noduplicates()


#
# KML element.
#
class kml(Container, Feature):
  from .logging import TYPE_KML20, TYPE_KML21, TYPE_KML22

  def do_NetworkLink(self):
    return NetworkLink()

  def do_GroundOverlay(self):
    return GroundOverlay()

  def do_ScreenOverlay(self):
    return ScreenOverlay()

  def do_NetworkLinkControl(self):
    return NetworkLinkControl()

  def do_atom_link(self):
    from .link import link
    return link()

  def do_atom_author(self):
    from .author import author
    return author()

class NetworkLinkControl(validatorBase):

  def do_minRefreshPeriod(self):
    return Float(),noduplicates()

  def do_linkName(self):
    return text(),noduplicates()

  def do_linkDescription(self):
    return text(),noduplicates()

  def do_cookie(self):
    return text(),noduplicates()

  def do_message(self):
    return text(), noduplicates()

  def do_linkSnippet(self):
    return Snippet(), noduplicates()

  def do_expires(self):
    return w3cdtf(),noduplicates()

  def do_Update(self):
    return Update(),noduplicates()

  def do_LookAt(self):
    return LookAt(),noduplicates()

  def do_View(self):
    return View(),noduplicates()

class Update(validatorBase):
  def validate(self):
    if not "targetHref" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"targetHref"}))

  def do_targetHref(self):
    return text(),noduplicates()

  # todo: child validation
  def do_Change(self):
    return noduplicates()

  # todo: child validation
  def do_Update(self):
    return noduplicates()

  # todo: child validation
  def do_Delete(self):
    return noduplicates()

class NetworkLink(FeatureType, Feature):
  def validate(self):
    if not "Link" in self.children and not "Url" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"Link"}))

  def do_targetHref(self):
    return Update(),noduplicates()

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_refreshInterval(self):
    return Float(), noduplicates()

  def do_flyToView(self):
    return zeroone(),noduplicates()

  def do_Link(self):
    return Link(),noduplicates()

  def do_Url(self):
    return Url(),noduplicates()

class Document(FeatureType, Container, Feature):

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_ScreenOverlay(self):
    return ScreenOverlay()

  def do_GroundOverlay(self):
    return GroundOverlay()

  def do_NetworkLink(self):
    return NetworkLink()

  def do_Schema(self):
    return Schema(), noduplicates()

class Schema(validatorBase):
  def getExpectedAttrNames(self):
    return [(None, 'name'), (None, 'parent')]

  def do_SimpleField(self):
    return SchemaField()

  def do_SimpleArrayField(self):
    return SchemaField()

  def do_ObjField(self):
    return SchemaField()

  def do_ObjArrayField(self):
    return SchemaField()

class SchemaField(validatorBase):
  def getExpectedAttrNames(self):
    return [
      (None, 'name'),
      (None, 'type'),
    ]

  def validate(self):
    self.validate_required_attribute((None,'name'), text)
    self.validate_required_attribute((None,'type'), SchemaFieldType)

class Placemark(FeatureType, Geometry):
  def prevalidate(self):
    if (None,"id") not in self.attrs:
      self.log(MissingId({"parent":self.name, "element":"id"}))
    self.validate_optional_attribute((None,'id'), unique('id',self.parent))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_GeometryCollection(self):
    return GeometryCollection()


class MultiGeometry(Geometry):
  # TODO: check for either geometry or multigeometry in feature, but not both?

  def getExpectedAttrNames(self):
    return [(None, 'id')]

class ScreenOverlay(FeatureType, OverlayType):

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_geomColor(self):
    return geomColor(),noduplicates()

  def do_overlayXY(self):
    return overlayxy(), noduplicates()

  def do_screenXY(self):
    return overlayxy(), noduplicates()

  def do_rotationXY(self):
    return overlayxy(), noduplicates()

  def do_size(self):
    return overlayxy(), noduplicates()

class GroundOverlay(FeatureType, OverlayType):
  def validate(self):
    if not "LatLonBox" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"LatLonBox"}))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_altitude(self):
    return FloatWithNegative(),noduplicates()

  def do_altitudeMode(self):
    return altitudeMode(),noduplicates()

  def do_geomColor(self):
    return geomColor(),noduplicates()

  def do_LatLonBox(self):
    return LatLonBox(), noduplicates()

class overlayxy(validatorBase):
  def getExpectedAttrNames(self):
    return [
      (None, 'x'),
      (None, 'y'),
      (None, 'xunits'),
      (None, 'yunits'),
    ]

  def validate(self):
    self.validate_required_attribute((None,'x'), FloatWithNegative)
    self.validate_required_attribute((None,'y'), FloatWithNegative)
    self.validate_required_attribute((None,'xunits'), kmlunits)
    self.validate_required_attribute((None,'yunits'), kmlunits)

class Region(validatorBase):
  def validate(self):
    if not "LatLonAltBox" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"LatLonAltBox"}))

  def do_LatLonAltBox(self):
    return LatLonAltBox(), noduplicates()

  def do_Lod(self):
    return Lod(), noduplicates()

class LatLonBox(validatorBase):
  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def validate(self):
    if not "north" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"north"}))
    if not "south" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"south"}))
    if not "east" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"east"}))
    if not "west" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"west"}))

  def do_north(self):
    return latitude(),noduplicates()

  def do_south(self):
    return latitude(),noduplicates()

  def do_east(self):
    return longitude(),noduplicates()

  def do_west(self):
    return longitude(),noduplicates()

  def do_rotation(self):
    return longitude(),noduplicates()

class LatLonAltBox(LatLonBox):

  def do_minAltitude(self):
    return Float(),noduplicates()

  def do_maxAltitude(self):
    return Float(), noduplicates()

  def do_altitudeMode(self):
    return altitudeMode(),noduplicates()

class Lod(validatorBase):

  def do_minLodPixels(self):
    return Float(),noduplicates()

  def do_maxLodPixels(self):
    return Float(),noduplicates()

  def do_minFadeExtent(self):
    return Float(),noduplicates()

  def do_maxFadeExtent(self):
    return Float(),noduplicates()

class Metadata(validatorBase):
  # TODO do smarter validation here
  def validate(self):
    return noduplicates()

class Snippet(text):
  def validate(self):
    return nonhtml(),noduplicates()

  def getExpectedAttrNames(self):
    return [(None, 'maxLines')]

class Folder(FeatureType, Container, Feature):
  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_NetworkLink(self):
    return NetworkLink()

  def do_GroundOverlay(self):
    return GroundOverlay()

  def do_ScreenOverlay(self):
    return ScreenOverlay()

class LookAt(LookAtType):

  def getExpectedAttrNames(self):
    return [(None, 'id')]

class StyleMap(validatorBase):
  def validate(self):
    if not "Pair" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"Pair"}))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_Pair(self):
    return Pair()

class Style(validatorBase):
  def prevalidate(self):
    self.validate_optional_attribute((None,'id'), unique('id',self.parent))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_LineStyle(self):
    return LineStyle(), noduplicates()

  def do_PolyStyle(self):
    return PolyStyle(), noduplicates()

  def do_IconStyle(self):
    return IconStyle(), noduplicates()

  def do_ListStyle(self):
    return ListStyle(), noduplicates()

  def do_LabelStyle(self):
    return LabelStyle(), noduplicates()

  def do_BalloonStyle(self):
    return BalloonStyle(), noduplicates()

  def do_scale(self):
    return Float(),noduplicates()

  def do_labelColor(self):
    return labelColor(),noduplicates()

class IconStyle(ColorStyleType):
  def prevalidate(self):
    self.validate_optional_attribute((None,'id'), unique('id',self.parent))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_heading(self):
    return angle360(),noduplicates()

  def do_Icon(self):
    return Icon(),noduplicates()

  def do_scale(self):
    return Float(),noduplicates()

  def do_hotSpot(self):
    return overlayxy(), noduplicates()

class Icon(validatorBase):
  def validate(self):
    if not 'href' in self.children:
      self.log(MissingElement({"parent":self.name, "element":"href"}))

  def do_href(self):
#    if not self.getFeedType() == TYPE_KML20 and self.startswith('root://'):
#      self.log(DeprecatedRootHref())
    return text(),noduplicates() # would be url, but has these weird root://

  def do_x(self):
    return noiconoffset()

  def do_y(self):
    return noiconoffset()

  def do_w(self):
    return noiconoffset()

  def do_h(self):
    return noiconoffset()

  def do_refreshInterval(self):
    return Float(), noduplicates()

  def do_refreshMode(self):
    return refreshMode(), noduplicates()

  def do_viewRefreshMode(self):
    return viewRefreshMode(), noduplicates()

  def do_viewRefreshTime(self):
    return Float(), noduplicates()

  def do_viewBoundScale(self):
    return Float(), noduplicates()

class BalloonStyle(validatorBase):
  def prevalidate(self):
    self.validate_optional_attribute((None,'id'), unique('id',self.parent))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_textColor(self):
    return color(),noduplicates()

  def do_bgColor(self):
    return color(),noduplicates()

  def do_color(self):
    return color(),noduplicates()

  def do_text(self):
    return text(),noduplicates()

class ListStyle(validatorBase):
  def prevalidate(self):
    self.validate_optional_attribute((None,'id'), unique('id',self.parent))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_bgColor(self):
    return color(),noduplicates()

  def do_ItemIcon(self):
    return ItemIcon()

  def do_listItemType(self):
    return listItemType(),noduplicates()

  def do_scale(self):
    return Float(),noduplicates()

class ItemIcon(validatorBase):
  def validate(self):
    if not 'href' in self.children:
      self.log(MissingElement({"parent":self.name, "element":"href"}))

  def do_href(self):
    return text(),noduplicates()

  def do_state(self):
    return itemIconState(),noduplicates()

class LabelStyle(ColorStyleType):
  def prevalidate(self):
    self.validate_optional_attribute((None,'id'), unique('id',self.parent))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_labelColor(self):
    return labelColor(),noduplicates()

  def do_scale(self):
    return Float(),noduplicates()

class LineStyle(ColorStyleType):
  def prevalidate(self):
    self.validate_optional_attribute((None,'id'), unique('id',self.parent))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_width(self):
    return Float(),noduplicates()

class PolyStyle(ColorStyleType):
  def prevalidate(self):
    self.validate_optional_attribute((None,'id'), unique('id',self.parent))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_fill(self):
    return zeroone(), noduplicates()

  def do_outline(self):
    return zeroone(), noduplicates()

class Link(LinkType):

  def getExpectedAttrNames(self):
    return [(None, 'id')]

class Pair(validatorBase):
  def validate(self):
    if not 'key' in self.children:
      self.log(MissingElement({"parent":self.name, "element":"key"}))
    if not 'styleUrl' in self.children:
      self.log(MissingElement({"parent":self.name, "element":"styleUrl"}))

  def do_key(self):
    return styleState(),noduplicates()

  def do_styleUrl(self):
    return text(),noduplicates()

class Point(GeometryElements):
  def validate(self):
    if not "coordinates" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"coordinates"}))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_coordinates(self):
    return coordinates()

class Model(validatorBase):
  # TODO seems to me that Location and Orientation ought to be required?
  def validate(self):
    if not "Link" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"Link"}))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_altitudeMode(self):
    return altitudeMode(), noduplicates()

  def do_Location(self):
    return Location(), noduplicates()

  def do_Orientation(self):
    return Orientation(), noduplicates()

  def do_Scale(self):
    return Scale(), noduplicates()

  def do_Link(self):
    return Link(), noduplicates()

  def do_ResourceMap(self):
    return ResourceMap(), noduplicates()

class ResourceMap(validatorBase):
  def do_Alias(self):
    return Alias()

class Alias(validatorBase):
  def do_targetHref(self):
    return text(),noduplicates()

  def do_sourceHref(self):
    return text(),noduplicates()

class Location(validatorBase):
  # TODO they are loosely defined in the schema, but 0,0,0 makes no sense.
  def validate(self):
    if not "longitude" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"longitude"}))
    if not "latitude" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"latitude"}))
    if not "altitude" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"altitude"}))

  def do_longitude(self):
    return longitude(), noduplicates()

  def do_latitude(self):
    return latitude(), noduplicates()

  def do_altitude(self):
    return FloatWithNegative(), noduplicates()

class Scale(validatorBase):

  def do_x(self):
    return Float(), noduplicates()

  def do_y(self):
    return Float(), noduplicates()

  def do_z(self):
    return Float(), noduplicates()

class Orientation(validatorBase):

  def do_heading(self):
    return angle360(), noduplicates()

  def do_tilt(self):
    return angle360(), noduplicates()

  def do_roll(self):
    return angle360(), noduplicates()

class Polygon(GeometryElements):
  def validate(self):
    if not "outerBoundaryIs" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"outerBoundaryIs"}))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_outerBoundaryIs(self):
    return boundary(), noduplicates()

  def do_innerBoundaryIs(self):
    return boundary()

class boundary(validatorBase):
  def validate(self):
    if not "LinearRing" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"LinearRing"}))

  def do_LinearRing(self):
    return LinearRing()

class LineString(GeometryElements):
  def validate(self):
    if not "coordinates" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"coordinates"}))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_coordinates(self):
    return coordinates(), noduplicates()

class LinearRing(GeometryElements):
  def validate(self):
    if not "coordinates" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"coordinates"}))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_coordinates(self):
    return coordinates(), noduplicates()

class TimeSpan(validatorBase):

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_begin(self):
    return w3cdtf(),noduplicates()

  def do_end(self):
    return w3cdtf(),noduplicates()

class TimeStamp(validatorBase):
  def validate(self):
    if not "when" in self.children:
      self.log(MissingElement({"parent":self.name, "element":"when"}))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

  def do_when(self):
    return unbounded_w3cdtf(),noduplicates()

class kmlunits(enumeration):
  error = InvalidKmlUnits
  valuelist = [
  "fraction", "pixels", "insetPixels"
]

class colorMode(enumeration):
  error = InvalidColorMode
  valuelist = [
  "normal", "random"
]

class refreshMode(enumeration):
  error = InvalidRefreshMode
  valuelist = [
  "onChange", "onInterval", "onExpire"
]

class viewRefreshMode(enumeration):
  error = InvalidViewRefreshMode
  valuelist = [
  "never", "onRequest", "onStop", "onRegion"
]

class styleState(enumeration):
  error = InvalidStyleState
  valuelist = [
  "normal", "highlight"
]

class listItemType(enumeration):
  error = InvalidListItemType
  valuelist = [
  "radioFolder", "check", "checkHideChildren", "checkOffOnly"
]

class itemIconState(enumeration):
  error = InvalidItemIconState
  valuelist = [
  "open", "closed", "error", "fetching0", "fetching1", "fetching2",
  "open error", "closed error", "fetching0 error", "fetching1 error",
  "fetching2 error"
]

class altitudeMode(enumeration):
  error = InvalidAltitudeMode
  valuelist = [
  "clampToGround", "relativeToGround", "absolute"
]

class SchemaFieldType(enumeration):
  error = InvalidSchemaFieldType
  valuelist = [
  "string", "int", "uint", "short", "ushort", "float", "double","bool"
]

#
# Deprecated in 2.0
#

class antialias(validatorBase):
  def prevalidate(self):
    self.log(Deprecated({"element":self.name, "replacement":"none"}))

  def validate(self):
    return zeroone(),noduplicates()

class View(LookAtType):
  def prevalidate(self):
    self.log(Deprecated({"element":self.name, "replacement":"LookAt"}))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

#
# Deprecated in 2.1
#

class labelColor(text):
  def prevalidate(self):
    if not self.getFeedType() == TYPE_KML20:
      self.log(Deprecated({"element":self.name, "replacement":"LabelStyle"}))

  def validate(self):
    if not re.match("([a-f]|[A-F]|[0-9]){8}",self.value):
      return self.log(InvalidColor({'value':self.value}))

class geomColor(text):
  def prevalidate(self):
    if not self.getFeedType() == TYPE_KML20:
      self.log(Deprecated({"element":self.name, "replacement":"color"}))

  def validate(self):
    if not re.match("([a-f]|[A-F]|[0-9]){8}",self.value):
      return self.log(InvalidColor({'value':self.value}))

class geomScale(text):
  def prevalidate(self):
    if not self.getFeedType() == TYPE_KML20:
      self.log(Deprecated({"element":self.name, "replacement":"scale"}))

  def validate(self):
      return Float()

class GeometryCollection(Geometry):
  def prevalidate(self):
    if not self.getFeedType() == TYPE_KML20:
      self.log(Deprecated({"element":self.name, "replacement":"MultiGeometry"}))

  def getExpectedAttrNames(self):
    return [(None, 'id')]

class Url(LinkType):
  def prevalidate(self):
    if not self.getFeedType() == TYPE_KML20:
      self.log(Deprecated({"element":self.name, "replacement":"Link"}))

class refreshVisibility(validatorBase):
  def prevalidate(self):
    if not self.getFeedType() == TYPE_KML20:
      self.log(Deprecated({"element":self.name, "replacement":"Update"}))

  def validate(self):
    return zeroone, noduplicates()

# In theory, the spec also supports things like .2 if unit is fractions. ugh.
class noiconoffset(text):
  def validate(self):
    if not self.getFeedType() == TYPE_KML20:
      self.log(Deprecated({"element":self.name, "replacement":"Icon"}))
    return Integer(), noduplicates()

#
# Validators
#

class zeroone(text):
  def normalizeWhitespace(self):
    pass
  def validate(self):
    if not self.value.lower() in ['0','1']:
      self.log(InvalidZeroOne({"parent":self.parent.name, "element":self.name,"value":self.value}))

class color(text):
  def validate(self):
    if not re.match("^([a-f]|[A-F]|[0-9]){8}$",self.value):
      return self.log(InvalidColor({'value':self.value}))

class coordinates(text):
  def validate(self):
    values = self.value.strip().split()
    for value in values:
      # ensure that commas are only used to separate lat and long (and alt)
      if not re.match('^[-+.0-9]+,[-+.0-9]+(,[-+.0-9]+)?$',
        value.strip()):
        return self.log(InvalidKmlCoordList({'value':self.value}))
      # Now validate individual coordinates
      point = value.split(',');
      # First coordinate is longitude
      try:
        lon = float(point[0].strip())
        if lon > 180 or lon < -180:
          raise ValueError
        else:
         self.log(ValidLongitude({"parent":self.parent.name, "element":self.name, "value":lon}))
      except ValueError:
       self.log(InvalidKmlLongitude({"parent":self.parent.name, "element":self.name, "value":lon}))
      # Second coordinate is latitude
      try:
        lat = float(point[1].strip())
        if lat > 90 or lat < -90:
          raise ValueError
        else:
         self.log(ValidLatitude({"parent":self.parent.name, "element":self.name, "value":lat}))
      except ValueError:
       self.log(InvalidKmlLatitude({"parent":self.parent.name, "element":self.name, "value":lat}))
      # Third coordinate value (altitude) has to be float, if present
      if len(point) == 3:
        if not re.match('\d+\.?\d*$', point[2]):
          self.log(InvalidFloat({"attr":self.name, "value":point[2]}))

class angle360(text):
  def validate(self):
    try:
      angle = float(self.value)
      if angle > 360 or angle < -360:
        raise ValueError
      else:
        self.log(ValidAngle({"parent":self.parent.name, "element":self.name, "value":self.value}))
    except ValueError:
      self.log(InvalidAngle({"parent":self.parent.name, "element":self.name, "value":self.value}))

class FloatWithNegative(text):
  def validate(self, name=None):
    if not re.match('-?\d+\.?\d*$', self.value):
      self.log(InvalidFloat({"attr":name or self.name, "value":self.value}))
