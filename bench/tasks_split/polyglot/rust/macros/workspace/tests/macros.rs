use macros::hashmap;
use std::collections::HashMap;

#[test]
fn empty() {
    let expected: HashMap<u32, u32> = HashMap::new();
    let computed: HashMap<u32, u32> = hashmap!();
    assert_eq!(computed, expected);
}

#[test]
fn no_trailing_comma() {
    let mut expected = HashMap::new();
    expected.insert(1, "one");
    expected.insert(2, "two");
    assert_eq!(hashmap!(1 => "one", 2 => "two"), expected);
}

#[test]
fn nested() {
    let mut expected = HashMap::new();
    expected.insert("non-empty", {
        let mut subhashmap = HashMap::new();
        subhashmap.insert(23, 623);
        subhashmap.insert(34, 21);
        subhashmap
    });
    expected.insert("empty", HashMap::new());
    assert_eq!(
        hashmap!(
            "non-empty" => hashmap!(
                23 => 623,
                34 => 21
            ),
            "empty" => hashmap!()
        ),
        expected
    );
}

mod test {
    #[test]
    #[ignore]
    fn type_not_in_scope() {
        use macros::hashmap;

        let _empty: ::std::collections::HashMap<(), ()> = hashmap!();
        let _without_comma = hashmap!(23=> 623, 34 => 21);
        let _with_trailing = hashmap!(23 => 623, 34 => 21,);
    }

    #[test]
    #[ignore]
    fn macro_out_of_scope() {
        let _empty: ::std::collections::HashMap<(), ()> = macros::hashmap!();
        let _without_comma = macros::hashmap!(23=> 623, 34 => 21);
        let _with_trailing = macros::hashmap!(23 => 623, 34 => 21,);
    }
}

#[test]
fn compile_fails_comma_sep() {
    simple_trybuild::compile_fail("comma-sep.rs");
}

#[test]
fn compile_fails_only_comma() {
    simple_trybuild::compile_fail("only-comma.rs");
}

#[test]
fn compile_fails_triple_arguments() {
    simple_trybuild::compile_fail("triple-arguments.rs");
}

#[test]
fn compile_fails_two_arrows() {
    simple_trybuild::compile_fail("two-arrows.rs");
}

#[test]
fn compile_fails_no_comma() {
    simple_trybuild::compile_fail("no-comma.rs");
}

