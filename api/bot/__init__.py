import os
from pathlib import Path

import anthropic
import yaml

MODEL = "claude-sonnet-5"

DEFAULT_SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / ".claude" / "skills"


def _skills_dir() -> Path:
    override = os.environ.get("SKILLS_DIR")
    return Path(override) if override else DEFAULT_SKILLS_DIR


def _parse_skill(path: Path) -> dict:
    text = path.read_text()
    if text.startswith("---"):
        _, frontmatter, body = text.split("---", 2)
        meta = yaml.safe_load(frontmatter) or {}
    else:
        meta, body = {}, text
    return {
        "name": path.parent.name,
        "description": (meta.get("description") or "").strip(),
        "instructions": body.strip(),
    }


def _load_skills() -> list[dict]:
    skills_dir = _skills_dir()
    if not skills_dir.is_dir():
        return []
    return [_parse_skill(path) for path in sorted(skills_dir.glob("*/SKILL.md"))]


def _build_system_prompt(skills: list[dict]) -> str:
    if not skills:
        return "You are a helpful assistant."

    sections = ["You are a helpful assistant with access to the following skills:"]
    for skill in skills:
        sections.append(
            f"\n## Skill: {skill['name']}\n{skill['description']}\n\n{skill['instructions']}"
        )
    return "\n".join(sections)


def _build_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")
    return anthropic.Anthropic(api_key=api_key)


def run_chat() -> None:
    """Interactive REPL that keeps asking the user for questions and forwards them to Claude."""
    client = _build_client()
    skills = _load_skills()
    system_prompt = _build_system_prompt(skills)
    messages: list[dict] = []

    print(f"Chat with {MODEL}. Type 'exit' or 'quit' to stop.")
    if skills:
        print(f"Loaded skills: {', '.join(skill['name'] for skill in skills)}")
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        messages.append({"role": "user", "content": user_input})

        print("Claude: ", end="", flush=True)
        try:
            with client.messages.stream(
                model=MODEL,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                response = stream.get_final_message()
        except anthropic.APIError as e:
            print(f"\n[error contacting Claude: {e}]")
            messages.pop()
            continue

        print()
        reply_text = next(
            (block.text for block in response.content if block.type == "text"), ""
        )
        messages.append({"role": "assistant", "content": reply_text})
