__author__ = 'fanxn'

import json
import urllib, urllib2

# Add the BING_API_KEY
BING_API_KEY = 'VbelGThqk2D0hZko/TfN5hyioWsb8rwcH0cJOm6Rkuk'

def run_query(search_terms):
    # Specify the base
    root_url = 'https://api.datamarket.azure.com/Bing/Search/v1/'
    source = 'web'.capitalize()

    # Specify how many results we wish to be returned per page.
    # Offset specifies where in the results list to start from.
    # With results_per_page = 10 and offset = 11, this would start from page 2.
    results_per_page = 10
    offset = 0

    # Wrap quotes around our query terms as required by the Bing API.
    # The query we will then use is stored within variable query.
    query = "'{0}'".format(search_terms)
    query = urllib.quote(query)

    # Construct the latter parts of our request's URL.
    # Sets the format of the response to JSON and sets other properties.

    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
        root_url,
        source,
        results_per_page,
        offset,
        query
    )

    # Setup authentication with the Bing servers.
    # The username must be a blank string, and put in your API key.
    username = ''

    # Create a passoword manager which handles authentication for us.
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, BING_API_KEY)

    # Create our results list which we will populate.
    results = []

    try:
        # Prepare for connection to Bing servers
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        # Connect to the server and read the response generated.
        response = urllib2.urlopen(search_url).read().decode('utf-8')

        # Convert the string response to a Pyhton dict object.
        json_response = json.loads(response, encoding="gb2312")

        # Loop through each page returned, populating our results list.
        for result in json_response['d']['results']:
            results.append({
                'title': result['Title'],
                'link': result['Url'],
                'summary': result['Description']
            })

    # Catch a URLException -- something went wrong when connecting!
    except urllib2.URLError, e:
        print 'Error when querying the Bing API:', e

    # Return the list of results to the calling function
    return results


if __name__ == '__main__':
    for e in run_query("django"):
        print json.dumps(e, ensure_ascii=False)
