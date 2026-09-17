use two_bucket::*;

#[test]
fn measure_using_bucket_one_of_size_3_and_bucket_two_of_size_5_start_with_bucket_one() {
    let output = solve(3, 5, 1, &Bucket::One);
    let expected = Some(BucketStats {
        moves: 4,
        goal_bucket: Bucket::One,
        other_bucket: 5,
    });
    assert_eq!(output, expected);
}

