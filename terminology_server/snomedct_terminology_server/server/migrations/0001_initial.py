# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-17 06:58
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnnotationReferenceSetDenormalizedView',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('effective_time', models.DateField(editable=False)),
                ('active', models.BooleanField(default=True, editable=False)),
                ('module_id', models.BigIntegerField(editable=False)),
                ('module_name', models.TextField(editable=False)),
                ('refset_id', models.BigIntegerField(editable=False)),
                ('refset_name', models.TextField(editable=False)),
                ('referenced_component_id', models.BigIntegerField(editable=False)),
                ('referenced_component_name', models.TextField(blank=True, editable=False, null=True)),
                ('annotation', models.TextField()),
            ],
            options={
                'verbose_name': 'annotation_refset_view',
                'db_table': 'annotation_reference_set_expanded_view',
            },
        ),
        migrations.CreateModel(
            name='AssociationReferenceSetDenormalizedView',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('effective_time', models.DateField(editable=False)),
                ('active', models.BooleanField(default=True, editable=False)),
                ('module_id', models.BigIntegerField(editable=False)),
                ('module_name', models.TextField(editable=False)),
                ('refset_id', models.BigIntegerField(editable=False)),
                ('refset_name', models.TextField(editable=False)),
                ('referenced_component_id', models.BigIntegerField(editable=False)),
                ('referenced_component_name', models.TextField(blank=True, editable=False, null=True)),
                ('target_component_id', models.BigIntegerField()),
                ('target_component_name', models.TextField(blank=True, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'association_refset_view',
                'db_table': 'association_reference_set_expanded_view',
            },
        ),
        migrations.CreateModel(
            name='AttributeValueReferenceSetDenormalizedView',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('effective_time', models.DateField(editable=False)),
                ('active', models.BooleanField(default=True, editable=False)),
                ('module_id', models.BigIntegerField(editable=False)),
                ('module_name', models.TextField(editable=False)),
                ('refset_id', models.BigIntegerField(editable=False)),
                ('refset_name', models.TextField(editable=False)),
                ('referenced_component_id', models.BigIntegerField(editable=False)),
                ('referenced_component_name', models.TextField(blank=True, editable=False, null=True)),
                ('value_id', models.BigIntegerField(editable=False)),
                ('value_name', models.TextField(blank=True, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'attrib_value_refset_view',
                'db_table': 'attribute_value_reference_set_expanded_view',
            },
        ),
        migrations.CreateModel(
            name='ComplexMapReferenceSetDenormalizedView',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('effective_time', models.DateField(editable=False)),
                ('active', models.BooleanField(default=True, editable=False)),
                ('module_id', models.BigIntegerField(editable=False)),
                ('module_name', models.TextField(editable=False)),
                ('refset_id', models.BigIntegerField(editable=False)),
                ('refset_name', models.TextField(editable=False)),
                ('referenced_component_id', models.BigIntegerField(editable=False)),
                ('referenced_component_name', models.TextField(blank=True, editable=False, null=True)),
                ('map_group', models.IntegerField(editable=False)),
                ('map_priority', models.IntegerField(editable=False)),
                ('map_rule', models.TextField(editable=False)),
                ('map_advice', models.TextField(editable=False)),
                ('map_target', models.CharField(editable=False, max_length=256)),
                ('correlation_id', models.BigIntegerField(editable=False)),
                ('correlation_name', models.TextField(blank=True, editable=False, null=True)),
                ('map_block', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'complex_map_refset_view',
                'db_table': 'complex_map_reference_set_expanded_view',
            },
        ),
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField()),
                ('module_id', models.BigIntegerField()),
                ('module_name', models.TextField()),
                ('definition_status_id', models.BigIntegerField()),
                ('definition_status_name', models.TextField()),
                ('is_primitive', models.BooleanField()),
                ('fully_specified_name', models.TextField()),
                ('preferred_term', models.TextField()),
                ('definition', django.contrib.postgres.fields.jsonb.JSONField()),
                ('descriptions', django.contrib.postgres.fields.jsonb.JSONField()),
                ('parents', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('children', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('ancestors', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('descendants', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('incoming_relationships', django.contrib.postgres.fields.jsonb.JSONField()),
                ('outgoing_relationships', django.contrib.postgres.fields.jsonb.JSONField()),
                ('reference_set_memberships', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
            options={
                'db_table': 'snomed_denormalized_concept_view_for_current_snapshot',
            },
        ),
        migrations.CreateModel(
            name='Description',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField()),
                ('module_id', models.BigIntegerField()),
                ('module_name', models.TextField()),
                ('language_code', models.TextField()),
                ('type_id', models.BigIntegerField()),
                ('type_name', models.TextField()),
                ('term', models.TextField()),
                ('case_significance_id', models.BigIntegerField()),
                ('case_significance_name', models.TextField()),
                ('concept_id', models.BigIntegerField()),
                ('reference_set_memberships', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
            options={
                'db_table': 'denormalized_description_for_current_snapshot',
            },
        ),
        migrations.CreateModel(
            name='DescriptionFormatReferenceSetDenormalizedView',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('effective_time', models.DateField(editable=False)),
                ('active', models.BooleanField(default=True, editable=False)),
                ('module_id', models.BigIntegerField(editable=False)),
                ('module_name', models.TextField(editable=False)),
                ('refset_id', models.BigIntegerField(editable=False)),
                ('refset_name', models.TextField(editable=False)),
                ('referenced_component_id', models.BigIntegerField(editable=False)),
                ('referenced_component_name', models.TextField(blank=True, editable=False, null=True)),
                ('description_format_id', models.BigIntegerField()),
                ('description_format_name', models.TextField(blank=True, editable=False, null=True)),
                ('description_length', models.IntegerField()),
            ],
            options={
                'verbose_name': 'desc_format_refset_view',
                'db_table': 'description_format_reference_set_expanded_view',
            },
        ),
        migrations.CreateModel(
            name='ExtendedMapReferenceSetDenormalizedView',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('effective_time', models.DateField(editable=False)),
                ('active', models.BooleanField(default=True, editable=False)),
                ('module_id', models.BigIntegerField(editable=False)),
                ('module_name', models.TextField(editable=False)),
                ('refset_id', models.BigIntegerField(editable=False)),
                ('refset_name', models.TextField(editable=False)),
                ('referenced_component_id', models.BigIntegerField(editable=False)),
                ('referenced_component_name', models.TextField(blank=True, editable=False, null=True)),
                ('map_group', models.IntegerField(editable=False)),
                ('map_priority', models.IntegerField(editable=False)),
                ('map_rule', models.TextField(editable=False)),
                ('map_advice', models.TextField(editable=False)),
                ('map_target', models.CharField(editable=False, max_length=256)),
                ('correlation_id', models.BigIntegerField(editable=False)),
                ('correlation_name', models.TextField(blank=True, editable=False, null=True)),
                ('map_category_id', models.BigIntegerField()),
                ('map_category_name', models.TextField(blank=True, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'extended_map_refset_view',
                'db_table': 'extended_map_reference_set_expanded_view',
            },
        ),
        migrations.CreateModel(
            name='LanguageReferenceSetDenormalizedView',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('effective_time', models.DateField(editable=False)),
                ('active', models.BooleanField(default=True, editable=False)),
                ('module_id', models.BigIntegerField(editable=False)),
                ('module_name', models.TextField(editable=False)),
                ('refset_id', models.BigIntegerField(editable=False)),
                ('refset_name', models.TextField(editable=False)),
                ('referenced_component_id', models.BigIntegerField(editable=False)),
                ('referenced_component_name', models.TextField(blank=True, editable=False, null=True)),
                ('acceptability_id', models.BigIntegerField()),
                ('acceptability_name', models.TextField(blank=True, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'lang_refset_view',
                'db_table': 'language_reference_set_expanded_view',
            },
        ),
        migrations.CreateModel(
            name='ModuleDependencyReferenceSetDenormalizedView',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('effective_time', models.DateField(editable=False)),
                ('active', models.BooleanField(default=True, editable=False)),
                ('module_id', models.BigIntegerField(editable=False)),
                ('module_name', models.TextField(editable=False)),
                ('refset_id', models.BigIntegerField(editable=False)),
                ('refset_name', models.TextField(editable=False)),
                ('referenced_component_id', models.BigIntegerField(editable=False)),
                ('referenced_component_name', models.TextField(blank=True, editable=False, null=True)),
                ('source_effective_time', models.DateField()),
                ('target_effective_time', models.DateField()),
            ],
            options={
                'verbose_name': 'module_dep_refset_view',
                'db_table': 'module_dependency_reference_set_expanded_view',
            },
        ),
        migrations.CreateModel(
            name='OrderedReferenceSetDenormalizedView',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('effective_time', models.DateField(editable=False)),
                ('active', models.BooleanField(default=True, editable=False)),
                ('module_id', models.BigIntegerField(editable=False)),
                ('module_name', models.TextField(editable=False)),
                ('refset_id', models.BigIntegerField(editable=False)),
                ('refset_name', models.TextField(editable=False)),
                ('referenced_component_id', models.BigIntegerField(editable=False)),
                ('referenced_component_name', models.TextField(blank=True, editable=False, null=True)),
                ('order', models.PositiveSmallIntegerField(editable=False)),
                ('linked_to_id', models.BigIntegerField(editable=False)),
                ('linked_to_name', models.TextField(blank=True, editable=False, null=True)),
            ],
            options={
                'db_table': 'ordered_reference_set_expanded_view',
            },
        ),
        migrations.CreateModel(
            name='QuerySpecificationReferenceSetDenormalizedView',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('effective_time', models.DateField(editable=False)),
                ('active', models.BooleanField(default=True, editable=False)),
                ('module_id', models.BigIntegerField(editable=False)),
                ('module_name', models.TextField(editable=False)),
                ('refset_id', models.BigIntegerField(editable=False)),
                ('refset_name', models.TextField(editable=False)),
                ('referenced_component_id', models.BigIntegerField(editable=False)),
                ('referenced_component_name', models.TextField(blank=True, editable=False, null=True)),
                ('query', models.TextField()),
            ],
            options={
                'verbose_name': 'query_spec_refset_view',
                'db_table': 'query_specification_reference_set_expanded_view',
            },
        ),
        migrations.CreateModel(
            name='ReferenceSetDescriptorReferenceSetDenormalizedView',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('effective_time', models.DateField(editable=False)),
                ('active', models.BooleanField(default=True, editable=False)),
                ('module_id', models.BigIntegerField(editable=False)),
                ('module_name', models.TextField(editable=False)),
                ('refset_id', models.BigIntegerField(editable=False)),
                ('refset_name', models.TextField(editable=False)),
                ('referenced_component_id', models.BigIntegerField(editable=False)),
                ('referenced_component_name', models.TextField(blank=True, editable=False, null=True)),
                ('attribute_description_id', models.BigIntegerField()),
                ('attribute_description_name', models.TextField(blank=True, editable=False, null=True)),
                ('attribute_type_id', models.BigIntegerField()),
                ('attribute_type_name', models.TextField(blank=True, editable=False, null=True)),
                ('attribute_order', models.IntegerField()),
            ],
            options={
                'verbose_name': 'refset_descriptor_refset_view',
                'db_table': 'reference_set_descriptor_reference_set_expanded_view',
            },
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('effective_time', models.DateField()),
                ('active', models.BooleanField()),
                ('module_id', models.BigIntegerField()),
                ('module_name', models.TextField()),
                ('relationship_group', models.IntegerField()),
                ('source_id', models.BigIntegerField()),
                ('source_name', models.TextField()),
                ('destination_id', models.BigIntegerField()),
                ('destination_name', models.TextField()),
                ('type_id', models.BigIntegerField()),
                ('type_name', models.TextField()),
                ('characteristic_type_id', models.BigIntegerField()),
                ('characteristic_type_name', models.TextField()),
                ('modifier_id', models.BigIntegerField()),
                ('modifier_name', models.TextField()),
            ],
            options={
                'db_table': 'denormalized_relationship_for_current_snapshot',
            },
        ),
        migrations.CreateModel(
            name='SimpleMapReferenceSetDenormalizedView',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('effective_time', models.DateField(editable=False)),
                ('active', models.BooleanField(default=True, editable=False)),
                ('module_id', models.BigIntegerField(editable=False)),
                ('module_name', models.TextField(editable=False)),
                ('refset_id', models.BigIntegerField(editable=False)),
                ('refset_name', models.TextField(editable=False)),
                ('referenced_component_id', models.BigIntegerField(editable=False)),
                ('referenced_component_name', models.TextField(blank=True, editable=False, null=True)),
                ('map_target', models.CharField(editable=False, max_length=256)),
            ],
            options={
                'verbose_name': 'simple_map_refset_view',
                'db_table': 'simple_map_reference_set_expanded_view',
            },
        ),
        migrations.CreateModel(
            name='SimpleReferenceSetDenormalizedView',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('effective_time', models.DateField(editable=False)),
                ('active', models.BooleanField(default=True, editable=False)),
                ('module_id', models.BigIntegerField(editable=False)),
                ('module_name', models.TextField(editable=False)),
                ('refset_id', models.BigIntegerField(editable=False)),
                ('refset_name', models.TextField(editable=False)),
                ('referenced_component_id', models.BigIntegerField(editable=False)),
                ('referenced_component_name', models.TextField(blank=True, editable=False, null=True)),
            ],
            options={
                'db_table': 'simple_reference_set_expanded_view',
            },
        ),
        migrations.CreateModel(
            name='TransitiveClosure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField()),
                ('effective_time', models.DateField()),
                ('supertype_id', models.BigIntegerField()),
                ('subtype_id', models.BigIntegerField()),
            ],
            options={
                'db_table': 'transitive_closure_for_current_snapshot',
            },
        ),
        migrations.AlterUniqueTogether(
            name='relationship',
            unique_together=set([('id', 'effective_time', 'active', 'module_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='description',
            unique_together=set([('id', 'effective_time', 'active', 'module_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='concept',
            unique_together=set([('id', 'effective_time', 'active', 'module_id')]),
        ),
    ]