from rest_framework import serializers
from battle.models import CurrentBattleList, BattleUser
from users.models import User
from users.serializers import UserBattleSerializer


class BattleParticipantSerializer(serializers.ModelSerializer):
    participant = UserBattleSerializer()

    class Meta:
        model = BattleUser
        fields = [
            # "btl",
            "participant",
            "is_host",
        ]


class BattleListSerializer(serializers.ModelSerializer):
    host_user = serializers.StringRelatedField()
    participants = serializers.SerializerMethodField()
    btl_category = serializers.CharField(source="get_btl_category_display")

    def get_participants(self, obj):
        return obj.battle_room_id.count()

    class Meta:
        model = CurrentBattleList
        fields = [
            "id",
            "btl_title",
            "btl_category",
            "host_user",
            "btl_created_at",
            "btl_updated_at",
            "participants",
            "max_users",
            "is_private",
            "room_password",
        ]


class BattleDetailSerializer(serializers.ModelSerializer):
    host_user = serializers.StringRelatedField()
    participant_list = BattleParticipantSerializer(many=True, source="battle_room_id")
    btl_category = serializers.CharField(source="get_btl_category_display")

    class Meta:
        model = CurrentBattleList
        fields = [
            "id",
            "btl_title",
            "btl_category",
            "host_user",
            "max_users",
            "is_private",
            "room_password",
            "btl_created_at",
            "btl_updated_at",
            "participant_list",
        ]


class BattleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentBattleList
        fields = [
            "btl_title",
            "btl_category",
            "max_users",
            "is_private",
            "room_password",
        ]
