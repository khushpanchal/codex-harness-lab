use acronym::*;

#[test]
fn basic() {
    let input = "Portable Network Graphics";
    let output = abbreviate(input);
    let expected = "PNG";
    assert_eq!(output, expected);
}

