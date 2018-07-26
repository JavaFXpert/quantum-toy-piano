#
# Copyright 2018 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from flask import Flask, jsonify, request
from flask_cors import CORS
from pyquil.quil import Program
from pyquil.quilbase import RawInstr, Pragma
from collections import deque
import pyquil.api as api
from pyquil.gates import *
from math import *
import copy
from s04_rotcircuit import *

#FOR COMPILERCONNECTION
from pyquil.api import CompilerConnection, get_devices

# compiler = CompilerConnection(quantum_device)
# devices = get_devices(as_dict=True)
# print(devices)
# quantum_device = devices['8Q-Agave']


app = Flask(__name__)
CORS(app)

DEGREES_OF_FREEDOM = 6
NUM_PITCHES = 4
DIATONIC_SCALE_OCTAVE_PITCHES = 8
NUM_CIRCUIT_WIRES = 3
TOTAL_MELODY_NOTES = 7
# RY_RAD_ADJ_MELODY = -np.pi/8  # adjustment in radians to each RY rotation in the circuit to compensate for QPU inaccuracies
RY_RAD_ADJ_MELODY = 0
RY_RAD_ADJ_HARMONY = 0

###
# Produces a musical (specifically second-species counterpoint) composition for
# a given initial pitch, and melodic/harmonic rotations degrees. This operates in a degraded mode,
# in that a call to the quantum computer or simulator is made for each note in the resulting
# composition.
#    Parameters:
#        pitch_index Index (0 - 3) of the initial pitch for which a composition is desired. This determines
#                    the mode (Ionian, Dorian, etc.) of the composition
#        species Number (1 - 3) representing the species of counterpoint desired
#        melodic_degrees Comma-delimited string containing 28 rotations in degrees for melody matrix
#        harmonic_degrees Comma-delimited string containing 28 rotations in degrees for harmony matrix
#
#    Returns JSON string containing:
#        melody_part
#            pitch_index
#            start_beat
#            pitch_probs
#        harmony_part
#            pitch_index
#            start_beat
#            pitch_probs
#
#        pitch_index is an integer from (0 - 7) resulting from measurement
#        start_beat is the beat in the entire piece for which the note was produced
#        pitch_probs is an array of eight probabilities from which the pitch_index resulted
###

@app.route('/toy_piano_counterpoint')
def toy_piano_counterpoint():
    pitch_index = int(request.args['pitch_index'])
    pitch_index %= (DIATONIC_SCALE_OCTAVE_PITCHES - 1)
    if pitch_index >= NUM_PITCHES:
        pitch_index = 0

    species = int(request.args['species'])
    print("species: ", species)

    melodic_degrees = request.args['melodic_degrees'].split(",")
    print("melodic_degrees: ", melodic_degrees)

    harmonyenabled = True
    harmonic_degrees = []
    harmonic_degrees_str = request.args['harmonic_degrees']
    if len(harmonic_degrees_str) > 0:
        harmonic_degrees = harmonic_degrees_str.split(",")
    else:
        harmonyenabled = False
    print("harmonic_degrees: ", harmonic_degrees)

    use_simulator = request.args['use_simulator'].lower() == "true"
    print("use_simulator: ", use_simulator)

    compiler = None
    quantum_device = None
    q_con = None

    melody_note_nums = []
    harmony_note_nums = []
    ret_dict = {}

    if use_simulator:
        q_con = api.QVMConnection()
    else:
        quantum_device = available_quantum_device()
        if quantum_device is not None:
            print('quantum_device: ', quantum_device)
            compiler = CompilerConnection(quantum_device)
            q_con = api.QPUConnection(quantum_device)

            # q_con = api.QVMConnection()
        else:
            # TODO: Test this condition
            print('No quantum devices available, using simulator')
            use_simulator = True
            q_con = api.QVMConnection()

    if (len(melodic_degrees) == DEGREES_OF_FREEDOM and
            (len(harmonic_degrees) == DEGREES_OF_FREEDOM or not harmonyenabled) and
            0 <= species <= 3 and
            0 <= pitch_index < NUM_PITCHES):

        #TODO: Move/change this
        rot_melodic_circuit = compute_circuit(melodic_degrees)

        if not use_simulator:
            # TODO: Put back in
            # rot_melodic_circuit = compiler.compile(rot_melodic_circuit)

            # TODO: Remove these lines
            tmp_rot_melodic_circuit = compiler.compile(rot_melodic_circuit)
            # print("tmp_rot_melodic_circuit:")
            # print(tmp_rot_melodic_circuit)
            rot_melodic_circuit = Program()
            for instruction in tmp_rot_melodic_circuit.instructions:
                if not isinstance(instruction, Pragma):
                    rot_melodic_circuit.inst(instruction)

        print("rot_melodic_circuit:")
        print(rot_melodic_circuit)

        if harmonyenabled:
            rot_harmonic_circuit = compute_circuit(harmonic_degrees)

            if not use_simulator:
                # TODO: Put back in
                # rot_harmonic_circuit = compiler.compile(rot_harmonic_circuit)

                # TODO: Remove these lines
                tmp_rot_harmonic_circuit = compiler.compile(rot_harmonic_circuit)
                # print("tmp_rot_harmonic_circuit:")
                # print(tmp_rot_harmonic_circuit)
                rot_harmonic_circuit = Program()
                for instruction in tmp_rot_harmonic_circuit.instructions:
                    if not isinstance(instruction, Pragma):
                        rot_harmonic_circuit.inst(instruction)

            print("rot_harmonic_circuit:")
            print(rot_harmonic_circuit)

        num_runs = 1
        if species == 0:
            circuit_dict = {}  # Key is circuit name, value is circuit

            res_dict = dict()
            res_dict['000_m'] = deque([])
            res_dict['000_h'] = deque([])
            res_dict['001_m'] = deque([])
            res_dict['001_h'] = deque([])
            res_dict['010_m'] = deque([])
            res_dict['010_h'] = deque([])
            res_dict['011_m'] = deque([])
            res_dict['011_h'] = deque([])

            res_dict['100_m'] = deque([])
            res_dict['100_h'] = deque([])
            res_dict['101_m'] = deque([])
            res_dict['101_h'] = deque([])
            res_dict['110_m'] = deque([])
            res_dict['110_h'] = deque([])
            res_dict['111_m'] = deque([])
            res_dict['111_h'] = deque([])

            # Create all of the potentially required melody circuits
            num_required_melodic_circuits_per_pitch = 10

            num_required_harmonic_circuits_per_pitch = 5 if harmonyenabled else 0

            for pitch_idx in range(0, DIATONIC_SCALE_OCTAVE_PITCHES):
                for melodic_circuit_idx in range(0, num_required_melodic_circuits_per_pitch):

                    p = Program()

                    # Convert the pitch index to a binary string
                    qubit_string = format(pitch_idx, '03b')

                    res_dict_key = qubit_string + "_m"

                    for idx, qubit_char in enumerate(qubit_string):
                        if qubit_char == '0':
                            p.inst(I(NUM_CIRCUIT_WIRES - 1 - idx))
                        else:
                            p.inst(X(NUM_CIRCUIT_WIRES - 1 - idx))

                    p.inst(copy.deepcopy(rot_melodic_circuit))
                    p.inst().measure(0, 0).measure(1, 1) \
                        .measure(2, 2)
                    # print("rot_melodic_circuit: ", p)

                    result = q_con.run(p, [2, 1, 0], num_runs)
                    bits = result[0]
                    meas_bitstr = ""
                    for bit_idx in range(0, NUM_CIRCUIT_WIRES):
                        meas_bitstr += str(bits[bit_idx])

                    print(res_dict_key + ':' + meas_bitstr)

                    res_dict[res_dict_key].append(meas_bitstr)

            if harmonyenabled:
                for pitch_idx in range(0, DIATONIC_SCALE_OCTAVE_PITCHES):
                    for harmonic_circuit_idx in range(0, num_required_harmonic_circuits_per_pitch):

                        p = Program()

                        # Convert the pitch index to a binary string
                        qubit_string = format(pitch_idx, '03b')

                        res_dict_key = qubit_string + "_h"

                        for idx, qubit_char in enumerate(qubit_string):
                            if qubit_char == '0':
                                p.inst(I(NUM_CIRCUIT_WIRES - 1 - idx))
                            else:
                                p.inst(X(NUM_CIRCUIT_WIRES - 1 - idx))

                        p.inst(copy.deepcopy(rot_harmonic_circuit))
                        p.inst().measure(0, 0).measure(1, 1) \
                            .measure(2, 2)
                        # print("rot_harmonic_circuit: ", p)

                        result = q_con.run(p, [2, 1, 0], num_runs)
                        bits = result[0]
                        meas_bitstr = ""
                        for bit_idx in range(0, NUM_CIRCUIT_WIRES):
                            meas_bitstr += str(bits[bit_idx])

                        print(res_dict_key + ':' + meas_bitstr)

                        res_dict[res_dict_key].append(meas_bitstr)

            print('res_dict: ', res_dict)

            full_res_dict = dict()
            for key in res_dict:
                full_res_dict[key] = list(res_dict[key])
            ret_dict = {"full_res_dict": full_res_dict}

        else:
            harmony_notes_factor = 2**(species - 1) * (1 if harmonyenabled else 0)  # Number of harmony notes for each melody note
            num_composition_bits = TOTAL_MELODY_NOTES * (harmony_notes_factor + 1) * NUM_CIRCUIT_WIRES

            composition_bits = [0] * num_composition_bits

            # Convert the pitch index to a binary string, and place into the
            # composition_bits array, least significant bits in lowest elements of array
            qubit_string = format(pitch_index, '03b')
            for idx, qubit_char in enumerate(qubit_string):
                if qubit_char == '0':
                    composition_bits[idx] = 0
                else:
                    composition_bits[idx] = 1

            # Compute notes for the main melody
            for melody_note_idx in range(0, TOTAL_MELODY_NOTES):
                #
                if (melody_note_idx < TOTAL_MELODY_NOTES - 1):
                    p = Program()

                    for bit_idx in range(0, NUM_CIRCUIT_WIRES):
                        if (composition_bits[melody_note_idx * NUM_CIRCUIT_WIRES + bit_idx] == 0):
                            p.inst(I(NUM_CIRCUIT_WIRES - 1 - bit_idx))
                        else:
                            p.inst(X(NUM_CIRCUIT_WIRES - 1 - bit_idx))

                    p.inst(copy.deepcopy(rot_melodic_circuit))
                    p.inst().measure(0, 0).measure(1, 1) \
                        .measure(2, 2)
                    # print("rot_melodic_circuit:")
                    # print(p)

                    result = q_con.run(p, [2, 1, 0], num_runs)
                    bits = result[0]
                    for bit_idx in range(0, NUM_CIRCUIT_WIRES):
                        composition_bits[(melody_note_idx + 1) * NUM_CIRCUIT_WIRES + bit_idx] = bits[bit_idx]

                    #print(composition_bits)

                    measured_pitch = bits[0] * 4 + bits[1] * 2 + bits[2]
                    #print("melody melody_note_idx measured_pitch")
                    #print(melody_note_idx)
                    #print(measured_pitch)

                if harmonyenabled:
                    # Now compute a harmony note for the melody note
                    #print("Now compute a harmony note for the melody notev")
                    p = Program()

                    for bit_idx in range(0, NUM_CIRCUIT_WIRES):
                        if composition_bits[melody_note_idx * NUM_CIRCUIT_WIRES + bit_idx] == 0:
                            p.inst(I(NUM_CIRCUIT_WIRES - 1 - bit_idx))
                        else:
                            p.inst(X(NUM_CIRCUIT_WIRES - 1 - bit_idx))

                    p.inst(copy.deepcopy(rot_harmonic_circuit))
                    p.inst().measure(0, 0).measure(1, 1) \
                        .measure(2, 2)
                    # print("rot_harmonic_circuit:")
                    # print(p)

                    result = q_con.run(p, [2, 1, 0], num_runs)
                    bits = result[0]
                    for bit_idx in range(0, NUM_CIRCUIT_WIRES):
                        composition_bits[(melody_note_idx * NUM_CIRCUIT_WIRES * harmony_notes_factor) +
                                         (TOTAL_MELODY_NOTES * NUM_CIRCUIT_WIRES) + bit_idx] = bits[bit_idx]

                    #print(composition_bits)

                    measured_pitch = bits[0] * 4 + bits[1] * 2 + bits[2]
                    #print("harmony melody_note_idx measured_pitch")
                    #print(melody_note_idx)
                    #print(measured_pitch)


                    # Now compute melody notes to follow the harmony note
                    #print("Now compute melody notes to follow the harmony note")
                    for harmony_note_idx in range(1, harmony_notes_factor):
                        p = Program()

                        for bit_idx in range(0, NUM_CIRCUIT_WIRES):
                            if (composition_bits[(melody_note_idx * NUM_CIRCUIT_WIRES * harmony_notes_factor) +
                                                 ((harmony_note_idx - 1) * NUM_CIRCUIT_WIRES) +
                                                 (TOTAL_MELODY_NOTES * NUM_CIRCUIT_WIRES) + bit_idx] == 0):
                                p.inst(I(NUM_CIRCUIT_WIRES - 1 - bit_idx))
                            else:
                                p.inst(X(NUM_CIRCUIT_WIRES - 1 - bit_idx))

                        p.inst(copy.deepcopy(rot_melodic_circuit))
                        p.inst().measure(0, 0).measure(1, 1) \
                            .measure(2, 2)
                        #print("rot_melodic_circuit:")
                        #print(p)

                        result = q_con.run(p, [2, 1, 0], num_runs)
                        bits = result[0]
                        for bit_idx in range(0, NUM_CIRCUIT_WIRES):
                            composition_bits[(melody_note_idx * NUM_CIRCUIT_WIRES * harmony_notes_factor) +
                                              ((harmony_note_idx) * NUM_CIRCUIT_WIRES) +
                                             (TOTAL_MELODY_NOTES * NUM_CIRCUIT_WIRES) + bit_idx] = bits[bit_idx]

                        #print(composition_bits)

                        measured_pitch = bits[0] * 4 + bits[1] * 2 + bits[2]
                        #print("melody after harmony melody_note_idx measured_pitch")
                        #print(melody_note_idx)
                        #print(measured_pitch)

            all_note_nums = create_note_nums_array(composition_bits)
            melody_note_nums = all_note_nums[0:TOTAL_MELODY_NOTES]
            harmony_note_nums = all_note_nums[7:num_composition_bits]

            if use_simulator:
                composer = "Rigetti QVM"
            else:
                composer = "Rigetti " + "8Q-Agave"

            ret_dict = {"melody": melody_note_nums,
                        "harmony": harmony_note_nums,
                        "lilypond": create_lilypond(melody_note_nums, harmony_note_nums, composer),
                        "toy_piano" : create_toy_piano(melody_note_nums, harmony_note_nums)}

    return jsonify(ret_dict)


def create_note_nums_array(ordered_classical_registers):
    allnotes_array = []
    cur_val = 0
    for idx, bit in enumerate(ordered_classical_registers):
        if idx % 3 == 0:
            cur_val += bit * 4
        elif idx % 3 == 1:
            cur_val += bit * 2
        else:
            cur_val += bit
            allnotes_array.append(cur_val)
            cur_val = 0
    return allnotes_array


def pitch_letter_by_index(pitch_idx):
    retval = "z"
    if pitch_idx == 0:
        retval = "c"
    elif pitch_idx == 1:
        retval = "d"
    elif pitch_idx == 2:
        retval = "e"
    elif pitch_idx == 3:
        retval = "f"
    elif pitch_idx == 4:
        retval = "g"
    elif pitch_idx == 5:
        retval = "a"
    elif pitch_idx == 6:
        retval = "b"
    elif pitch_idx == 7:
        retval = "c'"
    else:
        retval = "z"
    return retval


# Produce output for Lilypond
def create_lilypond(melody_note_nums, harmony_note_nums, composer):
    harmony_notes_fact = int(len(harmony_note_nums) / len(melody_note_nums))
    harmonyenabled = harmony_notes_fact > 0
    retval = "\\version \"2.18.2\" \\paper {#(set-paper-size \"a5\")} " +\
             " \\header {title=\"Schrodinger's Cat\" subtitle=\"on a Toy Piano\" composer = \"" + composer + "\"} " + \
             " melody = \\absolute { \\clef " + \
             (" \"bass\" " if harmonyenabled else " \"treble\" ") + \
             " \\numericTimeSignature \\time 4/4 \\tempo 4 = 100"
    for pitch in melody_note_nums:
        retval += " " + pitch_letter_by_index(pitch) + ("" if harmonyenabled else "'") + ("2" if harmonyenabled else "4")

    # Add the same pitch to the end of the melody as in the beginning
    retval += " " + pitch_letter_by_index(melody_note_nums[0]) + ("" if harmonyenabled else "'") + ("2" if harmonyenabled else "4")

    if harmonyenabled:
        retval += "} harmony = \\absolute { \\clef \"treble\" \\numericTimeSignature \\time 4/4 "
        for pitch in harmony_note_nums:
            retval += " " + pitch_letter_by_index(pitch) + "'" + str(int(harmony_notes_fact * 2))

        # Add the same pitch to the end of the harmony as in the beginning of the melody,
        # only an octave higher
        retval += " " + pitch_letter_by_index(melody_note_nums[0]) + "'2"

    retval += "} \\score { << "

    if harmonyenabled:
        retval += " \\new Staff \\with {instrumentName = #\"Harmony\"}  { \\harmony } "

    retval += " \\new Staff \\with {instrumentName = #\"Melody\"}  { \\melody } >> }"

    return retval

# Produce output for toy piano
def create_toy_piano(melody_note_nums, harmony_note_nums):
    harmony_notes_fact = int(len(harmony_note_nums) / len(melody_note_nums))
    harmonyenabled = harmony_notes_fact > 0
    quarter_note_dur = 150
    notes = []
    latest_melody_idx = 0
    latest_harmony_idx = 0
    num_pitches_in_octave = 7
    toy_piano_pitch_offset = 8

    for idx, pitch in enumerate(melody_note_nums):
        notes.append({"num": pitch + toy_piano_pitch_offset + (0 if harmonyenabled else num_pitches_in_octave), "time": idx * quarter_note_dur * (2 if harmonyenabled else 1)})
        latest_melody_idx = idx

    # Add the same pitch to the end of the melody as in the beginning
    notes.append({"num": melody_note_nums[0] + toy_piano_pitch_offset + (0 if harmonyenabled else num_pitches_in_octave), "time": (latest_melody_idx + 1) * quarter_note_dur * (2 if harmonyenabled else 1)})

    if harmonyenabled:
        for idx, pitch in enumerate(harmony_note_nums):
            notes.append({"num": pitch + num_pitches_in_octave + toy_piano_pitch_offset, "time": idx * quarter_note_dur * 2 / harmony_notes_fact})
            latest_harmony_idx = idx

        # Add the same pitch to the end of the harmony as in the beginning of the melody,
        # only an octave higher
        notes.append({"num": melody_note_nums[0] + num_pitches_in_octave + toy_piano_pitch_offset, "time": (latest_harmony_idx + 1) * quarter_note_dur * 2 / harmony_notes_fact})

    # Sort the array of dictionaries by time
    sorted_notes = sorted(notes, key=lambda k: k['time'])

    return sorted_notes

def available_quantum_device():
    # Returns first available quantum device
    devices_dict = get_devices(as_dict=True)
    print('devices_dict: ', devices_dict)

    for device in devices_dict.values():
        if (device.is_online()):
            return device

    # If we got here, there weren't any devices online
    return None

if __name__ == '__main__':
    # app.run()
    app.run(host='127.0.0.1', port=5001)
