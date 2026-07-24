from app.generation.pipeline import ProjectPlan, StructuredRequirements


class ProjectPlanner:
    def plan(self, requirements: StructuredRequirements, project_name: str) -> ProjectPlan:
        analysis = requirements.analysis
        pages = list(analysis.pages)
        if getattr(analysis, "layout", "multi_page") == "single_page":
            pages = ["Home"]

        type_id = (getattr(analysis, "website_type_id", "") or "").lower()
        prompt = (getattr(analysis, "raw_prompt", "") or "").lower()
        is_blog = (
            "blog" in type_id
            or "magazine" in type_id
            or "seo blog" in prompt
            or "seo website" in prompt
        )
        # Collapse Blog ↔ Articles so nav isn't duplicated
        if is_blog:
            lower_pages = {p.lower() for p in pages}
            if "articles" in lower_pages and "blog" in lower_pages:
                pages = [p for p in pages if p.lower() != "blog"]

        # Clothing + auth: only expand when user did not specify exact pages
        is_clothing = (
            "cloth" in type_id
            or "fashion" in type_id
            or "apparel" in prompt
            or "clothing" in prompt
            or "fashion" in prompt
        )
        pages_explicit = bool(getattr(analysis, "pages_explicit", False))
        if is_clothing and not pages_explicit:
            for extra in ("Shop", "Lookbook", "About", "Contact"):
                if extra not in pages:
                    pages.append(extra)
            if any(k in prompt for k in ("sign in", "sign up", "login", "register", "signup", "signin")):
                for extra in ("Login", "Register"):
                    if extra not in pages:
                        pages.append(extra)

        # Bookstore commerce IA when prompt didn't lock exact pages
        is_bookstore = (
            "book" in type_id
            or "bookstore" in type_id
            or "book store" in prompt
            or "bookstore" in prompt
            or ("book" in prompt and any(w in prompt for w in ("buy", "read", "pdf", "download", "search")))
        )
        if is_bookstore and not pages_explicit:
            for extra in ("Browse", "Library", "Cart", "About"):
                if extra not in pages:
                    pages.append(extra)

        routes = []
        for page in pages:
            slug = "/" if page.lower() == "home" else "/" + page.lower().replace(" ", "-")
            component = page.replace(" ", "") + "Page"
            if page.lower() == "home":
                component = "HomePage"
            routes.append({"path": slug, "page": page, "component": component})

        # Blog / magazine: Article detail via HashRouter `#/article?slug=...`
        if is_blog and not any(r.get("path") == "/article" for r in routes):
            routes.append({"path": "/article", "page": "Article", "component": "ArticlePage"})

        files = [
            "package.json",
            "index.html",
            "vite.config.ts",
            "tsconfig.json",
            "src/main.tsx",
            "src/App.tsx",
            "src/index.css",
            "src/components/Navbar.tsx",
            "src/components/Hero.tsx",
            "src/components/Footer.tsx",
            "src/components/Button.tsx",
            "src/components/Card.tsx",
            "src/hooks/useTheme.ts",
            "src/services/api.ts",
            "src/assets/.gitkeep",
            "preview.html",
            "README.md",
        ]
        for comp in analysis.components:
            path = f"src/components/{comp}.tsx"
            if path not in files:
                files.append(path)
        for route in routes:
            files.append(f"src/pages/{route['component']}.tsx")

        return ProjectPlan(
            project_name=project_name,
            routes=routes,
            files=files,
            stack={
                "framework": "react",
                "bundler": "vite",
                "language": "typescript",
                "styling": "tailwindcss",
                "routing": "react-router-dom",
            },
        )
