"""
This is to implement a function called step(), and a bunch-function steps() or s():
The format of a step looks like:
    obj.method(parameter) op exp-value options
In this one step, there is an action, and also a check point
This one step can be translated to multiple lines of python code,
or dozens lines of code if there is one option or multiple options.

How to import:
from pytest_oot import step, steps, s

Examples (Quick Start):
1.  step("num1.add(3,4,5) == 23")
    the same as:
        assert num1.add(3,4,5) == 23
very simple, right?

2.  step("string1.range(1..4) !~ r'\w\-\w'")
    Perl-like condition, =~ means 'contains', and !~ means 'not contains'
            btw, regex can be used
    The step is like:
        import re
        assert re.compile(r'\w\-\w').find(string1.range(1..4))

3.  step("num_async.data_sync() -t 15")
    a little complicated, -t means timeout. In this step, a time-out timer is set to 15 seconds.
    It means this step is allowed to be completed in 15 seconds, otherwise, it fails.
    no op (==, <, >, =~, etc.) in this step, it means no assert required to check the return value

    This is implemented by forking another thread to run the step.
    Considering some tests require to wait for a response, but how long? this can be useful

4.  step("num_async.get_value() == 500 --repeat 20")
    Another option --repeat (same as -r).
    The step means the step will be re-run every another second in total 20 seconds,
        until the condition comes true
    If the condition is always false in 20 seconds, then the step fails

5.  step("num2.multiple(4,5) == 460 -x True -t 12 -r 10")
    Multiple options for one step.
        -x (--expectedfail): pass if the condition is not met
        -t (--timeout): set a timeout timer
        -r (--repeat): repeat this step in 10 seconds until it comes true(here false actually due to -x), or timeout
6.  steps('''
        num1.add(4)
        num2.add(3,4,5,6) == 23
        num2.multiple(4,5) == 460 -x True -t 12 -r 10
        num3.add(3,4,var2) == 1000 --skip -t 25
    ''')
    multiple steps in one shot
7. Or you are lazy, just use s function like this:
   s("num2.multiple(4,5) == 460 -x True -t 12 -r 10")
   s('''
        num1.add(4)
        num2.add(3,4,5,6) == 23
        num2.multiple(4,5) == 460 -x True -t 12 -r 10
        num3.add(3,4,var2) == 1000 --skip -t 25
    ''')
"""


__author__ = 'Steven LI'

import time
import threading
import re
from inspect import getmodule, currentframe
#import pytest

def step(step_string, test_module=None, parent=None):
    __tracebackhide__ = True
    step = step_string.strip()
    if len(step) == 0: return
    if step[0] == '#': return

    if not test_module:
        test_module = getmodule(currentframe().f_back)
    test_step = TestStep(step_string, test_module, parent)
    test_step.parse()
    test_step.execute()

def steps(step_strings):
    __tracebackhide__ = True
    step_list = step_strings.split('\n')
    test_module = getmodule(currentframe().f_back)
    for step_string in step_list:
        step(step_string, test_module)

# a short-style of steps function
s = steps

class TestStep:
    '''A test step class, to deal with all test step related actions'''
    def __init__(self, step_string, test_module, parent=None):
        self.__default_set__()

        self.step_namespace = test_module.__dict__

        self.step_string_o = step_string
        self.step_string = step_string.strip()
        self.parent = parent
        #self.parse()

    def __default_set__(self):
        #self.obj   # the obj string
        #self.method    # the method string
        self.func = None  # the actual function object to be invoked (not the string)
        self.params = ()    # the list of parameters
        self.op = None
        self.exp_value = None
        self.options = {
            # 0: no timeout setting; others, raise Timeout exception if no return in Timeout seconds
            # --timeout   == -t
            "Timeout": 0,

            # 0: no duration setting; Stay on this step for xxx seconds if not 0
            # --duration == -d
            "Duration": 0,

            # Ture: this step is expected to fail
            # --expectedfailure  == -x
            "ExpectedFailure": False,

            # Repeat this step until expected value returned, the number setting means timeout seconds
            # --repeat  == -r
            "RepeatInSeconds": 0,

            # To skip this step
            # --skip  == -s
            "Skip": False
        }

    def execute(self):
        __tracebackhide__ = True
        if self.options["Skip"]: return
        end_time = time.time() + self.options["Duration"]
        if self.options["Timeout"] > 0 :
            t = threading.Thread(target = self.__execute)
            t.start()
            t.join(self.options["Timeout"])
            if t.is_alive():
                raise TestStepFail(self.step_string, self.__result_exp__("Timeout"))
        else:
            self.__execute()

        ## Deal with the Duration Options
        wait_seconds = end_time - time.time()
        if wait_seconds >0: time.sleep(wait_seconds)


    def __execute(self):
        __tracebackhide__ = True
        if self.options["RepeatInSeconds"] > 0:
            end_time = time.time() + self.options["RepeatInSeconds"]
            while (time.time() < end_time) :
                self.ret = self.func(*self.params)
                if self.__step_pass() :
                    return
                time.sleep(1)
            raise TestStepFail(self.step_string, self.__result_exp__())
            #pytest.fail("really failed. .... ", True)
        else :
            self.ret = self.func(*self.params)
            if not self.__step_pass():
                raise TestStepFail(self.step_string, self.__result_exp__())
                #pytest.fail("failed ........", True)

    def __result_exp__(self, msg = None):
        m = re.compile(r'(\s*)\w.*').match(self.step_string_o)
        if msg:
            return m.group(1) + msg
        else:
            return m.group(1) + '%r %s %s' %(self.ret, self.op, self.exp_value)

    def __step_pass(self):  # deal with the ExpectedFailure option
        if not self.op: return True
        if self.options["ExpectedFailure"] :
            return (not self.step_pass())
        else :
            return self.step_pass()

    def step_pass(self):
        ret_val = self.ret
        if self.exp_value == None: #There is an operator, but no expected value
            raise TestRunTimeError(self.step_string, self.__result_exp__("Expected_value required"))

        if isinstance(ret_val, str):
            if self.op in ['=~', '!=']:
                l = re.compile(self.exp_value).find(ret_val)
                return True if (self.op == '=~' and l) or (self.op == '!~' and not l) else False
            else: # for ==, !=, <, >, <= and >= of strings
                return eval('ret_val' + self.op + self.exp_value)
        elif isinstance(ret_val, float):
            import math
            try:
                exp_value_f = float(self.exp_value)            # The expected result is a number?
            except ValueError:
                raise TestRunTimeError(self.step_string, self.__result_exp__("expected value is expected to be a float"))
            if self.op in ['<', '<=', '>', '>=']:
                return eval('ret_val' + self.op + 'exp_value_f')
            elif self.op == '==': # to see if they are very close
                return math.fabs(ret_val - exp_value_f) < 1.0e-6  # precise 1.0e-6
            elif self.op == '!=' :
                return math.fabs(ret_val - exp_value_f) > 1.0e-6  # precise 1.0e-6
            else:
                raise TestRunTimeError(self.step_string, self.__result_exp__("Wrong operator for a float"))
        elif isinstance(ret_val, int):
            if not re.compile(r"\d*(\.\d+)?").match(self.exp_value):
                raise TestRunTimeError(self.step_string, self.__result_exp__("expected value is expected to be a integer"))
            if self.op in ['<', '<=', '>', '>=', '==', '!=']:
                return eval('ret_val' + self.op + self.exp_value)
            else:
                raise TestRunTimeError(self.step_string, self.__result_exp__("Wrong operator for a float"))


    def parse(self):
        __tracebackhide__ = True
        regex = re.compile(r'(\w+)\.(\w+)\s*(\(.*\))(.*)$')
        m = regex.match(self.step_string)
        (self.obj, self.method, param_str, p_f) = m.group(1,2,3,4)
        #obj = getattr(self.objs, self.obj)
        obj = self.step_namespace[self.obj]
        self.func = getattr(obj, self.method)
        try: #if wrong, just keep null list
            self.params = eval(param_str[0:-1] + ",)", self.step_namespace, {})  # the list of parameters
        except:
            self.params = ()
        p_f = p_f.strip()

        if len(p_f) != 0 and p_f[0] != '#':
            try:
                m = re.compile(r'(==|!=|<=|>=|<|>|=~|!~)\s*(\"[^\"]+\"|\'[^\']+\'|\S+)(.*)$').match(p_f)
                (self.op, self.exp_value, options) = m.group(1,2,3)
                options = options.strip()
            except:
                options = p_f

            if len(options) != 0 and options[0] != '#':
                ol = re.compile(r'(?<!^)\s+(?=(?:-\w|--\w{2,}))').split(options)
                for o in ol:
                    if o[0] != '-' :
                        raise TestRunTimeError(self.step_string, self.__result_exp__("wrong options: "+o))
                    if o[1] == '-': # It is a long option string
                        r = re.compile(r'--(\w+)\s*(\S*)$').match(o)
                        if r.group(1) == "timeout":
                            self.options['Timeout'] = int(r.group(2))
                        elif r.group(1) == "duration":
                            self.options['Duration'] = int(r.group(2))
                        elif r.group(1) == 'expectedfailure':
                            if len(r.group(2))==0 or r.group(2)[0] in "TtYy":
                                self.options['ExpectedFailure'] = True
                        elif r.group(1) == 'skip':
                            if len(r.group(2))==0 or r.group(2)[0] in "TtYy":
                                self.options['Skip'] = True
                        elif r.group(1) == 'repeat' :
                            self.options['RepeatInSeconds'] = int(r.group(2))
                        else: raise TestRunTimeError(self.step_string, self.__result_exp__("wrong options: "+o))
                    else:
                        key = o[1]
                        if len(o) > 2: value = o[2:].strip()
                        else: value = ''
                        if key == "t":
                            self.options['Timeout'] = int(value)
                        elif key == "d":
                            self.options['Duration'] = int(value)
                        elif key == 'x':
                            if len(value)==0 or value[0] in "TtYy":
                                self.options['ExpectedFailure'] = True
                        elif key == 's':
                            if len(value)==0 or value[0] in "TtYy":
                                self.options['Skip'] = True
                        elif key == 'r' :
                            self.options['RepeatInSeconds'] = int(value)
                        else: raise TestRunTimeError(self.step_string, self.__result_exp__("wrong options: "+o))


class TestStepFail(Exception):
    """ custom exception for error reporting. """

class TestRunTimeError(Exception):
    """ custom exception for error reporting. """


