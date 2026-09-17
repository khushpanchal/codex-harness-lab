use grade_school::*;

#[test]
fn grade_is_empty_if_no_students_in_the_roster() {
    let s = School::new();
    assert_eq!(s.grade(1), Vec::<String>::new())
}

