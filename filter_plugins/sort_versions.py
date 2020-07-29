from pkg_resources import parse_version

def filter_sort_versions(value):
    list = [item + '-z' for item in value]
    list2 = sorted(list, key=parse_version)
    return [x[:-2] for x in list2]

class FilterModule(object):
    filter_sort = {
        'sort_versions': filter_sort_versions,
    }

    def filters(self):
        return self.filter_sort
