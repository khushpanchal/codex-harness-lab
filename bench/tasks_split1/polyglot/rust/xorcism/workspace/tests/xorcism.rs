#[cfg(feature = "io")]
use std::io::{Read, Write};
use xorcism::Xorcism;

#[test]
fn munge_in_place_identity() {
    let mut xs = Xorcism::new(&[0]);
    let input = "This is super-secret, cutting edge encryption, folks.".as_bytes();
    let mut output = input.to_owned();
    xs.munge_in_place(&mut output);

    assert_eq!(&input, &output);
}

