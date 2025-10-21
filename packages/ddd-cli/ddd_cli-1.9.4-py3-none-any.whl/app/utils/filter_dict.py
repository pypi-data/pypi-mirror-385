
def clean_dict_of_keys(data: dict, keys=()) -> dict:
    """
    Limpia un diccionario eliminando claves específicas o valores None.

    Args:
        data (dict): El diccionario a limpiar.
        keys (list): Lista de claves a eliminar del diccionario.

    Returns:
        dict: Un nuevo diccionario sin las claves especificadas.
    """
    return {k: v for k, v in data.items() if k not in keys and v is not None}


def filter_dict_by_keys(data: dict, keys: set) -> dict:
    """
    Filtra un diccionario para incluir solo las claves especificadas y valores no None.
    
    Args:
        data (dict): Diccionario de entrada.
        keys (set): Conjunto de claves permitidas.
        
    Returns:
        dict: Nuevo diccionario con solo las claves permitidas.
    """
    return {k: v for k, v in data.items() if k in keys and v is not None}
