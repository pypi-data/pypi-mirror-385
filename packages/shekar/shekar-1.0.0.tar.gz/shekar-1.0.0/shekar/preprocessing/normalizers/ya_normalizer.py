from shekar.base import BaseTextTransform


class YaNormalizer(BaseTextTransform):
    """
    Normalizes Ya in the text regarding the offical Persian script standard published by the Iranian Academy of Language and Literature.
    reference: https://apll.ir/

    There are two styles available:
    - "standard": Follows the official Persian script standard.
    - "joda" (default): Follows the Joda script style.

    Examples:
        >>> ya_normalizer = YaNormalizer(style="standard")
        >>> ya_normalizer("خانه‌ی ما")
        "خانۀ ما"
        >>> ya_normalizer = YaNormalizer(style="joda")
        >>> ya_normalizer("خانۀ ما")
        "خانه‌ی ما"
    """

    def __init__(self, style="joda"):
        super().__init__()
        if style == "standard":
            self._ya_mappings = [
                (r"ه‌ی", "ۀ"),
                (r"ه ی", "ۀ"),
            ]
        elif style == "joda":
            self._ya_mappings = [
                (r"ۀ", "ه‌ی"),
                (r"ه ی", "ه‌ی"),
            ]

        self._patterns = self._compile_patterns(self._ya_mappings)

    def _function(self, text: str) -> str:
        return self._map_patterns(text, self._patterns).strip()
