import logging

from ..exceptions import NotLoadedOrEmpty, UnknownTxtEncoding
from ..factory.resource_manager import ResourceManager
from ..handlers.base_handler import FileHandler
from ..tools.text_postproc import TextPostprocessor
from ..utils.constants import TXT_HANDLER_ENCODINGS

logger = logging.getLogger("rara-digitizer")


class TXTHandler(FileHandler):
    def __init__(
        self, file_path: str, resource_manager: ResourceManager, **kwargs
    ) -> None:
        """
        Initializes the TXTHandler by loading the TXT document into `self.document`.

        Parameters
        ----------
        file_path : str
            The path to the TXT file.

        resource_manager: ResourceManager
            Class that caches and returns statically used resources throughout different tools and handlers.

        Keyword Arguments
        -----------------
        text_length_cutoff: str
            Minimum length texts need to be evaluated.

        evaluator_default_response: Any
            Default quality value for texts that don't make the length cutoff.

        txt_handler_encodings: List[str]
            Possible encodings for reading the txt file, in order of priority
        """
        super().__init__(file_path)
        self.resource_manager = resource_manager
        self.encodings = kwargs.get("txt_handler_encodings", TXT_HANDLER_ENCODINGS)

        self.text_postprocessor = TextPostprocessor(self.resource_manager, **kwargs)

        self._read_txt()
        self.estimate_page_count = True

    def _read_txt(self) -> None:
        """
        Reads the TXT file and stores the document in `self.document`.
        """
        for enc in self.encodings:
            try:
                with open(self.file_path, "r", encoding=enc) as file:
                    self.document = file.read()
                return
            except UnicodeDecodeError as e:
                logger.warning(f"Failed to decode with {enc}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error reading TXT file with {enc}: {e}")
                raise

        logger.error("All decoding attempts failed.")
        raise UnknownTxtEncoding(f"File has unknown encoding. None of {self.encodings} worked")

    def requires_ocr(self) -> bool:
        """
        TXT files do not require OCR.

        Returns
        -------
        bool
            Always returns False since TXT files contain machine-readable text.
        """
        return False

    def extract_text(self) -> list[dict[str, str | int | None]]:
        """
        Extracts text from a TXT file.

        Raises
        ------
        NotLoadedOrEmpty
            If the TXT document has not been loaded or is empty.

        Returns
        -------
        list[dict[str, str | int | None]]
            The extracted text from the file, if extraction fails, returns None.
        """
        if not self.document:
            raise NotLoadedOrEmpty("TXT document has not been loaded or is empty.")

        return (
            self.text_postprocessor.postprocess_text(
                input_data=self.document, split_long_texts=self.estimate_page_count
            )
            if self.document
            else []
        )

    def extract_images(self) -> list[dict[str, str | int | dict | None]]:
        """
        As there is no image data inside a TXT file, no images are extracted.

        Returns
        -------
        list[dict[str, str | int | dict | None]]
            An empty list as no images can be extracted from TXT files.
        """
        return []

    def extract_page_numbers(self) -> None:
        """
        TXT files are not paginated, no pages are extracted.

        Returns
        -------
        None
        """
        return None

    def extract_physical_dimensions(self) -> None:
        """
        TXT files do not have physical dimensions. Extracting physical dimensions returns None.

        Returns
        -------
        None
        """
        return None
