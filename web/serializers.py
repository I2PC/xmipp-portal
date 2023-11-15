from .models import Attempt, User, Version, Xmipp
from rest_framework.serializers import ModelSerializer

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['ID', 'country']
class XmippSerializer(ModelSerializer):
    class Meta:
        model = Xmipp
        fields = ['branch', 'updated']

class VersionsSerializer(ModelSerializer):
    class Meta:
        model = Version
        fields = ['os', 'cudaVersion', 'cmakeVersion', 'gccVersion', 'gppVersion', 'sconsVersion']

class AttemptSerializer(ModelSerializer):
    user = UserSerializer()
    xmipp = XmippSerializer()
    version = VersionsSerializer()
    class Meta:
        model = Attempt
        fields = ['user', 'version', 'xmipp', 'date', 'returnCode', 'logTail']

    #def create(self, validated_data):
    #       print('In create()')

    #       user_data = validated_data.pop('user')
    #       version_data = validated_data.pop('version')
    #       xmipp_data = validated_data.pop('xmipp')

    #       user, _ = User.objects.get_or_create(**user_data)
    #       version, _ = Version.objects.get_or_create(**version_data)
    #       xmipp, _ = Xmipp.objects.get_or_create(**xmipp_data)

    #       attempt = Attempt.objects.create(
    #           user=user, version=version, xmipp=xmipp, **validated_data)
    #       return attempt

    def validate_ID(self, value):
        print('Validate')
        # Si el usuario ya existe, no lanzar un error
        #if User.objects.filter(ID=value).exists():
        #    return value
        return value