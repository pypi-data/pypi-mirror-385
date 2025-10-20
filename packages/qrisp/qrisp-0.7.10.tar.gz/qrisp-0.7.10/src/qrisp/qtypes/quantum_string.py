"""
********************************************************************************
* Copyright (c) 2025 the Qrisp authors
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* This Source Code may also be made available under the following Secondary
* Licenses when the conditions for such availability set forth in the Eclipse
* Public License, v. 2.0 are satisfied: GNU General Public License, version 2
* with the GNU Classpath Exception which is
* available at https://www.gnu.org/software/classpath/license.html.
*
* SPDX-License-Identifier: EPL-2.0 OR GPL-2.0 WITH Classpath-exception-2.0
********************************************************************************
"""

import numpy as np

from qrisp.core.quantum_array import QuantumArray
from qrisp.qtypes.quantum_char import QuantumChar

nisq_init_quantum_char = QuantumChar(name="nisq_q_char")
init_quantum_char = QuantumChar(nisq_char=False, name="q_char")


class QuantumString(QuantumArray):
    """
    The QuantumString is the quantum equivalent of a string. It is implemented as a
    :ref:`QuantumArray` of :ref:`QuantumChars <QuantumChar>`.

    >>> from qrisp import QuantumString
    >>> q_str = QuantumString(size = len("hello world"))
    >>> q_str[:] = "hello world"
    >>> print(q_str)
    {'hello world': 1.0}

    It is also possible to have a QuantumString containing non-nisq chars

    >>> q_str_nn = QuantumString(size = len("hello world"), nisq_char = False)
    >>> q_str_nn[:] = "hello world"
    >>> print(q_str_nn)
    {'hello world': 1.0}

    This requires however considerably more qubits

    >>> print(len(q_str.qs.qubits))
    55
    >>> print(len(q_str_nn.qs.qubits))
    88

    Similar to its parent class, the size of a QuantumString does not have to be
    specified at creation

    >>> q_str = QuantumString()
    >>> q_str[:] = "hello world"
    >>> print(q_str)
    {'hello world': 1.0}

    **Concatenation**

    QuantumStrings provide a number of methods to concatenate:

    >>> q_str_0 = QuantumString()
    >>> q_str_1 = QuantumString()
    >>> q_str_2 = QuantumString()
    >>> q_str_0[:] = "hello"
    >>> q_str_1 += " "
    >>> q_str_2[:] = "world"
    >>> q_str_3 = q_str_1 + q_str_2
    >>> q_str_0 += q_str_3
    >>> print(q_str_0)
    {'hello world': 1.0}

    Note that these QuantumStrings share memory - i.e. if we modify a QuantumChar in one
    of them, this will potentially affect the others:

    >>> from qrisp import h
    >>> h(q_str_2[0][0])
    >>> print(q_str_0)
    {'hello world': 0.5, 'hello xorld': 0.5}

    """

    def __init__(self, size, qs=None, nisq_char=True):
        if nisq_char:
            qtype = nisq_init_quantum_char
        else:
            qtype = init_quantum_char

        QuantumArray.__init__(self, qtype=qtype, shape=size, qs=qs)

    def get_measurement(self, **kwargs):
        mes_result = QuantumArray.get_measurement(self, **kwargs)

        return_dic = {}

        for k, v in mes_result.items():
            return_dic["".join(list(k))] = v

        return return_dic

    def decoder(self, code_int):
        res_array = QuantumArray.decoder(self, code_int)
        res_str = ""

        for i in range(len(res_array)):
            res_str += res_array[i]

        return res_str

    def encode(self, encoding_str):
        encoding_array = np.array(list(encoding_str), dtype="object")
        QuantumArray.encode(self, encoding_array)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            QuantumArray.__setitem__(self, key, value)
            return

        QuantumArray.__setitem__(self, key, [ch for ch in value])

    @classmethod
    def quantize_string(cls, string):
        res = QuantumString(len(string))
        res[:] = string
        return res

    def __add__(self, other):
        return self.concatenate(other)

    def __iadd__(self, other):
        if isinstance(other, QuantumString):
            return self + other

        elif isinstance(other, str):
            return self + QuantumString.quantize_string(other)

        else:
            raise Exception(f"Don't know how to concatenate with type {type(other)}")
