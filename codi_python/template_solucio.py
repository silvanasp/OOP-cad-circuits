from abc import ABC
from copy import deepcopy

# class Id():
#     id = 0
#     @staticmethod
#     def get():
#         Id.id += 1
#         return str(Id.id)

class Circuit(ABC):
    def __init__(self, name, num_inputs, num_outputs):
        self.name = name
        self.inputs = [Pin('input {} of {}'.format(i,name)) for i in range(num_inputs)]
        self.outputs = [Pin('output {} of {}'.format(i,name)) for i in range(num_outputs)]
        self.connections = []

    def rename(self, new_name):
        self.name = new_name
        for i,pin in enumerate(self.inputs):
            pin.name = 'input {} of {}'.format(i,new_name)
        for i,pin in enumerate(self.outputs):
            pin.name = 'output {} of {}'.format(i,new_name)

    def process(self):
        raise NotImplementedError
        # can not call process(), it's an abstract method

    def set_input(self, num_input, state):
        self.inputs[num_input].set_state(state)

    # def find_pin(self, name):
    #     pins = self.inputs + self.outputs
    #     names = [pin.name for pin in pins]
    #     if name in names:
    #         idx = names.index(name)
    #         return pins[idx]
    #     return None



class And(Circuit):
    def __init__(self, name, num_inputs=2):
        super().__init__(name, num_inputs, 1)

    def process(self):
        result = True
        for pin_input in self.inputs:
            result = result and pin_input.is_state()
        self.outputs[0].set_state(result)


class Or(Circuit):
    def __init__(self, name, num_inputs=2):
        super().__init__(name, num_inputs, 1)

    def process(self):
        result = False
        for pin_input in self.inputs:
            result = result or pin_input.is_state()
        self.outputs[0].set_state(result)


class Not(Circuit):
    def __init__(self, name):
        super().__init__(name, 1, 1)

    def process(self):
        self.outputs[0].set_state(not self.inputs[0].is_state())


class Component(Circuit):
    def __init__(self, name, num_inputs, num_outputs):
        super().__init__(name, num_inputs, num_outputs)
        self.circuits = []

    def add_circuit(self, circuit):
        self.circuits.append(circuit)

    def process(self):
        for circuit in self.circuits:
            circuit.process()

    # # override
    # def find_pin(self, name):
    #     pin = super().find_pin(name)
    #     if pin is None:
    #         for circ in self.circuits:
    #             pin = circ.find_pin(name)
    #             if pin is not None:
    #                 break
    #     return pin


class Observable(ABC):
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        assert observer in self.observers
        self.observers.remove(observer)
        print('{} does not observe anymore {}'\
              .format(observer.name, self.name))

    def notify_observers(self, an_object=None):
        for obs in self.observers:
            obs.update(self, an_object)
            # observable sends itself to each observer


class Observer(ABC):
    def update(self, observable, an_object):
        raise NotImplementedError
        # abstract method


class Pin(Observable, Observer):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.state = None

    def is_state(self):
        return self.state

    def set_state(self, new_state):
        self.state = new_state
        self.notify_observers(self)

    def update(self, observed_pin, an_object):
        self.set_state(observed_pin.is_state())

    def __str__(self):
        str = self.name
        if len(self.observers) > 0:
            str += ' observed by'
            for obs in self.observers:
                str += ' ' + obs.name + ' '
        return str


class Connection:
    def __init__(self, pin_from, pin_to):
        pin_from.add_observer(pin_to)
        print('{} is observer of {}'.format(pin_to.name, pin_from.name))


xor1 = Component('xor1', 2, 1)
or1 = Or('or1')
and1 = And('and1')
not1 = Not('not1')
and2 = And('and2')
# the order of adds will matter to simulation
xor1.add_circuit(or1) # more readable than xor.circuits.append(or)
xor1.add_circuit(and1)
xor1.add_circuit(not1)
xor1.add_circuit(and2)

Connection(xor1.inputs[0], and1.inputs[0])
Connection(xor1.inputs[0], or1.inputs[0])
Connection(xor1.inputs[1], and1.inputs[1])
Connection(xor1.inputs[1], or1.inputs[1])
Connection(or1.outputs[0], and2.inputs[0])
Connection(and1.outputs[0], not1.inputs[0])
Connection(not1.outputs[0], and2.inputs[1])
Connection(and2.outputs[0], xor1.outputs[0])

import copy

one_bit_adder = Component("OneBitAdder", 3, 2)
xor2 = copy.deepcopy(xor1)
xor2.rename('xor2')
and3 = And('and3')
and4 = And('and4') # or copy.deepcopy(and3) and rename
or2 = Or('or2');
# this order matters for the simulation
one_bit_adder.add_circuit(xor1)
one_bit_adder.add_circuit(xor2)
one_bit_adder.add_circuit(and3)
one_bit_adder.add_circuit(and4)
one_bit_adder.add_circuit(or2)

# connections "left to right"

A = one_bit_adder.inputs[0]
B = one_bit_adder.inputs[1]
Ci = one_bit_adder.inputs[2]
S = one_bit_adder.outputs[0]
Co = one_bit_adder.outputs[1]

input1_xor1 = xor1.inputs[0]
input2_xor1 = xor1.inputs[1]
output_xor1 = xor1.outputs[0]

input1_xor2 = xor2.inputs[0]
input2_xor2 = xor2.inputs[1]
output_xor2 = xor2.outputs[0]

input1_and3 = and3.inputs[0]
input2_and3 = and3.inputs[1]
output_and3 = and3.outputs[0]

input1_and4 = and4.inputs[0]
input2_and4 = and4.inputs[1]
output_and4 = and4.outputs[0]

input1_or2 = or2.inputs[0]
input2_or2 = or2.inputs[1]
output_or2 = or2.outputs[0]

Connection(A, input1_xor1)
Connection(B, input2_xor1)
Connection(output_xor1, input1_xor2)
Connection(Ci, input2_xor2)
Connection(output_xor1, input1_and3)
Connection(Ci, input2_and3)
Connection(A, input1_and4)
Connection(B, input2_and4)
Connection(output_and3, input1_or2)
Connection(output_and4, input2_or2)
Connection(output_xor2, S)
Connection(output_or2, Co)

inputs = []
for a in [False, True]:
    for b in [False, True]:
        for c in [False, True]:
            inputs.append([a,b,c])
expected_S = [False, True, True, False, True, False, False, True]
expected_Co = [False, False, False, True, False, True, True, True]

for (a, b, ci), exp_s, exp_co in zip(inputs, expected_S, expected_Co):
  A.set_state(a)
  B.set_state(b)
  Ci.set_state(ci)
  one_bit_adder.process()
  s = S.is_state()
  co = Co.is_state()
  print('{} + {} + {} = {}, {}'.format(a, b, ci, s, co))
  assert s == exp_s
  assert co == exp_co

#
# n bits full adder
#
n = 4 # number of one-bit adders that make one n-bits adder
one_bit_adders = []
for i in range(n):
    new_adder = deepcopy(one_bit_adder)
    new_adder.rename('oneBitAdder{}'.format(i+1))
    one_bit_adders.append(new_adder)

n_bits_adder = Component("{}BitsAdder".format(n), 2*n+1, n+1) # n As + n Bs + 1 Cin, n S + 1 Cout
for adder in one_bit_adders:
    n_bits_adder.add_circuit(adder)

# make the connections between the n-bits adder inputs and outputs, and
# the inputs and outputs of each one bit adder

# first, make references to all the pins to connect
A_n_bits_adder = []
B_n_bits_adder = []
S_n_bits_adder = []
for i in range(n):
    ...
    ...
    ...
Ci_n_bits_adder = n_bits_adder.inputs[2*n]
Co_n_bits_adder = n_bits_adder.outputs[n]

A = []
B = []
Ci = []
S = []
Co = []
for adder in one_bit_adders:
    ...
    ...
    ...
    ...
    ...

# now make all connections
for i in range(n):
    Connection(...)
    Connection(...)
    if i==0:
        Connection(...)
    Connection(...)
    if i<n-1:
        Connection(...)
    if i==n-1:
        Connection(...)

# test nbits adder

def decimal_to_boolean_list(num, num_bits):
    assert num >= 0
    # most significative bit is the leftmost
    v = [bit=='1' for bit in bin(num).replace('0b','')]
    # bin() explained here https://docs.python.org/3/library/functions.html#bin
    return [False]*(num_bits - len(v)) + v

def boolean_list_to_decimal(bool):
    # most significative bit is the leftmost
    res = 0
    num_bits = len(bool)
    for i in range(num_bits):
        res += bool[i] * 2 ** (num_bits - i - 1)
        # True*5 == 5, False*5 == 0
    return res


for carry_in in [False, True]:
    for i in range(2**n):
        a = decimal_to_boolean_list(i, n) # MSB is left-most
        for k in range(n):
            A[k].set_state(a[n-k-1]) # reverse
        for j in range(2**n):
            b = decimal_to_boolean_list(j, n)
            for k in range(n):
                B[k].set_state(b[n-k-1])
            Ci_n_bits_adder.set_state(carry_in)
            n_bits_adder.process()
            bin_res = [s.is_state() for s in S] + [Co_n_bits_adder.is_state()]
            bin_res.reverse()
            dec_res = boolean_list_to_decimal(bin_res)
            print("{} + {} + {} = {}".format(i,j,int(carry_in),dec_res))
            assert dec_res == i + j + int(carry_in)

# disconnect carry out of last 1-bit adder in the n-bits adder and
# carry out of the n-bits adder

pin_from = Co[n-1]
pin_to = Co_n_bits_adder
assert pin_to in pin_from.observers
pin_from.remove_observer(pin_to)
pin_to.set_state(False)

# now test addition of two numbers again and see that 1 + 15 + 0 = 0 etc.

