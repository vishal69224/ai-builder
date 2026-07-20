from app.generation.pipeline import GeneratedFile, ProjectPlan


class RouterGenerator:
    """SDD §12 Routing Generator — React Router pages."""

    def generate(self, plan: ProjectPlan) -> list[GeneratedFile]:
        imports = "\n".join(
            f"import {r['component']} from './pages/{r['component']}'" for r in plan.routes
        )
        routes = "\n".join(
            f'          <Route path="{r["path"]}" element={{<{r["component"]} />}} />'
            for r in plan.routes
        )
        return [
            GeneratedFile(
                path="src/main.tsx",
                content=(
                    "import { StrictMode } from 'react'\n"
                    "import { createRoot } from 'react-dom/client'\n"
                    "import { HashRouter } from 'react-router-dom'\n"
                    "import App from './App'\n"
                    "import './index.css'\n\n"
                    "createRoot(document.getElementById('root')!).render(\n"
                    "  <StrictMode>\n"
                    "    <HashRouter>\n"
                    "      <App />\n"
                    "    </HashRouter>\n"
                    "  </StrictMode>,\n"
                    ")\n"
                ),
            ),
            GeneratedFile(
                path="src/App.tsx",
                content=(
                    "import { Route, Routes } from 'react-router-dom'\n"
                    "import { Footer } from './components/Footer'\n"
                    "import { Navbar } from './components/Navbar'\n"
                    "import { useTheme } from './hooks/useTheme'\n"
                    f"{imports}\n\n"
                    "export default function App() {\n"
                    "  useTheme()\n"
                    "  return (\n"
                    "    <div className=\"flex min-h-screen flex-col\">\n"
                    "      <Navbar />\n"
                    "      <main className=\"flex-1\">\n"
                    "        <Routes>\n"
                    f"{routes}\n"
                    "        </Routes>\n"
                    "      </main>\n"
                    "      <Footer />\n"
                    "    </div>\n"
                    "  )\n"
                    "}\n"
                ),
            ),
        ]
