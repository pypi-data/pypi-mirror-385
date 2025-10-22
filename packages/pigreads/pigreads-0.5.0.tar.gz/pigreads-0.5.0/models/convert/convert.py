#!/bin/env python3
"""
Export Myokit MMT files to Pigreads code
----------------------------------------
"""

from __future__ import annotations

import datetime
import os
import sys
import warnings
from pathlib import Path
from textwrap import dedent
from typing import Any

import myokit as mk  # type: ignore[import-not-found]
import yaml
from myokit.formats.cellml import (  # type: ignore[import-not-found]
    CellMLImporter,
)
from myokit.formats.opencl import (  # type: ignore[import-not-found]
    OpenCLExpressionWriter,
)

INDENT: str = "    "


def str_presenter(dumper, data):
    """
    A YAML string presenter that uses block style for multiline strings.
    """
    data = data.strip()
    if len(data.splitlines()) > 1:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.representer.SafeRepresenter.add_representer(str, str_presenter)


class PigreadsMyokitWriter:
    """
    This class implements the conversion of a Myokit model to Pigreads
    compatible code.

    :param model: The Myokit model to convert.
    :param meta: A dictionary with metadata to include in the generated code.

    :var model: The Myokit model to convert.
    :vartype model: myokit.Model
    :var exwr: The expression writer for double floating point precision
    :vartype exwr: myokit.formats.opencl.OpenCLExpressionWriter
    :var states: The list of states in the model.
    :vartype states: list[mk.State]
    :var meta: A dictionary with metadata to include in the generated code.
    :vartype meta: dict[str, Any]
    """

    def __init__(self, model: mk.Model, meta: dict[str, Any]):
        self.model = model
        self.exwr = OpenCLExpressionWriter(
            precision=mk.DOUBLE_PRECISION, native_math=False
        )
        self.exwr.set_lhs_function(self.lhs_format)
        self.states = list(model.states())
        self.meta = meta
        self.generate_variable_abbreviations()

    @property
    def diffusivities(self) -> dict[str, float]:
        """
        The diffusivities of the model as defined in the metadata.
        """
        d = self.meta.get("diffusivity", {})
        assert isinstance(d, dict)
        return d

    def get_ivar(self, varname: str) -> int:
        """
        Get the index of a state variable by its name.

        :param varname: The name of the state variable.
        :return: The index of the state variable.
        """
        return next(
            i
            for i, state in enumerate(self.states)
            if str(self.lhs_format(state)) == varname
        )

    @staticmethod
    def nodots(s: Any) -> str:
        """
        Convert an object to string and replace dots by underscores.

        :param s: any object to represent as a string.
        """
        return str(s).replace(".", "_")

    def lhs_format(self, x: mk.LhsExpression):
        """
        Format a left-hand side expression.

        :param x: The left-hand side expression to format.
        :return: The formatted left-hand side expression.
        """
        assert not isinstance(x, mk.Derivative), "Can not handle derivatives here."
        if isinstance(x, mk.Name):
            return self.lhs_format(x.var())
        s = self.nodots(x)
        return self.variable_abbreviations.get(s, s)

    @staticmethod
    def rush_larsen(
        v: mk.Variable,
        tau: mk.Variable,
        inf: mk.Variable,
        dt: str = "dt",
    ) -> mk.Expression:
        """
        The Rush-Larsen update for a state variable v.

        :param v: The state variable to update.
        :param tau: The time constant.
        :param inf: The steady state value.
        :param dt: Name of the time step.
        :return: The Rush-Larsen update for the state variable.
        """
        return mk.Plus(
            inf,
            mk.Multiply(
                mk.Minus(v, inf),
                mk.Exp(mk.PrefixMinus(mk.Divide(mk.Name(dt), tau))),
            ),
        )

    @staticmethod
    def safe_divide(a: mk.Expression, b: mk.Expression) -> mk.Expression:
        """
        Division that avoids division by a value close to zero.

        :param a: Enumerator.
        :param b: Denominator.
        :return: Expression of the safe division.
        """
        eps = mk.Name("VERY_SMALL_NUMBER")
        return mk.Divide(
            a,
            mk.If(
                i=mk.Less(mk.Abs(b), eps),
                t=mk.If(
                    i=mk.Less(b, mk.Number(0)),
                    t=mk.PrefixMinus(eps),
                    e=eps,
                ),
                e=b,
            ),
        )

    @classmethod
    def offset_in_division(cls, ex: mk.Expression) -> mk.Expression:
        """
        Avoid division by zero by adding a small offset in specific cases.

        :param ex: An expression to find and replace quotients in.
        :return: The updated expression.
        """

        subst: dict[Any, Any] = {}
        for quotient in ex.walk([mk.Divide]):
            numerator, denominator = quotient
            if not denominator.is_constant():
                subst[quotient] = cls.safe_divide(
                    cls.offset_in_division(numerator),
                    cls.offset_in_division(denominator),
                )
        return ex.clone(subst)

    def state_equation(self, q: mk.Equation):
        """
        Format a state equation.

        :param q: The state equation to format.
        :return: The formatted state equation.
        """
        w = q.lhs.walk()
        next(w)
        v = next(w)
        vin = str(self.lhs_format(v))

        # if possible, use Rush-Larsen step
        if isinstance(q.rhs, mk.Divide):
            difference, tau = q.rhs
            if isinstance(difference, mk.Minus):
                left, right = difference
                if left == v:
                    return f"*_new_{vin} = -({self.exwr.ex(self.rush_larsen(v=v, tau=tau, inf=right))});"
                if right == v:
                    return f"*_new_{vin} = {self.exwr.ex(self.rush_larsen(v=v, tau=tau, inf=left))};"

        # else use forward Euler
        rhs: mk.Expression = q.rhs.clone()
        rhs = self.offset_in_division(rhs)
        update: str = str(self.exwr.ex(rhs))
        if vin in self.diffusivities:
            update += f" + _diffuse_{vin}"
        return f"*_new_{vin} = {vin} + dt*({update});"

    def generate_variable_abbreviations(self) -> None:
        """
        Create a dictionary abbreviating long variable names if this
        is possible unambiguously. Short variable names are the last part of the
        long variable name after a dot.
        """
        variables = dict(
            zip(
                self.model.states(),
                self.model.initial_values(as_floats=True),
                strict=False,
            )
        )
        variables_long = {self.nodots(v): f for v, f in variables.items()}
        variables_short = {}
        for variable, value in variables.items():
            short_varname = str(variable).rsplit(".", maxsplit=1)[-1]
            if short_varname not in variables_short:
                variables_short[short_varname] = value
            else:
                variables_short = variables_long
                break
        self.variables = variables_short
        self.variable_abbreviations = dict(
            zip(variables_long.keys(), variables_short.keys(), strict=False)
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model to a dictionary. This is the main entry point for the
        conversion.

        :return: The model as a dictionary.
        """
        parameters = {
            self.lhs_format(q.lhs): float(q.rhs)
            for block in self.model.solvable_order().values()
            for q in block
            if q.rhs.is_constant()
        }

        d: dict[str, Any] = {
            "name": rf"{self.model.name()} (exported from Myokit)",
            "description": str(self.model.meta.get("desc", "")),
            "dois": [],
            "variables": self.variables,
            "parameters": parameters,
            **self.meta,
        }

        step = []
        for blockname, block in self.model.solvable_order().items():
            block_ = [eq for eq in block if not eq.rhs.is_constant()]
            if len(block_) < 1:
                continue
            step.append("")
            step.append(f"// {blockname}")
            for q in block_:
                if q.lhs.is_derivative():
                    step.append(self.state_equation(q))
                else:
                    step.append(
                        "const Real "
                        + self.exwr.eq(
                            mk.Equation(q.lhs, self.offset_in_division(q.rhs))
                        )
                        + ";"
                    )
        d["code"] = os.linesep.join(step).strip()

        return d

    def __str__(self) -> str:
        """
        Convert the model to a string. This is the another main entry point for the
        conversion.

        :return: The model as a string.
        """
        return yaml.safe_dump(
            self.to_dict(), sort_keys=False, indent=2, allow_unicode=True
        )


def main() -> None:
    cellml = CellMLImporter()

    path_in = Path()
    path_out = Path("..")

    paths_by_stem: dict[str, dict[str, str]] = {}
    for file in sorted(path_in.iterdir()):
        suffix = file.suffix[1:].lower()

        if suffix not in ["yaml", "mmt", "cellml"]:
            continue

        if file.stem not in paths_by_stem:
            paths_by_stem[file.stem] = {}

        paths_by_stem[file.stem][suffix] = str(file)

    models = {}
    for key, paths in paths_by_stem.items():
        model = {}
        meta = {}

        assert "yaml" in paths, "Must have yaml file."
        with Path(paths["yaml"]).open() as f:
            meta = yaml.safe_load(f.read())

        if "cellml" in paths:
            assert "mmt" not in paths, "Can only have mmt or cellml, not both."
            try:
                model = PigreadsMyokitWriter(
                    cellml.model(paths["cellml"]), meta
                ).to_dict()
            except Exception as e:
                warnings.warn(f"{paths['cellml']}: {e}", stacklevel=2)
                continue

        elif "mmt" in paths:
            try:
                model = PigreadsMyokitWriter(
                    mk.load_model(paths["mmt"]), meta
                ).to_dict()
            except Exception as e:
                warnings.warn(f"{paths['mmt']}: {e}", stacklevel=2)
                continue

        model.update(meta)
        models[key] = model

    for key, model in models.items():
        (path_out / f"{key}.yaml").write_text(
            dedent(f"""
            # converted from CellML or Myokit to Pigreads using {sys.argv[0]}
            # on {datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")}
            """).strip()
            + os.linesep * 2
            + dedent(
                yaml.safe_dump(model, sort_keys=False, indent=2, allow_unicode=True)
            )
        )


if __name__ == "__main__":
    main()
