use luhn_from::*;

#[test]
fn you_can_validate_from_a_str() {
    let valid = Luhn::from("046 454 286");
    let invalid = Luhn::from("046 454 287");
    assert!(valid.is_valid());
    assert!(!invalid.is_valid());
}

