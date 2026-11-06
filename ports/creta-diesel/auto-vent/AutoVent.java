package hmgapi.mods.creta;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Handler;
import android.os.HandlerThread;
import hmgapi.hook.MethodHook;
import hmgapi.hook.ModContext;
import hmgapi.hook.ModEntry;
import hmgapi.hook.Points;

/** RHD driver ventilation, using the same mapped USM method confirmed in the manual test. */
public final class AutoVent extends ModEntry {
    static final String ACTION = "com.hkmc.intent.action.ACTION_ACC_STATUS_CHANGED";
    static final String STATUS = "android.ibox.mode.EXTRA_ACC_STATUS";
    private boolean installed;
    private final StartCycle driverCycle = new StartCycle();
    private final StartCycle passengerCycle = new StartCycle();

    @Override public void zygoteInit(final ModContext mod) {
        mod.hook(null, "framework.hkmc_loader.automotive_service", new MethodHook() {
            @Override protected void afterHookedMethod(Param p) {
                if (installed || p.getResult() == null || p.hasThrowable()) return;
                final Context context = (Context) p.args[0];
                HandlerThread thread = new HandlerThread("creta-driver-vent");
                thread.start();
                final Handler worker = new Handler(thread.getLooper());
                final IntentFilter filter = new IntentFilter(ACTION);
                BroadcastReceiver receiver = new BroadcastReceiver() {
                    @Override public void onReceive(Context c, Intent intent) {
                        if (intent == null || !ACTION.equals(intent.getAction())) return;
                        scheduleSeats(mod, context, worker, filter, intent.getIntExtra(STATUS, -1));
                    }
                };
                context.registerReceiver(receiver, filter, null, worker);
                installed = true;
                worker.post(new Runnable() {
                    int checks;
                    @Override public void run() {
                        Intent sticky = context.registerReceiver(null, filter);
                        if (sticky != null) {
                            scheduleSeats(mod, context, worker, filter, sticky.getIntExtra(STATUS, -1));
                        } else if (++checks < 24) {
                            worker.postDelayed(this, 5000);
                        }
                    }
                });
                mod.log("RHD driver ventilation: watching native ACC power state");
            }
        });
    }

    private void scheduleSeats(ModContext mod, Context context, Handler worker,
                               IntentFilter filter, int status) {
        schedule(mod, context, worker, filter, status, driverCycle, SeatTarget.DRIVER);
        schedule(mod, context, worker, filter, status, passengerCycle, SeatTarget.PASSENGER);
    }

    private void schedule(final ModContext mod, final Context context, final Handler worker,
                          final IntentFilter filter, int status, final StartCycle cycle,
                          final SeatTarget seat) {
        final int token = cycle.power(status);
        if (token < 0) return;
        // Snapshot choices once for this startup; settings changed later apply next cycle.
        final boolean enabled = mod.settingBoolean(seat.enabledKey, seat.defaultEnabled);
        final int step = StartCycle.step(mod.settingString(seat.levelKey, "high"));
        worker.postDelayed(new Runnable() {
            @Override public void run() {
                if (!cycle.attempt(token)) return;
                if (!enabled || !mod.enabled() || !mod.settingBoolean(seat.enabledKey, seat.defaultEnabled)) {
                    cycle.finish();
                    return;
                }
                try {
                    Intent latest = context.registerReceiver(null, filter);
                    if (latest == null || latest.getIntExtra(STATUS, -1) != 0) {
                        if (latest != null) cycle.power(latest.getIntExtra(STATUS, -1));
                        worker.postDelayed(this, 5000);
                        return;
                    }
                    Object bcm = service("bcm");
                    int state = ((Number) Points.call(null,
                            seat.readPoint, bcm)).intValue();
                    if (state >= 3 && state <= 8) {
                        cycle.finish();
                        mod.log("RHD " + seat.name + " ventilation: seat climate already selected; kept");
                        return;
                    }
                    if (state != 2) {
                        worker.postDelayed(this, 5000);
                        return;
                    }
                    Object usm = service("usm");
                    // Finish before sending: a lost Binder reply must not repeat a seat command.
                    cycle.finish();
                    Points.call(null, seat.writePoint, usm, step);
                    mod.log( "RHD " + seat.name + " ventilation: startup level " + (step - 2) + " requested");
                } catch (Throwable unavailable) {
                    mod.log("RHD " + seat.name + " ventilation: service unavailable or request failed");
                    worker.postDelayed(this, 5000);
                }
            }
        }, 5000);
    }

    private static Object service(String name) throws Throwable {
        String serviceName = (String) Points.get(null, "framework.car_services." + name, null);
        Object binder = Class.forName("android.os.ServiceManager")
                .getMethod("getService", String.class).invoke(null, serviceName);
        if (binder == null) throw new IllegalStateException("No native service");
        return Points.call(null, "framework." + name + "_service_stub.as_interface", null, binder);
    }
}
