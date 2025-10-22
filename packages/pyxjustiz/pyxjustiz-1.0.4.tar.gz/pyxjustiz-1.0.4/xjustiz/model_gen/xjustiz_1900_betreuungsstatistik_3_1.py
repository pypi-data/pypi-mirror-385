from dataclasses import dataclass, field
from typing import Optional

from xsdata.models.datatype import XmlDate

from xjustiz.model_gen.xjustiz_0000_grunddatensatz_3_5 import (
    TypeGdsAktenzeichen,
    TypeGdsGeldbetrag,
    TypeGdsGrunddaten,
    TypeGdsNachrichtenkopf,
)
from xjustiz.model_gen.xjustiz_0010_cl_allgemein_3_6 import CodeGdsGeschlecht
from xjustiz.model_gen.xjustiz_1910_cl_betreuungsstatistik_3_0 import (
    CodeBestatArtGenehmigung,
    CodeBestatArtZahlung,
    CodeBestatAufgabenkreis,
    CodeBestatBeendigungBetreuung,
    CodeBestatBetreuerauswahl,
    CodeBestatEinleitungBetreuung,
    CodeBestatEntscheidungImLaufendenVerfahren,
    CodeBestatEntscheidungUeberEinrichtungDerBetreuung,
    CodeBestatGeschaeftsanfall,
    CodeBestatVeraenderung,
)

__NAMESPACE__ = "http://www.xjustiz.de"


@dataclass
class TypeBestatVerfahrenserhebung:
    """
    :ivar verfahren_id: Hier kann später auch die bundesweit eindeutige
        ID des gerichtlichen Verfahrens verwendet werden - bis dahin
        muss es eine für dieses Dokument eindeutige Nummer sein.
    :ivar aktenzeichen:
    :ivar schluesselzahl_erhebungseinheit: 5-stellige Zahl mit führender
        9
    :ivar lfd_nr_ve: 4-stellig
    :ivar value_002_tag_des_eingangs_der_sache:
    :ivar value_003_abgabe_innerhalb: zu liefern, wenn ja
    :ivar einleitung_des_verfahrens:
    :ivar person_betroffener:
    :ivar entscheidung_einrichtung: nicht öfter als zweimal, aber nur
        einmal je für vorläufig und einmal endgültig. Nicht liefern,
        wenn noch keine Einleitung
    :ivar art_betreuer:
    :ivar aufgabenkreise:
    :ivar veraenderung_im_berichtszeitraum: nicht öfter als zweimal,
        aber nur einmal je für vorläufig und einmal endgültig
    :ivar entscheidung_im_laufenden_verfahren: darf 6-mal, aber nur je
        dreimal je für vorläufig und dreimal endgültig
    :ivar value_007_anzahl_sachverstaendigengutachten: 0 bis höchstens
        99 in der Periode
    :ivar anordnung_einwilligungsvorbehalt:
    :ivar genehmigungen: 30-mal vorläufig ja und 30-mal vorläufig nein
    :ivar value_008_anzahl_ehrenamtliche_verfahrenspfleger: 0 bis
        höchstens 99 in der Periode
    :ivar value_009_anzahl_berufsmaessige_verfahrenspfleger: 0 bis
        höchstens 99 in der Periode
    :ivar beendigung: 0 bis 2-mal, wenn verschieden von 0 dann einmal
        vorläufig ja
    :ivar value_010_mittellosigkeit: wird nicht geliefert, wenn nicht
        bekannt
    :ivar value_011_aufenthalt_im_heim: wird nicht geliefert, wenn nicht
        bekannt
    :ivar zahlungen: nach Maßgabe der LJV
    :ivar value_017_tag_weglegung: auch endgültige Abgabe
    """

    class Meta:
        name = "Type.BESTAT.Verfahrenserhebung"

    verfahren_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "verfahren.ID",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
            "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )
    aktenzeichen: Optional[TypeGdsAktenzeichen] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    schluesselzahl_erhebungseinheit: Optional[str] = field(
        default=None,
        metadata={
            "name": "schluesselzahl.erhebungseinheit",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
            "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )
    lfd_nr_ve: Optional[str] = field(
        default=None,
        metadata={
            "name": "lfdNr.ve",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
            "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )
    value_002_tag_des_eingangs_der_sache: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "_002_tagDesEingangsDerSache",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    value_003_abgabe_innerhalb: Optional[bool] = field(
        default=None,
        metadata={
            "name": "_003_abgabe.innerhalb",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )
    einleitung_des_verfahrens: Optional[CodeBestatEinleitungBetreuung] = field(
        default=None,
        metadata={
            "name": "einleitungDesVerfahrens",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    person_betroffener: Optional[
        "TypeBestatVerfahrenserhebung.PersonBetroffener"
    ] = field(
        default=None,
        metadata={
            "name": "person.betroffener",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    entscheidung_einrichtung: list[
        "TypeBestatVerfahrenserhebung.EntscheidungEinrichtung"
    ] = field(
        default_factory=list,
        metadata={
            "name": "entscheidungEinrichtung",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "max_occurs": 2,
        },
    )
    art_betreuer: list["TypeBestatVerfahrenserhebung.ArtBetreuer"] = field(
        default_factory=list,
        metadata={
            "name": "art.betreuer",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "min_occurs": 16,
            "max_occurs": 16,
        },
    )
    aufgabenkreise: list["TypeBestatVerfahrenserhebung.Aufgabenkreise"] = (
        field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "max_occurs": 12,
            },
        )
    )
    veraenderung_im_berichtszeitraum: list[
        "TypeBestatVerfahrenserhebung.VeraenderungImBerichtszeitraum"
    ] = field(
        default_factory=list,
        metadata={
            "name": "veraenderungImBerichtszeitraum",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "max_occurs": 2,
        },
    )
    entscheidung_im_laufenden_verfahren: list[
        "TypeBestatVerfahrenserhebung.EntscheidungImLaufendenVerfahren"
    ] = field(
        default_factory=list,
        metadata={
            "name": "entscheidungImLaufendenVerfahren",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "max_occurs": 6,
        },
    )
    value_007_anzahl_sachverstaendigengutachten: Optional[int] = field(
        default=None,
        metadata={
            "name": "_007_anzahl.sachverstaendigengutachten",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    anordnung_einwilligungsvorbehalt: Optional[
        "TypeBestatVerfahrenserhebung.AnordnungEinwilligungsvorbehalt"
    ] = field(
        default=None,
        metadata={
            "name": "anordnungEinwilligungsvorbehalt",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    genehmigungen: list["TypeBestatVerfahrenserhebung.Genehmigungen"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "min_occurs": 60,
            "max_occurs": 60,
        },
    )
    value_008_anzahl_ehrenamtliche_verfahrenspfleger: Optional[int] = field(
        default=None,
        metadata={
            "name": "_008_anzahl.ehrenamtlicheVerfahrenspfleger",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    value_009_anzahl_berufsmaessige_verfahrenspfleger: Optional[int] = field(
        default=None,
        metadata={
            "name": "_009_anzahl.berufsmaessigeVerfahrenspfleger",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    beendigung: list["TypeBestatVerfahrenserhebung.Beendigung"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "max_occurs": 2,
        },
    )
    value_010_mittellosigkeit: Optional[bool] = field(
        default=None,
        metadata={
            "name": "_010_mittellosigkeit",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )
    value_011_aufenthalt_im_heim: Optional[bool] = field(
        default=None,
        metadata={
            "name": "_011_aufenthaltImHeim",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )
    zahlungen: Optional["TypeBestatVerfahrenserhebung.Zahlungen"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )
    value_017_tag_weglegung: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "_017_tagWeglegung",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )

    @dataclass
    class PersonBetroffener:
        """
        :ivar value_005_geschlecht:
        :ivar value_006_geburtsjahr: nicht liefern wenn unbekannt, sonst
            4-stellig
        """

        value_005_geschlecht: Optional[CodeGdsGeschlecht] = field(
            default=None,
            metadata={
                "name": "_005_geschlecht",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )
        value_006_geburtsjahr: Optional[str] = field(
            default=None,
            metadata={
                "name": "_006_geburtsjahr",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
            },
        )

    @dataclass
    class EntscheidungEinrichtung:
        art_entscheidung_einrichtung: Optional[
            CodeBestatEntscheidungUeberEinrichtungDerBetreuung
        ] = field(
            default=None,
            metadata={
                "name": "art.entscheidungEinrichtung",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        vorlaeufig: Optional[bool] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        datum_entscheidung: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "datum.entscheidung",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )

    @dataclass
    class ArtBetreuer:
        """
        :ivar betreuung_durch:
        :ivar zahl: Werte 0-9 zulässig
        :ivar vorlaeufig:
        """

        betreuung_durch: Optional[CodeBestatBetreuerauswahl] = field(
            default=None,
            metadata={
                "name": "betreuungDurch",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        zahl: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        vorlaeufig: Optional[bool] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )

    @dataclass
    class Aufgabenkreise:
        art_aufgabenkreis: Optional[CodeBestatAufgabenkreis] = field(
            default=None,
            metadata={
                "name": "art.aufgabenkreis",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        vorlaeufig: Optional[bool] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )

    @dataclass
    class VeraenderungImBerichtszeitraum:
        art_veraenderung: Optional[CodeBestatVeraenderung] = field(
            default=None,
            metadata={
                "name": "art.veraenderung",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        vorlaeufig: Optional[bool] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )

    @dataclass
    class EntscheidungImLaufendenVerfahren:
        art_entscheidung_laufend: Optional[
            CodeBestatEntscheidungImLaufendenVerfahren
        ] = field(
            default=None,
            metadata={
                "name": "art.entscheidungLaufend",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        vorlaeufig: Optional[bool] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )

    @dataclass
    class AnordnungEinwilligungsvorbehalt:
        """
        :ivar anzahl_vorl: 0 bis höchstens 99 in der Periode
        :ivar anzahl_ord: 0 bis höchstens 99 in der Periode
        """

        anzahl_vorl: Optional[int] = field(
            default=None,
            metadata={
                "name": "anzahlVorl",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        anzahl_ord: Optional[int] = field(
            default=None,
            metadata={
                "name": "anzahlOrd",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )

    @dataclass
    class Genehmigungen:
        art_genehmigung: Optional[CodeBestatArtGenehmigung] = field(
            default=None,
            metadata={
                "name": "art.genehmigung",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        zahl: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        vorlaeufig: Optional[bool] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )

    @dataclass
    class Beendigung:
        art_beendigung: Optional[CodeBestatBeendigungBetreuung] = field(
            default=None,
            metadata={
                "name": "art.beendigung",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        vorlaeufig: Optional[bool] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        datum_beendigung: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "datum.beendigung",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )

    @dataclass
    class Zahlungen:
        art_zahlung: Optional[CodeBestatArtZahlung] = field(
            default=None,
            metadata={
                "name": "art.zahlung",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        betrag_zahlung: Optional[TypeGdsGeldbetrag] = field(
            default=None,
            metadata={
                "name": "betrag.zahlung",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )


@dataclass
class NachrichtBestatMonatsmeldung1900001:
    class Meta:
        name = "nachricht.bestat.monatsmeldung.1900001"
        namespace = "http://www.xjustiz.de"

    nachrichtenkopf: Optional[TypeGdsNachrichtenkopf] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    grunddaten: Optional[TypeGdsGrunddaten] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    fachdaten: Optional["NachrichtBestatMonatsmeldung1900001.Fachdaten"] = (
        field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
            },
        )
    )

    @dataclass
    class Fachdaten:
        berichtsmonat: Optional[
            "NachrichtBestatMonatsmeldung1900001.Fachdaten.Berichtsmonat"
        ] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
            },
        )

        @dataclass
        class Berichtsmonat:
            monat: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "required": True,
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            verfahrenserhebung: list[TypeBestatVerfahrenserhebung] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                    "min_occurs": 1,
                },
            )
            besondere_erhebung: list[
                "NachrichtBestatMonatsmeldung1900001.Fachdaten.Berichtsmonat.BesondereErhebung"
            ] = field(
                default_factory=list,
                metadata={
                    "name": "besondereErhebung",
                    "type": "Element",
                    "min_occurs": 1,
                },
            )

            @dataclass
            class BesondereErhebung:
                """
                :ivar schluesselzahl_erhebungseinheit: 5-stellige Zahl
                    mit führender 9
                :ivar sonstiger_geschaeftsanfall: Jedes Element der
                    Codeliste genau einmal
                """

                schluesselzahl_erhebungseinheit: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "schluesselzahl.erhebungseinheit",
                        "type": "Element",
                        "required": True,
                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                    },
                )
                sonstiger_geschaeftsanfall: list[
                    "NachrichtBestatMonatsmeldung1900001.Fachdaten.Berichtsmonat.BesondereErhebung.SonstigerGeschaeftsanfall"
                ] = field(
                    default_factory=list,
                    metadata={
                        "name": "sonstigerGeschaeftsanfall",
                        "type": "Element",
                        "min_occurs": 42,
                        "max_occurs": 42,
                    },
                )

                @dataclass
                class SonstigerGeschaeftsanfall:
                    """
                    :ivar geschaeftsanfall:
                    :ivar zahl: 4-stellig mit führenden Nullen
                    """

                    geschaeftsanfall: Optional[CodeBestatGeschaeftsanfall] = (
                        field(
                            default=None,
                            metadata={
                                "type": "Element",
                                "required": True,
                            },
                        )
                    )
                    zahl: Optional[str] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                            "required": True,
                            "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                        },
                    )
