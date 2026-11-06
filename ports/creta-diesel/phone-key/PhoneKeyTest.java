package hmgapi.mods.creta;

/** Tests the actual release tracker without an Android input service. */
public final class PhoneKeyTest {
    public static void main(String[] ignored) {
        PhoneKey key = new PhoneKey();
        assert !key.release(1, 0, false, 1, 100, 150, true); // no matching down
        assert !key.release(0, 0, false, 1, 100, 100, true);
        assert key.release(1, 0, false, 1, 100, 180, true);
        assert !key.release(1, 0, false, 1, 100, 190, true); // consumed once
        key.release(0, 0, false, 1, 1000, 1000, false);
        assert !key.release(1, 0, false, 1, 1000, 1080, true); // call at down
        key.release(0, 0, false, 1, 2000, 2000, true);
        assert !key.release(1, 0, false, 1, 2000, 2080, false); // call arrives
        key.release(0, 0, false, 1, 3000, 3000, true);
        assert !key.release(1, 0, true, 1, 3000, 3080, true);
        key.release(0, 0, false, 1, 4000, 4000, true);
        assert !key.release(1, 0, false, 1, 4000, 4500, true); // hold
        key.release(0, 0, false, 1, 5000, 5000, true);
        key.release(0, 1, false, 1, 5000, 5100, true);
        assert !key.release(1, 0, false, 1, 5000, 5200, true);
        key.release(0, 0, false, 1, 6000, 6000, true);
        assert !key.release(1, 0, false, 2, 6000, 6080, true);
        assert !key.release(1, 0, false, 1, 6001, 6080, true); // mismatch
        System.out.println("PASS tap, duplicate, no down, call-state transitions, cancelled, hold, repeats and different devices");
    }
}
