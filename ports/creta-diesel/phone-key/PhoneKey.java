package hmgapi.mods.creta;

import android.content.Context;
import android.content.Intent;
import android.os.Handler;
import android.os.Looper;
import android.telephony.TelephonyManager;
import android.view.KeyEvent;
import java.util.HashMap;
import hmgapi.hook.MethodHook;
import hmgapi.hook.ModContext;
import hmgapi.hook.ModEntry;
import hmgapi.hook.Points;

/** Observe physical Call releases and open the confirmed native Phone view only at idle. */
public final class PhoneKey extends ModEntry {
    private boolean installed;
    private final HashMap<Integer, Long> presses = new HashMap<Integer, Long>();

    @Override public void zygoteInit(final ModContext mod) {
        mod.hook(null, "framework.hkmc_loader.automotive_service", new MethodHook() {
            @Override protected void afterHookedMethod(Param p) throws Throwable {
                if (installed || p.getResult() == null || p.hasThrowable()) return;
                ClassLoader loader = (ClassLoader) Points.get(null,
                        "framework.hkmc_loader.class_loader", p.getResult());
                final Context context = (Context) p.args[0];
                final Handler handler = new Handler(Looper.getMainLooper());
                mod.hook(loader, "framework.window_manager_service.intercept_key", new MethodHook() {
                    @Override protected void afterHookedMethod(Param key) {
                        if (key.hasThrowable() || !(key.args[0] instanceof KeyEvent)) return;
                        KeyEvent event = (KeyEvent) key.args[0];
                        if (event.getKeyCode() != KeyEvent.KEYCODE_CALL) return;
                        boolean idle = idleCarPlay(context);
                        boolean launch;
                        synchronized (presses) {
                            launch = release(event.getAction(), event.getRepeatCount(),
                                    event.isCanceled(), event.getDeviceId(), event.getDownTime(),
                                    event.getEventTime(), idle);
                        }
                        if (launch) handler.post(new Runnable() {
                            @Override public void run() {
                                if (!mod.enabled() || !idleCarPlay(context)) return;
                                try {
                                    Intent intent = new Intent().setClassName(
                                            "com.daudio.app.dipo",
                                            "com.daudio.app.dipo.ui.DipoActivity");
                                    intent.addFlags(0x34000000).putExtra("CarPlayMode", 2);
                                    context.startActivity(intent);
                                    mod.log("Phone key: native CarPlay Phone requested");
                                } catch (RuntimeException failure) {
                                    mod.log("Phone key: native Phone activity failed");
                                }
                            }
                        });
                    }
                });
                installed = true;
                mod.log("Phone key: observing Call releases");
            }
        });
    }

    // Called under the presses lock. Remember only device ID and monotonic press time.
    boolean release(int action, int repeat, boolean canceled, int device,
                    long down, long now, boolean idle) {
        if (action == KeyEvent.ACTION_DOWN) {
            if (repeat == 0 && !canceled && idle) presses.put(device, down);
            else presses.remove(device);
            return false;
        }
        if (action != KeyEvent.ACTION_UP) return false;
        Long began = presses.remove(device);
        return began != null && began.longValue() == down && !canceled && idle
                && now >= down && now - down < 500L;
    }

    static boolean idleCarPlay(Context context) {
        try {
            Object manager = context.getSystemService("dipo");
            if (manager == null || !Integer.valueOf(1).equals(Points.call(null,
                    "framework.dipo_manager.current_stat", manager))) return false;
            // The native API explicitly distinguishes idle (0), ringing (1), offhook (2).
            Object call = manager.getClass().getMethod("getDiPOCallstatus").invoke(manager);
            if (!Integer.valueOf(0).equals(call)) return false;
            Object mode = Points.call(null, "framework.dipo_manager.current_mode", manager);
            if (mode == null || !Integer.valueOf(0).equals(Points.call(null,
                    "framework.dipo_mode.phone_call", mode))) return false;
            TelephonyManager phone = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
            return phone != null && phone.getCallState() == TelephonyManager.CALL_STATE_IDLE;
        } catch (Throwable unavailable) {
            return false;
        }
    }
}
