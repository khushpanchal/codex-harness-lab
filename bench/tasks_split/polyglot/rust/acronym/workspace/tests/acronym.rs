use acronym::*;

#[test]
fn basic() {
    let input = "Portable Network Graphics";
    let output = abbreviate(input);
    let expected = "PNG";
    assert_eq!(output, expected);
}

#[test]
fn punctuation() {
    let input = "First In, First Out";
    let output = abbreviate(input);
    let expected = "FIFO";
    assert_eq!(output, expected);
}

#[test]
fn punctuation_without_whitespace() {
    let input = "Complementary metal-oxide semiconductor";
    let output = abbreviate(input);
    let expected = "CMOS";
    assert_eq!(output, expected);
}

#[test]
fn consecutive_delimiters() {
    let input = "Something - I made up from thin air";
    let output = abbreviate(input);
    let expected = "SIMUFTA";
    assert_eq!(output, expected);
}

#[test]
fn underscore_emphasis() {
    let input = "The Road _Not_ Taken";
    let output = abbreviate(input);
    let expected = "TRNT";
    assert_eq!(output, expected);
}

