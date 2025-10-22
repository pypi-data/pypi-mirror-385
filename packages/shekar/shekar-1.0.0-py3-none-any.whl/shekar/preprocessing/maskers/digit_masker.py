from shekar.base import BaseTextTransform
from shekar import data


class DigitMasker(BaseTextTransform):
    """
    A text transformation class for filtering numbers from the text.

    This class inherits from `BaseTextTransform` and provides functionality to remove or replace
    all numeric characters from the text. It uses predefined mappings to eliminate
    Arabic, English, and other Unicode numbers, ensuring a clean and normalized text representation.

    The `DigitMasker` class includes `fit` and `fit_transform` methods, and it
    is callable, allowing direct application to text data.

    Methods:

        fit(X, y=None):
            Fits the transformer to the input data.
        transform(X, y=None):
            Transforms the input data by removing numbers.
        fit_transform(X, y=None):
            Fits the transformer to the input data and applies the transformation.

        __call__(text: str) -> str:
            Allows the class to be called as a function, applying the transformation
            to the input text.

    Example:
        >>> digit_masker = DigitMasker()
        >>> cleaned_text = digit_masker("این متن 1234 شامل اعداد است.")
        >>> print(cleaned_text)
        "این متن  شامل اعداد است."
    """

    def __init__(self, mask_token: str = ""):
        super().__init__()
        self._number_mappings = [
            (rf"[{data.numbers}]", mask_token),
        ]

        self._patterns = self._compile_patterns(self._number_mappings)

    def _function(self, text: str) -> str:
        return self._map_patterns(text, self._patterns).strip()
