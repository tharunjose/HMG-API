package hmgapi.mods.wireless.dipo;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.SystemClock;
import hmgapi.hook.Cluster;

/** One receiver per projection process. Retain only the last heading, never coordinates. */
final class DieselCompass extends BroadcastReceiver {
    static final String ACTION = "com.hkmc.telematics.gis.action.NAVI_GPS_CHANGED";
    static final String HEADING = "com.hkmc.telematics.gis.extra.HEADING";
    private static boolean watching;
    private static int heading = -1;
    private static long seen;

    static synchronized void watch(Context context) {
        if (watching || context == null) return;
        try {
            Context app = context.getApplicationContext();
            if (app == null) return;
            app.registerReceiver(new DieselCompass(), new IntentFilter(ACTION));
            watching = true;
        } catch (RuntimeException ignored) { /* Keep the already tested no-symbol fallback. */ }
    }

    @Override public void onReceive(Context context, Intent intent) {
        // Sticky data can predate this session; only time a live broadcast.
        if (intent == null || !ACTION.equals(intent.getAction()) || isInitialStickyBroadcast()) return;
        synchronized (DieselCompass.class) {
            heading = intent.getIntExtra(HEADING, -1);
            seen = SystemClock.elapsedRealtime();
        }
    }

    static synchronized boolean restore(Cluster cluster) {
        long age = SystemClock.elapsedRealtime() - seen;
        if (heading < 0 || heading > 360 || age < 0 || age > 30000L) return false;
        float deg = Math.round((360f - heading) / 22.5f) * 22.5f % 360f;
        cluster.tbtInfo(8, 0, deg, 0f, 0, 0, 0, 0, -1);
        // Hyundai already resumes the sub frame; leave its trip and compass fields alone.
        return true;
    }
}
