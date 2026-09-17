use react::*;

#[test]
fn input_cells_have_a_value() {
    let mut reactor = Reactor::new();
    let input = reactor.create_input(10);
    assert_eq!(reactor.value(CellId::Input(input)), Some(10));
}

