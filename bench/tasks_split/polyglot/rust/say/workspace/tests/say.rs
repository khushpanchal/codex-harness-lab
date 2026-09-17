use say::*;

#[test]
fn zero() {
    let input = 0;
    let output = encode(input);
    let expected = "zero";
    assert_eq!(output, expected);
}

#[test]
fn fourteen() {
    let input = 14;
    let output = encode(input);
    let expected = "fourteen";
    assert_eq!(output, expected);
}

#[test]
fn twenty_two() {
    let input = 22;
    let output = encode(input);
    let expected = "twenty-two";
    assert_eq!(output, expected);
}

#[test]
fn ninety_nine() {
    let input = 99;
    let output = encode(input);
    let expected = "ninety-nine";
    assert_eq!(output, expected);
}

#[test]
fn one_hundred_twenty_three() {
    let input = 123;
    let output = encode(input);
    let expected = "one hundred twenty-three";
    assert_eq!(output, expected);
}

#[test]
fn nine_hundred_ninety_nine() {
    let input = 999;
    let output = encode(input);
    let expected = "nine hundred ninety-nine";
    assert_eq!(output, expected);
}

#[test]
fn one_thousand_two_hundred_thirty_four() {
    let input = 1_234;
    let output = encode(input);
    let expected = "one thousand two hundred thirty-four";
    assert_eq!(output, expected);
}

#[test]
fn one_million_two_thousand_three_hundred_forty_five() {
    let input = 1_002_345;
    let output = encode(input);
    let expected = "one million two thousand three hundred forty-five";
    assert_eq!(output, expected);
}

#[test]
fn a_big_number() {
    let input = 987_654_321_123;
    let output = encode(input);
    let expected = "nine hundred eighty-seven billion six hundred fifty-four million three hundred twenty-one thousand one hundred twenty-three";
    assert_eq!(output, expected);
}

#[test]
fn max_u64() {
    let input = 18_446_744_073_709_551_615;
    let output = encode(input);
    let expected = "eighteen quintillion four hundred forty-six quadrillion seven hundred forty-four trillion seventy-three billion seven hundred nine million five hundred fifty-one thousand six hundred fifteen";
    assert_eq!(output, expected);
}
