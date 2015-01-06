OOT library for the py.test runner
==================================

.. image:: https://pypip.in/v/pytest-oot/badge.png
    :target: https://crate.io/packages/pytest.oot/

.. image:: https://pypip.in/d/pytest-oot/badge.png
    :target: https://crate.io/packages/pytest-oot/

pytest-oot implements a simple way to write a test step for system test engineers.
It can be used for two ways:

- To directly use step() functions in a test_*.py file to reduce code lines
- To directly write a test_*.oot file to use a simple case/step language

The module is still under development. The following features will be added in:

- A hook to register logging for both pass/fail steps or cases
- Implement the mix-scripting in case file by using both python language and oot case/step format
- A hook to add new operators to enhance the conditions judgement
- A hook to add more options for steps

You can download the whole package to get the examples



Install pytest-oot
------------------

::

    pip install pytest-oot


Example for using step functions in a test_*.py
-----------------------------------------------

This is an easy way to use it, and options provide some tests specific functions.
The step functions include step(), steps() and s().
The format of a step looks like::

    obj.method(parameter) op exp-value options

In this one step, there is an action, and also a check point
This one step can be translated to multiple lines of python code,
or dozens lines of code if there is one option or multiple options.

How to import::

    from pytest_oot.oot_step import step, steps, s


Examples (Quick Start):

1.  The Simplest step:

    .. code-block:: python

        step("num1.add(3,4,5) == 23")

    It is similar as:

    .. code-block:: python

        assert num1.add(3,4,5) == 23

    very simple, right? (we do not consider advanced features here, e.g.
    auto-logging)


2.  Step with non-python-defined operators

    .. code-block:: python

        step("string1.range(1..4) !~ r'\w\-\w'")

    Perl-like condition, =~ means 'contains', and !~ means 'not contains'.
    btw, regex can be used. The step is like:

    .. code-block:: python

        import re
        assert not re.compile(r'\w\-\w').find(string1.range(1..4))

3.  Step with timeout option

    .. code-block:: python

        step("num_async.data_sync() -t 15")

    A little complicated, -t means timeout. In this step, a time-out timer
    is set to 15 seconds. It means this step is allowed to be completed
    in 15 seconds, otherwise, it fails. no op (==, <, >, =~, etc.) in this step,
    it means no assert required to check the return value

    This is implemented by forking another thread to run the step.
    Considering some tests require to wait for a response, but how long?
    this can be useful

4.  Step with repeat option:

    .. code-block:: python

        step("num_async.get_value() == 500 --repeat 20")

    Another option --repeat (same as -r).
    The step means the step will be re-run every another second
    in total 20 seconds, until the condition comes true

    If the condition is always false in 20 seconds, then the step fails

5.  Step with multiple options

    .. code-block:: python

        step("num2.multiple(4,5) == 460 -x True -t 12 -r 10")

    Multiple options for one step ::

        -x (--expectedfail): pass if the condition is not met
        -t (--timeout): set a timeout timer
        -r (--repeat): repeat this step in 10 seconds until it comes true
           (here false actually due to -x), or timeout

6.  Use steps function to execute multiple steps

    .. code-block:: python

        steps('''
            num1.add(4)
            num2.add(3,4,5,6) == 23
            num2.multiple(4,5) == 460 -x True -t 12 -r 10
            num3.add(3,4,var2) == 1000 --skip -t 20
        ''')

7. Or you are lazy, just use s function like this:

    .. code-block:: python

       s("num2.multiple(4,5) == 460 -x True -t 12 -r 10")
       s('''
            num1.add(4)
            num2.add(3,4,5,6) == 23
            num2.multiple(4,5) == 460 -x True -t 12 -r 10
            num3.add(3,4,var2) == 1000 --skip -t 25
        ''')


Example for test_*.oot file
---------------------------

Once the plug-in is installed, the pytest will automatically collect test_*.oot files
to get cases, and run each items in the files. In a test_*.oot file, each case is
a test item, and each line under it is a test step.


Example file: test_number.oot (you can get it from the source package)
----------------------------------------------------------------------

.. code-block:: python

    # Any words after # in a line are just comments
    # One file is a test suite. The test suite description
    test_suite: Trial1

    # Identify the test bed file, currently .py file is supported
    # similar as 'import testbed.py' in test*.py file
    test_bed: example.test.testbed

    # A case starts from a case_idString, the description is in the bracket
    # This is to define one case, just like a function or method in a .py file
    # case_id1 means the function name is "id1"
    case_id1 (NumberBase add function):
        # under a case, there could be multiple test steps, one step in one line
        # step format: obj.method(parameters) operator expected_result options
            # obj/methods are defined in test bed file
            # operator supports:
            #   ==(equal to), !=(not equal to), >(larger than), <(less than), >=, <=,
            #   =~(for string, contains, e.g. "hello world" =~ "llo", regex allowed
            #   !~ (not contain)
        num1.add(3,4,5,6) == 23 -t 3
        num1.add(var1, var2, var3) == 18

    case_id2 (NumberBase multiple function):
        num1.multiple(2,4,5) == 200

    case_id3 (NumberChange test):
        # Every line under the case line is a step of a case
        # there could be multiple lines; each line follows the format:
        #   obj.method([parameter1 [,parameter 2 [, ...]]] operator ExpectedValue -options
        # For details, see guidance ....
        # options:
        # --timeout 30 == -t 30: fail if the step could not complete in 30 seconds
        # --repeat 30 == -r 30: repeat per second if fail until pass, timeout in 30s
        # --duration 30 == -d 30: duration of the step is 30s, if completed early, just wait until 30s
        # --expectedfail == -x true == -x: If step fail, then report pass
        # --skip == -s: just skip this step
        #
        num1.add(4)
        num2.add(3,4,5,6) == 23
        num2.multiple(4,5) == 460 -x True -t 12 -r 10
        num3.add(3,4,var2) == 1000 --skip -t 25

    case_id4 (Reverse String test):
        string1.range(1,4) == 'dlr' -d 6

    case_async1 (To test async actions - timeout)
        num_async.addw(var100, var100) == 100
        num_async.data_sync() -t 18
        num_async.get_value() == 300

    case_async2 (To test async actions - repeat)
        num_async.addw(var100, var100) >= 300
        num_async.get_value() == 500 --repeat 20

Note: If it reports the testbed module could not be imported, please change the module path
to make it right.



Operators & Options
-------------------

Sometimes it is needed to declare the same fixtures or steps with the
different names for better readability. In order to use the same step

Supported Operators by default:
    ==, !=, <. >, <=, >=, =~, !~

Supported Options by default::

    # --timeout 30 == -t 30: fail if the step could not complete in 30 seconds
    # --repeat 30 == -r 30: repeat per second if fail until pass, timeout in 30s
    # --duration 30 == -d 30: duration of the step is 30s, if completed early,
      just wait until 30s
    # --expectedfail == -x true == -x: If step fail, then report pass
    # --skip == -s: just skip this step



Test bed
--------

If you use step functions in a .py file, it is required to make sure the objects in the step string
are in the module's name space.

If you are using a test_*.oot file, you need to use::

    testbed = [module.]testbedfilename

to import all the objects defined in the testbedfilename.py file.




Hooks
-----

pytest-oot is to support multiple hooks for operator, logs, and options next.
Please send mails to steven004@gmail.com if you have any comments or suggestions


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_.

© 2014 Steven LI

