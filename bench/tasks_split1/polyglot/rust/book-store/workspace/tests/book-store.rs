use book_store::*;

#[test]
fn only_a_single_book() {
    let input = &[1];
    let output = lowest_price(input);
    let expected = 800;
    assert_eq!(output, expected);
}

