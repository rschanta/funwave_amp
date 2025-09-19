from ._combination_functions import find_combinations_from_csv,find_combinations_from_dict


def find_combinations(matrix_dict=None,
                      matrix_csv= None):
    '''
    Finds the cartesian product of the range of all the parameters with 
    multiple possible values
    '''
    # Assert that both are not specified
    assert not (matrix_dict is not None 
                and matrix_csv is not None), "Choose either dictionary OR CSV, not both!"
    
    
    # Deal with the csv version
    if matrix_csv:
          df_permutations = find_combinations_from_csv(matrix_csv)
    
    # Deal with the dictionary version
    elif matrix_dict:
          df_permutations = find_combinations_from_dict(matrix_dict)
    
    # Raise error if both are none
    else:
          raise ValueError('Need either matrix_csv or matrix_dict!')
    
    return df_permutations