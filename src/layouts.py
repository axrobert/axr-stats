"""Generate a paste-ready GitHub README fragment for selected AXR Stats cards.

Layout controls the *README arrangement*, not the SVG's native geometry.
All paths are relative to the consuming repository, never absolute secrets.
"""
from __future__ import annotations
from pathlib import Path
from html import escape
from urllib.parse import quote

from config import CARD_IDS, LAYOUTS, SIZES

CARD_LABELS = {
    "lifetime": "Tempo total e progressão",
    "languages": "Linguagens",
    "activity": "Atividade diária",
    "ranking": "Ranking público WakaTime",
    "heatmap": "Calendário de atividade",
    "emblem": "Emblema do rank",
}
CARD_WIDTHS = {"compact": 500, "standard": 700, "large": 850}
PAIRED_WIDTHS = {"compact": 250, "standard": 350, "large": 420}


def selected_files(cards) -> tuple[str, ...]:
    """Published outputs; SVG and PNG from the requested cards only."""
    selection = set(cards)
    return (tuple(f"{key}.svg" for key in CARD_IDS if key in selection) +
            tuple(f"{key}.png" for key in ("lifetime", "emblem") if key in selection))


def snippet(cards, layout: str, size: str, destination: Path) -> str:
    if layout not in LAYOUTS or size not in SIZES:
        raise ValueError("Unknown layout or size")
    if not cards or len(cards) != len(set(cards)) or any(c not in CARD_IDS for c in cards):
        raise ValueError("Invalid card selection")
    output = Path(destination)
    # Absolute destination paths are used in local integration tests; the user
    # must adjust the prefix if embedding cards outside the repository root.
    prefix = output.as_posix().strip("/") if not output.is_absolute() else output.name
    ordered = [card for card in CARD_IDS if card in cards]

    def image(card, width):
        url = quote(f"{prefix}/{card}.svg", safe="/-._~")
        return (f'<img src="{escape(url, quote=True)}" '
                f'alt="AXR Stats — {escape(CARD_LABELS[card], quote=True)}" '
                f'width="{width}">')

    result = [
        "<!-- AXR Stats: copie este trecho para o README do seu perfil. -->",
        "<!-- Referências relativas à raiz do repositório; nenhum dado é fictício aqui. -->",
    ]
    if layout == "stacked":
        for card in ordered:
            result.append(f'<p align="center">{image(card, CARD_WIDTHS[size])}</p>')
    else:
        result.append("<table>")
        for index in range(0, len(ordered), 2):
            result.append("<tr>")
            for card in ordered[index:index+2]:
                result.append(f'<td align="center">{image(card, PAIRED_WIDTHS[size])}</td>')
            result.append("</tr>")
        result.append("</table>")
    return "\n".join(result) + "\n"
