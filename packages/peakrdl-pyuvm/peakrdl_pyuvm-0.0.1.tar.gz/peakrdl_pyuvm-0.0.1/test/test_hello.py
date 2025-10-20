from peakrdl_pyuvm.hello import main

def test_hello(capsys):
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello from peakrdl-pyuvm!\n"
