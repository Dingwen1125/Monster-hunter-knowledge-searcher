"""Create a small Monster Hunter knowledge-base PDF for the RAG demo.

The PDF writer is intentionally dependency-free so the knowledge base can be
created before installing the RAG stack.
"""

from __future__ import annotations

from pathlib import Path
import textwrap


KB_DIR = Path("knowledge_base")
PDF_PATH = KB_DIR / "monster_hunter_field_guide.pdf"

PAGES = [
    {
        "title": "Monster Hunter Field Guide: Hunting Fundamentals",
        "body": """
        Monster Hunter is an action hunting series about preparing for large
        monsters, reading their behavior, and converting openings into damage.
        A successful hunt is usually won before the first attack lands: eat a
        meal, bring healing items, carry traps when capture is allowed, sharpen
        or reload before combat, and choose armor skills that support the weapon.

        The core loop is observe, adapt, punish, and recover. Monsters telegraph
        attacks through posture, roars, turns, wing beats, tail lifts, and breath
        animations. New hunters should value survival skills, positioning, and
        item timing over risky damage windows. When a monster is enraged it often
        becomes faster and more dangerous, but it may also be more predictable.
        """,
    },
    {
        "title": "Weapon Roles and Practical Advice",
        "body": """
        Great Sword rewards patience, draw attacks, and precise charged hits.
        Long Sword builds Spirit Gauge and uses counters to stay aggressive.
        Sword and Shield is flexible, can use items quickly, and teaches safe
        fundamentals. Dual Blades trade reach for mobility and elemental damage.
        Hammer focuses on blunt head damage and knockouts. Lance and Gunlance
        favor blocking, counters, and steady pressure.

        Bow, Light Bowgun, and Heavy Bowgun require attention to distance,
        ammo or coatings, and monster hit zones. Hunting Horn supports the team
        with melodies while still dealing blunt damage. Charge Blade and Switch
        Axe have resource systems; they are powerful when the hunter understands
        when to store, spend, and reposition.
        """,
    },
    {
        "title": "Monsters, Weaknesses, and Captures",
        "body": """
        Rathalos is a flying wyvern known for fireballs, poison talons, and air
        pressure. Flash effects, careful anti-air timing, and cutting the tail
        can make the fight safer. Diablos charges, burrows, and punishes hunters
        standing in front of it; sonic effects can expose it while underground.
        Zinogre charges electricity and becomes more threatening when powered up.

        Capturing usually requires weakening the monster, placing a trap, and
        using tranquilizers. Capture can end a hunt faster and often changes the
        reward table. Cutting tails, breaking horns, breaking wings, or damaging
        claws can unlock additional materials. Always check the target monster's
        elemental weakness and weak hit zones before choosing a weapon setup.
        """,
    },
    {
        "title": "Team Play and Quest Strategy",
        "body": """
        In multiplayer, spacing matters. A Hammer user wants the head, blade
        weapons often want tails or weak sever zones, and ranged hunters should
        avoid dragging the monster away from teammates. Lifepowder, Dust of Life,
        traps, endemic life, and environmental hazards can save a difficult hunt.

        If a hunt is failing, reduce greed. Heal earlier, stop attacking during
        unknown animations, and watch the monster for a full pattern cycle.
        Upgrade armor with spheres, bring nullberries for elemental blights, and
        use mantles or defensive tools during the most dangerous phase. Good
        hunters do not simply memorize combos; they manage risk.

        If you are dying, fainting, or carting repeatedly, retreat and reset the
        fight instead of forcing damage. Sheathe your weapon, sprint away, heal
        with potions or max potions, remove blights with nullberries, sharpen in
        a safe area, and wait for the monster to finish an attack before
        re-engaging. A struggling hunter should prioritize staying alive over
        finishing a combo.
        """,
    },
]


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _page_stream(title: str, body: str) -> bytes:
    lines = [title, ""]
    for paragraph in textwrap.dedent(body).strip().split("\n\n"):
        lines.extend(textwrap.wrap(" ".join(paragraph.split()), width=86))
        lines.append("")

    commands = ["BT", "/F1 15 Tf", "72 750 Td", "18 TL"]
    first = True
    for line in lines:
        if first:
            first = False
        else:
            commands.append("T*")
        commands.append(f"({_escape_pdf_text(line)}) Tj")
    commands.append("ET")
    return "\n".join(commands).encode("ascii")


def create_pdf(path: Path = PDF_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"",  # filled after page object numbers are known
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    page_object_numbers = []
    for page in PAGES:
        stream = _page_stream(page["title"], page["body"])
        content_number = len(objects) + 2
        page_object_numbers.append(len(objects) + 1)
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 3 0 R >> >> "
                f"/Contents {content_number} 0 R >>"
            ).encode("ascii")
        )
        objects.append(
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )

    kids = " ".join(f"{number} 0 R" for number in page_object_numbers)
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_object_numbers)} >>".encode(
        "ascii"
    )

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )

    path.write_bytes(pdf)
    return path


if __name__ == "__main__":
    print(f"Created {create_pdf()}")
