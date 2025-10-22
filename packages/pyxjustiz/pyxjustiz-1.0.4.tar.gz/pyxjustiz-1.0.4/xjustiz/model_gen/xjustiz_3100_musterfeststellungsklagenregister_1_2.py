from dataclasses import dataclass, field
from typing import Optional

from xsdata.models.datatype import XmlDate

from xjustiz.model_gen.xjustiz_0000_grunddatensatz_3_5 import (
    TypeGdsBeteiligung,
    TypeGdsGeldbetrag,
    TypeGdsGrunddaten,
    TypeGdsNachrichtenkopf,
    TypeGdsSchriftgutobjekte,
)
from xjustiz.model_gen.xjustiz_3110_cl_musterfeststellungsklagenregister_1_2 import (
    CodeMfkregGliederungspunkte,
    CodeMfkregRegisterauszugsart,
)

__NAMESPACE__ = "http://www.xjustiz.de"


@dataclass
class TypeMfkregBekanntmachungstexte:
    """Je nach Kommunikationsszenario müssen bzw.

    können verschiedene Bekanntmachungen, Beschlüsse, Rechtsbelehrungen
    etc. zu einer Musterfeststellungsklage nach ZPO a.F., zu einer
    Unterlassungsklage oder zu einer einstweiligen Verfügung
    veröffentlicht werden. Das Szenario ergibt sich aus dem Ereignis,
    das im Nachrichtenkopf angegeben wird. Es ist dabei immer ein
    passender Gliederungspunkt zum Freitext anzugeben.

    :ivar ref_termins_id: Wenn die Bekanntmachung eines Termins zu einer
        Musterfeststellungsklage nach ZPO a.F. einen Hinweis zu diesem
        Termin enthält, dann wird dieser Hinweis als Bekanntmachungstext
        angegeben. Über diese ID kann der Hinweis auf den Termin
        referenzieren.
    :ivar textnummer: Die Texte innerhalb einer Bekanntmachung sind
        fortlaufend zu nummerieren.
    :ivar ueberschrift_bekanntmachung: Es ist zu jedem Text einer
        Bekanntmachung ein Gliederungspunkt als Überschrift gemäß
        Codeliste anzugeben.
    :ivar inhalt_bekanntmachung: Es ist der zum Gliederungspunkt
        passende Text der Bekanntmachung als Freitext anzugeben. Sofern
        es sich bei dem zu veröffentlichenden Text um eine
        Rechtsbelehrung handelt, wird ein Default-Text für die Gerichte
        vorgegeben (Codeliste Rechtsbelehrungen). Anderenfalls ist hier
        der, je nach Ereignis und Überschrift, zu veröffentlichende
        Inhalt der Bekanntmachung anzugeben.
    """

    class Meta:
        name = "Type.MFKREG.Bekanntmachungstexte"

    ref_termins_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ref.terminsID",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )
    textnummer: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    ueberschrift_bekanntmachung: Optional[CodeMfkregGliederungspunkte] = field(
        default=None,
        metadata={
            "name": "ueberschrift.bekanntmachung",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    inhalt_bekanntmachung: Optional[str] = field(
        default=None,
        metadata={
            "name": "inhalt.bekanntmachung",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
            "pattern": r"([ -~]|[¡-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )


@dataclass
class NachrichtMfkregRechtskraftVeroeffentlichungZustellung3100004:
    """Diese Nachricht wird für drei Kommunikationsszenarien genutzt.

    Erstens werden damit Bekanntmachungen zu rechtskräftigen
    Entscheidungen zu den Verfahren der Musterfeststellungsklagen nach
    ZPO a.F. von den Gerichten an das BfJ verschickt. Zweitens
    informiert so das BfJ die Gerichte über die Veröffentlichung einer
    Musterfeststellungsklage nach ZPO a.F. Und drittens übermitteln so
    die Prozessbevollmächtigten des Antragstellers auf Erlass einer
    einstweiligen Verfügung das Datum der Zustellung an den
    Antragsgegner, die Abschrift der einstweiligen Verfügung und den
    Zustellungsnachweis nach § 6a Absatz 1 Satz 3 bis 5 UKlaG (i.V.m. §
    8 Absatz 1 und 5 Satz 2 UWG). Diese letzte Nachricht ist die einzige
    im gesamten Fachmodul, bei der Schriftgutobjekte mitverschickt
    werden.
    """

    class Meta:
        name = (
            "nachricht.mfkreg.rechtskraft_veroeffentlichung_zustellung.3100004"
        )
        namespace = "http://www.xjustiz.de"

    nachrichtenkopf: Optional[TypeGdsNachrichtenkopf] = field(
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
    fachdaten: Optional[
        "NachrichtMfkregRechtskraftVeroeffentlichungZustellung3100004.Fachdaten"
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
        :ivar datum_ereignis: Je nach Ereignis ist entweder das Datum
            der Rechtskraft einer Rechtsprechung zu einer
            Musterfeststellungsklage, das Datum der Veröffentlichung der
            Bekanntmachung oder das Datum der erfolgten Zustellung des
            Erlasses einer einstweiligen Verfügung mitzuteilen. Das
            Gericht teilt die Rechtskraft einer Rechtsprechung dem BfJ
            mit. Das BfJ teilt das Datum der Veröffentlichung im
            Musterfeststellungsklagenregister mit. Der
            Prozessbevollmächtigte des Antragstellers auf Erlass einer
            einstweiligen Verfügung verschickt das Datum der erfolgten
            Zustellung, die Abschrift der einstweiligen Verfügung sowie
            den Zustellungsnachweis nach § 6a Absatz 1 Satz 3 bis 5
            UKlaG (i.V.m. § 8 Absatz 1 und 5 Satz 2 UWG).
        """

        datum_ereignis: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "datum.ereignis",
                "type": "Element",
                "required": True,
            },
        )


@dataclass
class NachrichtMfkregRegisterauszug3100007:
    """Diese Nachricht wird nur für den Registerauszug von
    Musterfeststellungsklagen nach ZPO a.F.

    genutzt.
    """

    class Meta:
        name = "nachricht.mfkreg.registerauszug.3100007"
        namespace = "http://www.xjustiz.de"

    nachrichtenkopf: Optional[TypeGdsNachrichtenkopf] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    fachdaten: Optional["NachrichtMfkregRegisterauszug3100007.Fachdaten"] = (
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
        """
        :ivar art_auszug: Es ist der jeweilige Anforderungsgrund
            anzugeben, der durch das Gericht angefordert wurde.
        :ivar stichtag_auszug: Hier ist das Datum des Stichtags
            angegeben, zu dem der Registerauszug erstellt wurde.
        :ivar richtigkeit_vollstaendigkeit: Mit diesem Element wird
            bestätigt, dass zu allen Anmeldungen deren Richtigkeit und
            Vollständigkeit vom Verbraucher oder dessen Vertreter
            versichert wurden.Es werden nur solche Anmeldungen durch das
            BfJ übermittelt.
        :ivar register_auszuege:
        """

        art_auszug: Optional[CodeMfkregRegisterauszugsart] = field(
            default=None,
            metadata={
                "name": "art.auszug",
                "type": "Element",
                "required": True,
            },
        )
        stichtag_auszug: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "stichtag.auszug",
                "type": "Element",
                "required": True,
            },
        )
        richtigkeit_vollstaendigkeit: Optional[bool] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
            },
        )
        register_auszuege: list[
            "NachrichtMfkregRegisterauszug3100007.Fachdaten.RegisterAuszuege"
        ] = field(
            default_factory=list,
            metadata={
                "name": "registerAuszuege",
                "type": "Element",
                "min_occurs": 1,
            },
        )

        @dataclass
        class RegisterAuszuege:
            """
            :ivar geschaeftszeichen_bf_j: Zu jeder Anmeldung im Register
                für Musterfeststellungsklagen gehört ein
                Geschäftszeichen des BfJ, mit der die Anmeldung
                eindeutig identifiziert ist.
            :ivar gegenstand_und_grund: Bei jeder Anmeldung muss der
                Gegenstand und Grund des Anspruchs oder des
                Rechtsverhältnisses vom Verbraucher gegenüber dem
                beklagten Unternehmen angegeben werden.
            :ivar betrag: Der Betrag der Forderung ist optional und wird
                in Euro angegeben.
            :ivar datum_anmeldung: Hier wird das Datum angegeben, an dem
                die Anmeldung im BfJ eingegangen ist.
            :ivar datum_ruecknahme: Hier wird das Datum angegeben, an
                dem die Anmeldung zurückgenommen wurde.
            :ivar aenderungshistorie: Sofern sich die Angaben der
                Beteiligten im Laufe des Verfahrens geändert haben (z.B.
                Name geändert), sind hier die Änderungen einzutragen.
            :ivar anmeldung_beteiligung: Hier sind die zugehörigen
                Beteiligtendaten der Anmeldung anzugeben. Für jede
                Anmeldung gibt es einen Beteiligten, den Verbraucher. Im
                Fall einer Rechtsnachfolge können auch mehrere
                Verbraucher als Beteiligte zur selben Anmeldung
                aufgeführt werden. Jeder Verbraucher kann zudem
                vertreten werden durch einen Rechtsbeistand, einen
                Betreuer oder einen sonstigen Vertreter.
            """

            geschaeftszeichen_bf_j: Optional[str] = field(
                default=None,
                metadata={
                    "name": "geschaeftszeichen.BfJ",
                    "type": "Element",
                    "required": True,
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            gegenstand_und_grund: Optional[str] = field(
                default=None,
                metadata={
                    "name": "gegenstandUndGrund",
                    "type": "Element",
                    "required": True,
                    "pattern": r"([ -~]|[¡-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            betrag: Optional[TypeGdsGeldbetrag] = field(
                default=None,
                metadata={
                    "type": "Element",
                },
            )
            datum_anmeldung: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.anmeldung",
                    "type": "Element",
                    "required": True,
                },
            )
            datum_ruecknahme: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.ruecknahme",
                    "type": "Element",
                },
            )
            aenderungshistorie: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "pattern": r"([ -~]|[¡-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            anmeldung_beteiligung: list[TypeGdsBeteiligung] = field(
                default_factory=list,
                metadata={
                    "name": "anmeldung.beteiligung",
                    "type": "Element",
                    "min_occurs": 1,
                },
            )


@dataclass
class NachrichtMfkregRevision3100005:
    """Diese Nachricht wird nur für Bekanntmachungen der Revision im Verfahren zu
    Musterfeststellungsklagen nach ZPO a.F.

    genutzt.
    """

    class Meta:
        name = "nachricht.mfkreg.revision.3100005"
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
    fachdaten: Optional["NachrichtMfkregRevision3100005.Fachdaten"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )

    @dataclass
    class Fachdaten:
        """
        :ivar datum_revision: Bei der Bekanntmachung einer Revision ist
            das Datum der Einlegung der Revision anzugeben.
        """

        datum_revision: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "datum.revision",
                "type": "Element",
                "required": True,
            },
        )


@dataclass
class NachrichtMfkregVergleichsaustritte3100008:
    """Diese Nachricht wird nur für die Vergleichsaustritte bei Verfahren zu
    Musterfeststellungsklagen nach ZPO a.F.

    genutzt.
    """

    class Meta:
        name = "nachricht.mfkreg.vergleichsaustritte.3100008"
        namespace = "http://www.xjustiz.de"

    nachrichtenkopf: Optional[TypeGdsNachrichtenkopf] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    fachdaten: Optional[
        "NachrichtMfkregVergleichsaustritte3100008.Fachdaten"
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
        :ivar vergleich_austritt: Die Geschäftsstelle des Gerichts
            protokolliert die Austritte aus einem Vergleich. Dazu
            gehören je Austritt das Geschäftszeichen der Anmeldung des
            BfJ sowie das Datum der Austrittserklärung.
        """

        vergleich_austritt: list[
            "NachrichtMfkregVergleichsaustritte3100008.Fachdaten.VergleichAustritt"
        ] = field(
            default_factory=list,
            metadata={
                "name": "vergleichAustritt",
                "type": "Element",
                "min_occurs": 1,
            },
        )

        @dataclass
        class VergleichAustritt:
            """
            :ivar geschaeftszeichen_bf_j: Hier wird das BfJ-
                Geschäftzeichen des Beteiligten angegeben.
            :ivar austrittsdatum: Hier wird das Datum des Austritts aus
                dem Vergleich angegeben.
            """

            geschaeftszeichen_bf_j: Optional[str] = field(
                default=None,
                metadata={
                    "name": "geschaeftszeichen.BfJ",
                    "type": "Element",
                    "required": True,
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            austrittsdatum: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "required": True,
                },
            )


@dataclass
class NachrichtMfkregVerhandlungRegisterauszugsanforderung3100006:
    """Diese Nachricht wird nur für Bekanntmachungen zu Verhandlungen und
    Registerauszugsanforderungen zu Verfahren von Musterfeststellungsklagen nach
    ZPO a.F.

    genutzt.
    """

    class Meta:
        name = (
            "nachricht.mfkreg.verhandlung_registerauszugsanforderung.3100006"
        )
        namespace = "http://www.xjustiz.de"

    nachrichtenkopf: Optional[TypeGdsNachrichtenkopf] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    fachdaten: Optional[
        "NachrichtMfkregVerhandlungRegisterauszugsanforderung3100006.Fachdaten"
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
        :ivar verhandlung: Unter der Sequenz werden Mitteilungen zum
            Beginn der Verhandlung des Musterfeststellungsverfahrens
            angegeben werden.
        :ivar registerauszug: Unter der Sequenz kann angegeben werden,
            ob ein Auszug beim Register angefordert wird. Es ist der
            jeweilige Anforderungsgrund anzugeben.
        """

        verhandlung: Optional[
            "NachrichtMfkregVerhandlungRegisterauszugsanforderung3100006.Fachdaten.Verhandlung"
        ] = field(
            default=None,
            metadata={
                "type": "Element",
            },
        )
        registerauszug: Optional[
            "NachrichtMfkregVerhandlungRegisterauszugsanforderung3100006.Fachdaten.Registerauszug"
        ] = field(
            default=None,
            metadata={
                "type": "Element",
            },
        )

        @dataclass
        class Verhandlung:
            """
            :ivar termin_stattgefunden: Es wird angegeben, ob der erste
                Termin stattfgefunden hat.
            :ivar datum_termin: Sofern der erste Termin stattgefunden
                hat, ist hier das Datum des Termins anzugeben.
            :ivar verhandlung_stattgefunden: Es wird angegeben, ob die
                mündliche Verhandlung begonnen wurde.
            :ivar datum_verhandlung: Sofern die mündliche Verhandlung
                begonnen wurde, ist hier das Datum des Beginns der
                mündlichen Verhandlung anzugeben.
            """

            termin_stattgefunden: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "terminStattgefunden",
                    "type": "Element",
                    "required": True,
                },
            )
            datum_termin: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.termin",
                    "type": "Element",
                },
            )
            verhandlung_stattgefunden: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "verhandlungStattgefunden",
                    "type": "Element",
                    "required": True,
                },
            )
            datum_verhandlung: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.verhandlung",
                    "type": "Element",
                },
            )

        @dataclass
        class Registerauszug:
            auszug_anfordern: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "auszugAnfordern",
                    "type": "Element",
                    "required": True,
                },
            )
            art_auszug: Optional[CodeMfkregRegisterauszugsart] = field(
                default=None,
                metadata={
                    "name": "art.auszug",
                    "type": "Element",
                    "required": True,
                },
            )


@dataclass
class NachrichtMfkregZurueckweisungVeroeffentlichung3100009:
    """Diese Nachricht wird nur für die Zurückweisung von Veröffentlichungen zu
    Musterfeststellungsklagen nach ZPO a.F.

    genutzt.
    """

    class Meta:
        name = "nachricht.mfkreg.zurueckweisungVeroeffentlichung.3100009"
        namespace = "http://www.xjustiz.de"

    nachrichtenkopf: Optional[TypeGdsNachrichtenkopf] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    fachdaten: Optional[
        "NachrichtMfkregZurueckweisungVeroeffentlichung3100009.Fachdaten"
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
        :ivar grund_zurueckweisung: Es ist anzugeben, welche Daten, die
            für die Veröffentlichung im
            Musterfeststellungsklagenregister notwendig sind, nicht
            durch das zuständige Gericht übermittelt bzw. nicht
            schlüssig angegeben worden sind, sodass eine
            Veröffentlichung durch das BfJ zurückgewiesen werden muss.
        """

        grund_zurueckweisung: Optional[str] = field(
            default=None,
            metadata={
                "name": "grund.zurueckweisung",
                "type": "Element",
                "required": True,
                "pattern": r"([ -~]|[¡-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
            },
        )


@dataclass
class NachrichtMfkregBeendigung3100003:
    """Diese Nachricht wird sowohl für Bekanntmachungen der Beendigung der
    Verfahren von Musterfeststellungsklagen nach ZPO a.F.

    als auch für Bekanntmachungen der Beendigung der Verfahren von
    Unterlassungsklagen und einstweiligen Verfügungen nach § 6a UKlaG
    (i.V.m. § 8 Absatz 1 und 5 Satz 2 UWG) genutzt. Nachricht zur
    Übermittlung des Formulars 5.
    """

    class Meta:
        name = "nachricht.mfkreg.beendigung.3100003"
        namespace = "http://www.xjustiz.de"

    nachrichtenkopf: Optional[TypeGdsNachrichtenkopf] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    fachdaten: Optional["NachrichtMfkregBeendigung3100003.Fachdaten"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )

    @dataclass
    class Fachdaten:
        """
        :ivar datum_verfahrensende: Bei der Bekanntmachung einer
            Beendigung des Verfahrens ist das Datum des Verfahrensendes
            anzugeben. Das Datum ist ungleich zum Erstellungszeitpunkt
            der XJustiz-Nachricht.
        :ivar verfahrensende_art: Hier wird angegeben, durch welche Art
            das Verfahren beendet worden ist. Teilbeendigungen können
            auch durch verschiedene Beendigungsarten angegeben werden.
            Für Musterfeststellungsverfahren nach ZPO a.F.,
            Unterlassungsklagen und einstweilige Verfügungen sind alle
            sieben Optionen (auch mehrere miteinander kombiniert)
            möglich.
        :ivar teilrechtskraft_entscheidung: Wenn eine BGH-Entscheidung
            Teilrechtskraft hat, kann das hier angegeben werden. Das
            Datum ist identisch mit dem Datum des Verfahrensendes
            (s.o.).
        :ivar beschlussinhalt: Es sind die bekanntzumachenden Inhalte
            des Beschlusses, des Vergleichs etc., der/ die zur
            Beendigung des Verfahrens geführt hat, anzugeben.
        """

        datum_verfahrensende: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "datum.verfahrensende",
                "type": "Element",
                "required": True,
            },
        )
        verfahrensende_art: Optional[
            "NachrichtMfkregBeendigung3100003.Fachdaten.VerfahrensendeArt"
        ] = field(
            default=None,
            metadata={
                "name": "verfahrensendeArt",
                "type": "Element",
                "required": True,
            },
        )
        teilrechtskraft_entscheidung: Optional[str] = field(
            default=None,
            metadata={
                "name": "teilrechtskraftEntscheidung",
                "type": "Element",
                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
            },
        )
        beschlussinhalt: list[TypeMfkregBekanntmachungstexte] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            },
        )

        @dataclass
        class VerfahrensendeArt:
            """
            :ivar beendigung_urteil:
            :ivar beendigung_beschluss:
            :ivar beendigung_vergleichsbeschluss:
            :ivar beendigung_klageruecknahme:
            :ivar beendigung_rechtsmittelruecknahme:
            :ivar beendigung_erledigung_rechtsstreit:
            :ivar sonstige_beendigung: Für den Fall, dass die
                Beendigungsart keinem der oben genannten Werte
                zugeordnet werden kann, kann diese weiterhin als
                Freitext übergeben werden.
            """

            beendigung_urteil: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "beendigungUrteil",
                    "type": "Element",
                    "required": True,
                },
            )
            beendigung_beschluss: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "beendigungBeschluss",
                    "type": "Element",
                    "required": True,
                },
            )
            beendigung_vergleichsbeschluss: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "beendigungVergleichsbeschluss",
                    "type": "Element",
                    "required": True,
                },
            )
            beendigung_klageruecknahme: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "beendigungKlageruecknahme",
                    "type": "Element",
                    "required": True,
                },
            )
            beendigung_rechtsmittelruecknahme: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "beendigungRechtsmittelruecknahme",
                    "type": "Element",
                    "required": True,
                },
            )
            beendigung_erledigung_rechtsstreit: Optional[bool] = field(
                default=None,
                metadata={
                    "name": "beendigungErledigungRechtsstreit",
                    "type": "Element",
                    "required": True,
                },
            )
            sonstige_beendigung: Optional[str] = field(
                default=None,
                metadata={
                    "name": "sonstigeBeendigung",
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )


@dataclass
class NachrichtMfkregBerichtigungsbeschluss3100010:
    """Diese Nachricht wird nur für Bekanntmachungen der Berichtigungsbeschlüsse
    von Musterfeststellungsklagen nach ZPO a.F.

    und zu einstweiligen Verfügungen und Unterlassungsklagen nach § 6a
    UKlaG (i.V.m. § 8 Absatz 1 und 5 Satz 2 UWG) genutzt.
    """

    class Meta:
        name = "nachricht.mfkreg.berichtigungsbeschluss.3100010"
        namespace = "http://www.xjustiz.de"

    nachrichtenkopf: Optional[TypeGdsNachrichtenkopf] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    fachdaten: Optional[
        "NachrichtMfkregBerichtigungsbeschluss3100010.Fachdaten"
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
        :ivar datum_bekanntmachung: Es ist das Datum der zu
            berichtigenden öffentlichen Bekanntmachung anzugeben.
        :ivar datum_berichtigungsbeschluss:
        :ivar beschlussinhalt: Ergeht ein Berichtigungsbeschluss, wird
            dieser Beschluss stets in der Form im Klageregister bekannt
            gemacht, in der er vom Gericht übermittelt wurde. Das
            Gericht kann den Berichtigungsbeschluss und/ oder einen
            konsolidierten Text, der die berichtigten Inhalte enthält,
            an das BfJ übermitteln.
        """

        datum_bekanntmachung: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "datum.bekanntmachung",
                "type": "Element",
                "required": True,
            },
        )
        datum_berichtigungsbeschluss: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "datum.berichtigungsbeschluss",
                "type": "Element",
                "required": True,
            },
        )
        beschlussinhalt: list[TypeMfkregBekanntmachungstexte] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            },
        )


@dataclass
class NachrichtMfkregHinweiseZwischenentscheidung3100002:
    """Diese Nachricht wird nur für Bekanntmachungen von Hinweisen und
    Zwischenentscheidungen zu Musterfeststellungsklagen nach ZPO a.F.

    genutzt. Nachricht zur Übermittlung der Formulare 3 und 4.
    """

    class Meta:
        name = "nachricht.mfkreg.hinweise_zwischenentscheidung.3100002"
        namespace = "http://www.xjustiz.de"

    nachrichtenkopf: Optional[TypeGdsNachrichtenkopf] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    fachdaten: Optional[
        "NachrichtMfkregHinweiseZwischenentscheidung3100002.Fachdaten"
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
        :ivar datum_ereignis: Bei der Bekanntmachung von Hinweisen oder
            Zwischenentscheidungen ist das Datum der jeweiligen
            Ereignisse anzugeben. Das Datum ist in der Regel ungleich
            zum Erstellungszeitpunkt der XJustiz-Nachricht.
        :ivar beschlussinhalt: Bei der Bekanntmachung von Hinweisen oder
            Zwischenentscheidungen kann angegeben werden, ob die
            jeweiligen Zwischenstände mit einem Termin oder einem
            Feststellungsziel verknüpft werden soll.
        """

        datum_ereignis: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "datum.ereignis",
                "type": "Element",
                "required": True,
            },
        )
        beschlussinhalt: list[
            "NachrichtMfkregHinweiseZwischenentscheidung3100002.Fachdaten.Beschlussinhalt"
        ] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            },
        )

        @dataclass
        class Beschlussinhalt:
            """
            :ivar text_bekanntmachung:
            :ivar feststellungsziele_verweis: Unter dieser Sequenz kann
                abgebildet werden, ob eine Verlinkung der
                bekanntzumachenden Hinweise oder Zwischenentscheidungen
                zu den Feststellungszielen erwünscht ist und wie die
                Verlinkung platziert werden soll. Es ist anzugeben, ob
                die Feststellungsziele ergänzt, modifiziert oder ergänzt
                und modifiziert worden sind.
            """

            text_bekanntmachung: Optional[TypeMfkregBekanntmachungstexte] = (
                field(
                    default=None,
                    metadata={
                        "name": "text.bekanntmachung",
                        "type": "Element",
                        "required": True,
                    },
                )
            )
            feststellungsziele_verweis: Optional[
                "NachrichtMfkregHinweiseZwischenentscheidung3100002.Fachdaten.Beschlussinhalt.FeststellungszieleVerweis"
            ] = field(
                default=None,
                metadata={
                    "name": "feststellungszieleVerweis",
                    "type": "Element",
                },
            )

            @dataclass
            class FeststellungszieleVerweis:
                ergaenzt: Optional[bool] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "required": True,
                    },
                )
                modifiziert: Optional[bool] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "required": True,
                    },
                )


@dataclass
class NachrichtMfkregKlagebekanntmachungTerminbestimmung3100001:
    """Diese Nachricht wird sowohl für Bekanntmachungen und Terminbestimmungen von
    Musterfeststellungsklagen nach ZPO a.F.

    als auch für Bekanntmachungen von Unterlassungsklagen und
    einstweiligen Verfügungen nach § 6a UKlaG (i.V.m. § 8 Absatz 1 und 5
    Satz 2 UWG) genutzt. Nachricht zur Übermittlung der Formulare 1 und
    2.
    """

    class Meta:
        name = "nachricht.mfkreg.klagebekanntmachung_terminbestimmung.3100001"
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
    fachdaten: Optional[
        "NachrichtMfkregKlagebekanntmachungTerminbestimmung3100001.Fachdaten"
    ] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )

    @dataclass
    class Fachdaten:
        """
        :ivar text_bekanntmachung: Es sind die bekanntzumachenden
            Inhalte als Freitext anzugeben. Bei der Bekanntmachung einer
            Musterfeststellungsklage nach ZPO a.F. sind hier zwingend
            die „Feststellungsziele“, die „kurze Darstellung des
            Lebenssachverhalts“ sowie vier Rechtsbelehrungen anzugeben.
            Für die Rechtsbelehrungen stehen Default-Texte zur
            Verfügung, die bei Bedarf angepasst werden können.
            Bekanntmachungen von Unterlassungsklagen und von
            einstweiligen Verfügungen enthalten jeweils nur einen
            Bekanntmachungstext zu der behaupteten Zuwiderhandlung, die
            Anlass des Antrags auf Erlass einer einstweiligen Verfügung
            ist bzw. gegen die die Klage gerichtet ist. Es sind die
            passenden Gliederungspunkte der Bekanntmachung aus der
            Codeliste auszuwählen. Bei der Bekanntmachung des Antrags
            auf Erlass einer einstweiligen Verfügung, der dem
            Antragsgegner zugestellt worden ist, sind das Datum des
            Eingangs des Antrags bei Gericht und das Datum der
            Zustellung des Antrags beim Antragsgegner unverzüglich
            bekanntzumachen. Wurde die einstweilige Verfügung erlassen,
            ohne dass der Antrag auf Erlass der einstweiligen Verfügung
            dem Antragsgegner vorher zugestellt worden ist, tritt an die
            Stelle der Bekanntmachung des Datums der Zustellung des
            Antrags das Datum des Erlasses der einstweiligen Verfügung.
            Bei der Bekanntmachung der Unterlassungsklage müssen das
            Datum der Anhängigkeit der Klage (= Eingang der Klage bei
            Gericht) und das Datum der Rechtshängigkeit der Klage (=
            Zustellung der Klage an den Beklagten) übermittelt werden.
            Sowohl für Unterlassungsklagen als auch für einstweilige
            Verfügungen muss mindestens ein Grund für die Erhebung der
            Klage bzw. die Stellung des Antrags angegeben werden:
            Verstoß gegen Normen des Gesetzes gegen den unlauteren
            Wettbewerb oder Verstoß gegen Normen des
            Unterlassungsklagengesetzes (oder beides).
        :ivar datum_eingang:
        :ivar datum_erlass:
        :ivar datum_zustellung:
        :ivar rechtsgrundlage_uwg:
        :ivar rechtsgrundlage_ukla_g:
        """

        text_bekanntmachung: list[TypeMfkregBekanntmachungstexte] = field(
            default_factory=list,
            metadata={
                "name": "text.bekanntmachung",
                "type": "Element",
            },
        )
        datum_eingang: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "datum.eingang",
                "type": "Element",
            },
        )
        datum_erlass: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "datum.erlass",
                "type": "Element",
            },
        )
        datum_zustellung: Optional[XmlDate] = field(
            default=None,
            metadata={
                "name": "datum.zustellung",
                "type": "Element",
            },
        )
        rechtsgrundlage_uwg: Optional[bool] = field(
            default=None,
            metadata={
                "name": "rechtsgrundlage.UWG",
                "type": "Element",
            },
        )
        rechtsgrundlage_ukla_g: Optional[bool] = field(
            default=None,
            metadata={
                "name": "rechtsgrundlage.UKlaG",
                "type": "Element",
            },
        )
