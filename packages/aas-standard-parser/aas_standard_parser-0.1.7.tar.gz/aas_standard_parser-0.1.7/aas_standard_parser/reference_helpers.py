from basyx.aas.model import ModelReference


def construct_idshort_path_from_reference(reference: ModelReference) -> str:
    idshort_path: str = ""

    # start from the second Key and omit the Identifiable at the beginning of the list
    for key in reference.key[1:]:
        idshort_path += (key.value + ".")

    # get rid of the trailing dot
    return idshort_path[:-1]
