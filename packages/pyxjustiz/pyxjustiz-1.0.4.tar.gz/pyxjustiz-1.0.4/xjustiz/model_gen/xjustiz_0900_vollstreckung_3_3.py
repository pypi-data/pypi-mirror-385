from dataclasses import dataclass, field
from typing import Optional

from xsdata.models.datatype import XmlDate, XmlDateTime

from xjustiz.model_gen.xjustiz_0000_grunddatensatz_3_5 import (
    TypeGdsAktenzeichen,
    TypeGdsBasisnachricht,
    TypeGdsGrunddaten,
    TypeGdsNachrichtenkopf,
    TypeGdsRefBeteiligtennummer,
)
from xjustiz.model_gen.xjustiz_0020_cl_gerichte_3_3 import CodeGdsGerichteTyp3
from xjustiz.model_gen.xjustiz_0910_cl_vollstreckung_3_1 import (
    CodeVstrAnredePartei,
    CodeVstrEintragungsgruendeGerichtsvollzieherVollstreckungsbehoerde,
    CodeVstrEintragungsgruendeInsolvenzgericht,
    CodeVstrEntscheidungsinhaltSchuldnerwiderspruch,
    CodeVstrGerichtsvollzieherDienstbezeichnung,
    CodeVstrKorrekturLoeschung,
    CodeVstrSchuldnerverzeichnisLoeschungsgruende,
    CodeVstrVerarbeitungsergebnisSchuldnerverzeichnis,
    CodeVstrVermoegensverzeichnisArt,
)

__NAMESPACE__ = "http://www.xjustiz.de"


@dataclass
class TypeVstrVollstreckungsbehoerde:
    class Meta:
        name = "Type.VSTR.Vollstreckungsbehoerde"

    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
            "pattern": r"([ -~]|[¡-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )
    ort: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
            "pattern": r"([ -~]|[¡-£]|¥|[§-¬]|[®-·]|[¹-»]|[¿-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )


@dataclass
class TypeVstrBeteiligterZusatz:
    """
    :ivar beteiligter_referenz: Referenz auf den im Grunddatensatz
        angegebenen Beteiligten
    :ivar anrede:
    :ivar person_handelnd_unter:
    :ivar organisation_namenszusatz:
    """

    class Meta:
        name = "Type.VSTR.Beteiligter.Zusatz"

    beteiligter_referenz: Optional[TypeGdsRefBeteiligtennummer] = field(
        default=None,
        metadata={
            "name": "beteiligter.referenz",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    anrede: Optional[CodeVstrAnredePartei] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    person_handelnd_unter: list[str] = field(
        default_factory=list,
        metadata={
            "name": "person.handelndUnter",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "pattern": r"([ -~]|[¡-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )
    organisation_namenszusatz: Optional[str] = field(
        default=None,
        metadata={
            "name": "organisation.namenszusatz",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "pattern": r"([ -~]|[¡-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )


@dataclass
class TypeVstrGerichtsvollzieher:
    class Meta:
        name = "Type.VSTR.Gerichtsvollzieher"

    dienstbezeichnung: Optional[
        CodeVstrGerichtsvollzieherDienstbezeichnung
    ] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    vorname: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
            "pattern": r"( |'|[,-\.]|[A-Z]|[`-z]|~|¨|´|·|[À-Ö]|[Ø-ö]|[ø-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
            "pattern": r"( |'|[,-\.]|[A-Z]|[`-z]|~|¨|´|·|[À-Ö]|[Ø-ö]|[ø-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )
    amtsgericht: Optional[CodeGdsGerichteTyp3] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )


@dataclass
class NachrichtVstrFehlermeldung0900008(TypeGdsBasisnachricht):
    class Meta:
        name = "nachricht.vstr.fehlermeldung.0900008"
        namespace = "http://www.xjustiz.de"

    fachdaten: Optional["NachrichtVstrFehlermeldung0900008.Fachdaten"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )

    @dataclass
    class Fachdaten:
        fehlertext: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
                "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
            },
        )


@dataclass
class TypeVstrEintragungsanordnungAllgemein:
    """
    Dieser Typ ist die Basis für die Typen
    'Type.VSTR.Eintragungsanordnung.Schuldnerverzeichnis' und
    'Type.VSTR.Eintragungsanordnung.Schuldnerverzeichnis.Portal'.

    :ivar auswahl_anordnungsbehoerde_eintragungsgrund: Hier ist die
        Stelle, von der die Eintragungsanordnung stammt, anzugeben und
        der Grund der Eintragung.
    :ivar aktenzeichen_eintragungsanordnung:
    :ivar datum_der_eintragungsanordnung:
    """

    class Meta:
        name = "Type.VSTR.Eintragungsanordnung.Allgemein"

    auswahl_anordnungsbehoerde_eintragungsgrund: Optional[
        "TypeVstrEintragungsanordnungAllgemein.AuswahlAnordnungsbehoerdeEintragungsgrund"
    ] = field(
        default=None,
        metadata={
            "name": "auswahl_anordnungsbehoerde.eintragungsgrund",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    aktenzeichen_eintragungsanordnung: Optional[TypeGdsAktenzeichen] = field(
        default=None,
        metadata={
            "name": "aktenzeichen.eintragungsanordnung",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    datum_der_eintragungsanordnung: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "datumDerEintragungsanordnung",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )

    @dataclass
    class AuswahlAnordnungsbehoerdeEintragungsgrund:
        anordnung_gerichtsvollzieher_vollstreckungsbehoerde: Optional[
            "TypeVstrEintragungsanordnungAllgemein.AuswahlAnordnungsbehoerdeEintragungsgrund.AnordnungGerichtsvollzieherVollstreckungsbehoerde"
        ] = field(
            default=None,
            metadata={
                "name": "anordnung.gerichtsvollzieherVollstreckungsbehoerde",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )
        anordnung_insolvenzgericht: Optional[
            "TypeVstrEintragungsanordnungAllgemein.AuswahlAnordnungsbehoerdeEintragungsgrund.AnordnungInsolvenzgericht"
        ] = field(
            default=None,
            metadata={
                "name": "anordnung.insolvenzgericht",
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )

        @dataclass
        class AnordnungGerichtsvollzieherVollstreckungsbehoerde:
            """
            :ivar auswahl_gerichtsvollzieher_vollstreckungsbehoerde:
            :ivar
                eintragungsgrund_gerichtsvollzieher_vollstreckungsbehoerde:
                Jede Eintragungsanordnung kann nur einen
                Eintragungsgrund enthalten.
            """

            auswahl_gerichtsvollzieher_vollstreckungsbehoerde: Optional[
                "TypeVstrEintragungsanordnungAllgemein.AuswahlAnordnungsbehoerdeEintragungsgrund.AnordnungGerichtsvollzieherVollstreckungsbehoerde.AuswahlGerichtsvollzieherVollstreckungsbehoerde"
            ] = field(
                default=None,
                metadata={
                    "name": "auswahl_gerichtsvollzieherVollstreckungsbehoerde",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )
            eintragungsgrund_gerichtsvollzieher_vollstreckungsbehoerde: Optional[
                CodeVstrEintragungsgruendeGerichtsvollzieherVollstreckungsbehoerde
            ] = field(
                default=None,
                metadata={
                    "name": "eintragungsgrund.gerichtsvollzieherVollstreckungsbehoerde",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )

            @dataclass
            class AuswahlGerichtsvollzieherVollstreckungsbehoerde:
                gerichtsvollzieher: Optional[TypeVstrGerichtsvollzieher] = (
                    field(
                        default=None,
                        metadata={
                            "type": "Element",
                            "namespace": "http://www.xjustiz.de",
                        },
                    )
                )
                vollstreckungsbehoerde: Optional[
                    TypeVstrVollstreckungsbehoerde
                ] = field(
                    default=None,
                    metadata={
                        "type": "Element",
                        "namespace": "http://www.xjustiz.de",
                    },
                )

        @dataclass
        class AnordnungInsolvenzgericht:
            """
            :ivar insolvenzgericht:
            :ivar eintragungsgrund_insolvenzgericht: Jede
                Eintragungsanordnung kann nur einen Eintragungsgrund
                enthalten.
            :ivar datum_erlass_des_beschlusses:
            """

            insolvenzgericht: Optional[CodeGdsGerichteTyp3] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )
            eintragungsgrund_insolvenzgericht: Optional[
                CodeVstrEintragungsgruendeInsolvenzgericht
            ] = field(
                default=None,
                metadata={
                    "name": "eintragungsgrund.insolvenzgericht",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )
            datum_erlass_des_beschlusses: Optional[XmlDate] = field(
                default=None,
                metadata={
                    "name": "datum.erlassDesBeschlusses",
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                    "required": True,
                },
            )


@dataclass
class TypeVstrUebermittlungVermoegensverzeichnis:
    """
    :ivar auswahl_anordnende_stelle: Hier ist d. Gerichtsvollzieher(in)
        oder die Vollstreckungsbehörde anzugeben, der/die das
        Vermögensverzeichnis abnimmt.
    :ivar aktenzeichen_anordnende_stelle:
    :ivar datum_des_vermoegensverzeichnisses:
    :ivar art_des_vermoegensverzeichnisses: Hier wird klargestellt, ob
        das Vermögensverzeichnis beruht auf (1) der erstmaligen
        Vermögensauskunft d. Schuldners/Schuldnerin, ggf. nach Ablauf
        der zweijährigen Löschfrist, (2) einer erneuten
        Vermögensauskunft nach § 802d ZPO oder (3) der Nachbesserung
        (Ergänzung) eines bereits übermittelten Vermögensverzeichnisses.
    :ivar korrektur_loeschung: Soll eine bereits übermittelte Eintragung
        geändert werden, ist hier festzulegen, (1) ob der Datensatz
        durch einen korrigierten Datensatz zu ersetzen ist oder der
        gesamte Datensatz gelöscht werden muss, (2) ob der Datensatz von
        Anfang an fehlerhaft war (irriger Eintrag) oder sich die Daten
        nachträglich geändert haben.
    :ivar dokumentenname: Hier ist der Dateiname des beigefügten
        Vermögensverzeichnisses anzugeben.
    """

    class Meta:
        name = "Type.VSTR.Uebermittlung.Vermoegensverzeichnis"

    auswahl_anordnende_stelle: Optional[
        "TypeVstrUebermittlungVermoegensverzeichnis.AuswahlAnordnendeStelle"
    ] = field(
        default=None,
        metadata={
            "name": "auswahl_anordnendeStelle",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    aktenzeichen_anordnende_stelle: Optional[TypeGdsAktenzeichen] = field(
        default=None,
        metadata={
            "name": "aktenzeichen.anordnendeStelle",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    datum_des_vermoegensverzeichnisses: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "datumDesVermoegensverzeichnisses",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    art_des_vermoegensverzeichnisses: Optional[
        CodeVstrVermoegensverzeichnisArt
    ] = field(
        default=None,
        metadata={
            "name": "artDesVermoegensverzeichnisses",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    korrektur_loeschung: Optional[CodeVstrKorrekturLoeschung] = field(
        default=None,
        metadata={
            "name": "korrekturLoeschung",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )
    dokumentenname: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
            "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
        },
    )

    @dataclass
    class AuswahlAnordnendeStelle:
        gerichtsvollzieher: Optional[TypeVstrGerichtsvollzieher] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.xjustiz.de",
            },
        )
        vollstreckungsbehoerde: Optional[TypeVstrVollstreckungsbehoerde] = (
            field(
                default=None,
                metadata={
                    "type": "Element",
                    "namespace": "http://www.xjustiz.de",
                },
            )
        )


@dataclass
class TypeVstrEintragungsanordnungSchuldnerverzeichnis(
    TypeVstrEintragungsanordnungAllgemein
):
    """
    :ivar korrektur_loeschung: Soll eine bereits übermittelte Eintragung
        geändert werden, ist hier festzulegen, (1) ob der Datensatz
        durch einen korrigierten Datensatz zu ersetzen ist oder der
        gesamte Datensatz gelöscht werden muss, (2) ob der Datensatz von
        Anfang an fehlerhaft war (irriger Eintrag) oder sich die Daten
        nachträglich geändert haben.
    """

    class Meta:
        name = "Type.VSTR.Eintragungsanordnung.Schuldnerverzeichnis"

    korrektur_loeschung: Optional[CodeVstrKorrekturLoeschung] = field(
        default=None,
        metadata={
            "name": "korrekturLoeschung",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )


@dataclass
class TypeVstrEintragungsanordnungSchuldnerverzeichnisPortal(
    TypeVstrEintragungsanordnungAllgemein
):
    """
    :ivar loeschung_aenderung_der_eintragung_im_schuldnerverzeichnis:
        Dieses Element findet Verwendung im Datenaustausch zwischen
        zentralem Vollstreckungsgericht und Vollstreckungsportal. Es
        wird außerdem durch das Vollstreckungsportal für die Nachrichten
        an die Abdruckempfänger genutzt.
    """

    class Meta:
        name = "Type.VSTR.Eintragungsanordnung.Schuldnerverzeichnis.Portal"

    loeschung_aenderung_der_eintragung_im_schuldnerverzeichnis: Optional[
        CodeVstrSchuldnerverzeichnisLoeschungsgruende
    ] = field(
        default=None,
        metadata={
            "name": "loeschungAenderungDerEintragungImSchuldnerverzeichnis",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )


@dataclass
class TypeVstrEntscheidungSchuldnerwiderspruch:
    """
    :ivar eintragungsanordnung_allgemein:
    :ivar datum_der_entscheidung: Hier ist das Datum der Entscheidung
        über den Schuldnerwiderspruch anzugeben.
    :ivar inhalt_der_entscheidung: Hier ist der Inhalt der Entscheidung
        über den Schuldnerwiderspruch anzugeben.
    :ivar korrektur_loeschung: Soll eine bereits übermittelte Eintragung
        geändert werden, ist hier festzulegen, (1) ob der Datensatz
        durch einen korrigierten Datensatz zu ersetzen ist oder der
        gesamte Datensatz gelöscht werden muss, (2) ob der Datensatz von
        Anfang an fehlerhaft war (irriger Eintrag) oder sich die Daten
        nachträglich geändert haben.
    """

    class Meta:
        name = "Type.VSTR.Entscheidung.Schuldnerwiderspruch"

    eintragungsanordnung_allgemein: Optional[
        TypeVstrEintragungsanordnungAllgemein
    ] = field(
        default=None,
        metadata={
            "name": "eintragungsanordnung.allgemein",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    datum_der_entscheidung: Optional[XmlDate] = field(
        default=None,
        metadata={
            "name": "datumDerEntscheidung",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    inhalt_der_entscheidung: Optional[
        CodeVstrEntscheidungsinhaltSchuldnerwiderspruch
    ] = field(
        default=None,
        metadata={
            "name": "inhaltDerEntscheidung",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
            "required": True,
        },
    )
    korrektur_loeschung: Optional[CodeVstrKorrekturLoeschung] = field(
        default=None,
        metadata={
            "name": "korrekturLoeschung",
            "type": "Element",
            "namespace": "http://www.xjustiz.de",
        },
    )


@dataclass
class NachrichtVstrVermoegensverzeichnisUebermittlungKorrektur0900006:
    class Meta:
        name = "nachricht.vstr.vermoegensverzeichnis.uebermittlung.korrektur.0900006"
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
        "NachrichtVstrVermoegensverzeichnisUebermittlungKorrektur0900006.Fachdaten"
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
        :ivar uebermittlung_vermoegensverzeichnis:
        :ivar beteiligter_zusatz: Für den im Grunddatensatz angegebenen
            Beteiligten werden weitergehende Informationen übergeben.
        """

        uebermittlung_vermoegensverzeichnis: Optional[
            TypeVstrUebermittlungVermoegensverzeichnis
        ] = field(
            default=None,
            metadata={
                "name": "uebermittlung.vermoegensverzeichnis",
                "type": "Element",
                "required": True,
            },
        )
        beteiligter_zusatz: Optional[TypeVstrBeteiligterZusatz] = field(
            default=None,
            metadata={
                "name": "beteiligter.zusatz",
                "type": "Element",
                "required": True,
            },
        )


@dataclass
class NachrichtVstrVermoegensverzeichnisUebermittlungsbestaetigungPortal0900007:
    class Meta:
        name = "nachricht.vstr.vermoegensverzeichnis.uebermittlungsbestaetigung.portal.0900007"
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
        "NachrichtVstrVermoegensverzeichnisUebermittlungsbestaetigungPortal0900007.Fachdaten"
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
        :ivar uebermittlung_vermoegensverzeichnis:
        :ivar beteiligter_zusatz: Für den im Grunddatensatz angegebenen
            Beteiligten werden weitergehende Informationen übergeben.
        :ivar ergebnis_der_verarbeitung: Hier wird nicht das Ergebnis
            formaler Prüfungen (z.B. Signaturprüfung, Virenprüfung,
            Authentifizierung usw.) mitgeteilt.
        """

        uebermittlung_vermoegensverzeichnis: Optional[
            TypeVstrUebermittlungVermoegensverzeichnis
        ] = field(
            default=None,
            metadata={
                "name": "uebermittlung.vermoegensverzeichnis",
                "type": "Element",
                "required": True,
            },
        )
        beteiligter_zusatz: Optional[TypeVstrBeteiligterZusatz] = field(
            default=None,
            metadata={
                "name": "beteiligter.zusatz",
                "type": "Element",
                "required": True,
            },
        )
        ergebnis_der_verarbeitung: Optional[
            "NachrichtVstrVermoegensverzeichnisUebermittlungsbestaetigungPortal0900007.Fachdaten.ErgebnisDerVerarbeitung"
        ] = field(
            default=None,
            metadata={
                "name": "ergebnisDerVerarbeitung",
                "type": "Element",
                "required": True,
            },
        )

        @dataclass
        class ErgebnisDerVerarbeitung:
            ergebnis_code: Optional[
                CodeVstrVerarbeitungsergebnisSchuldnerverzeichnis
            ] = field(
                default=None,
                metadata={
                    "name": "ergebnis.code",
                    "type": "Element",
                    "required": True,
                },
            )
            ergebnis_ergaenzender_fehlertext: Optional[str] = field(
                default=None,
                metadata={
                    "name": "ergebnis.ergaenzenderFehlertext",
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )


@dataclass
class NachrichtVstrEntscheidungSchuldnerwiderspruch0900001:
    class Meta:
        name = "nachricht.vstr.entscheidung.schuldnerwiderspruch.0900001"
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
        "NachrichtVstrEntscheidungSchuldnerwiderspruch0900001.Fachdaten"
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
        :ivar entscheidung_schuldnerwiderspruch:
        :ivar beteiligter_zusatz: Für den im Grunddatensatz angegebenen
            Beteiligten werden weitergehende Informationen übergeben.
        """

        entscheidung_schuldnerwiderspruch: Optional[
            TypeVstrEntscheidungSchuldnerwiderspruch
        ] = field(
            default=None,
            metadata={
                "name": "entscheidung.schuldnerwiderspruch",
                "type": "Element",
                "required": True,
            },
        )
        beteiligter_zusatz: Optional[TypeVstrBeteiligterZusatz] = field(
            default=None,
            metadata={
                "name": "beteiligter.zusatz",
                "type": "Element",
                "required": True,
            },
        )


@dataclass
class NachrichtVstrEntscheidungSchuldnerwiderspruchEintragungsbestaetigung0900002:
    class Meta:
        name = "nachricht.vstr.entscheidung.schuldnerwiderspruch.eintragungsbestaetigung.0900002"
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
        "NachrichtVstrEntscheidungSchuldnerwiderspruchEintragungsbestaetigung0900002.Fachdaten"
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
        :ivar entscheidung_schuldnerwiderspruch:
        :ivar beteiligter_zusatz: Für den im Grunddatensatz angegebenen
            Beteiligten werden weitergehende Informationen übergeben.
        :ivar ergebnis_der_verarbeitung: Hier wird nicht das Ergebnis
            formaler Prüfungen (z.B. Signaturprüfung, Virenprüfung,
            Authentifizierung usw.) mitgeteilt.
        """

        entscheidung_schuldnerwiderspruch: Optional[
            TypeVstrEntscheidungSchuldnerwiderspruch
        ] = field(
            default=None,
            metadata={
                "name": "entscheidung.schuldnerwiderspruch",
                "type": "Element",
                "required": True,
            },
        )
        beteiligter_zusatz: Optional[TypeVstrBeteiligterZusatz] = field(
            default=None,
            metadata={
                "name": "beteiligter.zusatz",
                "type": "Element",
                "required": True,
            },
        )
        ergebnis_der_verarbeitung: Optional[
            "NachrichtVstrEntscheidungSchuldnerwiderspruchEintragungsbestaetigung0900002.Fachdaten.ErgebnisDerVerarbeitung"
        ] = field(
            default=None,
            metadata={
                "name": "ergebnisDerVerarbeitung",
                "type": "Element",
                "required": True,
            },
        )

        @dataclass
        class ErgebnisDerVerarbeitung:
            ergebnis_code: Optional[
                CodeVstrVerarbeitungsergebnisSchuldnerverzeichnis
            ] = field(
                default=None,
                metadata={
                    "name": "ergebnis.code",
                    "type": "Element",
                    "required": True,
                },
            )
            ergebnis_ergaenzender_fehlertext: Optional[str] = field(
                default=None,
                metadata={
                    "name": "ergebnis.ergaenzenderFehlertext",
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )


@dataclass
class NachrichtVstrSchuldnerverzeichnisAbdrucke0900005:
    class Meta:
        name = "nachricht.vstr.schuldnerverzeichnis.abdrucke.0900005"
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
        "NachrichtVstrSchuldnerverzeichnisAbdrucke0900005.Fachdaten"
    ] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )

    @dataclass
    class Fachdaten:
        mitteilungsdaten: list[
            "NachrichtVstrSchuldnerverzeichnisAbdrucke0900005.Fachdaten.Mitteilungsdaten"
        ] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            },
        )
        abdruckzeitraum: Optional[
            "NachrichtVstrSchuldnerverzeichnisAbdrucke0900005.Fachdaten.Abdruckzeitraum"
        ] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
            },
        )

        @dataclass
        class Mitteilungsdaten:
            """
            :ivar eintragungsanordnung:
            :ivar verfahrensnummer: In dieser XJustiz-Nachricht wird die
                Verfahrensnummer im Fachdatenbereich und nicht in den
                Grunddaten angegeben!
            :ivar beteiligter_zusatz: Für den im Grunddatensatz
                angegebenen Beteiligten werden weitergehende
                Informationen übergeben.
            """

            eintragungsanordnung: Optional[
                TypeVstrEintragungsanordnungSchuldnerverzeichnisPortal
            ] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "required": True,
                },
            )
            verfahrensnummer: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "required": True,
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|[ʹ-ʺ]|[ʾ-ʿ]|ˈ|ˌ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|’|‡|€|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
            beteiligter_zusatz: Optional[TypeVstrBeteiligterZusatz] = field(
                default=None,
                metadata={
                    "name": "beteiligter.zusatz",
                    "type": "Element",
                    "required": True,
                },
            )

        @dataclass
        class Abdruckzeitraum:
            beginn: Optional[XmlDateTime] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "required": True,
                },
            )
            ende: Optional[XmlDateTime] = field(
                default=None,
                metadata={
                    "type": "Element",
                    "required": True,
                },
            )


@dataclass
class NachrichtVstrSchuldnerverzeichnisEintragungKorrektur0900003:
    class Meta:
        name = (
            "nachricht.vstr.schuldnerverzeichnis.eintragung.korrektur.0900003"
        )
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
        "NachrichtVstrSchuldnerverzeichnisEintragungKorrektur0900003.Fachdaten"
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
        :ivar eintragungsanordnung:
        :ivar beteiligter_zusatz: Für den im Grunddatensatz angegebenen
            Beteiligten werden weitergehende Informationen übergeben.
        """

        eintragungsanordnung: Optional[
            TypeVstrEintragungsanordnungSchuldnerverzeichnis
        ] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
            },
        )
        beteiligter_zusatz: Optional[TypeVstrBeteiligterZusatz] = field(
            default=None,
            metadata={
                "name": "beteiligter.zusatz",
                "type": "Element",
                "required": True,
            },
        )


@dataclass
class NachrichtVstrSchuldnerverzeichnisVerarbeitungsbestaetigungPortal0900004:
    class Meta:
        name = "nachricht.vstr.schuldnerverzeichnis.verarbeitungsbestaetigung.portal.0900004"
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
        "NachrichtVstrSchuldnerverzeichnisVerarbeitungsbestaetigungPortal0900004.Fachdaten"
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
        :ivar eintragungsanordnung:
        :ivar beteiligter_zusatz: Für den im Grunddatensatz angegebenen
            Beteiligten werden weitergehende Informationen übergeben.
        :ivar ergebnis_der_verarbeitung: Hier wird nicht das Ergebnis
            formaler Prüfungen (z.B. Signaturprüfung, Virenprüfung,
            Authentifizierung usw.) mitgeteilt.
        """

        eintragungsanordnung: Optional[
            TypeVstrEintragungsanordnungSchuldnerverzeichnisPortal
        ] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
            },
        )
        beteiligter_zusatz: Optional[TypeVstrBeteiligterZusatz] = field(
            default=None,
            metadata={
                "name": "beteiligter.zusatz",
                "type": "Element",
                "required": True,
            },
        )
        ergebnis_der_verarbeitung: Optional[
            "NachrichtVstrSchuldnerverzeichnisVerarbeitungsbestaetigungPortal0900004.Fachdaten.ErgebnisDerVerarbeitung"
        ] = field(
            default=None,
            metadata={
                "name": "ergebnisDerVerarbeitung",
                "type": "Element",
                "required": True,
            },
        )

        @dataclass
        class ErgebnisDerVerarbeitung:
            ergebnis_code: Optional[
                CodeVstrVerarbeitungsergebnisSchuldnerverzeichnis
            ] = field(
                default=None,
                metadata={
                    "name": "ergebnis.code",
                    "type": "Element",
                    "required": True,
                },
            )
            ergebnis_ergaenzender_fehlertext: Optional[str] = field(
                default=None,
                metadata={
                    "name": "ergebnis.ergaenzenderFehlertext",
                    "type": "Element",
                    "pattern": r"([\t-\n]|\r|[ -~]|[\xa0-¬]|[®-ž]|[Ƈ-ƈ]|Ə|ƒ|Ɨ|[Ơ-ơ]|[Ư-ư]|Ʒ|[Ǎ-ǜ]|[Ǟ-ǟ]|[Ǣ-ǰ]|[Ǵ-ǵ]|[Ǹ-ǿ]|[Ȓ-ȓ]|[Ș-ț]|[Ȟ-ȟ]|[ȧ-ȳ]|ə|ɨ|ʒ|ʰ|ʳ|[ʹ-ʺ]|[ʾ-ʿ]|ˆ|ˈ|ˌ|˜|ˢ|Ά|[Έ-Ί]|Ό|[Ύ-Ρ]|[Σ-ώ]|Ѝ|[А-Ъ]|Ь|[Ю-ъ]|ь|[ю-я]|ѝ|ᵈ|ᵗ|[Ḃ-ḃ]|[Ḇ-ḇ]|[Ḋ-ḑ]|ḗ|[Ḝ-ḫ]|[ḯ-ḷ]|[Ḻ-ḻ]|[Ṁ-ṉ]|[Ṓ-ṛ]|[Ṟ-ṣ]|[Ṫ-ṯ]|[Ẁ-ẇ]|[Ẍ-ẗ]|ẞ|[Ạ-ỹ]|[‘-‚]|[“-„]|[†-‡]|…|‰|[′-″]|[‹-›]|⁰|[⁴-⁹]|[ⁿ-₉]|€|™|∞|[≤-≥]|A̋|C(̀|̄|̆|̈|̕|̣|̦|̨̆)|D̂|F(̀|̄)|G̀|H(̄|̦|̱)|J(́|̌)|K(̀|̂|̄|̇|̕|̛|̦|͟H|͟h)|L(̂|̥|̥̄|̦)|M(̀|̂|̆|̐)|N(̂|̄|̆|̦)|P(̀|̄|̕|̣)|R(̆|̥|̥̄)|S(̀|̄|̛̄|̱)|T(̀|̄|̈|̕|̛)|U̇|Z(̀|̄|̆|̈|̧)|a̋|c(̀|̄|̆|̈|̕|̣|̦|̨̆)|d̂|f(̀|̄)|g̀|h(̄|̦)|j́|k(̀|̂|̄|̇|̕|̛|̦|͟h)|l(̂|̥|̥̄|̦)|m(̀|̂|̆|̐)|n(̂|̄|̆|̦)|p(̀|̄|̕|̣)|r(̆|̥|̥̄)|s(̀|̄|̛̄|̱)|t(̀|̄|̕|̛)|u̇|z(̀|̄|̆|̈|̧)|Ç̆|Û̄|ç̆|û̄|ÿ́|Č(̕|̣)|č(̕|̣)|ē̍|Ī́|ī́|ō̍|Ž(̦|̧)|ž(̦|̧)|Ḳ̄|ḳ̄|Ṣ̄|ṣ̄|Ṭ̄|ṭ̄|Ạ̈|ạ̈|Ọ̈|ọ̈|Ụ(̄|̈)|ụ(̄|̈))*",
                },
            )
