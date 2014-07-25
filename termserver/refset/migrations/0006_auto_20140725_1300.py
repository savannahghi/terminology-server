# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    SQL = """
    DROP MATERIALIZED VIEW IF EXISTS ordered_reference_set_expanded_view;
    CREATE MATERIALIZED VIEW ordered_reference_set_expanded_view AS
    SELECT
      rf.id, rf.row_id, rf.effective_time, rf.active, rf.order,
      rf.module_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.module_id) AS module_name,
      rf.refset_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.refset_id) AS refset_name,
      rf.referenced_component_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.referenced_component_id) AS referenced_component_name,
      rf.linked_to_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.linked_to_id) AS linked_to_name
    FROM snomed_ordered_reference_set rf;
    CREATE INDEX ordered_reference_set_expanded_view_id ON ordered_reference_set_expanded_view(id);
    CREATE INDEX ordered_reference_set_expanded_view_row_id ON ordered_reference_set_expanded_view(row_id);
    """

    dependencies = [
        ('refset', '0005_auto_20140725_1254'),
    ]

    operations = [
        migrations.RunSQL(),
    ]