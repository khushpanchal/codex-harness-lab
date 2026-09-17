use ocr_numbers as ocr;

#[test]
fn input_with_lines_not_multiple_of_four_is_error() {
    #[rustfmt::skip]
    let input = " _ \n".to_string() +
                "| |\n" +
                "   ";

    assert_eq!(Err(ocr::Error::InvalidRowCount(3)), ocr::convert(&input));
}

