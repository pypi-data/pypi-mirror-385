# The `Magic` class

`Magic` is the central class of Genie Bottle. 
You can add spells to it using the `add()` method and cast them using the `cast()` method. 
You can also create an instant REST api for your spells so they can be integrated into other applications (See [here]()).


## Initialisation

Initialising Magic lets you define how you want magic in your application to behave.

```python
from geniebottle import Magic

magic = Magic()
```

Here, you can specify arguments such as `max_cost_per_cast`. This means you can cap how much real world cost casting a spell
can have. This is useful if you are using third party APIs that charges you per request. It is **really** useful to prevent
overspending if you cast spells that can call on 10s to 100s of agents or ai models at a time (e.g. in the [virtual company example]()).

```python
magic = Magic(max_cost_per_cast=0.05)
```


## Adding Spells

You can add spells to `Magic` using the `add()` method. They can be a **simple python function** you have created, or they
can be a spell function imported from a **spellbook**.

Genie Bottle comes with many spellbooks with prebuilt spells you can use. You can also [create your own spells and spellbooks]().

See here for a list of [prebuilt spells](). 

In this example, we'll import the `Llama2` spell from the `Local` spellbook. These spells are ran locally on your machine and don't
cost anything to run (unlike spells that call on third party APIs).

```python
from geniebottle.spellbooks import Local

magic.add(Local('Llama2'))
```


## Casting Spells
