from string import Template
from pandas import json_normalize
import pandas as pd
import requests
import os

GH_TOKEN = os.environ['GH_TOKEN']
headers = {"Authorization": f"Bearer {GH_TOKEN}"}


def run_query(query):
    """A simple function to use requests.post
    to make the API call. Note the json= section."""

    request = requests.post('https://api.github.com/graphql',
                            json={'query': query}, headers=headers)
    if request.status_code == 200:  # 200 means request fulfilled
        return request.json()
    else:
        raise Exception(
                        "Query failed to run by returning code of {}. {}".format(
                                                                                 request.status_code, query))


def build_query(pr_cursor):
    return Template("""{
      repository(owner: "redhat-openshift-ecosystem", name: "operator-test-playbooks") {
        pullRequests(first: 15, after: $cursor) {
          pageInfo{
            hasNextPage
            endCursor
          }
          edges {
            node {
              author {
                login
              }
              mergedBy {
                login
              }
              createdAt
              mergedAt
              title
              url
            }
          }
        }
      }
    }
    """).substitute({'cursor': pr_cursor})


def format_cursor(cursor):
    """Format cursor inside double quotations as required by API"""
    return '"{}"'.format(cursor)


def get_PR_data(cursor):
    """This function will create and return a data
    frame with the data returned from the query"""

    all_data = []
    hasNextPage = True
    while hasNextPage:
        cursor = "null" if cursor is None else format_cursor(cursor)
        getPRinfo = build_query(cursor)
        result = run_query(getPRinfo)
        data_frame = pd.json_normalize(result['data']['repository']['pullRequests']['edges'])
        page_info = pd.json_normalize(result['data']['repository']['pullRequests']['pageInfo'])
        all_data.append(data_frame)
        cursor = page_info.loc[0, 'endCursor']  # update cursor
        hasNextPage = page_info.loc[0, 'hasNextPage']  # update hasNextPage
    res_data = pd.concat(all_data)  # creating a df with all PRs
    res_data.pop('node.mergedBy')

    return res_data
