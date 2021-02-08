import rdflib


def load_manifest(manifest_path: str) -> rdflib.Graph:
    """
    Loads a Tale's manifest into an rdf graph

    :param manifest_path:
    :return: A graph object loaded with the manifest
    """

    graph:rdflib.Graph = rdflib.Graph().parse(source=manifest_path, format='json-ld')
    graph.bind("wt", rdflib.Namespace("https://vocabularies.wholetale.org/wt/0.1/wt#"))
    return graph


def query_version_information():
    """
    Examples of how to query information regarding the Tale's version
    :return: None
    """

    # Query that retrieves the version ID, name, and date last modified
    query = """
    PREFIX wt: <https://vocabularies.wholetale.org/wt/0.1/wt#>
            SELECT ?version_id ?version_name ?date_modified
    WHERE {
        ?version_id rdf:type wt:TaleVersion .
        ?version_id schema:name ?version_name .
        ?version_id schema:dateModified ?date_modified .
    }
    """
    graph = load_manifest("./external-dataset/metadata/manifest.json")
    res = graph.query(query)
    assert len(res) > 0
    for row in res:
        print(f'Version ID: {row[0]}')
        print(f'Version Name: {row[1]}')
        print(f'Last Modified: {row[2]}')

    # Get the version author's information
    query = """
    PREFIX sdtl: <https://vocabularies.wholetale.org/wt/0.1/wt#>
            SELECT DISTINCT ?creator_id ?given_name ?family_name ?email
    WHERE {
        ?version_id rdf:type wt:TaleVersion .
        ?version_id schema:creator ?creator_id .
        ?creator_id schema:givenName ?given_name .
        ?creator_id schema:familyName ?family_name .
        ?creator_id schema:email ?email.
    }
    """
    res = graph.query(query)
    assert len(res) > 0
    for row in res:
        print(f'Creator ID: {row[0]}')
        print(f'Given Name: {row[1]}')
        print(f'Family Name: {row[2]}')
        print(f'Email Address: {row[3]}')


if __name__ == '__main__':
    query_version_information()