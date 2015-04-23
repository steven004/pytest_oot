"""
    pytest_oot
    ~~~~~~~~~~~~~~~

    Helpers for defining a simple format for object-oriented system-level testing
    The design is implemented taking pytest_yamlwsgi as a reference.

    :copyright: 2014-2015 Steven LI <steven004@gmail.com>
    :license: MIT

    This module is presented as a py.test plugin. It provides two main features:

        1. Provide a method to easy write test scripts in a plain format, easy to review and work, and
        2. Provide some options for test steps to simplify the test scripts writing. It could make 10 lines python code in one line

    How it works
    ------------

    py.test has a number of hooks that can be accessed to extend its
    behaviour. This plugin uses the `pytest_collect_file` hook which is called
    wih every file available in the test target. The first action of the
    hook-handler is that it checks if the filename is of the form `test*.oot`,
    here oot means object-oriented test since in the script file, every step is
    based on an object to take an action and compare the result.

    If it finds an appropriate file, the hook-handler will generate a number
    of tests based on that file. py.test provides a hierarchical system of
    tests. The top-level of this hierarchy is an object representing the oot
    file itself. The lower components are represented by further test
    containers, and subsequent individual tests.

    The test*.oot file is just like a test*.py file, but in different format, Let's
    see an example first. (you can get the code from the package source)
        # Any words after # in a line are just comments
        test_suite: Trial1
        # Identify the test bed file, currently .py file is supported
        # similar as 'import testbed.py' in test*.py file
        test_bed: testbed

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
            num1.multiple(2,4,5) == 100

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
            num2.add(3,4,5,6) == 478
            num2.multiple(4,5) == 460 -x True -t 12 -r 10
            num3.add(3,4,var2) == 1000 --skip -t 25

        case_id4 (Reverse String test):
            string1.range(1,4) == 'dlr' -d 6

        case_async1 (To test async actions - timeout)
            num_async.addw(var100, var100) == 100
            num_async.data_sync() -t 15
            num_async.get_value() == 300

        case_async2 (To test async actions - repeat)
            num_async.addw(var100, var100) >= 300
            num_async.get_value() == 500 --repeat 20


    Each case of the test suite should be a subclass of:class:`py.test.collect.Item`,
    which is a direct subclass, for leaf tests, implementing `runtest()`.

"""


__author__ = 'Steven LI'

import test_steps
import pytest


def pytest_configure(config):
    test_steps.auto_func_detection(False)


def pytest_collect_file(parent, path):
    if path.ext == ".oot" and path.basename.startswith("test"):
        return TestCaseFile(path, parent)

class TestCaseFile(pytest.File):
    # test_bed: the test bed file
    # test_cases: an array of the test cases

    def collect(self):
        suite_content = self.fspath.open().read()
        self.__parse_suite(suite_content)

        # Import objects in the test bed
        if self.test_bed != None:
            #self.objs = __import__(self.test_bed, globals())
            import importlib
            self.objs = importlib.import_module(self.test_bed)

        current_line_number = 0
        case_number = 0
        for case in self.cases:
            case_id = case[0:case.find(' ')]
            current_line_number += self.case_lines[case_number]
            case_number += 1
            yield TestCaseItem(case_id, self, case, current_line_number)

    def __parse_suite(self, suite_content):
        ''' To parse the system case file, see detail of the system test file example
        :param suite_content: The content of the test case file.
        :return: no return, exception will be raised if the format is not right
        '''

        # split cases, notice that the first element of the cases is about the test suite description
        cases = suite_content.split("\ncase_")
        self.case_lines = [c.count('\n')+1 for c in cases]

        # Deal with the test suite description; cases[0] is about the test suite summary
        self.name = 'unknown'
        self.test_bed = None
        self.suite_attr = {}
        self.cases = cases[1:]
        header = cases[0].split("\n")
        for line in header:
            line = line.strip()
            if len(line) == 0: continue
            if line[0] == '#': continue
            colon = line.find(':')
            if colon == -1: continue
            (name, spec) = (line[0:colon], line[colon+1:].strip())
            if name == 'test_suite':
                self.name = spec
            elif name == 'test_bed':
                self.test_bed = spec
            else:
                self.suite_attr[name] = spec


class TestCaseItem(pytest.Item):
    ''' A case structure, one case can contain multiple steps
    '''
    # def __init__(self, name, parent, case_dec, steps):
    #     super(TestCaseItem, self).__init__(name, parent)
    #     self.case_dec = case_dec
    #     self.steps = steps

    def __init__(self, case_id, parent, case_string, line_number):
        super(TestCaseItem, self).__init__(case_id, parent)
        header_end = case_string.find('\n')
        self.case_header = case_string[0:header_end].strip()
        self.steps = case_string[header_end:].split('\n')
        self.first_line = line_number
        self.parent = parent
        #m = re.match(r'(\w+)\s*\((.*)\)', line1)
        #(case_id, case_dec) = m.group(1,2)

    def runtest(self):
        self.current_step = 0
        for step_string in self.steps:
            #step_string = step_string.strip()
            #if len(step_string) == 0: continue
            #if step_string[0] == '#': continue
            #step_obj = TestStep(step, self) # To create a step_obj with parsing
            #step_obj.execute()
            test_steps.steps(step_string, self.parent.objs.__dict__)

            self.current_step += 1


    def runtest_setup(item):
        test_steps.log_new_func(item.name, str(item.fspath) )


    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """

        failed_line_number = self.first_line + self.current_step + 1

        fail_string = "case_" + self.case_header + "\n".join(self.steps[0:self.current_step])
        cur_step_str = self.steps[self.current_step]
#       fail_string += '\n>' + self.steps[self.current_step][1:]
        fail_string += '\n>' + cur_step_str[1:]
        fail_string += "\nE" + ' ' * (len(cur_step_str) - len(cur_step_str.lstrip()) - 1) + excinfo.value.args[1]

        fail_string += "\n\n%s:" % self.parent.fspath + "%d" % failed_line_number

        # if isinstance(excinfo.value, TestStepFail):
        #     fail_string += ": TestStepFail"
        #
        # elif isinstance(excinfo.value, TestRunTimeError):
        #     fail_string += ": TestRunTimeError"
        fail_string += ": " + excinfo.value.__class__.__name__

        return fail_string

    def reportinfo(self):
        ''' Called when there is a failure as a failed case title'''
        return self.fspath, 0, "%s" % self.case_header
