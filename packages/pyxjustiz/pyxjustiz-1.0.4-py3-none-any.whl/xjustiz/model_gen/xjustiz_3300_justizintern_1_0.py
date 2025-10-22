from dataclasses import dataclass, field
from typing import Optional

from xsdata.models.datatype import XmlDate

from xjustiz.model_gen.xjustiz_0000_grunddatensatz_3_5 import (
    TypeGdsGrunddaten,
    TypeGdsNachrichtenkopf,
    TypeGdsRefRollennummer,
    TypeGdsSchriftgutobjekte,
)
from xjustiz.model_gen.xjustiz_0010_cl_allgemein_3_6 import (
    CodeGdsEntscheidungsartTyp3,
    CodeGdsFachlicherZusammenhangTyp3,
    CodeGdsRechtsmittelartTyp3,
)

__NAMESPACE__ = "http://www.xjustiz.de"


@dataclass
class NachrichtIntAbgabeInnerhalbDerJustiz3300001:
    class Meta:
        name = "nachricht.int.abgabeInnerhalbDerJustiz.3300001"
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
            "required": True,
        },
    )
    fachdaten: Optional[
        "NachrichtIntAbgabeInnerhalbDerJustiz3300001.Fachdaten"
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
        :ivar einlegung_rechtsmittel:
        :ivar zusammengehoerige_verfahren: Mit diesem Element werden
            fachlich miteinander verbundene Verfahren gekennzeichnet.
        """

        einlegung_rechtsmittel: Optional[
            "NachrichtIntAbgabeInnerhalbDerJustiz3300001.Fachdaten.EinlegungRechtsmittel"
        ] = field(
            default=None,
            metadata={
                "name": "einlegungRechtsmittel",
                "type": "Element",
            },
        )
        zusammengehoerige_verfahren: Optional[
            "NachrichtIntAbgabeInnerhalbDerJustiz3300001.Fachdaten.ZusammengehoerigeVerfahren"
        ] = field(
            default=None,
            metadata={
                "name": "zusammengehoerigeVerfahren",
                "type": "Element",
            },
        )

        @dataclass
        class EinlegungRechtsmittel:
            """
            :ivar entscheidungsart: Hier ist die Art der Entscheidung
                anzugeben, gegen die das Rechtsmittel eingelegt wurde.
            :ivar entscheidungsdatum:
            :ivar rechtsmittelart: Sofern die Art des Rechtsmittels
                bekannt ist, soll der einschlägige Wert in diesem
                Element übergeben werden. Dies ist z.B. der Fall, wenn
                das Rechtsmittel bei dem Gericht, das die Entscheidung
                getroffen hat, eingelegt wird und die Abgabe an das
                Rechtsmittelgericht von dort aus erfolgt.
            :ivar beteiligter: Hier kann auf die Rechtsmittelführer
                referenziert werden.
            """

            entscheidungsart: Optional[CodeGdsEntscheidungsartTyp3] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "required": True,
                },
            )
            entscheidungsdatum: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            rechtsmittelart: Optional[CodeGdsRechtsmittelartTyp3] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            beteiligter: list[TypeGdsRefRollennummer] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )

        @dataclass
        class ZusammengehoerigeVerfahren:
            """
            :ivar hauptverfahren: Bezeichnet das Verfahren, für das ein
                zugehöriges Verfahren in der Sequenz
                "zugehoerigeVerfahren" angegeben wird.
            :ivar zugehoerige_verfahren: Bezeichnet das zugehörige
                Verfahren.
            """

            hauptverfahren: Optional[
                "NachrichtIntAbgabeInnerhalbDerJustiz3300001.Fachdaten.ZusammengehoerigeVerfahren.Hauptverfahren"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "required": True,
                },
            )
            zugehoerige_verfahren: list[
                "NachrichtIntAbgabeInnerhalbDerJustiz3300001.Fachdaten.ZusammengehoerigeVerfahren.ZugehoerigeVerfahren"
            ] = field(
                default_factory=list,
                metadata={
                    "name": "zugehoerigeVerfahren",
                    "type": "Element",
                    "min_occurs": 1,
                },
            )

            @dataclass
            class Hauptverfahren:
                ref_instanznummer: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "ref.instanznummer",
                        "type": "Element",
                        "required": True,
                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                    },
                )

            @dataclass
            class ZugehoerigeVerfahren:
                """
                :ivar ref_instanznummer:
                :ivar fachlicher_zusammenhang: In diesem Element wird
                    die Art des zugehörigen Verfahrens beschrieben.
                """

                ref_instanznummer: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "ref.instanznummer",
                        "type": "Element",
                        "required": True,
                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                    },
                )
                fachlicher_zusammenhang: Optional[
                    CodeGdsFachlicherZusammenhangTyp3
                ] = field(
                    default=None,
                    metadata={
                        "name": "fachlicherZusammenhang",
                        "type": "Element",
                        "required": True,
                    },
                )
