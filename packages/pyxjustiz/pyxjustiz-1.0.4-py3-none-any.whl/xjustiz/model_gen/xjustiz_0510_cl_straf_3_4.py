from dataclasses import dataclass, field
from typing import Any, Optional

from xjustiz.model_gen.xoev_code import Code

__NAMESPACE__ = "http://www.xjustiz.de"


@dataclass
class CodeStrafAbwesenheitsartTyp3(Code):
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
        name = "Code.STRAF.Abwesenheitsart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.abwesenheitsart",
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


@dataclass
class CodeStrafAnordnungsartTyp3(Code):
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
        name = "Code.STRAF.Anordnungsart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.anordnungsart",
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


@dataclass
class CodeStrafAsservatAuftragTyp3(Code):
    """
    :ivar name: Mit diesem optionalen XML-Element kann die Beschreibung
        des Codes, wie in der jeweiligen Beschreibungsspalte der
        Codeliste vorgegeben, übermittelt werden.
    :ivar list_uri:
    :ivar list_version_id:
    """

    class Meta:
        name = "Code.STRAF.Asservat.Auftrag.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.asservat.auftrag",
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


@dataclass
class CodeStrafAsservatGegenstandsartTyp3(Code):
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
        name = "Code.STRAF.Asservat.Gegenstandsart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.asservat.gegenstandsart",
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


@dataclass
class CodeStrafAsservatStatusmitteilungTyp3(Code):
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
        name = "Code.STRAF.Asservat.Statusmitteilung.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.asservat.statusmitteilung",
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


@dataclass
class CodeStrafAuflagenTyp3(Code):
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
        name = "Code.STRAF.Auflagen.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.auflagen",
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


@dataclass
class CodeStrafBescheidartTyp3(Code):
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
        name = "Code.STRAF.Bescheidart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.bescheidart",
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


@dataclass
class CodeStrafBeschlussartTyp3(Code):
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
        name = "Code.STRAF.Beschlussart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.beschlussart",
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


@dataclass
class CodeStrafBesuchserlaubnisartTyp3(Code):
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
        name = "Code.STRAF.Besuchserlaubnisart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.besuchserlaubnisart",
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


@dataclass
class CodeStrafBeteiligungsartTyp3(Code):
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
        name = "Code.STRAF.Beteiligungsart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.beteiligungsart",
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


@dataclass
class CodeStrafBeweismittelTyp3(Code):
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
        name = "Code.STRAF.Beweismittel.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.beweismittel",
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


@dataclass
class CodeStrafEinstellungsartTyp3(Code):
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
        name = "Code.STRAF.Einstellungsart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.einstellungsart",
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


@dataclass
class CodeStrafEntscheidungsartTyp3(Code):
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
        name = "Code.STRAF.Entscheidungsart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.entscheidungsart",
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


@dataclass
class CodeStrafErgebnisartTyp3(Code):
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
        name = "Code.STRAF.Ergebnisart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.ergebnisart",
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


@dataclass
class CodeStrafErledigungsartenTyp3(Code):
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
        name = "Code.STRAF.Erledigungsarten.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.erledigungsarten",
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


@dataclass
class CodeStrafFahndungsanlassTyp3(Code):
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
        name = "Code.STRAF.Fahndungsanlass.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.fahndungsanlass",
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


@dataclass
class CodeStrafFahndungsregionTyp3(Code):
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
        name = "Code.STRAF.Fahndungsregion.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.fahndungsregion",
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


@dataclass
class CodeStrafFahndungsverfahrenTyp3(Code):
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
        name = "Code.STRAF.Fahndungsverfahren.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.fahndungsverfahren",
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


@dataclass
class CodeStrafFahndungszweckTyp3(Code):
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
        name = "Code.STRAF.Fahndungszweck.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.fahndungszweck",
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


@dataclass
class CodeStrafGeldanordnungsartTyp3(Code):
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
        name = "Code.STRAF.Geldanordnungsart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.geldanordnungsart",
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


@dataclass
class CodeStrafHaftartTyp3(Code):
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
        name = "Code.STRAF.Haftart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.haftart",
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


@dataclass
class CodeStrafHaftbeginnTyp3(Code):
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
        name = "Code.STRAF.Haftbeginn.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.haftbeginn",
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


@dataclass
class CodeStrafHaftzeitendeartTyp3(Code):
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
        name = "Code.STRAF.Haftzeitendeart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.haftzeitendeart",
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


@dataclass
class CodeStrafHerkunftsartTyp3(Code):
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
        name = "Code.STRAF.Herkunftsart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.herkunftsart",
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


@dataclass
class CodeStrafHydaneHerkunftDerDatenTyp3(Code):
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
        name = "Code.STRAF.Hydane.HerkunftDerDaten.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.hydane.herkunft-der-daten",
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


@dataclass
class CodeStrafLoeschungsgrundTyp3(Code):
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
        name = "Code.STRAF.Loeschungsgrund.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.loeschungsgrund",
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


@dataclass
class CodeStrafOwiErledigungsartTyp3(Code):
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
        name = "Code.STRAF.OWI.Erledigungsart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.owi.erledigungsart",
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


@dataclass
class CodeStrafPruefvorschriftTyp3(Code):
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
        name = "Code.STRAF.Pruefvorschrift.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.pruefvorschrift",
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


@dataclass
class CodeStrafRechtsfolgenTyp3(Code):
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
        name = "Code.STRAF.Rechtsfolgen.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.rechtsfolgen",
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


@dataclass
class CodeStrafRechtsmittelTyp3(Code):
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
        name = "Code.STRAF.Rechtsmittel.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.rechtsmittel",
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


@dataclass
class CodeStrafVaErledigungsartTyp3(Code):
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
        name = "Code.STRAF.VA.Erledigungsart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.va.erledigungsart",
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


@dataclass
class CodeStrafVerbleibsartTyp3(Code):
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
        name = "Code.STRAF.Verbleibsart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.verbleibsart",
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


@dataclass
class CodeStrafWeisungenTyp3(Code):
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
        name = "Code.STRAF.Weisungen.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.weisungen",
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
