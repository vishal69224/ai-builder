from app.generation.pipeline import GeneratedFile, ProjectPlan, StructuredRequirements


class ReactGenerator:
    def generate(
        self, requirements: StructuredRequirements, plan: ProjectPlan
    ) -> list[GeneratedFile]:
        analysis = requirements.analysis
        files: list[GeneratedFile] = []
        title = plan.project_name
        prompt_excerpt = _clean(analysis.raw_prompt[:220])

        files.append(
            GeneratedFile(
                path="src/main.tsx",
                content=(
                    "import { StrictMode } from 'react'\n"
                    "import { createRoot } from 'react-dom/client'\n"
                    "import { BrowserRouter } from 'react-router-dom'\n"
                    "import App from './App'\n"
                    "import './index.css'\n\n"
                    "createRoot(document.getElementById('root')!).render(\n"
                    "  <StrictMode>\n"
                    "    <BrowserRouter>\n"
                    "      <App />\n"
                    "    </BrowserRouter>\n"
                    "  </StrictMode>,\n"
                    ")\n"
                ),
            )
        )

        link_lines = ",\n".join(
            f'  {{ to: "{r["path"]}", label: "{r["page"]}" }}' for r in plan.routes
        )
        files.append(
            GeneratedFile(
                path="src/components/Navbar.tsx",
                content=(
                    "import { Link, NavLink } from 'react-router-dom'\n\n"
                    f"const links = [\n{link_lines}\n]\n\n"
                    "export function Navbar() {\n"
                    "  return (\n"
                    '    <header className="border-b border-slate-200 bg-white/90 backdrop-blur">\n'
                    '      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">\n'
                    f'        <Link to="/" className="text-lg font-semibold tracking-tight">{title}</Link>\n'
                    '        <nav className="flex flex-wrap gap-3 text-sm">\n'
                    "          {links.map((link) => (\n"
                    "            <NavLink\n"
                    "              key={link.to}\n"
                    "              to={link.to}\n"
                    "              className={({ isActive }) =>\n"
                    "                isActive ? 'font-semibold text-slate-900' : 'text-slate-600 hover:text-slate-900'\n"
                    "              }\n"
                    "            >\n"
                    "              {link.label}\n"
                    "            </NavLink>\n"
                    "          ))}\n"
                    "        </nav>\n"
                    "      </div>\n"
                    "    </header>\n"
                    "  )\n"
                    "}\n"
                ),
            )
        )

        files.append(
            GeneratedFile(
                path="src/components/Footer.tsx",
                content=(
                    "export function Footer() {\n"
                    "  return (\n"
                    '    <footer className="border-t border-slate-200 bg-slate-50">\n'
                    '      <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-8 text-sm text-slate-600 sm:flex-row sm:items-center sm:justify-between">\n'
                    f"        <p>© {{new Date().getFullYear()}} {title}</p>\n"
                    "        <p>Built with React + Tailwind</p>\n"
                    "      </div>\n"
                    "    </footer>\n"
                    "  )\n"
                    "}\n"
                ),
            )
        )

        for route in plan.routes:
            if route["path"] == "/":
                body = (
                    '      <section className="mx-auto flex min-h-[70vh] max-w-6xl flex-col justify-center px-4 py-16">\n'
                    f'        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-teal-700">{analysis.website_type}</p>\n'
                    f'        <h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">{title}</h1>\n'
                    f'        <p className="mt-4 max-w-2xl text-lg text-slate-600">{prompt_excerpt}</p>\n'
                    '        <div className="mt-8">\n'
                    f'          <a href="#contact" className="rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white">{requirements.cta_primary}</a>\n'
                    "        </div>\n"
                    "      </section>"
                )
            else:
                body = (
                    '      <section className="mx-auto max-w-6xl px-4 py-16">\n'
                    f'        <h1 className="text-3xl font-bold tracking-tight">{route["page"]}</h1>\n'
                    f'        <p className="mt-3 max-w-2xl text-slate-600">Placeholder content for the {route["page"]} page of {title}. Tone: {requirements.tone}.</p>\n'
                    "      </section>"
                )
            files.append(
                GeneratedFile(
                    path=f"src/pages/{route['component']}.tsx",
                    content=(
                        f"export default function {route['component']}() {{\n"
                        "  return (\n"
                        "    <>\n"
                        f"{body}\n"
                        "    </>\n"
                        "  )\n"
                        "}\n"
                    ),
                )
            )

        return files


def _clean(text: str) -> str:
    return text.replace("`", "'").replace('"', "'")
