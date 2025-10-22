# # DP Wizard Templates
#
# [github](https://github.com/opendp/dp-wizard-templates) | [pypi](https://pypi.org/project/dp_wizard_templates/) | [docs](https://opendp.github.io/dp-wizard-templates) (this page)
#
# DP Wizard Templates helps you build Python code from templates
# which are themselves syntactically valid Python.
# Templates can be composed to generate entire notebooks.
#
# DP Wizard Templates relies on code inspection, so real working examples
# need to be in code, not in a notebook or a doctest.
# This documentation itself is rendered by the library.
#
# DP Wizard Templates was developed for
# [DP Wizard](https://github.com/opendp/dp-wizard),
# and that codebase remains a good place to look for further examples.
#
#
# ## Motivation
#
# Let's say you want to generate Python code programmatically,
# perhaps to demonstrate a workflow with parameters supplied by the user.
# One approach would be to use a templating system like Jinja,
# but this may be hard to maintain: The template itself is not Python,
# so syntax problems will not be obvious until it is filled in.
# At the other extreme, constructing code via an AST is very low-level.
#
# DP Wizard Templates is an alternative. The templates are themselves Python code,
# and the slots to fill are all-caps. This convention means that the template
# itself can be parsed as Python code, so syntax highlighting and linting still works.
#
#
# ## Examples: `dp_wizard_templates.code_template`
#
# There are two modules in this library. We'll look at `code_template` first.

# +

from dp_wizard_templates.code_template import Template


def conditional_print_template(CONDITION, MESSAGE):
    if CONDITION:
        print(MESSAGE)


conditional_print = (
    Template(conditional_print_template)
    .fill_expressions(CONDITION="temp_c < 0")
    .fill_values(MESSAGE="It is freezing!")
    .finish()
)

assert conditional_print == "if temp_c < 0:\n    print('It is freezing!')"

# -

# Note that `conditional_print_template` is not called: Instead,
# the `inspect` package is used to load its source, and the slots
# in all-caps are filled. Including a parameter list is optional,
# but providing args which match the names of your slots can prevent
# warnings from your IDE.
#
# Different methods are available on the `Template` object:
# - `fill_expressions()` fills the slot with verbatim text.
#   It can be used for an expression like this, or for variable names.
# - `fill_values()` fills the slot with the repr of the provided value.
#   This might be a string, or it might be a list or dict or other
#   data structure, as long as it has a usable repr.
# - `finish()` converts the template to a string, and will error
#   if not all slots have been filled.
#
# (The next section will introduce `fill_code_block()` and `fill_comment_block()`.)
#
# Templates can also be standalone files. If a `root` parameter is provided,
# the system will prepend `_` and append `.py` and look for a corresponding file.
# (The convention of prepending `_` reminds us that although these files
# can be parsed, they should not be imported or executed as-is.)

# +

from pathlib import Path

root = Path(__file__).parent.parent

block_demo = (
    Template("block_demo", root=root / "examples")
    .fill_expressions(FUNCTION_NAME="freeze_warning", PARAMS="temp_c")
    .fill_code_blocks(INNER_BLOCK=conditional_print)
    .fill_comment_blocks(
        COMMENT="""
        Water freezes at:
        32 Fahrenheit
        0 Celsius
        """
    )
    .finish()
)

assert (
    block_demo
    == '''def freeze_warning(temp_c):
    """
    This demonstrates how larger blocks of code can be built compositionally.
    """
    # Water freezes at:
    # 32 Fahrenheit
    # 0 Celsius
    if temp_c < 0:
        print('It is freezing!')
'''
)

# -

# Finally, plain strings can also be used for templates.

# +

assignment = (
    Template("VAR = NAME * 2")
    .fill_expressions(VAR="band")
    .fill_values(NAME="Duran")
    .finish()
)

assert assignment == "band = 'Duran' * 2"

# -

# ## Examples: `dp_wizard_templates.converters`
#
# DP Wizard Templates also includes utilities to convert Python code
# to notebooks, and to convert notebooks to HTML. It is a thin wrapper
# which provides default settings for `nbconvert` and `jupytext`.
#
# The Python code is converted to a notebook using the
# [jupytext light format](https://jupytext.readthedocs.io/en/latest/formats-scripts.html#the-light-format):
# Contiguous comments are coverted to markdown cells,
# and contiguous lines of code are converted to code cells.
#
# One additional feature is that a section with a `# Coda` header
# will be stripped from notebook output. This allows a notebook
# to produce other artifacts without adding clutter.

# +

from dp_wizard_templates.converters import convert_py_to_nb, convert_nb_to_html


def notebook_template(TITLE, BLOCK, FUNCTION_NAME):
    # # TITLE
    #
    # Comments will be rendered as *Markdown*.
    # The `+` and `-` below ensure that only one code cell is produced,
    # even though the lines are not contiguous

    # +
    BLOCK

    FUNCTION_NAME(-10)
    # -

    # # Coda
    #
    # Extra computations that will not be rendered.

    2 + 2


title = "Hello World!"
notebook_py = (
    Template(notebook_template)
    .fill_code_blocks(BLOCK=block_demo)
    .fill_expressions(FUNCTION_NAME="freeze_warning", TITLE=title)
    .finish()
)

notebook_ipynb = convert_py_to_nb(notebook_py, title=title, execute=True)
(root / "examples" / "hello-world.ipynb").write_text(notebook_ipynb)

notebook_html = convert_nb_to_html(notebook_ipynb)
(root / "examples" / "hello-world.html").write_text(notebook_html)

# -

# The [output](examples/hello-world.html) is short,
# but it is an end-to-end demonstration of DP Wizard Templates,
# and as noted at the top, this documentation itself is rendered with
# `convert_py_to_nb` and `convert_nb_to_html`.
#
# ## Last thoughts
#
# Because the templates are valid Python, linters and other tools
# will by default include them in their coverage, and this may not be
# what you want. The exact configuration tweaks needed will depend
# on your tools, but here are some recommendations:
#
# - You might keep template files under `templates/` subdirectories,
#   and configure pytest (`--ignore-glob '**/templates/`) and pyright
#   (`ignore = ["**/templates/"]`) to ignore them.
# - For template functions, you might have a consistent naming
#   convention, and configure coverage (`exclude_also = def template_`)
#   to exclude them as well, or else use `# pragma: no cover`.

# # Coda

# +

readme_test_py = Path(__file__).read_text()

html_path = root / "index.html"
before_hash = hash(html_path.read_text())

html = convert_nb_to_html(
    convert_py_to_nb(readme_test_py, "DP Wizard Templates"), numbered=False
)
(html_path).write_text(html)

after_hash = hash(html_path.read_text())
assert (
    before_hash == after_hash
), "index.html has changed: If that is intended, the next test run should pass."
