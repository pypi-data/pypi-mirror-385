# bacmman indices (barcode) manipulation
def get_parent(indices):
    split = indices.split('-')[:-1]
    if len(split)==1:
        return int(split[0])
    else:
        return '-'.join(split)
get_frame = lambda indices : int(indices.split('-')[0])
def get_previous(currentIndices):
    spl = currentIndices.split('-')
    spl[0] = str(int(spl[0])-1)
    return '-'.join(spl)
def get_next(currentIndices):
    spl = currentIndices.split('-')
    spl[0] = str(int(spl[0])+1)
    return '-'.join(spl)
def set_frame(indices, newFrame):
    spl = indices.split('-')
    spl[0] = str(newFrame)
    return '-'.join(spl)
