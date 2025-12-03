lemma Qfour(x: int)
  ensures 7 * x + 5 < (x + 3) * (x + 4)
{
  calc {
    7 * x + 5;
    < {
        // x*x >= 0 for all integers x
        assert 0 <= x * x;
        // therefore x*x + 7 > 0
        assert 0 < x * x + 7;
      }
      // Add x * x + 7 on both ends
    7 * x + 5 + x * x + 7;
    == { assert 5 + 7 == 12 ;}
    x * x + 7 * x + 12;
    == {
        // expand (x + 3) * (x + 4) to match
        assert (x + 3) * (x + 4) == x * x + 7 * x + 12;
      }
    x * x + 7 * x + 12;
  }
}