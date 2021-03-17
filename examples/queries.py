import rdflib
import urllib.parse


def load_manifest(manifest_path: str) -> rdflib.Graph:
    """
    Loads a Tale's manifest into an rdf graph

    :param manifest_path:
    :return: A graph object loaded with the manifest
    """

    graph:rdflib.Graph = rdflib.Graph().parse(source=manifest_path, format='json-ld')
    graph.bind("wt", rdflib.Namespace("https://vocabularies.wholetale.org/wt/1.0/"))
    return graph


def query_version_information(graph: rdflib.Graph):
    """
    Examples of how to query information regarding the Tale's version
    :param graph: The graph being queried
    :return: None
    """

    # Query that retrieves the version ID, name, and date last modified
    query = """
    PREFIX wt: <https://vocabularies.wholetale.org/wt/1.0/> 
    
    SELECT ?version_id ?version_name ?date_modified
    WHERE {
        ?version_id rdf:type wt:TaleVersion .
        ?version_id schema:name ?version_name .
        ?version_id schema:dateModified ?date_modified .
    }
    """
    res = graph.query(query)
    assert len(res) > 0
    for row in res:
        print(f'Version ID: {row[0]}')
        print(f'Version Name: {row[1]}')
        print(f'Last Modified: {row[2]}')

    # Get the version author's information
    query = """
    PREFIX sdtl: <https://vocabularies.wholetale.org/wt/1.0/>
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


def query_tale_properties(graph: rdflib.Graph):
    """
    Examples of how to query various Tale properties
    :param graph: The graph being queried
    :return: None
    """

    # Query that retrieves various root level properties of the Tale
    query = """
    PREFIX wt: <https://vocabularies.wholetale.org/wt/1.0/>
    SELECT ?tale_id ?tale_description ?tale_schema_version ?tale_name ?tale_keywords
            ?internal_id
    WHERE {
        ?tale_id rdf:type wt:Tale .
        ?tale_id schema:description ?tale_description .
        ?tale_id schema:schemaVersion ?tale_schema_version .
        ?tale_id schema:name ?tale_name .
        ?tale_id schema:keywords ?tale_keywords .
        ?tale_id wt:identifier ?internal_id .
    }
    """
    res = graph.query(query)
    assert len(res) > 0
    for row in res:
        print(f'Tale ID: {row[0]}')
        print(f'Tale Description: {row[1]}')
        print(f'Tale Schema Version: {row[2]}')
        print(f'Tale Tale Name: {row[3]}')
        print(f'Tale Keywords: {row[4]}')
        print(f'Tale Girder ID: {row[5]}')

    # Query that retrieves information about the Tale creator
    query = """
    PREFIX wt: <https://vocabularies.wholetale.org/wt/1.0/>
    SELECT ?creator_id ?family_name ?given_name ?email
    WHERE {
        ?tale_id rdf:type wt:Tale .
        ?tale_id pav:createdBy ?creator_id .
        ?creator_id schema:familyName ?family_name .
        ?creator_id schema:givenName ?given_name .
        ?creator_id schema:email ?email .
    }
    """
    res = graph.query(query)
    assert len(res) > 0
    for row in res:
        print(f'Creator ID: {row[0]}')
        print(f'Creator Last Name: {row[1]}')
        print(f'Creator First Name: {row[2]}')
        print(f'Creator Email: {row[3]}')


if __name__ == '__main__':
    urllib.parse.uses_relative.append('arcp')
    urllib.parse.uses_netloc.append('arcp')
    # g = load_manifest("./external-dataset/metadata/manifest.json")
    # g = load_manifest("./extra-metadata/metadata/manifest.json")
    g = load_manifest("./local-data/metadata/manifest.json")
    print(g.serialize(format='turtle').decode('utf-8'))

    print("Parsing the Tale's Version Information....")
    query_version_information(g)
    print("\n\n\n")
    print("Querying Tale properties")
    query_tale_properties(g)
