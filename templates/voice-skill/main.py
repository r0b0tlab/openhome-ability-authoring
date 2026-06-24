import json
from src.agent.capability import MatchingCapability
from src.main import AgentWorker
from src.agent.capability_worker import CapabilityWorker

TITLE = "Voice Skill Starter"
EXIT_WORDS = (
    "done", "exit", "stop", "quit", "bye", "goodbye",
    "never mind", "cancel", "no thanks", "nothing else",
)
SYSTEM_PROMPT = """
You are the spoken response layer for an OpenHome Ability.
Return one or two natural spoken sentences.
No markdown, no lists, no raw JSON, no code blocks.
If the request needs real integration, explain the next action briefly.
""".strip()


class VoiceSkillStarterCapability(MatchingCapability):
    worker: AgentWorker = None
    capability_worker: CapabilityWorker = None

    #{{register capability}}

    def call(self, worker: AgentWorker):
        self.worker = worker
        self.capability_worker = CapabilityWorker(self.worker)
        self.worker.session_tasks.create(self.run())

    async def run(self):
        try:
            user_input = self.get_trigger_context()
            if not user_input:
                user_input = await self.capability_worker.run_io_loop(
                    "What should I help with?"
                )

            if self.is_exit(user_input):
                await self.capability_worker.speak("Okay, handing you back.")
                return

            await self.capability_worker.speak("One sec, checking that.")
            response = self.handle_request(user_input)
            await self.capability_worker.speak(self.clean_for_voice(response))
        except Exception as exc:
            self.worker.editor_logging_handler.error(f"{TITLE} failed: {exc}")
            await self.capability_worker.speak(
                "Something went wrong. Check the ability logs."
            )
        finally:
            self.capability_worker.resume_normal_flow()

    def get_trigger_context(self) -> str:
        try:
            history = self.capability_worker.get_full_message_history() or []
        except Exception as exc:
            self.worker.editor_logging_handler.warning(
                f"Could not read message history: {exc}"
            )
            return ""

        for item in reversed(history):
            if item.get("role") == "user" and item.get("content"):
                return str(item["content"])
        return ""

    def is_exit(self, user_input: str) -> bool:
        lower = (user_input or "").lower()
        return any(word in lower for word in EXIT_WORDS)

    def handle_request(self, user_input: str) -> str:
        """Replace this method with API, DevKit, file, or workflow logic."""
        prompt = (
            f"Ability: {TITLE}
"
            f"User request: {user_input}
"
            "Draft the next spoken response."
        )
        return self.capability_worker.text_to_text_response(
            prompt,
            history=[],
            system_prompt=SYSTEM_PROMPT,
        )

    def clean_for_voice(self, text: str) -> str:
        cleaned = (text or "").replace("```json", "").replace("```", "").strip()
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                for key in ("spoken", "message", "response", "answer"):
                    if parsed.get(key):
                        cleaned = str(parsed[key])
                        break
        except json.JSONDecodeError:
            pass
        return " ".join(cleaned.split())[:500] or "Done."
