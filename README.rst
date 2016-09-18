OOT library for the py.test runner
==================================

.. image:: https://pypip.in/v/pytest-oot/badge.png
    :target: https://crate.io/packages/pytest.oot/

.. image:: https://pypip.in/d/pytest-oot/badge.png
    :target: https://crate.io/packages/pytest-oot/

pytest-oot implements a simple way to write a test step for test engineers.
This plug-in use test_steps module to implement the whole things.

The test engineer can simply create test_*.oot file to use a simple case/step language,
by using the operators and options defined in test_steps module, or user-defined by you.

For detailed operators and options for steps, please refer to test_steps module:
    https://pypi.python.org/pypi?:action=display&name=test_steps


Note: while using this plug-in,
you do not need pytest-autochecklog any more. All functions have been included.


Install pytest-oot
------------------

::

    pip install pytest-oot



Example for test_*.oot file
---------------------------

Once the plug-in is installed, the pytest will automatically collect test_*.oot files
to get cases, and run each items in the files. In a test_*.oot file, each case is
a test item, and each line under it is a test step. For each test step, the syntax is
the same as a code string in checks("code string") function defined in test_steps module.



Example file: test_number.oot (you can get it from the source package)
----------------------------------------------------------------------

.. code-block:: python

    # Any words after # in a line are just comments
    # One file is a test suite. The test suite description
    test_suite: Trial1

    # Identify the test bed file, currently .py file is supported
    # similar as 'import testbed.py' in test*.py file
    # .yaml file is support too. You can use: (see more information in TestSteps package)
    # test_bed: example.test.testbed.yaml
    test_bed: example.test.testbed.py

    # A case starts from a case_idString, the description is in the bracket
    # This is to define one case, just like a function or method in a .py file
    # case_id1 means the function name is "id1"
    case_id1 (NumberBase add function):
        # under a case, there could be multiple test steps, one step in one line
        # step format: expression1 operator expression2 options
            # An expression can use any objects defined in test bed file
            # operator supports:
            #   ==(equal to), !=(not equal to), >(larger than), <(less than), >=, <=,
            #   =~(for string, contains, e.g. "hello world" =~ "llo", regex allowed
            #   !~ (not contain)
        # the following step is just like:
        #   checks( "num1.add(3,4,5,6) == 23 -t 3" )
        # in a python file, in which test_steps module is used.
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

Note: the testbed file is a python file, which define all the variables and objects to be used in the test.
If it reports the testbed module could not be imported, please change the module path
to make it right.


Operators & Options
-------------------

Supported Operators by default:
    == (eq), != (ne), < (lt), > (gt), <= (le), >=(ge), =~(match), !~(unmatch), =>(has), !>(hasnt)

Again, all operators defined in test_steps are supported, and you can also define them by yourself.


Supported Options by default::

    -t 30   or --timeout 30    in checks()             means       timeout=30    in check()
    -r 10   or --repeat  10    in checks()             means       repeat=10
    -d 10   or --duration 10                          means       duration=10
    -x  or --xfail or -x True or --xfail True         means       xfail=True
    -w  or --warning  or -w True  or --warning True   means       warning=True
    -s  or --skip     or -s True  or --skip True      means       skip=True
    -e MyException                                    means       exception=MyException
    -p pass_str or --passdesc pass_str                means       passdesc=pass_str
    -f fail_str or --faildesc fail_str                means       faildesc=fail_str


Test bed
--------

If you are using a test_*.oot file, you need to use

::

    testbed = [module.]testbedfilename

to import all the objects defined in the testbedfilename.py file.



Example for using step functions in a test_*.py
-----------------------------------------------

Of course, you can directly use test_steps functions in your test_*.py test scripts files.
Please refer to test_steps module for details. Some basic examples as below:


Examples (Quick Start):

1.  The Simplest step:

    .. code-block:: python

        check("num1.add(3,4,5) == 23")

    It is similar as:

    .. code-block:: python

        assert num1.add(3,4,5) == 23

    very simple, right? (we do not consider advanced features here, e.g.
    auto-logging)


2.  Step with non-python-defined operators

    .. code-block:: python

        check("string1.range(1..4) !~ r'\w\-\w'")

    Perl-like condition, =~ means 'contains', and !~ means 'not contains'.
    btw, regex can be used. The step is like:

    .. code-block:: python

        import re
        assert not re.compile(r'\w\-\w').find(string1.range(1..4))

3.  Step with timeout option

    .. code-block:: python

        check("num_async.data_sync() -t 15")

    A little complicated, -t means timeout. In this step, a time-out timer
    is set to 15 seconds. It means this step is allowed to be completed
    in 15 seconds, otherwise, it fails. no op (==, <, >, =~, etc.) in this step,
    it means no assert required to check the return value

    This is implemented by forking another thread to run the step.
    Considering some tests require to wait for a response, but how long?
    this can be useful

4.  Step with repeat option:

    .. code-block:: python

        check("num_async.get_value() == 500 --repeat 20")

    Another option --repeat (same as -r).
    The step means the step will be re-run every another second
    in total 20 seconds, until the condition comes true

    If the condition is always false in 20 seconds, then the step fails

5.  Step with multiple options

    .. code-block:: python

        check("num2.multiple(4,5) == 460 -x True -t 12 -r 10")

    Multiple options for one step ::

        -x (--expectedfail): pass if the condition is not met
        -t (--timeout): set a timeout timer
        -r (--repeat): repeat this step in 10 seconds until it comes true
           (here false actually due to -x), or timeout

6.  Use steps function to execute multiple steps

    .. code-block:: python

        checks('''
            num1.add(4)
            num2.add(3,4,5,6) == 23
            num2.multiple(4,5) == 460 -x True -t 12 -r 10
            num3.add(3,4,var2) == 1000 --skip -t 20
        ''')

7. Or you are lazy, just use s function like this:

    .. code-block:: python

       c("num2.multiple(4,5) == 460 -x True -t 12 -r 10")
       c('''
            num1.add(4)
            num2.add(3,4,5,6) == 23
            num2.multiple(4,5) == 460 -x True -t 12 -r 10
            num3.add(3,4,var2) == 1000 --skip -t 25
        ''')


Note: each line of the code strings in the checks functions can be a step in test_*.oot file.


Hooks
-----

pytest-oot is to support multiple hooks for operator, logs, and options, refer to test_steps.
Please send mails to steven004@gmail.com if you have any comments or suggestions


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_.

© 2015 Steven LI

