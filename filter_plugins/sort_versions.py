from packaging.version import Version
def filter_sort_versions(l):
    ls = [str(x) for x in l]
    return sorted(ls, key=Version)
class FilterModule(object):
    def filters(self):
        return {
            'sort_versions': filter_sort_versions
        }
