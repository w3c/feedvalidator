__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

import feedvalidator
from feedvalidator.logging import *

line = "line %(line)s"
column = "column %(column)s"
occurances = " (%(msgcount)s occurrences)"

messages = {
  SAXError:                "XML parsing error: %(exception)s",
  WPBlankLine:             "Blank line before XML declaration",
  NotHtml:                 "%(message)s",
  UnicodeError:            "%(exception)s (maybe a high-bit character?)",
  UndefinedElement:        "Undefined %(parent)s element: %(element)s",
  MissingNamespace:        "Missing namespace for %(element)s",
  MissingElement:          "Missing %(parent)s element: %(element)s",
  MissingRecommendedElement: "%(parent)s should contain a %(element)s element",
  MissingAttribute:        "Missing %(element)s attribute: %(attr)s",
  MissingRecommendedAttribute: "Missing recommended %(element)s attribute: %(attr)s",
  UnexpectedAttribute:     "Unexpected %(attribute)s attribute on %(element)s element",
  NoBlink:                 "There is no blink element in RSS; use blogChannel:blink instead",
  NoThrWhen:               "thr:when attribute obsolete; use thr:updated instead",
  NoBlink:                 "There is no thr:when attribute in Atom; use thr:updated instead",
  InvalidWidth:            "%(element)s must be between 1 and 144",
  InvalidHeight:           "%(element)s must be between 1 and 400",
  InvalidHour:             "%(element)s must be an integer between 0 and 23",
  InvalidDay:              "%(element)s must be Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, or Sunday",
  InvalidInteger:          "%(element)s must be an integer",
  InvalidNonNegativeInteger: "%(element)s must be a non-negative integer",
  InvalidPositiveInteger:  "%(element)s must be a positive integer",
  InvalidAlphanum:         "%(element)s must be alphanumeric",
  InvalidLatitude:         "%(element)s must be between -90 and 90",
  InvalidLongitude:        "%(element)s must be between -180 and 180",
  InvalidCommaSeparatedIntegers: "%(element)s must be comma-separated integers",
  InvalidHttpGUID:         "guid must be a full URL, unless isPermaLink attribute is false",
  InvalidUpdatePeriod:     "%(element)s must be hourly, daily, weekly, monthly, or yearly",
  NotBlank:                "%(element)s should not be blank",
  AttrNotBlank:            "The %(attr)s attribute of %(element)s should not be blank",
  DuplicateElement:        "%(parent)s contains more than one %(element)s",
  DuplicateSemantics:      "A channel should not include both %(core)s and %(ext)s",
  DuplicateItemSemantics:  "An item should not include both %(core)s and %(ext)s",
  DuplicateValue:          "%(element)s values must not be duplicated within a feed",
  NonstdPrefix:            '"%(preferred)s" is the preferred prefix for the namespace "%(ns)s"',
  ReservedPrefix:          'The prefix "%(prefix)s" generally is associated with the namespace "%(ns)s"',
  MediaRssNamespace:       'Missing trailing slash in mediaRSS namespace',
  InvalidContact:          "Invalid email address",
  InvalidAddrSpec:         "%(element)s must be an email address",
  InvalidLink:             "%(element)s must be a valid URI",
  InvalidIRI:              "%(element)s must be a valid IRI",
  InvalidFullLink:         "%(element)s must be a full and valid URL",
  InvalidUriChar:          "Invalid character in a URI",
  InvalidISO8601Date:      "%(element)s must be an ISO8601 date",
  InvalidISO8601DateTime:  "%(element)s must be an ISO8601 date-time",
  InvalidW3CDTFDate:        "%(element)s must be an W3CDTF date",
  InvalidRFC2822Date:      "%(element)s must be an RFC-822 date-time",
  IncorrectDOW:            "Incorrect day of week",
  InvalidRFC3339Date:      "%(element)s must be an RFC-3339 date-time",
  InvalidNPTTime:          "%(attr)s must be an NPT-time",
  InvalidLanguage:         "%(element)s must be an ISO-639 language code",
  InvalidURIAttribute:     "%(attr)s attribute of %(element)s must be a valid URI",
  InvalidURLAttribute:     "%(element)s must be a full URL",
  InvalidIntegerAttribute: "%(attr)s attribute of %(element)s must be a positive integer",
  InvalidBooleanAttribute: "%(attr)s attribute of %(element)s must be 'true' or 'false'",
  InvalidMIMEAttribute:    "%(attr)s attribute of %(element)s must be a valid MIME type",
  ItemMustContainTitleOrDescription: "item must contain either title or description",
  ContainsHTML:            "%(element)s should not contain HTML",
  ContainsEmail:           "%(element)s should not include email address",
  ContainsUndeclaredHTML:  "%(element)s should not contain HTML unless declared in the type attribute",
  NotEnoughHoursInTheDay:  "skipHours can not contain more than 24 hour elements",
  EightDaysAWeek:          "skipDays can not contain more than 7 day elements",
  SecurityRisk:            "%(element)s should not contain %(tag)s tag",
  SecurityRiskAttr:        "%(element)s should not contain %(attr)s attribute",
  ContainsRelRef:          "%(element)s should not contain relative URL references",
  ContainsSystemEntity:    "Feeds must not contain SYSTEM entities",
  InvalidContentMode:      "mode must be 'xml', 'escaped', or 'base64'",
  InvalidMIMEType:         "Not a valid MIME type",
  NotEscaped:              "%(element)s claims to be escaped, but isn't",
  NotInline:               "%(element)s claims to be inline, but may contain html",
  NotBase64:               "%(element)s claims to be base64-encoded, but isn't",
  InvalidURN:              "%(element)s is not a valid URN",
  InvalidUUID:             "%(element)s is not a valid UUID",
  InvalidTAG:              "%(element)s is not a valid TAG",
  InvalidURI:              "%(element)s is not a valid URI",
  ObsoleteVersion:         "This feed is an obsolete version",
  ObsoleteNamespace:       "This feed uses an obsolete namespace",
  InvalidNamespace:        "%(element)s is in an invalid namespace: %(namespace)s",
  InvalidDoctype:          "This feed contains conflicting DOCTYPE and version information",
  DuplicateAtomLink:       "Duplicate alternate links with the same type and hreflang",
  MissingHref:             "%(element)s must have an href attribute",
  AtomLinkNotEmpty:        "%(element)s should not have text (all data is in attributes)",
  BadCharacters:           '%(element)s contains bad characters',
  BadXmlVersion:           "Incorrect XML Version: %(version)s",
  UnregisteredAtomLinkRel: "Unregistered link relationship",
  HttpError:               "Server returned %(status)s",
  IOError:                 "%(exception)s (%(message)s; misconfigured server?)",
  ObscureEncoding:         "Obscure XML character encoding: %(encoding)s",
  NonstdEncoding:          "This encoding is not mandated by the XML specification: %(encoding)s",
  UnexpectedContentType:   '%(type)s should not be served with the "%(contentType)s" media type',
  EncodingMismatch:        'Your feed appears to be encoded as "%(encoding)s", but your server is reporting "%(charset)s"',
  UnknownEncoding:         "Unknown XML character encoding: %(encoding)s",
  NotSufficientlyUnique:   "The specified guid is not sufficiently unique",
  MissingEncoding:         "No character encoding was specified",
  UnexpectedText:          "Unexpected Text",
  ValidatorLimit:          "Unable to validate, due to hardcoded resource limits (%(limit)s)",
  TempRedirect:            "Temporary redirect",
  TextXml:                 "Content type of text/xml with no charset",
  Uncompressed:            "Response is not compressed",
  HttpProtocolError:       'Response includes bad HTTP header name: "%(header)s"',
  HttpsProtocolError:      'Error when fetching content over HTTPs: "%(message)s"',
  HttpsProtocolWarning:    'Warning when fetching content over HTTPs: "%(message)s"',
  NonCanonicalURI:         'Identifier "%(uri)s" is not in canonical form (the canonical form would be "%(curi)s")',
  InvalidRDF:              'RDF parsing error: %(message)s',
  InvalidDuration:         'Invalid duration',
  InvalidYesNo:            '%(element)s must be "yes", "no"',
  InvalidYesNoClean:       '%(element)s must be "yes", "no", or "clean"',
  TooLong:                 'length of %(len)d exceeds the maximum allowable for %(element)s of %(max)d',
  InvalidItunesCategory:   '%(text)s is not one of the predefined iTunes categories or sub-categories',
  ObsoleteItunesCategory:   '%(text)s is an obsolete iTunes category or sub-category',
  InvalidKeywords:         'Use commas to separate keywords',
  InvalidTextType:         'type attribute must be "text", "html", or "xhtml"',
  MissingXhtmlDiv:         'Missing xhtml:div element',
  MissingSelf:             'Missing atom:link with rel="self"',
  MissingAtomSelfLink:             'Missing atom:link with rel="self"',
  DuplicateEntries:        'Two entries with the same id',
  DuplicateIds:            'All entries have the same id',
  MisplacedMetadata:       '%(element)s must appear before all entries',
  MissingSummary:          'Missing summary',
  MissingTextualContent:   'Missing textual content',
  MissingContentOrAlternate: 'Missing content or alternate link',
  MissingSourceElement:    "Missing %(parent)s element: %(element)s",
  MissingTypeAttr:         "Missing %(element)s attribute: %(attr)s",
  HtmlFragment:            "%(type)s type used for a document fragment",
  DuplicateUpdated:        "Two entries with the same value for atom:updated",
  UndefinedNamedEntity:    "Undefined named entity",
  ImplausibleDate:         "Implausible date",
  UnexpectedWhitespace:    "Whitespace not permitted here",
  SameDocumentReference:   "Same-document reference",
  SelfDoesntMatchLocation: "Self reference doesn't match document location",
  InvalidOPMLVersion:      'The "version" attribute for the opml element must be 1.0 or 1.1.',
  MissingXmlURL:           'An <outline> element whose type is "rss" must have an "xmlUrl" attribute.',
  InvalidOutlineVersion:   'An <outline> element whose type is "rss" may have a version attribute, whose value must be RSS, RSS1, RSS2, or scriptingNews.',
  InvalidOutlineType:      'The type attribute on an <outline> element should be a known type.',
  InvalidExpansionState:   '<expansionState> is a comma-separated list of line numbers.',
  InvalidTrueFalse:        '%(element)s must be "true" or "false"',
  MissingOutlineType:      'An <outline> element with more than just a "text" attribute should have a "type" attribute indicating how the other attributes are to be interpreted.',
  MissingTitleAttr:        'Missing outline attribute: title',
  MissingUrlAttr:          'Missing outline attribute: url',
  NotUTF8:                 'iTunes elements should only be present in feeds encoded as UTF-8',
  MissingItunesElement:    'Missing recommended iTunes %(parent)s element: %(element)s',
  UnsupportedItunesFormat: 'Format %(extension)s is not supported by iTunes',
  InvalidCountryCode:      "Invalid country code: \"%(value)s\"",
  InvalidCurrencyUnit:     "Invalid value for %(attr)s",
  InvalidFloat:            "Invalid value for %(attr)s",
  InvalidFloatUnit:        "Invalid value for %(attr)s",
  InvalidFullLocation:     "Invalid value for %(attr)s",
  InvalidGender:           "Invalid value for %(attr)s",
  InvalidIntUnit:          "Invalid value for %(attr)s",
  InvalidLabel:            "Invalid value for %(attr)s",
  InvalidLocation:         "Invalid value for %(attr)s",
  InvalidMaritalStatus:    "Invalid value for %(attr)s",
  InvalidPaymentMethod:    "Invalid value for %(attr)s",
  InvalidPercentage:       '%(element)s must be a percentage',
  InvalidPriceType:        "Invalid value for %(attr)s",
  InvalidRatingType:       "Invalid value for %(attr)s",
  InvalidReviewerType:     "Invalid value for %(attr)s",
  InvalidSalaryType:       "Invalid value for %(attr)s",
  InvalidServiceType:      "Invalid value for %(attr)s",
  InvalidValue:            "Invalid value for %(attr)s",
  InvalidYear:             "Invalid value for %(attr)s",
  TooMany:                 "%(parent)s contains more than ten %(element)s elements",
  InvalidPermalink:        "guid must be a full URL, unless isPermaLink attribute is false",
  NotInANamespace:         "Missing namespace for %(element)s",
  UndeterminableVocabulary:"Missing namespace for %(element)s",
  SelfNotAtom:             '"self" link references a non-Atom representation',
  InvalidFormComponentName: 'Invalid form component name',
  ImageLinkDoesntMatch:    "Image link doesn't match channel link",
  ImageUrlFormat:          "Image not in required format",
  ProblematicalRFC822Date: "Problematical RFC 822 date-time value",
  DuplicateEnclosure:      "item contains more than one enclosure",
  MissingItunesEmail:      "The recommended <itunes:email> element is missing",
  MissingGuid:             "%(parent)s should contain a %(element)s element",
  UriNotIri:               "IRI found where URL expected",
  ObsoleteWikiNamespace:   "Obsolete Wiki Namespace",
  DuplicateDescriptionSemantics: "Avoid %(element)s",
  InvalidCreditRole:       "Invalid Credit Role",
  InvalidMediaTextType:    'type attribute must be "plain" or "html"',
  InvalidMediaHash:        'Invalid Media Hash',
  InvalidMediaRating:      'Invalid Media Rating',
  InvalidMediaRestriction: "media:restriction must be 'all' or 'none'",
  InvalidMediaRestrictionRel: "relationship must be 'allow' or 'disallow'",
  InvalidMediaRestrictionType: "type must be 'country' or 'uri'",
  InvalidMediaMedium:      'Invalid content medium: "%(value)s"',
  InvalidMediaExpression:  'Invalid content expression: "%(value)s"',
  DeprecatedMediaAdult:    'media:adult is deprecated',
  MediaGroupWithoutAlternatives: 'media:group must have multiple media:content children',
  CommentRSS:              'wfw:commentRSS should be wfw:commentRss',
  NonSpecificMediaType:    '"%(contentType)s" media type is not specific enough',
  DangerousStyleAttr:      "style attribute contains potentially dangerous content",
  NotURLEncoded:           "%(element)s must be URL encoded",
  InvalidLocalRole:        "Invalid local role",
  InvalidEncoding:         "Invalid character encoding",
  ShouldIncludeExample:    "OpenSearchDescription should include an example Query",
  InvalidAdultContent:     "Non-boolean value for %(element)s",
  InvalidLocalParameter:   "Invalid local parameter name",
  UndeclaredPrefix:        "Undeclared %(element)s prefix",
  UseOfExtensionAttr:      "Use of extension attribute on RSS 2.0 core element: %(attribute)s",
  DeprecatedDTD:           "The use of this DTD has been deprecated by Netscape",
  MisplacedXHTMLContent:   "Misplaced XHTML content",
  SchemeNotIANARegistered: "URI scheme not IANA registered",
  InvalidCoord:            "Invalid coordinates",
  InvalidCoordList:        "Invalid coordinate list",
  CoordComma:              "Comma found in coordinate pair",
  AvoidNamespacePrefix:    "Avoid Namespace Prefix: %(prefix)s",
  Deprecated:              "%(element)s has been superceded by %(replacement)s.",
  DeprecatedRootHref:      "root:// URLs have been superceded by full http:// URLs",
  InvalidAltitudeMode:     "Invalid altitudeMode",
  InvalidAngle:            "%(element)s must be between -360 and 360",
  InvalidColor:            "Not a valid color",
  InvalidColorMode:        "Invalid colorMode.",
  InvalidItemIconState:    "Invalid state for Icon",
  InvalidListItemType:     "Invalid list item type",
  InvalidKmlCoordList:        "Invalid coordinate list. Make sure that coordinates are of the form longitude,latitude or longitude,latitude,altitude and separated by a single space. It is also a good idea to avoid line breaks or other extraneous white space",
  InvalidKmlLatitude:      "Invalid latitude found within coordinates. Latitudes have to be between -90 and 90.",
  InvalidKmlLongitude:      "Invalid longitude found within coordinates. Longitudes have to be between -180 and 180.",
  InvalidKmlMediaType:      "%(contentType)s is an invalid KML media type. Use application/vnd.google-earth.kml+xml or application/vnd.google-earth.kmz",
  InvalidKmlUnits:         "Invalid units.",
  InvalidRefreshMode:      "Invalid refreshMode",
  InvalidSchemaFieldType:  "Invalid Schema field type",
  InvalidStyleState:       "Invalid key for StyleMap.",
  InvalidViewRefreshMode:  "Invalid viewRefreshMode.",
  InvalidZeroOne:          "Invalid value. Should be 0 or 1.",
  MissingId:               "%(parent)s should contain a %(element)s attribute. This is important if you want to link directly to features.",
  InvalidSseType:          "sx:related type must be either 'aggregated' or 'compete'",
  FeedHistoryRelInEntry:   "%(rel)s link relation found in entry",
  LinkPastEnd:             "%(rel)s link in %(self)s entry in list",
  FeedRelInCompleteFeed:   "%(rel)s link relation found in complete feed",
  MissingCurrentInArchive: "Current link not found in archive feed",
  CurrentNotSelfInCompleteFeed: "Current not self in complete feed",
  ArchiveIncomplete:       "Archive incomplete",
  RelativeSelf:            "Relative href value on self link",
  ConflictingCatAttr:      "Categories can't have both href and %(attr)s attributes",
  ConflictingCatChildren:  "Categories can't have both href attributes and children",
  UndefinedParam:          "Undefined media-range parameter",
  CharacterData:           'Encode "&" and "<" in plain text using hexadecimal character references.',
  EmailFormat:             'Email address is not in the recommended format',
  MissingRealName:         'Email address is missing real name',
  MisplacedItem:           'Misplaced Item',
  ImageTitleDoesntMatch:   "Image title doesn't match channel title",
  AvoidTextInput:          "Avoid Text Input",
  NeedDescriptionBeforeContent: "Ensure description precedes content:encoded",
  SlashDate:               "Ensure lastBuildDate is present when slash:comments is used",
  UseZeroForMidnight:      "Use zero for midnight",
  UseZeroForUnknown:       "Use zero for unknown length",
  UnknownHost:             "Unknown host",
  UnknownNamespace:        "Use of unknown namespace: %(namespace)s",
  UnsupportedNamespace:    "Did not validate namespace: %(namespace)s. See the %(name)s specification at %(specification)s",
  IntegerOverflow:         "%(element)s value too large",
  InvalidNSS:              "Invalid Namespace Specific String: %(element)s",
  SinceAfterUntil:         "Since After until",
  MissingByAndWhenAttrs:   "Missing by and when attributes",
  QuestionableUsage:       "Undocumented use of %(element)s",
  InvalidRSSVersion:       "Invalid RSS Version",
  HttpErrorWithPossibleFeed:    "HTTP error with content that looks like a feed",
 }
