"""Templates for the Summarization task."""

import typing as t

from ..data_models import PromptConfig
from ..languages import (
    CS,
    DA,
    DE,
    EN,
    ES,
    ET,
    FI,
    FR,
    IS,
    IT,
    LT,
    LV,
    NB,
    NL,
    NN,
    NO,
    PL,
    PT,
    SV,
)

if t.TYPE_CHECKING:
    from ..data_models import Language

# TODO: Missing Faroese
SUMM_TEMPLATES: dict["Language", PromptConfig] = {
    CS: PromptConfig(
        default_prompt_prefix=("Následující jsou dokumenty s přiloženými souhrny."),
        default_prompt_template=("Dokument: {text}\nSouhrn: {target_text}"),
        default_instruction_prompt=(
            "Dokument: {text}\n\nNapište souhrn výše uvedeného dokumentu."
        ),
        default_prompt_label_mapping=dict(),
    ),
    DA: PromptConfig(
        default_prompt_prefix="Følgende er dokumenter med tilhørende resuméer.",
        default_prompt_template="Dokument: {text}\nResumé: {target_text}",
        default_instruction_prompt="Dokument: {text}\n\nSkriv et resumé af ovenstående "
        "dokument.",
        default_prompt_label_mapping=dict(),
    ),
    DE: PromptConfig(
        default_prompt_prefix="Nachstehend finden Sie Dokumente mit zugehörigen "
        "Zusammenfassungen.",
        default_prompt_template="Dokument: {text}\nZusammenfassung: {target_text}",
        default_instruction_prompt="Nachrichtenartikel: {text}\n\nSchreiben Sie eine "
        "Zusammenfassung des oben genannten Dokuments.",
        default_prompt_label_mapping=dict(),
    ),
    EN: PromptConfig(
        default_prompt_prefix="The following are documents with accompanying "
        "summaries.",
        default_prompt_template="Document: {text}\nSummary: {target_text}",
        default_instruction_prompt="Document: {text}\n\nWrite a summary of the above "
        "document.",
        default_prompt_label_mapping=dict(),
    ),
    ES: PromptConfig(
        default_prompt_prefix="A continuación se presentan documentos con resúmenes "
        "adjuntos.",
        default_prompt_template="Documento: {text}\nResumen: {target_text}",
        default_instruction_prompt="Documento: {text}\n\n",
        default_prompt_label_mapping=dict(),
    ),
    ET: PromptConfig(
        default_prompt_prefix="Allpool on dokumendid koos kokkuvõtetega.",
        default_prompt_template="Dokument: {text}\nKokkuvõte: {target_text}",
        default_instruction_prompt="Dokument: {text}\n\nKoosta ülaltoodud dokumendi "
        "kokkuvõte.",
        default_prompt_label_mapping=dict(),
    ),
    PT: PromptConfig(
        default_prompt_prefix="Abaixo encontras documentos com resumos associados.",
        default_prompt_template="Documento: {text}\nResumo: {target_text}",
        default_instruction_prompt="Documento: {text}\n\nEscreve um resumo do "
        "documento anterior.",
        default_prompt_label_mapping=dict(),
    ),
    FI: PromptConfig(
        default_prompt_prefix="Seuraavassa on artikkeleita ja niihin liittyviä "
        "tiivistelmiä.",
        default_prompt_template="Uutisartikkeli: {text}\nTiivistelmä: {target_text}",
        default_instruction_prompt="Uutisartikkeli: {text}\n\nKirjoita tiivistelmä "
        "yllä olevasta artikkelista.",
        default_prompt_label_mapping=dict(),
    ),
    FR: PromptConfig(
        default_prompt_prefix="Les documents suivants sont accompagnés d'un résumé.",
        default_prompt_template="Document: {text}\nRésumé: {target_text}",
        default_instruction_prompt="Document: {text}\n\nRédigez un résumé du "
        "document ci-dessus.",
        default_prompt_label_mapping=dict(),
    ),
    LV: PromptConfig(
        default_prompt_prefix="Tālāk ir dokumenti ar pievienotām kopsavilkumiem.",
        default_prompt_template="Dokuments: {text}\nKopsavilkums: {target_text}",
        default_instruction_prompt=(
            "Dokuments: {text}\n\n"
            "Uzrakstiet kopsavilkumu par iepriekš minēto dokumentu."
        ),
        default_prompt_label_mapping=dict(),
    ),
    LT: PromptConfig(
        default_prompt_prefix=(
            "Žemiau pateikiami dokumentai su pridėtomis santraukomis."
        ),
        default_prompt_template=("Dokumentas: {text}\nSantrauka: {target_text}"),
        default_instruction_prompt=(
            "Dokumentas: {text}\n\nParašykite aukščiau pateikto dokumento santrauką."
        ),
        default_prompt_label_mapping=dict(),
    ),
    IT: PromptConfig(
        default_prompt_prefix="Di seguito sono riportati i documenti con le relative "
        "sintesi.",
        default_prompt_template="Documento: {text}\nSintesi: {target_text}",
        default_instruction_prompt="Documento: {text}\n\nScrivete una sintesi del "
        "documento di cui sopra.",
        default_prompt_label_mapping=dict(),
    ),
    IS: PromptConfig(
        default_prompt_prefix="Eftirfarandi eru skjöl með meðfylgjandi samantektum.",
        default_prompt_template="Skjal: {text}\nSamantekt: {target_text}",
        default_instruction_prompt="Skjal: {text}\n\nSkrifaðu samantekt á ofangreindu "
        "skjali.",
        default_prompt_label_mapping=dict(),
    ),
    NB: PromptConfig(
        default_prompt_prefix="Nedenfor følger dokumenter med tilhørende sammendrag.",
        default_prompt_template="Dokument: {text}\nSammendrag: {target_text}",
        default_instruction_prompt="Dokument: {text}\n\nSkriv et sammendrag av "
        "dokumentet ovenfor.",
        default_prompt_label_mapping=dict(),
    ),
    NL: PromptConfig(
        default_prompt_prefix="Hieronder volgen documenten met bijbehorende "
        "samenvattingen.",
        default_prompt_template="Document: {text}\nSamenvatting: {target_text}",
        default_instruction_prompt="Document: {text}\n\nSchrijf een samenvatting van "
        "het bovenstaande document.",
        default_prompt_label_mapping=dict(),
    ),
    NN: PromptConfig(
        default_prompt_prefix="Nedenfor følger dokumenter med tilhørende sammendrag.",
        default_prompt_template="Dokument: {text}\nSammendrag: {target_text}",
        default_instruction_prompt="Dokument: {text}\n\nSkriv et sammendrag av "
        "dokumentet ovenfor.",
        default_prompt_label_mapping=dict(),
    ),
    NO: PromptConfig(
        default_prompt_prefix="Nedenfor følger dokumenter med tilhørende sammendrag.",
        default_prompt_template="Dokument: {text}\nSammendrag: {target_text}",
        default_instruction_prompt="Dokument: {text}\n\nSkriv et sammendrag av "
        "dokumentet ovenfor.",
        default_prompt_label_mapping=dict(),
    ),
    PL: PromptConfig(
        default_prompt_prefix="Poniżej znajdują się artykuły z towarzyszącymi "
        "im streszczeniami.",
        default_prompt_template="Artykuł: {text}\nStreszczenie: {target_text}",
        default_instruction_prompt="Artykuł: {text}\n\nNapisz streszczenie "
        "powyższego artykułu.",
        default_prompt_label_mapping=dict(),
    ),
    SV: PromptConfig(
        default_prompt_prefix="Nedan följer dokument med tillhörande sammanfattningar.",
        default_prompt_template="Dokument: {text}\nSammanfattning: {target_text}",
        default_instruction_prompt="Dokument: {text}\n\nSkriv en sammanfattning av "
        "ovanstående dokument.",
        default_prompt_label_mapping=dict(),
    ),
}
