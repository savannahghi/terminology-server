# -coding=utf-8
"""Models for core SNOMED components ( refsets excluded )

The initial SNOMED load ( and loading of updates ) will bypass the Django ORM
( for performance reasons, and also to sidestep a "chicken and egg" issue with the validators.

This is a PostgreSQL only implementation.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from .helpers import verhoeff_digit

import math
import re


SNOMED_TESTER = settings.SNOMED_TESTER
# TODO - Judicious indexes for all models, including refset models


@receiver(post_save, sender=get_user_model())
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Ensure that every user has a DRF auth token"""
    if created:
        Token.objects.create(user=instance)


class Component(models.Model):
    """Fields shared between all components; ABSTRACT"""
    component_id = models.BigIntegerField()
    effective_time = models.DateField()
    active = models.BooleanField(default=True)
    module_id = models.BigIntegerField()

    # TODO Add validator for existence of module before saving new record
    # TODO - component_id needs to be an index for this table; it will be queried A LOT

    # TODO - add @property for language name
    # TODO - add @property for moduleName

    def _validate_sctid_minimum(self):
        """Must be greater than 10^5"""
        if self.component_id < math.pow(10, 5):
            raise ValidationError("A SNOMED Identifier must be > 10^5")

    def _validate_sctid_maximum(self):
        """Must be less than 10^18"""
        if self.component_id > math.pow(10, 18):
            raise ValidationError("A SNOMED Identifier must be < 10^18")

    def _validate_sctid_is_positive(self):
        """Must be positive integers"""
        if self.component_id < 0:
            raise ValidationError("A SNOMED Identifier must be positive")

    def _validate_sctid_check_digit(self):
        """"The last digit is a Verhoeff dihedral check digit"""
        # Split out last digit
        s = str(self.component_id)
        identifier, check_digit = s[:-1], self._get_sctid_check_digit()
        if verhoeff_digit(identifier) != check_digit:
            raise ValidationError("The SNOMED Identifier has an invalid check digit")

    def _validate_sctid_no_leading_zeros(self):
        """The string rendering of a SNOMED identifier should have no leading zeroes"""
        pattern = re.compile('^0.+')
        if pattern.match(str(self.component_id)):
            raise ValidationError(
                "The string representation should not have leading zeroes"
            )

    def _sctid_is_short_format(self):
        """True if it contains 00 OR 01 OR 02 as partition identifiers"""
        partition_identifier = self._get_sctid_partition_identifier()
        return partition_identifier in ['00', '01', '02']

    def _sctid_is_long_format(self):
        """True if it contains 10, 11 or 12 as partition identifiers"""
        partition_identifier = self._get_sctid_partition_identifier()
        return partition_identifier in ['10', '11', '12']

    def _get_sctid_check_digit(self):
        """The check digit is always the last digit"""
        return str(self.component_id)[-1]

    def _get_sctid_partition_identifier(self):
        """The partition identifier is always the last two digits"""
        return str(self.component_id)[-4:-2]

    def _validate_identifier_components(self):
        """A valid long format SNOMED identifier has the following components:
            1. Item identifier
            2. Namespace identifier
            3. Partition identifier
            4. Check digit

        A valid short format SNOMED identifier has the following components:
            1. Item identifier
            2. Partition identifier
            3. Check digit
        """
        if not self._sctid_is_long_format() and not self._sctid_is_short_format():
            raise ValidationError("None of the expected partition identifiers was found")

    def _validate_partition_id(self):
        """Confirm that the partition id corresponds to the SNOMED identifier"""
        partition_id = self._get_sctid_partition_identifier()
        if isinstance(self, Concept) and partition_id not in ['00', '10']:
            raise ValidationError("Invalid concept partition identifier")
        elif isinstance(self, Description) and partition_id not in ['01', '11']:
            raise ValidationError("Invalid description partition identifier")
        elif isinstance(self, Relationship) and partition_id not in ['02', '12']:
            raise ValidationError("Invalid relationship partition identifier")

    def _validate_module(self):
        """All modules descend from 900000000000443000"""
        if not SNOMED_TESTER.is_child_of(900000000000443000, self.module_id):
            raise ValidationError("The module must be a descendant of '900000000000443000'")

    def _another_active_component_exists(self):
        """Helper; does another component with the same component id exists and is it active?"""
        return self.objects.get(component_id=self.component_id, active=True).count()

    def _inactivate_older_revisions(self):
        """Inactivate past revisions of this component"""
        for rev in self.objects.get(component_id=self.component_id, active=True):
            rev.active = False
            rev.save()

    def clean(self):
        """Sanity checks"""
        self._validate_sctid_minimum()
        self._validate_sctid_maximum()
        self._validate_sctid_is_positive()
        self._validate_sctid_is_positive()
        self._validate_sctid_check_digit()
        self._validate_sctid_no_leading_zeros()
        self._validate_identifier_components()
        self._validate_partition_id()
        self._validate_module()
        super(Component, self).clean()

    def save(self, *args, **kwargs):
        """
        Override save to introduce validation before every save

        :param args:
        :param kwargs:
        """
        # We do not allow updates
        if self.pk:
            raise ValidationError("SNOMED Components are immutable; they cannot be altered")

        # Perform sanity checks
        self.full_clean()

        # Next, ensure that only one component can be active at the same time
        # Inactivate older revisions
        if self._another_active_component_exists():
            self._inactivate_older_revisions()

        # Finally, save
        super(Component, self).save(*args, **kwargs)

    def delete(self, using=None):
        """Disable deleting

        :param using:
        """
        raise ValidationError("SNOMED Components are immutable; they cannot be deleted")

    class Meta(object):
        abstract = True


class Concept(Component):
    """SNOMED concepts"""
    definition_status_id = models.BigIntegerField()

    # TODO - add validator for existence of definition status when a new record is created

    # TODO - add an @property for preferred_term; to be used in nested serializers; use materialized view?
    # TODO - add @property for definitionStatusName
    # TODO - add @property for fullySpecifiedName
    # TODO - add @property for definition
    # TODO - add @property for descriptions
    # TODO - add @property for preferredTerms
    # TODO - add @property for synonyms
    # TODO - add @property for outgoingRelationships
    # TODO - add @property for incomingRelationships
    # TODO - add @property for parents
    # TODO - add @property for children
    # TODO - add @property for ancestors
    # TODO - add @property for descendants
    # TODO - add @property for branch numbers
    # TODO - add @property for sanctioned qualifiers
    # TODO - add @property for partOf


    def _validate_definition_status(self):
        """The definition status should be a descendant of 900000000000444006"""
        if not SNOMED_TESTER.is_child_of(900000000000444006, self.definition_status_id):
            raise ValidationError("The definition status must be a descendant of '900000000000444006'")

    def clean(self):
        """Sanity checks"""
        self._validate_definition_status()
        super(self, Concept).clean()

    class Meta(object):
        db_table = 'snomed_concept'


class Description(Component):
    """SNOMED descriptions"""
    concept_id = models.BigIntegerField()
    language_code = models.CharField(max_length=2, default='en')
    type_id = models.BigIntegerField()
    case_significance_id = models.BigIntegerField()
    term = models.TextField()

    # TODO - add validator for existence of concept
    # TODO - add validator for existence of type ( is the subsumption enough? )
    # TODO - add validator for existence of case significance

    # TODO - add @property for description type name
    # TODO - add @property for caseSignificanceName
    # TODO - add @property for concepts; serialize only the id [ SCTID ] and term [ preferred term ] for each concept

    def _validate_language_code(self):
        if self.language_code != 'en':
            raise ValidationError("The only language permitted in this terminology server is 'en'")

    def _validate_type(self):
        """Should be a descendant of 900000000000446008"""
        if not SNOMED_TESTER.is_child_of(900000000000446008, self.type_id):
            raise ValidationError("The type must be a descendant of '900000000000446008'")

    def _validate_case_significance(self):
        """Should be a descendant of 900000000000447004"""
        if not SNOMED_TESTER.is_child_of(900000000000447004, self.case_significance_id):
            raise ValidationError("The case significance must be a descendant of '900000000000447004'")

    def _validate_term_length(self):
        if len(self.term) > 32768:
            raise ValidationError("The supplied term is too long")

    def clean(self):
        """Perform sanity checks"""
        self._validate_language_code()
        self._validate_type()
        self._validate_case_significance()
        self._validate_term_length()
        super(self, Description).clean()

    class Meta(object):
        db_table = 'snomed_description'


class Relationship(Component):
    """SNOMED relationships"""
    source_id = models.BigIntegerField()
    destination_id = models.BigIntegerField()
    relationship_group = models.PositiveSmallIntegerField(default=0)
    type_id = models.BigIntegerField()
    characteristic_type_id = models.BigIntegerField()
    modifier_id = models.BigIntegerField()

    # TODO - add check that source concept exists
    # TODO - add check that destination concept exists
    # TODO - add check that type exists
    # TODO - add check that characteristic type exists
    # TODO - add check that modifier exists
    # TODO - consider what indexes can be added to make this more efficient; use "use the index, luke" as a guide

    # TODO - add @property for sourceName
    # TODO - add @property for destinationName
    # TODO - add @property for typeName
    # TODO - add @property for characteristicTypeName
    # TODO - add @property for modifierName

    def _validate_type(self):
        """Must be set to a descendant of 'Linkage concept [106237007]'"""
        if not SNOMED_TESTER.is_child_of(106237007, self.type.concept_id):
            raise ValidationError("The type must be a descendant of '106237007'")

    def _validate_characteristic_type(self):
        """Must be set to a descendant of '900000000000449001'"""
        if not SNOMED_TESTER.is_child_of(900000000000449001, self.characteristic_type.concept_id):
            raise ValidationError("The characteristic type must be a descendant of '900000000000449001'")

    def _validate_modifier(self):
        """Must be set to a descendant of '900000000000450001'"""
        if not SNOMED_TESTER.is_child_of(900000000000450001, self.modifier.concept_id):
            raise ValidationError("The modifier must be a descendant of '900000000000450001'")

    def clean(self):
        """Sanity checks"""
        self._validate_type()
        self._validate_characteristic_type()
        self._validate_modifier()
        super(self, Relationship).clean()

    class Meta(object):
        db_table = 'snomed_relationship'