import importlib
from typing import Dict, Any

class AgentTool:
    def __init__(self, domain: str):
        self.domain = domain
        self.slots_module = self._load_module("slots")
        self.checkout_module = self._load_module("checkout")

    def _load_module(self, name: str):
        try:
            module_path = f"app.domains.{self.domain}.{name}"
            return importlib.import_module(module_path)
        except ModuleNotFoundError:
            raise ImportError(f"Module {name} not found for domain '{self.domain}'")

    def extract_slots(self, intent: str, message: str) -> Dict[str, Any]:
        if hasattr(self.slots_module, "extract_slots"):
            return self.slots_module.extract_slots(intent, message)
        raise AttributeError(f"extract_slots not found in {self.domain}.slots")

    def handle_checkout(self, intent: str, slots: Dict[str, Any], user_id: str) -> Any:
        if hasattr(self.checkout_module, "handle"):
            return self.checkout_module.handle(intent, slots, user_id)
        raise AttributeError(f"handle not found in {self.domain}.checkout")