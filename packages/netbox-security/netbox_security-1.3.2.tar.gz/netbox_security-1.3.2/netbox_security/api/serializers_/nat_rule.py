from django.contrib.contenttypes.models import ContentType
from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ChoiceField,
    SerializerMethodField,
    JSONField,
    ValidationError,
    ListField,
    IntegerField,
)
from drf_spectacular.utils import extend_schema_field

from netbox.api.fields import SerializedPKRelatedField, ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from ipam.api.serializers import IPAddressSerializer, PrefixSerializer
from utilities.api import get_serializer_for_model
from ipam.models import IPAddress, Prefix

from netbox_security.models import NatRule, NatRuleAssignment
from netbox_security.constants import RULE_ASSIGNMENT_MODELS

from netbox_security.choices import (
    RuleStatusChoices,
    AddressTypeChoices,
    CustomInterfaceChoices,
)

from netbox_security.api.serializers import (
    NatPoolSerializer,
    NatRuleSetSerializer,
)


class NatRuleSerializer(NetBoxModelSerializer):
    url = HyperlinkedIdentityField(
        view_name="plugins-api:netbox_security-api:natrule-detail"
    )
    rule_set = NatRuleSetSerializer(nested=True, required=True)
    status = ChoiceField(choices=RuleStatusChoices, required=False)
    source_type = ChoiceField(choices=AddressTypeChoices, required=False)
    destination_type = ChoiceField(choices=AddressTypeChoices, required=False)
    custom_interface = ChoiceField(choices=CustomInterfaceChoices, required=False)
    source_addresses = SerializedPKRelatedField(
        nested=True,
        queryset=IPAddress.objects.all(),
        serializer=IPAddressSerializer,
        required=False,
        allow_null=True,
        many=True,
    )
    destination_addresses = SerializedPKRelatedField(
        nested=True,
        queryset=IPAddress.objects.all(),
        serializer=IPAddressSerializer,
        required=False,
        allow_null=True,
        many=True,
    )
    source_prefixes = SerializedPKRelatedField(
        nested=True,
        queryset=Prefix.objects.all(),
        serializer=PrefixSerializer,
        required=False,
        allow_null=True,
        many=True,
    )
    destination_prefixes = SerializedPKRelatedField(
        nested=True,
        queryset=Prefix.objects.all(),
        serializer=PrefixSerializer,
        required=False,
        allow_null=True,
        many=True,
    )
    source_pool = NatPoolSerializer(nested=True, required=False, allow_null=True)
    destination_pool = NatPoolSerializer(nested=True, required=False, allow_null=True)
    pool = NatPoolSerializer(nested=True, required=False, allow_null=True)
    source_ports = ListField(
        child=IntegerField(),
        required=False,
        allow_empty=True,
        default=[],
    )
    destination_ports = ListField(
        child=IntegerField(),
        required=False,
        allow_empty=True,
        default=[],
    )

    class Meta:
        model = NatRule
        fields = (
            "id",
            "url",
            "display",
            "rule_set",
            "name",
            "description",
            "status",
            "source_type",
            "destination_type",
            "source_addresses",
            "destination_addresses",
            "source_prefixes",
            "destination_prefixes",
            "source_ranges",
            "destination_ranges",
            "source_pool",
            "destination_pool",
            "source_ports",
            "destination_ports",
            "pool",
            "custom_interface",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "rule_set",
            "name",
            "description",
            "status",
        )

    def validate(self, data):
        if not isinstance(data, dict):
            return super().validate(data)

        def check_overlap(field1, field2, message, show_values=False):
            val1 = data.get(field1)
            val2 = data.get(field2)

            if val1 is not None and val2 is not None:
                # Use set comparison for iterables, direct equality for others
                if isinstance(val1, list) and isinstance(val2, list):
                    if set(val1) & set(val2):
                        full_msg = (
                            f"{message}: {val1} - {val2}" if show_values else message
                        )
                        return {field1: [full_msg], field2: [full_msg]}
                elif val1 == val2:
                    return {field1: [message], field2: [message]}
            return {}

        violations = [
            check_overlap(
                "source_addresses",
                "destination_addresses",
                "Source and Destination addresses cannot match",
                show_values=True,
            ),
            check_overlap(
                "source_prefixes",
                "destination_prefixes",
                "Source and Destination prefixes cannot match",
            ),
            check_overlap(
                "source_pool",
                "destination_pool",
                "Source and Destination pools cannot match",
            ),
            check_overlap(
                "source_ranges",
                "destination_ranges",
                "Source and Destination ranges cannot match",
            ),
        ]

        error_dict = {}
        for error in violations:
            error_dict.update(error)

        if error_dict:
            raise ValidationError(error_dict)

        return super().validate(data)

    def create(self, validated_data):
        source_addresses = validated_data.pop("source_addresses", None)
        destination_addresses = validated_data.pop("destination_addresses", None)
        source_prefixes = validated_data.pop("source_prefixes", None)
        destination_prefixes = validated_data.pop("destination_prefixes", None)
        source_ranges = validated_data.pop("source_ranges", None)
        destination_ranges = validated_data.pop("destination_ranges", None)
        obj = super().create(validated_data)
        if source_addresses is not None:
            obj.source_addresses.set(source_addresses)
        if destination_addresses is not None:
            obj.destination_addresses.set(destination_addresses)
        if source_prefixes is not None:
            obj.source_prefixes.set(source_prefixes)
        if destination_prefixes is not None:
            obj.destination_prefixes.set(destination_prefixes)
        if source_ranges is not None:
            obj.source_ranges.set(source_ranges)
        if destination_ranges is not None:
            obj.destination_ranges.set(destination_ranges)
        return obj

    def update(self, instance, validated_data):
        source_addresses = validated_data.pop("source_addresses", None)
        destination_addresses = validated_data.pop("destination_addresses", None)
        source_prefixes = validated_data.pop("source_prefixes", None)
        destination_prefixes = validated_data.pop("destination_prefixes", None)
        source_ranges = validated_data.pop("source_ranges", None)
        destination_ranges = validated_data.pop("destination_ranges", None)
        obj = super().update(instance, validated_data)
        if source_addresses is not None:
            obj.source_addresses.set(source_addresses)
        if destination_addresses is not None:
            obj.destination_addresses.set(destination_addresses)
        if source_prefixes is not None:
            obj.source_prefixes.set(source_prefixes)
        if destination_prefixes is not None:
            obj.destination_prefixes.set(destination_prefixes)
        if source_ranges is not None:
            obj.source_ranges.set(source_ranges)
        if destination_ranges is not None:
            obj.destination_ranges.set(destination_ranges)
        return obj


class NatRuleAssignmentSerializer(NetBoxModelSerializer):
    rule = NatRuleSerializer(nested=True, required=True, allow_null=False)
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(RULE_ASSIGNMENT_MODELS)
    )
    assigned_object = SerializerMethodField(read_only=True)

    class Meta:
        model = NatRuleAssignment
        fields = [
            "id",
            "url",
            "display",
            "rule",
            "assigned_object_type",
            "assigned_object_id",
            "assigned_object",
            "created",
            "last_updated",
        ]
        brief_fields = (
            "id",
            "url",
            "display",
            "rule",
            "assigned_object_type",
            "assigned_object_id",
        )

    @extend_schema_field(JSONField(allow_null=True))
    def get_assigned_object(self, obj):
        if obj.assigned_object is None:
            return None
        serializer = get_serializer_for_model(obj.assigned_object)
        context = {"request": self.context["request"]}
        return serializer(obj.assigned_object, nested=True, context=context).data
