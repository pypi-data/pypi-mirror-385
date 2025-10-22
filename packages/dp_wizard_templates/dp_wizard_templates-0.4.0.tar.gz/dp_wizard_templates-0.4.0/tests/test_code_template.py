from pathlib import Path

import pytest
from dp_wizard_templates.code_template import Template, TemplateException


def test_non_repr_value():
    def template(VALUE):
        print(VALUE)

    with pytest.raises(
        TemplateException,
        match=r"Object of type set is not JSON serializable",
    ):
        Template(template).fill_values(VALUE={1, 2, 3})


def test_ignore_todo_by_default():
    def template():
        print("TODO")

    assert Template(template).finish() == 'print("TODO")'


def test_ignore_kwarg():
    def template():
        print("IGNORE_ME")

    with pytest.raises(
        TemplateException,
        match=r"'IGNORE_ME' slot not filled",
    ):
        Template(template).finish()

    assert Template(template, ignore={"IGNORE_ME"}).finish() == 'print("IGNORE_ME")'


def test_strip_pragma():
    def template():
        pass  # pragma: no cover

    assert Template(template).finish() == "pass\n"


def test_strip_noqa():
    def template():
        pass  # noqa: B950 (explanation here!)

    assert Template(template).finish() == "pass\n"


def test_strip_type_ignore():
    def template():
        pass  # type: ignore

    assert Template(template).finish() == "pass\n"


def test_def_too_long():
    def template(
        BEGIN,
        END,
    ):
        print(BEGIN, END)

    with pytest.raises(
        TemplateException, match=r"def and parameters should fit on one line"
    ):
        Template(template)


def test_def_template():
    def template(BEGIN, END):
        print(BEGIN, END)

    assert (
        Template(template).fill_values(BEGIN="abc", END="xyz").finish()
        == "print('abc', 'xyz')"
    )


def test_fill_expressions():
    template = Template("No one VERB the ADJ NOUN!")
    filled = template.fill_expressions(
        VERB="expects",
        ADJ="Spanish",
        NOUN="Inquisition",
    ).finish()
    assert filled == "No one expects the Spanish Inquisition!"


def test_fill_expressions_missing_slots_in_template():
    template = Template("No one ... the ... ...!")
    with pytest.raises(
        TemplateException,
        match=r"no 'ADJ' slot to fill with 'Spanish', "
        r"no 'NOUN' slot to fill with 'Inquisition', "
        r"no 'VERB' slot to fill with 'expects':",
    ):
        template.fill_expressions(
            VERB="expects",
            ADJ="Spanish",
            NOUN="Inquisition",
        ).finish()


def test_fill_expressions_extra_slots_in_template():
    template = Template("No one VERB ARTICLE ADJ NOUN!")
    with pytest.raises(
        TemplateException, match=r"'ARTICLE' slot not filled, 'VERB' slot not filled"
    ):
        template.fill_expressions(
            ADJ="Spanish",
            NOUN="Inquisition",
        ).finish()


def test_fill_values():
    template = Template("assert [STRING] * NUM == LIST")
    filled = template.fill_values(
        STRING="🙂",
        NUM=3,
        LIST=["🙂", "🙂", "🙂"],
    ).finish()
    assert filled == "assert ['🙂'] * 3 == ['🙂', '🙂', '🙂']"


def test_fill_values_missing_slot_in_template():
    template = Template("assert [STRING] * ... == LIST")
    with pytest.raises(TemplateException, match=r"no 'NUM' slot to fill with '3'"):
        template.fill_values(
            STRING="🙂",
            NUM=3,
            LIST=["🙂", "🙂", "🙂"],
        ).finish()


def test_fill_values_extra_slot_in_template():
    template = Template("CMD [STRING] * NUM == LIST")
    with pytest.raises(TemplateException, match=r"'CMD' slot not filled"):
        template.fill_values(
            STRING="🙂",
            NUM=3,
            LIST=["🙂", "🙂", "🙂"],
        ).finish()


def test_fill_blocks():
    # "OK" is less than three characters, so it is not a slot.
    template = Template(
        """# MixedCase is OK

FIRST

with fake:
    my_tuple = (
        # SECOND
        VALUE,
    )
    if True:
        THIRD
""",
    )
    filled = (
        template.fill_code_blocks(
            FIRST="\n".join(f"import {i}" for i in "abc"),
            THIRD="\n".join(f"{i}()" for i in "xyz"),
        )
        .fill_comment_blocks(
            SECOND="This is a\nmulti-line comment",
        )
        .fill_values(VALUE=42)
        .finish()
    )
    assert (
        filled
        == """# MixedCase is OK

import a
import b
import c

with fake:
    my_tuple = (
        # This is a
        # multi-line comment
        42,
    )
    if True:
        x()
        y()
        z()
"""
    )


def test_fill_comment_block():
    template = Template("# SLOT")
    filled = template.fill_comment_blocks(SLOT="placeholder").finish()
    assert filled == "# placeholder"


def test_finish_reformat():
    template = Template("print( 'messy','code!' )#comment")
    filled = template.finish(reformat=True)
    assert filled == 'print("messy", "code!")  # comment\n'


def test_fill_comment_block_without_comment():
    template = Template("SLOT")
    with pytest.raises(
        TemplateException,
        match=r"In string template, no 'SLOT' slot to fill with 'placeholder' "
        r"\(comment slots must be prefixed with '#'\)",
    ):
        template.fill_comment_blocks(SLOT="placeholder").finish()


def test_fill_blocks_missing_slot_in_template_alone():
    template = Template("No block slot")
    with pytest.raises(
        TemplateException, match=r"no 'SLOT' slot to fill with 'placeholder':"
    ):
        template.fill_code_blocks(SLOT="placeholder").finish()


def test_fill_blocks_missing_slot_in_template_not_alone():
    template = Template("No block SLOT")
    with pytest.raises(
        TemplateException,
        match=r"no 'SLOT' slot to fill with 'placeholder' "
        r"\(block slots must be alone on line\)",
    ):
        template.fill_code_blocks(SLOT="placeholder").finish()


def test_fill_blocks_extra_slot_in_template():
    template = Template("EXTRA\nSLOT")
    with pytest.raises(TemplateException, match=r"'EXTRA' slot not filled"):
        template.fill_code_blocks(SLOT="placeholder").finish()


def test_fill_blocks_not_string():
    template = Template("SOMETHING")
    with pytest.raises(
        TemplateException,
        match=r"for 'SOMETHING' slot, expected string, not '123'",
    ):
        template.fill_code_blocks(SOMETHING=123).finish()


def test_no_root_kwarg_with_function_template():
    def template():
        pass

    with pytest.raises(
        TemplateException,
        match=r"If template is function, root kwarg not allowed",
    ):
        Template(template, root=Path("not-allowed"))
