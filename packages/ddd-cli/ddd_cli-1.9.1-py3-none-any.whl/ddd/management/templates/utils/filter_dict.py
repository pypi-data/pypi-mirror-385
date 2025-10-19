def clean_dict_of_keys(data: dict, keys=()) -> dict:
    """
    Limpia un diccionario eliminando claves específicas.

    Args:
        data (dict): El diccionario a limpiar.
        keys (list): Lista de claves a eliminar del diccionario.

    Returns:
        dict: Un nuevo diccionario sin las claves especificadas.
    """
    return {k: v for k, v in data.items() if k not in keys}


def filter_dict_by_keys(data: dict, keys: set) -> dict:
    """
    Filtra un diccionario para incluir SOLO las claves especificadas.
    
    Args:
        data (dict): Diccionario de entrada.
        keys (set): Conjunto de claves permitidas.
        
    Returns:
        dict: Nuevo diccionario con solo las claves permitidas.
    """
    return {k: v for k, v in data.items() if k in keys}