from tarotteller.interfaces.cli import main as cli_main


def run_cli(args):
    return cli_main(args)


def test_cli_list_major(capsys):
    exit_code = run_cli(["list", "--arcana", "major", "--limit", "3"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Cards in deck" in captured.out
    assert "The Fool" in captured.out


def test_cli_info(capsys):
    exit_code = run_cli(["info", "The Magician"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "The Magician" in captured.out
    assert "Arcana : Major" in captured.out


def test_cli_draw_cards(capsys):
    exit_code = run_cli([
        "draw",
        "--cards",
        "2",
        "--seed",
        "5",
        "--no-reversed",
    ])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Card 1:" in captured.out
    assert "(upright)" in captured.out


def test_cli_draw_with_question(capsys):
    exit_code = run_cli([
        "draw",
        "--seed",
        "7",
        "--spread",
        "single",
        "--question",
        "What career move should I make soon?",
    ])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Personalized Insight" in captured.out
    assert "career" in captured.out.lower()


def test_cli_draw_with_immersive_extras(capsys):
    exit_code = run_cli([
        "draw",
        "--cards",
        "1",
        "--seed",
        "3",
        "--no-reversed",
        "--immersive",
        "--tone",
        "grounded",
        "--question",
        "How do I stay balanced in my creative work?",
    ])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Immersive Companion" in captured.out
    assert "Micro-Ritual" in captured.out
    assert "Soundscape" in captured.out
