from __future__ import annotations

from dataclasses import dataclass, field

from app.generation.pipeline import ProjectPlan, StructuredRequirements


@dataclass
class FolderPlan:
    """SDD §9 — complete React project folder structure."""

    directories: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"directories": self.directories, "files": self.files}


class FolderPlanner:
    STANDARD_DIRS = [
        "src/components",
        "src/pages",
        "src/hooks",
        "src/assets",
        "src/services",
    ]

    def plan(self, requirements: StructuredRequirements, project_plan: ProjectPlan) -> FolderPlan:
        dirs = list(self.STANDARD_DIRS)
        files = list(project_plan.files)

        for comp in requirements.analysis.components:
            path = f"src/components/{comp}.tsx"
            if path not in files:
                files.append(path)

        for required in ("Navbar", "Hero", "Footer", "Button", "Card"):
            path = f"src/components/{required}.tsx"
            if path not in files:
                files.append(path)

        files.extend(
            [
                "src/hooks/useTheme.ts",
                "src/services/api.ts",
                "src/assets/.gitkeep",
            ]
        )

        return FolderPlan(directories=dirs, files=sorted(set(files)))
