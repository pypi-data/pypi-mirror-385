from dataclasses import dataclass, field
from typing import Optional

from xsdata.models.datatype import XmlDate, XmlPeriod

from xjustiz.model_gen.xjustiz_0000_grunddatensatz_3_5 import (
    TypeGdsGeldbetrag,
    TypeGdsGrunddaten,
    TypeGdsNachrichtenkopf,
    TypeGdsSchriftgutobjekte,
)
from xjustiz.model_gen.xjustiz_2110_cl_ehug_3_0 import (
    CodeEhugEbanzMeldungBfj,
    CodeEhugInfoBfj,
    CodeEhugPostZu,
)

__NAMESPACE__ = "http://www.xjustiz.de"


@dataclass
class TypeEhugFachdaten:
    """
    :ivar ergaenzungen_gesellschaft: Zur eindeutigen Bestimmung des
        Gegners des OG-Verfahrens.
    :ivar verfahrensgang_bfj:
    :ivar fachdaten_ehug_version:
    """

    class Meta:
        name = "Type.EHUG.Fachdaten"

    ergaenzungen_gesellschaft: Optional[
        "TypeEhugFachdaten.ErgaenzungenGesellschaft"
    ] = field(
        default=None,
        metadata={
            "name": "ergaenzungenGesellschaft",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    verfahrensgang_bfj: Optional["TypeEhugFachdaten.VerfahrensgangBfj"] = (
        field(
            default=None,
            metadata={
                "name": "verfahrensgang.BFJ",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
    )
    fachdaten_ehug_version: str = field(
        init=False,
        default="3.2",
        metadata={
            "name": "fachdatenEhugVersion",
            "type": "Attribute",
            "required": True,
            "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )

    @dataclass
    class ErgaenzungenGesellschaft:
        """
        :ivar ref_rollennummer: Hier ist ein Bezug zur Gesellschaft
            herzustellen wegen der das Verfahren durchgeführt wird.
        :ivar insolvenz:
        :ivar liquidation:
        :ivar loeschung:
        :ivar auswahl_geschaeftsjahr:
        """

        ref_rollennummer: Optional[str] = field(
            default=None,
            metadata={
                "name": "ref.rollennummer",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
            },
        )
        insolvenz: Optional[CodeEhugInfoBfj] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        liquidation: Optional[CodeEhugInfoBfj] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        loeschung: Optional[CodeEhugInfoBfj] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        auswahl_geschaeftsjahr: Optional[
            "TypeEhugFachdaten.ErgaenzungenGesellschaft.AuswahlGeschaeftsjahr"
        ] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )

        @dataclass
        class AuswahlGeschaeftsjahr:
            """
            :ivar geschaeftsjahr: Daten aus der Meldung BAnz, wenn
                identisch mit dem Inhalt des Ordnungsgeldbeschlusses
            :ivar abw_geschaeftsjahr:
            """

            geschaeftsjahr: Optional[XmlPeriod] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )
            abw_geschaeftsjahr: Optional[
                "TypeEhugFachdaten.ErgaenzungenGesellschaft.AuswahlGeschaeftsjahr.AbwGeschaeftsjahr"
            ] = field(
                default=None,
                metadata={
                    "name": "abwGeschaeftsjahr",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )

            @dataclass
            class AbwGeschaeftsjahr:
                """
                :ivar abw_geschaeftsjahr_von: Daten aus dem
                    angefochtenen OG-Beschluss, nur bei Abweichung vom
                    Kalenderjahr
                :ivar abw_geschaeftsjahr_bis: Daten aus dem
                    angefochtenen OG-Beschluss, nur bei Abweichung vom
                    Kalenderjahr
                """

                abw_geschaeftsjahr_von: Optional[XmlDate] = field(
                    default=None,
                    metadata={
                        "name": "abwGeschaeftsjahrVon",
                        "type": "Element",
                        "namespace": "http://www.xjustiz.de",
                        "required": True,
                    },
                )
                abw_geschaeftsjahr_bis: Optional[XmlDate] = field(
                    default=None,
                    metadata={
                        "name": "abwGeschaeftsjahrBis",
                        "type": "Element",
                        "namespace": "http://www.xjustiz.de",
                        "required": True,
                    },
                )

    @dataclass
    class VerfahrensgangBfj:
        """
        :ivar beschwerde_vom:
        :ivar eingang_am:
        :ivar beschluss_vom:
        :ivar zustellung_am:
        :ivar festgesetztes_ordnungsgeld:
        :ivar datum_offenlegung_vollstaendig: Wenn kein Datum übergeben
            wird, ist Offenlegung noch nicht vollständig.
        :ivar berichtsteil:
        :ivar ordnungsgeld:
        """

        beschwerde_vom: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "beschwerdeVom",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        eingang_am: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "eingangAm",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        beschluss_vom: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "beschlussVom",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        zustellung_am: Optional[XmlDate] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        festgesetztes_ordnungsgeld: Optional[TypeGdsGeldbetrag] = field(
            default=None,
            metadata={
                "name": "festgesetztesOrdnungsgeld",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        datum_offenlegung_vollstaendig: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "datum.offenlegung.vollstaendig",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )
        berichtsteil: list[
            "TypeEhugFachdaten.VerfahrensgangBfj.Berichtsteil"
        ] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "min_occurs": 1,
            },
        )
        ordnungsgeld: list[
            "TypeEhugFachdaten.VerfahrensgangBfj.Ordnungsgeld"
        ] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "min_occurs": 1,
            },
        )

        @dataclass
        class Berichtsteil:
            """
            :ivar erstmeldung:
            :ivar korrekturmeldung:
            :ivar bilanzsumme: wenn GJ größer 2012
            :ivar umsatzerloese: wenn GJ größer 2012
            :ivar mitarbeiterzahl: wenn GJ größer 2012
            """

            erstmeldung: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            korrekturmeldung: Optional[
                "TypeEhugFachdaten.VerfahrensgangBfj.Berichtsteil.Korrekturmeldung"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )
            bilanzsumme: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            umsatzerloese: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            mitarbeiterzahl: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )

            @dataclass
            class Korrekturmeldung:
                """
                :ivar korrekturgrund: Unterelement von Korrekturmeldung.
                :ivar korrekturgrund_freitext: Unterelement von
                    Korrekturmeldung zur näheren Erläuterung.
                """

                korrekturgrund: Optional[CodeEhugEbanzMeldungBfj] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "http://www.xjustiz.de",
                        "required": True,
                    },
                )
                korrekturgrund_freitext: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "korrekturgrund.freitext",
                        "type": "Element",
                        "namespace": "http://www.xjustiz.de",
                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                    },
                )

        @dataclass
        class Ordnungsgeld:
            """
            :ivar datum_androhungsverfuegung:
            :ivar hoehe_angedr_og:
            :ivar datum_zu_androhung: Tatsächliches Datum aus der
                Urkunde, nicht Eingang bei BfJ. (Liefermöglichkeit
                unklar, daher kein Pflichtfeld)
            :ivar uhrzeit_zu_androhung: Tatsächliche Uhrzeit aus der
                Urkunde (Liefermöglichkeit unklar, daher kein
                Pflichtfeld). Format: hh:mm
            :ivar art_zu_androhung: (Liefermöglichkeit unklar, daher
                kein Pflichtfeld)
            :ivar eingang_einspruch:
            :ivar datum_einspruch: wenn 'eingang.einspruch' = ja
            :ivar datum_einspruch_eingang: wenn 'eingang.einspruch' = ja
            :ivar ablauf_nachfrist: (Liefermöglichkeit unklar, daher
                kein Pflichtfeld)
            :ivar datum_og_beschluss: Bislang Feld 34 des csv
            :ivar hoehe_festg_og: Bislang Feld 35 des csv
            :ivar datum_zu_og: Tatsächliches Datum aus der Urkunde,
                nicht Eingang bei BfJ = Feld 36 der CSV
                (Liefermöglichkeit unklar, daher kein Pflichtfeld),
            :ivar art_zu_og: (Liefermöglichkeit unklar, daher kein
                Pflichtfeld)
            :ivar datum_sof_beschw: Bislang Feld 33 des csv
            :ivar eingang_sof_beschw: Bislang Feld 32 des csv
            :ivar datum_nichtabhilfebescheid: (Liefermöglichkeit unklar,
                daher kein Pflichtfeld)
            :ivar az_gerichtsentscheid: Bei weiteren Ordnungsgeldern
            :ivar datum_gerichtsentscheid: Bei weiteren Ordnungsgeldern
            :ivar datum_gerichtsentscheid_post: Wann ist der
                Gerichtsentscheid zur Post gegeben (zur Berechnung der
                Frist für weitere Androhungsverfügung).
            """

            datum_androhungsverfuegung: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.androhungsverfuegung",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )
            hoehe_angedr_og: Optional[TypeGdsGeldbetrag] = field(
                default=None,
                metadata={
                    "name": "hoehe.angedrOG",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )
            datum_zu_androhung: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.ZU.androhung",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )
            uhrzeit_zu_androhung: Optional[str] = field(
                default=None,
                metadata={
                    "name": "uhrzeit.ZU.androhung",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "pattern": r"(2[0-3]|[0-1]{0,1}[0-9]):[0-5][0-9]",
                },
            )
            art_zu_androhung: Optional[CodeEhugPostZu] = field(
                default=None,
                metadata={
                    "name": "art.ZU.androhung",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )
            eingang_einspruch: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "eingang.einspruch",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )
            datum_einspruch: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.einspruch",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )
            datum_einspruch_eingang: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.einspruch.eingang",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )
            ablauf_nachfrist: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "ablauf.nachfrist",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )
            datum_og_beschluss: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.OG-Beschluss",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )
            hoehe_festg_og: Optional[TypeGdsGeldbetrag] = field(
                default=None,
                metadata={
                    "name": "hoehe.festgOG",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )
            datum_zu_og: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.ZU.OG",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )
            art_zu_og: Optional[CodeEhugPostZu] = field(
                default=None,
                metadata={
                    "name": "art.ZU.OG",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )
            datum_sof_beschw: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.sofBeschw",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )
            eingang_sof_beschw: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "eingang.sofBeschw",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )
            datum_nichtabhilfebescheid: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.nichtabhilfebescheid",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )
            az_gerichtsentscheid: Optional[str] = field(
                default=None,
                metadata={
                    "name": "az.gerichtsentscheid",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            datum_gerichtsentscheid: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.gerichtsentscheid",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )
            datum_gerichtsentscheid_post: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.gerichtsentscheid.post",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )


@dataclass
class NachrichtEhugUebergabe2100001:
    class Meta:
        name = "nachricht.ehug.uebergabe.2100001"
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
    schriftgutobjekte: Optional[TypeGdsSchriftgutobjekte] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    fachdaten: Optional[TypeEhugFachdaten] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
