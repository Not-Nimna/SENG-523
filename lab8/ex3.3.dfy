lemma Qthree(x: int, y: int)
  ensures 2 * (x + 4 * y + 7) - 10 == 2 * x + 8 * y + 4
{
  calc {
    2 * (x + 4 * y + 7) - 10;
    == { assert 2 * (x + 4 * y + 7) - 10 == 2 * x + 2 * 4 * y + 2 * 7 - 10; }
    2 * x + 2 * 4 * y + 2 * 7 - 10;
    == { assert 2 * 4 * y == 8 * y; 
    assert 2 * 7 == 14; }
    2 * x + 8 * y + 14 - 10;
    == { assert 14 - 10 == 4; }
    2 * x + 8 * y + 4;
  }
}