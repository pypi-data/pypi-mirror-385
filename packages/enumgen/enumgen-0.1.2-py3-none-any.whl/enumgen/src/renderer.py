import typing as t
from abc import ABC, abstractmethod

import jinja2


class FileRenderer(ABC):
	@abstractmethod
	def __call__(self, **params: t.Any) -> int:
		pass


class FuncFileRenderer(FileRenderer):
	Renderer = t.Callable[..., str]

	def __init__(self, out: t.TextIO, renderer: Renderer) -> None:
		self.__out = out
		self.__renderer = renderer

	def __call__(self, **params: t.Any) -> int:
		rendered = self.__renderer(**params)
		return self.__out.write(rendered)


class FileManagingRenderer(FileRenderer):
	RendererBuilder = t.Callable[[t.TextIO], FileRenderer]

	def __init__(self,
		filename: str,
		subRendererBuilder: RendererBuilder
	) -> None:
		self.__filename = filename
		self.__subRendererBuilder = subRendererBuilder

	def __call__(self, **params: t.Any) -> int:
		with open(self.__filename, mode="w") as file:
			renderer = self.__subRendererBuilder(file)
			writtenCharCount = renderer(**params)
		return writtenCharCount


class MultiFileRenderer(FileRenderer):
	def __init__(self, *renderers: FileRenderer) -> None:
		self.__renderers = renderers

	def __call__(self, **params: t.Any) -> int:
		writtenCharCount = 0
		for renderer in self.__renderers:
			writtenCharCount += renderer(**params)
		return writtenCharCount


class ParamAddingFileRenderer(FileRenderer):
	def __init__(self,
		subRenderer: FileRenderer,
		**additionalParams: t.Any
	) -> None:
		self.__subRenderer = subRenderer
		self.__additionalParams = additionalParams

	def __call__(self, **params: t.Any) -> int:
		params |= self.__additionalParams
		return self.__subRenderer(**(params|self.__additionalParams))


class J2Renderer:
	def __init__(self, template: jinja2.Template) -> None:
		self.__template = template

	def __call__(self, **params: t.Any) -> str:
		rendered = self.__template.render(params)
		if isinstance(rendered, str):
			return rendered
		raise RuntimeError("render failed")
