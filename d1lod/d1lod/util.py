""" util.py

    Functions offering utility to other functions in this package.
"""

import os
import sys
import xml.etree.ElementTree as ET
import json
import csv
import requests


def continue_or_quit():
    """ Allows the program to pause in order to ask the user to
    continue or quit."""

    response = None

    while response is None:
        response = raw_input("c(ontinue) or q(uit)")

        if response != "c" and response != "q":
            response = None

    if response == "c":
        print "Continuing..."

    if response == "q":
        print "Exiting..."
        sys.exit()


def getXML(url):
    """Get XML document at the given url `url`"""

    try:
        r = requests.get(url)
    except:
        print "\tgetXML failed for %s" % url
        return None

    content = r.text
    xmldoc = ET.fromstring(content.encode('utf-8'))

    return(xmldoc)


def loadJSONFile(filename):
    """ Loads as a JSON file as a Python dict.
    """

    content = {}

    if not os.path.exists(filename):
        return content

    with open(filename, "rb") as content_file:
        try:
            content = json.load(content_file)
        except ValueError:
            content = {}

    return content


def saveJSONFile(content, filename):
    """ Saves a dict to a JSON file located at filename.
    """

    with open(filename, "wb") as content_file:
        content_file.write(json.dumps(content,
                            sort_keys=True,
                            indent=2,
                            separators=(',', ': ')))


def ns_interp(text, ns=None):
    """
    Triple strings (e.g. foo:Bar) have to be expanded because SPARQL queries
    can't handle the subject of a triple being

        d1resolve:doi:10.6073/AA/knb-lter-pie.77.3

    but can handle

        <https://cn.dataone.org/cn/v1/resolve/doi:10.6073/AA/knb-lter-pie.77.3>

    This method does that interpolation using the class instance's
    namespaces.

    Returns:
        String, either modified or not.
    """

    if ns is None:
        return text

    colon_index = text.find(":")

    if len(text) <= colon_index + 1:
        return text

    namespace = text[0:colon_index]
    rest = text[(colon_index)+1:]

    if namespace not in ns:
        return text

    return "<%s%s>" % (ns[namespace], rest)


def loadFormatsMap():
    """
    Gets the formats map from GitHub. These are the GeoLink URIs for the
    file format types DataOne knows about.

    Returns:
        A Dict of formats, indexed by format ID.
    """

    r = requests.get("https://raw.githubusercontent.com/ec-geolink/design/master/data/dataone/formats/formats.csv")
    reader = csv.DictReader(r.text.splitlines())

    formats_map = {}

    for row in reader:
        formats_map[row['id']] = {
            'type': row['type'],
            'uri' : row['uri'],
            'name': row['name']
        }

    return formats_map


def createIdentifierMap(path):
    """
    Converts a CSV of identifier<->filename mappings into a Dict.

    Returns:
        Dict of identifier<->filename mappings
    """

    identifier_map = None # Will be a docid <-> PID map

    if os.path.isfile(path):
        print "Loading identifiers map..."

        identifier_table = pandas.read_csv(path)
        identifier_map = dict(zip(identifier_table.guid, identifier_table.filepath))

    return identifier_map


def getIdentifierScheme(identifier):
    """Uses string matching on the given identifier string to guess a scheme.
    """

    if (identifier.startswith("doi:") |
            identifier.startswith("http://doi.org/") | identifier.startswith("https://doi.org/") |
            identifier.startswith("http://dx.doi.org/") | identifier.startswith("https://dx.doi.org/")):
        scheme = 'doi'
    elif (identifier.startswith("ark:")):
        scheme = 'ark'
    elif (identifier.startswith("http:")):
        scheme = 'uri'
    elif (identifier.startswith("https:")):
        scheme = 'uri'
    elif (identifier.startswith("urn:")):
        scheme = 'urn'
    else:
        scheme = 'local-resource-identifier-scheme'

    return scheme
