# Cast your first spell

## Magic

Magic is the main component of Genie Bottle.

You can create it with the following code:

```python
from geniebottle import Magic

magic = Magic()
```

## Adding a spell

After creating a magic instance, you can add a spell to it.
A spell

You can either [make your own spell](./make_your_own_spell) or load a spell from a pre-made spellbook.

A good starting point is adding one spell from a pre-made spellbook.

```python
from geniebottle.spellbooks import OpenAI

spellbook = OpenAI()

magic.add(spellbook.get('chatgpt'))
```

## Casting a spell

If you want to use the spell to do something, you `cast()` it!

```
magic.cast('Say hi like a cat!')
```
