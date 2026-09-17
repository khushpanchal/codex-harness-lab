use fizzy::*;

#[test]
fn simple() {
    let actual = fizz_buzz::<i32>().apply(1..=16).collect::<Vec<_>>();
    let expected = [
        "1", "2", "fizz", "4", "buzz", "fizz", "7", "8", "fizz", "buzz", "11", "fizz", "13", "14",
        "fizzbuzz", "16",
    ];
    assert_eq!(actual, expected);
}

