from turingarena.tests.test_utils import assert_error, assert_no_error


def test_missing_local_flush():
    assert_error("""
        main {
            var int a;
            output 5;
            input a;
        }
    """, "missing flush between output and input instructions")


def test_missing_flush_for():
    assert_error("""
        main {
            var int a;
            
            for (i : 5) {
                output 4;
            }
            
            input a;
        }
    """, "missing flush between output and input instructions")


def test_missing_flush_for_2():
    assert_error("""
        main {
            var int a;

            for (i : 5) {
                input a;
                output 4;
            }
        }
    """, "missing flush between output and input instructions")


def test_missing_flush_for_3():
    assert_error("""
        main {
            var int a, b;

            for (i : 5) {
                flush;
                input a;
                output 4;
            }
            input b;
        }
    """, "missing flush between output and input instructions")


def test_for():
    assert_no_error("""
        main {
            var int a;

            for (i : 5) {
                input a;
                output 4;
                flush;
            }
            output 4;
        }
    """)


def test_missing_flush_if():
    assert_error("""
        main {
            var int a, b;
            input a;
            if (a) {
                flush;
            } else {
                output 4;
            }
            
            input b;
        }
    """, "missing flush between output and input instructions")


def test_missing_flush_if_2():
    assert_no_error("""
        main {
            var int a, b;
            input a;
            if (a) {
                flush;
            } else {
                output 4;
                flush;
            }

            input b;
        }
    """)


def test_missing_flush_init():
    assert_error("""
        init {
            output 4;
        }
        
        main {
            var int a;
            input a;
        }
    """, "missing flush between output and input instructions")
