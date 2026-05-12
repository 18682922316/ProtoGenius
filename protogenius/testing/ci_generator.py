"""GitHub Actions workflow generator.

The generated workflow runs the pytest suite on Linux and Windows, mirroring
the v1 acceptance contract. An optional E2E job (Playwright) is appended
when the test spec contains at least one ``e2e`` case.
"""

from __future__ import annotations

from .spec_layer import TestSpec


def render_github_actions_workflow(spec: TestSpec, *, demo_root_rel: str = "prototype") -> str:
    has_e2e = any(case.kind == "e2e" for case in spec.cases)
    workflow = [
        "name: prototype-ci",
        "",
        "on:",
        "  push:",
        "  pull_request:",
        "",
        "jobs:",
        "  unit:",
        "    strategy:",
        "      matrix:",
        "        os: [ubuntu-latest, windows-latest]",
        "    runs-on: ${{ matrix.os }}",
        "    steps:",
        "      - uses: actions/checkout@v4",
        "      - uses: actions/setup-python@v5",
        "        with: { python-version: '3.11' }",
        "      - name: Install demo deps",
        "        run: |",
        f"          if [ -f {demo_root_rel}/requirements.txt ]; then pip install -r {demo_root_rel}/requirements.txt; fi",
        "          pip install pytest",
        "        shell: bash",
        "      - name: Run generated tests",
        "        run: pytest tests --maxfail=3 --tb=short",
        "        shell: bash",
    ]
    if has_e2e:
        workflow.extend(
            [
                "",
                "  e2e:",
                "    runs-on: ubuntu-latest",
                "    needs: unit",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - uses: actions/setup-node@v4",
                "        with: { node-version: '20' }",
                "      - name: Install Playwright",
                "        run: |",
                "          npm install --save-dev @playwright/test",
                "          npx playwright install --with-deps",
                "      - name: Run E2E",
                "        run: npx playwright test --config tests/playwright.config.ts",
            ]
        )
    return "\n".join(workflow) + "\n"
