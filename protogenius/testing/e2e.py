"""Playwright E2E generator.

§6.1 requires browser E2E coverage "when applicable". The generator emits a
``playwright.config.ts`` and one ``*.spec.ts`` file per E2E case; the runner
is left to the project's CI configuration (see ``ci_generator.py``).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .spec_layer import TestSpec


@dataclass
class PlaywrightE2EGenerator:
    base_url: str = "http://localhost:3000"

    def materialize(self, spec: TestSpec, target_dir: Path) -> list[Path]:
        target_dir.mkdir(parents=True, exist_ok=True)
        config_path = target_dir / "playwright.config.ts"
        config_path.write_text(
            'import { defineConfig } from "@playwright/test";\n'
            "\n"
            "export default defineConfig({\n"
            f'  testDir: "./e2e",\n'
            f'  use: {{ baseURL: "{self.base_url}", headless: true }},\n'
            "  reporter: [['list'], ['junit', { outputFile: 'reports/e2e.junit.xml' }]],\n"
            "});\n",
            encoding="utf-8",
        )
        spec_dir = target_dir / "e2e"
        spec_dir.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = [config_path]
        for case in spec.cases:
            if case.kind != "e2e":
                continue
            spec_path = spec_dir / f"{_safe(case.id)}.spec.ts"
            spec_path.write_text(self._render(case.id, case.steps, case.expected), encoding="utf-8")
            paths.append(spec_path)
        return paths

    def _render(self, case_id: str, steps: list[str], expected: str) -> str:
        steps_md = "\n".join(f"  // step: {s}" for s in steps)
        return (
            'import { test, expect } from "@playwright/test";\n\n'
            f'test("{case_id}", async ({{ page }}) => {{\n'
            f'  await page.goto("/");\n'
            f"{steps_md}\n"
            f"  // expected: {expected}\n"
            f"  await expect(page).toHaveTitle(/.+/);\n"
            "});\n"
        )


def _safe(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in value).lower().strip("-")
