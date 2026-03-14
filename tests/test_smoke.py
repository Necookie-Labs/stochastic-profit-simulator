from main import main


def test_main_prints_simulation_summary(capsys) -> None:
    main()
    captured = capsys.readouterr()
    assert "Scenario: expected" in captured.out
    assert "Probability of loss:" in captured.out
    assert "Convergence checkpoints:" in captured.out
