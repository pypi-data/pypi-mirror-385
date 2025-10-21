/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use dupe::Dupe;
use pyrefly_python::module_name::ModuleName;
use ruff_python_ast::name::Name;

/// These are names that are exported from the stdlib, but which take on
/// a more keyword-like quality. E.g. `x: TypeAlias = ...` meaningfully
/// changes the sense of the binding.
#[derive(Debug, Clone, Dupe, Copy, PartialEq, Eq)]
pub enum SpecialExport {
    TypeAlias,
    TypeAliasType,
    TypeVar,
    ParamSpec,
    TypeVarTuple,
    Annotated,
    Literal,
    Enum,
    StrEnum,
    IntEnum,
    TypedDict,
    CollectionsNamedTuple,
    TypingNamedTuple,
    AssertType,
    NewType,
    Union,
    Optional,
    Cast,
    Super,
    Exit,
    Quit,
    OsExit,
    Len,
    Bool,
    BuiltinsType,
    TypingType,
    NoTypeCheck,
    Overload,
    AbstractMethod,
    SelfType,
    Generic,
    Protocol,
    PydanticConfigDict,
    PydanticField,
    HasAttr,
    GetAttr,
    Callable,
    BuiltinsDict,
    TypingDict,
    BuiltinsList,
    TypingList,
    BuiltinsTuple,
    TypingTuple,
}

impl SpecialExport {
    pub fn new(name: &Name) -> Option<Self> {
        match name.as_str() {
            "TypeAlias" => Some(Self::TypeAlias),
            "TypeVar" => Some(Self::TypeVar),
            "ParamSpec" => Some(Self::ParamSpec),
            "TypeVarTuple" => Some(Self::TypeVarTuple),
            "Annotated" => Some(Self::Annotated),
            "Literal" => Some(Self::Literal),
            "Enum" => Some(Self::Enum),
            "StrEnum" => Some(Self::StrEnum),
            "IntEnum" => Some(Self::IntEnum),
            "TypedDict" => Some(Self::TypedDict),
            "namedtuple" => Some(Self::CollectionsNamedTuple),
            "NamedTuple" => Some(Self::TypingNamedTuple),
            "Self" => Some(Self::SelfType),
            "assert_type" => Some(Self::AssertType),
            "NewType" => Some(Self::NewType),
            "Union" => Some(Self::Union),
            "Optional" => Some(Self::Optional),
            "Generic" => Some(Self::Generic),
            "Protocol" => Some(Self::Protocol),
            "cast" => Some(Self::Cast),
            "super" => Some(Self::Super),
            "exit" => Some(Self::Exit),
            "quit" => Some(Self::Quit),
            "_exit" => Some(Self::OsExit),
            "len" => Some(Self::Len),
            "bool" => Some(Self::Bool),
            "type" => Some(Self::BuiltinsType),
            "Type" => Some(Self::TypingType),
            "no_type_check" => Some(Self::NoTypeCheck),
            "overload" => Some(Self::Overload),
            "abstractmethod" => Some(Self::AbstractMethod),
            "ConfigDict" => Some(Self::PydanticConfigDict),
            "Field" => Some(Self::PydanticField),
            "hasattr" => Some(Self::HasAttr),
            "getattr" => Some(Self::GetAttr),
            "TypeAliasType" => Some(Self::TypeAliasType),
            "Callable" => Some(Self::Callable),
            "dict" => Some(Self::BuiltinsDict),
            "Dict" => Some(Self::TypingDict),
            "list" => Some(Self::BuiltinsList),
            "List" => Some(Self::TypingList),
            "tuple" => Some(Self::BuiltinsTuple),
            "Tuple" => Some(Self::TypingTuple),
            _ => None,
        }
    }

    pub fn defined_in(self, m: ModuleName) -> bool {
        match self {
            Self::TypeAlias
            | Self::TypeVar
            | Self::ParamSpec
            | Self::TypeVarTuple
            | Self::Annotated
            | Self::Literal
            | Self::TypedDict
            | Self::TypingNamedTuple
            | Self::NewType
            | Self::Union
            | Self::Optional
            | Self::AssertType
            | Self::TypeAliasType
            | Self::NoTypeCheck
            | Self::Overload
            | Self::SelfType
            | Self::Cast
            | Self::Generic
            | Self::Protocol
            | Self::TypingType
            | Self::TypingDict
            | Self::TypingList
            | Self::TypingTuple => {
                matches!(m.as_str(), "typing" | "typing_extensions")
            }
            Self::CollectionsNamedTuple => matches!(m.as_str(), "collections"),
            Self::Enum | Self::StrEnum | Self::IntEnum => matches!(m.as_str(), "enum"),
            Self::Super
            | Self::Len
            | Self::Quit
            | Self::Bool
            | Self::BuiltinsType
            | Self::HasAttr
            | Self::GetAttr
            | Self::BuiltinsDict
            | Self::BuiltinsList
            | Self::BuiltinsTuple => {
                matches!(m.as_str(), "builtins")
            }
            Self::Exit => matches!(m.as_str(), "sys" | "builtins"),
            Self::OsExit => matches!(m.as_str(), "os"),
            Self::AbstractMethod => matches!(m.as_str(), "abc"),
            Self::PydanticConfigDict | Self::PydanticField => matches!(m.as_str(), "pydantic"),
            Self::Callable => matches!(
                m.as_str(),
                "typing" | "typing_extensions" | "collections.abc"
            ),
        }
    }
}
