from dataclasses import dataclass, field
from typing import Any, Optional

from xjustiz.model_gen.xoev_code import Code

__NAMESPACE__ = "http://www.xjustiz.de"


@dataclass
class CodeGdsJustizvollzugTyp3(Code):
    """Die Werte einer Codeliste vom Code-Typ 3 können im XRepository eingesehen
    werden.

    Nähere Details sind im Kapitel "Codelisten vom Code-Typ 3"
    beschrieben.

    :ivar name: Mit diesem optionalen XML-Element kann die Beschreibung
        des Codes, wie in der jeweiligen Beschreibungsspalte der
        Codeliste vorgegeben, übermittelt werden.
    :ivar list_uri:
    :ivar list_version_id:
    """

    class Meta:
        name = "Code.GDS.Justizvollzug.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:gds.justizvollzug",
        metadata={
            "name": "listURI",
            "type": "Attribute",
        },
    )
    list_version_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "listVersionID",
            "type": "Attribute",
            "required": True,
        },
    )
