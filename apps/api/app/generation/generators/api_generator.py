from app.generation.pipeline import GeneratedFile, StructuredRequirements


class ApiGenerator:
    """SDD §7 API Generator — axios service layer for generated projects."""

    def generate(self, requirements: StructuredRequirements) -> list[GeneratedFile]:
        base_url = "/api"
        return [
            GeneratedFile(
                path="src/services/api.ts",
                content=(
                    "import axios from 'axios'\n\n"
                    f"export const api = axios.create({{\n"
                    f"  baseURL: '{base_url}',\n"
                    "  timeout: 10000,\n"
                    "  headers: { 'Content-Type': 'application/json' },\n"
                    "})\n\n"
                    "export async function fetchHealth() {\n"
                    "  const { data } = await api.get('/health')\n"
                    "  return data\n"
                    "}\n\n"
                    "export async function submitContact(payload: { name: string; email: string; message: string }) {\n"
                    "  // Placeholder — wire to your backend when deployed\n"
                    "  return { ok: true, payload }\n"
                    "}\n"
                ),
            ),
            GeneratedFile(
                path="src/assets/.gitkeep",
                content="",
            ),
        ]
