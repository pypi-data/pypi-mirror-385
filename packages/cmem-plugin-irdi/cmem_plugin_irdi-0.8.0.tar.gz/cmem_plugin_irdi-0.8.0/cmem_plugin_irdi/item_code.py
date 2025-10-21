"""Create unique item codes"""

from pathlib import Path

from cmem.cmempy.dp.proxy.graph import post_streamed
from cmem.cmempy.queries import SparqlQuery

from cmem_plugin_irdi.utils import base_36_encode

MAX_IC_LENGTH = 6
COUNTER_ONTOLOGY_GRAPH = "http://purl.org/ontology/co/core#"

INITIALIZE_COUNTER = SparqlQuery(
    text="""
    PREFIX co: <http://purl.org/ontology/co/core#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX vs: <http://www.w3.org/2003/06/sw-vocab-status/ns#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    WITH <{{graph}}>
    DELETE {
        ?counter co:object ?object .
    }
    INSERT {
        <{{graph}}> a <https://vocab.eccenca.com/di/Dataset> .

        ?counter a co:Counter ;
                 dcterms:identifier "{{identifier}}" ;
                 rdfs:label "{{identifier}}";
                 {{counted_object_term}}.

    } WHERE {
        BIND(SHA256("{{identifier}}") as ?identifier_encoded)
        BIND(URI(CONCAT("https://ns.eccenca.com/counter/",
                        ?identifier_encoded
                        )) as ?counter)
        OPTIONAL {
            ?counter co:object ?object .
        }
    }
    """,
    query_type="UPDATE",
)

GET_COUNT: SparqlQuery = SparqlQuery(
    text="""
    PREFIX co: <http://purl.org/ontology/co/core#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT ?count FROM <{{graph}}> WHERE {
        ?counter a co:Counter ;
                 dcterms:identifier "{{identifier}}" ;
                 co:count ?count .
    }
    """
)

UPDATE_COUNT: SparqlQuery = SparqlQuery(
    text="""
    PREFIX co: <http://purl.org/ontology/co/core#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    WITH <{{graph}}>
    DELETE {
        ?counter co:count ?count_old .
    }
    INSERT {
        ?counter co:count ?count_new .
    }
    USING <{{graph}}>
    WHERE {
        ?counter a co:Counter ;
                dcterms:identifier "{{identifier}}" .
        OPTIONAL {
            ?counter co:count ?count_old .
            BIND((?count_old + 1) as ?count_new)
        }
        OPTIONAL {
            BIND(0 as ?count_new)
        }
    }
""",
    query_type="UPDATE",
)


def generate_item_code(graph: str, identifier: str) -> str:
    """Generate a base 36 IC (item code)

    :param graph: The graph in which the counter and its value are stored
    :param identifier: A unique identifier for the counter.
    :return: A base 36 item code
    """
    placeholders = {"graph": graph, "identifier": identifier}

    UPDATE_COUNT.get_results(placeholder=placeholders)

    res = GET_COUNT.get_json_results(placeholder=placeholders)

    try:
        count = int(res["results"]["bindings"][0]["count"]["value"])
    except (KeyError, IndexError) as error:
        raise ValueError(f"No counter found for {identifier}") from error

    item_code = base_36_encode(count).zfill(MAX_IC_LENGTH)

    if len(item_code) > MAX_IC_LENGTH:
        raise ValueError(
            f"Maximum Item Code length ({MAX_IC_LENGTH}) for counter {identifier} reached"
        )

    return item_code


def init_counter(graph: str, identifier: str, counted_object: str | None = None) -> None:
    """Initialize counter entity

    :param graph: The graph in which the counter is stored
    :param identifier: A unique identifier for the counter
    :param csi: Code space identifier
    """
    # Get path to vocabulary
    current_directory = Path(__file__).resolve().parent
    absolute_path = current_directory / "vocabs/counterontology.ttl"

    # Upload ontology
    post_streamed(graph=COUNTER_ONTOLOGY_GRAPH, file=absolute_path, replace=True)

    counted_object_term = f"co:object <{counted_object}>" if counted_object else ""

    INITIALIZE_COUNTER.get_results(
        placeholder={
            "graph": graph,
            "identifier": identifier,
            "counted_object_term": counted_object_term,
        }
    )
