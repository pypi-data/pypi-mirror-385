from dataclasses import dataclass, field
from typing import Optional

from xjustiz.model_gen.xjustiz_0000_grunddatensatz_3_5 import (
    TypeGdsBasisnachricht,
    TypeGdsGrunddaten,
    TypeGdsNachrichtenkopf,
    TypeGdsSchriftgutobjekte,
)
from xjustiz.model_gen.xjustiz_0010_cl_allgemein_3_6 import (
    CodeFehlerTyp4,
    CodeGdsAuskunftVollstreckungssachenFehlerTyp3,
    CodeGdsFehlercodesTyp3,
    CodeGdsInsoIriFehlercodeTyp3,
    CodeGdsVagFehlerTyp3,
)

__NAMESPACE__ = "http://www.xjustiz.de"


@dataclass
class NachrichtGdsBasisnachricht0005006:
    """
    Diese Nachricht kann für alle Kommunikationsszenarien, bei denen keine
    Schriftgutobjekte übermittelt werden und für die keine spezielle Fachnachricht
    bereitsteht, genutzt werden.
    """

    class Meta:
        name = "nachricht.gds.basisnachricht.0005006"
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
        },
    )


@dataclass
class NachrichtGdsFehler0005007:
    class Meta:
        name = "nachricht.gds.fehler.0005007"
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
        },
    )
    fachdaten: Optional["NachrichtGdsFehler0005007.Fachdaten"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )

    @dataclass
    class Fachdaten:
        fehler: list["NachrichtGdsFehler0005007.Fachdaten.Fehler"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            },
        )

        @dataclass
        class Fehler:
            """
            :ivar auswahl_fehlercode:
            :ivar zusatzinformation: In diesem Element können weitere
                Informationen zum Fehler angegeben werden. Dies kann zum
                Beispiel bei einem Validierungsfehler die Meldung vom
                Parser oder die Fehlerbeschreibung bei Auswahl des
                Wertes "Sonstiger Fehler" sein.
            """

            auswahl_fehlercode: Optional[
                "NachrichtGdsFehler0005007.Fachdaten.Fehler.AuswahlFehlercode"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "required": True,
                },
            )
            zusatzinformation: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )

            @dataclass
            class AuswahlFehlercode:
                """
                :ivar fehlercode: Dieses Element ist zu verwenden, wenn
                    keine fach- oder anwendungsspezifische Codeliste
                    abgestimmt ist.
                :ivar anwendungsspezifischer_fehler: Mit diesem Element
                    kann auf Codelisten zurückgegriffen werden, die für
                    bestimmte IT-Anwendungen abgestimmt wurden, jedoch
                    (noch) nicht in den XJustiz-Standards aufgenommen
                    werden konnten. In diesem Fall muss die Kennung und
                    Version der verwendeten Codeliste bei der
                    Nachrichtenübermittlung angegeben werden. Zudem muss
                    sichergestellt sein, dass der Empfänger Kenntnis von
                    der Codeliste hat und auf sie zugreifen kann.
                :ivar vag_fehler: Zu verwenden für
                    Kommunikationsszenarien des Fachmoduls
                    Versorgungsausgleich.
                :ivar inso_iri_fehler: Zu verwenden für
                    Kommunikationsszenarien des Fachmoduls Insolvenz.
                :ivar auskunft_vollstreckungssachen_fehler:
                    Fehlermeldung für die Kommunikation bei
                    Auskunftsersuchen im Rahmen von
                    Vollstreckungssachen. z.B. für Fachmodule eZoll und
                    ZPO Fremdauskunft
                """

                fehlercode: Optional[CodeGdsFehlercodesTyp3] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                    },
                )
                anwendungsspezifischer_fehler: Optional[CodeFehlerTyp4] = (
                    field(
                        default=None,
                        metadata={
                            "name": "anwendungsspezifischerFehler",
                            "type": "Element",
                        },
                    )
                )
                vag_fehler: Optional[CodeGdsVagFehlerTyp3] = field(
                    default=None,
                    metadata={
                        "name": "vag.fehler",
                        "type": "Element",
                    },
                )
                inso_iri_fehler: Optional[CodeGdsInsoIriFehlercodeTyp3] = (
                    field(
                        default=None,
                        metadata={
                            "name": "inso.iri.fehler",
                            "type": "Element",
                        },
                    )
                )
                auskunft_vollstreckungssachen_fehler: Optional[
                    CodeGdsAuskunftVollstreckungssachenFehlerTyp3
                ] = field(
                    default=None,
                    metadata={
                        "name": "auskunft.vollstreckungssachen.fehler",
                        "type": "Element",
                    },
                )


@dataclass
class NachrichtGdsUebermittlungSchriftgutobjekte0005005(TypeGdsBasisnachricht):
    """
    Diese Nachricht ist eine Erweiterung des Type.GDS.Basisnachricht.
    """

    class Meta:
        name = "nachricht.gds.uebermittlungSchriftgutobjekte.0005005"
        namespace = "http://www.xjustiz.de"

    schriftgutobjekte: Optional[TypeGdsSchriftgutobjekte] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
