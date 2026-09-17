use accumulate::map;

fn square(x: i32) -> i32 {
    x * x
}

#[test]
fn accumulate_empty() {
    let input = vec![];
    let expected = vec![];
    assert_eq!(map(input, square), expected);
}

#[test]
fn accumulate_squares() {
    let input = vec![1, 2, 3];
    let expected = vec![1, 4, 9];
    assert_eq!(map(input, square), expected);
}

#[test]
fn closure_floats() {
    let input = vec![2.0, 3.0, 4.0, 5.0];
    let expected = vec![4.0, 9.0, 16.0, 25.0];
    assert_eq!(map(input, |x| x * x), expected);
}

#[test]
fn accumulate_upcases() {
    let input = vec!["Hello", "world"];
    let expected = vec!["HELLO", "WORLD"];
    assert_eq!(map(input, str::to_uppercase), expected);
}

#[test]
fn accumulate_recursively() {
    let input = vec!["a", "b", "c"];
    let expected = vec![
        vec!["a1", "a2", "a3"],
        vec!["b1", "b2", "b3"],
        vec!["c1", "c2", "c3"],
    ];
    assert_eq!(
        map(input, |x| map(vec!["1", "2", "3"], |y| [x, y].join(""))),
        expected
    );
}

#[test]
fn mutating_closure() {
    let mut counter = 0;
    let input = vec![-2, 3, 4, -5];
    let expected = vec![2, 3, 4, 5];
    let result = map(input, |x: i64| {
        counter += 1;
        x.abs()
    });
    assert_eq!(result, expected);
    assert_eq!(counter, 4);
}

