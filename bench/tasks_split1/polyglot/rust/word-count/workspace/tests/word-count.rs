use word_count::*;

#[test]
fn count_one_word() {
    let input = "word";
    let mut output = word_count(input);
    let expected = [("word", 1)];
    for (word, count) in expected {
        assert_eq!((word, output.remove(word).unwrap_or(0)), (word, count));
    }
    assert_eq!(output.into_iter().collect::<Vec<_>>(), vec![]);
}

