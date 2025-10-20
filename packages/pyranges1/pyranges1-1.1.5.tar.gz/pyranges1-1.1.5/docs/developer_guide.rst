Developer guide
===============

Pyranges was originally written by Endre Bakken Stovner under supervision of Pål Sætrom.
It is now mainly developed by Endre Bakken Stovner and by the Comparative Genomics lab of
Marco Mariotti. It follows the guidelines for open source software, and external contributors
are welcome. The code is centralized on github, at https://github.com/pyranges/pyranges_1.x

Bugs and feature requests can be reported as github issues. You may also contribute by submitting
your own code edits, either to deal with issues or to add new functionalities. Please discuss new
features with the team before making a PR. The code will be reviewed by the core development team,
which may integrate it in the main repository. Contributions are tracked by github and are publicly
visible.

Below, we sketch a guide to contribute to Pyranges. It assumes familiarity with python and with the
terminal, and minimal experience with git/github. Before the actual list of steps follow (:ref:`Task
sequence <task_sequence>`), we go over some essential concepts used in the "continuous integration" system in place
to maintain and evolve Pyranges.




Tests
~~~~~

Tests are an essential part of continuous integration. Briefly, they ensure that code edits do not
break existing functions. Various layers of tests are implemented in Pyranges:

- **unit tests**: quick and compulsory tests about the main Pyranges functionalities
- **doctest**: quick and compulsory tests that ensures that the code in the documentation (tutorial and how-to-pages) gives the expected results
- **property based tests**: time-consuming tests that involve the generation of random data to check that the results of Pyranges functions match that of other reference bioinformatic tools. These tests are not compulsory: the core development team runs them when the code backbone is edited.

If the code submitted to Pyranges does not pass the compulsory tests, it will not be integrated.
Therefore, we highly recommend developers to run tests before code submissions, as explained
further below.



Documentation: docstrings
~~~~~~~~~~~~~~~~~~~~~~~~~

Python docstrings are widely used to document the rationale, input arguments, and returned values of
all functions and methods. The use of a consistent docstring style allows the automatic generation
of API documentation, as seen in Pyranges documentation at `https://pyranges.readthedocs.io/
<https://pyranges.readthedocs.io/>`_, built through the Sphynx software.

Pyranges adopts the NumPy/SciPy-style: `https://numpydoc.readthedocs.io/en/latest/format.html
<https://numpydoc.readthedocs.io/en/latest/format.html>`_. It is important that code contributors
who edit any function also update their docstrings to reflect how it works; and that all new
functions contain an appropriate docstring. Follow the link above and inspect existing Pyranges
code to write good docstrings.



Code formatting and linting
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyranges code follows strict guidelines about its formatting and non-redundancy. This burden is
not upon the developer: instead, this is achieved by running dedicated software that polishes,
formats, and "lints" the code before its integration in the main repository. The tool **ruff**
is used, for both code linting and formatting.

Type checking
~~~~~~~~~~~~~

Pyranges is strict about type checking to ensure code reliability and maintainability. Type
checking involves specifying and verifying the data types of variables and functions, a
practice that may be unfamiliar to some Python developers.

These annotations allow tools like **pyright**, which we use extensively, to check types.
Consequently, if `add` is called with non-integer arguments or if it returns a non-integer value,
the type checker flags an error. This preemptive error detection, happening at compile
time (before the code is run), significantly reduces runtime issues and enhances code quality.

For example, consider this basic function:

.. code:: python

    def add(a, b):
        return a + b

With type annotations, it becomes:

.. code:: python

    def add(a: int, b: int) -> int:
        return a + b

For more detailed guidance on typing in Python, see the
`official Python documentation <https://docs.python.org/3/library/typing.html>`_.

We encourage contributions to Pyranges, even if they involve partial typing. If you're new
to typing or have any questions, feel free to ask for help. We're committed to supporting
our community in enhancing Pyranges together.

.. _task_sequence:

Task sequence
~~~~~~~~~~~~~

1. Create and download your own Pyranges fork
---------------------------------------------

The easiest way to do this is through github. Login into the github website if you aren't already,
then visit the Pyranges page on github, click "Fork" on the top right. 
Fill the form and confirm. In the page of your new fork, find the
**<> Code** button, and copy the https address. On your computer, create a new folder dedicated
to the project, then clone your fork inside it:

.. code:: bash

	mkdir mypyranges
	cd mypyranges
	git clone PASTE_GITHUB_HTTPS

2. Set up your developer environment and install Pyranges
---------------------------------------------------------

We recommend creating an environment dedicated to the development of pyranges:

.. code:: bash

	conda create -n prdev python pip
	conda activate prdev


Next, let's install pyranges and its dependencies: cd into your pyranges fork, 
and install it locally with pip as shown below. By using pip
option ``-e``, your installation is in "editable" mode: any changes you make to your pyranges code
will be immediately reflected in your environment. In other words, you won't need to re-run pip
install every time you change something in the code. 

.. code:: bash

	cd pyranges
	pip install -e .

Next, let's install optional dependencies (necessary to run certain functions and thus required to 
pass tests) and all developer dependencies (necessary to run tests, lint code etc). Their list, like 
most of Pyranges configuration, is found in the pyproject.toml file. You can install all you need with:

.. code:: bash

	pip install .[all]


3. Edit the code
----------------

Now, you're ready to edit the code in the pyranges/ folder.

To run your code to see that it behaves as intended, we recommend using a separate script that
imports pyranges, making sure you're in the prdev conda environment.


4. Run tests
------------

For each of the commands below, inspect the output of pytest: warnings are acceptable, but errors must be
fixed. To run the compulsory **doctest** and **unit tests**, run:

.. code:: bash

        pytest --doctest-modules pyranges
        pytest tests/unit

If you modified core Pyranges functions, you may want to also run the non-compulsory **property-based tests**:

.. code:: bash

	pytest tests/property_based/

If any of the tests fail, you must amend them before proceeding. 



5. Format, lint, type-checking code
-----------------------------------

Next, let's format code with ruff:

.. code:: bash

        ruff format pyranges

Then, let's lint code, also with ruff:

.. code:: bash

        ruff check pyranges


If the ruff check above shows any error, you must fix them before you proceed. 
If errors are deemed 'fixable', you may simply run ``ruff check --fix pyranges``. 
If not, you must delve into the code -- note, ChatGPT/Copilot are your friends!

Lastly, let's use pyright to ensure correct type-checking:


.. code:: bash

        pyright

Again, any error in the pyright must be amended before proceeding. Note that if you edit the code, 
you may want to format and lint code again with ruff.

6. Test on all supported python and package versions
-----------------------------------------------------

Next, we use **tox** to test whether the code works across all the versions of python and main dependencies 
that we intend to support. This step internally runs steps 4 and 5 for every such version defined in 
pyproject.toml. (Advanced users may actually directly run 6 instead of 4-5). For this, run:

.. code:: bash

	tox

If any errors emerge, correct them (or ask us for help).

7. Inspect the Sphynx documentation
-----------------------------------

Your code edits may warrant edits in the Pyranges docstrings. In this case, it is compelling to
locally check that the automatically generated documentation is built appropriately. Inside the
pyranges/ folder, run these commands:

.. code:: bash

	cd docs
	make html
	cd -

If the "make" command has no major errors, it will generate the full pyranges documentation in the
form of html pages, identical to `https://pyranges.readthedocs.io/ <https://pyranges.readthedocs.io/>`_.
Open the file docs/build/html/index.html with a browser to inspect all the parts that may have
been affected by your changes, and fix any potential problems. To know more about its inner workings,
read about the Sphynx system.


8. Log your changes
----------------------

At this stage, you are ready to submit your code for integration into the
main Pyranges repository; that is to say, to open a "pull request". Before you can do that, you
have to update your remote repository, i.e. your Pyranges fork at github.

First, bump the version number in the file pyproject.toml. Then, it's essential to document your changes
in the CHANGE_LOG.txt file. This log should provide a clear and
concise summary of the modifications, additions, and fixes made in each version of your project. Include
relevant details such as feature enhancements, bug fixes, and any other notable alterations to help
maintain a transparent and informative record of your project's evolution.

9. Commit and push to your remote repository
---------------------------------------------

Run this command to list all the local files you modified:

.. code:: bash

	git status

You must tell git which of these files have to be synchronized, i.e. "git add" them. You can do this
by explicitly providing the list of files with:

.. code:: bash

	git add file1 file2 ... fileN

Alternatively to the previous command, if you want to add ALL edited files, you can use:

.. code:: bash

	git add . --dry-run

to check the list of all modified files, then this to actually add them:

.. code:: bash

	git add .

After adding files, you have to **commit** your changes locally with:

.. code:: bash

	git commit -m"Include an informative message here"

Finally, **push** to your remote repository, i.e. update your online fork at github, with:

.. code:: bash

	git push

You will be requested your github credentials. Note that your online password may not work; in this
case, google how to set up a github token that you can use.


10. Open a pull request
-----------------------

The easiest way to open a pull request is through the github website. Go to **your**
Pyranges fork on github, then find the "Contribute" button (near the **<> Code** button). Click
it, and select **Open pull request**.

In the newly opened page, carefully check that source and destination are correctly selected. The
Base repository should be pyranges/pyranges (i.e. the main pyranges repo), and the Head repository
should be your fork. If you worked on non-master git branches, select them here.

In the comments, write a summary of the introduced changes and their rationale, tagging any related
github issues (i.e. paste their http address). On the rest of the page, you are presented with a
list of the code edits. When you're ready, click "Open pull request".

Github will run a "check" workflow which basically replicates the steps above. If all checks are ok, 
Pyranges administrators will inspect the pull request, comment it if necessary, and potentially accept it.



11. Core team only: upload to PyPI
----------------------------------

Every now and then, the core development team considers that a new pyranges version should be
released. To do so:

- Update the version number in the pyproject.toml file
- Find the "Build and upload to PyPI" workflow in the left menu of the github actions at `https://github.com/pyranges/pyranges_1.x/actions/ <https://github.com/pyranges/pyranges_1.x/actions/>`_
- Click the "Run workflow" button on the right

Next, check that everything worked correctly, by confirming that a new pyranges installation via
pip selects the new version.

Finally, the pyranges conda package at Bioconda is updated automatically upon pip upload. Check
that this is updated correctly.

12. Assorted tips and recommended tools
---------------------------------------

While developing you might want to autorerun all the unittests and doctests if the contents of the
pyranges folder changes. You can do this with:

.. code:: bash

    ptw pyranges -- --doctest-modules pyranges/ tests/unit/

If you want to run tests in parallel, use the -n flag (only gives a speedup for the long-running
property-based tests):

.. code:: bash

    pytest -n 4 tests/property_based

Other useful tools:

* [rg](https://github.com/BurntSushi/ripgrep): ripgrep recursively searches directories for a regex pattern while respecting your gitignore
* [fd](https://github.com/sharkdp/fd): A simple, fast and user-friendly alternative to 'find'
