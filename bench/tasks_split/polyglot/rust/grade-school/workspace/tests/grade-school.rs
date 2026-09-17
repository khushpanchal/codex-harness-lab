use grade_school::*;

#[test]
fn grade_is_empty_if_no_students_in_the_roster() {
    let s = School::new();
    assert_eq!(s.grade(1), Vec::<String>::new())
}

#[test]
fn student_not_added_to_same_grade_more_than_once() {
    let mut s = School::new();
    s.add(2, "Blair");
    s.add(2, "James");
    s.add(2, "James");
    s.add(2, "Paul");
    assert_eq!(s.grade(2), vec!["Blair", "James", "Paul"])
}

#[test]
fn student_not_added_to_other_grade_for_multiple_grades() {
    let mut s = School::new();
    s.add(2, "Blair");
    s.add(2, "James");
    s.add(3, "James");
    s.add(3, "Paul");
    assert_eq!(s.grade(3), vec!["Paul"])
}

#[test]
fn grades_for_empty_school() {
    let s = School::new();
    assert_eq!(s.grades(), vec![])
}

#[test]
fn grades_for_several_students_are_sorted() {
    let mut s = School::new();
    s.add(2, "Aimee");
    s.add(7, "Logan");
    s.add(4, "Blair");
    assert_eq!(s.grades(), vec![2, 4, 7])
}

