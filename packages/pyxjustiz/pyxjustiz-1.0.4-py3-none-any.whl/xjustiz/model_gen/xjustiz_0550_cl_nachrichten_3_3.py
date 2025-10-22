from dataclasses import dataclass, field
from typing import Any, Optional

from xjustiz.model_gen.xoev_code import Code

__NAMESPACE__ = "http://www.xjustiz.de"


@dataclass
class CodeStrafAstralTyp3(Code):
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
        name = "Code.STRAF.ASTRAL.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.astral",
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
class CodeStrafAnordnungsbefugterTyp3(Code):
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
        name = "Code.STRAF.Anordnungsbefugter.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.anordnungsbefugter",
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
class CodeStrafBfjArtDerAuskunftsdatenTyp3(Code):
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
        name = "Code.STRAF.BFJ.ArtDerAuskunftsdaten.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.bfj.artderauskunftsdaten",
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
class CodeStrafBfjBzrFreiheitsentziehungArtTyp3(Code):
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
        name = "Code.STRAF.BFJ.BZR.FreiheitsentziehungArt.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:bzr.freiheitsentziehungart",
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
class CodeStrafBfjBzrHinweisArtTyp3(Code):
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
        name = "Code.STRAF.BFJ.BZR.HinweisArt.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:bzr.hinweisart",
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
class CodeStrafBfjBzrTextkennzahlTyp3(Code):
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
        name = "Code.STRAF.BFJ.BZR.Textkennzahl.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:bzr.textkennzahl",
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
class CodeStrafBfjBehoerdenfuehrungszeugnisBzrGrundTyp3(Code):
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
        name = "Code.STRAF.BFJ.Behoerdenfuehrungszeugnis.BZR.Grund.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:bzr.behoerdenfuehrungszeugnisgrund",
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
class CodeStrafBfjBenachrichtigungGrundTyp3(Code):
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
        name = "Code.STRAF.BFJ.BenachrichtigungGrund.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:bfj.benachrichtigunggrund",
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
class CodeStrafBfjGzrGewerbeartTyp3(Code):
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
        name = "Code.STRAF.BFJ.GZR.Gewerbeart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:gzr.gewerbeart",
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
class CodeStrafBfjGzrGewerbeschluesselTyp3(Code):
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
        name = "Code.STRAF.BFJ.GZR.Gewerbeschluessel.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:gzr.gewerbeschluessel",
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
class CodeStrafBfjGzrRechtsvorschriftenTyp3(Code):
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
        name = "Code.STRAF.BFJ.GZR.Rechtsvorschriften.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:gzr.rechtsvorschriften",
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
class CodeStrafBfjGzrTextkennzahlTyp3(Code):
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
        name = "Code.STRAF.BFJ.GZR.Textkennzahl.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:gzr.textkennzahl",
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
class CodeStrafBfjHinweisAnlassTyp3(Code):
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
        name = "Code.STRAF.BFJ.HinweisAnlass.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:bfj.hinweisanlass",
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
class CodeStrafBfjNachrichtencodeBzrAnfrageUnbeschraenkteAuskunftTyp3(Code):
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
        name = "Code.STRAF.BFJ.Nachrichtencode.BZR.Anfrage.UnbeschraenkteAuskunft.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:nachrichtencode.bzr.anfrageunbeschraenkteauskunft",
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
class CodeStrafBfjNachrichtencodeBzrAntragBehoerdenfuehrungszeugnisTyp3(Code):
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
        name = "Code.STRAF.BFJ.Nachrichtencode.BZR.Antrag.Behoerdenfuehrungszeugnis.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:nachrichtencode.bzr.antragbehoerdenfuehrungszeugnis",
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
class CodeStrafBfjNachrichtencodeBzrAuskunftTyp3(Code):
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
        name = "Code.STRAF.BFJ.Nachrichtencode.BZR.Auskunft.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:nachrichtencode.bzr.auskunft",
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
class CodeStrafBfjNachrichtencodeBzrMitteilungenTyp3(Code):
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
        name = "Code.STRAF.BFJ.Nachrichtencode.BZR.Mitteilungen.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:nachrichtencode.bzr.mitteilung",
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
class CodeStrafBfjNachrichtencodeGzrAnfrageOeffentlicheStelleTyp3(Code):
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
        name = "Code.STRAF.BFJ.Nachrichtencode.GZR.Anfrage.OeffentlicheStelle.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:nachrichtencode.gzr.anfrageoeffentlichestelle",
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
class CodeStrafBfjNachrichtencodeGzrAuskunftTyp3(Code):
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
        name = "Code.STRAF.BFJ.Nachrichtencode.GZR.Auskunft.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:nachrichtencode.gzr.auskunft",
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
class CodeStrafBfjNachrichtencodeGzrMitteilungenTyp3(Code):
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
        name = "Code.STRAF.BFJ.Nachrichtencode.GZR.Mitteilungen.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:nachrichtencode.gzr.mitteilung",
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
class CodeStrafBfjUebermittelndeStelleTyp3(Code):
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
        name = "Code.STRAF.BFJ.UebermittelndeStelle.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:bfj.uebermittelndestelle",
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
class CodeStrafBfjVerwendungszweckAuskunftTyp3(Code):
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
        name = "Code.STRAF.BFJ.VerwendungszweckAuskunft.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:bund:bfj:codeliste:bfj.verwendungszweckauskunft",
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
class CodeStrafMassnahmeartTyp3(Code):
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
        name = "Code.STRAF.Massnahmeart.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.massnahmeart",
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
class CodeStrafMassnahmegegenstandTyp3(Code):
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
        name = "Code.STRAF.Massnahmegegenstand.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.massnahmegegenstand",
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
class CodeStrafSicherungsmassnahmeTyp3(Code):
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
        name = "Code.STRAF.Sicherungsmassnahme.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.sicherungsmassnahme",
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
class CodeStrafTatmerkmalTyp3(Code):
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
        name = "Code.STRAF.Tatmerkmal.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.tatmerkmal",
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
class CodeStrafWebRegZurechnungTyp3(Code):
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
        name = "Code.STRAF.WebReg.Zurechnung.Typ3"

    name: Any = field(
        init=False,
        default=None,
        metadata={
            "type": "Ignore",
        },
    )
    list_uri: str = field(
        init=False,
        default="urn:xoev-de:xjustiz:codeliste:straf.webreg.zurechnung",
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
