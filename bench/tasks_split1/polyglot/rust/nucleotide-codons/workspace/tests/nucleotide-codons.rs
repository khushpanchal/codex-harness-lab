#[test]
fn methionine() {
    let info = nucleotide_codons::parse(make_pairs());
    assert_eq!(info.name_for("ATG"), Ok("methionine"));
}

