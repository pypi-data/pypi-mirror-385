from dataclasses import dataclass, field
from typing import Optional

from xsdata.models.datatype import XmlDate, XmlTime

from xjustiz.model_gen.xjustiz_0000_grunddatensatz_3_5 import (
    TypeGdsAktenzeichen,
    TypeGdsBeurkundung,
    TypeGdsGeldbetrag,
    TypeGdsGrunddaten,
    TypeGdsNachrichtenkopf,
    TypeGdsOrganisation,
    TypeGdsRefRollennummer,
    TypeGdsRefSgo,
    TypeGdsSchriftgutobjekte,
)
from xjustiz.model_gen.xjustiz_0010_cl_allgemein_3_6 import (
    CodeGdsEreignisTyp3,
    CodeGdsSprachen,
)
from xjustiz.model_gen.xjustiz_0020_cl_gerichte_3_3 import CodeGdsGerichteTyp3
from xjustiz.model_gen.xjustiz_0410_cl_register_3_1 import (
    CodeRegDokumentstatusTyp3,
    CodeRegEintragungstypTyp3,
    CodeRegRegisterzeichenwechselgrundTyp3,
    CodeRegStatusRechtstraegerTyp3,
    CodeRegVertragsartTyp3,
)
from xjustiz.model_gen.xjustiz_0420_cl_vertretung_register_3_0 import (
    CodeRegAllgemeineBefreiungTyp3,
    CodeRegAllgemeineVertretungsregelungTyp3,
    CodeRegBesondereBefreiungTyp3,
    CodeRegBesondereVertretungsregelungTyp3,
    CodeRegSachlicheErweiterungProkuraTyp3,
)

__NAMESPACE__ = "http://www.xjustiz.de"


@dataclass
class NachrichtReg0400003:
    """Der Erweiterungsmechanismus für die Facherweiterungen des Grundmoduls sieht
    die Extension des im Grundmodul definierten Schemas (mit Type.GDS.Grunddaten)
    durch die jeweiligen fachspezifischen Erweiterungen als Sequenz vor.

    Zur Anwendung im Instanzdokument muss im Instanzdokument das Schema
    des Fachmoduls referenziert werden. Ein XML-Parser kann durch die
    "include"-Referenz auf das Grundmodul den gesamten Schemabaum
    aufbauen und validieren.

    :ivar nachrichtenkopf:
    :ivar grunddaten:
    :ivar schriftgutobjekte:
    :ivar fachdaten_register: Dieses Element enthält die Daten eines
        Eintragungsantrags bzw. einer Eintragungsnachricht für genau
        einen Rechtsträger. Zu welchem Zweck die Daten übermittelt
        werden, ergibt sich aus dem Element Mitteilungsart. Wenn ein
        Antrag mehrere Mitteilungsarten betrifft (z.B. Löschung eines
        Geschäftsführers und Eintragung eines neuen Geschäftsführers)
        oder wenn Anträge für mehrere Rechtsträger zusammen übermittelt
        werden sollen, ist für jeden Rechtsträger und für jede
        Mitteilungsart jeweils ein separates Element Fachdaten_Register
        zu verwenden. Das Attribut maxOccurs ist deshalb als "unbounded"
        definiert.
    """

    class Meta:
        name = "nachricht.reg.0400003"
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
    fachdaten_register: list["NachrichtReg0400003.FachdatenRegister"] = field(
        default_factory=list,
        metadata={
            "name": "fachdatenRegister",
            "type": "Element",
        },
    )

    @dataclass
    class FachdatenRegister:
        """
        :ivar mitteilungsart: Dieses Element zeigt an, zu welchem Zweck
            die nachfolgenden Daten übermittelt werden. Zulässige Werte
            sind definiert in der Codeliste Ereignis
        :ivar betroffener_rechtstraeger: Dieses Element enthält einen
            Verweis auf die Rollennummer eines Beteiligten, der im
            Grunddatensatz in der Liste der Beteiligten aufgeführt ist.
        :ivar auszug: Zusätzliche Angaben zu einem Registerauszug.
        :ivar basisdaten_register: Für die Auflistung der Beteiligten
            werden die Strukturen des Grunddatensatzes verwendet.
        :ivar auswahl_zusatzangaben:
        :ivar dokumentangaben: Hier sind zusätzliche Angaben zu einem in
            den Sendungsdaten angegebenem Dokument.
        :ivar datum_der_wirksamkeit: Effective_Date
        :ivar adresse_endempfaenger_handelsregister: ausländische
            Registerbehörde
        :ivar auswahl_art_zweigniederlassung:
        :ivar auswahl_vertragsart:
        :ivar fachdaten_register_version: Dieses Attribut wird
            verwendet, um sicherzustellen, dass jedes Instanzdokument
            gegen die "richtige" Version des XML-Schemas geprüft wird.
            Angegeben werden hier nur die beiden ersten Stellen der
            Versionsnummer. Dies ermöglicht es, an einzelnen Dateien
            Fehlerbereinigungen und dergleichen vorzunehmen, ohne dass
            die anderen Bestandteile von XJustiz geändert werden müssen.
        """

        mitteilungsart: Optional[CodeGdsEreignisTyp3] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
            },
        )
        betroffener_rechtstraeger: Optional[TypeGdsRefRollennummer] = field(
            default=None,
            metadata={
                "name": "betroffenerRechtstraeger",
                "type": "Element",
                "required": True,
            },
        )
        auszug: Optional["NachrichtReg0400003.FachdatenRegister.Auszug"] = (
            field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
        )
        basisdaten_register: Optional[
            "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister"
        ] = field(
            default=None,
            metadata={
                "name": "basisdatenRegister",
                "type": "Element",
                "required": True,
            },
        )
        auswahl_zusatzangaben: Optional[
            "NachrichtReg0400003.FachdatenRegister.AuswahlZusatzangaben"
        ] = field(
            default=None,
            metadata={
                "type": "Element",
            },
        )
        dokumentangaben: list[
            "NachrichtReg0400003.FachdatenRegister.Dokumentangaben"
        ] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )
        datum_der_wirksamkeit: Optional[str] = field(
            default=None,
            metadata={
                "name": "datumDerWirksamkeit",
                "type": "Element",
                "pattern": r"\d{4}((-\d{2}){0,1}-\d{2}){0,1}",
            },
        )
        adresse_endempfaenger_handelsregister: Optional[str] = field(
            default=None,
            metadata={
                "name": "adresseEndempfaengerHandelsregister",
                "type": "Element",
                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
            },
        )
        auswahl_art_zweigniederlassung: list[
            "NachrichtReg0400003.FachdatenRegister.AuswahlArtZweigniederlassung"
        ] = field(
            default_factory=list,
            metadata={
                "name": "auswahl_artZweigniederlassung",
                "type": "Element",
            },
        )
        auswahl_vertragsart: Optional[
            "NachrichtReg0400003.FachdatenRegister.AuswahlVertragsart"
        ] = field(
            default=None,
            metadata={
                "type": "Element",
            },
        )
        fachdaten_register_version: str = field(
            init=False,
            default="3.4",
            metadata={
                "name": "fachdatenRegisterVersion",
                "type": "Attribute",
                "required": True,
                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
            },
        )

        @dataclass
        class Auszug:
            """
            :ivar eintragungstext: Hier können besondere
                Eintragungstexte übermittelt werden, deren Inhalt sich
                mit den übrigen Elementen dieses Fachmoduls nicht
                darstellen lässt.
            :ivar abrufuhrzeit: Hier ist die Uhrzeit des Datenabrufs
                anzugeben.
            :ivar abrufdatum: Hier ist das Datum des Datenabrufs
                anzugeben.
            :ivar letzte_eintragung: Hier ist das Datum der letzten
                Eintragung anzugeben.
            :ivar anzahl_eintragungen: Die Anzahl der bisherigen
                Eintragungen sind hier anzugeben.
            :ivar letzte_aenderung:
            :ivar ref_rollennummer:
            """

            eintragungstext: list[
                "NachrichtReg0400003.FachdatenRegister.Auszug.Eintragungstext"
            ] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            abrufuhrzeit: Optional[XmlTime] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "required": True,
                },
            )
            abrufdatum: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "required": True,
                },
            )
            letzte_eintragung: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "letzteEintragung",
                    "type": "Element",
                    "required": True,
                },
            )
            anzahl_eintragungen: Optional[int] = field(
                default=None,
                metadata={
                    "name": "anzahlEintragungen",
                    "type": "Element",
                    "required": True,
                },
            )
            letzte_aenderung: Optional[
                "NachrichtReg0400003.FachdatenRegister.Auszug.LetzteAenderung"
            ] = field(
                default=None,
                metadata={
                    "name": "letzteAenderung",
                    "type": "Element",
                },
            )
            ref_rollennummer: Optional[TypeGdsRefRollennummer] = field(
                default=None,
                metadata={
                    "name": "ref.rollennummer",
                    "type": "Element",
                },
            )

            @dataclass
            class Eintragungstext:
                """
                :ivar spalte: Hier wird die Spalte angegeben, in der der
                    Eintragungstext steht bzw. eingetragen werden soll.
                :ivar position:
                :ivar laufende_nummer:
                :ivar eintragungsart:
                :ivar text: Hier wird der in der angegebenen Spalte
                    enthaltene bzw. einzutragende Text mitgeteilt.
                """

                spalte: Optional[int] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "required": True,
                    },
                )
                position: Optional[int] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "required": True,
                    },
                )
                laufende_nummer: Optional[int] = field(
                    default=None,
                    metadata={
                        "name": "laufendeNummer",
                        "type": "Element",
                        "required": True,
                    },
                )
                eintragungsart: Optional[CodeRegEintragungstypTyp3] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "required": True,
                    },
                )
                text: Optional[str] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "required": True,
                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                    },
                )

            @dataclass
            class LetzteAenderung:
                """
                :ivar aenderungsdatum: Die letzte Änderung des
                    Gesellschaftsvertrages im Datumsformat.
                :ivar aenderungsdatum_freitext:
                """

                aenderungsdatum: Optional[XmlDate] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                    },
                )
                aenderungsdatum_freitext: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "aenderungsdatumFreitext",
                        "type": "Element",
                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                    },
                )

        @dataclass
        class BasisdatenRegister:
            """
            :ivar gruendungsmetadaten: Dieses Element enthält Angaben
                zur Gründung des Rechtsträgers
            :ivar satzungsdatum:
            :ivar urkundsdaten: Hier können Daten zu der Urkunde
                angegeben werden, mit der der Rechtsträger gegründet
                worden ist.
            :ivar rechtstraeger: Diese Daten betreffen den vom
                Eintragungsantrag betroffenen Rechtsträger
                (Gesellschaft, Genossenschaft, Verein usw.). Dieses
                Element ist nur dann zu übermitteln, wenn geänderte
                Daten zum Rechtsträger in das Register eingetragen
                werden sollen. Die vollständigen Angaben zum
                Rechtsträger werden in den Grunddaten übermittelt.
            :ivar vertretung:
            :ivar gegenstand: Hier wird der Gegenstand des Rechtsträgers
                angegeben.
            :ivar geschaeftszweck: Hier wird der Geschäftszweck des
                Rechtsträgers angegeben.
            :ivar status_rechtstraeger:
            :ivar historie_rechtstraeger:
            :ivar empfangsberechtigte:
            :ivar unternehmensteile:
            :ivar sonstige_registerbeteiligte:
            """

            gruendungsmetadaten: Optional[
                "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.Gruendungsmetadaten"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            satzungsdatum: Optional[
                "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.Satzungsdatum"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            urkundsdaten: Optional[TypeGdsBeurkundung] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            rechtstraeger: Optional[TypeGdsOrganisation] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            vertretung: Optional[
                "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.Vertretung"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            gegenstand: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            geschaeftszweck: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            status_rechtstraeger: Optional[CodeRegStatusRechtstraegerTyp3] = (
                field(
                    default=None,
                    metadata={
                        "name": "statusRechtstraeger",
                        "type": "Element",
                    },
                )
            )
            historie_rechtstraeger: Optional[
                "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.HistorieRechtstraeger"
            ] = field(
                default=None,
                metadata={
                    "name": "historieRechtstraeger",
                    "type": "Element",
                },
            )
            empfangsberechtigte: list[TypeGdsRefRollennummer] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            unternehmensteile: list[TypeGdsRefRollennummer] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            sonstige_registerbeteiligte: list[TypeGdsRefRollennummer] = field(
                default_factory=list,
                metadata={
                    "name": "sonstigeRegisterbeteiligte",
                    "type": "Element",
                },
            )

            @dataclass
            class Gruendungsmetadaten:
                """
                :ivar urkundsperson: Dieses Element enthält einen
                    Verweis auf die Rollennummer eines Beteiligten, der
                    im Grunddatensatz in der Liste der Beteiligten
                    aufgeführt ist.
                :ivar gruendungsdatum:
                """

                urkundsperson: Optional[TypeGdsRefRollennummer] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                    },
                )
                gruendungsdatum: Optional[XmlDate] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "required": True,
                    },
                )

            @dataclass
            class Satzungsdatum:
                """
                :ivar aktuelles_satzungsdatum: Hier kann das Datum der
                    derzeit gültigen Fassung der Satzung oder des
                    Gesellschaftsvertrages angegeben werden.
                :ivar satzungsdatum_freitext:
                """

                aktuelles_satzungsdatum: Optional[XmlDate] = field(
                    default=None,
                    metadata={
                        "name": "aktuellesSatzungsdatum",
                        "type": "Element",
                    },
                )
                satzungsdatum_freitext: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "satzungsdatumFreitext",
                        "type": "Element",
                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                    },
                )

            @dataclass
            class Vertretung:
                """
                :ivar allgemeine_vertretungsregelung: Hier können
                    Regelungen übermittelt werden, die für alle
                    Vertreter gleichermaßen gelten
                :ivar vertretungsberechtigte: Dieses Element enthält
                    einen Verweis auf die Rollennummer eines
                    Beteiligten, der im Grunddatensatz in der Liste der
                    Beteiligten aufgeführt ist und zur individuellen
                    Ausgestaltung von deren Vertretungsmacht übermittelt
                    werden soll.
                """

                allgemeine_vertretungsregelung: Optional[
                    "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.Vertretung.AllgemeineVertretungsregelung"
                ] = field(
                    default=None,
                    metadata={
                        "name": "allgemeineVertretungsregelung",
                        "type": "Element",
                    },
                )
                vertretungsberechtigte: list[
                    "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.Vertretung.Vertretungsberechtigte"
                ] = field(
                    default_factory=list,
                    metadata={
                        "type": "Element",
                    },
                )

                @dataclass
                class AllgemeineVertretungsregelung:
                    """
                    :ivar auswahl_vertretungsbefugnis:
                    :ivar auswahl_befreiung_von181_bgb: Dieses Element
                        wird benötigt, wenn der Vertreter von den
                        Beschränkungen des § 181 BGB befreit ist.
                    """

                    auswahl_vertretungsbefugnis: Optional[
                        "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.Vertretung.AllgemeineVertretungsregelung.AuswahlVertretungsbefugnis"
                    ] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        },
                    )
                    auswahl_befreiung_von181_bgb: Optional[
                        "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.Vertretung.AllgemeineVertretungsregelung.AuswahlBefreiungVon181Bgb"
                    ] = field(
                        default=None,
                        metadata={
                            "name": "auswahl_befreiungVon181BGB",
                            "type": "Element",
                        },
                    )

                    @dataclass
                    class AuswahlVertretungsbefugnis:
                        """
                        :ivar vertretungsbefugnis: Zulässige Werte für
                            dieses Element sind in der Codeliste
                            definiert.
                        :ivar vertretungsbefugnis_freitext:
                        """

                        vertretungsbefugnis: Optional[
                            CodeRegAllgemeineVertretungsregelungTyp3
                        ] = field(
                            default=None,
                            metadata={
                                "type": "Element",
                            },
                        )
                        vertretungsbefugnis_freitext: Optional[str] = field(
                            default=None,
                            metadata={
                                "name": "vertretungsbefugnisFreitext",
                                "type": "Element",
                                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                            },
                        )

                    @dataclass
                    class AuswahlBefreiungVon181Bgb:
                        befreiung_von181_bgb: Optional[
                            CodeRegAllgemeineBefreiungTyp3
                        ] = field(
                            default=None,
                            metadata={
                                "name": "befreiungVon181BGB",
                                "type": "Element",
                            },
                        )
                        befreiung_von181_bgbfreitext: Optional[str] = field(
                            default=None,
                            metadata={
                                "name": "befreiungVon181BGBFreitext",
                                "type": "Element",
                                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                            },
                        )

                @dataclass
                class Vertretungsberechtigte(TypeGdsRefRollennummer):
                    besondere_vertretungsregelung: list[
                        "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.Vertretung.Vertretungsberechtigte.BesondereVertretungsregelung"
                    ] = field(
                        default_factory=list,
                        metadata={
                            "name": "besondereVertretungsregelung",
                            "type": "Element",
                        },
                    )

                    @dataclass
                    class BesondereVertretungsregelung:
                        """
                        :ivar auswahl_vertretungsbefugnis:
                        :ivar auswahl_befreiung_von181_bgb: Dieses
                            Element wird benötigt, wenn der Vertreter
                            von den Beschränkungen des § 181 BGB befreit
                            ist.
                        :ivar oertliche_beschraenkung: Für dieses
                            Element ist keine Codeliste definiert. Es
                            kann bei Bedarf mit Freitext gefüllt werden.
                            Beispiel: Prokura beschränkt auf eine
                            bestimmte Zweigniederlassung)
                        :ivar prokura:
                        """

                        auswahl_vertretungsbefugnis: Optional[
                            "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.Vertretung.Vertretungsberechtigte.BesondereVertretungsregelung.AuswahlVertretungsbefugnis"
                        ] = field(
                            default=None,
                            metadata={
                                "type": "Element",
                            },
                        )
                        auswahl_befreiung_von181_bgb: Optional[
                            "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.Vertretung.Vertretungsberechtigte.BesondereVertretungsregelung.AuswahlBefreiungVon181Bgb"
                        ] = field(
                            default=None,
                            metadata={
                                "name": "auswahl_befreiungVon181BGB",
                                "type": "Element",
                            },
                        )
                        oertliche_beschraenkung: Optional[str] = field(
                            default=None,
                            metadata={
                                "name": "oertlicheBeschraenkung",
                                "type": "Element",
                                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                            },
                        )
                        prokura: Optional[
                            "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.Vertretung.Vertretungsberechtigte.BesondereVertretungsregelung.Prokura"
                        ] = field(
                            default=None,
                            metadata={
                                "type": "Element",
                            },
                        )

                        @dataclass
                        class AuswahlVertretungsbefugnis:
                            """
                            :ivar vertretungsbefugnis: Zulässige Werte
                                für dieses Element sind in der Codeliste
                                definiert.
                            :ivar vertretungsbefugnis_freitext:
                            """

                            vertretungsbefugnis: Optional[
                                CodeRegBesondereVertretungsregelungTyp3
                            ] = field(
                                default=None,
                                metadata={
                                    "type": "Element",
                                },
                            )
                            vertretungsbefugnis_freitext: Optional[str] = (
                                field(
                                    default=None,
                                    metadata={
                                        "name": "vertretungsbefugnisFreitext",
                                        "type": "Element",
                                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                                    },
                                )
                            )

                        @dataclass
                        class AuswahlBefreiungVon181Bgb:
                            befreiung_von181_bgb: Optional[
                                CodeRegBesondereBefreiungTyp3
                            ] = field(
                                default=None,
                                metadata={
                                    "name": "befreiungVon181BGB",
                                    "type": "Element",
                                },
                            )
                            befreiung_von181_bgbfreitext: Optional[str] = (
                                field(
                                    default=None,
                                    metadata={
                                        "name": "befreiungVon181BGBFreitext",
                                        "type": "Element",
                                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                                    },
                                )
                            )

                        @dataclass
                        class Prokura:
                            auswahl_sachliche_erweiterung_prokura: Optional[
                                "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.Vertretung.Vertretungsberechtigte.BesondereVertretungsregelung.Prokura.AuswahlSachlicheErweiterungProkura"
                            ] = field(
                                default=None,
                                metadata={
                                    "name": "auswahl_sachlicheErweiterungProkura",
                                    "type": "Element",
                                },
                            )

                            @dataclass
                            class AuswahlSachlicheErweiterungProkura:
                                """
                                :ivar sachliche_erweiterung_prokura:
                                    Zulässige Werte für dieses Element
                                    sind in der Codeliste definiert.
                                :ivar
                                    sachliche_erweiterung_prokura_freitext:
                                """

                                sachliche_erweiterung_prokura: Optional[
                                    CodeRegSachlicheErweiterungProkuraTyp3
                                ] = field(
                                    default=None,
                                    metadata={
                                        "name": "sachlicheErweiterungProkura",
                                        "type": "Element",
                                    },
                                )
                                sachliche_erweiterung_prokura_freitext: Optional[
                                    str
                                ] = field(
                                    default=None,
                                    metadata={
                                        "name": "sachlicheErweiterungProkuraFreitext",
                                        "type": "Element",
                                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                                    },
                                )

            @dataclass
            class HistorieRechtstraeger:
                """
                :ivar bisher: Angaben zu einem Rechtsträger, aus dem der
                    betroffene Rechtsträger hervorgegangen ist (quasi
                    ein Vorgänger). Bei einer Verschmelzung können
                    mehrere Vorgänger existieren.
                :ivar nunmehr: Angaben zu einem Rechtsträger, in den der
                    betroffene Rechtsträger überführt wurde (quasi ein
                    Nachfolger). Bei einer Spaltung können mehrere
                    Nachfolger existieren.
                """

                bisher: list[
                    "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.HistorieRechtstraeger.Bisher"
                ] = field(
                    default_factory=list,
                    metadata={
                        "type": "Element",
                    },
                )
                nunmehr: list[
                    "NachrichtReg0400003.FachdatenRegister.BasisdatenRegister.HistorieRechtstraeger.Nunmehr"
                ] = field(
                    default_factory=list,
                    metadata={
                        "type": "Element",
                    },
                )

                @dataclass
                class Bisher:
                    """
                    :ivar ref_rechtstraeger:
                    :ivar wechselgrund: Grund für den vollzogenen
                        Registerzeichenwechsel. Zulässige Werte für
                        dieses Element sind in der hinterlegten
                        Codeliste definiert.
                    """

                    ref_rechtstraeger: Optional[TypeGdsRefRollennummer] = (
                        field(
                            default=None,
                            metadata={
                                "name": "ref.rechtstraeger",
                                "type": "Element",
                                "required": True,
                            },
                        )
                    )
                    wechselgrund: Optional[
                        CodeRegRegisterzeichenwechselgrundTyp3
                    ] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                            "required": True,
                        },
                    )

                @dataclass
                class Nunmehr:
                    """
                    :ivar ref_rechtstraeger:
                    :ivar wechselgrund: Grund für den vollzogenen
                        Registerzeichenwechsel. Zulässige Werte für
                        dieses Element sind in der hinterlegten
                        Codeliste definiert.
                    """

                    ref_rechtstraeger: Optional[TypeGdsRefRollennummer] = (
                        field(
                            default=None,
                            metadata={
                                "name": "ref.rechtstraeger",
                                "type": "Element",
                                "required": True,
                            },
                        )
                    )
                    wechselgrund: Optional[
                        CodeRegRegisterzeichenwechselgrundTyp3
                    ] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                            "required": True,
                        },
                    )

        @dataclass
        class AuswahlZusatzangaben:
            kapitalgesellschaft: Optional[
                "NachrichtReg0400003.FachdatenRegister.AuswahlZusatzangaben.Kapitalgesellschaft"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            personengesellschaft: Optional[
                "NachrichtReg0400003.FachdatenRegister.AuswahlZusatzangaben.Personengesellschaft"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            genossenschaft: Optional[
                "NachrichtReg0400003.FachdatenRegister.AuswahlZusatzangaben.Genossenschaft"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )

            @dataclass
            class Kapitalgesellschaft:
                """
                :ivar zusatz_aktiengesellschaft: Aufsichtsrat und
                    Gründer werden über die Angaben im Grunddatensatz
                    und in der ergänzenden Codeliste abgedeckt.
                :ivar zusatz_gmb_h:
                :ivar dauer_des_rechtstraegers:
                :ivar sacheinlage:
                """

                zusatz_aktiengesellschaft: Optional[
                    "NachrichtReg0400003.FachdatenRegister.AuswahlZusatzangaben.Kapitalgesellschaft.ZusatzAktiengesellschaft"
                ] = field(
                    default=None,
                    metadata={
                        "name": "zusatzAktiengesellschaft",
                        "type": "Element",
                    },
                )
                zusatz_gmb_h: Optional[
                    "NachrichtReg0400003.FachdatenRegister.AuswahlZusatzangaben.Kapitalgesellschaft.ZusatzGmbH"
                ] = field(
                    default=None,
                    metadata={
                        "name": "zusatzGmbH",
                        "type": "Element",
                    },
                )
                dauer_des_rechtstraegers: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "dauerDesRechtstraegers",
                        "type": "Element",
                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                    },
                )
                sacheinlage: list[
                    "NachrichtReg0400003.FachdatenRegister.AuswahlZusatzangaben.Kapitalgesellschaft.Sacheinlage"
                ] = field(
                    default_factory=list,
                    metadata={
                        "type": "Element",
                    },
                )

                @dataclass
                class ZusatzAktiengesellschaft:
                    grundkapital: list[
                        "NachrichtReg0400003.FachdatenRegister.AuswahlZusatzangaben.Kapitalgesellschaft.ZusatzAktiengesellschaft.Grundkapital"
                    ] = field(
                        default_factory=list,
                        metadata={
                            "type": "Element",
                        },
                    )

                    @dataclass
                    class Grundkapital:
                        """
                        :ivar hoehe: Hier kann die Höhe des
                            Grundkapitals angegeben werden
                        :ivar zusatz: Hier ist Raum für ergänzende
                            Angaben (als Freitext)
                        """

                        hoehe: Optional[TypeGdsGeldbetrag] = field(
                            default=None,
                            metadata={
                                "type": "Element",
                            },
                        )
                        zusatz: Optional[str] = field(
                            default=None,
                            metadata={
                                "type": "Element",
                                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                            },
                        )

                @dataclass
                class ZusatzGmbH:
                    stammkapital: list[TypeGdsGeldbetrag] = field(
                        default_factory=list,
                        metadata={
                            "type": "Element",
                        },
                    )
                    stammeinlage: list[
                        "NachrichtReg0400003.FachdatenRegister.AuswahlZusatzangaben.Kapitalgesellschaft.ZusatzGmbH.Stammeinlage"
                    ] = field(
                        default_factory=list,
                        metadata={
                            "type": "Element",
                        },
                    )

                    @dataclass
                    class Stammeinlage:
                        """
                        :ivar einlage:
                        :ivar beteiligter: Hier wird verwiesen auf die
                            Rollennummer eines Beteiligten, der in der
                            bei den Grunddaten enthaltenen Liste der
                            Beteiligten aufgeführt ist.
                        """

                        einlage: Optional[TypeGdsGeldbetrag] = field(
                            default=None,
                            metadata={
                                "type": "Element",
                                "required": True,
                            },
                        )
                        beteiligter: Optional[TypeGdsRefRollennummer] = field(
                            default=None,
                            metadata={
                                "type": "Element",
                                "required": True,
                            },
                        )

                @dataclass
                class Sacheinlage:
                    """
                    :ivar eingebrachtes_wirtschaftsgut:
                    :ivar zeitwert:
                    :ivar anschaffungspreis_ohne_ust:
                    :ivar anschaffungsdatum:
                    :ivar anrechnungswert:
                    :ivar beteiligter: Dieses Element enthält einen
                        Verweis auf einen Beteiligten, der in den
                        Grunddaten in der Liste der Beteiligten
                        aufgeführt ist.
                    """

                    eingebrachtes_wirtschaftsgut: Optional[str] = field(
                        default=None,
                        metadata={
                            "name": "eingebrachtesWirtschaftsgut",
                            "type": "Element",
                            "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                        },
                    )
                    zeitwert: Optional[TypeGdsGeldbetrag] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        },
                    )
                    anschaffungspreis_ohne_ust: Optional[TypeGdsGeldbetrag] = (
                        field(
                            default=None,
                            metadata={
                                "name": "anschaffungspreisOhneUST",
                                "type": "Element",
                            },
                        )
                    )
                    anschaffungsdatum: Optional[XmlDate] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                        },
                    )
                    anrechnungswert: Optional[TypeGdsGeldbetrag] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                            "required": True,
                        },
                    )
                    beteiligter: Optional[TypeGdsRefRollennummer] = field(
                        default=None,
                        metadata={
                            "type": "Element",
                            "required": True,
                        },
                    )

            @dataclass
            class Personengesellschaft:
                zusatz_kg: Optional[
                    "NachrichtReg0400003.FachdatenRegister.AuswahlZusatzangaben.Personengesellschaft.ZusatzKg"
                ] = field(
                    default=None,
                    metadata={
                        "name": "zusatzKG",
                        "type": "Element",
                    },
                )
                zusatz_ewiv: Optional[
                    "NachrichtReg0400003.FachdatenRegister.AuswahlZusatzangaben.Personengesellschaft.ZusatzEwiv"
                ] = field(
                    default=None,
                    metadata={
                        "name": "zusatzEWIV",
                        "type": "Element",
                    },
                )

                @dataclass
                class ZusatzKg:
                    """
                    :ivar daten_kommanditist: Dieses Element enthält
                        einen Verweis auf einen Beteiligten, der in den
                        Grunddaten in der Liste der Beteiligten
                        aufgeführt ist.
                    """

                    daten_kommanditist: list[
                        "NachrichtReg0400003.FachdatenRegister.AuswahlZusatzangaben.Personengesellschaft.ZusatzKg.DatenKommanditist"
                    ] = field(
                        default_factory=list,
                        metadata={
                            "name": "datenKommanditist",
                            "type": "Element",
                            "min_occurs": 1,
                        },
                    )

                    @dataclass
                    class DatenKommanditist(TypeGdsRefRollennummer):
                        hafteinlage: Optional[TypeGdsGeldbetrag] = field(
                            default=None,
                            metadata={
                                "type": "Element",
                                "required": True,
                            },
                        )

                @dataclass
                class ZusatzEwiv:
                    """
                    :ivar daten_mitglied_ewiv: Dieses Element enthält
                        einen Verweis auf einen Beteiligten, der in den
                        Grunddaten in der Liste der Beteiligten
                        aufgeführt ist.
                    """

                    daten_mitglied_ewiv: list[TypeGdsRefRollennummer] = field(
                        default_factory=list,
                        metadata={
                            "name": "datenMitgliedEWIV",
                            "type": "Element",
                            "min_occurs": 1,
                        },
                    )

            @dataclass
            class Genossenschaft:
                haftsumme_je_geschaeftsanteil: Optional[TypeGdsGeldbetrag] = (
                    field(
                        default=None,
                        metadata={
                            "name": "haftsummeJeGeschaeftsanteil",
                            "type": "Element",
                        },
                    )
                )
                hoechstzahl_der_geschaeftsanteile_je_genosse: Optional[str] = (
                    field(
                        default=None,
                        metadata={
                            "name": "hoechstzahlDerGeschaeftsanteileJeGenosse",
                            "type": "Element",
                            "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                        },
                    )
                )
                nachschusspflicht: Optional[str] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                    },
                )
                mindestkapital: list[TypeGdsGeldbetrag] = field(
                    default_factory=list,
                    metadata={
                        "type": "Element",
                    },
                )
                dauer_des_rechtstraegers: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "dauerDesRechtstraegers",
                        "type": "Element",
                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                    },
                )

        @dataclass
        class Dokumentangaben:
            """
            :ivar ref_dokument_id: Hier wird auf ein Dokument über die
                Dokument_ID dieses Dokuments Bezug genommen.
            :ivar stichtag: Hier wird der Stichtag des Dokuments
                angegeben z.B. Bilanzstichtag oder bei
                Gesellschafterlisten wichtig.
            :ivar sprache:
            :ivar status:
            :ivar gesperrt:
            :ivar freigabedatum:
            :ivar aufnahmedatum: Einstelldatum/Aufnahmedatum in den
                Registerordner
            :ivar hinweis: Hinweistext zum Dokument, der zur Ausgabe in
                der Internet Registerauskunft (Regisportal, RegisWeb)
                vorgesehen ist.
            :ivar vorband: Angaben zum Geschaeftszeichen am Gericht,
                welches das Dokument anfangs im Besitz hatte.
            :ivar aenderungssperre:
            :ivar bemerkung:
            :ivar bezug:
            :ivar doppelstueck:
            :ivar einreicher:
            :ivar erstellt_am:
            :ivar erstellt_zum_stichtag:
            :ivar freigabe_von:
            :ivar freigabe_von_stammakte:
            :ivar freigabe_von_vorband:
            :ivar gegenstand_der_einreichung:
            :ivar loeschungssperre:
            :ivar merkmal_aktuell:
            :ivar sperrkennzeichen:
            :ivar urkunden_nummer:
            :ivar urspruengliches_eingangs_datum:
            :ivar vorgangsnummer:
            :ivar webfreigabe_datum:
            :ivar zustell_datum:
            """

            ref_dokument_id: Optional[TypeGdsRefSgo] = field(
                default=None,
                metadata={
                    "name": "ref.dokumentID",
                    "type": "Element",
                    "required": True,
                },
            )
            stichtag: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            sprache: Optional[CodeGdsSprachen] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            status: Optional[CodeRegDokumentstatusTyp3] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            gesperrt: Optional[bool] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            freigabedatum: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            aufnahmedatum: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            hinweis: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            vorband: Optional[
                "NachrichtReg0400003.FachdatenRegister.Dokumentangaben.Vorband"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            aenderungssperre: Optional[bool] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            bemerkung: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            bezug: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            doppelstueck: Optional[bool] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            einreicher: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "pattern": r"([ -~]|[¡-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            erstellt_am: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "erstelltAm",
                    "type": "Element",
                },
            )
            erstellt_zum_stichtag: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "erstelltZumStichtag",
                    "type": "Element",
                },
            )
            freigabe_von: Optional[str] = field(
                default=None,
                metadata={
                    "name": "freigabeVon",
                    "type": "Element",
                    "pattern": r"( |'|[,-\.]|[A-Z]|[`-z]|~|¨|´|·|[À-Ö]|[Ø-ö]|[ø-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            freigabe_von_stammakte: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "freigabeVonStammakte",
                    "type": "Element",
                },
            )
            freigabe_von_vorband: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "freigabeVonVorband",
                    "type": "Element",
                },
            )
            gegenstand_der_einreichung: Optional[str] = field(
                default=None,
                metadata={
                    "name": "gegenstandDerEinreichung",
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            loeschungssperre: Optional[bool] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            merkmal_aktuell: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "merkmalAktuell",
                    "type": "Element",
                },
            )
            sperrkennzeichen: Optional[bool] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            urkunden_nummer: Optional[str] = field(
                default=None,
                metadata={
                    "name": "urkundenNummer",
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            urspruengliches_eingangs_datum: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "urspruenglichesEingangsDatum",
                    "type": "Element",
                },
            )
            vorgangsnummer: Optional[int] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            webfreigabe_datum: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "webfreigabeDatum",
                    "type": "Element",
                },
            )
            zustell_datum: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "zustellDatum",
                    "type": "Element",
                },
            )

            @dataclass
            class Vorband:
                """
                :ivar gericht: Zur Bezeichnung des Gerichts werden die
                    Gerichtskennzahlen der Codeliste GDS.Gerichte
                    verwendet.
                :ivar geschaeftszeichen: Aktenzeichen im Format:
                    "Registertyp", "Nummer" und optional
                    "Ortskennzeichen", z.B. HRB 12345 Kl
                """

                gericht: Optional[CodeGdsGerichteTyp3] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "required": True,
                    },
                )
                geschaeftszeichen: Optional[TypeGdsAktenzeichen] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "required": True,
                    },
                )

        @dataclass
        class AuswahlArtZweigniederlassung(TypeGdsRefRollennummer):
            gleiche_firma: str = field(
                init=False,
                default="gleiche Firma",
                metadata={
                    "name": "gleicheFirma",
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            gleiche_firma_mit_zusatz: str = field(
                init=False,
                default="gleiche Firma mit Zusatz",
                metadata={
                    "name": "gleicheFirmaMitZusatz",
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            abweichende_firma: str = field(
                init=False,
                default="abweichende Firma",
                metadata={
                    "name": "abweichendeFirma",
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )

        @dataclass
        class AuswahlVertragsart:
            vertragsart: Optional[CodeRegVertragsartTyp3] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            vertragsart_freitext: Optional[str] = field(
                default=None,
                metadata={
                    "name": "vertragsartFreitext",
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
