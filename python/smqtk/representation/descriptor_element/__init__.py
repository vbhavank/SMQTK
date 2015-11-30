import abc
import numpy

from smqtk.representation import SmqtkRepresentation
from smqtk.utils import plugin


__author__ = "paul.tunison@kitware.com"


class DescriptorElement (SmqtkRepresentation, plugin.Pluggable):
    """
    Abstract descriptor vector container.

    This structure supports implementations that cache descriptor vectors on a
    per-UUID basis.

    Descriptor element equality based on shared descriptor type and vector
    equality. Two descriptor vectors that are generated by different types of
    descriptor generator should not be considered the same (though, this may be
    up for discussion).

    """

    def __init__(self, type_str, uuid):
        """
        Initialize a new descriptor element.

        :param type_str: Type of descriptor. This is usually the name of the
            content descriptor that generated this vector.
        :type type_str: str

        :param uuid: Unique ID reference of the descriptor.
        :type uuid: collections.Hashable

        """
        self._type_label = type_str
        self._uuid = uuid

    def __hash__(self):
        return hash((self.type(), self.uuid()))

    def __eq__(self, other):
        if isinstance(other, DescriptorElement):
            b = self.vector() == other.vector()
            if isinstance(b, numpy.core.multiarray.ndarray):
                vec_equal = b.all()
            else:
                vec_equal = b
            return vec_equal and (self.type() == other.type())
        return False

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return "%s{type: %s, uuid: %s}" % (self.__class__.__name__, self.type(),
                                           self.uuid())

    @classmethod
    def get_default_config(cls):
        """
        Generate and return a default configuration dictionary for this class.
        This will be primarily used for generating what the configuration
        dictionary would look like for this class without instantiating it.

        By default, we observe what this class's constructor takes as arguments,
        aside from the first two assumed positional arguments, turning those
        argument names into configuration dictionary keys.
        If any of those arguments have defaults, we will add those values into
        the configuration dictionary appropriately.
        The dictionary returned should only contain JSON compliant value types.

        It is not be guaranteed that the configuration dictionary returned
        from this method is valid for construction of an instance of this class.

        :return: Default configuration dictionary for the class.
        :rtype: dict

        """
        # similar to parent impl, except we remove the ``type_str`` and ``uuid``
        # configuration parameters as they are to be specified at runtime.
        dc = super(DescriptorElement, cls).get_default_config()
        # These parameters must be specified at construction time.
        del dc['type_str'], dc['uuid']
        return dc

    # noinspection PyMethodOverriding
    @classmethod
    def from_config(cls, config_dict, type_str, uuid):
        """
        Instantiate a new instance of this class given the desired type, uuid,
        and JSON-compliant configuration dictionary.

        :param type_str: Type of descriptor. This is usually the name of the
            content descriptor that generated this vector.
        :type type_str: str

        :param uuid: Unique ID reference of the descriptor.
        :type uuid: collections.Hashable

        :param config_dict: JSON compliant dictionary encapsulating
            a configuration.
        :type config_dict: dict

        :return: Constructed instance from the provided config.
        :rtype: DescriptorElement

        """
        # merge input config on top of defaults
        merged_config = cls.get_default_config()
        merged_config.update(config_dict)
        return cls(type_str, uuid, **merged_config)

    def uuid(self):
        """
        :return: Unique ID for this vector.
        :rtype: collections.Hashable
        """
        return self._uuid

    def type(self):
        """
        :return: Type label type of the DescriptorGenerator that generated this
            vector.
        :rtype: str
        """
        return self._type_label

    ###
    # Abstract methods
    #

    @abc.abstractmethod
    def has_vector(self):
        """
        :return: Whether or not this container current has a descriptor vector
            stored.
        :rtype: bool
        """
        return

    @abc.abstractmethod
    def vector(self):
        """
        :return: Get the stored descriptor vector as a numpy array. This returns
            None of there is no vector stored in this container.
        :rtype: numpy.core.multiarray.ndarray or None
        """
        return

    @abc.abstractmethod
    def set_vector(self, new_vec):
        """
        Set the contained vector.

        If this container already stores a descriptor vector, this will
        overwrite it.

        :param new_vec: New vector to contain.
        :type new_vec: numpy.core.multiarray.ndarray

        """
        return


from ._io import *


def get_descriptor_element_impls(reload_modules=False):
    """
    Discover and return Descriptor implementation classes found in the plugin
    directory. Keys in the returned map are the names of the discovered classes
    and the paired values are the actual class type objects.

    We look for modules (directories or files) that start with and alphanumeric
    character ('_' prefixed files/directories are hidden, but not recommended).

    Within a module, we first look for a helper variable by the name
    ``DESCRIPTOR_ELEMENT_CLASS``, which can either be a single class object or
    an iterable of class objects, to be exported. If the variable is set to
    None, we skip that module and do not import anything. If the variable is not
    present, we look for a class by the same na e and casing as the module's
    name. If neither are found, the module is skipped.

    :param reload_modules: Explicitly reload discovered modules from source.
    :type reload_modules: bool

    :return: Map of discovered class objects of type ``DescriptorElement`` whose
        keys are the string names of the classes.
    :rtype: dict[str, type]

    """
    import os
    from smqtk.utils.plugin import get_plugins

    this_dir = os.path.abspath(os.path.dirname(__file__))
    env_var = "DESCRIPTOR_ELEMENT_PATH"
    helper_var = "DESCRIPTOR_ELEMENT_CLASS"
    return get_plugins(__name__, this_dir, env_var, helper_var,
                       DescriptorElement, reload_modules)
