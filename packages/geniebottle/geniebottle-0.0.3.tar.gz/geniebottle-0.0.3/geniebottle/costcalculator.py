from rich.console import Console
from rich.table import Table
from .utils import get_default_args, get_arg_names
from typing import Callable
import warnings


class CostCalculator:
    def __init__(self, max_cost_per_cast: float = 0.0, spells: list = []):
        self.max_cost_per_cast = max_cost_per_cast
        self.spells = spells
        self.spell_costs = {}
        self.cost_total = 0
        self.spells_checked = []

    def _raise_cost_exception(self, costs, prefix: str = "", include_max_cost_per_cast_tip: bool = True):
        # determine unique cost categories
        unique_cost_keys = set(key for cost_dict in costs.values() for key in cost_dict)

        # initialize total costs
        cost_totals = {key: 0 for key in unique_cost_keys}

        # initialize table
        table = Table(title="Cost breakdown")
        table.add_column("Spell")
        for key in unique_cost_keys:
            table.add_column(key)
        table.add_column("Total cost")

        # build rows for each spell and update total costs
        for spell in self.spells_checked:
            spell_costs = costs[spell.__name__]
            row_values = [spell.__name__]

            for key in unique_cost_keys:
                cost_value = spell_costs.get(key, 0)
                row_values.append(f"{cost_value}")
                cost_totals[key] += cost_value

            total_spell_cost = sum(spell_costs.values())
            row_values.append(f"${total_spell_cost:.6f}")
            table.add_row(*row_values)

        # add total row
        total_row = ["Total"] + [f"${cost_totals[key]:.6f}" for key in unique_cost_keys]
        total_cost = sum(cost_totals.values())
        total_row.append(f"${total_cost:.6f}")
        table.add_row(*total_row)

        # capture and raise exception with table
        console = Console(record=True, force_terminal=False, color_system=None)
        with console.capture() as capture:
            console.print(table)
        table_str = capture.get()

        if include_max_cost_per_cast_tip:
            prefix += (
                f"This cast with {len(self.spells_checked)} spells will cost "
                f"{total_cost:.6f} USD.\n"
                f"Your max cost per cast is {self.max_cost_per_cast:.6f}. Please "
                "either:\n"
                "1. Check for accidental excessive spell casting, or\n"
                "2. Increase your `max_cost_per_cast` limit, e.g.\n"
                f"\tmagic = Magic(max_cost_per_cast={total_cost+0.000001:.6f})\n\n"
                "WARNING: Raising the max cost per cast incurs real-world costs.\n\n"
            )

        raise ValueError(f"{prefix}\n" f"Cost breakdown:\n{table_str}")

    def _get_cost_from_cost_func(self, fun, kwargs, spell):
        kwarg_names = get_arg_names(fun)
        # add kwargs defined when the spell was cast
        if "kwargs" in kwarg_names:
            # include all kwargs
            kwargs_for_this_fun = kwargs
        else:
            # include a subset of kwargs or else the function will return an unknown
            # argument error
            kwargs_for_this_fun = {k: v for k, v in kwargs.items() if k in kwarg_names}

        # add kwargs defined when the spell was defined
        if hasattr(spell, "defined_kwargs"):
            new_kwargs = {k: v for k, v in spell.defined_kwargs.items() if k in kwarg_names}
            kwargs_for_this_fun.update(new_kwargs)

        # add default kwargs if they are not specified
        defaults = get_default_args(spell)
        for kk, vv in defaults.items():
            if kk in kwarg_names and kk not in kwargs_for_this_fun:
                kwargs_for_this_fun[kk] = vv

        # run the cost calculation function
        return fun(**kwargs_for_this_fun)

    def get_cost_from_cost_funcs(self, spell, kwargs):
        # find all the cost functions added by the @limit_cost decorator
        limit_cost_functions = {k: v for k, v in spell.__dict__.items() if str(k).startswith("cost")}
        # loop through each cost function and calculate the estimated cost
        costs = {}
        for k, v in limit_cost_functions.items():
            if v is None:
                continue

            if not isinstance(v, Callable):
                costs[k] = v
                continue

            # get cost by running the cost functions with user-defined kwargs
            costs[k] = self._get_cost_from_cost_func(v, kwargs, spell)

        return costs

    def _check_max_cost_of_spell(self, spell_cost: float, spell: Callable, kwargs):
        if not hasattr(spell, "max_cost") or spell.max_cost is None:
            warnings.warn(
                f"no `max_cost` attribute found on spell {spell.__name__}.\n"
                "a `max_cost` attribute ensures you don't cast a spell that\n"
                "uses too much money per cast.\n"
                "Add a `max_cost` argument to the limit_cost decorator like so:\n"
                "```python\n"
                "from geniebottle.decorators import limit_cost\n"
                "\n"
                "# using a fixed value\n"
                "@limit_cost(max_cost=0.1)\n"
                "def your_spell_function(input)\n"
                "   pass\n"
                "\n\n"
                "# using input arguments with a function\n"
                "@limit_cost(max_cost= lambda max_tokens: max_tokens * 0.002)\n"
                "def another_spell_function(input, max_tokens):\n"
                "   pass\n"
            )
            return

        if isinstance(spell.max_cost, Callable):
            spell.max_cost = self._get_cost_from_cost_func(spell.max_cost, kwargs, spell)

        if spell_cost > spell.max_cost:
            self._raise_cost_exception(
                self.spell_costs,
                prefix=(
                    f"spell: {spell.__name__} has an estimated cost of {spell_cost}, "
                    f"exceeding this spell's max_cost of {spell.max_cost}.\n"
                    "Check for errors in input or update your `max_cost` attribute "
                    "in the `@limit_cost` decorator.\n"
                ),
                include_max_cost_per_cast_tip=False,
            )

    def check_cost(self, spell: callable = None, **kwargs):
        """
        Check the cost per cast of spells added to the `Magic` instance.
        If a spell argument is provided, then the cost of that spell will
        be calculated and added to a running cost.

        Args:
            spell (callable): The spell to check the cost of. If None, then
            use all spells added to the `Magic` instance. If a spell is
            provided, then the cost of that spell will be calculated and
            added to a running cost.

        Raises:
            ValueError: If the cost of the spells exceeds the `max_cost_per_cast`
            provided to the `Magic` instance.

        Returns:
            float: The total cost of the spells checked so far.
        """
        if self.max_cost_per_cast is None:
            return

        spells_to_check = [spell] if spell is not None else self.spells

        for spell in spells_to_check:
            self.spell_costs[spell.__name__] = self.get_cost_from_cost_funcs(spell, kwargs)
            self.spells_checked.append(spell)

            spell_cost = sum(self.spell_costs[spell.__name__].values())
            self._check_max_cost_of_spell(spell_cost, spell, kwargs)

            self.cost_total += spell_cost

        if self.cost_total > self.max_cost_per_cast:
            self._raise_cost_exception(self.spell_costs)

        return self.cost_total
