use wordy::*;

#[test]
fn just_a_number() {
    let input = "What is 5?";
    let output = answer(input);
    let expected = Some(5);
    assert_eq!(output, expected);
}

