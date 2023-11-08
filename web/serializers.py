from .models import Attempt
from rest_framework.serializers import ModelSerializer
class AttemptSerializer(ModelSerializer):
    class Meta:
        model = Attempt
        fields = ['user', 'version', 'xmipp', 'date', 'returnCode', 'logTail']
