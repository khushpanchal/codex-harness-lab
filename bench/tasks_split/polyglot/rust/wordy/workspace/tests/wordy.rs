use wordy::*;

#[test]
fn just_a_number() {
    let input = "What is 5?";
    let output = answer(input);
    let expected = Some(5);
    assert_eq!(output, expected);
}

#[test]
fn more_addition() {
    let input = "What is 53 plus 2?";
    let output = answer(input);
    let expected = Some(55);
    assert_eq!(output, expected);
}

#[test]
fn large_addition() {
    let input = "What is 123 plus 45678?";
    let output = answer(input);
    let expected = Some(45801);
    assert_eq!(output, expected);
}

#[test]
fn multiplication() {
    let input = "What is -3 multiplied by 25?";
    let output = answer(input);
    let expected = Some(-75);
    assert_eq!(output, expected);
}

#[test]
fn multiple_additions() {
    let input = "What is 1 plus 1 plus 1?";
    let output = answer(input);
    let expected = Some(3);
    assert_eq!(output, expected);
}

#[test]
fn multiple_subtraction() {
    let input = "What is 20 minus 4 minus 13?";
    let output = answer(input);
    let expected = Some(3);
    assert_eq!(output, expected);
}

#[test]
fn multiple_multiplication() {
    let input = "What is 2 multiplied by -2 multiplied by 3?";
    let output = answer(input);
    let expected = Some(-12);
    assert_eq!(output, expected);
}

#[test]
fn multiple_division() {
    let input = "What is -12 divided by 2 divided by -3?";
    let output = answer(input);
    let expected = Some(2);
    assert_eq!(output, expected);
}

#[test]
fn non_math_question() {
    let input = "Who is the President of the United States?";
    let output = answer(input);
    let expected = None;
    assert_eq!(output, expected);
}

#[test]
fn reject_problem_with_no_operands_or_operators() {
    let input = "What is?";
    let output = answer(input);
    let expected = None;
    assert_eq!(output, expected);
}

#[test]
fn reject_two_numbers_in_a_row() {
    let input = "What is 1 plus 2 1?";
    let output = answer(input);
    let expected = None;
    assert_eq!(output, expected);
}

#[test]
fn reject_prefix_notation() {
    let input = "What is plus 1 2?";
    let output = answer(input);
    let expected = None;
    assert_eq!(output, expected);
}

#[test]
#[cfg(feature = "exponentials")]
fn addition_and_exponential() {
    let input = "What is 1 plus 2 raised to the 2nd power?";
    let output = answer(input);
    let expected = Some(9);
    assert_eq!(output, expected);
}
