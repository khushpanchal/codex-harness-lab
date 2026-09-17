use variable_length_quantity as vlq;

#[test]
fn zero() {
    let input = &[0];
    let output = vlq::to_bytes(input);
    let expected = vec![0x0];
    assert_eq!(output, expected);
}

