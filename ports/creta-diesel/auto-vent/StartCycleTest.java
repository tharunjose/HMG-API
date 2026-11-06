package hmgapi.mods.creta;

public final class StartCycleTest {
    public static void main(String[] ignored) {
        StartCycle cycle = new StartCycle();
        assert cycle.power(-1) == -1;
        assert cycle.power(1) == -1; // native LOGICON is not ACCON
        int first = cycle.power(0);
        assert first > 0 && cycle.power(0) == -1;
        assert cycle.attempt(first);
        cycle.finish();
        assert !cycle.attempt(first); // physical controls stay effective after first write
        assert cycle.power(0) == -1;
        cycle.power(255);
        int second = cycle.power(0);
        assert second != first && !cycle.attempt(first);
        cycle.power(6); // power-off during delay invalidates the task
        assert !cycle.attempt(second);
        int third = cycle.power(0);
        for (int i = 0; i < 12; i++) assert cycle.attempt(third);
        assert !cycle.attempt(third);
        assert cycle.power(0) == -1; // no endless retry on duplicate broadcasts
        assert StartCycle.step("low") == 3;
        assert StartCycle.step("medium") == 4;
        assert StartCycle.step("high") == 5;
        assert StartCycle.step("corrupt") == 5;
        System.out.println("PASS native ACCON0, duplicate/off cancellation, stale tasks, bounded readiness, one request and levels1/2/3");
    }
}
