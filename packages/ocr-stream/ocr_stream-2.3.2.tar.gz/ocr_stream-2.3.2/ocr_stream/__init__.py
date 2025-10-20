#!/usr/bin/env python3

from ocr_stream.modules import *
from ocr_stream.bin_tess import BinTesseract, get_path_tesseract_sys
from ocr_stream.ocr import TesseractOcr, TextRecognized, DEFAULT_LIB_OCR
from ocr_stream.recognize import RecognizeImage, RecognizePdf
from soup_files import File
from convert_stream import (
    ImageObject, DocumentPdf, ConvertPdfToImages, ColumnsTable, CollectionImages, FindText
)
from pandas import DataFrame
from soup_files import JsonConvert, ProgressBarAdapter, CreatePbar


def read_images(
            images: list[ImageObject], *,
            pbar: ProgressBarAdapter = CreatePbar().get()
        ) -> DocumentPdf:
    pbar.start()
    print()
    max_num = len(images)
    pages = []
    rec = RecognizeImage()
    for idx, image in enumerate(images):
        pbar.update(
            ((idx + 1) / max_num) * 100,
            f'[OCR] {idx + 1} / {max_num}',
        )
        out = rec.image_recognize(image).to_page_pdf()
        pages.append(out)
    tmp_doc = DocumentPdf.create_from_pages(pages)
    print()
    pbar.stop()
    return tmp_doc


def read_document(
            document: DocumentPdf, *,
            dpi: int = 300,
            pbar: ProgressBarAdapter = CreatePbar().get()
        ) -> DocumentPdf:
    pbar.start()
    print()
    convert = ConvertPdfToImages.create(document)
    convert.set_pbar(pbar)
    images = convert.to_images(dpi=dpi)
    print()
    return read_images(images, pbar=pbar)


class SearchableTextImage(object):
    """
        Esta classe serve para armazenar textos filtrados em documentos PDF
    guardando o texto buscado e outros elementos como a página em que o texto foi
    encontrado, linha e o nome do respetivo arquivo.
    """
    def __init__(self, silent: bool = False):
        self.silent = silent
        self.elements: dict[str, list[str]] = {
            ColumnsTable.NUM_LINE.value: [],
            ColumnsTable.TEXT.value: [],
            ColumnsTable.FILE_PATH.value: [],
        }

    def __repr__(self):
        return f'{__class__.__name__}: {self.elements}'

    def is_empty(self) -> bool:
        return len(self.elements[ColumnsTable.TEXT.value]) == 0

    @property
    def first(self) -> dict[str, str]:
        if self.is_empty():
            return {}
        return {
            ColumnsTable.NUM_LINE.value: self.elements[ColumnsTable.NUM_LINE.value][0],
            ColumnsTable.TEXT.value: self.elements[ColumnsTable.TEXT.value][0],
            ColumnsTable.FILE_PATH.value: self.elements[ColumnsTable.FILE_PATH.value][0],
        }

    @property
    def last(self) -> dict[str, str]:
        if self.is_empty():
            return {}
        return {
            ColumnsTable.NUM_LINE.value: self.elements[ColumnsTable.NUM_LINE.value][-1],
            ColumnsTable.TEXT.value: self.elements[ColumnsTable.TEXT.value][-1],
            ColumnsTable.FILE_PATH.value: self.elements[ColumnsTable.FILE_PATH.value][-1],
        }

    @property
    def length(self) -> int:
        return len(self.elements[ColumnsTable.TEXT.value])

    @property
    def files(self) -> list[str]:
        if self.is_empty():
            return []
        return self.elements[ColumnsTable.FILE_PATH.value]

    def get_item(self, idx: int) -> dict[str, str]:
        try:
            return {
                ColumnsTable.NUM_LINE.value: self.elements[ColumnsTable.NUM_LINE.value][idx],
                ColumnsTable.TEXT.value: self.elements[ColumnsTable.TEXT.value][idx],
                ColumnsTable.FILE_PATH.value: self.elements[ColumnsTable.FILE_PATH.value][idx],
            }
        except Exception as err:
            if not self.silent:
                print(err)
            return {}

    def add_line(self, text, *, num_line: str, file: str) -> None:
        if not self.silent:
            print('----------------------')
            print(f'{file} => {text}')
        self.elements[ColumnsTable.NUM_LINE.value].append(num_line)
        self.elements[ColumnsTable.TEXT.value].append(text)
        self.elements[ColumnsTable.FILE_PATH.value].append(file)

    def clear(self) -> None:
        for _k in self.elements.keys():
            self.elements[_k].clear()

    def to_string(self) -> str:
        """
            Retorna o texto da coluna TEXT em formato de string
        ou 'nas' em caso de erro nas = Not a String
        """
        try:
            return ' '.join(self.elements[ColumnsTable.TEXT.value])
        except Exception as e:
            print(e)
            return 'nas'

    def to_data_frame(self) -> DataFrame:
        return DataFrame.from_dict(self.elements)

    def to_file_json(self, file: File):
        """Exporta os dados da busca para arquivo .JSON"""
        dt = JsonConvert.from_dict(self.elements).to_json_data()
        dt.to_file(file)

    def to_file_excel(self, file: File):
        """Exporta os dados da busca para um arquivo .XLSX"""
        try:
            self.to_data_frame().to_excel(file.absolute())
        except Exception as e:
            print(e)


class FindTextImages(object):

    def __init__(
                self, collection_images: CollectionImages,
                *,
                rec_img: RecognizeImage = RecognizeImage(),
                pbar: ProgressBarAdapter = CreatePbar().get(),
            ):
        self.collection_images: CollectionImages = collection_images
        self._rec_img: RecognizeImage = rec_img
        self.pbar: ProgressBarAdapter = pbar

    def find(
            self, text: str,
            separator: str = '\n',
            iqual: bool = False,
            case: bool = False,
            silent: bool = False,
    ) -> SearchableTextImage:
        """
            Filtrar texto retornando a primeira ocorrência do Documento PDF.
        """
        print()
        self.pbar.start()
        _searchable = SearchableTextImage(silent)

        max_num: int = self.collection_images.length
        for idx, image in enumerate(self.collection_images):
            self.pbar.update(
                ((idx + 1) / max_num) * 100,
                f'[Pesquisando]: {idx + 1} / {max_num} Aguarde...',
            )
            text_str_in_page: str = self._rec_img.image_to_string(image)

            if (text_str_in_page == 'nas') or (text_str_in_page is None):
                continue
            try:
                fd = FindText(text_str_in_page, separator=separator)
                idx = fd.find_index(text, iqual=iqual, case=case)
                if idx is None:
                    continue
                math_text = fd.get_index(idx)
            except Exception as err:
                print(f'{__class__.__name__} {err}')
            else:
                _searchable.add_line(
                    math_text,
                    num_line=str(idx + 1),
                    file=image.name,
                )
                return _searchable
        self.pbar.stop()
        print()
        return _searchable

    def find_all(
            self, text: str,
            separator: str = '\n',
            iqual: bool = False,
            case: bool = False,
            silent: bool = False,
    ) -> SearchableTextImage:
        """
            Filtrar texto em documento PDF e retorna todas as ocorrências do texto
        encontradas no documento, incluindo o número da linha, página e nome do arquivo
        em cada ocorrência.
        """
        print()
        self.pbar.start()
        _searchable = SearchableTextImage(silent)
        max_num: int = self.collection_images.length
        for idx, image in enumerate(self.collection_images):
            self.pbar.update(
                ((idx + 1) / max_num) * 100,
                f'[Pesquisando]: {idx + 1} / {max_num} Aguarde...',
            )

            text_str_in_page = self._rec_img.image_to_string(image)
            if (text_str_in_page == 'nas') or (text_str_in_page is None):
                continue
            try:
                _values = text_str_in_page.split(separator)
                for num, item in enumerate(_values):
                    if case:
                        if iqual:
                            if text == item:
                                _searchable.add_line(
                                    item,
                                    num_line=str(num + 1),
                                    file=image.name,
                                )
                        else:
                            if text in item:
                                _searchable.add_line(
                                    item,
                                    num_line=str(num + 1),
                                    file=image.name,
                                )
                    else:
                        if iqual:
                            if text.lower() == item.lower():
                                _searchable.add_line(
                                    item,
                                    num_line=str(num + 1),
                                    file=image.name,
                                )
                        else:
                            if text.lower() in item.lower():
                                _searchable.add_line(
                                    item,
                                    num_line=str(num + 1),
                                    file=image.name,
                                )
            except Exception as e:
                print(f'{__class__.__name__} {e}')
        self.pbar.stop()
        print()
        return _searchable
