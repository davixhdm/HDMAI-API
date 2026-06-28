from typing import Dict, Any, Optional
from services.ai_service import ai_service

class WidgetChatService:
    MAX_HISTORY = 15

    async def chat(self, source: str, message: str, messages: Optional[list] = None, user_id: Optional[str] = None, context: Optional[dict] = None, data: Optional[dict] = None) -> Dict[str, Any]:
        history = messages or []
        history.append({"role": "user", "content": message})

        system = self._build_system_prompt(source, context, data)
        history.insert(0, {"role": "system", "content": system})

        result = await ai_service.groq_chat(history, max_tokens=800, module="widget")
        reply = result.get("reply", "Sorry, I couldn't process that.")

        return {"reply": reply, "source": source, "tokens_used": result.get("tokens_used", 0)}

    def _build_system_prompt(self, source: str, context: Optional[dict] = None, data: Optional[dict] = None) -> str:
        system_prompts = {
            "docusoft": "You are DocuSoft AI. Help with documents, pricing, and purchases.",
            "hdm_portfolio": "You are HDM Portfolio AI. Answer questions about our company, services, apps, and projects."
        }
        system = system_prompts.get(source, system_prompts["hdm_portfolio"])

        services = (data or {}).get("services") or (context or {}).get("services")
        apps = (data or {}).get("apps") or (context or {}).get("apps")
        projects = (data or {}).get("projects") or (context or {}).get("projects")
        company = (data or {}).get("company") or (context or {}).get("company")
        social = (data or {}).get("socialLinks") or (context or {}).get("socialLinks")

        parts = ["\n\nAnswer questions using ONLY the information provided below. Do NOT invent anything."]

        if apps:
            parts.append("\nOUR APPS:")
            for a in apps:
                parts.append(f"  • {a.get('name','')}: {a.get('description','')}")
            parts.append("\nWhen asked about apps, list all apps above.")

        if services:
            parts.append("\nOUR SERVICES:")
            for s in services:
                name = s.get("title") or s.get("name", "")
                desc = s.get("description", "")
                parts.append(f"  • {name}: {desc}" if desc else f"  • {name}")

        if projects:
            parts.append("\nOUR PROJECTS:")
            for p in projects:
                parts.append(f"  • {p.get('name','')}: {p.get('description','')}")

        if company:
            parts.append(f"\nCOMPANY: {company.get('name','')} | {company.get('email','')} | {company.get('phone','')}")

        if social:
            parts.append(f"\nLINKS: {', '.join(social.keys())}")

        system += "\n".join(parts)

        return system

widget_chat_service = WidgetChatService()