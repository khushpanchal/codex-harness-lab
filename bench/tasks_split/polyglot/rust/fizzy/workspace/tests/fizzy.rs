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

#[test]
fn u64() {
    let actual = fizz_buzz::<u64>().apply(1_u64..=16).collect::<Vec<_>>();
    let expected = [
        "1", "2", "fizz", "4", "buzz", "fizz", "7", "8", "fizz", "buzz", "11", "fizz", "13", "14",
        "fizzbuzz", "16",
    ];
    assert_eq!(actual, expected);
}

#[test]
fn custom() {
    let expected = vec![
        "1", "2", "Fizz", "4", "Buzz", "Fizz", "Bam", "8", "Fizz", "Buzz", "11", "Fizz", "13",
        "Bam", "BuzzFizz", "16",
    ];
    let fizzer: Fizzy<i32> = Fizzy::new()
        .add_matcher(Matcher::new(|n: i32| n % 5 == 0, "Buzz"))
        .add_matcher(Matcher::new(|n: i32| n % 3 == 0, "Fizz"))
        .add_matcher(Matcher::new(|n: i32| n % 7 == 0, "Bam"));
    let actual = fizzer.apply(1..=16).collect::<Vec<_>>();
    assert_eq!(actual, expected);
}

#[test]
fn minimal_generic_bounds() {
    use std::fmt;
    use std::ops::{Add, Rem};

    #[derive(Clone, Copy, Debug, Default, PartialEq)]
    struct Fizzable(u8);

    impl From<u8> for Fizzable {
        fn from(i: u8) -> Fizzable {
            Fizzable(i)
        }
    }

    impl fmt::Display for Fizzable {
        fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
            let Fizzable(ref n) = self;
            write!(f, "{n}")
        }
    }

    impl Add for Fizzable {
        type Output = Fizzable;
        fn add(self, rhs: Fizzable) -> Fizzable {
            let Fizzable(n1) = self;
            let Fizzable(n2) = rhs;
            Fizzable(n1 + n2)
        }
    }

    impl Rem for Fizzable {
        type Output = Fizzable;
        fn rem(self, rhs: Fizzable) -> Fizzable {
            let Fizzable(n1) = self;
            let Fizzable(n2) = rhs;
            Fizzable(n1 % n2)
        }
    }

    let actual = fizz_buzz::<Fizzable>()
        .apply(std::iter::successors(Some(Fizzable(1)), |prev| {
            Some(*prev + 1.into())
        }))
        .take(16)
        .collect::<Vec<_>>();
    let expected = [
        "1", "2", "fizz", "4", "buzz", "fizz", "7", "8", "fizz", "buzz", "11", "fizz", "13", "14",
        "fizzbuzz", "16",
    ];
    assert_eq!(actual, expected);
}
