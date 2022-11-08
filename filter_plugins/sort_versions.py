from packaging.version import Version

def version_sort(l):
    return sorted(l, key=Version)

class FilterModule(object):

    def filters(self):
        return {
            'sort_versions': version_sort
        }
