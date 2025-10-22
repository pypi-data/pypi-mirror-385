"""Test basic cases for only the class DsiUnit constructor & string representation."""

from __future__ import annotations

from fractions import Fraction
from sys import float_info

import pytest

from dsi_unit import DsiUnit, DsiUnitNode
from dsi_unit.warnings import NonDsiUnitWarning


@pytest.mark.parametrize(
    ("unit_str", "latex_str", "expected_tree"),
    [
        # Case 1: No prefix and simple unit.
        (r"\metre", r"$$\mathrm{m}$$", [[DsiUnitNode(prefix="", unit="metre", exponent=1.0)]]),
        # Case 2: Simple DSI prefix, exponent as string.
        (r"\kilo\metre", r"$$\mathrm{k}\mathrm{m}$$", [[DsiUnitNode("kilo", "metre", "")]]),
        # Case 3: Simple but complete node.
        (r"\kilo\metre\tothe{2}", r"$$\mathrm{k}\mathrm{m}^{2}$$", [[DsiUnitNode("kilo", "metre", "2")]]),
        # Case 4: Fractions
        (
            r"\mega\metre\per\second\tothe{2}",
            r"$$\frac{\mathrm{M}\mathrm{m}}{\mathrm{s}^{2}}$$",
            [[DsiUnitNode("mega", "metre", "")], [DsiUnitNode("", "second", "2")]],
        ),
        # Case 5: Very complete and complex unit with prefix & exponent.
        (
            r"\milli\metre\tothe{1_2}\kilogram\per\mega\second\tothe{3}\ampere\tothe{-2}",
            r"$$\frac{\sqrt{\mathrm{m}\mathrm{m}}\mathrm{kg}}{\mathrm{M}\mathrm{s}^{3}\mathrm{A}^{-2}}$$",
            [
                [
                    DsiUnitNode(prefix=r"milli", unit=r"metre", exponent=Fraction(1, 2)),
                    DsiUnitNode(prefix="", unit=r"kilogram"),
                ],
                [
                    DsiUnitNode(prefix=r"mega", unit=r"second", exponent=3),
                    DsiUnitNode(prefix="", unit="ampere", exponent=-2),
                ],
            ],
        ),
        # Case 6: Non-dsi unit.
        (r"|fluid ounce", r"$$\textpipe\mathrm{fluid ounce}$$", [[DsiUnitNode("", "fluid ounce", valid=False)]]),
    ],
)
def test_base_usage(unit_str: str, latex_str: str, expected_tree: list):
    """Different cases considering prefixes, units and fractions as exponents."""
    if unit_str.startswith("|"):
        with pytest.warns(NonDsiUnitWarning):
            unit = DsiUnit(unit_str)
    else:
        unit = DsiUnit(unit_str)

    assert unit.valid, "The initialized unit is not valid."
    assert len(unit.warnings) == 0, "The unit initialization should contain no warnings."
    assert unit.to_latex() == latex_str, "Incorrect latex."
    assert unit.tree == expected_tree
    assert str(unit) == unit_str, "Incorrect unit conversion."


@pytest.mark.parametrize(
    ("exponent_str", "expected_exponent_fraction", "expected_exponent_str"),
    [
        ("2", Fraction(numerator=2, denominator=1), "2"),
        ("0.5", Fraction(numerator=1, denominator=2), "1_2"),
        ("1_2", Fraction(numerator=1, denominator=2), "1_2"),
        ("1/2", Fraction(numerator=1, denominator=2), "1_2"),
        ("0.6666666", Fraction(numerator=2, denominator=3), "2_3"),
        ("2_3", Fraction(numerator=2, denominator=3), "2_3"),
        ("-1_2", Fraction(numerator=-1, denominator=2), "-1_2"),
    ],
)
def test_exponent(exponent_str: str, expected_exponent_fraction: Fraction, expected_exponent_str: str):
    """Test parsing of different representations of fractions."""
    unit = DsiUnit(rf"\metre\tothe{{{exponent_str}}}")
    assert unit.tree[0][0].exponent == expected_exponent_fraction
    assert str(unit) == rf"\metre\tothe{{{expected_exponent_str}}}"


@pytest.mark.parametrize(
    ("unit_str", "latex_str", "warning_partial_msg"),
    [
        (r"\kilogram \metre\tothe{2}", r"$$\mathrm{kg}\mathrm{m}^{2}$$", "Given D-SI string contains spaces"),
        (
            r"\metre\tothe(2)",
            r"$$\mathrm{m}^{{\color{red}\mathrm{(2)}}}$$",
            r"looks like an exponent, but does not contain",
        ),
        (r"\foo", r"$${\color{red}\mathrm{foo}}$$", r"«foo» does not match any D-SI units"),
        (r"\molli\metre", r"$${\color{red}\mathrm{molli}}\mathrm{m}$$", r"Did you mean one of these «\\milli, \\mole»"),
        (
            r"\kilo\metre\per\mini\second",
            r"$$\frac{\mathrm{k}\mathrm{m}}{{\color{red}\mathrm{mini}}\mathrm{s}}$$",
            r"one of these «\\milli»?",
        ),
        (r"\milli\tothe{2}", r"$${\color{red}\mathrm{m}{\color{red}\mathrm{}}^{2}}$$", r"missing the base unit"),
        (
            r"\metre\per\metre\per\metre",
            r"$$\mathrm{m}{\color{red}/}\mathrm{m}{\color{red}/}\mathrm{m}$$",
            r"dsi string contains more than one",
        ),
        (r"\per\one", r"$$1$$", r"missing a numerator or denominator"),
        ("", r"$$\textpipe\mathrm{NULL}$$", "string is empty"),
        ("m_1_2_3", r"$$\textpipe\mathrm{m_1_2_3}$$", "Invalid BIPM-RP component"),
        (r"\metre\tothe{-1_-2}", r"$$\mathrm{m}^{{\color{red}\mathrm{-1_-2}}}$$", "exponent «-1_-2» is not a number"),
        (r"\metre\tothe{1_-2}", r"$$\mathrm{m}^{{\color{red}\mathrm{1_-2}}}$$", "exponent «1_-2» is not a number"),
        (r"\metre\tothe{2}gram", r"$$\mathrm{m}^{2}\mathrm{g}$$", "contained something after the"),
    ],
)
def test_invalid_entries(unit_str: str, latex_str: str, warning_partial_msg: str):
    """Checks for invalid entries."""
    with pytest.warns(RuntimeWarning, match=warning_partial_msg):
        unit = DsiUnit(unit_str)
    assert not unit.valid
    assert unit.to_latex() == latex_str


@pytest.mark.parametrize(
    ("unit_str", "utf_repr", "sirp_repr", "latex_str"),
    [
        (r"\metre", "m", "m", r"$$\mathrm{m}$$"),
        (r"\metre\tothe{2}", "m²", "m2", r"$$\mathrm{m}^{2}$$"),
        (r"\kilo\metre\tothe{-2}", "km⁻²", "km-2", r"$$\mathrm{k}\mathrm{m}^{-2}$$"),
        (r"\metre\tothe{0.5}", "m¹/²", "m1_2", r"$$\sqrt{\mathrm{m}}$$"),
        (r"\kilo\metre\tothe{0.333333333333333}", "km¹/³", "km1_3", r"$$\sqrt[3]{\mathrm{k}\mathrm{m}}$$"),
        (r"\kilo\metre\tothe{0.666666666666666}", "km²/³", "km2_3", r"$$\sqrt[3]{\mathrm{k}\mathrm{m}^{2}}$$"),
        (r"\kilo\metre\tothe{2}\per\volt", "km²/V", "km2.V-1", r"$$\frac{\mathrm{k}\mathrm{m}^{2}}{\mathrm{V}}$$"),
        (r"\volt\tothe{2}\per\ohm", "V²/Ω", "V2.Ω-1", r"$$\frac{\mathrm{V}^{2}}{\Omega}$$"),
        (r"\ampere\tothe{2}\ohm", "A²Ω", "A2.Ω", r"$$\mathrm{A}^{2}\Omega$$"),
        (r"\volt\ampere", "VA", "V.A", r"$$\mathrm{V}\mathrm{A}$$"),
        (
            r"\kilogram\metre\tothe{2}\per\second\tothe{3}",
            "kgm²/s³",
            "kg.m2.s-3",
            r"$$\frac{\mathrm{kg}\mathrm{m}^{2}}{\mathrm{s}^{3}}$$",
        ),
        (r"\joule\per\second", "J/s", "J.s-1", r"$$\frac{\mathrm{J}}{\mathrm{s}}$$"),
        (r"\newton\metre\per\second", "Nm/s", "N.m.s-1", r"$$\frac{\mathrm{N}\mathrm{m}}{\mathrm{s}}$$"),
        (
            r"\pascal\metre\tothe{3}\per\second",
            "Pam³/s",
            "Pa.m3.s-1",
            r"$$\frac{\mathrm{Pa}\mathrm{m}^{3}}{\mathrm{s}}$$",
        ),
        (r"\coulomb\volt\per\second", "CV/s", "C.V.s-1", r"$$\frac{\mathrm{C}\mathrm{V}}{\mathrm{s}}$$"),
        (r"\farad\volt\tothe{2}\per\second", "FV²/s", "F.V2.s-1", r"$$\frac{\mathrm{F}\mathrm{V}^{2}}{\mathrm{s}}$$"),
        (r"\henry\ampere\tothe{2}\per\second", "HA²/s", "H.A2.s-1", r"$$\frac{\mathrm{H}\mathrm{A}^{2}}{\mathrm{s}}$$"),
        (r"\weber\ampere\per\second", "WbA/s", "Wb.A.s-1", r"$$\frac{\mathrm{Wb}\mathrm{A}}{\mathrm{s}}$$"),
        (r"\siemens\volt\tothe{2}", "SV²", "S.V2", r"$$\mathrm{S}\mathrm{V}^{2}$$"),
        (
            r"\kilogram\metre\tothe{2}\per\second\tothe{2}",
            "kgm²/s²",
            "kg.m2.s-2",
            r"$$\frac{\mathrm{kg}\mathrm{m}^{2}}{\mathrm{s}^{2}}$$",
        ),
        (
            r"\milli\metre\tothe{2}\nano\second\tothe{-2}",
            "mm²ns⁻²",
            "mm2.ns-2",
            r"$$\mathrm{m}\mathrm{m}^{2}\mathrm{n}\mathrm{s}^{-2}$$",
        ),
        (
            r"\kilogram\second\metre\tothe{2}\per\second\tothe{3}",
            "kgsm²/s³",
            "kg.s.m2.s-3",
            r"$$\frac{\mathrm{kg}\mathrm{s}\mathrm{m}^{2}}{\mathrm{s}^{3}}$$",
        ),
        (
            r"\kilogram\milli\metre\tothe{2}\nano\second\tothe{-2}\degreecelsius",
            "kgmm²ns⁻²℃",
            "kg.mm2.ns-2.℃",
            r"$$\mathrm{kg}\mathrm{m}\mathrm{m}^{2}\mathrm{n}\mathrm{s}^{-2}^\circ\mathrm{C}$$",
        ),
    ],
)
@pytest.mark.filterwarnings("ignore")
def test_representations(unit_str: str, utf_repr: str, sirp_repr: str, latex_str: str):
    """Checking UTF8 & SIRP representation."""
    unit = DsiUnit(unit_str)
    assert unit.to_utf8() == utf_repr
    assert unit.to_sirp() == sirp_repr
    assert unit.to_latex() == latex_str
    assert unit.to_latex(wrapper="", prefix="pref-", suffix="-suf") == "pref-" + latex_str.replace("$", "") + "-suf"
    assert unit == DsiUnit(sirp_repr)


@pytest.mark.parametrize(
    ("base_unit", "test_unit_str", "latex_str"),
    [
        (DsiUnit(r"\watt"), u, r"$$\mathrm{kg}\mathrm{m}^{2}\mathrm{s}^{-3}$$")
        for u in (
            r"\volt\ampere",
            r"\volt\tothe{2}\per\ohm",
            r"\ampere\tothe{2}\ohm",
            r"\kilogram\metre\tothe{2}\per\second\tothe{3}",
            r"\joule\per\second",
            r"\newton\metre\per\second",
            r"\pascal\metre\tothe{3}\per\second",
            r"\coulomb\volt\per\second",
            r"\farad\volt\tothe{2}\per\second",
            r"\henry\ampere\tothe{2}\per\second",
            r"\weber\ampere\per\second",
            r"\siemens\volt\tothe{2}",
        )
    ]
    + [
        (DsiUnit(r"\ohm"), u, r"$$\mathrm{A}^{-2}\mathrm{kg}\mathrm{m}^{2}\mathrm{s}^{-3}$$")
        for u in (
            r"\siemens\tothe{-1}",
            r"\volt\per\ampere",
            r"\watt\ampere\tothe{-2}",
            r"\second\per\farad",
            r"\weber\per\coulomb",
            r"\volt\per\ampere",
            r"\siemens\tothe{-1}",
            r"\watt\per\ampere\tothe{2}",
            r"\volt\tothe{2}\per\watt",
            r"\second\per\farad",
            r"\henry\per\second",
            r"\weber\per\coulomb",
            r"\weber\coulomb\tothe{-1}",
            r"\joule\second\per\coulomb\tothe{2}",
            r"\kilogram\metre\tothe{2}\per\second\coulomb\tothe{2}",
            r"\joule\per\second\ampere\tothe{2}",
            r"\kilogram\metre\tothe{2}\per\second\tothe{3}\ampere\tothe{2}",
        )
    ],
)
def test_scale_factor(base_unit: DsiUnit, test_unit_str: str, latex_str: str):
    """Scale factor test between a base unit and another unit."""
    test_unit = DsiUnit(test_unit_str)
    scale_factor = test_unit.get_scale_factor(base_unit)
    common_unit = test_unit.get_base_unit(base_unit)

    assert abs(scale_factor - 1) < float_info.epsilon, "Scale factor should be 1.0"
    assert common_unit.to_latex() == latex_str


@pytest.mark.parametrize(
    ("bimp_unit", "exp_tree"),
    [
        (
            "mol.cd.m",
            [
                [
                    DsiUnitNode(prefix="", unit="mole"),
                    DsiUnitNode(prefix="", unit="candela"),
                    DsiUnitNode(prefix="", unit="metre"),
                ]
            ],
        ),
        (
            "kg2.m-1.s3",
            [
                [
                    DsiUnitNode(prefix="", unit="kilogram", exponent=2),
                    DsiUnitNode(prefix="", unit="metre", exponent=-1),
                    DsiUnitNode(prefix="", unit="second", exponent=3),
                ]
            ],
        ),
        (
            "kg.mm2.ns-2.℃",
            [
                [
                    DsiUnitNode(prefix="", unit="kilogram"),
                    DsiUnitNode(prefix="milli", unit="metre", exponent=2),
                    DsiUnitNode(prefix="nano", unit="second", exponent=-2),
                    DsiUnitNode(prefix="", unit="degreecelsius"),
                ]
            ],
        ),
    ],
)
def test_bimp_sirp_notation(bimp_unit: str, exp_tree: list[list[DsiUnitNode]]):
    """Creation of the unit using only BIMP notation."""
    unit = DsiUnit(bimp_unit)
    assert unit.valid
    assert unit.tree == exp_tree
