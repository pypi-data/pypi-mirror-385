from geniebottle.spellbooks.spellbook import SpellBook
# from stability_sdk import client
from typing import Optional
import os


class StabilityAI(SpellBook):
    '''
    `StabilityAI` class helps you define a new spell for use with `Magic`.

    Example:
    ```python
        from geniebottle import Magic
        from geniebottle.spellbooks import StabilityAI

        magic = Magic()

        magic.add(StabilityAI().get('stable_diffusion'))
    ```
    '''

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: str = 'grpc.stability.ai:443'
    ):
        super().__init__()

        if api_key is None:
            api_key = self._get_api_key()
        self.api_key = api_key

        self.host = host

    def _get_api_key(self):
        """
        Get API key from multiple sources in priority order:
        1. Environment variable
        2. Stored credentials (~/.geniebottle/credentials.json)
        """
        # First check environment variable (highest priority for backward compatibility)
        key = os.environ.get('STABILITY_KEY')
        if key:
            return key

        # Try to load from stored credentials
        try:
            from geniebottle.credentials import CredentialsManager
            creds = CredentialsManager()
            key = creds.get_key('stabilityai')
            if key:
                return key
        except ImportError:
            pass  # credentials module not available

        # No key found
        raise ValueError(
            "API key not set. You can set it in three ways:\n"
            "\n"
            "1. Use the bottle CLI (recommended):\n"
            "   `bottle auth login stabilityai`\n"
            "\n"
            "2. Pass the API key when instantiating the StabilityAI class:\n"
            "   `StabilityAI(api_key=\"YOUR_API_KEY\")`\n"
            "\n"
            "3. Set it as environment variable, `STABILITY_KEY`:\n"
            "   - Unix/Linux: `export STABILITY_KEY=YOUR_API_KEY`\n"
            "   - Windows: `set STABILITY_KEY=YOUR_API_KEY`\n"
            "\n"
            "If you don't have an API key yet:\n"
            "  • Sign up: https://platform.stability.ai/\n"
            "  • Get key: https://platform.stability.ai/account/keys"
        )

    def check_pricing(self):
        print(
            'See this link for pricing of the StabilityAI API: '
            'https://platform.stability.ai/pricing'
        )

    def __repr__(self):
        return '<StabilityAI SpellBook>'
