use react::*;

#[test]
fn input_cells_have_a_value() {
    let mut reactor = Reactor::new();
    let input = reactor.create_input(10);
    assert_eq!(reactor.value(CellId::Input(input)), Some(10));
}

#[test]
fn error_setting_a_nonexistent_input_cell() {
    let mut dummy_reactor = Reactor::new();
    let input = dummy_reactor.create_input(1);
    assert!(!Reactor::new().set_value(input, 0));
}

#[test]
fn compute_cells_take_inputs_in_the_right_order() {
    let mut reactor = Reactor::new();
    let one = reactor.create_input(1);
    let two = reactor.create_input(2);
    let output = reactor
        .create_compute(&[CellId::Input(one), CellId::Input(two)], |v| {
            v[0] + v[1] * 10
        })
        .unwrap();
    assert_eq!(reactor.value(CellId::Compute(output)), Some(21));
}

#[test]
fn do_not_break_cell_if_creating_compute_cell_with_valid_and_invalid_input() {
    let mut dummy_reactor = Reactor::new();
    let _ = dummy_reactor.create_input(1);
    let dummy_cell = dummy_reactor.create_input(2);
    let mut reactor = Reactor::new();
    let input = reactor.create_input(1);
    assert_eq!(
        reactor.create_compute(&[CellId::Input(input), CellId::Input(dummy_cell)], |_| 0),
        Err(CellId::Input(dummy_cell))
    );
    assert!(reactor.set_value(input, 5));
    assert_eq!(reactor.value(CellId::Input(input)), Some(5));
}

#[test]
fn compute_cells_can_depend_on_other_compute_cells() {
    let mut reactor = Reactor::new();
    let input = reactor.create_input(1);
    let times_two = reactor
        .create_compute(&[CellId::Input(input)], |v| v[0] * 2)
        .unwrap();
    let times_thirty = reactor
        .create_compute(&[CellId::Input(input)], |v| v[0] * 30)
        .unwrap();
    let output = reactor
        .create_compute(
            &[CellId::Compute(times_two), CellId::Compute(times_thirty)],
            |v| v[0] + v[1],
        )
        .unwrap();
    assert_eq!(reactor.value(CellId::Compute(output)), Some(32));
    assert!(reactor.set_value(input, 3));
    assert_eq!(reactor.value(CellId::Compute(output)), Some(96));
}

/// A CallbackRecorder helps tests whether callbacks get called correctly.
/// You'll see it used in tests that deal with callbacks.
/// The names should be descriptive enough so that the tests make sense,
/// so it's not necessary to fully understand the implementation,
/// though you are welcome to.
struct CallbackRecorder {
    // Note that this `Cell` is https://doc.rust-lang.org/std/cell/
    // a mechanism to allow internal mutability,
    // distinct from the cells (input cells, compute cells) in the reactor
    value: std::cell::Cell<Option<i32>>,
}

impl CallbackRecorder {
    fn new() -> Self {
        CallbackRecorder {
            value: std::cell::Cell::new(None),
        }
    }

    fn expect_to_have_been_called_with(&self, v: i32) {
        assert_ne!(
            self.value.get(),
            None,
            "Callback was not called, but should have been"
        );
        assert_eq!(
            self.value.replace(None),
            Some(v),
            "Callback was called with incorrect value"
        );
    }

    fn expect_not_to_have_been_called(&self) {
        assert_eq!(
            self.value.get(),
            None,
            "Callback was called, but should not have been"
        );
    }

    fn callback_called(&self, v: i32) {
        assert_eq!(
            self.value.replace(Some(v)),
            None,
            "Callback was called too many times; can't be called with {v}"
        );
    }
}

#[test]
fn error_adding_callback_to_nonexistent_cell() {
    let mut dummy_reactor = Reactor::new();
    let input = dummy_reactor.create_input(1);
    let output = dummy_reactor
        .create_compute(&[CellId::Input(input)], |_| 0)
        .unwrap();
    assert_eq!(
        Reactor::new().add_callback(output, |_: u32| println!("hi")),
        None
    );
}

#[test]
fn callbacks_only_fire_on_change() {
    let cb = CallbackRecorder::new();
    let mut reactor = Reactor::new();
    let input = reactor.create_input(1);
    let output = reactor
        .create_compute(
            &[CellId::Input(input)],
            |v| if v[0] < 3 { 111 } else { 222 },
        )
        .unwrap();
    assert!(reactor
        .add_callback(output, |v| cb.callback_called(v))
        .is_some());

    assert!(reactor.set_value(input, 2));
    cb.expect_not_to_have_been_called();
    assert!(reactor.set_value(input, 4));
    cb.expect_to_have_been_called_with(222);
}

#[test]
fn callbacks_can_be_called_from_multiple_cells() {
    let cb1 = CallbackRecorder::new();
    let cb2 = CallbackRecorder::new();
    let mut reactor = Reactor::new();
    let input = reactor.create_input(1);
    let plus_one = reactor
        .create_compute(&[CellId::Input(input)], |v| v[0] + 1)
        .unwrap();
    let minus_one = reactor
        .create_compute(&[CellId::Input(input)], |v| v[0] - 1)
        .unwrap();
    assert!(reactor
        .add_callback(plus_one, |v| cb1.callback_called(v))
        .is_some());
    assert!(reactor
        .add_callback(minus_one, |v| cb2.callback_called(v))
        .is_some());

    assert!(reactor.set_value(input, 10));
    cb1.expect_to_have_been_called_with(11);
    cb2.expect_to_have_been_called_with(9);
}

#[test]
fn removing_a_callback_multiple_times_doesnt_interfere_with_other_callbacks() {
    let cb1 = CallbackRecorder::new();
    let cb2 = CallbackRecorder::new();

    let mut reactor = Reactor::new();
    let input = reactor.create_input(1);
    let output = reactor
        .create_compute(&[CellId::Input(input)], |v| v[0] + 1)
        .unwrap();
    let callback = reactor
        .add_callback(output, |v| cb1.callback_called(v))
        .unwrap();
    assert!(reactor
        .add_callback(output, |v| cb2.callback_called(v))
        .is_some());
    // We want the first remove to be Ok, but the others should be errors.
    assert!(reactor.remove_callback(output, callback).is_ok());
    for _ in 1..5 {
        assert_eq!(
            reactor.remove_callback(output, callback),
            Err(RemoveCallbackError::NonexistentCallback)
        );
    }

    assert!(reactor.set_value(input, 2));
    cb1.expect_not_to_have_been_called();
    cb2.expect_to_have_been_called_with(3);
}

#[test]
fn callbacks_should_not_be_called_if_dependencies_change_but_output_value_doesnt_change() {
    let cb = CallbackRecorder::new();
    let mut reactor = Reactor::new();
    let input = reactor.create_input(1);
    let plus_one = reactor
        .create_compute(&[CellId::Input(input)], |v| v[0] + 1)
        .unwrap();
    let minus_one = reactor
        .create_compute(&[CellId::Input(input)], |v| v[0] - 1)
        .unwrap();
    let always_two = reactor
        .create_compute(
            &[CellId::Compute(plus_one), CellId::Compute(minus_one)],
            |v| v[0] - v[1],
        )
        .unwrap();
    assert!(reactor
        .add_callback(always_two, |v| cb.callback_called(v))
        .is_some());
    for i in 2..5 {
        assert!(reactor.set_value(input, i));
        cb.expect_not_to_have_been_called();
    }
}

