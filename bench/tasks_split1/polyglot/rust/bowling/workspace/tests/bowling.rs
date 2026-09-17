use bowling::*;

#[test]
fn roll_returns_a_result() {
    let mut game = BowlingGame::new();
    assert!(game.roll(0).is_ok());
}

