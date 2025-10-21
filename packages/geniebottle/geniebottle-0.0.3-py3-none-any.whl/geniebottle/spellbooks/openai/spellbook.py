from openai import OpenAI as OpenAIClient
from geniebottle.spellbooks.spellbook import SpellBook
from typing import Optional
import os


class OpenAI(SpellBook):
    '''
    `OpenAI` class helps you define a new spell for use with `Magic`.

    Example:
    ```python
        from geniebottle import Magic
        from geniebottle.spellbooks import OpenAI

        magic = Magic()

        magic.add(OpenAI().get('chatgpt'))
    ```
    '''

    def __init__(
        self,
        api_key: Optional[str] = None
    ):
        super().__init__()

        if api_key is None:
            api_key = self._get_api_key()

        self.client: OpenAIClient = OpenAIClient(api_key=api_key)

    def _get_api_key(self):
        """
        Get API key from multiple sources in priority order:
        1. Environment variable
        2. Stored credentials (~/.geniebottle/credentials.json)
        """
        # First check environment variable (highest priority for backward compatibility)
        key = os.environ.get('OPENAI_API_KEY')
        if key:
            return key

        # Try to load from stored credentials
        try:
            from geniebottle.credentials import CredentialsManager
            creds = CredentialsManager()
            key = creds.get_key('openai')
            if key:
                return key
        except ImportError:
            pass  # credentials module not available

        # No key found
        raise ValueError(
            "API key not set. You can set it in three ways:\n"
            "\n"
            "1. Use the bottle CLI (recommended):\n"
            "   `bottle auth login openai`\n"
            "\n"
            "2. Pass the API key when instantiating the OpenAI class:\n"
            "   `OpenAI(api_key=\"YOUR_API_KEY\")`\n"
            "\n"
            "3. Set it as environment variable, `OPENAI_API_KEY`:\n"
            "   - Unix/Linux: `export OPENAI_API_KEY=YOUR_API_KEY`\n"
            "   - Windows: `set OPENAI_API_KEY=YOUR_API_KEY`"
        )
        return key

    def check_pricing(self):
        print('See this link for pricing of the OpenAI API: https://openai.com/pricing')

    def __repr__(self):
        return '<OpenAI Spellbook>'
