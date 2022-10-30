import fontforge
font = fontforge.activeFont()

# Remove unused glyphs

font.encoding = "UnicodeFull"
font.selection.select(("unicode", "ranges"), 0xe000, 0xf8ff)
font.selection.select(("more", "unicode", "ranges"), 0xf0000, 0x10ffff)
font.selection.select(("less", "unicode"), 0xf800)
font.selection.select(("less", "unicode", "ranges"), 0xf1b00, 0xf1c3f)
font.selection.select(("more", "ranges"), 0x110000, len(font) - 1)
font.selection.select(("less",), ".notdef")

for glyph in font.selection.byGlyphs:
	font.removeGlyph(glyph)

font.encoding = "compacted"

# Define alternative codepoints for shidinn characters

def setAlt(uni, altuni):
	font.createChar(uni).altuni = ((altuni, -1, 0),)

for ind in range(89):
	for cas in range(3):
		setAlt(0xf1b00 + ind + cas * 0x60, 0xe020 + ind + (ind >> 4 << 5) + (cas << 4))

for i in range(1, 10):
	setAlt(0xf1c20 + i, 0xe000 + i)
setAlt(0xf1c20, 0xe00a)
setAlt(0xf1c2a, 0xe00b)
setAlt(0xf1c2b, 0xe00c)
setAlt(0xf1bbd, 0xe00d)
setAlt(0xf1bbe, 0xe00e)
setAlt(0xf1bbf, 0xe00f)

for i in range(3):
	setAlt(0xf1c30 + i, 0xe016 + i)

# Reencode
font.encoding = "UnicodeFull"

# Patch metadata
name = font.fullname
font.fontname += "XdPUA"
font.fullname += " XdPUA"
font.familyname += " XdPUA"
font.copyright = "%s XdPua by DGCK81LNN, based on %s by Kreative Software, version %s.\n\n" % (name, name, font.version) + font.copyright
font.weight = ""

sfntNames = []
for entry in font.sfnt_names:
	if entry[1] != "UniqueID":
		sfntNames.append(entry)
font.sfnt_names = tuple(sfntNames)
