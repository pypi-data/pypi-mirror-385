from typing                                                                     import Dict, Any, Type

from osbot_utils.type_safe.Type_Safe__Primitive import Type_Safe__Primitive
from osbot_utils.type_safe.primitives.domains.identifiers.Obj_Id                import Obj_Id
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid           import Random_Guid
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Cache               import type_safe_cache, Type_Safe__Cache
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Shared__Variables   import IMMUTABLE_TYPES
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Validation          import type_safe_validation
from osbot_utils.type_safe.type_safe_core.steps.Type_Safe__Step__Default_Value  import type_safe_step_default_value


class Type_Safe__Step__Class_Kwargs:                                                     # Handles class-level keyword arguments processing

    type_safe_cache : Type_Safe__Cache                                                   # Cache component reference

    def __init__(self):
        self.type_safe_cache = type_safe_cache                                           # Initialize with singleton cache

    def get_cls_kwargs(self, cls                  : Type )\
                    -> Dict[str, Any]:                                                   # Main entry point for getting class kwargs, returns dict of class kwargs

        if not hasattr(cls, '__mro__'):                                                  # Handle non-class inputs
            return {}

        kwargs  = type_safe_cache.get_cls_kwargs(cls)                                    # see if we have cached data for this class

        if kwargs is not None:
            return kwargs
        else:
            kwargs = {}

        base_classes = type_safe_cache.get_class_mro(cls)
        for base_cls in base_classes:
            self.process_mro_class  (base_cls, kwargs)                                  # Handle each class in MRO
            self.process_annotations(cls, base_cls, kwargs)                             # Process its annotations

        if self.is_kwargs_cacheable(cls, kwargs):                                            # if we can cache it (i.e. only IMMUTABLE_TYPES vars)
            type_safe_cache.set_cache__cls_kwargs(cls, kwargs)                          #   cache it
        # else:
        #     pass                                                  # todo:: see how we can cache more the cases when the data is clean (i.e. default values)
        return kwargs

    def is_kwargs_cacheable(self, cls, kwargs: Dict[str, Any]) -> bool:                                         # check if we can cache the kwargs
        annotations = type_safe_cache.get_class_annotations(cls)
        match       = all(isinstance(value, IMMUTABLE_TYPES) for value in kwargs.values())

        if match:
            annotations_types = list(dict(annotations).values())
            for annotation_type in annotations_types:
                if isinstance(annotation_type, type) and issubclass(annotation_type, Type_Safe__Primitive):     # Don't cache if any field is a Type_Safe__Primitive
                    return False
        return match


    def handle_undefined_var(self, cls      : Type            ,                         # Handle undefined class variables
                                   kwargs   : Dict[str, Any] ,
                                   var_name : str            ,
                                   var_type : Type           )\
                          -> None:
        if var_name in kwargs:                                                          # Skip if already defined
            return
        var_value        = type_safe_step_default_value.default_value(cls, var_type)    # Get default value
        kwargs[var_name] = var_value                                                    # Store in kwargs

    def handle_defined_var(self, base_cls : Type ,                                      # Handle defined class variables
                                 var_name : str  ,
                                 var_type : Type )\
                        -> None:
        # var_value = getattr(base_cls, var_name)                                         # Get current value
        # if var_value is None:                                                           # Allow None assignments
        #     return
        #
        # if type_safe_validation.should_skip_type_check(var_type):                       # Skip validation if needed
        #     return
        #
        # type_safe_validation.validate_variable_type    (var_name, var_type, var_value)  # Validate type
        # type_safe_validation.validate_type_immutability(var_name, var_type)             # Validate immutability

        var_value = getattr(base_cls, var_name)
        if var_value is None:
            return
        if type_safe_validation.should_skip_type_check(var_type):
            return

        # NEW: Try to convert primitive values to Type_Safe__Primitive types
        from osbot_utils.type_safe.Type_Safe__Primitive import Type_Safe__Primitive
        if (isinstance(var_type, type) and
            issubclass(var_type, Type_Safe__Primitive) and
            type(var_value) in (str, int, float)):
            try:
                # Attempt conversion and validate the converted value
                converted_value = var_type(var_value)
                # Set the converted value back on the class
                setattr(base_cls, var_name, converted_value)
                var_value = converted_value
            except (ValueError, TypeError):
                # If conversion fails, let the original validation handle it
                pass

        type_safe_validation.validate_variable_type(base_cls, var_name, var_type, var_value)
        type_safe_validation.validate_type_immutability(var_name, var_type)

    def process_annotation(self, cls      : Type           ,                            # Process single annotation
                                 base_cls : Type           ,
                                 kwargs   : Dict[str, Any] ,
                                 var_name : str            ,
                                 var_type : Type           )\
                       -> None:
        if not hasattr(base_cls, var_name):                                             # Handle undefined variables
            self.handle_undefined_var(cls, kwargs, var_name, var_type)
        else:                                                                           # Handle defined variables
            self.handle_defined_var(base_cls, var_name, var_type)

    def process_annotations(self, cls      : Type           ,                           # Process all annotations
                                  base_cls : Type           ,
                                  kwargs   : Dict[str, Any] )\
                         -> None:
        if hasattr(base_cls, '__annotations__'):                                        # Process if annotations exist
            for var_name, var_type in type_safe_cache.get_class_annotations(base_cls):
                self.process_annotation(cls, base_cls, kwargs, var_name, var_type)

    def process_mro_class(self, base_cls : Type           ,                             # Process class in MRO chain
                                kwargs   : Dict[str, Any] )\
                       -> None:
        if base_cls is object:                                                                              # Skip object class
            return

        class_variables = type_safe_cache.get_valid_class_variables(base_cls                            ,
                                                                    type_safe_validation.should_skip_var)   # Get valid class variables

        for name, value in class_variables.items():                                                         # Add non-existing variables
            if name not in kwargs:
                kwargs[name] = value


# Create singleton instance
type_safe_step_class_kwargs = Type_Safe__Step__Class_Kwargs()