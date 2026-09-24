import re

from app.generation.pipeline import GeneratedFile, ProjectPlan


REQUIRED_PATHS = {
    "package.json",
    "index.html",
    "src/main.tsx",
    "src/App.tsx",
    "src/index.css",
    "src/components/Navbar.tsx",
    "src/components/Hero.tsx",
    "src/components/Footer.tsx",
}


class GenerationValidator:
    """SDD §13 — JSX, imports, duplicates, routes, build readiness."""

    def validate(self, files: list[GeneratedFile], plan: ProjectPlan, *, skip_routes: bool = False) -> dict:
        paths = {f.path for f in files}
        path_list = [f.path for f in files]
        missing = sorted(REQUIRED_PATHS - paths)
        empty = [f.path for f in files if not f.content.strip() and not f.path.endswith(".gitkeep")]
        escaped = [f.path for f in files if ".." in f.path or f.path.startswith("/")]

        duplicates = sorted({p for p in path_list if path_list.count(p) > 1})
        jsx_errors = self._check_jsx(files)
        import_errors = self._check_imports(files)
        # Edit/revert must not re-plan routes from a vague follow-up prompt
        route_errors = [] if skip_routes else self._check_routes(files, plan)

        ok = (
            not missing
            and not empty
            and not escaped
            and not duplicates
            and not jsx_errors
            and not import_errors
            and not route_errors
        )

        return {
            "ok": ok,
            "file_count": len(files),
            "missing_required": missing,
            "empty_files": empty,
            "invalid_paths": escaped,
            "duplicate_files": duplicates,
            "jsx_errors": jsx_errors,
            "import_errors": import_errors,
            "route_errors": route_errors,
            "planned_files": len(plan.files),
        }

    def _check_jsx(self, files: list[GeneratedFile]) -> list[str]:
        errors: list[str] = []
        for f in files:
            if not f.path.endswith((".tsx", ".jsx")):
                continue
            opens = f.content.count("<") - f.content.count("</") - f.content.count("/>")
            if "export default function" in f.content and f.content.count("return (") == 0 and f.content.count("return(") == 0:
                if "return" not in f.content:
                    errors.append(f"{f.path}: missing return in component")
            if f.content.count("{") != f.content.count("}"):
                errors.append(f"{f.path}: unbalanced braces")
        return errors[:10]

    def _check_imports(self, files: list[GeneratedFile]) -> list[str]:
        errors: list[str] = []
        available = {f.path for f in files}
        for f in files:
            if not f.path.endswith((".tsx", ".ts")):
                continue
            for match in re.finditer(r"from ['\"](\\.\\.?/[^'\"]+)['\"]", f.content):
                rel = match.group(1)
                if rel.startswith("."):
                    base = f.path.rsplit("/", 1)[0]
                    target = self._resolve_import(base, rel)
                    candidates = [target, target + ".tsx", target + ".ts", target + "/index.tsx"]
                    if not any(c in available for c in candidates):
                        errors.append(f"{f.path}: unresolved import {rel}")
        return errors[:10]

    def _resolve_import(self, base: str, rel: str) -> str:
        parts = (base + "/" + rel).replace("\\", "/").split("/")
        stack: list[str] = []
        for p in parts:
            if p == "..":
                if stack:
                    stack.pop()
            elif p != "." and p:
                stack.append(p)
        return "/".join(stack)

    def _check_routes(self, files: list[GeneratedFile], plan: ProjectPlan) -> list[str]:
        app = next((f for f in files if f.path == "src/App.tsx"), None)
        if app is None:
            return ["src/App.tsx missing for route validation"]
        errors: list[str] = []
        for route in plan.routes:
            comp = route["component"]
            if comp not in app.content:
                errors.append(f"Route component {comp} not referenced in App.tsx")
            page_path = f"src/pages/{comp}.tsx"
            if page_path not in {f.path for f in files}:
                errors.append(f"Missing page file for route {route['path']}")
        return errors
