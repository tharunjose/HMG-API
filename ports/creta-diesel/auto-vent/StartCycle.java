package hmgapi.mods.creta;

/** One bounded attempt window per native ACCON transition. */
final class StartCycle {
    private boolean on, finished;
    private int generation, attempts;

    int power(int status) {
        if (status != 0 && status != 1 && status != 2 && status != 5
                && status != 6 && status != 7 && status != 255) return -1;
        if (status != 0) {
            if (on) generation++;
            on = false;
            finished = true;
            return -1;
        }
        if (on) return -1;
        on = true;
        finished = false;
        attempts = 0;
        return ++generation;
    }

    boolean attempt(int token) {
        if (!on || finished || token != generation || attempts >= 12) return false;
        attempts++;
        return true;
    }

    void finish() { finished = true; }

    static int step(String level) {
        if ("low".equals(level)) return 3;
        if ("medium".equals(level)) return 4;
        return 5;
    }
}
