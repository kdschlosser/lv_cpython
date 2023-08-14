
def is_lib_c_node(n):
    if hasattr(n, 'coord') and n.coord is not None:
        if 'fake_libc_include' in n.coord.file:
            return True
    return False

