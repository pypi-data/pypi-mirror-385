from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional

from xsdata.models.datatype import XmlDate

from xjustiz.model_gen.xjustiz_0000_grunddatensatz_3_5 import (
    TypeGdsAktenzeichen,
    TypeGdsGeldbetrag,
    TypeGdsGrunddaten,
    TypeGdsNachrichtenkopf,
    TypeGdsRefRollennummer,
    TypeGdsSchriftgutobjekte,
)
from xjustiz.model_gen.xjustiz_0010_cl_allgemein_3_6 import (
    CodeGdsForderungsteil,
)
from xjustiz.model_gen.xjustiz_0020_cl_gerichte_3_3 import CodeGdsGerichteTyp3
from xjustiz.model_gen.xjustiz_2510_cl_gerichtsvollzieher_3_1 import (
    CodeGvzAuftragsart,
    CodeGvzBuchungstext,
    CodeGvzTitelart,
    CodeGvzZinsmethode,
)

__NAMESPACE__ = "http://www.xjustiz.de"


class TypeGvzForderungVerrechnungsart(Enum):
    VALUE_367_ZPO = "§ 367 ZPO"
    VALUE_497_ZPO = "§ 497 ZPO"


@dataclass
class TypeGvzForderung:
    """
    :ivar verrechnungsart: Information zur Art der Verrechnung von
        Zahlungen des Schuldners. Zulässige Werte: '§ 367 ZPO' oder '§
        497 ZPO'
    :ivar buchung:
    """

    class Meta:
        name = "Type.GVZ.Forderung"

    verrechnungsart: Optional[TypeGvzForderungVerrechnungsart] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )
    buchung: list["TypeGvzForderung.Buchung"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "min_occurs": 1,
        },
    )

    @dataclass
    class Buchung:
        """
        :ivar datum: Im Sinne einer chronologischen Kontenführung, die
            für Zahlungsverrechnung erforderlich ist, hat JEDE Buchung
            ein Datum.
        :ivar buchungsart:
        :ivar buchungstext: Als Information zur weiteren Differenzierung
            für den Anwender.
        :ivar betrag:
        :ivar forderungsnummer: Bei Buchungsarten wie z. B.
            "Zinsänderung" muss die zugehörige Forderung referenziert
            werden können.
        :ivar zinssatz: Erforderlich bei Zinsenberechung
        :ivar zinsmethode: Wenn ein Zinssatz angegeben wird, so muss
            auch die Zinssatzmethode angegegen werden.
        :ivar zinsbeginndatum: Erforderlich bei Zinsenberechung
        :ivar zinsendedatum:
        """

        datum: Optional[XmlDate] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        buchungsart: Optional[CodeGdsForderungsteil] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        buchungstext: Optional[CodeGvzBuchungstext] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )
        betrag: Optional[TypeGdsGeldbetrag] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        forderungsnummer: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
            },
        )
        zinssatz: Optional[Decimal] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )
        zinsmethode: Optional[CodeGvzZinsmethode] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )
        zinsbeginndatum: Optional[XmlDate] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )
        zinsendedatum: Optional[XmlDate] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )


@dataclass
class TypeGvzSchuldtitel:
    """
    :ivar titelart:
    :ivar titelbezeichnung: Z.B. wenn in Element 'titelart' Sonstiger
        ausgewählt worden ist.
    :ivar aktenzeichen:
    :ivar auswahl_ausstellende_behoerde: Wer hat den Schuldtitel
        ausgestellt / erlassen?
    :ivar titeldatum: Wann wurde der Schuldtitel ausgestellt / erlassen?
    :ivar zustelldatum: Wann wurde der Schuldtitel zugestellt?
    :ivar rechtsnachfolgedatum: Enthält der Schuldtitel eine
        Rechtsnachfolgeklausel, wenn ja, von wann?
    :ivar rechtsnachfolgezustelldatum: Wann wurde der Schuldtitel mit
        Rechtsnachfolgeklausel zugestellt?
    """

    class Meta:
        name = "Type.GVZ.Schuldtitel"

    titelart: Optional[CodeGvzTitelart] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    titelbezeichnung: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
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
    auswahl_ausstellende_behoerde: Optional[
        "TypeGvzSchuldtitel.AuswahlAusstellendeBehoerde"
    ] = field(
        default=None,
        metadata={
            "name": "auswahl_ausstellendeBehoerde",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    titeldatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    zustelldatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )
    rechtsnachfolgedatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )
    rechtsnachfolgezustelldatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )

    @dataclass
    class AuswahlAusstellendeBehoerde:
        gericht: Optional[CodeGdsGerichteTyp3] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )
        sonstige: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "pattern": r"([ -~]|[¡-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
            },
        )


@dataclass
class NachrichtGvzUebernahmebestaetigung2500002:
    class Meta:
        name = "nachricht.gvz.uebernahmebestaetigung.2500002"
        namespace = "http://www.xjustiz.de"

    nachrichtenkopf: Optional[TypeGdsNachrichtenkopf] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    fachdaten: Optional[
        "NachrichtGvzUebernahmebestaetigung2500002.Fachdaten"
    ] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )

    @dataclass
    class Fachdaten:
        """
        :ivar uebernahmebestaetigung: Für jede Sonderakte eine
            Übernahmebestätigung
        """

        uebernahmebestaetigung: list[
            "NachrichtGvzUebernahmebestaetigung2500002.Fachdaten.Uebernahmebestaetigung"
        ] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            },
        )

        @dataclass
        class Uebernahmebestaetigung:
            az_abgebender_gv: Optional[
                "NachrichtGvzUebernahmebestaetigung2500002.Fachdaten.Uebernahmebestaetigung.AzAbgebenderGv"
            ] = field(
                default=None,
                metadata={
                    "name": "az.abgebenderGV",
                    "type": "Element",
                    "required": True,
                },
            )
            az_uebernehmender_gv: Optional[
                "NachrichtGvzUebernahmebestaetigung2500002.Fachdaten.Uebernahmebestaetigung.AzUebernehmenderGv"
            ] = field(
                default=None,
                metadata={
                    "name": "az.uebernehmenderGV",
                    "type": "Element",
                    "required": True,
                },
            )

            @dataclass
            class AzAbgebenderGv:
                """
                :ivar dr_nummer: Bisherige DR-Nummer
                :ivar dr_jahrgang:
                :ivar dr_register:
                """

                dr_nummer: Optional[int] = field(
                    default=None,
                    metadata={
                        "name": "dr.nummer",
                        "type": "Element",
                        "required": True,
                    },
                )
                dr_jahrgang: Optional[int] = field(
                    default=None,
                    metadata={
                        "name": "dr.jahrgang",
                        "type": "Element",
                        "required": True,
                    },
                )
                dr_register: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "dr.register",
                        "type": "Element",
                        "required": True,
                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                    },
                )

            @dataclass
            class AzUebernehmenderGv:
                """
                :ivar dr_nummer: Neue DR-Nummer
                :ivar dr_jahrgang:
                :ivar dr_register:
                """

                dr_nummer: Optional[int] = field(
                    default=None,
                    metadata={
                        "name": "dr.nummer",
                        "type": "Element",
                        "required": True,
                    },
                )
                dr_jahrgang: Optional[int] = field(
                    default=None,
                    metadata={
                        "name": "dr.jahrgang",
                        "type": "Element",
                        "required": True,
                    },
                )
                dr_register: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "dr.register",
                        "type": "Element",
                        "required": True,
                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                    },
                )


@dataclass
class TypeGvzSonderakte:
    """
    :ivar dr_nummer: Die lfd. Nummer aus dem Dienstregister der
        exportierten Sonderakte - ohne Jahreszahl
    :ivar dr_jahrgang: Der Jahrgang der exportierten Sonderakte -
        vierstellig - z.B. 2020
    :ivar dr_register: Das Register der exportierten Sonderakte:
        1=Dienstregister I 2=Dienstregister II
    :ivar eingangsdatum: Eingangsdatum der exportierten Sonderakte
    :ivar bemerkung: Allgemeine Bemerkung zur Akte
    :ivar auftrag:
    :ivar ref_rollennummer: In jeder Sonderakte werden mindestens zwei
        Beteiligte (Gläubiger, Schuldner) über ihre Rollennummer
        referenziert.
    :ivar schuldtitel:
    :ivar forderung:
    """

    class Meta:
        name = "Type.GVZ.Sonderakte"

    dr_nummer: Optional[int] = field(
        default=None,
        metadata={
            "name": "dr.nummer",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    dr_jahrgang: Optional[int] = field(
        default=None,
        metadata={
            "name": "dr.jahrgang",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    dr_register: Optional[int] = field(
        default=None,
        metadata={
            "name": "dr.register",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    eingangsdatum: Optional[XmlDate] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    bemerkung: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )
    auftrag: Optional["TypeGvzSonderakte.Auftrag"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    ref_rollennummer: list[TypeGdsRefRollennummer] = field(
        default_factory=list,
        metadata={
            "name": "ref.rollennummer",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "min_occurs": 2,
        },
    )
    schuldtitel: list[TypeGvzSchuldtitel] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "min_occurs": 1,
        },
    )
    forderung: Optional[TypeGvzForderung] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )

    @dataclass
    class Auftrag:
        auftragsart: list["TypeGvzSonderakte.Auftrag.Auftragsart"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "min_occurs": 1,
            },
        )

        @dataclass
        class Auftragsart:
            """
            :ivar auftragsart_code: Hier werden die Gläubigeranträge
                (Auftragsarten) übergeben, die innerhalb eines Auftrages
                gestellt sind.
            :ivar auftragsart_datum: Datum ab wann die jeweilige
                Auftragsart statistisch gezählt wird.
            """

            auftragsart_code: Optional[CodeGvzAuftragsart] = field(
                default=None,
                metadata={
                    "name": "auftragsart.code",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )
            auftragsart_datum: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "auftragsart.datum",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )


@dataclass
class NachrichtGvzDatenaustausch2500001:
    """
    :ivar nachrichtenkopf:
    :ivar grunddaten:
    :ivar schriftgutobjekte: Dieses Element wird nur für die
        Kommunikation mit der elektronischen Aktenablage für
        Gerichtsvollzieher verwendet.
    :ivar fachdaten:
    """

    class Meta:
        name = "nachricht.gvz.datenaustausch.2500001"
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
    fachdaten: Optional["NachrichtGvzDatenaustausch2500001.Fachdaten"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )

    @dataclass
    class Fachdaten:
        sonderakte: list[TypeGvzSonderakte] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            },
        )
