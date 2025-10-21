/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//! Things that abstract over the binding types.

pub trait TableKeyed<K> {
    type Value;
    fn get(&self) -> &Self::Value;
    fn get_mut(&mut self) -> &mut Self::Value;
}

#[macro_export]
macro_rules! table {
    (#[$($derive:tt)*] pub struct $name:ident(pub $t:tt)) => {
        table!(@impl, [pub], #[$($derive)*] pub struct $name($t));
    };
    (#[$($derive:tt)*] pub struct $name:ident($t:tt)) => {
        table!(@impl, [], #[$($derive)*] pub struct $name($t));
    };
    (@impl, [$($vis:tt)*], #[$($derive:tt)*] pub struct $name:ident($t:tt)) => {
        #[$($derive)*]
        pub struct $name {
            $($vis)* types: $t<$crate::binding::binding::Key>,
            $($vis)* expectations: $t<$crate::binding::binding::KeyExpect>,
            $($vis)* consistent_override_checks: $t<$crate::binding::binding::KeyConsistentOverrideCheck>,
            $($vis)* exports: $t<$crate::binding::binding::KeyExport>,
            $($vis)* decorated_functions: $t<$crate::binding::binding::KeyDecoratedFunction>,
            $($vis)* undecorated_functions: $t<$crate::binding::binding::KeyUndecoratedFunction>,
            $($vis)* classes: $t<$crate::binding::binding::KeyClass>,
            $($vis)* tparams: $t<$crate::binding::binding::KeyTParams>,
            $($vis)* class_base_types: $t<$crate::binding::binding::KeyClassBaseType>,
            $($vis)* class_fields: $t<$crate::binding::binding::KeyClassField>,
            $($vis)* class_synthesized_fields: $t<$crate::binding::binding::KeyClassSynthesizedFields>,
            $($vis)* variance: $t<$crate::binding::binding::KeyVariance>,
            $($vis)* annotations: $t<$crate::binding::binding::KeyAnnotation>,
            $($vis)* class_metadata: $t<$crate::binding::binding::KeyClassMetadata>,
            $($vis)* class_mros: $t<$crate::binding::binding::KeyClassMro>,
            $($vis)* abstract_class_check: $t<$crate::binding::binding::KeyAbstractClassCheck>,
            $($vis)* legacy_tparams: $t<$crate::binding::binding::KeyLegacyTypeParam>,
            $($vis)* yields: $t<$crate::binding::binding::KeyYield>,
            $($vis)* yield_froms: $t<$crate::binding::binding::KeyYieldFrom>,
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::Key> for $name {
            type Value = $t<$crate::binding::binding::Key>;
            fn get(&self) -> &Self::Value { &self.types }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.types }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyExpect> for $name {
            type Value = $t<$crate::binding::binding::KeyExpect>;
            fn get(&self) -> &Self::Value { &self.expectations }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.expectations }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyConsistentOverrideCheck> for $name {
            type Value = $t<$crate::binding::binding::KeyConsistentOverrideCheck>;
            fn get(&self) -> &Self::Value { &self.consistent_override_checks }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.consistent_override_checks }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyExport> for $name {
            type Value = $t<$crate::binding::binding::KeyExport>;
            fn get(&self) -> &Self::Value { &self.exports }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.exports }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyDecoratedFunction> for $name {
            type Value = $t<$crate::binding::binding::KeyDecoratedFunction>;
            fn get(&self) -> &Self::Value { &self.decorated_functions }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.decorated_functions }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyUndecoratedFunction> for $name {
            type Value = $t<$crate::binding::binding::KeyUndecoratedFunction>;
            fn get(&self) -> &Self::Value { &self.undecorated_functions }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.undecorated_functions }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyClass> for $name {
            type Value = $t<$crate::binding::binding::KeyClass>;
            fn get(&self) -> &Self::Value { &self.classes }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.classes }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyTParams> for $name {
            type Value = $t<$crate::binding::binding::KeyTParams>;
            fn get(&self) -> &Self::Value { &self.tparams }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.tparams }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyClassBaseType> for $name {
            type Value = $t<$crate::binding::binding::KeyClassBaseType>;
            fn get(&self) -> &Self::Value { &self.class_base_types }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.class_base_types }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyClassField> for $name {
            type Value = $t<$crate::binding::binding::KeyClassField>;
            fn get(&self) -> &Self::Value { &self.class_fields }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.class_fields }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyClassSynthesizedFields> for $name {
            type Value = $t<$crate::binding::binding::KeyClassSynthesizedFields>;
            fn get(&self) -> &Self::Value { &self.class_synthesized_fields }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.class_synthesized_fields }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyVariance> for $name {
            type Value = $t<$crate::binding::binding::KeyVariance>;
            fn get(&self) -> &Self::Value { &self.variance }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.variance }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyAnnotation> for $name {
            type Value = $t<$crate::binding::binding::KeyAnnotation>;
            fn get(&self) -> &Self::Value { &self.annotations }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.annotations }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyClassMetadata> for $name {
            type Value = $t<$crate::binding::binding::KeyClassMetadata>;
            fn get(&self) -> &Self::Value { &self.class_metadata }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.class_metadata }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyClassMro> for $name {
            type Value = $t<$crate::binding::binding::KeyClassMro>;
            fn get(&self) -> &Self::Value { &self.class_mros }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.class_mros }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyAbstractClassCheck> for $name {
            type Value = $t<$crate::binding::binding::KeyAbstractClassCheck>;
            fn get(&self) -> &Self::Value { &self.abstract_class_check }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.abstract_class_check }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyLegacyTypeParam> for $name {
            type Value = $t<$crate::binding::binding::KeyLegacyTypeParam>;
            fn get(&self) -> &Self::Value { &self.legacy_tparams }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.legacy_tparams }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyYield> for $name {
            type Value = $t<$crate::binding::binding::KeyYield>;
            fn get(&self) -> &Self::Value { &self.yields }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.yields }
        }

        impl $crate::binding::table::TableKeyed<$crate::binding::binding::KeyYieldFrom> for $name {
            type Value = $t<$crate::binding::binding::KeyYieldFrom>;
            fn get(&self) -> &Self::Value { &self.yield_froms }
            fn get_mut(&mut self) -> &mut Self::Value { &mut self.yield_froms }
        }

        impl $name {
            #[allow(dead_code)]
            fn get<K>(&self) -> &<Self as $crate::binding::table::TableKeyed<K>>::Value
            where
                Self: $crate::binding::table::TableKeyed<K>,
            {
                $crate::binding::table::TableKeyed::<K>::get(self)
            }

            #[allow(dead_code)]
            fn get_mut<K>(&mut self) -> &mut <Self as $crate::binding::table::TableKeyed<K>>::Value
            where
                Self: $crate::binding::table::TableKeyed<K>,
            {
                $crate::binding::table::TableKeyed::<K>::get_mut(self)
            }
        }
    };
}

#[macro_export]
macro_rules! table_for_each(
    ($e:expr, $f:expr) => {
        $f(&($e).types);
        $f(&($e).expectations);
        $f(&($e).consistent_override_checks);
        $f(&($e).exports);
        $f(&($e).decorated_functions);
        $f(&($e).undecorated_functions);
        $f(&($e).classes);
        $f(&($e).tparams);
        $f(&($e).class_base_types);
        $f(&($e).class_fields);
        $f(&($e).class_synthesized_fields);
        $f(&($e).variance);
        $f(&($e).annotations);
        $f(&($e).class_metadata);
        $f(&($e).class_mros);
        $f(&($e).abstract_class_check);
        $f(&($e).legacy_tparams);
        $f(&($e).yields);
        $f(&($e).yield_froms);
    };
);

#[macro_export]
macro_rules! table_mut_for_each(
    ($e:expr, $f:expr) => {
        $f(&mut ($e).types);
        $f(&mut ($e).expectations);
        $f(&mut ($e).consistent_override_checks);
        $f(&mut ($e).exports);
        $f(&mut ($e).decorated_functions);
        $f(&mut ($e).undecorated_functions);
        $f(&mut ($e).classes);
        $f(&mut ($e).tparams);
        $f(&mut ($e).class_base_types);
        $f(&mut ($e).class_fields);
        $f(&mut ($e).class_synthesized_fields);
        $f(&mut ($e).variance);
        $f(&mut ($e).annotations);
        $f(&mut ($e).class_metadata);
        $f(&mut ($e).class_mros);
        $f(&mut ($e).abstract_class_check);
        $f(&mut ($e).legacy_tparams);
        $f(&mut ($e).yields);
        $f(&mut ($e).yield_froms);
    };
);

#[macro_export]
macro_rules! table_try_for_each(
    ($e:expr, $f:expr) => {
        $f(&($e).types)?;
        $f(&($e).expectations)?;
        $f(&($e).consistent_override_checks)?;
        $f(&($e).exports)?;
        $f(&($e).decorated_functions)?;
        $f(&($e).undecorated_functions)?;
        $f(&($e).classes)?;
        $f(&($e).tparams)?;
        $f(&($e).class_base_types)?;
        $f(&($e).class_fields)?;
        $f(&($e).class_synthesized_fields)?;
        $f(&($e).variance)?;
        $f(&($e).annotations)?;
        $f(&($e).class_metadata)?;
        $f(&($e).class_mros)?;
        $f(&($e).abstract_class_check)?;
        $f(&($e).legacy_tparams)?;
        $f(&($e).yields)?;
        $f(&($e).yield_froms)?;
    };
);
