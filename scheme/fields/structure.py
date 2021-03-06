from scheme.exceptions import *
from scheme.field import *
from scheme.fields.enumeration import Enumeration
from scheme.interpolation import interpolate_parameters
from scheme.util import getitem, string

__all__ = ('Structure',)

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

class Structure(Field):
    """A field for structures containing specific key/value pairs.

    A structure is defined with an explicit set of key/value pairs, with each pair value
    being a :class:`scheme.field.Field` value which specifies the potential value for that key
    within the structure. The standard representation of a structure is a ``dict``.

    Structures can be polymorphic, such that a discriminator value within a candidate value is
    used to determine the structure variant used to parse the rest of the candidate value. To
    define a polymorphic structure, ``polymorphic_on`` needs to be specified and ``structure``
    needs to be a nested ``dict``.

    :param dict structure: A ``dict`` containing ``str`` keys and :class:`Field` values which
        describes the structure of this field. When ``polymorphic_on`` is specified, this value
        needs to be nested accordingly.

    :param boolean strict: Optional, default is ``True``; if ``False``, key/value pairs which are
        not defined in ``structure`` are silently ignored and dropped during validation instead
        of causing a :exc:`ValidationError` to be raised.

    :param polymorphic_on: Optional, default is ``None``; if specified, should be either a
        :class:`Field` insance to be used as the discriminator field for this field, or a ``str``
        specifying the name of the discriminator field that should be autogenerated. In either
        case, specifying ``polymorphic_on`` makes this field polymorphic.

    :param boolean generate_default: Optional, default is ``False``; 

    :param boolean generate_default: Optional, default is ``False``; if ``True``, a default value
        for this field will be dynamically constructed by collecting the default values, if any,
        of the fields specified within ``structure``.

    :param list key_order: Optional, default is ``None``; if specified, either a ``list``
        containing the keys defined for this field or a space-delimited ``str`` containing the
        same. In either case, the argument should specify the preferred ordering of keys for output
        values of this field, and will cause such output values to be :class:`OrderedDict` instead
        of plain ``dict``.
    """

    basetype = 'structure'
    parameters = {'strict': True}
    structural = True

    errors = [
        FieldError('invalid', 'invalid value', '%(field)s must be a structure'),
        FieldError('required', 'required field', "%(field)s is missing required field '%(name)s'"),
        FieldError('unknown', 'unknown field', "%(field)s includes an unknown field '%(name)s'"),
        FieldError('unrecognized', 'unrecognized polymorphic identity',
            "%(field)s must specify a recognized polymorphic identity"),
    ]

    def __init__(self, structure, strict=True, polymorphic_on=None, generate_default=False,
            key_order=None, **params):

        if not isinstance(structure, dict):
            raise TypeError("argument 'structure' must be a dict value")

        if polymorphic_on:
            if '*' in structure:
                common = structure.pop('*')
                for value in structure.values():
                    value.update(common)
            if isinstance(polymorphic_on, string):
                polymorphic_on = Enumeration(sorted(structure.keys()), nonempty=True,
                    name=polymorphic_on)
            if not isinstance(polymorphic_on, Field):
                raise TypeError("argument 'polymorphic_on' must be either a Field instance or None")
            if not polymorphic_on.required:
                polymorphic_on = polymorphic_on.clone(required=True)

        if not key_order:
            key_order = None
        if isinstance(key_order, string):
            key_order = key_order.split(' ')
        if key_order and not isinstance(key_order, list):
            raise TypeError("argument 'key_order' must be either None, a list of strings, or"
                " a space-delimited string of key names")

        super(Structure, self).__init__(**params)
        self.key_order = key_order
        self.polymorphic_on = polymorphic_on
        self.strict = strict
        self.structure = structure

        if polymorphic_on:
            for identity, candidate in self.structure.items():
                self._prevalidate_structure(candidate, identity)
                candidate[polymorphic_on.name] = polymorphic_on.clone(constant=identity)
        else:
            self._prevalidate_structure(self.structure)

        if generate_default and not self.default:
            if self.polymorphic:
                if generate_default in self.structure:
                    self.default = self.generate_defaults(generate_default)
                else:
                    raise ValueError('generate_default must be a valid polymorphic identity')
            elif generate_default is True:
                self.default = self.generate_defaults()
            else:
                raise ValueError('generate_default must be boolean')

    def __repr__(self):
        aspects = ['structure=%r' % self.structure]
        if self.polymorphic_on:
            aspects.append('polymorphic_on=%r' % self.polymorphic_on.name)
        if not self.strict:
            aspects.append('strict=False')
        if self.key_order:
            aspects.append('key_order=%r' % self.key_order)
        return super(Structure, self).__repr__(aspects)

    @property
    def has_required_fields(self):
        """need doc"""

        if self.polymorphic_on:
            return True

        for field in self.structure.values():
            if field.required and field.default is None:
                return True
        else:
            return False

    @property
    def polymorphic(self):
        """need doc"""

        return (self.polymorphic_on is not None)

    def describe(self, parameters=None, verbose=False):
        default_structure = self.structure
        
        polymorphic_on = self.polymorphic_on
        if polymorphic_on:
            if self.default:
                default_structure = self.structure[self.default[polymorphic_on.name]]

            structure = {}
            for identity, candidate in self.structure.items():
                identity = polymorphic_on._serialize_value(identity)
                structure[identity] = self._describe_structure(candidate, parameters, verbose)

            polymorphic_on = polymorphic_on.describe(parameters, verbose)
        else:
            structure = self._describe_structure(self.structure, parameters, verbose)

        default = None
        if self.default:
            default = {}
            for name, value in self.default.items():
                default[name] = default_structure[name]._serialize_value(value)

        return super(Structure, self).describe(parameters, verbose, default=default,
            polymorphic_on=polymorphic_on, structure=structure)

    def extend(self, structure):
        """Constructs and returns a clone of this field extended with the key/field pairs specified
        in ``structure``."""

        extension = self.clone()
        for name, field in structure.items():
            if not isinstance(field, Field):
                raise TypeError("values of argument 'structure' must be Field instances")
            if field.name != name:
                field.name = name
            extension.structure[name] = field

        return extension

    def extract(self, subject, strict=True, **params):
        if params and not self.screen(**params):
            raise FieldExcludedError(self)

        if subject is None:
            return None

        if self.extractor:
            try:
                subject = self.extractor(self, subject)
            except Exception:
                raise CannotExtractError('extractor raised exception')

        if isinstance(subject, dict):
            getter = getitem
        elif not strict:
            getter = getattr
        else:
            raise CannotExtractError('extraction candidate must be a dict value')

        definition = self._get_definition(subject, getter)
        extraction = {}

        for name, field in definition.items():
            try:
                value = getter(subject, name)
                if value is None:
                    continue
            except (AttributeError, KeyError):
                continue

            try:
                extraction[name] = field.extract(value, strict, **params)
            except FieldExcludedError:
                pass
            except AttributeError:
                if isinstance(field, Undefined):
                    raise UndefinedFieldError('the %r field of this structure is undefined' % name)
                else:
                    raise

        return extraction

    def filter(self, all=False, **params):
        if not super(Structure, self).filter(all, **params):
            return None

        filtered = False
        if self.polymorphic_on:
            structure = {}
            for identity, substructure in self.structure.items():
                candidate = self._filter_structure(substructure, all, params)
                if candidate:
                    structure[identity] = candidate
                    filtered = True
                else:
                    structure[identity] = substructure
        else:
            structure = self._filter_structure(self.structure, all, params)
            if structure:
                filtered = True

        if filtered:
            return self.clone(structure=structure)
        else:
            return self

    def generate_defaults(self, identity=None, sparse=True):
        """need doc"""

        if not self.polymorphic:
            if identity is None:
                return self._generate_default_values(self.structure, sparse)
            else:
                raise ValueError(identity)

        if identity is not None:
            if identity in self.structure:
                return self._generate_default_values(self.structure[identity], sparse)
            else:
                raise ValueError(identity)

        defaults = {}
        for identity, structure in self.structure.items():
            defaults[identity] = self._generate_default_values(structure, sparse)
        return defaults

    def get(self, key, default=None):
        return self.structure.get(key, default)

    def insert(self, field, overwrite=False):
        """Inserts ``field`` into the structure of this field.

        :param field: The ``Field`` instance to insert; must have a valid name.

        :param boolean overwrite: Optional, default is ``False``; if ``True``, ``field``
            will be inserted regardless of the preexisting presence of a field with the
            same name.
        """

        if not isinstance(field, Field):
            raise TypeError("argument 'field' must be a Field instance")
        if not field.name:
            raise ValueError("argument 'field' must have a defined 'name' attribute")
        if overwrite or field.name not in self.structure:
            self.structure[field.name] = field

    def instantiate(self, value, key=None):
        if value is None:
            return None

        definition = self._get_definition(value)
        params = {}
        
        for k, v in value.items():
            try:
                params[k] = definition[k].instantiate(v, k)
            except AttributeError:
                if isinstance(definition[k], Undefined):
                    raise UndefinedFieldError('the %r field of this structure is undefined' % k)
                else:
                    raise

        return super(Structure, self).instantiate(params, key)

    def interpolate(self, subject, parameters, interpolator=None):
        if subject is None:
            return None

        if isinstance(subject, string):
            subject = interpolate_parameters(subject, parameters, True, interpolator)

        if not isinstance(subject, dict):
            raise CannotInterpolateError('interpolation candidate must be a dict value')

        definition = self._get_definition(subject)
        interpolation = {}

        for name, field in definition.items():
            try:
                value = subject[name]
            except KeyError:
                continue

            try:
                interpolation[name] = field.interpolate(value, parameters, interpolator)
            except UndefinedParameterError:
                continue
            except AttributeError:
                if isinstance(field, Undefined):
                    raise UndefinedFieldError('the %r field of this structure is undefined' % name)
                else:
                    raise

        return interpolation

    def merge(self, structure, prefer=False):
        """Merges all key/field pairs in ``structure`` into this field.

        :param dict structure: A `dict` containing key/field pairs.

        :param boolean prefer: Optional, default is ``False``; if ``True``, key/field pairs
            which are already present in this field will be replaced with matching ones from
            ``structure``. By default, such pairs are ignored.
        """

        for name, field in structure.items():
            if not isinstance(field, Field):
                raise TypeError("values of argument 'structure' must be Field instances")
            if name in self.structure and not prefer:
                return
            if field.name != name:
                field = field.clone(name=name)
            self.structure[name] = field

    def process(self, value, phase=INBOUND, serialized=False, ancestry=None, partial=False):
        if not ancestry:
            ancestry = [self.guaranteed_name]

        if self._is_null(value, ancestry):
            return None

        if not isinstance(value, dict):
            raise InvalidTypeError(identity=ancestry, field=self, value=value).construct('invalid')

        if self.preprocessor:
            try:
                value = self.preprocessor(value)
            except Exception:
                raise InvalidTypeError(identity=ancestry, field=self,
                    value=value).construct('invalid').capture()

        valid = True
        names = set(value.keys())

        identity = None
        definition = self.structure

        polymorphic_on = self.polymorphic_on
        if polymorphic_on:
            identity = value.get(polymorphic_on.name)
            if identity is None:
                raise ValidationError(identity=ancestry, field=self).construct('required',
                    name=polymorphic_on.name)

            identity = polymorphic_on.process(identity, phase, serialized,
                ancestry + ['.' + polymorphic_on.name])

            definition = self.structure.get(identity)
            if not definition:
                raise ValidationError(identity=ancestry, field=self,
                    value=identity).construct('unrecognized')

        if self.key_order:
            structure = OrderedDict()
            if identity:
                key_order = self.key_order[identity]
            else:
                key_order = self.key_order
        else:
            structure = {}
            key_order = definition.keys()

        for name in key_order:
            field = definition[name]
            if name in names:
                names.remove(name)
                field_value = value[name]
            elif partial:
                continue
            elif phase == INBOUND and field.default is not None:
                field_value = field.default
            elif field.required:
                valid = False
                structure[name] = ValidationError(identity=ancestry, field=self).construct(
                    'required', name=name)
                continue
            else:
                continue

            try:
                if not (field.ignore_null and field_value is None):
                   structure[name] = field.process(field_value, phase, serialized,
                        ancestry + ['.' + name])
                else:
                    continue
            except StructuralError as exception:
                valid = False
                structure[name] = exception
            except AttributeError:
                if isinstance(field, Undefined):
                    raise UndefinedFieldError("the %r field of this structure is undefined" % name)
                else:
                    raise

        if self.strict:
            for name in names:
                valid = False
                structure[name] = ValidationError(identity=ancestry, field=self).construct(
                    'unknown', name=name)

        if valid:
            return structure
        else:
            raise ValidationError(identity=ancestry, field=self, value=value, structure=structure)

    def remove(self, *names):
        """Removes the field named ``name`` from the structure of this field.
        """

        for name in names:
            if name in self.structure:
                del self.structure[name]

    def replace(self, structure):
        """Constructs and returns a clone of this field with the key/field pairs specified
        in ``structure`` replacing any in this field with the same key. Any keys in
        ``structure`` not initially present in this field are silently ignored. If no
        replacements are made, this field is returned without cloning."""

        for name in structure:
            if name in self.structure:
                break
        else:
            return self

        replacement = self.clone()
        for name, field in structure.items():
            if not isinstance(field, Field):
                raise TypeError(field)
            if field.name != name:
                field.name = name
            if name in replacement.structure:
                replacement.structure[name] = field

        return replacement

    def transform(self, transformer):
        candidate = transformer(self)
        if isinstance(candidate, Field):
            return candidate
        elif candidate is False:
            return self

        transformed = False
        candidates = {}

        for name, field in self.structure.items():
            candidate = field.transform(transformer)
            if candidate is not field:
                candidates[name] = candidate
                transformed = True
            else:
                candidates[name] = field

        if transformed:
            return self.clone(structure=candidates)
        else:
            return self

    def _define_undefined_field(self, field, name):
        identity, name = name
        if self.polymorphic_on:
            self.structure[identity][name] = field.clone(name=name)
        else:
            self.structure[name] = field.clone(name=name)

    def _describe_structure(self, structure, parameters, verbose):
        description = {}
        for name, field in structure.items():
            description[name] = field.describe(parameters, verbose)

        return description

    def _filter_structure(self, structure, exclusive, params):
        filtered = False
        candidates = {}

        for name, field in structure.items():
            candidate = field.filter(all, **params)
            if candidate:
                candidates[name] = candidate
                if candidate is not field:
                    filtered = True
            else:
                filtered = True

        if filtered:
            return candidates

    def _generate_default_values(self, structure, sparse=False):
        default = {}
        for name, field in structure.items():
            value = field.default
            if value is None:
                value = field.constant
            if not sparse or value is not None:
                default[name] = value

        return default

    def _get_definition(self, value, getter=getitem):
        identity = self._get_polymorphic_identity(value, getter)
        if identity:
            return self.structure[identity]
        else:
            return self.structure

    def _get_polymorphic_identity(self, value, getter=getitem):
        polymorphic_on = self.polymorphic_on
        if polymorphic_on:
            return getter(value, polymorphic_on.name)

    def _prevalidate_structure(self, structure, identity=None):
        if not isinstance(structure, dict):
            raise TypeError("argument 'structure' must be a dict instance")

        for name, field in structure.items():
            if isinstance(field, Undefined):
                if field.field:
                    field = field.field
                    structure[name] = field
                else:
                    field.register(self._define_undefined_field, (identity, name))
                    continue

            if not isinstance(field, Field):
                raise TypeError("values of argument 'structure' must be Field instances")
            if not field.name:
                field.name = name

    @classmethod
    def _visit_field(cls, specification, callback):
        def visit(structure):
            return dict((k, callback(v)) for k, v in structure.items())

        if specification.get('polymorphic_on'):
            return {'structure': dict((k, visit(v)) for k, v
                in specification['structure'].items())}
        else:
            return {'structure': visit(specification['structure'])}
