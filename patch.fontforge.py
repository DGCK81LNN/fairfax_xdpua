import fontforge

def patch(font: fontforge.font, legacy=True):
	"""
	:param legacy: Set to False for the new community encoding standard.
		(see https://wiki.xdi8.top/index.php?oldid=32456)
		Note: due to the new standard having added, removed and modified some of the letters,
		currently only partial support is available
	"""
	suffix = "XdPUA" if legacy else "Xdi8"

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

	## basic letters: new #x00-2d = old #0-45
	for ind in range(89 if legacy else 46):
		for cas in range(3):
			setAlt(0xf1b00 + ind + cas * 0x60, 0xe020 + ind % 16 + cas * 16 + ind // 16 * 48)

	if not legacy:
		## supplementary letters (newExtInd = new# - 0x40)
		def setAltForSupplementaryLetter(ind, newExtInd):
			for cas in range(3):
				setAlt(0xf1b00 + ind + cas * 0x60, 0xe100 + newExtInd % 16 + cas * 16 + newExtInd // 16 * 64)

		for ind in range(46, 78):
			setAltForSupplementaryLetter(ind, ind - 46) # new #x40-5f = old #46-95

		setAltForSupplementaryLetter(82, 0x20) # new #x60 = old #82 音

	## miscellaneous characters
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
	font.fontname += suffix
	font.fullname += f" {suffix}"
	font.familyname += f" {suffix}"
	font.copyright = f"{font.fullname} by DGCK81LNN, based on {name} by Kreative Software, version {font.version}.\n\n{font.copyright}"

	# Fix font not loading in Chrome due to corrupted OS/2 table
	# (OTS parsing error: OS/2: Failed to parse table)
	font.os2_version = 4

import os
import sys

os.makedirs("output", exist_ok=True)

def heading(text: str):
	print(f"\033[m{text}\033[2m", file=sys.stderr)
def clear_color():
	print("\033[m", end="", file=sys.stderr)

def patchFont(
	path: str,
	legacy: bool,
	*,
	formats: tuple[str] = ("ttf", "woff2", "woff"),
):
	try:
		heading(f"Open {path}")
		font = fontforge.open(path)

		heading(f"Patch ({'Legacy Encoding' if legacy else 'New Standard'})")
		patch(font, legacy)
		fontname = font.fontname
		for format in formats:
			heading(f"Generate {fontname}.{format}")
			font.generate(f"output/{fontname}.{format}")
		heading(f"Close {path}")
		font.close()
		clear_color()
	except BaseException as e:
		clear_color()
		raise e

def patchBothEncodings(path: str, **kwargs):
	patchFont(path, True, **kwargs)
	patchFont(path, False, **kwargs)

patchBothEncodings("input/FairfaxHD.ttf")
patchBothEncodings("input/Fairfax.ttf")
patchBothEncodings("input/FairfaxSMHD.ttf", formats=("ttf",))
patchBothEncodings("input/FairfaxSM.ttf", formats=("ttf",))
patchBothEncodings("input/FairfaxSerif.ttf")
patchBothEncodings("input/FairfaxSerifSM.ttf", formats=("ttf",))
