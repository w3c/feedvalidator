__author__ = "Sam Ruby <http://intertwingly.net/> and Mark Pilgrim <http://diveintomark.org/>"
__version__ = "$Revision$"
__copyright__ = "Copyright (c) 2002 Sam Ruby and Mark Pilgrim"

from .validators import *

class itunes:
  def do_itunes_author(self):
    return lengthLimitedText(255), noduplicates()

  def do_itunes_block(self):
    return yesnoclean(), noduplicates()

  def do_itunes_explicit(self):
    return yesnoclean(), noduplicates()

  def do_itunes_keywords(self):
    return lengthLimitedText(255), keywords(), noduplicates()

  def do_itunes_subtitle(self):
    return lengthLimitedText(255), noduplicates()

  def do_itunes_summary(self):
    return lengthLimitedText(4000), noduplicates()

  def do_itunes_image(self):
    return image(), noduplicates()

class itunes_channel(itunes):
  from .logging import MissingItunesElement

  def validate(self):
    if not 'language' in self.children and not self.xmlLang:
      self.log(MissingItunesElement({"parent":self.name, "element":'language'}))
    if not 'itunes_category' in self.children:
      self.log(MissingItunesElement({"parent":self.name, "element":'itunes:category'}))
    if not 'itunes_explicit' in self.children:
      self.log(MissingItunesElement({"parent":self.name, "element":'itunes:explicit'}))
    if not 'itunes_owner' in self.children:
      self.log(MissingItunesEmail({"parent":self.name, "element":'itunes:email'}))

  def setItunes(self, value):
    if value and not self.itunes:
      if self.dispatcher.encoding.lower() not in ['utf-8','utf8']:
        from .logging import NotUTF8
        self.log(NotUTF8({"parent":self.parent.name, "element":self.name}))
      if self.getFeedType() == TYPE_ATOM and 'entry' in self.children:
        self.validate()

    self.itunes |= value

  def do_itunes_owner(self):
    return owner(), noduplicates()

  def do_itunes_category(self):
    return category()

  def do_itunes_pubDate(self):
    return rfc822(), noduplicates()

  def do_itunes_new_feed_url(self):
    if self.child != 'itunes_new-feed-url':
      self.log(UndefinedElement({"parent":self.name.replace("_",":"), "element":self.child}))
    return rfc2396_full(), noduplicates()

  def do_itunes_type(self):
    return channeltype(), noduplicates()

class itunes_item(itunes):
  supported_formats = ['m4a', 'mp3', 'mov', 'mp4', 'm4v', 'pdf', 'epub']

  def validate(self):
    pass

  def setItunes(self, value):
    if value and not self.itunes:
      self.parent.setItunes(True)
      self.itunes = value
      if hasattr(self, 'enclosures'):
        save, self.enclosures = self.enclosures, []
        for enclosure in save:
          self.setEnclosure(enclosure)

  def setEnclosure(self, url):
    if self.itunes:
      # http://www.apple.com/itunes/podcasts/techspecs.html#_Toc526931678
      ext = url.split('.')[-1]
      if ext not in itunes_item.supported_formats:
        from .logging import UnsupportedItunesFormat
        self.log(UnsupportedItunesFormat({"parent":self.parent.name, "element":self.name, "extension":ext}))

    if not hasattr(self, 'enclosures'): self.enclosures = []
    self.enclosures.append(url)

  def do_itunes_duration(self):
    return duration(), noduplicates()

  def do_itunes_title(self):
    return text(), noduplicates()

  def do_itunes_episode(self):
    return positiveInteger(), noduplicates()

  def do_itunes_season(self):
    return positiveInteger(), noduplicates()

  def do_itunes_episodeType(self):
    return episodetype(), noduplicates()

class owner(validatorBase):
  def validate(self):
    if not "itunes_email" in self.children:
      self.log(MissingElement({"parent":self.name.replace("_",":"),
        "element":"itunes:email"}))

  def do_itunes_email(self):
    return email(), noduplicates()

  def do_itunes_name(self):
    return lengthLimitedText(255), noduplicates()

class subcategory(validatorBase):
  def __init__(self, newlist, oldlist):
    validatorBase.__init__(self)
    self.newlist = newlist
    self.oldlist = oldlist
    self.text = None

  def getExpectedAttrNames(self):
      return [(None, 'text')]

  def prevalidate(self):
    try:
      self.text=self.attrs.getValue((None, "text"))
      if not self.text in self.newlist:
        if self.text in self.oldlist:
          self.log(ObsoleteItunesCategory({"parent":self.parent.name.replace("_",":"),
            "element":self.name.replace("_",":"),
            "text":self.text}))
        else:
          self.log(InvalidItunesCategory({"parent":self.parent.name.replace("_",":"),
            "element":self.name.replace("_",":"),
            "text":self.text}))
    except KeyError:
      self.log(MissingAttribute({"parent":self.parent.name.replace("_",":"),
        "element":self.name.replace("_",":"),
        "attr":"text"}))

class image(validatorBase):
  def getExpectedAttrNames(self):
    return [(None, 'href')]

  def prevalidate(self):
    self.validate_required_attribute((None,'href'), httpURL)

class category(subcategory):
  def __init__(self):
    subcategory.__init__(self, list(valid_itunes_categories.keys()),
        list(old_itunes_categories.keys()))

  def do_itunes_category(self):
    if not self.text: return eater()
    return subcategory(valid_itunes_categories.get(self.text,[]),
        old_itunes_categories.get(self.text,[]))

valid_itunes_categories = {
  "Arts": [
    "Books",
    "Design",
    "Fashion & Beauty",
    "Food",
    "Performing Arts",
    "Visual Arts"],
  "Business": [
    "Careers",
    "Entrepreneurship",
    "Investing",
    "Management",
    "Marketing",
    "Non-Profit"
  ],
  "Comedy": [
    "Comedy Interviews",
    "Improv",
    "Stand-Up"
  ],
  "Education": [
    "Courses",
    "How To",
    "Language Learning",
    "Self-Improvement"
  ],
  "Fiction": [
    "Comedy Fiction",
    "Drama",
    "Science Fiction"
  ],
  "Government": [],
  "History": [],
  "Health & Fitness": [
    "Alternative Health",
    "Fitness",
    "Medicine",
    "Mental Health",
    "Nutrition",
    "Sexuality"
  ],
  "Kids & Family": [
    "Education for Kids",
    "Parenting",
    "Pets & Animals",
    "Stories for Kids"],
  "Leisure": [
    "Animation & Manga",
    "Automotive",
    "Aviation",
    "Crafts",
    "Games",
    "Hobbies",
    "Home & Garden",
    "Video Games"
  ],
  "Music": [
    "Music Commentary",
    "Music History",
    "Music Interviews"],
  "News": [
    "Business News",
    "Daily News",
    "Entertainment News",
    "News Commentary",
    "Politics",
    "Sports News",
    "Tech News"
  ],
  "Religion & Spirituality": [
    "Buddhism",
    "Christianity",
    "Hinduism",
    "Islam",
    "Judaism",
    "Spirituality"],
  "Science": [
    "Astronomy",
    "Chemistry",
    "Earth Sciences",
    "Life Sciences",
    "Mathematics",
    "Natural Sciences",
    "Nature",
    "Physics",
    "Social Sciences"
  ],
  "Society & Culture": [
    "Documentary",
    "Personal Journals",
    "Philosophy",
    "Places & Travel",
    "Relationships"],
  "Sports": [
    "Baseball",
    "Basketball",
    "Cricket",
    "Fantasy Sports",
    "Football",
    "Golf",
    "Hockey",
    "Rugby",
    "Running",
    "Soccer",
    "Swimming",
    "Tennis",
    "Volleyball",
    "Wilderness",
    "Wrestling"],
  "Technology": [],
  "True Crime": [],
  "TV & Film": [
    "After Shows",
    "Film History",
    "Film Interviews",
    "Film Reviews",
    "TV Reviews"]
}

old_itunes_categories = {
  "Arts": [
    "Literature"
  ],
  "Arts & Entertainment": [
    "Architecture",
    "Design",
    "Entertainment",
    "Games",
    "Performing Arts",
    "Photography",
    "Poetry",
    "Science Fiction"],
  "Audio Blogs": [],
  "Business": [
    "Careers",
    "Finance",
    "Investing",
    "Management & Marketing",
    "News",
    "Shopping"],
  "Comedy": [],
  "Education": [
    "Education Technology",
    "Higher Education",
    "K-12",
    "Language Courses",
    "Training"],
  "Family": [],
  "Food": [],
  "Games & Hobbies": [
    "Automotive",
    "Aviation",
    "Hobbies",
    "Other Games",
    "Video Games"],
  "Government & Organizations": [
    "Local",
    "National",
    "Non-Profit",
    "Regional"],
  "Health": [
    "Alternative Health",
    "Diet & Nutrition",
    "Fitness",
    "Fitness & Nutrition",
    "Relationships",
    "Self-Help",
    "Sexuality"],
  "International": [
    "Australian",
    "Belgian",
    "Brazilian",
    "Canadian",
    "Chinese",
    "Dutch",
    "French",
    "German",
    "Hebrew",
    "Italian",
    "Japanese",
    "Norwegian",
    "Polish",
    "Portuguese",
    "Spanish",
    "Swedish"],
  "Movies & Television": [],
  "News & Politics": [],
  "Politics": [],
  "Public Radio": [],
  "Religion & Spirituality": [
    "Buddhism",
    "Christianity",
    "Islam",
    "Judaism",
    "New Age",
    "Philosophy",
    "Other",
    "Spirituality"],
  "Science & Medicine": [
    "Medicine",
    "Natural Sciences",
    "Social Sciences"],
  "Society & Culture": [
      "History"
  ],
  "Sports & Recreation": [
    "Amateur",
    "College & High School",
    "Outdoor",
    "Professional"],
  "Talk Radio": [],
  "Technology": [
    "Computers",
    "Developers",
    "Gadgets",
    "Information Technology",
    "News",
    "Operating Systems",
    "Podcasting",
    "Smart Phones",
    "Software How-To",
    "Tech News",
    "Text/Speech"],
  "Transportation": [
    "Automotive",
    "Aviation",
    "Bicycles",
    "Commuting"],
  "Travel": []
}

class yesnoclean(text):
  def normalizeWhitespace(self):
    pass
  def validate(self):
    if not self.value.lower() in ['yes','no','clean']:
      self.log(InvalidYesNoClean({"parent":self.parent.name, "element":self.name,"value":self.value}))

class channeltype(enumeration):
  error = InvalidItunesChannelType
  valuelist = ["episodic", "serial"]

class episodetype(enumeration):
  error = InvalidItunesEpisodeType
  valuelist = ["full", "trailer", "bonus"]
