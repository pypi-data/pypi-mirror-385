import typing as t
import os
import sys
import functools

import argparse
import commentjson as json
import jinja2

from . import \
	FileRenderer, FuncFileRenderer, FileManagingRenderer, \
	MultiFileRenderer, ParamAddingFileRenderer, \
	J2Renderer


DIR_BASENAME = os.path.basename(os.path.dirname(__file__))

HEADER_TEMPLATE_FILENAME = "header.j2"
SRC_TEMPLATE_FILENAME = "src.j2"
STANDALONE_TEMPLATE_FILENAME = "standalone.j2"

J2_ENV = jinja2.Environment(
	loader=jinja2.PackageLoader(DIR_BASENAME, "templates")
)


def renderEntryValue(entryName: str, value: t.Any) -> t.Any:
	if isinstance(value, str):
		return value.replace("$$", entryName)
	if isinstance(value, bool):
		return str(value).lower()
	return value


def mkSingleFileRenderer(
	ofilename: t.Union[str, None],
	textRenderer: t.Callable[..., str]
) -> FileRenderer:
	if ofilename:
		renderBuilder = functools.partial(
			FuncFileRenderer,
			renderer=textRenderer
		)
		return FileManagingRenderer(ofilename, renderBuilder)
	return FuncFileRenderer(sys.stdout, textRenderer)


def mkFileRenderer(
	srcFilename: t.Union[str, None],
	headerFilename: t.Union[str, None]
) -> FileRenderer:
	if headerFilename:
		header = os.path.basename(headerFilename)
		additionalParams = {
			"header": header,
			"guard": header.replace(".", "_").replace("-", "_").upper()
		}
		headerTextRenderer \
			= J2Renderer(J2_ENV.get_template(HEADER_TEMPLATE_FILENAME))
		srcTextRenderer = J2Renderer(J2_ENV.get_template(SRC_TEMPLATE_FILENAME))
		return MultiFileRenderer(
			ParamAddingFileRenderer(mkSingleFileRenderer(
				headerFilename, headerTextRenderer
			), **additionalParams),
			ParamAddingFileRenderer(mkSingleFileRenderer(
				srcFilename, srcTextRenderer
			), **additionalParams),
		)
	srcTextRenderer \
		= J2Renderer(J2_ENV.get_template(STANDALONE_TEMPLATE_FILENAME))
	return mkSingleFileRenderer(srcFilename, srcTextRenderer)

	
def parseArgs() -> argparse.Namespace:
	prs = argparse.ArgumentParser(DIR_BASENAME)
	prs.add_argument("config", help="Configuration filename")
	prs.add_argument("-o", "--output",
		help="Output filename (stdout by default)")
	prs.add_argument("-d", "--define-header",
		help="Also produce the header file")
	return prs.parse_args()


if __name__ == "__main__":
	args = parseArgs()

	fileRenderer = mkFileRenderer(args.output, args.define_header)

	with open(args.config) as file:
		params = json.load(file)
	
	fileRenderer(**params, renderEntryValue=renderEntryValue)
