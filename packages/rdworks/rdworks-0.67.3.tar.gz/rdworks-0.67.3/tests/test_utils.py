import rdworks
import rdworks.autograph
import numpy as np
from rdworks import Mol
from rdworks.utils import (
    recursive_round,
    convert_triu_to_symm,
    serialize, 
    deserialize,
    compress_string,
    decompress_string,
)



def test_compress():
    m = Mol("CC(C)C1=C(C(=C(N1CC[C@H](C[C@H](CC(=O)O)O)O)C2=CC=C(C=C2)F)C3=CC=CC=C3)C(=O)NC4=CC=CC=C4",
              "atorvastatin")
    original_str = m.molblock
    compressed_str = compress_string(m.molblock)
    restored_str = decompress_string(compressed_str)
    assert original_str == restored_str


def test_serialize():
    data = {
        "users": ["alice", "bob", "charlie"],
        "count": 42,
        "active": True,
        "metadata": {"version": "1.0", "timestamp": "2025-10-10"}
    }
    serialized = serialize(data)
    deserialized = deserialize(serialized)
    assert deserialized == data


def test_serialize_integer_keys():
    # Integer key is not valid in JSON.
    data = {1 : 'a', 2: 'b', 3: 'c'}
    serialized = serialize(data)
    deserialized = deserialize(serialized)
    assert deserialized != data
    # AssertionError: assert {'1': 'a', '2': 'b', '3': 'c'} == {1: 'a', 2: 'b', 3: 'c'}
    # key type is changed from integer to string
    restored = {int(k): v for k, v in deserialized.items()}
    assert restored == data


def test_recursive_round():
    data1 = {
        "name": "Test Data",
        "version": 1.0,
        "values": [1.23456, 2.34567, {"nested_value": 3.456789}],
        "details": {
            "temperature": 25.1234567,
            "pressure": 1013.256789,
            "measurements": [0.000123, 123.45000, 987.654321]
        },
        "another_list": [
            {"a": 1.111, "b": 2.2222},
            [3.33333, 4.444444]
        ],
        "integer_val": 10,
        "string_val": "hello"
    }

    data2 = [
        10.123,
        "string",
        [1.0, 2.3456, {"key": 9.87654321}],
        {"val1": 7.777777, "val2": [0.1, 0.02, 0.003]}
    ]

    data3 = 123.456789

    data4 = "Just a string"

    data5 = [1, 2, 3] # No floats

    print("Original data1:", data1)
    
    modified_data1_dp2 = recursive_round(data1, 2)
    
    assert modified_data1_dp2 == {'name': 'Test Data', 'version': 1.0, 'values': [1.23, 2.35, {'nested_value': 3.46}], 'details': {'temperature': 25.12, 'pressure': 1013.26, 'measurements': [0.0, 123.45, 987.65]}, 'another_list': [{'a': 1.11, 'b': 2.22}, [3.33, 4.44]], 'integer_val': 10, 'string_val': 'hello'}
    print("\nModified data1 (2 decimal places):", modified_data1_dp2)
    
    modified_data1_dp0 = recursive_round(data1, 0)
    assert modified_data1_dp0 == {'name': 'Test Data', 'version': 1.0, 'values': [1.0, 2.0, {'nested_value': 3.0}], 'details': {'temperature': 25.0, 'pressure': 1013.0, 'measurements': [0.0, 123.0, 988.0]}, 'another_list': [{'a': 1.0, 'b': 2.0}, [3.0, 4.0]], 'integer_val': 10, 'string_val': 'hello'}
    print("\nModified data1 (0 decimal places):", modified_data1_dp0)

    print("\nOriginal data2:", data2)
    modified_data2_dp3 = recursive_round(data2, 3)
    assert modified_data2_dp3 == [10.123, 'string', [1.0, 2.346, {'key': 9.877}], {'val1': 7.778, 'val2': [0.1, 0.02, 0.003]}]
    print("\nModified data2 (3 decimal places):", modified_data2_dp3)

    print("\nOriginal data3:", data3)
    modified_data3_dp1 = recursive_round(data3, 1)
    assert modified_data3_dp1 == 123.5
    print("\nModified data3 (1 decimal place):", modified_data3_dp1)

    print("\nOriginal data4:", data4)
    modified_data4_dp2 = recursive_round(data4, 2)
    assert modified_data4_dp2 == 'Just a string'
    print("\nModified data4 (2 decimal places):", modified_data4_dp2) # Should be unchanged

    print("\nOriginal data5:", data5)
    modified_data5_dp2 = recursive_round(data5, 2)
    assert modified_data5_dp2 == [1, 2, 3]
    print("\nModified data5 (2 decimal places):", modified_data5_dp2) # Should be unchanged

    # Example of invalid decimal_places
    try:
        recursive_round(data1, -1)
    except ValueError as e:
        print(f"\nError caught: {e}")

    try:
        recursive_round(data1, 1.5)
    except ValueError as e:
        print(f"Error caught: {e}")


def test_autograph():
    N = 50
    upper_triangle_values = 5.0 *np.random.rand(N*(N-1)//2)
    rmsdMatrix = convert_triu_to_symm(upper_triangle_values)
    com, cen = rdworks.autograph.NMRCLUST(rmsdMatrix)
    assert len(com) == N
    assert len(set(com)) == len(cen)
    
    com, cen = rdworks.autograph.DynamicTreeCut(rmsdMatrix)
    assert len(com) == N
    assert len(set(com)) == len(cen)
    
    com, cen = rdworks.autograph.RCKmeans(rmsdMatrix)
    assert len(com) == N
    assert len(set(com)) == len(cen)

    com, cen  = rdworks.autograph.AutoGraph(rmsdMatrix)
    assert len(com) == N
    assert len(set(com)) == len(cen)