import json
from typing import Any

import kubernetes
import yaml
from apischema import serialize
from kubernetes import utils
from kubernetes.client.models.v1_object_meta import V1ObjectMeta

from kubecrds.types import Scope
from dataclasses import fields

# ObjectMeta_attribute_map is simply the reverse of the
# V1ObjectMeta.attribute_map , which is a mapping from python attribute to json
# key while this is the opposite from json key to python attribute so that we
# can pass in the values to instantiate the V1ObjectMeta object.
ObjectMeta_attribute_map = {
    value: key for key, value in V1ObjectMeta.attribute_map.items()
}


class KubeResourceBase:
    """KubeResourceBase is base class that provides methods to converts dataclass
    into Kubernetes CR. It provides ability to create a Kubernetes CRD from the
    class and supports deserialization of the object JSON from K8s into Python
    obects with support for Metadata.
    """

    __group__: str
    __version__: str
    __scope__: Scope = Scope.NAMESPACE

    @staticmethod
    def dataclass_to_properties(dc_type: Any) -> dict:
        """Convert dataclass fields into CRD-style 'properties' schema."""
        props = {}
        for f in fields(dc_type):
            prop_schema = {}

            # Infer type
            if f.type is str:
                prop_schema["type"] = "string"
            elif f.type is int:
                prop_schema["type"] = "integer"
            elif f.type is bool:
                prop_schema["type"] = "boolean"
            elif f.type is float:
                prop_schema["type"] = "number"
            elif getattr(f.type, "__origin__", None) is list:
                prop_schema["type"] = "array"
                item_type = f.type.__args__[0]
                if item_type is str:
                    prop_schema["items"] = {"type": "string"}
                else:
                    prop_schema["items"] = {"type": "object"}

            elif getattr(f.type, "__module__", None) == "__main__":
                prop_schema["type"] = "object"
                prop_schema["properties"] = KubeResourceBase.dataclass_to_properties(
                    f.type
                )

            else:
                prop_schema["type"] = "object"

            # Add metadata (like description)
            prop_schema.update(f.metadata)

            props[f.name] = prop_schema

        return props

    @classmethod
    def apischema(cls):
        """Get serialized openapi 3.0 schema for the cls.

        The output is a dict with (possibly nested) key-value pairs based on
        the schema of the class. This is used to generate the CRD schema down
        the line which rely on (a subset?) of OpenAPIV3 schema for the
        definition of a Kubernetes Custom Resource.
        """

        return cls.dataclass_to_properties(dc_type=cls)

    @classmethod
    def apischema_json(cls):
        """JSON Serialized OpenAPIV3 schema for the cls."""
        return json.dumps(cls.apischema())

    @classmethod
    def apischema_yaml(cls):
        """YAML Serialized OpenAPIV3 schema for the cls."""
        yaml_schema = yaml.load(cls.apischema_json(), Loader=yaml.Loader)
        return yaml.dump(yaml_schema, Dumper=yaml.Dumper)

    @classmethod
    def singular(cls):
        """Return the 'singular' name of the CRD.

        This is currently just the lower case name of the Python class.
        """
        return cls.__name__.lower()

    @classmethod
    def plural(cls):
        """Plural name of the CRD.

        This defaults ot just the lower case name of the Python class with an
        additional 's' in the end of the name. This might not be correct for
        all CRs though.

        TODO: Make singular and plural a configurable parameter using dunder
        attributes on cls like ``__group__`` and ``__version__``.
        """
        return f"{cls.singular()}s"

    @classmethod
    def crd_schema_dict(cls):
        """Return cls serialized as a Kubernetes CRD schema dict.

        This returns a dict representation of the Kubernetes CRD Object of cls.
        """
        crd = {
            "apiVersion": "apiextensions.k8s.io/v1",
            "kind": "CustomResourceDefinition",
            "metadata": {
                "name": f"{cls.plural()}.{cls.__group__}",
            },
            "spec": {
                "group": cls.__group__,
                "scope": cls.__scope__.value,
                "names": {
                    "singular": cls.singular(),
                    "plural": cls.plural(),
                    "kind": cls.__name__,
                },
                "versions": [
                    {
                        "name": cls.__version__,
                        # This API is served by default, currently there is no
                        # support for multiple versions.
                        "served": True,
                        "storage": True,
                        "schema": {
                            "openAPIV3Schema": {
                                "type": "object",
                                "properties": {
                                    "spec": {
                                        "type": "object",
                                        "properties": cls.apischema(),
                                    }
                                },
                            }
                        },
                    }
                ],
            },
        }

        return crd

    @classmethod
    def crd_schema(cls):
        """Serialized YAML representation of Kubernetes CRD definition for cls.

        This serializes the dict representation from
        :py:method:`crd_schema_dict` to YAML.
        """
        return yaml.dump(
            yaml.load(json.dumps(cls.crd_schema_dict()), Loader=yaml.Loader),
            Dumper=yaml.Dumper,
        )

    @classmethod
    def from_json(cls, json_data):
        """Instantiate the class from json value fetched from Kubernetes.

        :param json_data: The CR JSON returned from Kubernetes API.
        :type json_data: Dict
        :returns: Instantiated cls with the data from json_data.
        :rtype: cls
        """
        assert json_data.get("apiVersion") == f"{cls.__group__}/{cls.__version__}"
        assert json_data.get("kind") == cls.__name__
        inputs = {}
        for key, value in json_data.get("metadata").items():
            inputs[ObjectMeta_attribute_map.get(key)] = value
        meta = V1ObjectMeta(**inputs)
        ins = cls(**json_data.get("spec"))
        ins.json = json_data
        ins.metadata = meta
        return ins

    @classmethod
    def install(cls, k8s_client, exist_ok=True):
        """Install the CRD in Kubernetes.

        :param k8s_client: Instantiated Kubernetes API Client.
        :type k8s_client: kubernetes.client.api_client.ApiClient
        :param exist_ok: Boolean representing if error should be raised when
            trying to install a CRD that was already installed.
        :type exist_ok: bool
        """
        try:
            utils.create_from_yaml(
                k8s_client,
                yaml_objects=[yaml.load(cls.crd_schema(), Loader=yaml.Loader)],
            )

        except utils.FailToCreateError as e:
            code = json.loads(e.api_exceptions[0].body).get("code")
            if code == 409 and exist_ok:
                return
            raise

    @classmethod
    def watch(cls, client):
        """List and watch the changes in the Resource in Cluster."""
        api_instance = kubernetes.client.CustomObjectsApi(client)
        watch = kubernetes.watch.Watch()
        for event in watch.stream(
            func=api_instance.list_cluster_custom_object,
            group=cls.__group__,
            version=cls.__version__,
            plural=cls.plural().lower(),
            watch=True,
            allow_watch_bookmarks=True,
            timeout_seconds=50,
        ):
            obj = cls.from_json(event["object"])
            yield (event["type"], obj)

    @classmethod
    async def async_watch(cls, k8s_client):
        """Similar to watch, but uses async Kubernetes client for aio."""
        from kubernetes_asyncio import client, watch

        api_instance = client.CustomObjectsApi(k8s_client)
        watch = watch.Watch()
        stream = watch.stream(
            func=api_instance.list_cluster_custom_object,
            group=cls.__group__,
            version=cls.__version__,
            plural=cls.plural().lower(),
            watch=True,
        )
        async for event in stream:
            obj = cls.from_json(event["object"])
            yield (event["type"], obj)

    def serialize(self, name_prefix=None):
        """Serialize the CR as a JSON suitable for POST'ing to K8s API."""
        if name_prefix is None:
            name_prefix = self.__class__.__name__.lower()

        return {
            "kind": self.__class__.__name__,
            "apiVersion": f"{self.__group__}/{self.__version__}",
            "spec": serialize(self),
            "metadata": {
                "name": (name_prefix + str(id(self))).lower(),
            },
        }

    def save(self, k8s_client, namespace="default"):
        """Save the instance of this class as a K8s custom resource."""
        api_instance = kubernetes.client.CustomObjectsApi(k8s_client)
        resp = api_instance.create_namespaced_custom_object(
            group=self.__group__,
            namespace=namespace,
            version=self.__version__,
            plural=self.plural(),
            body=self.serialize(),
        )
        return resp

    async def async_save(self, k8s_client, namespace="default"):
        """Save the instance of this class as a K8s custom resource."""
        from kubernetes_asyncio import client

        api_instance = client.CustomObjectsApi(k8s_client)
        resp = await api_instance.create_namespaced_custom_object(
            group=self.__group__,
            namespace=namespace,
            version=self.__version__,
            plural=self.plural(),
            body=self.serialize(),
        )
        return resp
