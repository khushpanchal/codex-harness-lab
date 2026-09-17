use book_store::*;

#[test]
fn only_a_single_book() {
    let input = &[1];
    let output = lowest_price(input);
    let expected = 800;
    assert_eq!(output, expected);
}

#[test]
fn empty_basket() {
    let input = &[];
    let output = lowest_price(input);
    let expected = 0;
    assert_eq!(output, expected);
}

#[test]
fn three_different_books() {
    let input = &[1, 2, 3];
    let output = lowest_price(input);
    let expected = 2160;
    assert_eq!(output, expected);
}

#[test]
fn five_different_books() {
    let input = &[1, 2, 3, 4, 5];
    let output = lowest_price(input);
    let expected = 3000;
    assert_eq!(output, expected);
}

#[test]
fn two_groups_of_four_is_cheaper_than_groups_of_five_and_three() {
    let input = &[1, 1, 2, 3, 4, 4, 5, 5];
    let output = lowest_price(input);
    let expected = 5120;
    assert_eq!(output, expected);
}

#[test]
fn two_each_of_first_four_books_and_one_copy_each_of_rest() {
    let input = &[1, 1, 2, 2, 3, 3, 4, 4, 5];
    let output = lowest_price(input);
    let expected = 5560;
    assert_eq!(output, expected);
}

#[test]
fn three_copies_of_first_book_and_two_each_of_remaining() {
    let input = &[1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 1];
    let output = lowest_price(input);
    let expected = 6800;
    assert_eq!(output, expected);
}

#[test]
fn four_groups_of_four_are_cheaper_than_two_groups_each_of_five_and_three() {
    let input = &[1, 1, 2, 2, 3, 3, 4, 5, 1, 1, 2, 2, 3, 3, 4, 5];
    let output = lowest_price(input);
    let expected = 10240;
    assert_eq!(output, expected);
}

#[test]
fn one_group_of_one_and_four_is_cheaper_than_one_group_of_two_and_three() {
    let input = &[1, 1, 2, 3, 4];
    let output = lowest_price(input);
    let expected = 3360;
    assert_eq!(output, expected);
}

