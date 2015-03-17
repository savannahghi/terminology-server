CREATE VIEW snomed_concept AS
WITH recent_view_cte AS (
    SELECT component_id, MAX(effective_time) AS max_effective_time
    FROM snomed_concept_full
    GROUP BY component_id
)
SELECT component.*
FROM snomed_concept_full component
JOIN recent_view_cte ON
    component.component_id = recent_view_cte.component_id
    AND component.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_description AS
WITH recent_view_cte AS (
    SELECT component_id, MAX(effective_time) AS max_effective_time
    FROM snomed_description_full
    GROUP BY component_id
)
SELECT component.*
FROM snomed_description_full component
JOIN recent_view_cte ON
    component.component_id = recent_view_cte.component_id
    AND component.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_relationship AS
WITH recent_view_cte AS (
    SELECT component_id, MAX(effective_time) AS max_effective_time
    FROM snomed_relationship_full
    GROUP BY component_id
)
SELECT component.*
FROM snomed_relationship_full component
JOIN recent_view_cte ON
    component.component_id = recent_view_cte.component_id
    AND component.effective_time = recent_view_cte.max_effective_time;
CREATE EXTENSION IF NOT EXISTS plpythonu;
CREATE OR REPLACE FUNCTION generate_subsumption_maps() RETURNS
TABLE(
    concept_id bigint,
    is_a_direct_parents bigint[], is_a_parents bigint[],
    is_a_direct_children bigint[], is_a_children bigint[],
    part_of_direct_parents bigint[], part_of_parents bigint[],
    part_of_direct_children bigint[], part_of_children bigint[],
    other_direct_parents bigint[], other_parents bigint[],
    other_direct_children bigint[], other_children bigint[]
) AS $$
import networkx as nx


def _get_transitive_closure_map():
    """Load SNOMED relationships into a networkx directed multi graph"""
    g = nx.MultiDiGraph()
    relationships = plpy.execute(
        "SELECT destination_id, source_id, type_id "
        "FROM snomed_relationship WHERE active = True"
    )
    for rel in relationships:
        g.add_edge(
            rel["destination_id"], rel["source_id"],
            type_id=rel["type_id"]
        )
    return g

# The primary graph, and sub-graphs for various types
G = _get_transitive_closure_map()
IS_A = nx.DiGraph(
    (source, target, attr) for source, target, attr in G.edges_iter(data=True)
    if attr['type_id'] == 116680003
)
PART_OF = nx.DiGraph(
    (source, target, attr) for source, target, attr in G.edges_iter(data=True)
    if attr['type_id'] == 123005000
)
OTHER = nx.DiGraph(
    (source, target, attr) for source, target, attr in G.edges_iter(data=True)
    if attr['type_id'] not in [116680003, 123005000]
)

# Release memory from the main graph; we have a hard 4GB limit on CircleCI
del G
import gc
gc.collect()  # Yeah, this is not Pythonic

def get_relationships(concept_id):
    """Extract a single concept's relationships"""
    return (
        concept_id,
        IS_A.predecessors(concept_id),
        list(nx.dag.ancestors(IS_A, concept_id)),
        IS_A.successors(concept_id),
        list(nx.dag.descendants(IS_A, concept_id)),
        PART_OF.predecessors(concept_id) if concept_id in PART_OF else [],
        list(nx.dag.ancestors(PART_OF, concept_id)) if concept_id in PART_OF else [],
        PART_OF.successors(concept_id) if concept_id in PART_OF else [],
        list(nx.dag.descendants(PART_OF, concept_id)) if concept_id in PART_OF else [],
        OTHER.predecessors(concept_id) if concept_id in OTHER else [],
        list(nx.dag.ancestors(OTHER, concept_id)) if concept_id in OTHER else [],
        OTHER.successors(concept_id) if concept_id in OTHER else [],
        list(nx.dag.descendants(OTHER, concept_id)) if concept_id in OTHER else [],
    )

concepts = plpy.execute(
    "SELECT DISTINCT component_id FROM snomed_concept WHERE active = True")
return (get_relationships(concept["component_id"]) for concept in concepts)
$$ LANGUAGE plpythonu;
CREATE MATERIALIZED VIEW snomed_subsumption AS
SELECT
  concept_id,
  is_a_direct_parents, is_a_parents, is_a_direct_children, is_a_children,
  part_of_direct_parents, part_of_parents, part_of_direct_children, part_of_children,
  other_direct_parents, other_parents, other_direct_children, other_children
FROM generate_subsumption_maps();
CREATE TYPE description AS (
    component_id bigint,
    module_id bigint,
    type_id bigint,
    effective_time date,
    case_significance_id bigint,
    term text,
    language_code character varying(2),
    active boolean,
    acceptability_id bigint,
    refset_id bigint
);
CREATE TYPE shortened_description AS (
    term text,
    acceptability_id bigint,
    refset_id bigint
);

CREATE OR REPLACE FUNCTION get_preferred_term(descs shortened_description[]) RETURNS text AS $$
    -- GB English is 900000000000508004
    -- UK English reference set is 999001251000000103
    -- UK Extension drug lang refset is 999000681000001101
    SELECT term FROM unnest(descs)
    WHERE acceptability_id = 900000000000548007
    AND refset_id IN (900000000000508004, 999001251000000103, 999000681000001101);
$$ LANGUAGE SQL;
CREATE MATERIALIZED VIEW concept_preferred_terms AS
SELECT
  con.component_id as concept_id,
  get_preferred_term(array_agg((des.term, ref.acceptability_id, ref.refset_id)::shortened_description)) AS preferred_term
FROM snomed_concept con
JOIN snomed_description des ON des.concept_id = con.component_id
JOIN snomed_language_reference_set ref ON ref.referenced_component_id = des.component_id
GROUP BY con.component_id;


CREATE OR REPLACE FUNCTION get_concept_preferred_term(bigint) returns text AS $$
    SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = $1;
$$ LANGUAGE SQL;
CREATE TYPE denormalized_description AS (
    component_id bigint,
    module_id bigint,
    module_name text,
    type_id bigint,
    type_name text,
    effective_time date,
    case_significance_id bigint,
    case_significance_name text,
    term text,
    language_code character varying(2),
    active boolean,
    acceptability_id bigint,
    acceptability_name text,
    refset_id bigint,
    refset_name text
);
CREATE OR REPLACE FUNCTION extract_fully_specified_name(descs denormalized_description[])
RETURNS denormalized_description AS $$
    SELECT descr FROM unnest(descs) descr WHERE descr.type_id = 900000000000003001 LIMIT 1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION extract_definition(descs denormalized_description[])
RETURNS denormalized_description AS $$
    SELECT descr FROM unnest(descs) descr WHERE descr.type_id = 900000000000550004 LIMIT 1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION extract_preferred_term(descs denormalized_description[])
RETURNS denormalized_description AS $$
    SELECT descr FROM unnest(descs) descr WHERE descr.type_id = 900000000000013009
    AND descr.refset_id IN (900000000000508004, 999001251000000103, 999000681000001101)
    LIMIT 1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION extract_preferred_terms(descs denormalized_description[])
RETURNS denormalized_description[] AS $$
    SELECT array_agg(descr) FROM unnest(descs) descr WHERE descr.type_id = 900000000000013009
    AND descr.acceptability_id = 900000000000548007;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION extract_synonyms(descs denormalized_description[])
RETURNS denormalized_description[] AS $$
    SELECT array_agg(descr) FROM unnest(descs) descr WHERE descr.type_id = 900000000000013009
    AND descr.acceptability_id != 900000000000548007;
$$ LANGUAGE SQL;
CREATE TYPE expanded_relationship AS (
    concept_id bigint,
    concept_name text
);

CREATE OR REPLACE FUNCTION expand_relationships(rels bigint[])
RETURNS expanded_relationship[] AS $$
    SELECT array_agg(
        (rel_id, get_concept_preferred_term(rel_id))::expanded_relationship
    )
    FROM unnest(rels)
    AS rel_id;
$$ LANGUAGE SQL;
-- The final output view for concepts
CREATE MATERIALIZED VIEW concept_expanded_view AS
WITH con_desc_cte AS (
SELECT
    conc.id as id, conc.component_id AS concept_id,
    conc.effective_time, conc.active, conc.module_id, conc.definition_status_id,
    CASE WHEN conc.definition_status_id = 900000000000074008 THEN true ELSE false END AS is_primitive,
    array_agg(
        (
            des.component_id,
            des.module_id,
            get_concept_preferred_term(des.module_id),
            des.type_id,
            get_concept_preferred_term(des.type_id),
            des.effective_time,
            des.case_significance_id,
            get_concept_preferred_term(des.case_significance_id),
            des.term,
            des.language_code,
            des.active,
            ref.acceptability_id,
            get_concept_preferred_term(ref.acceptability_id),
            ref.refset_id,
            get_concept_preferred_term(ref.refset_id)
        )::denormalized_description
    ) AS descs
  FROM snomed_concept conc
  JOIN snomed_description des ON des.concept_id = conc.component_id
  JOIN snomed_language_reference_set ref ON ref.referenced_component_id = des.component_id
  GROUP BY
    conc.id, conc.component_id, conc.effective_time, conc.active,
    conc.module_id, conc.definition_status_id
)
SELECT
    -- Straight forward retrieval from the pre-processed view
    con_desc.id, con_desc.concept_id, con_desc.effective_time, con_desc.active, con_desc.is_primitive,
    -- Look up the names of these attributes
    con_desc.module_id, get_concept_preferred_term(con_desc.module_id) AS module_name,
    con_desc.definition_status_id, get_concept_preferred_term(con_desc.definition_status_id) AS definition_status_name,
    -- Get the descriptions from the stored procedure
    con_desc.descs as descriptions,
    extract_preferred_terms(con_desc.descs) as preferred_terms,
    extract_synonyms(con_desc.descs) as synonyms,
    extract_fully_specified_name(con_desc.descs) as fully_specified_name,
    extract_definition(con_desc.descs) as definition,
    extract_preferred_term(con_desc.descs) as preferred_term,
    -- Relationships - use stored procedure to fill out
    expand_relationships(sub.is_a_parents) as is_a_parents,
    expand_relationships(sub.is_a_children) as is_a_children,
    expand_relationships(sub.is_a_direct_parents) as is_a_direct_parents,
    expand_relationships(sub.is_a_direct_children) as is_a_direct_children,
    expand_relationships(sub.part_of_parents) as part_of_parents,
    expand_relationships(sub.part_of_children) as part_of_children,
    expand_relationships(sub.part_of_direct_parents) as part_of_direct_parents,
    expand_relationships(sub.part_of_direct_children) as part_of_direct_children,
    expand_relationships(sub.other_parents) as other_parents,
    expand_relationships(sub.other_children) as other_children,
    expand_relationships(sub.other_direct_parents) as other_direct_parents,
    expand_relationships(sub.other_direct_children) as other_direct_children
FROM con_desc_cte con_desc
JOIN snomed_subsumption sub ON sub.concept_id = con_desc.concept_id;
CREATE MATERIALIZED VIEW relationship_expanded_view AS
  SELECT
    rel.id, rel.component_id, rel.effective_time, rel.active, rel.relationship_group,
    rel.module_id, get_concept_preferred_term(rel.module_id) AS module_name,
    rel.source_id, get_concept_preferred_term(rel.source_id) AS source_name,
    rel.destination_id, get_concept_preferred_term(rel.destination_id) AS destination_name,
    rel.type_id, get_concept_preferred_term(rel.type_id) AS type_name,
    rel.characteristic_type_id, get_concept_preferred_term(rel.characteristic_type_id) AS characteristic_type_name,
    rel.modifier_id, get_concept_preferred_term(rel.modifier_id) AS modifier_name
  FROM snomed_relationship rel;
CREATE MATERIALIZED VIEW description_expanded_view AS
  SELECT
    descr.id, descr.component_id, descr.effective_time, descr.active, descr.language_code, descr.term,
    descr.module_id, get_concept_preferred_term(descr.module_id) AS module_name,
    descr.concept_id, get_concept_preferred_term(descr.concept_id) AS concept_name,
    descr.type_id, get_concept_preferred_term(descr.type_id) AS type_name,
    descr.case_significance_id, get_concept_preferred_term(descr.case_significance_id) AS case_significance_name
  FROM snomed_description descr;
CREATE VIEW search_content_view AS
SELECT
  conc.id,
  conc.concept_id,
  conc.active,
  conc.is_primitive,
  conc.module_id,
  conc.module_name,
  (conc.fully_specified_name).term AS fully_specified_name,
  (conc.preferred_term).term AS preferred_term,
  ARRAY(SELECT term FROM unnest(conc.descriptions)) AS descriptions,
  ARRAY(SELECT concept_id FROM unnest(conc.is_a_parents)) AS is_a_parent_ids,
  ARRAY(SELECT concept_id FROM unnest(conc.is_a_children)) AS is_a_children_ids,
  ARRAY(
      SELECT DISTINCT(refset_id) FROM snomed_simple_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_ordered_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_attribute_value_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_simple_map_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_complex_map_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_extended_map_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_query_specification_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_annotation_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_association_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_module_dependency_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_description_format_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_reference_set_descriptor_reference_set WHERE referenced_component_id = conc.concept_id
  ) AS refset_ids
FROM concept_expanded_view conc;

