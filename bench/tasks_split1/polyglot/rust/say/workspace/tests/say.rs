use say::*;

#[test]
fn zero() {
    let input = 0;
    let output = encode(input);
    let expected = "zero";
    assert_eq!(output, expected);
}

