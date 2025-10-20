import django_filters
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from ipam.models import IPAddress, Prefix, IPRange

from netbox_security.models import (
    NatPool,
    NatRule,
    NatRuleSet,
    NatRuleAssignment,
)

from netbox_security.choices import AddressTypeChoices, RuleStatusChoices
from netbox_security.mixins import PortsFilterSet, AssignmentFilterSet


class NatRuleFilterSet(PortsFilterSet, NetBoxModelFilterSet):
    rule_set_id = django_filters.ModelMultipleChoiceFilter(
        queryset=NatRuleSet.objects.all(),
        field_name="rule_set",
        to_field_name="id",
        label=_("Rule Set (ID)"),
    )
    rule_set = django_filters.ModelMultipleChoiceFilter(
        queryset=NatRuleSet.objects.all(),
        field_name="rule_set__name",
        to_field_name="name",
        label=_("Rule Set (Name)"),
    )
    pool_id = django_filters.ModelMultipleChoiceFilter(
        queryset=NatPool.objects.all(),
        field_name="pool",
        to_field_name="id",
        label=_("NAT Pool (ID)"),
    )
    pool = django_filters.ModelMultipleChoiceFilter(
        queryset=NatPool.objects.all(),
        field_name="pool__name",
        to_field_name="name",
        label=_("NAT Pool (Name)"),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=RuleStatusChoices,
        required=False,
    )
    source_type = django_filters.MultipleChoiceFilter(
        choices=AddressTypeChoices,
        required=False,
    )
    destination_type = django_filters.MultipleChoiceFilter(
        choices=AddressTypeChoices,
        required=False,
    )
    source_address_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        field_name="source_addresses",
        to_field_name="id",
        label=_("Source Address (ID)"),
    )
    source_address = django_filters.ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        field_name="source_addresses__address",
        to_field_name="address",
        label=_("Source Address (Address)"),
    )
    destination_address_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        field_name="destination_addresses",
        to_field_name="id",
        label=_("Destination Address (ID)"),
    )
    destination_address = django_filters.ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        field_name="destination_addresses__address",
        to_field_name="address",
        label=_("Destination Address (Address)"),
    )
    ip_address_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        field_name="source_addresses",
        to_field_name="id",
        label=_("Source Address (ID)"),
    )
    source_prefix_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        field_name="source_prefixes",
        to_field_name="id",
        label=_("Source Prefix (ID)"),
    )
    source_prefix = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        field_name="source_prefixes__prefix",
        to_field_name="prefix",
        label=_("Source Prefix (Prefix)"),
    )
    destination_prefix_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        field_name="destination_prefixes",
        to_field_name="id",
        label=_("Destination Prefix (ID)"),
    )
    destination_prefix = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        field_name="destination_prefixes__prefix",
        to_field_name="prefix",
        label=_("Destination Prefix (Prefix)"),
    )
    prefix_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        field_name="source_prefixes",
        to_field_name="id",
        label=_("Source Prefix (ID)"),
    )
    destination_range_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IPRange.objects.all(),
        field_name="destination_ranges",
        to_field_name="id",
        label=_("Destination Range (ID)"),
    )
    destination_range = django_filters.ModelMultipleChoiceFilter(
        queryset=IPRange.objects.all(),
        field_name="destination_ranges__start_address",
        to_field_name="start_address",
        label=_("Destination Range (Start Address)"),
    )
    source_range_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IPRange.objects.all(),
        field_name="source_ranges",
        to_field_name="id",
        label=_("Source Range (ID)"),
    )
    source_range = django_filters.ModelMultipleChoiceFilter(
        queryset=IPRange.objects.all(),
        field_name="source_ranges__start_address",
        to_field_name="start_address",
        label=_("Source Range (Start Address)"),
    )
    ip_range_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IPRange.objects.all(),
        field_name="source_ranges",
        to_field_name="id",
        label=_("Source Range (ID)"),
    )
    source_pool_id = django_filters.ModelMultipleChoiceFilter(
        queryset=NatPool.objects.all(),
        field_name="source_pool",
        to_field_name="id",
        label=_("Source Pool (ID)"),
    )
    source_pool = django_filters.ModelMultipleChoiceFilter(
        queryset=NatPool.objects.all(),
        field_name="source_pool__name",
        to_field_name="name",
        label=_("Source Pool (Name)"),
    )
    destination_pool_id = django_filters.ModelMultipleChoiceFilter(
        queryset=NatPool.objects.all(),
        field_name="destination_pool",
        to_field_name="id",
        label=_("Destination Pool (ID)"),
    )
    destination_pool = django_filters.ModelMultipleChoiceFilter(
        queryset=NatPool.objects.all(),
        field_name="destination_pool__name",
        to_field_name="name",
        label=_("Destination Pool (Name)"),
    )

    class Meta:
        model = NatRule
        fields = ["id", "name", "description", "custom_interface"]

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(custom_interface__icontains=value)
        )
        return queryset.filter(qs_filter)


class NatRuleAssignmentFilterSet(AssignmentFilterSet):
    rule_id = django_filters.ModelMultipleChoiceFilter(
        queryset=NatRule.objects.all(),
        label=_("NAT Rule (ID)"),
    )
    rule = django_filters.ModelMultipleChoiceFilter(
        field_name="rule__name",
        queryset=NatRule.objects.all(),
        to_field_name="name",
        label=_("NAT Rule (Name)"),
    )

    class Meta:
        model = NatRuleAssignment
        fields = ("id", "rule_id", "assigned_object_type", "assigned_object_id")
