# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/grade-school/canonical-data.json
# File last updated on 2023-07-19

import unittest

from grade_school import (
    School,
)


class GradeSchoolTest(unittest.TestCase):
    def test_roster_is_empty_when_no_student_is_added(self):
        school = School()
        expected = []

        self.assertEqual(school.roster(), expected)


    def test_student_is_added_to_the_roster(self):
        school = School()
        school.add_student(name="Aimee", grade=2)
        expected = ["Aimee"]

        self.assertEqual(school.roster(), expected)


    def test_multiple_students_in_the_same_grade_are_added_to_the_roster(self):
        school = School()
        school.add_student(name="Blair", grade=2)
        school.add_student(name="James", grade=2)
        school.add_student(name="Paul", grade=2)
        expected = ["Blair", "James", "Paul"]

        self.assertEqual(school.roster(), expected)


    def test_student_not_added_to_same_grade_in_the_roster_more_than_once(self):
        school = School()
        school.add_student(name="Blair", grade=2)
        school.add_student(name="James", grade=2)
        school.add_student(name="James", grade=2)
        school.add_student(name="Paul", grade=2)
        expected = ["Blair", "James", "Paul"]

        self.assertEqual(school.roster(), expected)


    def test_students_in_multiple_grades_are_added_to_the_roster(self):
        school = School()
        school.add_student(name="Chelsea", grade=3)
        school.add_student(name="Logan", grade=7)
        expected = ["Chelsea", "Logan"]

        self.assertEqual(school.roster(), expected)


    def test_student_not_added_to_multiple_grades_in_the_roster(self):
        school = School()
        school.add_student(name="Blair", grade=2)
        school.add_student(name="James", grade=2)
        school.add_student(name="James", grade=3)
        school.add_student(name="Paul", grade=3)
        expected = ["Blair", "James", "Paul"]

        self.assertEqual(school.roster(), expected)


    def test_students_are_sorted_by_name_in_the_roster(self):
        school = School()
        school.add_student(name="Peter", grade=2)
        school.add_student(name="Zoe", grade=2)
        school.add_student(name="Alex", grade=2)
        expected = ["Alex", "Peter", "Zoe"]

        self.assertEqual(school.roster(), expected)


    def test_grade_is_empty_if_no_students_in_the_roster(self):
        school = School()
        expected = []
        self.assertEqual(school.grade(1), expected)


    def test_student_not_added_to_same_grade_more_than_once(self):
        school = School()
        school.add_student(name="Blair", grade=2)
        school.add_student(name="James", grade=2)
        school.add_student(name="James", grade=2)
        school.add_student(name="Paul", grade=2)
        expected = ["Blair", "James", "Paul"]
        self.assertEqual(school.grade(2), expected)


    def test_student_not_added_to_other_grade_for_multiple_grades(self):
        school = School()
        school.add_student(name="Blair", grade=2)
        school.add_student(name="James", grade=2)
        school.add_student(name="James", grade=3)
        school.add_student(name="Paul", grade=3)
        expected = ["Paul"]
        self.assertEqual(school.grade(3), expected)

