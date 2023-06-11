from rest_framework import serializers
from battle.models import CurrentBattleList, BattleUser
from users.models import User


class BattleParticipantSerializer(serializers.ModelSerializer):
    participant = serializers.StringRelatedField()

    class Meta:
        model = BattleUser
        fields = [
            "btl",
            "participant",
            "is_host",
        ]


class BattleListSerializer(serializers.ModelSerializer):
    host_user = serializers.StringRelatedField()
    participants = serializers.SerializerMethodField()

    def get_participants(self, obj):
        return obj.battle_room_id.count()

    class Meta:
        model = CurrentBattleList
        fields = [
            "id",
            "btl_title",
            "host_user",
            "btl_created_at",
            "btl_updated_at",
            "participants",
        ]


class BattleDetailSerializer(serializers.ModelSerializer):
    host_user = serializers.StringRelatedField()
    participant_list = BattleParticipantSerializer(many=True, source="battle_room_id")

    class Meta:
        model = CurrentBattleList
        fields = [
            "id",
            "btl_title",
            "host_user",
            "btl_created_at",
            "btl_updated_at",
            "participant_list",
        ]


class BattleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentBattleList
        fields = [
            "btl_title",
        ]
