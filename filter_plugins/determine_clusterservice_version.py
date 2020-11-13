#!/usr/bin/env python
import pprint


def determine_csv(channels, current_channel):
    """
    params
    channels: list of dictionaries of channels
    current_channel: searched channel name
    """
    pprint.pprint(channels)
    pprint.pprint(current_channel)
    result = []
    for channel in channels:
        if str(channel['name']) == str(current_channel):
            result.append(channel['currentCSV'])
    return result


class FilterModule(object):
    ''' A filter to fetch current clusterserviceversion '''
    def filters(self):
        return {
            'determine_clusterservice_version': determine_csv
        }
