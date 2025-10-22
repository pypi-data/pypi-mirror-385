from dataclasses import dataclass, field
from typing import Optional

from xsdata.models.datatype import XmlDate

from xjustiz.model_gen.xjustiz_0000_grunddatensatz_3_5 import (
    TypeGdsBasisnachricht,
    TypeGdsGeldbetrag,
    TypeGdsGrunddaten,
    TypeGdsNachrichtenkopf,
    TypeGdsRefRollennummer,
    TypeGdsSchriftgutobjekte,
)
from xjustiz.model_gen.xjustiz_0610_cl_mahn_3_0 import (
    CodeMahnKostenbefreiung,
    CodeMahnWiderspruchsart,
)

__NAMESPACE__ = "http://www.xjustiz.de"


@dataclass
class TypeMahnFachdatenAktenzeichenmitteilung:
    class Meta:
        name = "Type.MAHN.Fachdaten.Aktenzeichenmitteilung"

    instanzdaten: Optional[
        "TypeMahnFachdatenAktenzeichenmitteilung.Instanzdaten"
    ] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )

    @dataclass
    class Instanzdaten:
        """
        :ivar ref_instanznummer: Enthält eine Referenz auf die
            Instanznummer des Mahngerichts in den Instanzdaten des
            Grunddatensatzes.
        :ivar geschaeftszeichen_gericht: In der Aktenzeichenmitteilung
            ist das Geschäftszeichen des Antragsgegners zurückzugeben,
            auf den sich die Abgabe des Mahngerichts bezog. Dieser
            ergibt sich aus der Nachricht
            nachricht.mahn.uebergabe.0600002 (Element
            fachdaten/verfahrensablauf/antragsgegner). Anschließend kann
            das Element fachdaten/mahnbescheid/geschaeftszeichen.gericht
            aus dem Mahnbescheid entnommen werden, das sich gegen diesen
            Antragsgegner richtet.
        """

        ref_instanznummer: str = field(
            init=False,
            default="2",
            metadata={
                "name": "ref.instanznummer",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
            },
        )
        geschaeftszeichen_gericht: Optional[str] = field(
            default=None,
            metadata={
                "name": "geschaeftszeichen.gericht",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
            },
        )


@dataclass
class TypeMahnFachdatenUebergabe:
    """
    :ivar mahnbescheid: Daten des Mahnbescheids als Grundlage für einen
        Vollstreckungsbescheid, der evt. erst im streitigen Verfahren
        erlassen wird. In einem Mahnverfahren können mehrere
        Mahnbescheid gegen div. Antragsgegner ergehen.
    :ivar anspruch: Die Informationen zu einem gestellten Anspruch.
    :ivar widerspruch:
    :ivar vollstreckungsbescheid:
    :ivar verfahrensablauf: Kosten bezüglich Mahnverfahren oder
        Verfahrensablauf
    :ivar fachdaten_version:
    """

    class Meta:
        name = "Type.MAHN.Fachdaten.Uebergabe"

    mahnbescheid: list["TypeMahnFachdatenUebergabe.Mahnbescheid"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "min_occurs": 1,
        },
    )
    anspruch: list["TypeMahnFachdatenUebergabe.Anspruch"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "min_occurs": 1,
        },
    )
    widerspruch: list["TypeMahnFachdatenUebergabe.Widerspruch"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )
    vollstreckungsbescheid: list[
        "TypeMahnFachdatenUebergabe.Vollstreckungsbescheid"
    ] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )
    verfahrensablauf: list["TypeMahnFachdatenUebergabe.Verfahrensablauf"] = (
        field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )
    )
    fachdaten_version: str = field(
        init=False,
        default="1.6",
        metadata={
            "name": "fachdatenVersion",
            "type": "Attribute",
            "required": True,
            "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )

    @dataclass
    class Mahnbescheid:
        """
        :ivar antragsgegner: Über eine Referenz auf den Grunddatensatz
            wird der Antragsgegner angegeben. Je Antragsgegner ergeht
            ein Mahnbescheid.
        :ivar geschaeftszeichen_gericht: Rollenspezifisches
            gerichtliches Geschäftszeichen. Wenn ein Mahnverfahren gegen
            mehrere Antragsgegner geht, wird pro einzelnen Antragsgegner
            ein rollenspezifisches Geschäftszeichen vergeben.
        :ivar antragsdatum: Antragsdatum des Mahnbescheids
        :ivar antragseingangsdatum: Eingangsdatum des Antrag auf
            Erstellung eines Mahnbescheids
        :ivar erlassdatum: Das Datum, wann der Mahnbescheid erlassen
            wurde. Das Erlassdatum ist grundsätzlich anzugeben. Eine
            Ausnahme gilt für anfängliche Auslands- oder Nato-Verfahren.
            Hier wird der Mahnbescheid nicht zwingend vom Mahngericht
            erlassen. Die Abgabe erfolgt u.U. vor Erlass des
            Mahnbescheids. In diesen Fällen wird kein Erlassdatum
            angegeben.
        :ivar zustelldatum: Hier ist das Datum der Zustellung des
            Mahnbescheids an den einzelnen Antragsgegner anzugeben.
        """

        antragsgegner: Optional[TypeGdsRefRollennummer] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        geschaeftszeichen_gericht: list[str] = field(
            default_factory=list,
            metadata={
                "name": "geschaeftszeichen.gericht",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
            },
        )
        antragsdatum: Optional[XmlDate] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )
        antragseingangsdatum: Optional[XmlDate] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        erlassdatum: Optional[XmlDate] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )
        zustelldatum: Optional[XmlDate] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )

    @dataclass
    class Anspruch:
        """
        :ivar anspruchsnummer: Anspruchsnummer des Anspruchs: Eindeutige
            Kennzeichnung des Anspruchs innerhalb eines MB wird vom
            Mahngericht vergeben.
        :ivar auswahl_anspruch:
        :ivar betrag: Betragswert des Anspruchs
        """

        anspruchsnummer: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
            },
        )
        auswahl_anspruch: Optional[
            "TypeMahnFachdatenUebergabe.Anspruch.AuswahlAnspruch"
        ] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        betrag: Optional[TypeGdsGeldbetrag] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )

        @dataclass
        class AuswahlAnspruch:
            """
            :ivar sonstiger_anspruch: Bezeichnung des Sonstigen
                Anspruchs (=Zeile 36 des Mahnbescheidsantrags). Angabe
                eines Sonstigen Anspruchs, der nicht dem Hauptkatalog zu
                entnehmen ist.
            :ivar hauptforderung: Bezeichnung des Anspruchs entsprechend
                dem Hauptforderungs-Katalog von AUGEMA. (= Bezeichnung
                der im Mahnbescheidsantrag ausgewählten
                Hauptkatalognummer)
            """

            sonstiger_anspruch: Optional[str] = field(
                default=None,
                metadata={
                    "name": "sonstigerAnspruch",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            hauptforderung: Optional[
                "TypeMahnFachdatenUebergabe.Anspruch.AuswahlAnspruch.Hauptforderung"
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )

            @dataclass
            class Hauptforderung:
                """
                :ivar bezeichnung: Mögliche Werte sind
                    Dienstleistungsvertrag, Frachtkosten etc.
                """

                bezeichnung: Optional[str] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "http://www.xjustiz.de",
                        "required": True,
                        "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                    },
                )

    @dataclass
    class Widerspruch:
        """
        :ivar widerspruchsart: Gesamt / Teilwiderspruch
        :ivar datum: Datum des Widerspruchs (wird vom Mahngericht aus
            den Angaben im Formular, Schreiben etc. übernommen)
        :ivar eingangsdatum: Datum des Eingangs des Widerspruchs beim
            Mahngericht
        :ivar verspaetet: verspäteter Widerspruch J/N
        :ivar eingelegt_fuer: Hier ist die Referenz auf die Rollennummer
            des Beteiligten anzugeben, für den das Rechtsmittel
            eingelegt wurde.
        :ivar eingelegt_durch: Hier ist die Referenz auf die
            Rollennummer des Beteiligten anzugeben, der das Rechtsmittel
            eingelegt hat.
        """

        widerspruchsart: Optional[CodeMahnWiderspruchsart] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        datum: Optional[XmlDate] = field(
            default=None,
            metadata={
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
        verspaetet: Optional[bool] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        eingelegt_fuer: Optional[TypeGdsRefRollennummer] = field(
            default=None,
            metadata={
                "name": "eingelegtFuer",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        eingelegt_durch: Optional[TypeGdsRefRollennummer] = field(
            default=None,
            metadata={
                "name": "eingelegtDurch",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )

    @dataclass
    class Vollstreckungsbescheid:
        """
        :ivar schuldner: Referenz auf die Rollennummer des Schuldners,
            gegen den der Vollstreckungsbescheid erlassen wird.
        :ivar datum: Datum des Vollstreckungsbescheids
        :ivar einspruch:
        :ivar zustelldatum: Hier ist das Datum der Zustellung des
            Vollstreckungsbescheids an den Schuldner anzugeben.
        """

        schuldner: Optional[TypeGdsRefRollennummer] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        datum: Optional[XmlDate] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        einspruch: list[
            "TypeMahnFachdatenUebergabe.Vollstreckungsbescheid.Einspruch"
        ] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )
        zustelldatum: Optional[XmlDate] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )

        @dataclass
        class Einspruch:
            """
            :ivar datum: Datum des Einspruchs
            :ivar eingangsdatum: Datum des Eingangs des Einspruchs beim
                Mahngericht
            :ivar eingelegt_fuer: Hier ist die Referenz auf die
                Rollennummer des Beteiligten anzugeben, für den das
                Rechtsmittel eingelegt wurde.
            :ivar eingelegt_durch: Hier ist die Referenz auf die
                Rollennummer des Beteiligten anzugeben, der das
                Rechtsmittel eingelegt hat.
            """

            datum: Optional[XmlDate] = field(
                default=None,
                metadata={
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
            eingelegt_fuer: Optional[TypeGdsRefRollennummer] = field(
                default=None,
                metadata={
                    "name": "eingelegtFuer",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )
            eingelegt_durch: Optional[TypeGdsRefRollennummer] = field(
                default=None,
                metadata={
                    "name": "eingelegtDurch",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )

    @dataclass
    class Verfahrensablauf:
        """
        :ivar antragsgegner: Mit der Nachricht
            nachricht.mahn.uebergabe.0600002 wird nur der
            Verfahrensablauf gegen den Antragsgegner, gegen den das
            Verfahren abgegeben wird, übergeben. Aus der Referenz auf
            die Rollennummer des Antragsgegners geht hervor, gegen
            welchen von ggf. mehreren Antragsgegnern die Abgabe erfolgt.
        :ivar kosten:
        """

        antragsgegner: Optional[TypeGdsRefRollennummer] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
                "required": True,
            },
        )
        kosten: Optional[
            "TypeMahnFachdatenUebergabe.Verfahrensablauf.Kosten"
        ] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )

        @dataclass
        class Kosten:
            """
            :ivar kostenbefreiung: Kostenbefreiung, volle
                Zahlungspflicht, kostenbefreit, gebührenbefreit
            """

            kostenbefreiung: Optional[CodeMahnKostenbefreiung] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )


@dataclass
class NachrichtMahnAktenzeichenmitteilung0600001(TypeGdsBasisnachricht):
    """
    Diese Nachricht wird vom Prozessgericht an das Mahngericht gesendet und dient
    als Rückmeldung über das neu erfasste Verfahren.
    """

    class Meta:
        name = "nachricht.mahn.aktenzeichenmitteilung.0600001"
        namespace = "http://www.xjustiz.de"

    fachdaten: Optional[TypeMahnFachdatenAktenzeichenmitteilung] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class NachrichtMahnUebergabe0600002:
    """Diese Nachricht dient dazu, ein Mahnverfahren von einem Mahngericht an ein
    Prozessgericht zu übergeben.

    Es gibt Datensätze im Fachverfahren, in denen im Element 'vorname'
    Inhalte wie "Vorstand", "Geschäftsführer" oder dergleichen stehen,
    da die Rechtsprechung es zuließ, dass die namentliche Bezeichnung
    der Vertretungsorgane nicht immer erforderlich ist. Da für den
    Datenaustausch die Unterdrückung eines gültigen gesetzlichen
    Vertreters keine glückliche Lösung wäre (würde auch zu
    Constraintverletzungen im Verfahrensablauf führen, wenn die Referenz
    auf die Rollennummer ins Leere liefe), wurde beschlossen, in diesen
    Fällen den Eintrag "Name nicht bekannt" im Nachnamen zu setzen. Das
    übernehmende Fachverfahren muss darauf reagieren.
    """

    class Meta:
        name = "nachricht.mahn.uebergabe.0600002"
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
    fachdaten: Optional[TypeMahnFachdatenUebergabe] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
