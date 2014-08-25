# coding=utf-8
"""UNMANAGED models for MATERIALIZED VIEWS that are used as performance optimizations"""
from django.db import models
from jsonfield import JSONField

import json


class ConceptDenormalizedView(models.Model):
    """This maps the materialized view that pre-computes all the attributes needed to index or render a concept"""
    id = models.IntegerField(editable=False, primary_key=True)
    concept_id = models.BigIntegerField(editable=False)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)
    is_primitive = models.BooleanField(editable=False, default=False)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    definition_status_id = models.BigIntegerField(editable=False)
    definition_status_name = models.TextField(editable=False)

    fully_specified_name = models.TextField(editable=False)
    preferred_term = models.TextField(editable=False)
    definition = models.TextField(editable=False, null=True, blank=True)

    descriptions = JSONField(editable=False)
    preferred_terms = JSONField(editable=False)
    synonyms = JSONField(editable=False)

    is_a_parents = JSONField(editable=False)
    is_a_children = JSONField(editable=False)
    is_a_direct_parents = JSONField(editable=False)
    is_a_direct_children = JSONField(editable=False)

    part_of_parents = JSONField(editable=False)
    part_of_children = JSONField(editable=False)
    part_of_direct_parents = JSONField(editable=False)
    part_of_direct_children = JSONField(editable=False)

    other_parents = JSONField(editable=False)
    other_children = JSONField(editable=False)
    other_direct_parents = JSONField(editable=False)
    other_direct_children = JSONField(editable=False)

    @property
    def preferred_terms_list(self):
        """Parse the JSON that is embedded inside the preferred terms JSONField"""
        return [json.loads(term) for term in self.preferred_terms]

    @property
    def synonyms_list(self):
        """Parse the JSON that is embedded inside the synonyms JSONField"""
        return [json.loads(term) for term in self.synonyms]

    @property
    def descriptions_list(self):
        """Parse the JSON that is embedded inside the descriptions JSONField"""
        return [json.loads(term) for term in self.descriptions]

    @property
    def is_a_parents_ids(self):
        """Extract IDs of is_a_parents"""
        return list(set([rel["concept_id"] for rel in self.is_a_parents]))

    @property
    def is_a_children_ids(self):
        """Extract IDs of is_a_children"""
        return list(set([rel["concept_id"] for rel in self.is_a_children]))

    class Meta:
        managed = False
        db_table = 'concept_expanded_view'


class DescriptionDenormalizedView(models.Model):
    """This maps the materialized view that pre-computes the names of description attributes"""
    id = models.IntegerField(editable=False, primary_key=True)
    component_id = models.BigIntegerField(editable=False)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)
    language_code = models.CharField(max_length=2, editable=False)
    term = models.TextField(editable=False)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    concept_id = models.BigIntegerField(editable=False)
    concept_name = models.TextField(editable=False)

    type_id = models.BigIntegerField(editable=False)
    type_name = models.TextField(editable=False)

    case_significance_id = models.BigIntegerField(editable=False)
    case_significance_name = models.TextField(editable=False)

    class Meta:
        managed = False
        db_table = 'description_expanded_view'


class RelationshipDenormalizedView(models.Model):
    """This maps the materialized view that pre-computes the names of relationship attributes"""
    id = models.IntegerField(editable=False, primary_key=True)
    component_id = models.BigIntegerField(editable=False)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)
    relationship_group = models.SmallIntegerField(editable=False, null=True, blank=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    source_id = models.BigIntegerField(editable=False)
    source_name = models.TextField(editable=False)

    destination_id = models.BigIntegerField(editable=False)
    destination_name = models.TextField(editable=False)

    type_id = models.BigIntegerField(editable=False)
    type_name = models.TextField(editable=False)

    characteristic_type_id = models.BigIntegerField(editable=False)
    characteristic_type_name = models.TextField(editable=False)

    modifier_id = models.BigIntegerField(editable=False)
    modifier_name = models.TextField(editable=False)

    class Meta:
        managed = False
        db_table = 'relationship_expanded_view'


class SubsumptionView(models.Model):
    """This maps the materialized view that pre-computes all subsumption information"""
    concept_id = models.BigIntegerField(editable=False, primary_key=True)

    is_a_direct_parents = JSONField(editable=False)
    is_a_parents = JSONField(editable=False)
    is_a_direct_children = JSONField(editable=False)
    is_a_children = JSONField(editable=False)

    part_of_direct_parents = JSONField(editable=False)
    part_of_parents = JSONField(editable=False)
    part_of_direct_children = JSONField(editable=False)
    part_of_children = JSONField(editable=False)

    other_direct_parents = JSONField(editable=False)
    other_parents = JSONField(editable=False)
    other_direct_children = JSONField(editable=False)
    other_children = JSONField(editable=False)

    class Meta:
        managed = False
        db_table = 'snomed_subsumption'
