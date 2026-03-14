from main import main


def test_main_prints_ready_message(capsys) -> None:
    main()
    captured = capsys.readouterr()
    assert "environment is ready" in captured.out
