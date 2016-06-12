from typing import List, Dict, Any, Tuple, Union


class CaseClassMeta(type):
    """ Meta-Class for case classes. """

    instance_keys = {}  # type: Dict[type, List[Tuple[List[Any], Dict[str, Any]]]]
    instance_values = {}  # type: Dict[type, Dict[int, Any]]

    def __new__(mcs, name: str, bases: List[type], attrs: Dict[str, Any]):
        """ Creates a new class with MetaClass CaseClassMeta.

        :param name: Name of the class to create.
        :param bases: Base classes for the class.
        :param attrs: Attributes of this class.
        """

        # skip the CaseClass and AbstractCaseClass
        if CaseClassBase in bases:
            return super(CaseClassMeta, mcs).__new__(mcs, name, bases, attrs)

        # no case-to-case inheritance
        if CaseClassMeta.inherits_from_caseclass(bases):
            raise ValueError("Cannot create class %s: Case-to-case inheritance is prohibited. " % name)

        # store the reference to the old __init__ class in a variable old_init

        # if we have an __oldinit__ this is perfectly fine
        if "__init__" in attrs:
            old_init = attrs["__init__"]

        # else we shall just call the super class manually we need to call the super() __init__
        else:
            def old_init(self, *args, **kwargs):
                super(cls, self).__init__(*args, **kwargs)

        # Define a new __init__ function that (1) makes sure the cc is instantiated and (2) calls the oldinit function.
        def __init__(self, *args, **kwargs):

            CaseClass.__case_class_init__(self, *args, **kwargs)

            return old_init(self, *args, **kwargs)

        # set that as the __init__
        attrs["__init__"] = __init__

        # create the class
        cls = super(CaseClassMeta, mcs).__new__(mcs, name, bases, attrs)

        # and return it
        return cls


    def __call__(cls, *args: List[Any], **kwargs: Dict[str, Any]):
        """ Creates a new CaseClass() instance.

        :param args: Arguments to this CaseClass instance.
        :param kwargs: Keyword arguments to this CaseClass instance.
        :return: a new CaseClass instance.
        """
        if AbstractCaseClass in cls.__bases__:
            raise TypeError("Cannot instantiate AbstractCaseClass %s" % (cls.__name__, ))

        if cls == CaseClass:
            raise TypeError("A CaseClass can only be created as a subclass. ")

        # make sure we have the dictionary
        if cls not in CaseClassMeta.instance_keys:
            CaseClassMeta.instance_keys[cls] = []
            CaseClassMeta.instance_values[cls] = {}

        # Extract the instances for this class
        ckey = CaseClassMeta.instance_keys[cls]
        cval = CaseClassMeta.instance_values[cls]

        # key we will use for this instance.
        key = (args, kwargs)

        # try and return an existing instance.
        try:
            return cval[ckey.index(key)]
        except ValueError:
            pass

        # create a new instance
        instance = super(CaseClassMeta, cls).__call__(*args, **kwargs)

        # store the instance
        idx = len(ckey)
        ckey.append(key)
        cval[idx] = instance

        # and return it
        return instance

    @staticmethod
    def get_hash(cc) -> int:
        """ Gets a hash for a CaseClass or None.

        :param cc: CaseClass instance to get hash for
        :type cc: CaseClass
        """

        if not isinstance(cc, CaseClass):
            raise ValueError("Argument is not a CaseClass, can not get hash. ")

        # get a key for the instance
        cls = cc.__class__
        key = (cc.case_args, cc.case_kwargs)

        # extract the key
        ckey = CaseClassMeta.instance_keys[cls]
        idx = ckey.index(key)

        # and return a hash of it
        return hash((CaseClassMeta, ckey, idx))

    @staticmethod
    def is_concrete_caseclass(cls : type) -> bool:
        """ Checks if a class is a concrete case class via inheritance.

        :type cls: Class to check
        """

        return cls != AbstractCaseClass and CaseClass in cls.__bases__

    @staticmethod
    def inherits_from_caseclass(bases: List[type]) -> bool:
        """ Checks if this class inherits from a non-inheritable case class.

        :param bases: List of bases of the class to check
        """

        if InheritableCaseClass in bases:
            return False

        for b in bases:
            if CaseClassMeta.is_concrete_caseclass(b):
                return True

        return False



    @staticmethod
    def get_base_closure(type_or_list_of_types : Union[type, List[type]]) -> List[type]:
        """ Returns the transitive closure of the bases of a type. """

        if isinstance(type_or_list_of_types, type):
            return [type_or_list_of_types] + CaseClassMeta.get_base_closure(type_or_list_of_types.__bases__)

        types = set()

        for t in type_or_list_of_types:
            types.update(map(CaseClassMeta.get_base_closure, t))

        return list(types)


class AbstractCaseClassMeta(CaseClassMeta):
    """ Represents an abstract case class that can not be instantianted. """

    def __call__(cls, *args: List[Any], **kwargs: Dict[str, Any]):

        if AbstractCaseClass in cls.__bases__ and not InheritableCaseClass in cls.__bases__:
            raise TypeError("Can not instantiate AbstractCaseClass %s" % cls.__name__)

        return super(AbstractCaseClassMeta, cls).__call__(*args, **kwargs)

class CaseClassBase(object):
    """ Internal base class for CaseClasses """
    pass

class CaseClass(CaseClassBase, metaclass=CaseClassMeta):
    """ Super-class used for all case classes. """

    def __case_class_init__(self, *args: List[Any], **kwargs: Dict[str, Any]):
        """ Initialises case class parameters. """

        # The name of this case class
        self.__name = self.__class__.__name__  # type: str

        # The arguments given to this case class
        self.__args = args  # type: List[Any]

        # The keyword arguments given to this case class
        self.__kwargs = kwargs  # type: Dict[str, Any]

    def __hash__(self) -> int:
        """ Returns a hash representing this case class. """

        return hash((CaseClassMeta, CaseClass, ))

    @property
    def case_args(self) -> List[Any]:
        """ Returns the arguments originally given to this CaseClass. """

        return self.__args
    
    @property
    def case_kwargs(self) -> Dict[str, Any]:
        """ Returns the keyword arguments given to this CaseClass. """

        return self.__kwargs

    def __repr__(self) -> str:
        """ Implements a representation for Case classes. This is given by the class
        name and the representation of all the parameters.
        """

        # string representations of the arguments and keyword arguments
        a_list = list(map(repr, self.case_args))
        kwarg_list = list(map(lambda p:"%s=%r" % p, self.case_kwargs.items()))

        # join them
        a_repr = ",".join(a_list+kwarg_list)

        # and put them after the name of the class
        return "%s(%s)" % (self.__name, a_repr)

class AbstractCaseClass(CaseClass, CaseClassBase, metaclass=AbstractCaseClassMeta):
    """ Represents a non-instatiable abstract case class. """

    pass

class InheritableCaseClass(CaseClass, CaseClassBase):
    """ Represent a caseClass that may be inherited from. """

    pass