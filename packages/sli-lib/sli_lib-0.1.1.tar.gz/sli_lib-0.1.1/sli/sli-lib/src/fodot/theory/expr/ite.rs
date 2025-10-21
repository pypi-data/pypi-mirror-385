use super::{
    Expr, FreeVariableIter, FreeVariables, Metadata, MetadataMethods, VocabIterCheck,
    WellDefinedCondition,
};
use crate::fodot::display_as_debug;
use crate::fodot::error::{ExprMismatchError, TypeMismatch, VocabMismatchError};
use crate::fodot::fmt::{FodotOptions, FodotPrecDisplay};
use crate::fodot::{
    fmt::{Fmt, FodotDisplay, FormatOptions},
    vocabulary::{TypeRef, Vocabulary},
};
use sli_collections::rc::RcA;
use std::fmt::{Display, Write};
use std::iter::once;

/// An 'if then else' expression.
#[derive(Clone)]
pub struct Ite {
    if_formula: Expr,
    then_expr: Expr,
    else_expr: Expr,
    vocab: Option<RcA<Vocabulary>>,
    metadata: Option<Box<Metadata>>,
}

impl FodotOptions for Ite {
    type Options<'a>
        = FormatOptions
    where
        Self: 'a;
}

impl FodotDisplay for Ite {
    fn fmt(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        FodotPrecDisplay::fmt_with_prec(fmt, f, 0)
    }
}

impl FodotPrecDisplay for Ite {
    fn fmt_with_prec(
        fmt: Fmt<&Self, Self::Options<'_>>,
        f: &mut std::fmt::Formatter<'_>,
        super_prec: u32,
    ) -> std::fmt::Result {
        let this_prec = fmt.value.precedence();
        let needs_bracket = super_prec > this_prec;
        if needs_bracket {
            f.write_char('(')?;
        }
        write!(
            f,
            "if {} then {} else {}",
            fmt.with_format_opts(&fmt.value.if_formula),
            fmt.with_format_opts(&fmt.value.then_expr),
            fmt.with_format_opts(&fmt.value.else_expr)
                .with_prec(this_prec),
        )?;
        if needs_bracket {
            f.write_char(')')?;
        }
        Ok(())
    }
}

impl Display for Ite {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", Fmt::with_defaults(self))
    }
}

display_as_debug!(Ite);

impl PartialEq for Ite {
    fn eq(&self, other: &Self) -> bool {
        self.if_formula == other.if_formula
            && self.then_expr == other.then_expr
            && self.else_expr == other.else_expr
    }
}

impl Eq for Ite {}

impl Ite {
    /// Try to create an if then else expression with the given condition, then expression and else
    /// expression.
    pub fn try_new(
        if_formula: Expr,
        then_expr: Expr,
        else_expr: Expr,
    ) -> Result<Self, ExprMismatchError> {
        let mut vocab_checker = VocabIterCheck::new(
            once(if_formula.vocab_rc())
                .chain(once(then_expr.vocab_rc()))
                .chain(once(else_expr.vocab_rc())),
        );
        if !vocab_checker.check_if_consistent() {
            return Err(VocabMismatchError.into());
        }
        if !if_formula.codomain().is_bool() {
            return Err(TypeMismatch {
                expected: TypeRef::Bool.into(),
                found: if_formula.codomain().into(),
            }
            .into());
        }
        if then_expr.codomain() != else_expr.codomain() {
            return Err(TypeMismatch {
                expected: then_expr.codomain().into(),
                found: else_expr.codomain().into(),
            }
            .into());
        }
        let vocab = if_formula
            .vocab_rc()
            .or(then_expr.vocab_rc())
            .or(else_expr.vocab_rc())
            .cloned();

        Ok(Self {
            if_formula,
            then_expr,
            else_expr,
            vocab,
            metadata: Default::default(),
        })
    }

    pub fn precedence(&self) -> u32 {
        50
    }

    pub fn codomain(&self) -> TypeRef {
        self.then_expr.codomain()
    }

    pub fn vocab_rc(&self) -> Option<&RcA<Vocabulary>> {
        self.vocab.as_ref()
    }

    /// Returns the condition.
    pub fn if_formula(&self) -> &Expr {
        &self.if_formula
    }

    /// Returns the then expression.
    pub fn then_expr(&self) -> &Expr {
        &self.then_expr
    }

    /// Returns the else expression.
    pub fn else_expr(&self) -> &Expr {
        &self.else_expr
    }

    pub fn collect_wdcs(&self) -> Vec<WellDefinedCondition> {
        self.if_formula
            .collect_wdcs()
            .into_iter()
            .chain(self.then_expr.collect_wdcs().into_iter())
            .chain(self.else_expr.collect_wdcs().into_iter())
            .collect()
    }
}

impl FreeVariables for Ite {
    fn add_to_free_variable_iter<'a>(&'a self, iter: &mut FreeVariableIter<'a>) {
        iter.add_expr(self.if_formula().into());
        iter.add_expr(self.then_expr().into());
        iter.add_expr(self.else_expr().into());
    }
}

impl MetadataMethods for Ite {
    fn with_new_metadata(self, metadata: Metadata) -> Self {
        Self {
            metadata: Some(metadata.into()),
            ..self
        }
    }

    fn metadata(&self) -> Option<&Metadata> {
        self.metadata.as_deref()
    }

    fn metadata_mut(&mut self) -> &mut Metadata {
        self.metadata.get_or_insert_with(|| Default::default())
    }
}
